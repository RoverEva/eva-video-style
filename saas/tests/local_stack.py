#!/usr/bin/env python3
"""Run the whole product on one machine: web API (local storage), real render pipeline as the worker, a fake Stripe
Checkout page that sends a correctly SIGNED webhook, and the static site. For development and the browser test.

    python3 saas/tests/local_stack.py STATE_DIR [--fixture-asr "spoken text"]   → API :8000, site :8080

--fixture-asr: no eva-asr here (no torch/models), so the ASR stage is fed a hand-timed transcript; every other stage is real.
"""
import argparse, functools, http.server, json, os, subprocess, sys, threading, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parents[1]
sys.path[:0] = [str(HERE.parent / "web"), str(HERE.parent / "worker")]
os.environ.setdefault("EVA_ALLOWED_ORIGINS", "http://127.0.0.1:8080")   # local site only
import api, store, stripe_lite
import uvicorn
from starlette.responses import RedirectResponse
from starlette.routing import Route

SECRET = "whsec_local"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("state"); ap.add_argument("--fixture-asr"); a = ap.parse_args()
    st = Path(a.state); S = store.Local(st / "bucket", "http://127.0.0.1:8000")

    KV = {}   # stands in for the Modal Dict (rate limits + live progress)

    def worker(kind, job, opts, attempt=0):
        """same sequence as modal_app.render_job, in-process: real progress via the pipeline hook, regenerate resets"""
        import pipeline, progress
        def run():
            key = f"jobs/{job}/{kind}.json"; t0 = time.time(); s = {"kind": kind, "attempt": attempt}; preview = kind == "preview"
            def put(**kw): s.update(kw, updated_ts=time.time()); S.put_json(key, s)
            put(state="running", stage="preparing"); progress.reset(KV, job, kind, [])
            pipeline.PROGRESS.set(progress.Reporter(KV, job, kind))
            jd = st / "work" / job; jd.mkdir(parents=True, exist_ok=True); inp = jd / "input.mp4"; w = jd / "work"
            try:
                if not inp.exists(): S.download(f"uploads/{job}/input.mp4", inp)
                rn, mk = int(opts.get("regen_n") or 0), w / "regen_n"
                if preview and rn and w.exists() and (mk.read_text().strip() if mk.exists() else "0") != str(rn):
                    pipeline.reset_for_regenerate(w); mk.write_text(str(rn))
                if a.fixture_asr and not (w / "stages/asr.json").exists():
                    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", inp], capture_output=True, text=True).stdout or 10)
                    subprocess.run([sys.executable, HERE / "make_fixture.py", w, "-", str(min(dur, 30)), a.fixture_asr], check=True, stdout=subprocess.DEVNULL)
                    progress.Reporter(KV, job, kind)("asr", "start"); time.sleep(3)   # fixture ASR is instant; real eva-asr takes ~25 s
                if pipeline.prepare(inp, w, opts) == 2:
                    put(state="rejected", stage="rejected", reason=json.loads((w / "job.json").read_text()).get("rejected")); return
                J = pipeline.Job(w); idx = pipeline.preview_chunks(J) if preview else list(range(len(J.j["chunks"])))
                KV[progress.key(job, kind, "meta")] = {"chunks": idx, "t": time.time()}; put(stage="rendering")
                for i in idx: pipeline.render(w, i)
                put(stage="finishing"); pipeline.finish(w, preview)
                tag = "preview" if preview else "final"
                S.upload(w / "out" / ("preview.mp4" if preview else "final.mp4"), f"outputs/{job}/{tag}.mp4")
                rep = json.loads((w / f"out/report_{tag}.json").read_text())
                put(state="done", stage="done", report={k: rep.get(k) for k in ("width", "height", "duration", "music")}, timing={"total_s": round(time.time() - t0, 1)})
            except Exception as e:
                import traceback; traceback.print_exc(); put(state="failed", stage="failed", error=str(e)[:300])
            if not preview: print("final:", svc.on_final_result(job), flush=True)
        threading.Thread(target=run, daemon=True).start()

    class FakeStripe:
        StripeError = stripe_lite.StripeError
        def mode(self): return "test"
        def checkout(self, job, success_url, cancel_url, amount, title, attempt=0, email=None):
            FAKE[job] = success_url; return {"id": f"cs_local_{job}_{attempt}", "url": f"http://127.0.0.1:8000/_fakepay/{job}"}
        def refund(self, pi, job, reason=""): print("REFUND", pi, job, reason, flush=True); return {"id": "re_local"}

    FAKE = {}
    svc = api.Service(S, KV, worker, FakeStripe())
    # ── account features (My Videos, credits): local Postgres + stand-in sign-in + fake Stripe top-up ──
    import db as DBM, api_v2, versions, uuid
    DB = DBM.LocalPG()
    for m in sorted((REPO / "saas/db").glob("[0-9]*.sql")): subprocess.run(["psql", *DB.args, "-q", "-1", "-f", str(m)], check=True, capture_output=True)

    def run_version(kind, vid):
        import pipeline, progress
        preview = kind == "preview"; pk = "preview" if preview else "final"; t0 = time.time()
        v = DB.rpc("eva_version", version_id=vid)
        if not v or v["status"] not in ("queued", "running"): return
        DB.rpc("eva_set_running", version_id=vid); progress.reset(KV, vid, pk, [])
        pipeline.PROGRESS.set(progress.Reporter(KV, vid, pk))
        w = versions.work_dir(st / "jobs", v["project_id"], v["n"]); retain = 30 if preview else 90
        try:
            inp = versions.before_prepare(S, v["project_id"], v["upload_key"], w, None if preview else v["source_version"])
            if "e2e-fail" in (v.get("project_title") or ""): raise RuntimeError("injected local failure")
            if a.fixture_asr and not (w / "srt/.restored").exists() and not (w / "stages/asr.json").exists():
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", inp], capture_output=True, text=True).stdout or 10)
                subprocess.run([sys.executable, HERE / "make_fixture.py", w, "-", str(min(dur, 30)), a.fixture_asr], check=True, stdout=subprocess.DEVNULL)
                progress.Reporter(KV, vid, pk)("asr", "start"); time.sleep(2)
            opts = dict(v["options"], paid=not preview, reuse_plan=not preview, preview_seconds=10)
            if pipeline.prepare(inp, w, opts) == 2:
                return DB.rpc("eva_finish", version_id=vid, status="failed", retain_days=0, error=json.loads((w / "job.json").read_text()).get("rejected"))
            versions.after_prepare(S, v["project_id"], w)
            tq = time.time(); qa_pre = versions.run_qa(w, "pre")[0]; qa_pre_s = round(time.time() - tq, 1)
            if versions.duration(w): DB.rpc("eva_set_duration", project_id=v["project_id"], duration_s=versions.duration(w))
            J = pipeline.Job(w); idx = pipeline.preview_chunks(J) if preview else list(range(len(J.j["chunks"])))
            KV[progress.key(vid, pk, "meta")] = {"chunks": idx, "t": time.time()}
            for i in idx:
                if (DB.rpc("eva_version", version_id=vid) or {}).get("status") == "canceled": return
                pipeline.render(w, i)
            mode = os.environ.get("EVA_QA", "report"); os.environ["EVA_QA"] = "off"
            try: pipeline.finish(w, preview)
            finally: os.environ["EVA_QA"] = mode
            tq = time.time(); qa_post = versions.run_qa(w, "post", preview)[0]; qa_post_s = round(time.time() - tq, 1)
            keys, _, rep = versions.outputs(S, vid, w, preview); qa = versions.qa_combined(qa_pre, qa_post)
            DB.rpc("eva_finish", version_id=vid, status=versions.gate(qa), retain_days=retain, qa=qa, report=rep,
                   cost={"timing": {"total_s": round(time.time() - t0, 1), "qa_pre_s": qa_pre_s, "qa_post_s": qa_post_s},
                         "asr_cached": (w / "srt/.restored").exists()}, **keys)
        except Exception as e:
            import traceback; traceback.print_exc()
            DB.rpc("eva_finish", version_id=vid, status="failed", retain_days=0, error=str(e)[:300])

    class FakeStripeV2:
        StripeError = stripe_lite.StripeError
        def call(self, method, path, data=None, idem=None):
            sid = "cs_test_local_" + uuid.uuid4().hex[:10]; TOP[sid] = data; return {"id": sid, "url": f"http://127.0.0.1:8000/_fakepay_topup/{sid}"}
    TOP = {}
    acc = api_v2.Accounts(DB, S, KV, lambda kind, vid: threading.Thread(target=run_version, args=(kind, vid), daemon=True).start(), FakeStripeV2())
    app = api.make_app(svc, lambda: SECRET, local_store=S, accounts=acc)

    async def signin(req):   # stand-in for Supabase Auth: email → stable user id + bearer token
        email = req.query_params.get("email", "tester@example.com"); tok = "tok_" + uuid.uuid4().hex
        DB.tokens[tok] = {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "eva:" + email)), "email": email}
        from starlette.responses import JSONResponse
        return JSONResponse({"access_token": tok, "email": email})

    async def fakepay_topup(req):   # "pays" then sends the signed webhook exactly like Stripe (twice: retries must not double-credit)
        sid = req.path_params["sid"]; d = TOP[sid]
        ev = json.dumps({"type": "checkout.session.completed", "data": {"object": {"id": sid, "payment_status": "paid", "amount_total": 999,
              "metadata": d["metadata"], "livemode": False}}}).encode()
        import requests
        from starlette.concurrency import run_in_threadpool
        for _ in range(2):
            r = await run_in_threadpool(requests.post, "http://127.0.0.1:8000/api/stripe/webhook", data=ev, headers={"stripe-signature": stripe_lite.sign(ev, SECRET)})
            print("topup webhook:", r.status_code, r.text, flush=True)
        return RedirectResponse(d["success_url"].replace("https://eva-video-studio.vercel.app", "http://127.0.0.1:8080"))

    async def fakepay(req):   # stands in for Stripe's hosted page: "pays", then sends the signed webhook like Stripe does
        job = req.path_params["job"]
        ev = json.dumps({"type": "checkout.session.completed", "data": {"object": {"id": f"cs_{job}", "payment_status": "paid", "payment_intent": f"pi_{job}",
              "amount_total": 999, "metadata": {"job": job}, "customer_details": {"email": "test@example.com"}, "livemode": False}}}).encode()
        import requests
        from starlette.concurrency import run_in_threadpool
        r = await run_in_threadpool(requests.post, "http://127.0.0.1:8000/api/stripe/webhook", data=ev, headers={"stripe-signature": stripe_lite.sign(ev, SECRET)})
        print("webhook:", r.status_code, r.text, flush=True)
        return RedirectResponse(FAKE[job].replace("https://eva-video-studio.vercel.app", "http://127.0.0.1:8080"))
    app.router.routes.insert(0, Route("/_fakepay/{job}", fakepay))
    app.router.routes.insert(0, Route("/_fakepay_topup/{sid}", fakepay_topup))
    app.router.routes.insert(0, Route("/_local_signin", signin))

    site = REPO / "site"; (site / "config.js").write_text('window.EVA_API = "http://127.0.0.1:8000";\nwindow.EVA_LOCAL_AUTH = true;\n')
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site))
    threading.Thread(target=http.server.ThreadingHTTPServer(("127.0.0.1", 8080), h).serve_forever, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


if __name__ == "__main__":
    main()
