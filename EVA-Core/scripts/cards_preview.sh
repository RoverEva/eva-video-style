#!/usr/bin/env bash
# EVA Card System preview stills (no video render): one still per template + a 3x3 sheet of the nine layouts.
#   scripts/cards_preview.sh [OUT_DIR]   (default: out/cards-preview)
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-out/cards-preview}"; mkdir -p "$OUT"
for d in t17 t20 t01 t09; do node scripts/render.mjs "template/cards/$d/index.html" --stills "$OUT/$d" --times 3 >/dev/null; done
node scripts/render.mjs template/cards/layouts/index.html --stills "$OUT/layouts" --times 1.95,3.95,5.95,7.95,9.95,11.95,13.95,15.95,17.95 >/dev/null
python3 - "$OUT" <<'PY'
import sys, glob
from PIL import Image
o = sys.argv[1]; fs = sorted(glob.glob(f'{o}/layouts/*.png'))
W = Image.new('RGB', (1928, 1088), 'white')
for i, f in enumerate(fs): W.paste(Image.open(f).convert('RGB').resize((640, 360), Image.LANCZOS), ((i % 3) * 644, (i // 3) * 364))
W.save(f'{o}/EVA_cards_9_layouts.png')
W = Image.new('RGB', (1924, 1084), 'white')
for i, d in enumerate(['t17', 't20', 't01', 't09']):
    im = Image.open(f'{o}/{d}/t_0003.00.png').convert('RGB'); im.save(f'{o}/EVA_cards_{d.upper()}.jpg', quality=90)
    W.paste(im.resize((960, 540), Image.LANCZOS), ((i % 2) * 964, (i // 2) * 544))
W.save(f'{o}/EVA_cards_T17_T20_T01_T09.png'); print('previews ->', o)
PY
