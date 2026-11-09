#!/bin/bash
# Upload the APPROVED Template Gallery assets to R2 staging — and nothing else — with the official AWS SDK (boto3).
#
#   cd ~/Documents/ChatGPT/Video/template-demos/_gallery
#   export R2_ACCOUNT_ID=… R2_ACCESS_KEY_ID=… R2_SECRET_ACCESS_KEY=… R2_BUCKET=eva-video-studio   # typed in this terminal only
#   ./upload_gallery.sh            # dry run: shows what would be uploaded
#   ./upload_gallery.sh --upload   # credential shape check → upload → HEAD-verify
#   python3 verify_gallery.py      # listing, privacy, signed-link checksums, playback page
#
# boto3 is installed once into a throwaway venv ($TMPDIR/eva-r2-venv); nothing is installed system-wide.
# (Earlier version used curl --aws-sigv4; replaced by the SDK — same client settings as the production API.)
set -euo pipefail
cd "$(dirname "$0")"
V="${TMPDIR:-/tmp}/eva-r2-venv"
if [ "${1:-}" = "--upload" ] && ! [ -x "$V/bin/python" ] ; then
  echo "installing boto3 into $V (one time)"; python3 -m venv "$V" && "$V/bin/pip" -q install boto3
fi
PY=python3; [ -x "$V/bin/python" ] && PY="$V/bin/python"
exec "$PY" upload_gallery.py "$@"
