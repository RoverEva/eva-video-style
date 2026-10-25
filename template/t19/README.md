# T19 · 真实影像引入 · Footage Intro

Media this demo expects (not shipped — use your own):
- `../media/eva/` — the talking-head frames (`scripts/extract_frames.sh`)
- `../media/t19/cut/` — the presenter cut-out: `python3 scripts/matte.py media/eva FIRST LAST media/t19/cut`
- `../media/t19/plates/p1.jpg … p5.jpg` — your own 16:9 background images for the fast swaps
- `../media/web/` — the real footage as a 30 fps JPG sequence

After rendering, move captions off the footage:
`python3 scripts/caption_zones.py section_no_captions.mp4 captions.ass captions_placed.ass avoid.json`
