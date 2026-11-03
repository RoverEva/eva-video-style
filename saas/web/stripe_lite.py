"""EVA Video Studio · the four Stripe calls the MVP needs, over Stripe's REST API (no SDK).

checkout(job, ...)          Checkout Session, $9.99 one-off, job id in metadata (server-side price, never from the browser)
verify(payload, header)     webhook signature check (Stripe-Signature: t=..., v1=HMAC-SHA256(secret, "t.payload"))
refund(payment_intent, ...) full refund (render failed after retries, or a duplicate payment for the same video)
ensure_webhook(url)         creates the webhook endpoint once and returns its signing secret (used by setup)

Live keys are refused unless EVA_ALLOW_LIVE=1 is set on purpose (Live payments stay off until end-to-end tests pass).
"""
import hashlib, hmac, os, time
import requests

API = "https://api.stripe.com/v1"
EVENTS = ["checkout.session.completed", "checkout.session.async_payment_succeeded", "checkout.session.async_payment_failed"]


class StripeError(Exception): pass


def key():
    k = os.environ.get("STRIPE_SECRET_KEY", "")
    if not k: raise StripeError("STRIPE_SECRET_KEY is not set")
    if k.startswith(("sk_live_", "rk_live_")) and os.environ.get("EVA_ALLOW_LIVE") != "1":
        raise StripeError("live Stripe key refused: set EVA_ALLOW_LIVE=1 only after the end-to-end tests pass")
    return k


def mode(): k = os.environ.get("STRIPE_SECRET_KEY", ""); return "live" if "_live_" in k else "test" if k else "off"


def _flat(d, pre=""):
    out = []
    for k, v in d.items():
        name = f"{pre}[{k}]" if pre else k
        if isinstance(v, dict): out += _flat(v, name)
        elif isinstance(v, list):
            for i, x in enumerate(v): out += _flat(x, f"{name}[{i}]") if isinstance(x, dict) else [(f"{name}[{i}]", x)]
        elif v is not None: out.append((name, "true" if v is True else "false" if v is False else v))
    return out


def call(method, path, data=None, idem=None):
    h = {"Stripe-Version": "2024-06-20"}
    if idem: h["Idempotency-Key"] = idem
    r = requests.request(method, API + path, auth=(key(), ""), data=_flat(data or {}), headers=h, timeout=30)
    j = r.json()
    if r.status_code >= 400: raise StripeError(j.get("error", {}).get("message", r.text))
    return j


def checkout(job, success_url, cancel_url, amount_cents, title, attempt=0, email=None):
    return call("POST", "/checkout/sessions", {
        "mode": "payment", "client_reference_id": job, "success_url": success_url, "cancel_url": cancel_url,
        "customer_email": email, "metadata": {"job": job},
        "payment_intent_data": {"metadata": {"job": job}, "description": f"EVA Video Studio · HD video {job}"},
        "line_items": [{"quantity": 1, "price_data": {"currency": "usd", "unit_amount": amount_cents,
                        "product_data": {"name": title, "description": "Full-length 1080p MP4, no watermark, delivered automatically"}}}],
        "custom_text": {"submit": {"message": "Your HD video starts rendering as soon as payment is confirmed. The download appears on your video page."}},
        "expires_at": int(time.time()) + 3600,
    }, idem=f"checkout-{job}-{attempt}")


def refund(payment_intent, job, reason="requested_by_customer"):
    return call("POST", "/refunds", {"payment_intent": payment_intent, "reason": reason, "metadata": {"job": job}}, idem=f"refund-{payment_intent}")


def verify(payload: bytes, header: str, secret: str, tolerance=300):
    parts = {}
    for item in (header or "").split(","):
        k, _, v = item.partition("="); parts.setdefault(k.strip(), []).append(v.strip())
    try: t = int(parts["t"][0])
    except (KeyError, ValueError): raise StripeError("bad signature header")
    if abs(time.time() - t) > tolerance: raise StripeError("signature timestamp outside tolerance")
    want = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(want, s) for s in parts.get("v1", [])): raise StripeError("signature mismatch")
    return True


def sign(payload: bytes, secret: str, t=None):
    """test helper: the header Stripe would send"""
    t = t or int(time.time()); return f"t={t},v1=" + hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()


def ensure_webhook(url, old_id=None):
    """(Re)create the endpoint for `url` and return {id, secret}. Stripe shows a secret only at creation, so an endpoint we
    hold no secret for is replaced."""
    for ep in call("GET", "/webhook_endpoints?limit=100").get("data", []):
        if ep["url"] == url and ep["id"] != old_id: call("DELETE", f"/webhook_endpoints/{ep['id']}")
        elif ep["url"] == url and ep["id"] == old_id: return None   # still there, caller keeps its secret
    ep = call("POST", "/webhook_endpoints", {"url": url, "enabled_events": EVENTS, "description": "EVA Video Studio MVP"})
    return {"id": ep["id"], "secret": ep["secret"], "livemode": ep.get("livemode")}
