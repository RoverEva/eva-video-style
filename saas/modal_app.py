"""EVA Video Studio · cloud runner on Modal (Phase 1: cloud rendering proof of concept).

One job = prepare (validate, eva-asr, face, plan) → N render chunks in parallel containers → finish (SFX, captions,
assembly, music, checks) → results in private R2 + status.json. Nothing runs on a local machine.

  modal deploy saas/modal_app.py                                   # deploy (CI does this: .github/workflows/modal-deploy.yml)
  modal run saas/modal_app.py --video talk.mp4 --templates T17,T20 --mode multi --music auto
  modal run saas/modal_app.py --video https://…/talk.mp4 --preview  # 15 s watermarked preview only

Secrets (Modal dashboard → Secrets): `eva-r2` = R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET.
Optional `eva-anthropic` = ANTHROPIC_API_KEY (planner text choice; deploy with EVA_USE_LLM=1). Without it the
deterministic planner is used.
"""
import json, os, shutil, sys, time, uuid
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
app = modal.App("eva-video-studio")
image = modal.Image.from_dockerfile(str(ROOT / "saas/Dockerfile"), context_dir=str(ROOT))
jobs = modal.Volume.from_name("eva-jobs", create_if_missing=True)
music = modal.Volume.from_name("eva-music", create_if_missing=True)
SECRETS = [modal.Secret.from_name("eva-r2")] + ([modal.Secret.from_name("eva-anthropic")] if os.environ.get("EVA_USE_LLM") == "1" else [])
VOLS = {"/jobs": jobs, "/music": music}
RETRY = modal.Retries(max_retries=2, backoff_coefficient=2.0, initial_delay=5.0)


def _pl():
    sys.path.insert(0, "/app/saas/worker"); import pipeline; return pipeline


def _status(job_id, **kw):
    import storage
    p = Path(f"/jobs/{job_id}/status.json"); s = json.loads(p.read_text()) if p.exists() else {"job": job_id}
    s.update(kw, updated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(s))
    try: storage.upload(p, f"outputs/{job_id}/status.json", "application/json")
    except Exception as e: print("status upload failed:", e)
    return s


@app.function(image=image, volumes=VOLS, secrets=SECRETS, cpu=1.0, memory=2048, timeout=600)
def ingest(job_id: str, data: bytes = None, url: str = None):
    """Put the customer's video at uploads/<job>/input.mp4 (bytes from the CLI, or a URL)."""
    sys.path.insert(0, "/app/saas/worker"); import storage, urllib.request
    d = Path(f"/jobs/{job_id}"); d.mkdir(parents=True, exist_ok=True); f = d / "input.mp4"
    if data is not None: f.write_bytes(data)
    else: urllib.request.urlretrieve(url, f)
    storage.upload(f, f"uploads/{job_id}/input.mp4"); jobs.commit()
    return f.stat().st_size


@app.function(image=image, volumes=VOLS, secrets=SECRETS, cpu=3.0, memory=6144, timeout=1200, retries=RETRY)
def prepare(job_id: str, opts: dict):
    sys.path.insert(0, "/app/saas/worker"); import storage
    jobs.reload(); d = Path(f"/jobs/{job_id}"); d.mkdir(parents=True, exist_ok=True)
    if not (d / "input.mp4").exists(): storage.download(f"uploads/{job_id}/input.mp4", d / "input.mp4")
    (d / "options.json").write_text(json.dumps(opts))
    rc = _pl().prepare(d / "input.mp4", d / "work", opts); jobs.commit()
    j = json.loads((d / "work/job.json").read_text())
    return {"rc": rc, "chunks": len(j.get("chunks", [])), "rejected": j.get("rejected"), "frames": j.get("frames")}


@app.function(image=image, volumes=VOLS, secrets=SECRETS, cpu=1.0, memory=3072, timeout=900, retries=RETRY)
def render_chunk(job_id: str, i: int):
    jobs.reload(); t = time.time(); _pl().render(f"/jobs/{job_id}/work", i); jobs.commit()
    return {"chunk": i, "wall_s": round(time.time() - t, 1)}


