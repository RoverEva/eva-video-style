"""Build QA contexts from an EVA Video Studio job folder (saas/worker/pipeline.py layout) or from plan.json."""
import json
from pathlib import Path


def plan_scenes(plan):
    """plan.json sections -> scenes; card in/out times -> expected visual events"""
    secs = [{"t0": s["t0"], "t1": s["t1"], "template": s.get("template")} for s in plan.get("sections", [])]
    ev = sorted({round(c[k], 3) for c in plan.get("cards", []) for k in ("t_in", "t_out")})
    return secs, ev


def job_post(jd, preview=False):
    jd = Path(jd); j = json.loads((jd / "job.json").read_text())
    tag = "preview" if preview else "final"; W = jd / tag; o = j.get("options", {})
    video = jd / "out" / ("preview_hd.mp4" if preview else "final.mp4")
    plan = json.loads((jd / "plan.json").read_text()) if (jd / "plan.json").exists() else {}
    scenes, events = plan_scenes(plan)
    end = None
    if preview:
        chunks = j.get("chunks", []); ps = o.get("preview_seconds", 10)
        end = max(b for a, b in chunks if a < ps) if chunks else None
        scenes = [dict(s, t1=min(s["t1"], end)) for s in scenes if s["t0"] < end]
    frames = round(end * 30) if end else j.get("frames")
    trace = jd / "qa" / "pre" / "trace.json"
    tpls = o.get("templates") or []
    ctx = {"video": str(video), "clean": str(W / "master_Clean.mp4"), "source": str(jd / "media/eva"),
           "source_native": [j["input"]["width"], j["input"]["height"]] if j.get("input") else None,
           "audio_source": str(W / "src.mp4") if (W / "src.mp4").exists() else str(jd / "src.mp4"),
           "srt": str(W / "captions.srt"), "ass": str(W / "captions.ass"), "captions_burned": True,
           "aspect": o.get("aspect"), "kind": "final", "expected_frames": frames,
           "template": tpls[0] if len(tpls) == 1 else None, "scenes": scenes, "events": events,
           "face": json.loads((jd / "face.json").read_text()) if (jd / "face.json").exists() else plan.get("face")}
    if trace.exists(): ctx["trace"] = str(trace); ctx["trace_data"] = json.loads(trace.read_text())
    return ctx


def job_pre(jd):
    jd = Path(jd); j = json.loads((jd / "job.json").read_text()); o = j.get("options", {})
    plan = json.loads((jd / "plan.json").read_text()) if (jd / "plan.json").exists() else {}
    scenes, events = plan_scenes(plan)
    sw, sh = j.get("src_size", [1920, 1080])
    return {"input": j.get("input", {}).get("path") or str(jd / "src.mp4"), "srt": str(jd / "srt/talk.bilingual.srt"),
            "transcript": str(jd / "srt/talk.transcript.js"), "plan": str(jd / "plan.json") if plan else None,
            "face": json.loads((jd / "face.json").read_text()) if (jd / "face.json").exists() else None,
            "page": str(jd / "auto/index.html"), "aspect": o.get("aspect"), "query": f"srcw={sw}&srch={sh}",
            "templates": o.get("templates"), "template": (o.get("templates") or [None])[0] if len(o.get("templates") or []) == 1 else None,
            "scenes": scenes, "events": events, "duration": j.get("end"), "frames_dir": str(jd / "media/eva"), "src_frames": j.get("frames")}
