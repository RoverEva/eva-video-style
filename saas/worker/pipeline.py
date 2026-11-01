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

options (JSON): {"templates": ["T17","T20"], "template_mode": "single|multi|auto", "music": "auto|manual|none",
                 "music_track": null, "paid": false, "preview_seconds": 15}
Outputs in JOB_DIR/out: final.mp4 (1920x1080, 30 fps) or preview.mp4 (watermarked, 1280x720), captions.srt, report.json.
Exit codes: 2 input rejected (message in report.json), 3 stage failed (retryable), 0 ok.
"""
import argparse, json, os, resource, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE_REPO = Path(os.environ.get("EVA_ENGINE", HERE.parents[1])).resolve()   # eva-video-style checkout
CFG = HERE.parent / "config"
FPS, CHUNK_S = 30, 10.0
LIMITS = {"max_seconds": 60.5, "max_bytes": 200 * 1024 * 1024, "min_seconds": 3.0}
ALLOWED_MUSIC_LICENSES = {"CC0-1.0", "CC-BY-4.0", "licensed-commercial", "user-supplied"}
DEFAULT_OPTS = {"templates": ["T17"], "template_mode": "single", "music": "auto", "music_track": None, "paid": False, "preview_seconds": 15}
PY = sys.executable


class Reject(Exception): pass


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
        if mk.exists(): return
        t, c = time.time(), cpu_s(); self.log.write(f"\n== {name}\n")
        fn()
        if self.j: self.save()   # facts recorded by the stage (prepare is single-process)
        rec = {"ok": True, "wall_s": round(time.time() - t, 2), "cpu_s": round(cpu_s() - c, 2), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        mk.write_text(json.dumps(rec)); print(f"[{name}] {rec}", flush=True)


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
        if dur > LIMITS["max_seconds"]: raise Reject(f"video is {dur:.1f} s; the limit is 60 s")
        if dur < LIMITS["min_seconds"]: raise Reject("video is too short")
        w, h = int(st["video"]["width"]), int(st["video"]["height"])
        if w / h < 1.6: raise Reject(f"video is {w}x{h}; landscape 16:9 talking-head videos only for now")
        J.j["input"] = {"path": str(inp), "duration": dur, "width": w, "height": h, "bytes": inp.stat().st_size, "fps": st["video"]["r_frame_rate"]}

    def media():
        sh([ENGINE_REPO / "scripts/extract_frames.sh", inp, J.d / "media/eva"], J.log)
        n = len(list((J.d / "media/eva").glob("f_*.jpg")))
        J.j["frames"] = n; J.j["end"] = round(n / FPS, 3)
        # the voice source for assembly: same length as the frames (assemble.sh uses -shortest)
        sh(["ffmpeg", "-loglevel", "error", "-y", "-i", inp, "-map", "0:v:0", "-map", "0:a:0", "-t", f"{n / FPS:.3f}", "-c", "copy", J.d / "src.mp4"], J.log)

    def asr():
        (J.d / "srt").mkdir(exist_ok=True)
        for f in (J.d / "srt").glob("talk.*"): f.unlink()     # retry after a partial run
        sh([PY, ENGINE_REPO / "scripts/asr.py", J.d / "src.mp4", J.d / "srt/talk", "--config", CFG / "asr.en.json"], J.log)

    def face(): sh([PY, HERE / "face.py", J.d / "media/eva", J.d / "face.json"], J.log)

    def plan():
        sh([PY, HERE / "planner.py", J.d / "srt/talk.transcript.js", J.d, "--duration", J.j["end"],
            "--templates", ",".join(o["templates"]), "--mode", o["template_mode"], "--face", J.d / "face.json"], J.log)

    def page():
        if (J.d / "engine").exists(): shutil.rmtree(J.d / "engine")
        shutil.copytree(ENGINE_REPO / "engine", J.d / "engine")
        if (J.d / "auto").exists(): shutil.rmtree(J.d / "auto")
        shutil.copytree(HERE / "auto", J.d / "auto")
        shutil.copy(J.d / "srt/talk.transcript.js", J.d / "transcript.js")
        n = J.j["frames"]; step = int(CHUNK_S * FPS)
        J.j["chunks"] = [[f / FPS, min(n, f + step) / FPS] for f in range(0, n, step)]

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
        cmd = ["node", ENGINE_REPO / "scripts/render.mjs", J.d / "auto/index.html", "--out", out, "--from", a, "--to", b]
        if os.environ.get("CHROME"): cmd += ["--browser", os.environ["CHROME"]]
        sh(cmd, J.log, cwd=ENGINE_REPO)   # render.mjs resolves playwright from the cwd
    J.stage(f"render_{i:02}", run)


def preview_chunks(J):
    ps = J.j["options"]["preview_seconds"]
    return [i for i, (a, b) in enumerate(J.j["chunks"]) if a < ps]


# ───────────────────────────── finish ─────────────────────────────
def finish(jd, preview=False):
    tag = "preview" if preview else "final"; J = Job(jd, f"finish_{tag}.log"); o = J.j["options"]
    W = J.d / tag; W.mkdir(exist_ok=True); (J.d / "out").mkdir(exist_ok=True)
    idx = preview_chunks(J) if preview else range(len(J.j["chunks"]))
    end = J.j["chunks"][max(idx)][1]
    report = {"ok": False, "kind": tag, "warnings": []}

    def audio():
        sh(["node", ENGINE_REPO / "scripts/render.mjs", J.d / "auto/index.html", "--cues", W / "cues.json"]
           + (["--browser", os.environ["CHROME"]] if os.environ.get("CHROME") else []), J.log, cwd=ENGINE_REPO)
        cues = [c for c in json.loads((W / "cues.json").read_text()) if c[1] < end - .05]
        (W / "cues.json").write_text(json.dumps(cues))
        sh([PY, ENGINE_REPO / "scripts/sfx.py", W / "cues.json", end, W / "sfx.wav"], J.log)
        sh(["ffmpeg", "-loglevel", "error", "-y", "-i", J.d / "src.mp4", "-t", f"{end:.3f}", "-c", "copy", W / "src.mp4"], J.log)

    def captions():
        sh([PY, ENGINE_REPO / "scripts/captions.py", J.d / "srt/talk.en.srt", 0, end, W / "captions", CFG / "captions.en.json"], J.log)

    def assemble():
        for f in W.glob("master_*.mp4"): f.unlink()
        sh([ENGINE_REPO / "scripts/assemble.sh", W / "src.mp4", W / "sfx.wav", W / "captions.ass", W / "master"]
           + [J.d / f"sec/c{i:02}.mp4" for i in idx], J.log, env=dict(os.environ, FONTSDIR=os.environ.get("FONTSDIR", "/usr/share/fonts")))

    def music():
        mode = o["music"]; md = W / "music"
        if md.exists(): shutil.rmtree(md)
        src = W / "master_CN-EN.mp4"   # captions burned (English-only in this mode; the name comes from assemble.sh)
        cfg = json.loads((CFG / "music.saas.json").read_text()); cfg["background_music"] = mode
        if mode == "manual": cfg["manual"]["file"] = o.get("music_track")
        (W / "music.json").write_text(json.dumps(cfg))
        final = J.d / "out" / ("preview_hd.mp4" if preview else "final.mp4")
        if final.exists(): final.unlink()
        if mode == "none":
            shutil.copy(src, final); report["music"] = {"mode": "none"}; return
        try:
            sh([PY, ENGINE_REPO / "scripts/music.py", "plan", src, J.d / "srt/talk.en.srt", md, "--config", W / "music.json",
                "--cues", W / "cues.json", "--storyboard", J.d / "storyboard.json"], J.log)
            plan = json.loads((md / "music_plan.json").read_text()); lic = (plan.get("background") or {}).get("license")
            if o.get("paid") and lic not in ALLOWED_MUSIC_LICENSES:
                raise RuntimeError(f"background track license is {lic}: not cleared for paid output")
            sh([PY, ENGINE_REPO / "scripts/music.py", "apply", md / "music_plan.json", final, "--video", src], J.log)
            chk = json.loads((md / "music_check.json").read_text()) if (md / "music_check.json").exists() else {}
            report["music"] = {"mode": mode, "track": plan["background"]["file"], "license": lic, "jingles": len(plan.get("jingles", [])),
                               "sync_ok": chk.get("sync_ok"), "speech_clear": chk.get("speech_clear")}
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
            vf = (f"scale=1280:720,drawtext=fontfile={font}:text='EVA VIDEO STUDIO · PREVIEW':fontsize=64:fontcolor=white@0.42:"
                  f"x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.3:shadowx=2:shadowy=2")
            sh(["ffmpeg", "-loglevel", "error", "-y", "-i", final, "-t", ps, "-vf", vf, "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out], J.log)
            final.unlink(); final = out
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
