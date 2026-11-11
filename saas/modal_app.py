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
API_SECRETS = [_S("eva-r2"), _S("eva-stripe"), _S("eva-stripe-webhook"), _S("eva-config"), _S("eva-supabase")]
VERSION_SECRETS = [_S("eva-r2"), _S("eva-config"), _S("eva-supabase"), _S("eva-stripe")]   # Stripe key only to know test vs live mode
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
    return A.make_app(svc, webhook_secret, accounts=_accounts())


# ───────────────────────────── render ─────────────────────────────
@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS + LLM, cpu=3.0, memory=6144, timeout=1200, retries=RETRY)
def prepare(job: str, opts: dict, kind: str = "preview", ver: dict = None):
    _paths(); import store, pipeline, progress, versions
    jobs.reload(); d = Path(f"/jobs/{job}"); d.mkdir(parents=True, exist_ok=True); t = time.time()
    if ver:   # account version: shared project source + transcript cache + (HD) the saved plan
        S = store.from_env(); inp = versions.before_prepare(S, ver["pid"], ver["upload_key"], d / "work", ver.get("plan_from"))
        pipeline.PROGRESS.set(progress.Reporter(counters, ver["vid"], kind))
        rc = pipeline.prepare(inp, d / "work", opts); cached = versions.after_prepare(S, ver["pid"], d / "work") if rc == 0 else 0
        tq = time.time(); qa_pre = versions.run_qa(d / "work", "pre")[0] if rc == 0 else None   # Stage A: page trace before rendering
        qa_pre_s = round(time.time() - tq, 1); jobs.commit()
        j = json.loads((d / "work/job.json").read_text())
        return {"rc": rc, "chunks": j.get("chunks", []), "rejected": j.get("rejected"), "duration": versions.duration(d / "work"),
                "qa_pre": qa_pre, "qa_pre_s": qa_pre_s, "face_detector": _face_detector(),
                "wall_s": round(time.time() - t, 1), "asr_cached": (d / "work/srt/.restored").exists(), "cache_saved": cached,
                "stages": {k: v.get("wall_s") for k, v in pipeline.Job(d / "work").stages().items()}}
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
def render_chunk(job: str, i: int, kind: str = "preview", pkey: str = None):
    _paths(); import pipeline, progress
    pipeline.PROGRESS.set(progress.Reporter(counters, pkey or job, kind))
    jobs.reload(); t = time.time(); pipeline.render(f"/jobs/{job}/work", i); jobs.commit()
    return {"chunk": i, "wall_s": round(time.time() - t, 1)}


@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS, cpu=2.0, memory=4096, timeout=900, retries=RETRY)
def finish(job: str, preview: bool, vid: str = None):
    _paths(); import store, pipeline, progress, versions
    pipeline.PROGRESS.set(progress.Reporter(counters, vid or job, "preview" if preview else "final"))
    jobs.reload(); w = Path(f"/jobs/{job}/work"); t = time.time()
    if vid:   # account versions: QA runs once at job level (full context) instead of assemble's generic pass
        mode = os.environ.get("EVA_QA", "report"); os.environ["EVA_QA"] = "off"
        try: pipeline.finish(w, preview)
        finally: os.environ["EVA_QA"] = mode
        tq = time.time(); qa_post = versions.run_qa(w, "post", preview)[0]; qa_post_s = round(time.time() - tq, 1); jobs.commit()   # Stage B
        keys, _, rep = versions.outputs(store.from_env(), vid, w, preview)
        return {"keys": keys, "qa_post": qa_post, "qa_post_s": qa_post_s, "report": rep, "finish_wall_s": round(time.time() - t, 1)}
    pipeline.finish(w, preview); jobs.commit()
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


