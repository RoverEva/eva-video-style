"""EVA Video Studio · per-version rendering helpers for account projects (My Videos).

Layout
  R2   projects/<pid>/source.mp4             original upload (kept for the preview retention period)
       projects/<pid>/cache/…                transcript (srt/talk.*), face.json — reused by every later version / HD export
       versions/<vid>/video.mp4 | thumb.jpg | plan.json | qa-report.json | report.json
  disk <jobs>/<pid>/v<n>/work                pipeline work dir of preview version n; its HD export renders in the same dir
                                             (full-resolution chunks of the same configuration are reused, never upscaled)
QA (module from the separate QA session, branch feat/video-qa): when merged, scripts/assemble.sh writes
<work>/<preview|final>/master_qa/qa-report.json (EVA_QA=report|block). We store it with the version; with
EVA_QA_GATE=block a critical FAIL marks the version qa_failed (reservation released, nothing charged). Until the module
is present the version records qa={"status": "pending_module"}.
"""
import json, os, shutil, subprocess
from pathlib import Path

CACHE_FILES = ["srt/talk.asr.json", "srt/talk.bilingual.srt", "srt/talk.transcript.js", "srt/talk.en.srt", "face.json"]


def work_dir(root, pid, n): return Path(root) / pid / f"v{n}" / "work"


def source_path(root, pid): return Path(root) / pid / "source.mp4"


def before_prepare(S, pid, upload_key, w, plan_from=None):
    """source download, transcript/face cache restore (skips ASR), saved plan for HD export (skips planner/AI)"""
    src = source_path(w.parent.parent.parent, pid)
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True); S.download(upload_key, src)
    w.mkdir(parents=True, exist_ok=True)
    if not (w / "stages/asr.json").exists():
        got = 0
        for f in CACHE_FILES:
            k = f"projects/{pid}/cache/{f}"
            if S.size(k):
                (w / f).parent.mkdir(parents=True, exist_ok=True); S.download(k, w / f); got += 1
        if got >= 3: (w / "srt/.restored").write_text("cache")
    if plan_from and not (w / "plan.json").exists() and S.size(f"versions/{plan_from}/plan.json"):
        S.download(f"versions/{plan_from}/plan.json", w / "plan.json")
    return src


def after_prepare(S, pid, w):
    """first version of a project: keep its transcript + face data for later versions (no second ASR)"""
    if (w / "srt/.restored").exists(): return 0
    n = 0
    for f in CACHE_FILES:
        if (w / f).exists() and not S.size(f"projects/{pid}/cache/{f}"):
            S.upload(w / f, f"projects/{pid}/cache/{f}", "application/octet-stream"); n += 1
    return n


def duration(w):
    try: return round(json.loads((w / "job.json").read_text())["input"]["duration"], 2)
    except Exception: return None


def qa_result(w, tag):
    for p in (w / tag / "master_qa" / "qa-report.json", w / "out" / tag / "master_qa" / "qa-report.json"):
        if p.exists():
            try: r = json.loads(p.read_text())
            except Exception: return {"status": "unreadable"}, p
            verdict = str(r.get("verdict") or r.get("status") or r.get("result") or r.get("overall") or "").upper()
            crit = r.get("critical") or r.get("failures") or []
            return {"status": "pass" if verdict.startswith("PASS") else "fail" if verdict.startswith("FAIL") else (verdict.lower() or "unknown"),
                    "critical": len(crit) if isinstance(crit, list) else crit, "summary": r.get("summary")}, p
    return {"status": "pending_module"}, None


def outputs(S, vid, w, preview):
    """upload the version's files; returns keys + QA + report"""
    tag = "preview" if preview else "final"; out = w / "out"
    video = out / ("preview.mp4" if preview else "final.mp4")
    rep = json.loads((out / f"report_{tag}.json").read_text())
    keys = {"video_key": f"versions/{vid}/video.mp4"}
    S.upload(video, keys["video_key"], "video/mp4")
    thumb = out / f"thumb_{tag}.jpg"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "1.5", "-i", str(video), "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "4", str(thumb)])
    if thumb.exists(): keys["thumb_key"] = f"versions/{vid}/thumb.jpg"; S.upload(thumb, keys["thumb_key"], "image/jpeg")
    if preview and (w / "plan.json").exists():   # the exact configuration HD export will reuse
        keys["plan_key"] = f"versions/{vid}/plan.json"; S.upload(w / "plan.json", keys["plan_key"], "application/json")
    qa, qp = qa_result(w, tag)
    if qp: keys["qa_key"] = f"versions/{vid}/qa-report.json"; S.upload(qp, keys["qa_key"], "application/json")
    S.upload(out / f"report_{tag}.json", f"versions/{vid}/report.json", "application/json")
    return keys, qa, {k: rep.get(k) for k in ("width", "height", "duration", "lufs", "music", "warnings", "bytes", "planner")}


def gate(qa):
    """critical QA failure blocks completion only when the gate is on (EVA_QA_GATE=block); default records the report"""
    return "qa_failed" if os.environ.get("EVA_QA_GATE", "report") == "block" and qa.get("status") == "fail" else "done"


def storage_usd(bytes_, days):   # R2 standard storage $0.015 per GB-month, egress free
    return round((bytes_ or 0) / 1e9 * 0.015 * days / 30, 6)
