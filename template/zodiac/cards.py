#!/usr/bin/env python3
"""Render the 12 zodiac hero cards (1920x1080) and a 4x3 overview."""
import os, sys, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zodiac_signs import SIGNS, card
out = sys.argv[1] if len(sys.argv) > 1 else 'out/zodiac_cards'
os.makedirs(out, exist_ok=True)
tiles = []
for i, s in enumerate(SIGNS, 1):
    im = card(s); p = os.path.join(out, f"{i:02d}_{s['key']}_{s['cn']}.jpg")
    cv2.imwrite(p, im, [cv2.IMWRITE_JPEG_QUALITY, 92]); print(p)
    tiles.append(cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA))
grid = np.vstack([np.hstack(tiles[r * 4:(r + 1) * 4]) for r in range(3)])
cv2.imwrite(os.path.join(out, 'zodiac_overview.jpg'), grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
