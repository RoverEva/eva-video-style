#!/usr/bin/env python3
"""Fast deploy smoke test (≈ 5 s), run before the 10-minute browser test:

    smoke_cors.py API_URL SITE_ORIGIN

1. Preflight OPTIONS /api/uploads from the site → 200 and Access-Control-Allow-Origin == SITE_ORIGIN exactly
2. Preflight from a foreign origin → no Access-Control-Allow-Origin
3. Real POST /api/uploads from the site → 200 with the same exact header (exercises R2 + the order record)
4. PUT 16 bytes to the returned signed R2 URL with the site's Origin → 200 (signing + bucket CORS)
Exit 1 with the reason on the first failure. Prints no tokens or signed URLs.
"""
import json, sys
import requests

api, site = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")
fails = []


def check(name, cond, detail):
    print(("PASS " if cond else "FAIL ") + name + ": " + detail, flush=True)
    if not cond: fails.append(name)


pre = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"}
r = requests.options(f"{api}/api/uploads", headers={"Origin": site, **pre}, timeout=60)
acao = r.headers.get("access-control-allow-origin")
check("preflight from site", r.status_code == 200 and acao == site,
      f"HTTP {r.status_code}, allow-origin={acao!r}, allow-methods={r.headers.get('access-control-allow-methods')!r}, allow-headers={r.headers.get('access-control-allow-headers')!r}")

r = requests.options(f"{api}/api/uploads", headers={"Origin": "https://evil.example", **pre}, timeout=60)
check("preflight from foreign origin refused", "access-control-allow-origin" not in r.headers, f"HTTP {r.status_code}, allow-origin={r.headers.get('access-control-allow-origin')!r}")

r = requests.post(f"{api}/api/uploads", headers={"Origin": site, "Content-Type": "application/json"},
                  data=json.dumps({"name": "smoke-test.mp4", "size": 16, "type": "video/mp4"}), timeout=60)
acao = r.headers.get("access-control-allow-origin")
body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
check("POST /api/uploads from site", r.status_code == 200 and acao == site and "put_url" in body,
      f"HTTP {r.status_code}, allow-origin={acao!r}, " + (f"error={body.get('error')!r}" if r.status_code != 200 else "job created"))

if "put_url" in body:
    r = requests.put(body["put_url"], data=b"0" * 16, headers={"Content-Type": body.get("put_type", "video/mp4"), "Origin": site}, timeout=60)
    check("signed upload to private R2", r.status_code == 200, f"HTTP {r.status_code}, allow-origin={r.headers.get('access-control-allow-origin')!r}" +
          ("" if r.ok else f", {r.text[:200]!r}"))

print("smoke test:", "OK" if not fails else "FAILED: " + ", ".join(fails))
sys.exit(1 if fails else 0)
