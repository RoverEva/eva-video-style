#!/usr/bin/env bash
# Eva Video Style · video -> eva-asr -> captions, in one step.
#   1. scripts/asr.py   : eva-asr transcribes (+ aligns, + translates to English) the video's speech
#   2. scripts/captions.py : the existing caption step turns the bilingual SRT into the editable .srt + styled .ass
# usage: asr_captions.sh VIDEO SRT_BASENAME CAPTIONS_BASENAME [asr_config.json] [display_fix.json]
#   e.g. scripts/asr_captions.sh raw/talk.mp4 srt/talk out/NAME_CN-EN config/asr.json srt/display_fix.json
# Outputs: SRT_BASENAME.{zh,en,bilingual}.srt, .asr.json, .transcript.js  and  CAPTIONS_BASENAME.{srt,ass}
set -euo pipefail
[ $# -ge 3 ] || { sed -n 2,7p "$0" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
video="$1"; srtbase="$2"; capbase="$3"; asrcfg="${4:-}"; fix="${5:-}"
for f in "${capbase}.srt" "${capbase}.ass"; do [ -e "$f" ] && { echo "Refusing to overwrite $f" >&2; exit 1; }; done
python3 "$here/asr.py" "$video" "$srtbase" ${asrcfg:+--config "$asrcfg"}
mkdir -p "$(dirname "$capbase")"
python3 "$here/captions.py" "${srtbase}.bilingual.srt" 0 99999 "$capbase" ${fix:+"$fix"}
