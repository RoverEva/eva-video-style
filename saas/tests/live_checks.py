#!/usr/bin/env python3
"""Live security, privacy and failure probes against a deployed EVA Video Studio (run by CI after the browser purchase).

    python3 saas/tests/live_checks.py API_URL PURCHASE_SUMMARY.json OUT.json

Webhook: unsigned / forged / stale signatures are rejected. Jobs: no or wrong token → 404. Files: the HD link is a
presigned URL that works; the same object without or with a tampered signature is refused (bucket is private).
CORS: a foreign origin gets no CORS grant. Rejection: a 40 s upload is refused by the server-side check (no ASR, no
render, no charge). Output: the delivered file is full resolution. Prints and writes a JSON report; exit 1 on failure.
"""
import hashlib, hmac, json, subprocess, sys, tempfile, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path


def req(url, method="GET", data=None, headers=None):
    r = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=60) as x: return x.status, x.read(), dict(x.headers)
    except urllib.error.HTTPError as e: return e.code, e.read(), dict(e.headers)


def main():
    api, summary, out = sys.argv[1].rstrip("/"), Path(sys.argv[2]), Path(sys.argv[3])
    s = json.loads(summary.read_text()); priv = json.loads((summary.parent / "private.txt").read_text())
    job, tok, href = priv["job"], priv["token"], priv["href"]; R = {}
    ok = lambda name, cond, detail="": R.__setitem__(name, {"ok": bool(cond), "detail": detail})

    c, b, _ = req(f"{api}/api/health"); h = json.loads(b); ok("stripe_test_mode", h.get("stripe") == "test", h)

    ev = json.dumps({"type": "checkout.session.completed", "data": {"object": {"id": "cs_forged", "payment_status": "paid",
                     "payment_intent": "pi_forged", "metadata": {"job": job}}}}).encode()
    t = int(time.time()); fake = hmac.new(b"whsec_not_the_secret", f"{t}.".encode() + ev, hashlib.sha256).hexdigest()
    for name, hdr in (("webhook_unsigned", {}), ("webhook_forged", {"stripe-signature": f"t={t},v1={fake}"}),
                      ("webhook_stale", {"stripe-signature": f"t={t - 7200},v1={fake}"})):
        c, b, _ = req(f"{api}/api/stripe/webhook", "POST", ev, dict(hdr, **{"content-type": "application/json"}))
        ok(name + "_rejected", c == 400, f"HTTP {c}")

    for name, q in (("job_no_token", ""), ("job_wrong_token", "?t=wrong")):
        c, _, _ = req(f"{api}/api/jobs/{job}{q}"); ok(name + "_404", c == 404, f"HTTP {c}")
    c, b, _ = req(f"{api}/api/jobs/{job}?t={urllib.parse.quote(tok)}"); v = json.loads(b)
    ok("job_with_token", c == 200 and v.get("state") == "delivered", v.get("state"))
    href = (v.get("final") or {}).get("url") or href

    c, _, _ = req(href, headers={"Range": "bytes=0-1023"}); ok("presigned_download_works", c in (200, 206), f"HTTP {c}")
    bare = href.split("?")[0]; c, _, _ = req(bare, headers={"Range": "bytes=0-15"}); ok("unsigned_object_refused", c in (400, 401, 403), f"HTTP {c}")
    tampered = href.replace("X-Amz-Signature=", "X-Amz-Signature=0") ; c, _, _ = req(tampered, headers={"Range": "bytes=0-15"})
    ok("tampered_signature_refused", c in (400, 401, 403), f"HTTP {c}")
    other = href.replace(f"outputs/{job}/final.mp4", f"uploads/{job}/input.mp4"); c, _, _ = req(other, headers={"Range": "bytes=0-15"})
    ok("signature_bound_to_one_file", c in (400, 401, 403), f"HTTP {c}")

    c, _, hd = req(f"{api}/api/config", "OPTIONS", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    ok("cors_foreign_origin_denied", "access-control-allow-origin" not in {k.lower() for k in hd}, f"HTTP {c}")

    d = s.get("delivered") or {}
    ok("full_resolution_output", (d.get("width"), d.get("height")) in ((1080, 1920), (1920, 1080)) and d.get("audio"), d)

    # server-side rejection (the browser would block > 30 s before uploading, so call the API directly)
    with tempfile.TemporaryDirectory() as tmp:
        long = Path(tmp) / "long.mp4"; src = Path(__file__).parent / "media/education.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-stream_loop", "3", "-i", src, "-c", "copy", long], check=True)
        data = long.read_bytes()
        c, b, _ = req(f"{api}/api/uploads", "POST", json.dumps({"name": "too-long.mp4", "size": len(data), "type": "video/mp4"}).encode(), {"content-type": "application/json"})
        u = json.loads(b); c, _, _ = req(u["put_url"], "PUT", data, {"Content-Type": "video/mp4"}); ok("upload_put_to_private_bucket", c == 200, f"HTTP {c}")
        c, b, _ = req(f"{api}/api/jobs/{u['job']}/preview", "POST", json.dumps({"token": u["token"], "aspect": "9:16", "templates": ["T17"]}).encode(), {"content-type": "application/json"})
        state, t0 = None, time.time()
        while time.time() - t0 < 600:
            v = json.loads(req(f"{api}/api/jobs/{u['job']}?t={urllib.parse.quote(u['token'])}")[1]); state = (v.get("preview") or {}).get("state")
            if state in ("rejected", "failed", "done"): break
            time.sleep(5)
        ok("over_30s_rejected_server_side", state == "rejected" and "30" in str(v["preview"].get("error")), {"state": state, "error": v["preview"].get("error"), "s": round(time.time() - t0)})

    rep = {"all_ok": all(x["ok"] for x in R.values()), "checks": R}
    out.write_text(json.dumps(rep, indent=1)); print(json.dumps(rep, indent=1))
    sys.exit(0 if rep["all_ok"] else 1)


if __name__ == "__main__":
    main()
