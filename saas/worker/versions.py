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
import json, os, shutil, subprocess, sys, time
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


ENGINE = Path(os.environ.get("EVA_ENGINE_REPO", Path(__file__).resolve().parents[2]))


def _qa_summary(r):
    """schema eva-qa/1 (qa/report.py): verdict PASS|WARN|FAIL, blocking = FAIL, counts per severity, issues, not_run"""
    v = str(r.get("verdict") or "").upper()
    return {"status": {"PASS": "pass", "WARN": "warn", "FAIL": "fail"}.get(v, "unknown"), "blocking": bool(r.get("blocking")),
            "counts": r.get("counts"), "issues": [{k: i.get(k) for k in ("check", "severity", "message", "t")} for i in (r.get("issues") or [])][:20],
            "not_run": [n.get("check") for n in (r.get("not_run") or [])], "qa_version": r.get("qa_version"), "elapsed_s": r.get("elapsed_s")}


def qa_dir(w, stage, preview=False): return Path(w) / "qa" / ("pre" if stage == "pre" else "post_preview" if preview else "post")


def run_qa(w, stage, preview=False, timeout=420):
    """Run the QA module (feat/video-qa v1.0) on a job folder: `python3 -m qa job W pre|post [--preview]`.
    EVA_QA=off skips it. In report mode QA never fails a render: its exit code is ignored, and a QA crash is recorded
    as status "error" (the video is still delivered). Returns (summary, report_path or None)."""
    if os.environ.get("EVA_QA", "report") == "off": return {"status": "off"}, None
    d = qa_dir(w, stage, preview)
    if stage == "pre" and (d / "qa-report.json").exists():   # same plan already checked (HD export of a checked version)
        return dict(_qa_summary(json.loads((d / "qa-report.json").read_text())), reused=True), d / "qa-report.json"
    t = time.time()
    try:
        r = subprocess.run([sys.executable, "-m", "qa", "job", str(w), stage] + (["--preview"] if preview and stage == "post" else []),
                           cwd=ENGINE, env=dict(os.environ, PYTHONPATH=str(ENGINE)), capture_output=True, text=True, timeout=timeout)
        out = (r.stdout + r.stderr)[-600:]
    except subprocess.TimeoutExpired: out = "timeout"
    p = d / "qa-report.json"
    if not p.exists(): return {"status": "error", "detail": out, "elapsed_s": round(time.time() - t, 1)}, None
    try: return _qa_summary(json.loads(p.read_text())), p
    except Exception as e: return {"status": "error", "detail": str(e)}, None


def qa_combined(pre, post):
    """one status for the version: worst of pre/post (error/pending never counts as a defect)"""
    rank = {"pass": 0, "warn": 1, "fail": 2}
    sts = [x.get("status") for x in (pre, post) if x and x.get("status") in rank]
    worst = max(sts, key=rank.get) if sts else (post or pre or {}).get("status", "pending_module")
    return {"status": worst, "blocking": bool((post or {}).get("blocking")), "mode": os.environ.get("EVA_QA", "report"), "pre": pre, "post": post}


def qa_result(w, tag):
    """post-render report written by assemble.sh (legacy layout) — kept for the legacy per-video flow"""
    for p in (w / tag / "master_qa" / "qa-report.json",):
        if p.exists():
            try: return _qa_summary(json.loads(p.read_text())), p
            except Exception: return {"status": "unreadable"}, p
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
    # QA reports saved with the version: post-render (main) + pre-render, with their readable summaries
    for stage, name in (("post", "qa-report.json"), ("pre", "qa-pre-report.json")):
        p = qa_dir(w, stage, preview) / "qa-report.json"
        if p.exists():
            S.upload(p, f"versions/{vid}/{name}", "application/json")
            if stage == "post": keys["qa_key"] = f"versions/{vid}/{name}"
            md = p.with_name("qa-summary.md")
            if md.exists(): S.upload(md, f"versions/{vid}/{name.replace('report.json', 'summary.md')}", "text/markdown")
    qa, _ = qa_result(w, tag)   # legacy location (assemble's own run), only used when the job-level run didn't happen
    S.upload(out / f"report_{tag}.json", f"versions/{vid}/report.json", "application/json")
    return keys, qa, {k: rep.get(k) for k in ("width", "height", "duration", "lufs", "music", "warnings", "bytes", "planner")}


def gate(qa):
    """critical QA failure blocks completion only when the gate is on (EVA_QA_GATE=block); default (report) records it.
    Only a blocking FAIL counts; warnings, errors, pending never block."""
    return "qa_failed" if os.environ.get("EVA_QA_GATE", "report") == "block" and (qa.get("blocking") or qa.get("status") == "fail") else "done"


def storage_usd(bytes_, days):   # R2 standard storage $0.015 per GB-month, egress free
    return round((bytes_ or 0) / 1e9 * 0.015 * days / 30, 6)
