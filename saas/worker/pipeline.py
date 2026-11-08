#!/usr/bin/env python3
"""EVA Video Studio · unattended job pipeline. Wraps the existing eva-video-style scripts; adds no editing logic.

    Upload → validate → frames + audio → eva-asr (SRT + word times) → face calibration → plan (sections + cards)
    → render chunks (scripts/render.mjs, parallel) → SFX (sfx.py) → captions (captions.py, English)
    → assemble (assemble.sh, -16 LUFS) → music (music.py plan + apply, license-gated) → checks → MP4

Stages are separate commands so a cloud runner can fan the render chunks out over several containers:
    pipeline.py prepare INPUT.mp4 JOB_DIR [--options opts.json]   validate, ASR, face, plan, job page (writes job.json)
    pipeline.py render  JOB_DIR CHUNK_INDEX                        one 10-second render chunk
    pipeline.py finish  JOB_DIR [--preview]                        audio, captions, assembly, music, checks
    pipeline.py run     INPUT.mp4 JOB_DIR [--options o.json] [--preview] [--workers N]   everything, locally

options (JSON): {"aspect": "9:16|16:9", "templates": ["T17","T20"], "template_mode": "single|multi|auto",
                 "music": "auto|manual|mix|none", "music_tracks": [], "paid": false, "preview_seconds": 10}
Input: any orientation (portrait phone video or landscape), ≤ 30 s, ≤ 200 MB, with speech.
Outputs in JOB_DIR/out: final.mp4 (1080x1920 or 1920x1080, 30 fps) or preview.mp4 (watermarked 720p, ≤ 10 s), captions.srt, report.json.
Exit codes: 2 input rejected (message in report.json), 3 stage failed (retryable), 0 ok.
"""
import argparse, json, os, resource, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE_REPO = Path(os.environ.get("EVA_ENGINE", HERE.parents[1])).resolve()   # eva-video-style checkout
CFG = HERE.parent / "config"
FPS, CHUNK_S = 30, 10.0
LIMITS = {"max_seconds": 30.5, "max_bytes": 200 * 1024 * 1024, "min_seconds": 3.0}
TRACKS = Path(os.environ.get("EVA_TRACKS", HERE.parent / "music/tracks"))   # composed by saas/music/compose.py (rights-cleared)
DEFAULT_OPTS = {"aspect": "9:16", "templates": ["T17"], "template_mode": "single", "music": "none", "music_tracks": [], "paid": False, "preview_seconds": 10}
SIZES = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
PREVIEW = {"9:16": (720, 1280), "16:9": (1280, 720)}
PY = sys.executable


class Reject(Exception): pass


# progress hook (saas/web/progress.py Reporter): PROGRESS.get()(stage, "start"|"done") / (stage, "frames", done, total)
import contextvars, re as _re
PROGRESS = contextvars.ContextVar("eva_progress", default=None)


def _report(*a):
    fn = PROGRESS.get()
    if fn:
        try: fn(*a)
        except Exception: pass


def sh(cmd, log, **kw):
    t = time.time(); log.write(f"$ {' '.join(map(str, cmd))}\n"); log.flush()
    r = subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, **kw)
    log.write(f"  -> exit {r.returncode} in {time.time() - t:.1f}s\n"); log.flush()
    if r.returncode: raise subprocess.CalledProcessError(r.returncode, cmd)


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate,nb_frames",
                        "-of", "json", str(p)], capture_output=True, text=True)
    if r.returncode: raise Reject("not a readable video file")
    return json.loads(r.stdout)


def cpu_s():
    a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


