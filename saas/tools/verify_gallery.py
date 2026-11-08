#!/usr/bin/env python3
"""Verify the Template Gallery on R2 staging after `upload_gallery.sh --upload` — read-only, Python standard library only.

    cd ~/Documents/ChatGPT/Video/template-demos/_gallery
    export R2_ACCOUNT_ID=… R2_ACCESS_KEY_ID=… R2_SECRET_ACCESS_KEY=… R2_BUCKET=eva-video-studio   # this terminal only
    python3 verify_gallery.py

Checks (exit 1 on any failure):
  1. listing of <prefix> holds exactly the approved keys of gallery.json — nothing pending (T17 16:9), no T19, no extras
  2. the bucket is private: an unsigned GET of an approved object is refused
  3. every approved object, fetched through a 15-minute signed link (the same SigV4 query signing the API uses), is
     byte-identical to gallery.json (sha256 + size) and has the right Content-Type (image/webp, video/mp4)
  4. writes gallery_check.html: every asset per aspect via signed links (valid 1 hour) — open it to see thumbnails and
     play the 5 s + 15 s demos in both aspect ratios. Delete it afterwards (it contains signed links).
Credentials are read from the environment and never written anywhere.
"""
import datetime, hashlib, hmac, html, json, os, sys, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REGION, SERVICE = "auto", "s3"


def _sign(key, msg): return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def _signing_key(secret, date, region=REGION):
    k = _sign(("AWS4" + secret).encode(), date)
    return _sign(_sign(_sign(k, region), SERVICE), "aws4_request")


def presign(host, path, access, secret, expires=900, now=None, region=REGION, query=None):
    """SigV4 query-string signed GET URL (path-style, as boto3 generates for R2)."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    amz, date = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
    scope = f"{date}/{region}/{SERVICE}/aws4_request"
    q = dict(query or {}, **{"X-Amz-Algorithm": "AWS4-HMAC-SHA256", "X-Amz-Credential": f"{access}/{scope}", "X-Amz-Date": amz,
                             "X-Amz-Expires": str(expires), "X-Amz-SignedHeaders": "host"})
    cq = "&".join(f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}" for k, v in sorted(q.items()))
    cpath = urllib.parse.quote(path, safe="/-_.~")
    creq = "\n".join(["GET", cpath, cq, f"host:{host}\n", "host", "UNSIGNED-PAYLOAD"])
    sts = "\n".join(["AWS4-HMAC-SHA256", amz, scope, hashlib.sha256(creq.encode()).hexdigest()])
    sig = hmac.new(_signing_key(secret, date, region), sts.encode(), hashlib.sha256).hexdigest()
    return f"https://{host}{cpath}?{cq}&X-Amz-Signature={sig}"


def selftest():
    """AWS's published S3 query-string-auth example (Signature Version 4 docs, 'Example: GET object')."""
    now = datetime.datetime(2013, 5, 24, tzinfo=datetime.timezone.utc)
    u = presign("examplebucket.s3.amazonaws.com", "/test.txt", "AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                expires=86400, now=now, region="us-east-1")
    return u.endswith("X-Amz-Signature=aeeed9bbccd4d02ee5c0109b86d86835f995330da4c265957d157751f604d404")


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), e.read()


def main():
    if not selftest(): sys.exit("SigV4 self-test failed")
    env = {k: os.environ.get(k) for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET")}
    miss = [k for k, v in env.items() if not v]
    if miss: sys.exit("missing " + ", ".join(miss) + " (export them in this terminal)")
    prefix = os.environ.get("EVA_GALLERY_PREFIX", "staging/template-demos/gallery/")
    host = f"{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"; B = env["R2_BUCKET"]
    sg = lambda path, exp=900, q=None: presign(host, f"/{B}/{path}", env["R2_ACCESS_KEY_ID"], env["R2_SECRET_ACCESS_KEY"], exp, query=q)
    g = json.load(open(Path(__file__).resolve().parent / "gallery.json"))
    want = {}
    for t in g["templates"]:
        for ar, a in t["assets"].items():
            if a["status"] != "approved": continue
            for k in ("thumb", "clip5", "full15"): want[prefix + a[k]["key"]] = (t["id"], ar, k, a[k])
    fails = []
    def check(c, m):
        print(("PASS " if c else "FAIL ") + m)
        if not c: fails.append(m)

    # 1 · listing
    st, _, body = fetch(presign(host, f"/{B}", env["R2_ACCESS_KEY_ID"], env["R2_SECRET_ACCESS_KEY"], 900,
                                query={"list-type": "2", "prefix": prefix, "max-keys": "1000"}))
    keys = []
    if st == 200:
        ns = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
        keys = [c.find("s:Key", ns).text for c in ET.fromstring(body).findall("s:Contents", ns)]
    check(st == 200, f"list {prefix} (HTTP {st})")
    check(set(keys) == set(want), f"exactly the {len(want)} approved keys on R2 ({len(keys)} found; missing {sorted(set(want) - set(keys))[:3]}, extra {sorted(set(keys) - set(want))[:3]})")
    check(not any("t17_169" in k or "/T19/" in k for k in keys), "no pending T17 16:9 and no T19 objects")
    # 2 · private
    any_key = next(iter(want))
    st, _, _ = fetch(f"https://{host}/{B}/{urllib.parse.quote(any_key)}")
    check(st in (400, 401, 403), f"bucket private: unsigned GET refused (HTTP {st})")
    # 3 · signed fetch, bytes, type
    for key, (tid, ar, k, a) in sorted(want.items()):
        st, h, b = fetch(sg(key))
        ctype = {".webp": "image/webp", ".mp4": "video/mp4"}[Path(key).suffix]
        ok = st == 200 and len(b) == a["bytes"] and hashlib.sha256(b).hexdigest() == a["sha256"] and h.get("Content-Type", "").startswith(ctype)
        check(ok, f"{tid} {ar} {k}: signed GET {st}, {len(b)} bytes, sha256 {'match' if ok else 'MISMATCH'}, {h.get('Content-Type')}")
    # 4 · playback page
    rows = []
    for t in g["templates"]:
        for ar in ("9:16", "16:9"):
            a = t["assets"].get(ar)
            if not a or a["status"] != "approved":
                rows.append(f"<section><h3>{t['id']} {t['name']} · {ar}</h3><p>{'pending review — not uploaded' if a else 'no asset'}</p></section>"); continue
            u = {k: html.escape(sg(prefix + a[k]["key"], 3600)) for k in ("thumb", "clip5", "full15")}
            w = 320 if ar == "16:9" else 180
            rows.append(f"<section><h3>{t['id']} {t['name']} · {ar}</h3><img src='{u['thumb']}' width='{w}'>"
                        f"<video src='{u['clip5']}' width='{w}' muted loop autoplay playsinline></video>"
                        f"<video src='{u['full15']}' width='{w}' controls playsinline></video></section>")
    Path("gallery_check.html").write_text("<!doctype html><meta charset=utf-8><title>Gallery check</title><style>body{font:14px system-ui;margin:16px}"
                                         "section{margin:12px 0;display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}h3{width:100%;margin:0}</style>"
                                         "<h1>Template Gallery · R2 staging (signed links valid 1 hour)</h1>" + "".join(rows))
    print("wrote gallery_check.html (open it to check playback in both aspects; delete it afterwards)")
    print("gallery on R2 staging:", "OK" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
