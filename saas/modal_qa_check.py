"""Ephemeral Modal check of QA in the real Modal runtime — NOT the production app.

    modal run saas/modal_qa_check.py --video saas/tests/media/education.mp4

Separate app name (eva-qa-check), no secrets, no volumes, no web endpoints, no schedules: it builds the same worker image
(saas/Dockerfile) and runs saas/tests/image_qa_check.py in one container (real eva-asr, renders, pre + post QA, face
detector check). The app stops when the run ends; production (eva-video-studio) is never touched.
"""
import json
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
app = modal.App("eva-qa-check")
image = modal.Image.from_dockerfile(str(ROOT / "saas/Dockerfile"), context_dir=str(ROOT))


@app.function(image=image, cpu=3.0, memory=6144, timeout=2400)
def check(video: bytes, aspect: str, templates: str) -> dict:
    import subprocess, time
    Path("/tmp/in.mp4").write_bytes(video); t = time.time()
    r = subprocess.run(["python3", "saas/tests/image_qa_check.py", "/tmp/in.mp4", "/tmp/out", "--aspect", aspect, "--templates", templates],
                       cwd="/app", capture_output=True, text=True)
    s = json.loads(Path("/tmp/out/summary.json").read_text()) if Path("/tmp/out/summary.json").exists() else {}
    return {"exit": r.returncode, "wall_s": round(time.time() - t, 1), "summary": s, "log_tail": (r.stdout + r.stderr)[-1500:] if r.returncode else ""}


@app.local_entrypoint()
def main(video: str = "saas/tests/media/education.mp4", aspect: str = "9:16", templates: str = "T17,T20"):
    res = check.remote(Path(video).read_bytes(), aspect, templates)
    print(json.dumps(res, indent=1))
    Path("modal_qa_check.json").write_text(json.dumps(res, indent=1))
    if res["exit"] != 0: raise SystemExit("QA check failed in the Modal container")
