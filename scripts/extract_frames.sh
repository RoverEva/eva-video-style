#!/usr/bin/env bash
# Extract a video to a 30 fps JPG sequence named by absolute frame number (f_00000.jpg ...), scaled to 1920 wide.
# usage: extract_frames.sh INPUT.mp4 OUT_DIR [WIDTH]
set -euo pipefail
in="$1"; out="$2"; w="${3:-1920}"
[ -e "$out" ] && { echo "Refusing to overwrite $out" >&2; exit 1; }
mkdir -p "$out"
ffmpeg -loglevel error -i "$in" -vf "fps=30,scale=${w}:-2" -q:v 3 -start_number 0 "$out/f_%05d.jpg"
echo "$out: $(ls "$out" | wc -l) frames"
