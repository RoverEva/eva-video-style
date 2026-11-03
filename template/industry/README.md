# Industry templates (native 9:16)

Vertical-first templates for specific verticals. Each one is driven by a beat plan generated from the talk's SRT, so the
next video needs no code changes:

```bash
python3 scripts/srt_to_beats.py talk.srt template/industry/t26/data.js --end 10.08   # on-screen text = the SRT, unchanged
python3 scripts/matte.py media/re_eva 0 FRAMES media/re_cut                                 # cut-out presenter (RGBA WebP)
node scripts/render.mjs template/industry/t26/index.html --out out/t26.mp4            # 1080x1920, 30 fps
```

| Folder | Look |
|---|---|
| `t26/` | **T26 Real Estate Social** (9:16 only) — Chinese social property tour: cut-out presenter with a white sticker outline, heavy dark headline with a white keyline and one red phrase, yellow brush underline and spark strokes, red hearts, icon list that builds up line by line |

Media goes in `template/industry/media/` (not in the repository). Background: `?plate=IMG` (a still with the presenter
removed), `?bg=DIR` (property footage frames) or a per-beat `bg` photo in `data.js`. Only real property facts the client
supplies belong on screen; the template never adds numbers.
