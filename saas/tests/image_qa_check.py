#!/usr/bin/env python3
"""Runs INSIDE the worker image (docker on CI, or a Modal container): the account-version render path with QA, on a real
upload, with real eva-asr — no database, no Stripe, no R2 (a local folder stands in for the bucket).

    python3 saas/tests/image_qa_check.py VIDEO OUT_DIR [--aspect 9:16] [--templates T23,T21]

Checks: face detector + model assets available to QA (OpenCV Haar cascade), Chrome/trace for Stage A, ASR models baked
into the image, pre-render QA (report), preview render, post-render QA on the preview, HD export of the same version
(saved plan reused, preview chunk reused), post-render QA on the HD master, reports saved with the version.
Report mode: QA never fails a render. Prints a JSON summary and writes OUT_DIR/summary.json; exit 1 on a render failure
or if QA could not run at all.
"""
import argparse, json, os, resource, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "worker"), str(HERE.parent / "web")]
import pipeline, versions, store

ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--aspect", default="9:16"); ap.add_argument("--templates", default="T23,T21"); a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True); R = {"env": {}, "runs": {}}
def cpu():   # CPU seconds used by this process + finished children (render.mjs/Chrome, ffmpeg, ASR, QA)
    u, c = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime + u.ru_stime + c.ru_utime + c.ru_stime
os.environ.setdefault("EVA_QA", "report")

# 1 · environment: face detector + assets QA needs
import cv2
hc = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml") if hasattr(cv2, "data") else None
R["env"]["opencv"] = cv2.__version__
R["env"]["haar_cascade"] = bool(hc and os.path.exists(hc) and not cv2.CascadeClassifier(hc).empty())
sys.path.insert(0, str(versions.ENGINE)); import qa.face as QF
try: R["env"]["qa_face_detector"] = QF.Detector().name
except Exception as e: R["env"]["qa_face_detector"] = f"error: {e}"
R["env"]["chrome"] = os.environ.get("CHROME") or "playwright default"
R["env"]["asr_models"] = [p.name for p in Path(os.environ.get("HF_HOME", "/root/.cache/huggingface")).glob("hub/models--*")][:6]
R["env"]["EVA_QA"], R["env"]["EVA_QA_GATE"] = os.environ.get("EVA_QA"), os.environ.get("EVA_QA_GATE")

S = store.Local(out / "bucket"); pid = "pimgcheck000"; up = f"projects/{pid}/source.mp4"; S.upload(Path(a.video), up)
w = versions.work_dir(out / "jobs", pid, 1)
opts = {"aspect": a.aspect, "templates": a.templates.split(","), "template_mode": "multi" if "," in a.templates else "single", "music": "mix",
        "music_tracks": [], "preview_seconds": 10}

for kind in ("preview", "hd"):
    preview = kind == "preview"; c0 = cpu(); t0 = time.time(); vid = ("v" if preview else "h") + "imgcheck001"
    inp = versions.before_prepare(S, pid, up, w, None if preview else "vimgcheck001")
    rc = pipeline.prepare(inp, w, dict(opts, paid=not preview, reuse_plan=not preview)); t_prep = time.time() - t0; c_prep = cpu() - c0
    if rc: R["runs"][kind] = {"rejected": json.loads((w / "job.json").read_text()).get("rejected")}; break
    if preview: versions.after_prepare(S, pid, w)
    cq = cpu(); tq = time.time(); qa_pre = versions.run_qa(w, "pre")[0]; t_pre = time.time() - tq; c_pre = cpu() - cq
    J = pipeline.Job(w); idx = pipeline.preview_chunks(J) if preview else list(range(len(J.j["chunks"])))
    cr = cpu(); tr = time.time()
    for i in idx: pipeline.render(w, i)
    t_render = time.time() - tr; c_render = cpu() - cr
    os.environ["EVA_QA"] = "off"
    cf = cpu(); tf = time.time()
    try: pipeline.finish(w, preview)
    finally: os.environ["EVA_QA"] = "report"
    t_finish = time.time() - tf; c_finish = cpu() - cf
    cq = cpu(); tq = time.time(); qa_post = versions.run_qa(w, "post", preview)[0]; t_post = time.time() - tq; c_post = cpu() - cq
    keys, _, rep = versions.outputs(S, vid, w, preview)
    qa = versions.qa_combined(qa_pre, qa_post)
    R["runs"][kind] = {"status": versions.gate(qa), "size": [rep.get("width"), rep.get("height")], "duration": rep.get("duration"),
                       "lufs": rep.get("lufs"), "planner": rep.get("planner"), "language": J.j.get("language"),
                       "asr_cached": (w / "srt/.restored").exists(), "plan_reused": not preview,
                       "qa": {"status": qa["status"], "pre": {k: (qa_pre or {}).get(k) for k in ("status", "counts", "not_run", "reused", "detail")},
                              "post": {k: (qa_post or {}).get(k) for k in ("status", "counts", "not_run", "detail")},
                              "issues": [(i["check"], i["severity"], (i["message"] or "")[:110]) for i in ((qa_pre or {}).get("issues") or []) + ((qa_post or {}).get("issues") or [])]},
                       "saved_with_version": sorted(p.name for p in (out / "bucket/versions" / vid).glob("*")),
                       "seconds": {"prepare": round(t_prep, 1), "qa_pre": round(t_pre, 1), "render": round(t_render, 1), "finish": round(t_finish, 1),
                                   "qa_post": round(t_post, 1), "total": round(time.time() - t0, 1)},
                       "cpu_s": {"prepare": round(c_prep, 1), "qa_pre": round(c_pre, 1), "render": round(c_render, 1), "finish": round(c_finish, 1),
                                 "qa_post": round(c_post, 1)},
                       "chunks": len(idx), "output_bytes": rep.get("bytes"),
                       "asr_s": (pipeline.Job(w).stages().get("asr") or {}).get("wall_s"),
                       "planner_usage": json.loads((w / "plan.json").read_text())["planner"].get("usage") if (w / "plan.json").exists() else None}

faces = [json.loads((w / "face.json").read_text()).get("source", "")] if (w / "face.json").exists() else [""]   # the worker's face locator result
R["env"]["worker_face"] = faces[0]
(out / "summary.json").write_text(json.dumps(R, indent=1)); print(json.dumps(R, indent=1))
ok = R["env"]["haar_cascade"] and R["env"]["qa_face_detector"] == "opencv-haar" and all(f.startswith("opencv") for f in faces) and all(r.get("status") == "done" for r in R["runs"].values()) and len(R["runs"]) == 2 \
     and all(r["qa"]["post"]["status"] in ("pass", "warn", "fail") for r in R["runs"].values())
sys.exit(0 if ok else 1)
