#!/usr/bin/env python3
"""Web API + order state machine, offline: local storage, fake Stripe (real webhook signatures), fake render workers.
Covers limits, private tokens, presigned upload size, preview rate limits, checkout, verified webhooks, duplicate events
and duplicate payments, retry-then-refund, delivery, stuck-render reconciliation and the live-key guard."""
import json, os, sys, tempfile, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "web"))
import api, store, stripe_lite
from starlette.testclient import TestClient

SECRET = "whsec_test_123"


class FakeStripe:
    StripeError = stripe_lite.StripeError
    def __init__(self): self.sessions, self.refunds = [], []
    def mode(self): return "test"
    def checkout(self, job, success_url, cancel_url, amount, title, attempt=0, email=None):
        self.sessions.append(dict(job=job, success_url=success_url, amount=amount)); return {"id": f"cs_test_{job}_{attempt}", "url": f"https://checkout.stripe.test/{job}"}
    def refund(self, pi, job, reason="requested_by_customer"): self.refunds.append((pi, job, reason)); return {"id": f"re_{len(self.refunds)}"}


def main():
    tmp = Path(tempfile.mkdtemp()); S = store.Local(tmp / "bucket"); spawned, mails = [], []
    fs = FakeStripe(); svc = api.Service(S, {}, lambda kind, job, opts, attempt=0: spawned.append((kind, job, opts, attempt)), fs,
                                         mailer=lambda to, job, tok: mails.append((to, job, tok)) or True)
    c = TestClient(api.make_app(svc, lambda: SECRET, local_store=S))
    ok = lambda r, code=200: (r.status_code == code) or sys.exit(f"expected {code}, got {r.status_code}: {r.text}")

    # uploads: limits
    ok(c.post("/api/uploads", json={"name": "a.mp4", "size": 201 * 1024 * 1024, "type": "video/mp4"}), 400)
    ok(c.post("/api/uploads", json={"name": "a.avi", "size": 1000, "type": "video/x-msvideo"}), 400)
    data = os.urandom(5000)
    r = c.post("/api/uploads", json={"name": "talk.mp4", "size": len(data), "type": "video/mp4"}); ok(r); u = r.json(); job, tok = u["job"], u["token"]
    ok(c.put(u["put_url"].replace("http://testserver", ""), content=data[:-1]), 403)     # signed size enforced
    ok(c.put(u["put_url"].replace("http://testserver", ""), content=data))
    ok(c.get(f"/api/jobs/{job}?t=wrong"), 404); ok(c.get(f"/api/jobs/{job}"), 404)
    assert c.get(f"/api/jobs/{job}?t={tok}").json()["state"] == "uploaded"
    assert "token" not in json.dumps(S.get_json(f"orders/{job}.json")).replace("token_hash", "")   # raw token never stored

    # preview: option validation, then a render is queued (unpaid)
    ok(c.post(f"/api/jobs/{job}/preview", json={"token": tok, "aspect": "4:3", "templates": ["T17"]}), 400)
    ok(c.post(f"/api/jobs/{job}/preview", json={"token": tok, "aspect": "9:16", "templates": [], "template_mode": "single"}), 400)
    ok(c.post(f"/api/jobs/{job}/preview", json={"token": tok, "aspect": "9:16", "templates": ["T17", "T20"], "template_mode": "multi",
                                                "music": "track", "music_tracks": ["bright-pop", "nope", "inspire"]}))
    assert spawned[-1][0] == "preview" and spawned[-1][2]["paid"] is False and spawned[-1][2]["music_tracks"] == ["bright-pop", "inspire"]
    ok(c.post(f"/api/jobs/{job}/preview", json={"token": tok, "aspect": "9:16", "templates": ["T17"]})); assert len(spawned) == 1   # idempotent
    ok(c.post(f"/api/jobs/{job}/checkout", json={"token": tok}), 400)   # no checkout before the preview exists

    # per-IP preview limit (3/day)
    for i in range(3):
        r = c.post("/api/uploads", json={"name": "x.mp4", "size": 10, "type": "video/mp4"}); j = r.json()
        c.put(j["put_url"].replace("http://testserver", ""), content=b"0" * 10)
        ok(c.post(f"/api/jobs/{j['job']}/preview", json={"token": j["token"], "aspect": "16:9", "templates": ["T01"]}), 200 if i < 2 else 429)

    # worker finishes the preview → URL appears, checkout opens with the token in the return fragment
    S.put_json(f"jobs/{job}/preview.json", {"state": "done", "timing": {"total_s": 61}, "compute_usd": .006})
    v = c.get(f"/api/jobs/{job}?t={tok}").json(); assert v["preview"]["url"] and v["preview"]["metrics"]["compute_usd"] == .006
    r = c.post(f"/api/jobs/{job}/checkout", json={"token": tok}, headers={"origin": "https://eva-video-studio.vercel.app"}); ok(r)
    assert fs.sessions[-1]["amount"] == 999 and fs.sessions[-1]["success_url"].startswith("https://eva-video-studio.vercel.app/video.html") and tok in fs.sessions[-1]["success_url"]

    # webhook: signature required
    sess = {"id": "cs_1", "object": "checkout.session", "payment_status": "paid", "payment_intent": "pi_1", "amount_total": 999,
            "metadata": {"job": job}, "client_reference_id": job, "customer_details": {"email": "buyer@example.com"}, "livemode": False}
    ev = json.dumps({"type": "checkout.session.completed", "data": {"object": sess}}).encode()
    ok(c.post("/api/stripe/webhook", content=ev, headers={"stripe-signature": "t=1,v1=bad"}), 400)
    ok(c.post("/api/stripe/webhook", content=ev, headers={"stripe-signature": stripe_lite.sign(ev, "whsec_other")}), 400)
    ok(c.post("/api/stripe/webhook", content=ev, headers={"stripe-signature": stripe_lite.sign(ev, SECRET, int(time.time()) - 3600)}), 400)
    r = c.post("/api/stripe/webhook", content=ev, headers={"stripe-signature": stripe_lite.sign(ev, SECRET)}); ok(r)
    assert r.json()["result"] == "render started" and spawned[-1][:2] == ("final", job) and spawned[-1][2]["paid"] is True
    n = len(spawned)
    r = c.post("/api/stripe/webhook", content=ev, headers={"stripe-signature": stripe_lite.sign(ev, SECRET)}); assert r.json()["result"] == "duplicate event" and len(spawned) == n
    ev2 = json.dumps({"type": "checkout.session.completed", "data": {"object": dict(sess, id="cs_2", payment_intent="pi_2")}}).encode()
    r = c.post("/api/stripe/webhook", content=ev2, headers={"stripe-signature": stripe_lite.sign(ev2, SECRET)})
    assert r.json()["result"] == "duplicate payment refunded" and fs.refunds[-1][:2] == ("pi_2", job)

    # paid render fails → one automatic retry → fails again → automatic full refund
    S.put_json(f"jobs/{job}/final.json", {"state": "failed", "error": "boom"}); assert svc.on_final_result(job) == "retrying" and spawned[-1][3] == 2
    S.put_json(f"jobs/{job}/final.json", {"state": "failed", "error": "boom"}); assert svc.on_final_result(job) == "refunded" and fs.refunds[-1][0] == "pi_1"
    v = c.get(f"/api/jobs/{job}?t={tok}").json(); assert v["state"] == "refunded" and "url" not in v["final"]

    # a second order that succeeds → delivered, mail with a separate link token, HD URL visible
    r = c.post("/api/uploads", json={"name": "b.mp4", "size": 10, "type": "video/mp4"}, headers={"x-forwarded-for": "9.9.9.9"}); j = r.json()
    c.put(j["put_url"].replace("http://testserver", ""), content=b"0" * 10)
    ok(c.post(f"/api/jobs/{j['job']}/preview", json={"token": j["token"], "aspect": "9:16", "template_mode": "auto", "music": "mix"}, headers={"x-forwarded-for": "9.9.9.9"}))
    S.put_json(f"jobs/{j['job']}/preview.json", {"state": "done"})
    ev3 = json.dumps({"type": "checkout.session.completed", "data": {"object": dict(sess, id="cs_3", payment_intent="pi_3", metadata={"job": j["job"]})}}).encode()
    ok(c.post("/api/stripe/webhook", content=ev3, headers={"stripe-signature": stripe_lite.sign(ev3, SECRET)}))
    S.put_json(f"jobs/{j['job']}/final.json", {"state": "done", "report": {"width": 1080, "height": 1920, "duration": 10.0}, "timing": {"total_s": 95}, "compute_usd": .012})
    assert svc.on_final_result(j["job"]) == "delivered" and mails[-1][:2] == ("buyer@example.com", j["job"])
    v = c.get(f"/api/jobs/{j['job']}?t={mails[-1][2]}").json(); assert v["state"] == "delivered" and v["final"]["url"] and v["final"]["height"] == 1920

    # stuck paid render → reconciler marks it failed and retries
    r = c.post("/api/uploads", json={"name": "c.mp4", "size": 10, "type": "video/mp4"}, headers={"x-forwarded-for": "8.8.8.8"}); k = r.json()
    o = S.get_json(f"orders/{k['job']}.json"); o.update(options={"aspect": "9:16"}, paid={"payment_intent": "pi_9"}, state="rendering", final_attempts=1, final_started=time.time() - 3600)
    S.put_json(f"orders/{k['job']}.json", o)
    assert svc.reconcile().get(k["job"]) == "retrying"

    # live keys are refused unless explicitly allowed
    os.environ["STRIPE_SECRET_KEY"] = "sk_live_x"
    try: stripe_lite.key(); sys.exit("live key accepted")
    except stripe_lite.StripeError: pass
    print("api tests: ok")


if __name__ == "__main__":
    main()