class Job:
    """job.json = static facts written by `prepare` only; stages/<name>.json = one marker per finished stage, so parallel
    render workers (threads here, separate containers in the cloud, sharing one volume) never write the same file."""
    def __init__(self, d, log="pipeline.log"):
        self.d = Path(d).resolve(); (self.d / "stages").mkdir(parents=True, exist_ok=True); (self.d / "logs").mkdir(exist_ok=True)
        self.jf = self.d / "job.json"
        self.j = json.loads(self.jf.read_text()) if self.jf.exists() else {}
        self.log = open(self.d / "logs" / log, "a")   # one log per worker: no two containers append to one file

    def save(self): self.jf.write_text(json.dumps(self.j, indent=1))

    def stages(self):
        return {f.stem: json.loads(f.read_text()) for f in sorted((self.d / "stages").glob("*.json"))}

    def stage(self, name, fn):
        """run a stage once; a retried job skips stages that already finished (safe retries)."""
        mk = self.d / "stages" / f"{name}.json"
        if mk.exists(): _report(name, "done"); return
        t, c = time.time(), cpu_s(); self.log.write(f"\n== {name}\n"); _report(name, "start")
        fn()
        if self.j: self.save()   # facts recorded by the stage (prepare is single-process)
        rec = {"ok": True, "wall_s": round(time.time() - t, 2), "cpu_s": round(cpu_s() - c, 2), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        mk.write_text(json.dumps(rec)); print(f"[{name}] {rec}", flush=True); _report(name, "done")


# ───────────────────────────── prepare ─────────────────────────────
def prepare(inp, jd, opts):
    J = Job(jd, "prepare.log"); o = dict(DEFAULT_OPTS, **(opts or {})); J.j.setdefault("options", o); J.save()
    inp = Path(inp).resolve()

    def validate():
        if inp.stat().st_size > LIMITS["max_bytes"]: raise Reject("video is larger than 200 MB")
        pr = probe(inp); st = {s["codec_type"]: s for s in pr["streams"]}
        dur = float(pr["format"]["duration"])
        if "video" not in st: raise Reject("no video stream")
        if "audio" not in st: raise Reject("no audio track: talking-head videos need the spoken audio")
        if dur > LIMITS["max_seconds"]: raise Reject(f"video is {dur:.1f} s; the limit is 30 s")
        if dur < LIMITS["min_seconds"]: raise Reject("video is too short")
        w, h = int(st["video"]["width"]), int(st["video"]["height"])
        for sd in st["video"].get("side_data_list") or []:   # phone videos stored landscape with a rotation flag
            if abs(int(float(sd.get("rotation", 0)))) in (90, 270): w, h = h, w
        if o.get("aspect") not in SIZES: raise Reject(f"unknown aspect {o.get('aspect')}")
        J.j["input"] = {"path": str(inp), "duration": dur, "width": w, "height": h, "bytes": inp.stat().st_size, "fps": st["video"]["r_frame_rate"]}

    def media():
        portrait_src = J.j["input"]["height"] > J.j["input"]["width"]
        sh([ENGINE_REPO / "scripts/extract_frames.sh", inp, J.d / "media/eva", 1080 if portrait_src else 1920], J.log)
        pr = probe(J.d / "media/eva/f_00000.jpg"); v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        J.j["src_size"] = [int(v["width"]), int(v["height"])]
        n = len(list((J.d / "media/eva").glob("f_*.jpg")))
        J.j["frames"] = n; J.j["end"] = round(n / FPS, 3)
        # the voice source for assembly: same length as the frames (assemble.sh uses -shortest)
        sh(["ffmpeg", "-loglevel", "error", "-y", "-i", inp, "-map", "0:v:0", "-map", "0:a:0", "-t", f"{n / FPS:.3f}", "-c", "copy", J.d / "src.mp4"], J.log)

    def asr():
        (J.d / "srt").mkdir(exist_ok=True)
        if (J.d / "srt/.restored").exists():   # transcript restored from the project cache (same source): no second ASR
            J.log.write("asr: reusing cached transcript\n")
        else:
            for f in (J.d / "srt").glob("talk.*"): f.unlink()     # retry after a partial run
            sh([PY, ENGINE_REPO / "scripts/asr.py", J.d / "src.mp4", J.d / "srt/talk", "--config", CFG / "asr.en.json"], J.log)
        J.j["language"] = json.loads((J.d / "srt/talk.asr.json").read_text()).get("source", {}).get("language") or "en"

    def face():
        if (J.d / "face.json").exists() and (J.d / "srt/.restored").exists(): return   # cached with the transcript
        sh([PY, HERE / "face.py", J.d / "media/eva", J.d / "face.json"], J.log)

    def plan():
        if o.get("reuse_plan") and (J.d / "plan.json").exists():   # HD export of a saved version: its exact plan, no planner/AI call
            J.log.write("plan: reusing the saved version plan\n")
            (J.d / "srt/talk.en.srt").exists() or shutil.copy(J.d / "srt/talk.bilingual.srt", J.d / "srt/talk.en.srt"); return
        sh([PY, HERE / "planner.py", J.d / "srt/talk.transcript.js", J.d, "--duration", J.j["end"],
            "--templates", ",".join(o["templates"]), "--mode", o["template_mode"], "--face", J.d / "face.json"], J.log)
        (J.d / "srt/talk.en.srt").exists() or shutil.copy(J.d / "srt/talk.bilingual.srt", J.d / "srt/talk.en.srt")   # music.py speech map

    def page():
        if (J.d / "engine").exists(): shutil.rmtree(J.d / "engine")
        shutil.copytree(ENGINE_REPO / "engine", J.d / "engine")
        if (J.d / "auto").exists(): shutil.rmtree(J.d / "auto")
        shutil.copytree(HERE / "auto", J.d / "auto")
        shutil.copy(J.d / "srt/talk.transcript.js", J.d / "transcript.js")
        n = J.j["frames"]; step = int(CHUNK_S * FPS)
        ch = [[f / FPS, min(n, f + step) / FPS] for f in range(0, n, step)]
        if len(ch) > 1 and ch[-1][1] - ch[-1][0] < 1.0: tail = ch.pop(); ch[-1][1] = tail[1]   # no 1-frame tail chunk (and its container start)
        J.j["chunks"] = ch

    try:
        J.stage("validate", validate)
    except Reject as e:
        J.j["rejected"] = str(e); J.save(); (J.d / "out").mkdir(exist_ok=True)
        (J.d / "out/report.json").write_text(json.dumps({"ok": False, "rejected": str(e)})); print("REJECTED:", e); return 2
    for name, fn in (("media", media), ("asr", asr), ("face", face), ("plan", plan), ("page", page)): J.stage(name, fn)
    return 0


# ───────────────────────────── render ─────────────────────────────
def render(jd, i):
    J = Job(jd, f"render_{i:02}.log"); a, b = J.j["chunks"][i]; out = J.d / f"sec/c{i:02}.mp4"
    def run():
        if out.exists(): out.unlink()   # a half-written chunk from a crashed attempt
        cmd = ["node", ENGINE_REPO / "scripts/render.mjs", J.d / "auto/index.html", "--out", out, "--from", a, "--to", b] + page_args(J)
        if os.environ.get("CHROME"): cmd += ["--browser", os.environ["CHROME"]]
        # stream render.mjs output: its "frame N/M" lines are real progress (every 15 frames when EVA_PROGRESS_EVERY is set)
        J.log.write(f"$ {' '.join(map(str, cmd))}\n"); J.log.flush(); t = time.time()
        p = subprocess.Popen([str(c) for c in cmd], cwd=ENGINE_REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             env=dict(os.environ, EVA_PROGRESS_EVERY="15"))
        for line in p.stdout:
            J.log.write(line); m = _re.match(r"frame (\d+)/(\d+)", line)
            if m: _report(f"render_{i:02}", "frames", int(m.group(1)), int(m.group(2)))
        rc = p.wait(); J.log.write(f"  -> exit {rc} in {time.time() - t:.1f}s\n"); J.log.flush()
        if rc: raise subprocess.CalledProcessError(rc, cmd)
    J.stage(f"render_{i:02}", run)


def reset_for_regenerate(jd):
    """Regenerate preview: keep the upload, media and transcript (validate/media/asr/face), redo plan → page → render →
    preview finish from the same options."""
    st = Path(jd) / "stages"
    for f in st.glob("*.json"):
        if f.stem in ("plan", "page") or f.stem.startswith(("render_", "preview_")): f.unlink()


def page_args(J):
    """aspect + presenter footage size for the engine (EV.portrait, EV.src): see references/responsive-layout.md"""
    sw, sh_ = J.j.get("src_size", [1920, 1080])
    return ["--ar", J.j["options"].get("aspect", "16:9"), "--query", f"srcw={sw}&srch={sh_}"]


def preview_chunks(J):
    ps = J.j["options"]["preview_seconds"]
    return [i for i, (a, b) in enumerate(J.j["chunks"]) if a < ps]


# ───────────────────────────── finish ─────────────────────────────
def phrase_srt(transcript, out, max_chars=26, cjk=False, max_s=2.8, gap=.6):
    """Short caption phrases from eva-asr's aligned word times. ASR cues can run 8 s / 90 characters, which wraps into a
    wall of text on a phone screen; phrases break at sentence ends, pauses, ~2.8 s or max_chars. None if no word times."""
    try:
        t = transcript.read_text(encoding="utf-8"); d = json.loads(t[t.index("{"): t.rindex("}") + 1])
    except Exception: return None
    words = [w for sg in d.get("segments", []) for w in (sg.get("words") or []) if "start" in w and "end" in w and w.get("w", "").strip()]
    if not words: return None
    join = (lambda ws: "".join(w["w"].strip() for w in ws)) if cjk else (lambda ws: " ".join(w["w"].strip() for w in ws))
    cues, cur = [], []
    for w in words:
        ends = w["w"].strip()[-1:] in ".!?。！？"   # a sentence's last word may overflow a little rather than sit alone
        if cur and (len(join(cur + [w])) > max_chars + (10 if ends else 0) or w["start"] - cur[-1]["end"] > gap
                    or w["end"] - cur[0]["start"] > max_s + (.8 if ends else 0)):
            cues.append(cur); cur = []
        cur.append(w)
        if w["w"].strip()[-1:] in ".!?。！？": cues.append(cur); cur = []
    if cur: cues.append(cur)
    f = lambda x: f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{int(x % 60):02},{int(round(x % 1 * 1000)) % 1000:03}"
    srt = []
    for i, c in enumerate(cues, 1):
        a, z = c[0]["start"], max(c[-1]["end"], c[0]["start"] + .5)
        if i < len(cues): z = min(z + .25, cues[i][0]["start"] - .02)   # hold a little, never overlap the next phrase
        srt.append(f"{i}\n{f(a)} --> {f(z)}\n{join(c)}\n")
    out.write_text("\n".join(srt), encoding="utf-8"); return out


def portrait_ass(p):
    """captions.py writes a 1920x1080 ASS; for 9:16 masters re-declare the canvas and restyle so lines sit in the engine's
    caption zone (EV.zone('caption'): above the platform caption, buttons and like rail) instead of being stretched."""
    t = p.read_text(encoding="utf-8").replace("PlayResX: 1920", "PlayResX: 1080").replace("PlayResY: 1080", "PlayResY: 1920")
    sty = {"CN": "Noto Sans CJK SC Black,62", "EN": "Inter,38", "ENB": "Inter Black,64"}
    out = []
    for ln in t.splitlines():
        if ln.startswith("Style: "):
            f = ln[7:].split(","); name = f[0]; font, size = sty.get(name, f"{f[1]},{f[2]}").split(",")
            f[1], f[2] = font, size; f[19], f[20], f[21] = "110", "170", "440"   # MarginL, MarginR (like rail), MarginV
            ln = "Style: " + ",".join(f)
        out.append(ln)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")



def finish(jd, preview=False):
    tag = "preview" if preview else "final"; J = Job(jd, f"finish_{tag}.log"); o = J.j["options"]
    W = J.d / tag; W.mkdir(exist_ok=True); (J.d / "out").mkdir(exist_ok=True)
    idx = preview_chunks(J) if preview else range(len(J.j["chunks"]))
    end = J.j["chunks"][max(idx)][1]
    report = {"ok": False, "kind": tag, "warnings": []}

    def audio():
        sh(["node", ENGINE_REPO / "scripts/render.mjs", J.d / "auto/index.html", "--cues", W / "cues.json"] + page_args(J)
           + (["--browser", os.environ["CHROME"]] if os.environ.get("CHROME") else []), J.log, cwd=ENGINE_REPO)
        cues = [c for c in json.loads((W / "cues.json").read_text()) if c[1] < end - .05]
        (W / "cues.json").write_text(json.dumps(cues))
        sh([PY, ENGINE_REPO / "scripts/sfx.py", W / "cues.json", end, W / "sfx.wav"], J.log)
        sh(["ffmpeg", "-loglevel", "error", "-y", "-i", J.d / "src.mp4", "-t", f"{end:.3f}", "-c", "copy", W / "src.mp4"], J.log)

    def captions():
        cjk = J.j.get("language", "en") in ("zh", "ja", "ko", "yue")
        src = phrase_srt(J.d / "srt/talk.transcript.js", J.d / "srt/talk.phrases.srt", 26 if o.get("aspect") == "9:16" else 40, cjk) or J.d / "srt/talk.bilingual.srt"
        sh([PY, ENGINE_REPO / "scripts/captions.py", src, 0, end, W / "captions",
            CFG / ("captions.cjk.json" if cjk else "captions.en.json")], J.log)
        if o.get("aspect") == "9:16": portrait_ass(W / "captions.ass")

    def assemble():
        for f in W.glob("master_*.mp4"): f.unlink()
        sh([ENGINE_REPO / "scripts/assemble.sh", W / "src.mp4", W / "sfx.wav", W / "captions.ass", W / "master"]
           + [J.d / f"sec/c{i:02}.mp4" for i in idx], J.log, env=dict(os.environ, FONTSDIR=os.environ.get("FONTSDIR", "/usr/share/fonts")))

    def music():
        """music: none | track (music_tracks: 1-3 ids, one per section) | mix (AI Auto Mix). Rights-cleared tracks only
        (saas/worker/musicbed.py); scripts/music.py ducks the bed under the voice. Never blocks delivery."""
        mode = {"auto": "mix", "manual": "track"}.get(o.get("music"), o.get("music") or "none"); md = W / "music"
        if md.exists(): shutil.rmtree(md)
        md.mkdir(parents=True)
        src = W / "master_CN-EN.mp4"   # captions burned (the name comes from assemble.sh)
        final = J.d / "out" / ("preview_hd.mp4" if preview else "final.mp4")
        if final.exists(): final.unlink()
        if mode == "none":
            shutil.copy(src, final); report["music"] = {"mode": "none"}; return
        try:
            r = subprocess.run([PY, HERE / "musicbed.py", TRACKS, J.d / "plan.json", J.d / "transcript.js", md / "bed.wav", "--mode", mode,
                                "--tracks", ",".join(o.get("music_tracks") or [])], capture_output=True, text=True)
            J.log.write(r.stdout + r.stderr)
            if r.returncode: raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1])
            bed = json.loads(r.stdout.strip().splitlines()[-1])
            cfg = json.loads((CFG / "music.saas.json").read_text())
            cfg.update(background_music="manual", manual={"file": str(md / "bed.wav"), "start": 0}, jingles=False)
            (W / "music.json").write_text(json.dumps(cfg))
            sh([PY, ENGINE_REPO / "scripts/music.py", "plan", src, J.d / "srt/talk.bilingual.srt", md, "--config", W / "music.json",
                "--cues", W / "cues.json", "--storyboard", J.d / "storyboard.json"], J.log)
            sh([PY, ENGINE_REPO / "scripts/music.py", "apply", md / "music_plan.json", final, "--video", src], J.log)
            chk = json.loads((md / "music_check.json").read_text()) if (md / "music_check.json").exists() else {}
            report["music"] = dict(bed, speech_clear=chk.get("speech_clear"), sync_ok=chk.get("sync_ok"))
        except Exception as e:   # music must never block delivery: fall back to voice + SFX, and say so
            report["warnings"].append(f"music skipped: {e}"); report["music"] = {"mode": "none", "requested": mode}
            if final.exists(): final.unlink()
            shutil.copy(src, final)

    def deliver():
        final = J.d / "out" / ("preview_hd.mp4" if preview else "final.mp4")
        if preview:
            ps = o["preview_seconds"]; out = J.d / "out/preview.mp4"
            if out.exists(): out.unlink()
            font = ENGINE_REPO / "engine/fonts/Anton-Regular.ttf"
            pw, ph = PREVIEW[o.get("aspect", "16:9")]; fs = round(pw / 20)
            mark = f"drawtext=fontfile={font}:text='EVA VIDEO STUDIO · PREVIEW':fontsize={fs}:fontcolor=white@0.45:shadowcolor=black@0.35:shadowx=2:shadowy=2"
            vf = (f"scale={pw}:{ph},{mark}:x=(w-text_w)/2:y=h*0.30,{mark}:x=(w-text_w)/2:y=h*0.62")
            sh(["ffmpeg", "-loglevel", "error", "-y", "-i", final, "-t", ps, "-vf", vf, "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out], J.log)
            final = out   # keep out/preview_hd.mp4 (full-res, unwatermarked, never uploaded): post-render QA checks it
        shutil.copy(W / "captions.srt", J.d / "out/captions.srt")
        pr = probe(final); v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        lufs = subprocess.run(["ffmpeg", "-nostats", "-i", str(final), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
        I = [l.split(":")[1].split()[0] for l in lufs.splitlines() if l.strip().startswith("I:")]
        report.update({"ok": True, "file": final.name, "duration": float(pr["format"]["duration"]), "width": v["width"], "height": v["height"],
                       "fps": v["r_frame_rate"], "lufs": float(I[-1]) if I else None, "bytes": final.stat().st_size,
                       "source_frames": J.j["frames"], "planner": json.loads((J.d / "plan.json").read_text())["planner"]["source"]})

    for name, fn in (("audio", audio), ("captions", captions), ("assemble", assemble), ("music", music), ("deliver", deliver)):
        J.stage(f"{tag}_{name}", fn)
    report["stages"] = st = J.stages()
    report["cpu_s_total"] = round(sum(s.get("cpu_s", 0) for s in st.values()), 1)   # per-thread render CPU is counted once in-process; cloud runs measure per container
    (J.d / "out" / f"report_{tag}.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: report[k] for k in ("ok", "file", "duration", "width", "height", "lufs", "music", "warnings") if k in report}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("prepare"); p.add_argument("input"); p.add_argument("job"); p.add_argument("--options")
    p = sp.add_parser("render"); p.add_argument("job"); p.add_argument("chunk", type=int)
    p = sp.add_parser("finish"); p.add_argument("job"); p.add_argument("--preview", action="store_true")
    p = sp.add_parser("run"); p.add_argument("input"); p.add_argument("job"); p.add_argument("--options"); p.add_argument("--preview", action="store_true")
    p.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    a = ap.parse_args(argv)
    opts = json.loads(Path(a.options).read_text()) if getattr(a, "options", None) else None
    try:
        if a.cmd == "prepare": return prepare(a.input, a.job, opts)
        if a.cmd == "render": render(a.job, a.chunk); return 0
        if a.cmd == "finish": return finish(a.job, a.preview)
        rc = prepare(a.input, a.job, opts)
        if rc: return rc
        J = Job(a.job); idx = preview_chunks(J) if a.preview else range(len(J.j["chunks"]))
        with ThreadPoolExecutor(a.workers) as ex: list(ex.map(lambda i: render(a.job, i), idx))
        return finish(a.job, a.preview)
    except subprocess.CalledProcessError as e:
        print(f"STAGE FAILED: {e}  (see JOB/logs/)", file=sys.stderr); return 3


if __name__ == "__main__":
    sys.exit(main())
