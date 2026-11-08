"""Stage A · pre-render validation: fail early on deterministic errors before any frame is rendered.

ctx keys (all optional): input (raw video), srt, transcript (transcript.js), plan (plan.json path), face {x,y,h},
page (section index.html) + aspect + query, frames_dir (+ src_frames expected count), template/templates, scenes, events,
duration (seconds the render will cover).
"""
import json, os, re, shutil, subprocess
from pathlib import Path

from . import media, subs
from .config import Config
from .report import Report

HERE = Path(__file__).resolve().parent
KNOWN = {f"T{i:02d}" for i in range(1, 29)} - {"T18", "T22"}   # T18 and T22 are retired


def _group_missing(urls):
    """failed URLs -> [(kind, dir, [file names])]: one entry per image-sequence folder (f_00315.jpg ...), one per other file"""
    groups = {}
    for u in sorted(urls):
        path = u.replace("file://", "").split("?")[0]; d, _, name = path.rpartition("/")
        kind = ("font" if re.search(r"\.(ttf|otf|woff2?)$", name, re.I) else "image" if re.search(r"\.(jpe?g|png|webp|gif|svg|avif)$", name, re.I)
                else "script" if name.endswith((".js", ".mjs")) else "stylesheet" if name.endswith(".css") else "asset")
        key = (kind, d) if re.match(r"f_\d+\.", name) else (kind, path)
        groups.setdefault(key, []).append(name)
    return [(k, d if re.match(r"f_\d+\.", n[0]) else d.rpartition("/")[0], n) for (k, d), n in groups.items()]


def _guard(t, scenes, events, end, g=.35):
    ev = list(events or []) + [x for s in scenes or [] for x in (s["t0"], s["t1"])]
    return t < .5 or (end and t > end - .3) or any(abs(t - e) <= g for e in ev)


