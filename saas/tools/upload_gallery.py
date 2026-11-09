#!/usr/bin/env python3
"""Upload the APPROVED Template Gallery assets to R2 staging with the official AWS SDK (boto3) — the same client settings
the production API uses against R2 (endpoint https://<account>.r2.cloudflarestorage.com, region "auto", SigV4).
Run through upload_gallery.sh (creates a throwaway venv with boto3). Credentials only from the environment.

Before any request: credential shape check (account id 32 hex, access key id 32 hex, secret 64 hex, bucket name), with
whitespace/newlines from pasting stripped. Uploads only status "approved" files after re-checking sha256, then HEADs
each object and compares size. R2 errors are shown as HTTP status + Code + Message only.
"""
import hashlib, json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TYPES = {".webp": "image/webp", ".mp4": "video/mp4"}


def creds():
    v = {k: (os.environ.get(k) or "").strip() for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET")}
    bad = []
    for k, n in (("R2_ACCOUNT_ID", 32), ("R2_ACCESS_KEY_ID", 32), ("R2_SECRET_ACCESS_KEY", 64)):
        if not re.fullmatch(rf"[0-9a-f]{{{n}}}", v[k]):
            hint = " — this looks like a Cloudflare API token; use the token's 'Access Key ID' / 'Secret Access Key' (S3 client values)" \
                if len(v[k]) == 40 else ""
            bad.append(f"{k}: length {len(v[k])}, expected {n} lowercase hex characters{hint}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]", v["R2_BUCKET"]): bad.append("R2_BUCKET: not a valid bucket name")
    return v, bad


def plan(prefix):
    g = json.loads((HERE / "gallery.json").read_text()); out = []
    for t in g["templates"]:
        for ar, a in t["assets"].items():
            if a.get("status") != "approved": continue
            for k in ("thumb", "clip5", "full15"):
                f = HERE / a[k]["key"]
                if not f.exists(): sys.exit(f"missing {f.name}")
                if f.stat().st_size != a[k]["bytes"] or hashlib.sha256(f.read_bytes()).hexdigest() != a[k]["sha256"]:
                    sys.exit(f"checksum mismatch: {a[k]['key']}")
                out.append((f, prefix + a[k]["key"], TYPES[f.suffix], a[k]["bytes"]))
    return out


def main():
    upload = "--upload" in sys.argv
    prefix = os.environ.get("EVA_GALLERY_PREFIX", "staging/template-demos/gallery/")
    files = plan(prefix)
    print(f"approved assets: {len(files)} files, {sum(f[3] for f in files)} bytes, checksums OK → <bucket>/{prefix}")
    if not upload:
        for _, key, _, _ in files: print(" ", key)
        print("(dry run — add --upload to upload)"); return 0
    v, bad = creds()
    if bad:
        print("credential problem (nothing was sent):"); [print("  " + b) for b in bad]; return 2
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    c = boto3.client("s3", endpoint_url=os.environ.get("R2_ENDPOINT_OVERRIDE") or f"https://{v['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                     aws_access_key_id=v["R2_ACCESS_KEY_ID"], aws_secret_access_key=v["R2_SECRET_ACCESS_KEY"], region_name="auto",
                     config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}))
    try:
        for f, key, ctype, _ in files:
            c.upload_file(str(f), v["R2_BUCKET"], key, ExtraArgs={"ContentType": ctype, "CacheControl": "public, max-age=86400"})
            print("uploaded", key)
        bad = 0
        for f, key, _, n in files:
            got = c.head_object(Bucket=v["R2_BUCKET"], Key=key)["ContentLength"]
            print(("verified " if got == n else "VERIFY FAILED ") + f"{key} ({got} bytes)"); bad += got != n
    except ClientError as e:
        er = e.response.get("Error", {})
        print(f"R2 error: HTTP {e.response.get('ResponseMetadata', {}).get('HTTPStatusCode')} {er.get('Code')}: {er.get('Message')}"); return 1
    print(f"done: {len(files)} approved gallery assets on R2 staging" if not bad else f"{bad} objects failed verification")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
