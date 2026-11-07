#!/usr/bin/env python3
"""Offline check of browser_e2e.checkout_opened(): Stripe-hosted URL + cs_test_ session id, then the session is verified via
the Stripe API (stubbed here): test mode, $9.99 USD, belongs to the job, open/unpaid, returns to our video page.
No card entry anywhere. Network is stubbed with page.route, Stripe with a fake `call`."""
import os, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "web")]
from playwright.sync_api import sync_playwright
import browser_e2e as E, stripe_lite

JOB, CS = "abc123def456", "cs_test_a1B2c3D4e5F6g7H8"
URL = f"https://checkout.stripe.com/c/pay/{CS}#fidkdWxOYHwnPyd1blpx"
SESSION = {"id": CS, "livemode": False, "amount_total": 999, "currency": "usd", "metadata": {"job": JOB}, "client_reference_id": JOB,
           "status": "open", "payment_status": "unpaid", "success_url": f"https://eva-video-studio.vercel.app/video.html?id={JOB}&paid=1#t=x"}


def run(pg, out, session=None, url=URL):
    pg.goto(url)
    if session is None: os.environ.pop("STRIPE_SECRET_KEY", None)
    else: os.environ["STRIPE_SECRET_KEY"] = "rk_test_stub"; stripe_lite.call = lambda m, p, *a, **k: dict(session)
    return E.checkout_opened(pg, out, JOB, redact=["SECRET"])["checks"]


def main():
    out = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.route("https://checkout.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html", body="<title>Checkout</title><p>Pay $9.99</p>"))
        pg.route("https://evil.example/**", lambda r: r.fulfill(status=200, content_type="text/html", body="<title>fake</title>"))
        c = run(pg, out, SESSION); assert all(c.values()), c; print("verified test session:", c)
        c = run(pg, out, None); assert c["stripe_hosted_url"] and c["test_mode_session_id"] and not c["session_verified_via_api"], c
        c = run(pg, out, dict(SESSION, livemode=True)); assert not c["session_livemode_false"], c
        c = run(pg, out, dict(SESSION, amount_total=1)); assert not c["amount_999_usd"], c
        c = run(pg, out, dict(SESSION, metadata={"job": "zzz"})); assert not c["session_belongs_to_job"], c
        c = run(pg, out, SESSION, url=f"https://checkout.stripe.com/c/pay/cs_live_XYZ"); assert not c["test_mode_session_id"], c
        c = run(pg, out, SESSION, url=f"https://evil.example/c/pay/{CS}"); assert not c["stripe_hosted_url"], c
        assert (out / "stripe_fail.png").exists() and (out / "stripe_fail.html").exists()
        b.close()
    print("checkout-opened tests: ok")


if __name__ == "__main__":
    main()
