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

    def worker(kind, job, opts, attempt=0):
        def run():
            key = f"jobs/{job}/{kind}.json"; t0 = time.time(); s = {"kind": kind, "attempt": attempt}
            def put(**kw): s.update(kw, updated_ts=time.time()); S.put_json(key, s)
            put(state="running", stage="preparing", progress=5)
            jd = st / "work" / job; jd.mkdir(parents=True, exist_ok=True); inp = jd / "input.mp4"
            if not inp.exists(): S.download(f"uploads/{job}/input.mp4", inp)
            if a.fixture_asr and not (jd / "work/stages/asr.json").exists():
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", inp], capture_output=True, text=True).stdout or 10)
                subprocess.run([sys.executable, HERE / "make_fixture.py", jd / "work", "-", str(min(dur, 30)), a.fixture_asr], check=True)
            env = dict(os.environ); log = open(jd / f"{kind}.log", "a")
            cmd = [sys.executable, REPO / "saas/worker/pipeline.py", "run", inp, jd / "work", "--options", jd / f"{kind}.opts.json", "--workers", "1"]
            (jd / f"{kind}.opts.json").write_text(json.dumps(opts)); put(stage="rendering", progress=30)
            rc = subprocess.run(cmd + (["--preview"] if kind == "preview" else []), stdout=log, stderr=subprocess.STDOUT, env=env).returncode
            if rc == 2: put(state="rejected", stage="rejected", reason=json.loads((jd / "work/job.json").read_text()).get("rejected"))
            elif rc: put(state="failed", stage="failed", error=f"exit {rc}")
            else:
                tag = "preview" if kind == "preview" else "final"
                S.upload(jd / "work/out" / ("preview.mp4" if kind == "preview" else "final.mp4"), f"outputs/{job}/{tag}.mp4")
                rep = json.loads((jd / f"work/out/report_{tag}.json").read_text())
                put(state="done", stage="done", progress=100, report={k: rep.get(k) for k in ("width", "height", "duration", "music")}, timing={"total_s": round(time.time() - t0, 1)})
            if kind == "final": print("final:", svc.on_final_result(job), flush=True)
        threading.Thread(target=run, daemon=True).start()

    class FakeStripe:
        StripeError = stripe_lite.StripeError
        def mode(self): return "test"
        def checkout(self, job, success_url, cancel_url, amount, title, attempt=0, email=None):
            FAKE[job] = success_url; return {"id": f"cs_local_{job}_{attempt}", "url": f"http://127.0.0.1:8000/_fakepay/{job}"}
        def refund(self, pi, job, reason=""): print("REFUND", pi, job, reason, flush=True); return {"id": "re_local"}

    FAKE = {}
    svc = api.Service(S, {}, worker, FakeStripe())
    app = api.make_app(svc, lambda: SECRET, local_store=S)

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

    site = REPO / "site"; (site / "config.js").write_text('window.EVA_API = "http://127.0.0.1:8000";\n')
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site))
    threading.Thread(target=http.server.ThreadingHTTPServer(("127.0.0.1", 8080), h).serve_forever, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


if __name__ == "__main__":
    main()
