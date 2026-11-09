#!/bin/bash
# R2 upload diagnostics — prints facts and R2's error Code/Message only; never credentials, signatures or signed URLs.
#
#   cd ~/Documents/ChatGPT/Video/template-demos/_gallery
#   export R2_ACCOUNT_ID=… R2_ACCESS_KEY_ID=… R2_SECRET_ACCESS_KEY=… R2_BUCKET=eva-video-studio
#   bash r2_debug.sh
#
# 1. credential SHAPE (lengths / hex / stray spaces) — R2 S3 credentials: account id 32 hex, access key id 32 hex,
#    secret access key 64 hex (from R2 → Manage API tokens → the "S3 client" values, NOT the Cloudflare API token)
# 2. curl SigV4 PUT of one 12-byte test object → HTTP status + R2 <Code>/<Message>
# 3. the same with the official AWS SDK (boto3, installed into a throwaway venv in /tmp) → put, head, delete
# The test object (staging/template-demos/gallery/_r2-debug.txt) is deleted again so the gallery listing stays exact.
set -uo pipefail
PREFIX="${EVA_GALLERY_PREFIX:-staging/template-demos/gallery/}"; KEY="${PREFIX}_r2-debug.txt"
echo "== 1. credential shape (values not shown)"
python3 - <<'PY'
import os, re
for n, want in (("R2_ACCOUNT_ID", 32), ("R2_ACCESS_KEY_ID", 32), ("R2_SECRET_ACCESS_KEY", 64), ("R2_BUCKET", None)):
    raw = os.environ.get(n, ""); v = raw.strip()
    facts = [f"length {len(v)}" + (f" (expected {want})" if want and len(v) != want else "")]
    if raw != v: facts.append("HAS leading/trailing whitespace or newline")
    if want: facts.append("hex only" if re.fullmatch(r"[0-9a-f]+", v) else "NOT lowercase hex")
    if n == "R2_BUCKET": facts.append("valid bucket name" if re.fullmatch(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]", v) else "INVALID bucket name")
    if n == "R2_ACCESS_KEY_ID" and len(v) == 40: facts.append("looks like a Cloudflare API token, not the S3 Access Key ID")
    print(f"  {n}: " + ", ".join(facts) if v else f"  {n}: MISSING")
PY
curl --version | head -1 | sed 's/^/  /'
EP="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${R2_BUCKET}"
T=$(mktemp -d -t eva-r2dbg.XXXXXX); trap 'rm -rf "$T"' EXIT; printf 'eva r2 test\n' > "$T/t.txt"

echo "== 2. curl SigV4 PUT (region auto)"
code=$(curl -sS -o "$T/body" -w "%{http_code}" --aws-sigv4 "aws:amz:auto:s3" --user "$R2_ACCESS_KEY_ID:$R2_SECRET_ACCESS_KEY" \
       -T "$T/t.txt" -H "Content-Type: text/plain" "$EP/$KEY" 2>"$T/err")
echo "  HTTP $code"; [ -s "$T/err" ] && sed 's/^/  curl: /' "$T/err" | head -3
python3 - "$T/body" <<'PY'
import re, sys
b = open(sys.argv[1], errors="replace").read()
for tag in ("Code", "Message"):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", b, re.S)
    if m: print(f"  R2 {tag}: {m.group(1).strip()[:200]}")
PY
[ "$code" = 200 ] && curl -sS -o /dev/null --aws-sigv4 "aws:amz:auto:s3" --user "$R2_ACCESS_KEY_ID:$R2_SECRET_ACCESS_KEY" -X DELETE "$EP/$KEY"

echo "== 3. official AWS SDK (boto3)"
V="${TMPDIR:-/tmp}/eva-r2-venv"; [ -x "$V/bin/python" ] || { python3 -m venv "$V" && "$V/bin/pip" -q install boto3 >/dev/null; }
"$V/bin/python" - "$T/t.txt" "$KEY" <<'PY'
import os, sys, boto3
from botocore.config import Config
from botocore.exceptions import ClientError
c = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID'].strip()}.r2.cloudflarestorage.com",
                 aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"].strip(), aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"].strip(),
                 region_name="auto", config=Config(signature_version="s3v4"))
b, k = os.environ["R2_BUCKET"].strip(), sys.argv[2]
try:
    c.upload_file(sys.argv[1], b, k, ExtraArgs={"ContentType": "text/plain"}); print("  put: OK")
    print("  head: OK, ContentLength", c.head_object(Bucket=b, Key=k)["ContentLength"])
    c.delete_object(Bucket=b, Key=k); print("  delete: OK (test object removed)")
except ClientError as e:
    er = e.response.get("Error", {}); print(f"  SDK error: HTTP {e.response.get('ResponseMetadata', {}).get('HTTPStatusCode')} {er.get('Code')}: {er.get('Message')}")
except Exception as e: print(f"  SDK error: {type(e).__name__}: {str(e)[:200]}")
PY
