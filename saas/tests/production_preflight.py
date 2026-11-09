#!/usr/bin/env python3
"""Read-only checks of the PRODUCTION credentials (run by production-preflight.yml in the `production` environment).

Nothing is created, changed or charged. Prints PASS/FAIL facts only — never a key, URL with credentials or signed link.
  Stripe  key is TEST mode (sk_test_/rk_test_), authenticates, can read Checkout Sessions + webhook endpoints
  R2      credential shape; bucket private; gallery prefix holds exactly the approved keys of gallery.json (no T19)
  Vercel  token authenticates (GET /v2/user)
  Resend  optional: API key authenticates and the EVA_MAIL_FROM domain is verified
Supabase is checked by saas/tests/supabase_staging_check.py (same script the deploy runs first; rolled back, nothing kept).
"""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "saas/tools"))
from verify_gallery import presign, selftest  # stdlib SigV4 signer, checked against AWS's published vector

fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

def env(k): return "".join((os.environ.get(k) or "").split())

def get(url, headers=None, auth=None):
    req = urllib.request.Request(url, headers=headers or {})
    if auth:
        import base64; req.add_header("Authorization", "Basic " + base64.b64encode(f"{auth}:".encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
    except Exception as e: return 0, type(e).__name__.encode()


def stripe():
    k = env("STRIPE_SECRET_KEY")
    if not k: return check(False, "Stripe: STRIPE_SECRET_KEY set")
    check(k.startswith(("sk_test_", "rk_test_")), f"Stripe: key is TEST mode ({k[:8]}…)")
    if "_live_" in k: return   # never call Stripe with a live key from here
    h = {"Stripe-Version": "2024-06-20"}
    st, b = get("https://api.stripe.com/v1/checkout/sessions?limit=1", h, k)
    check(st == 200, f"Stripe: authenticates and can read Checkout Sessions (HTTP {st})")
    st, b = get("https://api.stripe.com/v1/webhook_endpoints?limit=20", h, k)
    if st == 200:
        eps = json.loads(b).get("data", [])
        print(f"INFO Stripe: {len(eps)} TEST webhook endpoint(s) exist (the deploy creates/updates its own)")
    check(st == 200, f"Stripe: can read webhook endpoints (needed by the deploy to register its webhook) (HTTP {st})")


def r2():
    v = {k: env(k) for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")}
    v["R2_BUCKET"] = env("R2_BUCKET") or "eva-video-studio"
    ok = True
    for k, n in (("R2_ACCOUNT_ID", 32), ("R2_ACCESS_KEY_ID", 32), ("R2_SECRET_ACCESS_KEY", 64)):
        good = bool(re.fullmatch(rf"[0-9a-f]{{{n}}}", v[k])); ok &= good
        check(good, f"R2: {k} shape ({n} hex; got length {len(v[k])})")
    if not ok: return
    check(selftest(), "R2: SigV4 signer self-test")
    host, B = f"{v['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com", v["R2_BUCKET"]
    prefix = os.environ.get("EVA_GALLERY_PREFIX") or "staging/template-demos/gallery/"
    g = json.loads((ROOT / "saas/web/gallery.json").read_text())
    want = {prefix + a[k]["key"] for t in g["templates"] for a in t["assets"].values() if a["status"] == "approved"
            for k in ("thumb", "clip5", "full15")}
    st, body = get(presign(host, f"/{B}", v["R2_ACCESS_KEY_ID"], v["R2_SECRET_ACCESS_KEY"], 300,
                           query={"list-type": "2", "prefix": prefix, "max-keys": "1000"}))
    keys = []
    if st == 200:
        ns = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
        keys = [c.find("s:Key", ns).text for c in ET.fromstring(body).findall("s:Contents", ns)]
    check(st == 200, f"R2: production credentials can list the bucket (HTTP {st})")
    check(set(keys) == want, f"R2: gallery prefix holds exactly the {len(want)} approved assets ({len(keys)} found)")
    check(not any("/T19/" in k or Path(k).name.lower().startswith("t19") for k in keys), "R2: no T19 objects")
    if keys:
        st, _ = get(f"https://{host}/{B}/{urllib.parse.quote(keys[0])}")
        check(st in (400, 401, 403), f"R2: bucket private — unsigned GET refused (HTTP {st})")
        st, _ = get(presign(host, f"/{B}/{keys[0]}", v["R2_ACCESS_KEY_ID"], v["R2_SECRET_ACCESS_KEY"], 300))
        check(st == 200, f"R2: signed GET works (HTTP {st})")


def vercel():
    t = env("VERCEL_TOKEN")
    if not t: return check(False, "Vercel: VERCEL_TOKEN set")
    st, _ = get("https://api.vercel.com/v2/user", {"Authorization": f"Bearer {t}"})
    check(st == 200, f"Vercel: token authenticates (HTTP {st})")


def resend():
    k, frm = env("RESEND_API_KEY"), (os.environ.get("EVA_MAIL_FROM") or "").strip()
    if not k: print("INFO Resend: RESEND_API_KEY not set (optional — Supabase SMTP settings are configured in Supabase itself)"); return
    st, b = get("https://api.resend.com/domains", {"Authorization": f"Bearer {k}"})
    check(st == 200, f"Resend: API key authenticates (HTTP {st})")
    if st == 200 and frm:
        dom = frm.rsplit("@", 1)[-1].strip("> ").lower()
        ds = {d["name"].lower(): d.get("status") for d in json.loads(b).get("data", [])}
        check(ds.get(dom) == "verified", f"Resend: sender domain of EVA_MAIL_FROM is verified (status {ds.get(dom)})")


if __name__ == "__main__":
    for name, f in (("Stripe", stripe), ("R2", r2), ("Vercel", vercel), ("Resend", resend)):
        print(f"== {name}", flush=True)
        try: f()
        except Exception as e: check(False, f"{name}: {type(e).__name__}")
    print("production preflight:", "OK" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
