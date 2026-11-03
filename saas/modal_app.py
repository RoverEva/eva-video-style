"""EVA Video Studio · everything that runs in the cloud, on Modal (no local machine involved).

  api            ASGI web API for the website (saas/web/api.py): uploads, previews, Stripe Checkout + webhook, job status
  render_job     one order render (preview ≤ 10 s watermarked, or the paid full HD): prepare → chunks in parallel → finish
  prepare / render_chunk / finish   the stages (saas/worker/pipeline.py), each with retries; finished stages are skipped
  reconcile      every 10 min: paid renders that failed or went silent are retried once, then refunded automatically
  cleanup        daily: job working folders on the volume older than 2 days are removed (R2 lifecycle deletes media)
  setup          once per deploy (CI): R2 lifecycle + CORS, Stripe webhook endpoint (secret stored in private R2)

  modal deploy saas/modal_app.py                            # CI does this (.github/workflows/mvp-deploy.yml)
  modal run saas/modal_app.py::e2e --video URL_OR_PATH      # one real preview + paid render, with timings and cost

Secrets (created by CI from GitHub secrets): eva-r2 (R2_*), eva-stripe (STRIPE_SECRET_KEY), eva-mail (RESEND_API_KEY,
EVA_MAIL_FROM; optional), eva-anthropic (ANTHROPIC_API_KEY; optional, deploy with EVA_USE_LLM=1).
"""
import json, os, shutil, sys, time, traceback
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
app = modal.App("eva-video-studio")
image = modal.Image.from_dockerfile(str(ROOT / "saas/Dockerfile"), context_dir=str(ROOT))
web_image = (modal.Image.debian_slim(python_version="3.12").pip_install("starlette==0.41.3", "requests==2.32.3", "boto3==1.35.90")
             .add_local_dir(str(ROOT / "saas/web"), "/app/saas/web"))
jobs = modal.Volume.from_name("eva-jobs", create_if_missing=True)
counters = modal.Dict.from_name("eva-counters", create_if_missing=True)
SECRETS = [modal.Secret.from_name("eva-r2"), modal.Secret.from_name("eva-stripe"), modal.Secret.from_name("eva-mail")] + \
          ([modal.Secret.from_name("eva-anthropic")] if os.environ.get("EVA_USE_LLM") == "1" else [])
RETRY = modal.Retries(max_retries=2, backoff_coefficient=2.0, initial_delay=5.0)
# Modal list prices (USD) used for the per-video cost estimate: CPU per physical core-second, memory per GiB-second
CPU_S, MEM_GIB_S = 0.0000131, 0.00000222
RES = {"prepare": (3.0, 6.0), "render_chunk": (1.0, 3.0), "finish": (2.0, 4.0), "render_job": (0.25, 0.5)}


def cost(fn, wall): c, m = RES[fn]; return wall * (c * CPU_S + m * MEM_GIB_S)


def _paths():
    for p in ("/app/saas/worker", "/app/saas/web"):
        if p not in sys.path: sys.path.insert(0, p)


def _svc():
    _paths(); import api, store
    def spawn(kind, job, opts, attempt=0): render_job.spawn(kind, job, opts, attempt)
    return api.Service(store.from_env(), counters, spawn, mailer=_mail)


def _mail(to, job, token):
    import requests
    key, frm, site = os.environ.get("RESEND_API_KEY"), os.environ.get("EVA_MAIL_FROM"), os.environ.get("EVA_SITE_URL", "")
    if not (key and frm and site): return False
    link = f"{site}/video.html?id={job}#t={token}"
    r = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {key}"}, timeout=20, json={
        "from": frm, "to": [to], "subject": "Your EVA Video Studio video is ready",
        "html": f"<p>Your HD video is ready.</p><p><a href=\"{link}\">Download it here</a> (available for 7 days).</p><p>EVA Video Studio</p>"})
    return r.status_code < 300


# ───────────────────────────── web ─────────────────────────────
_WH = {"t": 0, "v": None}


@app.function(image=web_image, secrets=SECRETS, cpu=0.25, memory=512, min_containers=0, timeout=60)
@modal.concurrent(max_inputs=50)
@modal.asgi_app(label="eva-api")
def api():
    _paths(); import api as A, store
    svc = A.Service(store.from_env(), counters, lambda kind, job, opts, attempt=0: render_job.spawn(kind, job, opts, attempt))

    def webhook_secret():   # written by `setup` into the private bucket; cached for a minute
        if time.time() - _WH["t"] > 60:
            _WH["v"] = (svc.s.get_json("config/stripe_webhook.json") or {}).get("secret") or os.environ.get("STRIPE_WEBHOOK_SECRET"); _WH["t"] = time.time()
        return _WH["v"]
    return A.make_app(svc, webhook_secret)


# ───────────────────────────── render ─────────────────────────────
@app.function(image=image, volumes={"/jobs": jobs}, secrets=SECRETS, cpu=3.0, memory=6144, timeout=1200, retries=RETRY)
def prepare(job: str, opts: dict):
    _paths(); import store, pipeline
    jobs.reload(); d = Path(f"/jobs/{job}"); d.mkdir(parents=True, exist_ok=True); t = time.time()
    if not (d / "input.mp4").exists(): store.from_env().download(f"uploads/{job}/input.mp4", d / "input.mp4")
    rc = pipeline.prepare(d / "input.mp4", d / "work", opts); jobs.commit()
    j = json.loads((d / "work/job.json").read_text())
    return {"rc": rc, "chunks": j.get("chunks", []), "rejected": j.get("rejected"), "frames": j.get("frames"), "wall_s": round(time.time() - t, 1),
            "stages": {k: v.get("wall_s") for k, v in pipeline.Job(d / "work").stages().items()}}