class Pre:
    def __init__(self, ctx, out_dir, config=None):
        self.ctx = ctx; self.cfg = config if isinstance(config, Config) else Config(config, ctx.get("category"))
        self.rep = Report("pre", out_dir, context={k: v for k, v in ctx.items()})
        self.out = Path(out_dir)

    def th(self, tpl=None, sec=None):
        d = self.cfg.for_template(tpl or self.ctx.get("template"))
        return d[sec] if sec else d

    def run(self):
        self.dur = self.ctx.get("duration")
        self.check_input(); self.check_srt(); self.check_transcript(); self.check_template_plan(); self.check_face(); self.check_frames()
        self.check_page()
        return self.rep.write()

    def check_input(self):
        R = self.rep; inp = self.ctx.get("input")
        if not inp: R.skip("PRE_INPUT", "no input video given"); return
        try:
            p = media.probe(inp)
        except Exception as e:
            R.add("PRE_INPUT", "FAIL", f"input video cannot be read: {e}", fix="re-export the video (H.264 MP4)"); return
        R.info["input"] = {"duration": p["duration"], "video": p["video"], "audio": p["audio"]}
        if not p["video"]: R.add("PRE_INPUT", "FAIL", "input has no video stream", fix="upload the talking-head video"); return
        if self.th(None, "render")["require_audio"] and not p["audio"]:
            R.add("PRE_INPUT", "FAIL", "input has no audio: the speaker's voice is required", fix="upload the video with its sound")
        v = p["video"]; self.dur = self.dur or v["duration"]
        if min(v["width"], v["height"]) < 720:
            R.add("PRE_INPUT_RES", "WARN", f"input is {v['width']}x{v['height']}: the presenter will be upscaled and look soft", fix="use a 1080p export")
        else: R.ran("PRE_INPUT_RES")
        if v["avg_fps"] and abs(v["avg_fps"] - v["fps"]) > .5:
            R.info["input_vfr"] = f"variable frame rate ({v['avg_fps']:.2f} avg vs {v['fps']:.2f}); extract_frames.sh resamples to 30 fps"
        R.ran("PRE_INPUT")

    def check_srt(self):
        R = self.rep; s = self.ctx.get("srt")
        if not s or not Path(s).exists(): R.skip("SRT_TIMING", "no SRT given"); return
        raw = Path(s).read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            R.add("SRT_SYNTAX", "FAIL", "SRT is not valid UTF-8", fix="save the SRT as UTF-8"); return
        probs, cues = subs.validate_srt(text, self.dur, self.th(None, "srt"), Path(s).name)
        for sev, chk, msg, t in probs: R.add(chk, sev, msg, t=t, fix="correct the cue timing/text in a copy of the SRT")
        for c in ("SRT_SYNTAX", "SRT_TIMING", "SRT_ORDER", "SRT_BOUNDS", "SRT_READ", "SRT_PAIRING"): R.ran(c)
        R.info["srt"] = {"cues": len(cues), "tracks": list(subs.tracks(cues))}

    def check_transcript(self):
        R = self.rep; tp = self.ctx.get("transcript")
        if not tp or not Path(tp).exists(): return
        try:
            s = Path(tp).read_text(encoding="utf-8"); d = json.loads(s[s.index("{"): s.rindex("}") + 1])
        except Exception as e:
            R.add("PRE_TRANSCRIPT", "FAIL", f"transcript.js cannot be parsed: {e}", fix="re-run scripts/asr.py"); return
        ws = [w for sg in d.get("segments", []) for w in (sg.get("words") or []) if "start" in w]
        bad = [w for w in ws if w.get("end", w["start"]) < w["start"]]
        back = sum(1 for a, b in zip(ws, ws[1:]) if b["start"] < a["start"] - .01)
        late = [w for w in ws if self.dur and w["start"] > self.dur + .05]
        if bad or back or late:
            R.add("PRE_TRANSCRIPT", "WARN", f"word timings: {len(bad)} end before start, {back} out of order, {len(late)} after the video end",
                  fix="re-run eva-asr; cards land on word times")
        else: R.ran("PRE_TRANSCRIPT", f"{len(ws)} timed words")

    def check_template_plan(self):
        R = self.rep; ctx = self.ctx
        if ctx.get("aspect") and ctx["aspect"] not in ("16:9", "9:16"):
            R.add("PRE_TEMPLATE", "FAIL", f"unknown aspect {ctx['aspect']}", fix="use 16:9 or 9:16")
        plan_secs = json.loads(Path(ctx["plan"]).read_text()).get("sections", []) if ctx.get("plan") and Path(ctx["plan"]).exists() else []
        tpls = [t for t in (ctx.get("templates") or [ctx.get("template")]) if t] + [s.get("template") for s in (ctx.get("scenes") or []) + plan_secs if s.get("template")]
        unknown = sorted({t for t in tpls if t not in KNOWN and t not in self.cfg.known_templates()})
        if unknown: R.add("PRE_TEMPLATE", "WARN", f"unknown template id(s) {', '.join(unknown)}: default thresholds apply", fix="add the template to qa/thresholds.json")
        R.ran("PRE_TEMPLATE")
        if not ctx.get("plan") or not Path(ctx["plan"]).exists(): return
        p = json.loads(Path(ctx["plan"]).read_text()); secs = p.get("sections", []); end = p.get("end") or self.dur
        probs = []
        if not secs: probs.append("plan has no sections")
        else:
            if abs(secs[0]["t0"]) > 1e-3: probs.append(f"first section starts at {secs[0]['t0']}s, not 0")
            if end and abs(secs[-1]["t1"] - end) > 1 / 30 + 1e-3: probs.append(f"last section ends at {secs[-1]['t1']}s, the video at {end}s")
            for a, b in zip(secs, secs[1:]):
                if abs(a["t1"] - b["t0"]) > 1e-3: probs.append(f"gap/overlap between sections at {a['t1']}s / {b['t0']}s")
            for s in secs:
                if s["t1"] <= s["t0"]: probs.append(f"section {s['t0']}–{s['t1']}s has no length")
        for sev, msg in [("FAIL", m) for m in probs]: R.add("PRE_PLAN", sev, msg, fix="re-run the planner; sections must tile the whole video")
        cap = {"16:9": 900 / 1080, "9:16": None}.get(ctx.get("aspect") or "16:9")
        for i, c in enumerate(p.get("cards", [])):
            if not (0 <= c["t_in"] < c["t_out"] <= (end or 1e9) + .05):
                R.add("PRE_PLAN", "FAIL", f"card {i} has impossible timing {c['t_in']}–{c['t_out']}s", t=(c["t_in"], c["t_out"]), fix="re-run the planner")
            pos = (c.get("spec") or {}).get("position")
            if pos:
                if pos["x"] < -1e-3 or pos["y"] < -1e-3 or pos["x"] + pos["w"] > 1.001 or pos["y"] + pos["h"] > 1.001:
                    R.add("PRE_PLAN", "FAIL", f"card {i} box {pos} reaches outside the frame", t=(c["t_in"], c["t_out"]), fix="keep card boxes inside the frame")
                elif cap and pos["y"] + pos["h"] > cap + 1e-3:
                    R.add("PRE_PLAN", "WARN", f"card {i} enters the caption zone", t=(c["t_in"], c["t_out"]), fix="move the card above the caption zone")
        R.ran("PRE_PLAN", f"{len(secs)} sections, {len(p.get('cards', []))} cards")

    def check_face(self):
        R = self.rep; f = self.ctx.get("face")
        if not f: R.skip("PRE_FACE", "no face calibration given"); return
        if not all(0 < f.get(k, -1) < 1 for k in ("x", "y", "h")):
            R.add("PRE_FACE", "FAIL", f"face calibration out of range: {f}", fix="re-run face calibration (x, y, h are fractions of the frame)"); return
        if f["y"] - f["h"] / 2 < -.01 or f["y"] + f["h"] / 2 > 1.01:
            R.add("PRE_FACE", "WARN", "the head is already cut off in the SOURCE footage (calibration reaches past the frame); template checks cannot fix that",
                  fix="re-shoot or re-frame the source")
        if str(f.get("source", "")).startswith("default") or f.get("warning"):
            R.add("PRE_FACE", "WARN", f"face calibration is a fallback ({f.get('source')}: {f.get('warning', 'no face found')}); presenter framing may be off",
                  fix="calibrate the face by hand (references/pipeline.md step 3)")
        R.ran("PRE_FACE")

    def check_frames(self):
        R = self.rep; d = self.ctx.get("frames_dir")
        if not d or not Path(d).is_dir(): return
        nums = sorted(int(m.group(1)) for f in os.listdir(d) if (m := re.match(r"f_(\d{5})\.jpg$", f)))
        exp = self.ctx.get("src_frames")
        missing = (set(range(nums[0], nums[-1] + 1)) - set(nums)) if nums else set()
        if not nums: R.add("ASSET_FRAMES", "FAIL", f"no f_00000.jpg frames in {d}", fix="scripts/extract_frames.sh RAW.mp4 media/eva")
        elif missing: R.add("ASSET_FRAMES", "FAIL", f"{len(missing)} presenter frames missing (first f_{min(missing):05d}.jpg)", fix="re-extract the frames")
        elif exp and len(nums) < exp: R.add("ASSET_FRAMES", "FAIL", f"{len(nums)} presenter frames, expected {exp}", fix="re-extract the frames")
        else: R.ran("ASSET_FRAMES", f"{len(nums)} frames")

    def check_page(self):
        R = self.rep; pg = self.ctx.get("page")
        if not pg: R.skip("ASSET_MISSING", "no section page given (--page)"); return
        if not shutil.which("node"): R.skip("ASSET_MISSING", "node not installed"); return
        out = self.out / "trace.json"
        cmd = ["node", str(HERE / "trace.mjs"), str(pg), "--out", str(out)] + (["--ar", self.ctx["aspect"]] if self.ctx.get("aspect") else []) \
              + (["--query", self.ctx["query"]] if self.ctx.get("query") else []) + (["--browser", os.environ["CHROME"]] if os.environ.get("CHROME") else [])
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(HERE.parent), timeout=900)
        if r.returncode == 3: R.skip("ASSET_MISSING", "playwright not installed"); return
        if r.returncode or not out.exists():
            R.add("PAGE_READY", "FAIL", f"page trace failed: {(r.stderr or r.stdout).strip()[-300:]}", fix="open the page with node scripts/render.mjs --stills to see the error"); return
        T = json.loads(out.read_text()); self.trace = T; R.info["trace"] = str(out)
        if not T.get("ready"):
            R.add("PAGE_READY", "FAIL", f"page never became ready (fonts/first frame did not load): {T.get('ready_error', '')[:200]}", fix="check fonts, scripts and the frames folder"); return
        R.ran("PAGE_READY")
        miss = {x["url"] for x in T["requests_failed"]} | {x["url"] for x in T["http_errors"]}
        self.missing = miss
        for kind, where, names in _group_missing(miss)[:15]:
            if len(names) > 1:
                R.add("ASSET_MISSING", "FAIL", f"{len(names)} {kind} files missing in {where[-110:]} ({names[0]} … {names[-1]})",
                      fix="extract/copy the missing frames (scripts/extract_frames.sh, scripts/matte.py) or shorten the section to the footage it has",
                      data={"dir": where, "count": len(names), "first": names[0], "last": names[-1]})
            else:
                R.add("ASSET_MISSING", "FAIL", f"missing {kind}: {(where + '/' + names[0])[-140:]}", fix="fix the path or add the file (check EV.evaDir and relative ../engine paths)")
        R.ran("ASSET_MISSING")
        for e in T["page_errors"][:5]:
            R.add("PAGE_ERROR", "FAIL", f"JavaScript error while rendering: {e[:200]}", fix="fix scenes.js; a thrown error stops the scene from building")
        R.ran("PAGE_ERROR")
        for e in [c for c in T["console_errors"] if "net::ERR_FILE_NOT_FOUND" not in c and "Failed to load resource" not in c][:3]:
            R.add("PAGE_ERROR", "WARN", f"console error: {e[:200]}", fix="check the browser console of the page")
        for fam, ok in (T.get("fonts") or {}).items():
            if not ok: R.add("ASSET_FONT", "FAIL", f"font '{fam}' is used by on-screen text but is not installed: text renders in a fallback font",
                             fix="install it (engine/fonts/README.md) or pass FONTSDIR")
        R.ran("ASSET_FONT", ", ".join(f for f, ok in (T.get("fonts") or {}).items() if ok))
        scenes, events, end = self.ctx.get("scenes") or [], self.ctx.get("events"), T.get("END")
        tpl_at = lambda t: next((s.get("template") for s in scenes if s["t0"] <= t < s["t1"]), self.ctx.get("template"))
        broken_seen = set()
        scale_bad, face_text, clips = [], [], []
        calib_fallback = str((self.ctx.get("face") or {}).get("source", "")).startswith("default")
        for s in T["samples"]:
            t = s["t"]; g = _guard(t, scenes, events, end); tpl = tpl_at(t); fth = self.th(tpl, "face")
            for b in s["broken"]:
                if b in broken_seen or any(u.endswith(re.sub(r"^(\.\./|\./)+", "", b.split("?")[0])) for u in miss): continue   # already reported as missing
                broken_seen.add(b); R.add("ASSET_IMAGE", "FAIL", f"image did not load: {b[-120:]}", t=t, template=tpl, fix="check the path / frame numbering (f_00000.jpg)")
            f = s.get("face")
            if f:
                cut = {k: v for k, v in f["cut"].items() if v > fth["warn_head_out"]}
                if cut and not fth["allow_crop"] and not g: clips.append((t, cut, tpl))
                if f["scale"] > fth["max_subject_scale"]: scale_bad.append((t, f["scale"], tpl, g))
            for o in s["over_face"]:
                if o["frac"] >= .08: face_text.append((t, o, tpl, g))
            for o in s["overflow"][:2]:
                R.add("LAYOUT_TEXT_OVERFLOW", "WARN", f"text overflows its box and is clipped: \"{o['txt']}\" ({o['scroll']}px in {o['client']}px)", t=t, template=tpl,
                      fix="shorten the text or let EV.fit() shrink it")
        # head cut by the window/frame: the geometry is exact but the head box comes from the face calibration, so only a
        # deep cut (>= 25% of the head) on >= 2 samples with a measured calibration is a confirmed FAIL; Stage B confirms it on pixels
        deep = [c for c in clips if max(c[1].values()) >= .25]
        for t, cut, tpl in clips:
            sev = "FAIL" if len(deep) >= 2 and max(cut.values()) >= .25 and not calib_fallback else "WARN"
            R.add("LAYOUT_FACE_CLIP", sev, f"presenter window cuts her head ({', '.join(f'{k} {v:.0%}' for k, v in cut.items())}) by the layout", t=t, template=tpl,
                  fix="keep the presenter at the footage's own scale and move her only as far as the whole head stays in the window and the frame")
        for c in ("ASSET_IMAGE", "LAYOUT_FACE_CLIP", "LAYOUT_TEXT_OVERFLOW"): R.ran(c)
        R.ran("LAYOUT_SCALE")
        for t, sc, tpl, g in scale_bad:
            fth = self.th(tpl, "face"); bad = sc > fth["fail_subject_scale"] and not g
            R.add("LAYOUT_SCALE", "FAIL" if bad and sum(1 for x in scale_bad if x[1] > fth["fail_subject_scale"] and not x[3]) >= 2 else "WARN",
                  f"layout enlarges the presenter to {sc:.2f}x the footage's own size (limit {fth['max_subject_scale']:.2f}x)", t=t, template=tpl,
                  fix="presenter keeps the footage's own scale; move her instead of zooming (lower the pose's s)")
        R.ran("LAYOUT_TEXT_FACE")
        for t, o, tpl, g in face_text:
            fth = self.th(tpl, "face")
            strong = fth["face_safe_text"] and not g and sum(1 for x in face_text if x[1]["txt"] == o["txt"]) >= 2
            R.add("LAYOUT_TEXT_FACE", "FAIL" if strong else "WARN", f"text is drawn on top of the presenter's face ({o['frac']:.0%} of the head): \"{o['txt']}\"",
                  t=t, template=tpl, fix="keep text behind or beside the presenter (T.sciAvoid / presenter on top)")
        # caption zone collisions (burned captions sit there)
        cz = T.get("caption")
        if cz:
            for s in T["samples"]:
                for x in s["text"]:
                    r = x["rect"]
                    ov = max(0, min(r["x"] + r["w"], cz["x"] + cz["w"]) - max(r["x"], cz["x"])) * max(0, min(r["y"] + r["h"], cz["y"] + cz["h"]) - max(r["y"], cz["y"]))
                    if ov > .3 * r["w"] * r["h"] and r["h"] > 18:
                        R.add("LAYOUT_CAPTION_ZONE", "WARN", f"on-screen text sits in the caption zone: \"{x['txt']}\"", t=s["t"], fix="move graphics above the caption zone")
                        break
            R.ran("LAYOUT_CAPTION_ZONE")
        # animation: a scene whose elements never change over its samples
        sth = self.th(None, "motion")
        by_scene = {}
        for s in T["samples"]:
            key = tuple(s["layers"]); by_scene.setdefault(key, []).append(s)
        declared = [(sc["t0"], sc["t1"]) for sc in scenes if sc.get("static")] + [tuple(r) for r in self.ctx.get("static_ranges") or []]
        for key, ss in by_scene.items():
            if declared and all(any(a - .35 <= s["t"] <= b + .35 for a, b in declared) for s in ss): continue   # intended static scene
            if len(ss) >= 3 and len({s["sig"] for s in ss}) == 1 and sth["expects_animation"]:
                idx = [i for i, sc in enumerate(T.get("scenes", [])) if i in key]
                if any(i in sth["static_scenes"] for i in idx): continue
                R.add("ANIM_STATIC", "WARN", f"scene layer(s) {list(key)} never change between {ss[0]['t']:.2f}s and {ss[-1]['t']:.2f}s (no animation runs)",
                      t=(ss[0]["t"], ss[-1]["t"]), fix="fine if the scene is meant to be static; otherwise check its update()")
        R.ran("ANIM_STATIC")


def run(ctx, out_dir, config=None):
    return Pre(ctx, out_dir, config).run()
