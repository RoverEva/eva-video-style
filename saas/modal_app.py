"""EVA Video Studio · everything that runs in the cloud, on Modal (no local machine involved).

  api            ASGI web API for the website (saas/web/api.py): uploads, previews, Stripe Checkout + webhook, job status
  render_job     one order render (preview ≤ 10 s watermarked, or the paid full HD): prepare → chunks in parallel → finish
  prepare / render_chunk / finish   the stages (saas/worker/pipeline.py), each with retries; finished stages are skipped
  reconcile      every 10 min: paid renders that failed or went silent are retried once, then refunded automatically
  cleanup        daily: job working folders on the volume older than 2 days are removed (R2 lifecycle deletes media)
  setup          once per deploy (CI): R2 lifecycle + CORS when permitted (Stripe webhook: saas/deploy/stripe_webhook.py)

  modal deploy saas/modal_app.py                            # CI does this (.github/workflows/mvp-deploy.yml)
  modal run saas/modal_app.py::e2e --video URL_OR_PATH      # one real preview + paid render, with timings and cost

Modal Secrets (created by CI from the GitHub `production` environment): eva-r2 (R2_*), eva-stripe (STRIPE_SECRET_KEY),
eva-stripe-webhook (STRIPE_WEBHOOK_SECRET, written straight from Stripe by the deploy step), eva-config (EVA_SITE_URL,
EVA_ALLOWED_ORIGINS = exact site origin), eva-mail (optional RESEND_API_KEY, EVA_MAIL_FROM), eva-anthropic (optional ANTHROPIC_API_KEY).
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
# Least privilege per function (Modal Secrets = the secret manager; nothing secret is stored in R2 or the repo):
#   render stages   → R2 only (+ Anthropic for the planner)      render_job/reconcile → R2 + Stripe key (refunds) + mail + site
#   api             → R2 + Stripe key + webhook signing secret + site
_S = lambda n: modal.Secret.from_name(n)
LLM = [_S("eva-anthropic")] if os.environ.get("EVA_USE_LLM") == "1" else []
STAGE_SECRETS = [_S("eva-r2")]
ORCH_SECRETS = [_S("eva-r2"), _S("eva-stripe"), _S("eva-mail"), _S("eva-config")]
API_SECRETS = [_S("eva-r2"), _S("eva-stripe"), _S("eva-stripe-webhook"), _S("eva-config")]
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
    if not (key and frm and site) or "none" in (key, frm): return False
    link = f"{site}/video.html?id={job}#t={token}"
    r = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {key}"}, timeout=20, json={
        "from": frm, "to": [to], "subject": "Your EVA Video Studio video is ready",
        "html": f"<p>Your HD video is ready.</p><p><a href=\"{link}\">Download it here</a> (available for 7 days).</p><p>EVA Video Studio</p>"})
    return r.status_code < 300


# ───────────────────────────── web ─────────────────────────────
@app.function(image=web_image, secrets=API_SECRETS, cpu=0.25, memory=512, min_containers=0, timeout=60)
@modal.concurrent(max_inputs=50)
@modal.asgi_app(label="eva-api")
def api():
    _paths(); import api as A, store
    svc = A.Service(store.from_env(), counters, lambda kind, job, opts, attempt=0: render_job.spawn(kind, job, opts, attempt))

    def webhook_secret():   # Modal secret `eva-stripe-webhook`, set by saas/deploy/stripe_webhook.py ("unset" until then)
        v = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        return v if v.startswith("whsec_") else None
    return A.make_app(svc, webhook_secret)


# ───────────────────────────── render ─────────────────────────────
@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS + LLM, cpu=3.0, memory=6144, timeout=1200, retries=RETRY)
def prepare(job: str, opts: dict, kind: str = "preview"):
    _paths(); import store, pipeline, progress
    jobs.reload(); d = Path(f"/jobs/{job}"); d.mkdir(parents=True, exist_ok=True); t = time.time()
    if not (d / "input.mp4").exists(): store.from_env().download(f"uploads/{job}/input.mp4", d / "input.mp4")
    rn, mk = int(opts.get("regen_n") or 0), d / "work/regen_n"
    if kind == "preview" and rn and (d / "work").exists() and (mk.read_text().strip() if mk.exists() else "0") != str(rn):
        pipeline.reset_for_regenerate(d / "work"); mk.write_text(str(rn))   # same upload + settings, fresh plan/render
    pipeline.PROGRESS.set(progress.Reporter(counters, job, kind))
    rc = pipeline.prepare(d / "input.mp4", d / "work", opts); jobs.commit()
    j = json.loads((d / "work/job.json").read_text())
    return {"rc": rc, "chunks": j.get("chunks", []), "rejected": j.get("rejected"), "frames": j.get("frames"), "wall_s": round(time.time() - t, 1),
            "stages": {k: v.get("wall_s") for k, v in pipeline.Job(d / "work").stages().items()}}


@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS, cpu=1.0, memory=3072, timeout=900, retries=RETRY)
def render_chunk(job: str, i: int, kind: str = "preview"):
    _paths(); import pipeline, progress
    pipeline.PROGRESS.set(progress.Reporter(counters, job, kind))
    jobs.reload(); t = time.time(); pipeline.render(f"/jobs/{job}/work", i); jobs.commit()
    return {"chunk": i, "wall_s": round(time.time() - t, 1)}


@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS, cpu=2.0, memory=4096, timeout=900, retries=RETRY)
def finish(job: str, preview: bool):
    _paths(); import store, pipeline, progress
    pipeline.PROGRESS.set(progress.Reporter(counters, job, "preview" if preview else "final"))
    jobs.reload(); w = Path(f"/jobs/{job}/work"); t = time.time(); pipeline.finish(w, preview); jobs.commit()
    tag = "preview" if preview else "final"; rep = json.loads((w / f"out/report_{tag}.json").read_text())
    S = store.from_env(); ct = {".mp4": "video/mp4", ".srt": "text/plain", ".json": "application/json"}
    S.upload(w / "out" / ("preview.mp4" if preview else "final.mp4"), f"outputs/{job}/{tag}.mp4")
    S.upload(w / f"out/report_{tag}.json", f"outputs/{job}/report_{tag}.json", ct[".json"])
    if not preview: S.upload(w / "out/captions.srt", f"outputs/{job}/captions.srt", ct[".srt"])
    rep["finish_wall_s"] = round(time.time() - t, 1)
    return rep


@app.function(image=image, secrets=ORCH_SECRETS, cpu=0.25, memory=512, timeout=3600)
def render_job(kind: str, job: str, opts: dict, attempt: int = 0):
    """Orchestrates one render and records its state in jobs/<job>/<kind>.json (read by the API)."""
    _paths(); import store, progress
    S = store.from_env(); key = f"jobs/{job}/{kind}.json"; t0 = time.time(); preview = kind == "preview"
    if not preview:   # a paid render never runs alongside a regenerating preview (same working folder)
        while (S.get_json(f"jobs/{job}/preview.json") or {}).get("state") == "running" and time.time() - t0 < 1800: time.sleep(10)
    progress.reset(counters, job, kind, [])
    st = {"kind": kind, "attempt": attempt, "started": t0}
    def put(**kw): st.update(kw, updated_ts=time.time()); S.put_json(key, st); return st
    put(state="running", stage="preparing")
    try:
        import stripe_lite
        if not preview and opts.get("_fail_final") and stripe_lite.mode() == "test": raise RuntimeError("injected test failure (e2e-fail-final, test mode only)")
        p = prepare.remote(job, opts, kind)
        if p["rc"] == 2:
            put(state="rejected", stage="rejected", reason=p["rejected"])
        else:
            n = len(p["chunks"]); idx = [i for i, (a, b) in enumerate(p["chunks"]) if a < opts.get("preview_seconds", 10)] if preview else list(range(n))
            counters[progress.key(job, kind, "meta")] = {"chunks": idx, "t": time.time()}   # render progress denominator
            put(stage="rendering", chunks=len(idx))
            renders = list(render_chunk.starmap([(job, i, kind) for i in idx]))
            put(stage="finishing")
            rep = finish.remote(job, preview)
            walls = {"prepare": p["wall_s"], "render_chunk": sum(r["wall_s"] for r in renders), "finish": rep["finish_wall_s"]}
            usd = sum(cost(f, w) for f, w in walls.items()) + cost("render_job", time.time() - t0)
            put(state="done", stage="done", report={k: rep.get(k) for k in ("width", "height", "duration", "lufs", "music", "warnings", "bytes", "planner")},
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
@app.function(image=web_image, secrets=ORCH_SECRETS, schedule=modal.Period(minutes=10), timeout=300)
def reconcile():
    acts = _svc().reconcile(); print("reconcile:", acts); return acts


@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS, schedule=modal.Cron("17 3 * * *"), timeout=600)
def cleanup():
    """Volume working folders hold copies of customer media: remove after 2 days (R2 lifecycle rules handle the bucket)."""
    jobs.reload(); cut = time.time() - 2 * 86400; gone = 0
    for d in Path("/jobs").iterdir():
        if d.is_dir() and d.stat().st_mtime < cut: shutil.rmtree(d, ignore_errors=True); gone += 1
    jobs.commit()
    _paths(); import store
    S = store.from_env(); dropped = S.expire()   # same periods as the bucket lifecycle rules; works with an object-only token
    print("cleanup: removed", gone, "job folders;", dropped, "expired objects"); return {"folders": gone, "objects": dropped}


@app.function(image=web_image, secrets=ORCH_SECRETS, timeout=120)
def setup():
    """Bucket policy (lifecycle + CORS for the exact site origin) when the R2 token is allowed to set it; with the
    recommended object-only token these are set once in the Cloudflare dashboard and only verified by CI."""
    _paths(); import store, stripe_lite
    if stripe_lite.mode() != "test" and os.environ.get("EVA_ALLOW_LIVE") != "1": raise SystemExit("refusing: Stripe key is not a TEST key")
    out = {"bucket": store.from_env().setup_bucket(), "stripe_mode": stripe_lite.mode()}
    print(json.dumps(out)); return out