@app.function(image=image, volumes={"/jobs": jobs}, secrets=SECRETS, cpu=1.0, memory=3072, timeout=900, retries=RETRY)
def render_chunk(job: str, i: int):
    _paths(); import pipeline
    jobs.reload(); t = time.time(); pipeline.render(f"/jobs/{job}/work", i); jobs.commit()
    return {"chunk": i, "wall_s": round(time.time() - t, 1)}


@app.function(image=image, volumes={"/jobs": jobs}, secrets=SECRETS, cpu=2.0, memory=4096, timeout=900, retries=RETRY)
def finish(job: str, preview: bool):
    _paths(); import store, pipeline
    jobs.reload(); w = Path(f"/jobs/{job}/work"); t = time.time(); pipeline.finish(w, preview); jobs.commit()
    tag = "preview" if preview else "final"; rep = json.loads((w / f"out/report_{tag}.json").read_text())
    S = store.from_env(); ct = {".mp4": "video/mp4", ".srt": "text/plain", ".json": "application/json"}
    S.upload(w / "out" / ("preview.mp4" if preview else "final.mp4"), f"outputs/{job}/{tag}.mp4")
    S.upload(w / f"out/report_{tag}.json", f"outputs/{job}/report_{tag}.json", ct[".json"])
    if not preview: S.upload(w / "out/captions.srt", f"outputs/{job}/captions.srt", ct[".srt"])
    rep["finish_wall_s"] = round(time.time() - t, 1)
    return rep


@app.function(image=image, secrets=SECRETS, cpu=0.25, memory=512, timeout=3600)
def render_job(kind: str, job: str, opts: dict, attempt: int = 0):
    """Orchestrates one render and records its state in jobs/<job>/<kind>.json (read by the API)."""
    _paths(); import store
    S = store.from_env(); key = f"jobs/{job}/{kind}.json"; t0 = time.time(); preview = kind == "preview"
    st = {"kind": kind, "attempt": attempt, "started": t0}
    def put(**kw): st.update(kw, updated_ts=time.time()); S.put_json(key, st); return st
    put(state="running", stage="preparing", progress=5)
    try:
        p = prepare.remote(job, opts)
        if p["rc"] == 2:
            put(state="rejected", stage="rejected", reason=p["rejected"])
        else:
            n = len(p["chunks"]); idx = [i for i, (a, b) in enumerate(p["chunks"]) if a < opts.get("preview_seconds", 10)] if preview else list(range(n))
            put(stage="rendering", progress=30, chunks=len(idx))
            renders = list(render_chunk.starmap([(job, i) for i in idx]))
            put(stage="finishing", progress=80)
            rep = finish.remote(job, preview)
            walls = {"prepare": p["wall_s"], "render_chunk": sum(r["wall_s"] for r in renders), "finish": rep["finish_wall_s"]}
            usd = sum(cost(f, w) for f, w in walls.items()) + cost("render_job", time.time() - t0)
            put(state="done", stage="done", progress=100, report={k: rep.get(k) for k in ("width", "height", "duration", "lufs", "music", "warnings", "bytes", "planner")},
                timing={"total_s": round(time.time() - t0, 1), "prepare_s": p["wall_s"], "prepare_stages": p["stages"],
                        "chunk_s": [r["wall_s"] for r in renders], "finish_s": rep["finish_wall_s"]},
                compute_usd=round(usd, 4))
    except Exception as e:
        traceback.print_exc(); put(state="failed", stage="failed", error=f"{type(e).__name__}: {e}"[:500])
    if not preview:
        try: print("final result:", _svc().on_final_result(job))
        except Exception: traceback.print_exc()   # the reconciler will pick it up
    return st


# ───────────────────────────── operations ─────────────────────────────
@app.function(image=web_image, secrets=SECRETS, schedule=modal.Period(minutes=10), timeout=300)
def reconcile():
    acts = _svc().reconcile(); print("reconcile:", acts); return acts


@app.function(image=image, volumes={"/jobs": jobs}, secrets=SECRETS, schedule=modal.Cron("17 3 * * *"), timeout=600)
def cleanup():
    """Volume working folders hold copies of customer media: remove after 2 days (R2 lifecycle rules handle the bucket)."""
    jobs.reload(); cut = time.time() - 2 * 86400; gone = 0
    for d in Path("/jobs").iterdir():
        if d.is_dir() and d.stat().st_mtime < cut: shutil.rmtree(d, ignore_errors=True); gone += 1
    jobs.commit(); print("cleanup: removed", gone, "job folders"); return gone


@app.function(image=web_image, secrets=SECRETS, timeout=120)
def setup(api_url: str):
    _paths(); import store, stripe_lite
    S = store.from_env(); out = {"lifecycle": [r["ID"] for r in S.setup_bucket()], "stripe_mode": stripe_lite.mode()}
    cur = S.get_json("config/stripe_webhook.json") or {}
    url = api_url.rstrip("/") + "/api/stripe/webhook"
    if cur.get("url") != url: cur = {}
    new = stripe_lite.ensure_webhook(url, cur.get("id"))
    if new: S.put_json("config/stripe_webhook.json", dict(new, url=url)); out["webhook"] = "created " + new["id"]
    else: out["webhook"] = "kept " + cur["id"]
    print(json.dumps(out)); return out
