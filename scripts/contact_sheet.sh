#!/usr/bin/env bash
# One frame every N seconds tiled into a JPG for a quick visual review.  usage: contact_sheet.sh VIDEO OUT.jpg [EVERY_SECONDS]
set -euo pipefail
n=$(( ${3:-5} * 30 ))
ffmpeg -loglevel error -y -i "$1" -vf "select='not(mod(n\,$n))',scale=480:-1,tile=4x5:padding=4" -frames:v 1 "$2" && echo "$2"
