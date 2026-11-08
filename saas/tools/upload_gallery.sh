#!/bin/bash
# Upload the APPROVED Template Gallery assets to R2 staging — and nothing else.
#
#   cd ~/Documents/ChatGPT/Video/template-demos/_gallery
#   export R2_ACCOUNT_ID=… R2_ACCESS_KEY_ID=… R2_SECRET_ACCESS_KEY=… R2_BUCKET=eva-video-studio   # typed in this terminal only
#   ./upload_gallery.sh            # dry run: shows what would be uploaded
#   ./upload_gallery.sh --upload   # upload + verify
#
# Reads gallery.json next to this script. Uploads only assets with status "approved" (never pending/superseded/originals),
# to  <bucket>/<EVA_GALLERY_PREFIX, default staging/template-demos/gallery/><TEMPLATE>/<file>, after checking each file's
# sha256 against gallery.json. Then HEADs every object and compares the size. Needs only macOS curl (7.75+, SigV4) + python3.
# Credentials are read from the environment and never written anywhere.
set -euo pipefail
cd "$(dirname "$0")"
PREFIX="${EVA_GALLERY_PREFIX:-staging/template-demos/gallery/}"
MODE="${1:-dry-run}"
for v in R2_ACCOUNT_ID R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY R2_BUCKET; do
  [ "$MODE" = "--upload" ] && [ -z "${!v:-}" ] && { echo "missing $v (export it in this terminal)"; exit 1; }
done
EP="https://${R2_ACCOUNT_ID:-ACCOUNT}.r2.cloudflarestorage.com/${R2_BUCKET:-BUCKET}"
LIST="$(mktemp -t eva-gallery.XXXXXX)"; trap 'rm -f "$LIST"' EXIT

python3 - "$PREFIX" > "$LIST" <<'PY'
import hashlib, json, sys
from pathlib import Path
g = json.load(open("gallery.json")); prefix = sys.argv[1]
types = {".webp": "image/webp", ".mp4": "video/mp4"}
for t in g["templates"]:
    for ar, a in t["assets"].items():
        if a.get("status") != "approved": continue
        for k in ("thumb", "clip5", "full15"):
            f = Path(a[k]["key"])
            if not f.exists(): sys.exit(f"missing {f}")
            if hashlib.sha256(f.read_bytes()).hexdigest() != a[k]["sha256"] or f.stat().st_size != a[k]["bytes"]: sys.exit(f"checksum mismatch: {f}")
            print(f"{f}\t{prefix}{f}\t{types[f.suffix]}\t{a[k]['bytes']}")
PY
n=$(wc -l < "$LIST" | tr -d ' '); total=$(awk -F'\t' '{s+=$4} END {print s}' "$LIST")
echo "approved assets: $n files, $total bytes, checksums OK → $EP/$PREFIX"
if [ "$MODE" != "--upload" ]; then cut -f2 "$LIST"; echo "(dry run — add --upload to upload)"; exit 0; fi

auth=(--aws-sigv4 "aws:amz:auto:s3" --user "$R2_ACCESS_KEY_ID:$R2_SECRET_ACCESS_KEY")
while IFS=$'\t' read -r f key ctype bytes; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" "${auth[@]}" -X PUT -T "$f" -H "Content-Type: $ctype" \
         -H "Cache-Control: public, max-age=86400" "$EP/$key")
  [ "$code" = 200 ] || { echo "upload failed ($code): $key"; exit 1; }
  echo "uploaded $key"
done < "$LIST"
fail=0
while IFS=$'\t' read -r f key ctype bytes; do
  len=$(curl -sS -I "${auth[@]}" "$EP/$key" | awk 'tolower($1)=="content-length:" {print $2}' | tr -d '\r')
  [ "$len" = "$bytes" ] && echo "verified $key ($len bytes)" || { echo "VERIFY FAILED $key (got '$len', want $bytes)"; fail=1; }
done < "$LIST"
[ $fail = 0 ] && echo "done: $n approved gallery assets on R2 staging" || exit 1
