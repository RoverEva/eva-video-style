#!/usr/bin/env bash
# Eva Video Style · one command: background music + a few Kenney accents for a finished video.
#   step 1 (default): analyse the library (cached in music-library/catalog.json) → plan → audio-only preview, then STOP so you can listen
#   step 2 (--apply): mix the approved plan into the video (video stream copied, never re-rendered)
# usage: auto_music.sh VIDEO SRT OUT_DIR [--config music.json] [--mode auto|manual|none] [--cues all_cues.json]
#                      [--script talk.txt] [--storyboard sb.json] [--refs DIR] [--replan] [--apply [OUT.mp4]]
#   e.g. scripts/auto_music.sh out/NAME_CN-EN.mp4 srt/talk.en.srt out/music --mode auto --cues sec/all_cues.json
#        scripts/auto_music.sh out/NAME_CN-EN.mp4 srt/talk.en.srt out/music --apply
# Without --mode or a config that says auto/manual, background_music is "none" and nothing is changed.
set -euo pipefail
[ $# -ge 3 ] || { sed -n 2,9p "$0" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"; PY="${PYTHON:-python3}"
video="$1"; srt="$2"; dir="$3"; shift 3
apply=0; final=""; plan_args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) apply=1; if [ $# -gt 1 ] && [ "${2#--}" = "$2" ]; then final="$2"; shift; fi ;;
    --replan) plan_args+=(--replan) ;;
    --config|--mode|--cues|--script|--storyboard|--refs) [ $# -ge 2 ] || { echo "$1 needs a value" >&2; exit 2; }; plan_args+=("$1" "$2"); shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac; shift
done
plan="$dir/music_plan.json"
if [ "$apply" = 1 ]; then
  [ -f "$plan" ] || { echo "no plan at $plan: run without --apply first" >&2; exit 1; }
  name="$(basename "${video%.*}")"; final="${final:-$dir/${name}_Music.mp4}"
  "$PY" "$here/music.py" apply "$plan" "$final" --video "$video"
  exit 0
fi
mkdir -p "$dir"
if [ -f "$plan" ] && [ ${#plan_args[@]} -eq 0 ]; then   # no options: keep the plan already made
  echo "using the existing plan (pass options or --replan to choose again):"; "$PY" "$here/music.py" show "$plan"
else
  [ -f "$plan" ] && [[ " ${plan_args[*]} " != *" --replan "* ]] && plan_args+=(--replan)
  "$PY" "$here/music.py" plan "$video" "$srt" "$dir" ${plan_args[@]+"${plan_args[@]}"}
fi
"$PY" "$here/music.py" preview "$plan" --video "$video"
if grep -q '"mode": "none"' "$plan"; then exit 0; fi
echo
echo "▶ listen: $dir/music_preview.m4a    plan: $dir/music_plan.md"
echo "▶ if it sounds right: $0 $video $srt $dir --apply"