@app.function(image=image, volumes=VOLS, secrets=SECRETS, cpu=2.0, memory=4096, timeout=900, retries=RETRY)
def finish(job_id: str, preview: bool):
    sys.path.insert(0, "/app/saas/worker"); import storage
    jobs.reload(); w = Path(f"/jobs/{job_id}/work"); _pl().finish(w, preview); jobs.commit()
    tag = "preview" if preview else "final"; rep = json.loads((w / f"out/report_{tag}.json").read_text())
    for f in (w / "out").iterdir():
        if f.suffix in (".mp4", ".srt", ".json"): storage.upload(f, f"outputs/{job_id}/{f.name}", {".mp4": "video/mp4", ".srt": "text/plain", ".json": "application/json"}[f.suffix])
    storage.upload(w / "plan.json", f"outputs/{job_id}/plan.json", "application/json")
    for lg in (w / "logs").glob("*.log"): storage.upload(lg, f"outputs/{job_id}/logs/{lg.name}", "text/plain")
    return rep


@app.function(image=image, volumes=VOLS, secrets=SECRETS, cpu=0.25, memory=512, timeout=3600)
def run_job(job_id: str, opts: dict, preview: bool = False):
    """Orchestrator. Each stage has its own retries; finished stages are skipped on retry (stage markers on the volume)."""
    sys.path.insert(0, "/app/saas/worker"); import storage
    t0 = time.time(); _status(job_id, state="preparing", options=opts, preview=preview)
    try:
        p = prepare.remote(job_id, opts)
        if p["rc"] == 2: return _status(job_id, state="rejected", reason=p["rejected"])
        n = p["chunks"]; ps = opts.get("preview_seconds", 15)
        idx = [i for i in range(n) if i * 10 < ps] if preview else list(range(n))
        _status(job_id, state="rendering", chunks=len(idx))
        renders = list(render_chunk.starmap([(job_id, i) for i in idx]))
        _status(job_id, state="finishing", renders=renders)
        rep = finish.remote(job_id, preview)
        name = "preview.mp4" if preview else "final.mp4"
        return _status(job_id, state="done", report=rep, wall_s=round(time.time() - t0, 1), output=f"outputs/{job_id}/{name}",
                       download_url=storage.presign_get(f"outputs/{job_id}/{name}", 3600, f"EVA_{job_id}.mp4"))
    except Exception as e:
        return _status(job_id, state="failed", error=f"{type(e).__name__}: {e}", wall_s=round(time.time() - t0, 1))


@app.function(image=image, volumes=VOLS, secrets=SECRETS, schedule=modal.Cron("17 3 * * *"), timeout=600)
def cleanup():
    """Daily: delete job working folders older than 2 days (R2 lifecycle rules delete the customer media)."""
    sys.path.insert(0, "/app/saas/worker"); import storage
    jobs.reload(); cut = time.time() - 2 * 86400; gone = 0
    for d in Path("/jobs").iterdir():
        if d.is_dir() and d.stat().st_mtime < cut: shutil.rmtree(d, ignore_errors=True); gone += 1
    jobs.commit()
    try: storage.apply_retention()
    except Exception as e: print("lifecycle:", e)
    print("cleanup: removed", gone, "job folders"); return gone


@app.local_entrypoint()
def main(video: str, templates: str = "T17", mode: str = "single", music: str = "auto", track: str = "", preview: bool = False, paid: bool = False):
    job_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    opts = {"templates": templates.split(","), "template_mode": mode, "music": music, "music_track": track or None, "paid": paid, "preview_seconds": 15}
    print("job", job_id, opts)
    if video.startswith("http"): size = ingest.remote(job_id, url=video)
    else: size = ingest.remote(job_id, data=Path(video).read_bytes())
    print(f"uploaded {size / 1e6:.1f} MB to R2 uploads/{job_id}/")
    s = run_job.remote(job_id, opts, preview)
    print(json.dumps(s, indent=1))
    if s.get("state") != "done": raise SystemExit(1)
