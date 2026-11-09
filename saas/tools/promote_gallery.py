#!/usr/bin/env python3
"""Copy the approved Gallery assets R2 staging → production prefix (server-side copy, same bytes; staging copies kept).

    python3 saas/tools/promote_gallery.py            # dry run: what would be copied
    python3 saas/tools/promote_gallery.py --copy     # run ONLY by the approved production deploy

Source: staging/template-demos/gallery/  →  destination: gallery/v1/ (EVA_GALLERY_PREFIX). Only status "approved" assets of
gallery.json; each object is checked against gallery.json (size + sha256 of the source) before copying, existing identical
destinations are skipped, and every destination is HEAD-verified (size + ETag equal to the source). Nothing is deleted.
"""
import hashlib, json, os, sys
from pathlib import Path

SRC = "staging/template-demos/gallery/"
DST = os.environ.get("EVA_GALLERY_PREFIX") or "gallery/v1/"
G = json.loads((Path(__file__).resolve().parents[1] / "web/gallery.json").read_text())


def main():
    copy = "--copy" in sys.argv
    if DST == SRC or not DST.endswith("/"): sys.exit("destination prefix must differ from staging and end with /")
    items = [(a[k]["key"], a[k]) for t in G["templates"] for a in t["assets"].values() if a["status"] == "approved"
             for k in ("thumb", "clip5", "full15")]
    if any(Path(k).name.lower().startswith("t19") or k.startswith("T19/") for k, _ in items): sys.exit("T19 in gallery.json")
    print(f"{len(items)} approved assets: {SRC} → {DST}" + ("" if copy else " (dry run)"))
    if not copy: return 0
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    e = lambda k: "".join((os.environ.get(k) or "").split())
    B = e("R2_BUCKET") or "eva-video-studio"
    c = boto3.client("s3", endpoint_url=f"https://{e('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com", region_name="auto",
                     aws_access_key_id=e("R2_ACCESS_KEY_ID"), aws_secret_access_key=e("R2_SECRET_ACCESS_KEY"),
                     config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}))
    bad = copied = 0
    for key, a in items:
        try:
            src = c.get_object(Bucket=B, Key=SRC + key); body = src["Body"].read()
            if len(body) != a["bytes"] or hashlib.sha256(body).hexdigest() != a["sha256"]:
                print("SOURCE MISMATCH", key); bad += 1; continue
            try:
                d = c.head_object(Bucket=B, Key=DST + key)
                if d["ContentLength"] == a["bytes"] and d["ETag"] == src["ETag"]: print("same    ", DST + key); continue
            except ClientError: pass
            c.copy_object(Bucket=B, Key=DST + key, CopySource={"Bucket": B, "Key": SRC + key}, MetadataDirective="COPY")
            d = c.head_object(Bucket=B, Key=DST + key)
            ok = d["ContentLength"] == a["bytes"] and d["ETag"] == src["ETag"]
            print(("copied  " if ok else "VERIFY FAILED ") + DST + key); bad += not ok; copied += ok
        except ClientError as x:
            er = x.response.get("Error", {}); print(f"R2 error on {key}: {er.get('Code')}: {er.get('Message')}"); bad += 1
    print(f"gallery → {DST}: {copied} copied, {len(items) - copied - bad} already identical, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
