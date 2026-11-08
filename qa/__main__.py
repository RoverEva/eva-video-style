"""Eva Video QA command line.

  python3 -m qa post VIDEO [--clean CLEAN.mp4] [--source RAW.mp4|FRAMES_DIR] [--srt X.srt] [--ass X.ass] [--aspect 9:16]
                     [--template T17] [--plan plan.json] [--expected-frames N] [--out DIR]     post-render QA of a finished video
  python3 -m qa pre  [--input RAW.mp4] [--srt X.srt] [--page SECTION/index.html] [--plan plan.json] [--face face.json]
                     [--aspect 9:16] [--template T17] [--out DIR]                                pre-render validation
  python3 -m qa srt  FILE.srt [--duration SECONDS]                                               SRT syntax + timing only
  python3 -m qa job  JOB_DIR (pre|post) [--preview]                                              EVA Video Studio job folder

Exit code: 0 = PASS or WARN, 1 = FAIL (blocking), 2 = usage/input error. Reports: OUT/qa-report.json, qa-summary.md, evidence/.
"""
import argparse, json, sys
from pathlib import Path

from . import jobctx, subs
from .config import Config


def _out(a, default):
    return Path(a.out or default)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 -m qa", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out"); common.add_argument("--config", help="JSON threshold overrides (same shape as qa/thresholds.json)")
    common.add_argument("--template"); common.add_argument("--category", choices=["talk", "ads", "science", "explain"])
    common.add_argument("--aspect", choices=["16:9", "9:16"]); common.add_argument("--plan"); common.add_argument("--face", help="face calibration JSON {x,y,h}")
    p = sp.add_parser("post", parents=[common]); p.add_argument("video"); p.add_argument("--clean"); p.add_argument("--source")
    p.add_argument("--source-offset", type=float, default=0); p.add_argument("--audio-source"); p.add_argument("--srt"); p.add_argument("--ass")
    p.add_argument("--no-burn", action="store_true", help="captions are not burned into VIDEO"); p.add_argument("--expected-frames", type=int)
    p.add_argument("--kind", choices=["final", "preview"], default="final"); p.add_argument("--trace"); p.add_argument("--static", default="",
                   help="intentionally static parts: scene indexes from --plan (e.g. 2,5) or time ranges (e.g. 1.5-4)")
    p.add_argument("--size", help="expected output size WxH (default: the standard size for --aspect)"); p.add_argument("--fps", type=float)
    p = sp.add_parser("pre", parents=[common]); p.add_argument("--input"); p.add_argument("--srt"); p.add_argument("--transcript")
    p.add_argument("--static", default="", help="time ranges that are intentionally static, e.g. 2-4,9.5-11 (or scene indexes with --plan)")
    p.add_argument("--page"); p.add_argument("--query", default=""); p.add_argument("--frames-dir")
    p = sp.add_parser("srt"); p.add_argument("file"); p.add_argument("--duration", type=float)
    p = sp.add_parser("job"); p.add_argument("job"); p.add_argument("stage", choices=["pre", "post"]); p.add_argument("--preview", action="store_true")
    p.add_argument("--config")
    a = ap.parse_args(argv)

    if a.cmd == "srt":
        probs, cues = subs.validate_srt(Path(a.file).read_text(encoding="utf-8-sig", errors="replace"), a.duration, Config()["srt"], Path(a.file).name)
        for sev, chk, msg, t in probs: print(f"{sev:4} {chk:12} {msg}")
        print(f"{len(cues)} cues, tracks: {', '.join(subs.tracks(cues)) or '-'}")
        return 1 if any(p[0] == "FAIL" for p in probs) else 0

    if a.cmd == "job":
        jd = Path(a.job)
        if a.stage == "pre":
            from . import pre
            d = pre.run(jobctx.job_pre(jd), jd / "qa" / "pre", a.config)
        else:
            from . import post
            d = post.run(jobctx.job_post(jd, a.preview), jd / "qa" / ("post_preview" if a.preview else "post"), a.config)
        print(json.dumps({k: d[k] for k in ("verdict", "counts", "blocking")}))
        return 1 if d["blocking"] else 0

    plan = json.loads(Path(a.plan).read_text()) if a.plan else {}
    scenes, events = jobctx.plan_scenes(plan)
    face = json.loads(Path(a.face).read_text()) if a.face else plan.get("face")
    cfg = Config(a.config, a.category)
    static_ranges = []
    for x in [x.strip() for x in a.static.split(",") if x.strip()]:   # scene index, or a time range a-b (seconds)
        if "-" in x: static_ranges.append([float(v) for v in x.split("-", 1)])
        elif x.isdigit() and int(x) < len(scenes): scenes[int(x)]["static"] = True
    if a.cmd == "post":
        from . import post
        ctx = {"video": a.video, "clean": a.clean, "source": a.source, "source_offset": a.source_offset, "audio_source": a.audio_source,
               "srt": a.srt, "ass": a.ass, "captions_burned": not a.no_burn, "aspect": a.aspect, "kind": a.kind, "expected_frames": a.expected_frames,
               "template": a.template, "category": a.category, "scenes": scenes, "events": events, "face": face,
               "size": [int(v) for v in a.size.lower().split("x")] if a.size else None, "fps": a.fps,
               "static_ranges": static_ranges or None}
        if a.trace: ctx["trace"] = a.trace; ctx["trace_data"] = json.loads(Path(a.trace).read_text())
        d = post.run({k: v for k, v in ctx.items() if v is not None}, _out(a, Path(a.video).with_suffix("").as_posix() + "_qa"), cfg)
    else:
        from . import pre
        ctx = {"input": a.input, "srt": a.srt, "transcript": a.transcript, "plan": a.plan, "face": face, "page": a.page, "query": a.query,
               "aspect": a.aspect, "template": a.template, "category": a.category, "scenes": scenes, "events": events, "frames_dir": a.frames_dir,
               "static_ranges": static_ranges or None}
        d = pre.run({k: v for k, v in ctx.items() if v is not None}, _out(a, "qa_pre"), cfg)
    print(f"QA {d['stage']}: {d['verdict']}  ({d['counts']['FAIL']} FAIL, {d['counts']['WARN']} WARN, {d['counts']['PASS']} PASS)")
    for i in d["issues"]:
        t = "" if not i["t"] else f"{i['t'][0]:.2f}s" + (f"-{i['t'][1]:.2f}s" if i["t"][1] != i["t"][0] else "")
        print(f"  {i['severity']:4} {i['check']:16} {t:14} {i['message']}")
    return 1 if d["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())