# ───────────────────────────── account versions (My Videos) ─────────────────────────────
@app.function(image=image, secrets=VERSION_SECRETS, cpu=0.25, memory=512, timeout=3600)
def render_version(kind: str, vid: str):
    """One preview or HD export of an account project. The reservation made by the API is captured only when the video
    (and, when the QA gate is on, its QA) succeeded; any failure / cancel releases it (free slot or credits back)."""
    _paths(); import db as DB, progress, versions
    D = DB.from_env(); t0 = time.time(); preview = kind == "preview"; pk = "preview" if preview else "final"
    v = D.rpc("eva_version", version_id=vid)
    if not v or v["status"] not in ("queued", "running"): return {"skipped": True}
    D.rpc("eva_set_running", version_id=vid); progress.reset(counters, vid, pk, [])
    job = f"{v['project_id']}/v{v['n']}"; retain = int(os.environ.get("EVA_PREVIEW_DAYS" if preview else "EVA_HD_DAYS", 30 if preview else 90))
    canceled = lambda: (D.rpc("eva_version", version_id=vid) or {}).get("status") == "canceled"
    try:
        opts = dict(v["options"], paid=not preview, reuse_plan=not preview, preview_seconds=10)
        ver = {"vid": vid, "pid": v["project_id"], "upload_key": v["upload_key"], "plan_from": None if preview else v["source_version"]}
        import stripe_lite
        if (v.get("project_title") or "").startswith("e2e-fail") and stripe_lite.mode() == "test":
            raise RuntimeError("injected test failure (e2e-fail project, Stripe test mode only)")   # live proof that failures release credits
        p = prepare.remote(job, opts, pk, ver)
        if p.get("duration"): D.rpc("eva_set_duration", project_id=v["project_id"], duration_s=p["duration"])
        if p["rc"] == 2: return D.rpc("eva_finish", version_id=vid, status="failed", retain_days=0, error=p["rejected"])
        if canceled(): return {"canceled": True}
        idx = [i for i, (a, b) in enumerate(p["chunks"]) if a < 10] if preview else list(range(len(p["chunks"])))
        counters[progress.key(vid, pk, "meta")] = {"chunks": idx, "t": time.time()}
        renders = list(render_chunk.starmap([(job, i, pk, vid) for i in idx]))
        if canceled(): return {"canceled": True}
        f = finish.remote(job, preview, vid)
        walls = {"prepare": p["wall_s"], "render_chunk": sum(r["wall_s"] for r in renders), "finish": f["finish_wall_s"]}
        compute = sum(cost(fn, w) for fn, w in walls.items()) + cost("render_job", time.time() - t0)
        costs = {"compute_usd": round(compute, 4), "storage_usd_est": versions.storage_usd(f["report"].get("bytes"), retain),
                 "ai_calls": 1 if (preview and f["report"].get("planner") == "llm") else 0, "asr_cached": p.get("asr_cached"),
                 "timing": {"total_s": round(time.time() - t0, 1), "prepare_s": p["wall_s"], "chunk_s": [r["wall_s"] for r in renders],
                            "finish_s": f["finish_wall_s"], "prepare_stages": p["stages"]}}
        qa = versions.qa_combined(p.get("qa_pre"), f.get("qa_post")); qa["face_detector"] = p.get("face_detector")
        costs["timing"].update(qa_pre_s=p.get("qa_pre_s"), qa_post_s=f.get("qa_post_s"))
        status = versions.gate(qa)   # report mode (default): always "done"; block: a blocking FAIL → qa_failed (released)
        return D.rpc("eva_finish", version_id=vid, status=status, retain_days=retain, qa=qa, report=f["report"], cost=costs,
                     error="critical QA failure" if status == "qa_failed" else None, **f["keys"])
    except Exception as e:
        traceback.print_exc()
        qa_fail = "exit status 3" in str(e) and "assemble" in str(e)   # QA module (EVA_QA=block) stops assemble with exit 3
        return D.rpc("eva_finish", version_id=vid, status="qa_failed" if qa_fail else "failed", retain_days=0, error=f"{type(e).__name__}: {e}"[:400])


def _face_detector():
    """which face detector QA can use in this container (the Haar cascade ships with opencv-python-headless)"""
    try:
        import cv2
        p = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        return {"opencv": cv2.__version__, "haar": os.path.exists(p) and not cv2.CascadeClassifier(p).empty()}
    except Exception as e: return {"error": str(e)[:120]}


def _accounts():
    _paths(); import api_v2, db as DB, store
    def spawn(kind, vid):
        call = render_version.spawn(kind, vid)
        counters[f"call:{vid}"] = call.object_id
    def cancel(vid):
        cid = counters.get(f"call:{vid}")
        if cid: modal.FunctionCall.from_id(cid).cancel()
    D = DB.from_env(); D.timeout = (5, 15)   # web requests: fail fast instead of holding the request (Modal cuts it at 60 s)
    return api_v2.Accounts(D, store.from_env(connect_timeout=5, read_timeout=10, attempts=2), counters, spawn, cancel=cancel)


# ───────────────────────────── operations ─────────────────────────────
@app.function(image=web_image, secrets=ORCH_SECRETS + [_S("eva-supabase")], schedule=modal.Period(minutes=10), timeout=300)
def reconcile():
    acts = _svc().reconcile()
    acc = _accounts()
    for vid in acc.db.rpc("eva_stuck", minutes=45):   # lost workers: release their reservations
        acts[vid] = acc.db.rpc("eva_finish", version_id=vid, status="failed", retain_days=0, error="stalled: no progress").get("reservation")
    print("reconcile:", acts); return acts


@app.function(image=image, volumes={"/jobs": jobs}, secrets=STAGE_SECRETS + [_S("eva-supabase")], schedule=modal.Cron("17 3 * * *"), timeout=600)
def cleanup():
    """Volume working folders hold copies of customer media: remove after 2 days (R2 lifecycle rules handle the bucket)."""
    jobs.reload(); cut = time.time() - 2 * 86400; gone = 0
    for d in Path("/jobs").iterdir():
        if d.is_dir() and d.stat().st_mtime < cut: shutil.rmtree(d, ignore_errors=True); gone += 1
    jobs.commit()
    _paths(); import store
    S = store.from_env(); dropped = S.expire()   # same periods as the bucket lifecycle rules; works with an object-only token
    acc = _accounts()
    for k in acc.db.rpc("eva_expire")["keys"]:    # My Videos retention: previews 30 d, HD 90 d, source = preview period
        try: S.delete(k); dropped += 1
        except Exception: pass
    print("cleanup: removed", gone, "job folders;", dropped, "expired objects"); return {"folders": gone, "objects": dropped}


@app.function(image=web_image, secrets=ORCH_SECRETS, timeout=120)
def setup():
    """Bucket policy (lifecycle + CORS for the exact site origin) when the R2 token is allowed to set it; with the
    recommended object-only token these are set once in the Cloudflare dashboard and only verified by CI."""
    _paths(); import store, stripe_lite
    if stripe_lite.mode() != "test" and os.environ.get("EVA_ALLOW_LIVE") != "1": raise SystemExit("refusing: Stripe key is not a TEST key")
    out = {"bucket": store.from_env().setup_bucket(), "stripe_mode": stripe_lite.mode()}
    print(json.dumps(out)); return out
