# Responsive Video Layout (16:9 + 9:16)

One engine, two canvases. A section renders 1920×1080 by default, or 1080×1920 when the page URL has `?ar=9:16`
(`node scripts/render.mjs SECTION/index.html --ar 9:16 ...`). Both are 30 fps. Nothing is cropped: each template states
where its elements sit in portrait, and every 16:9 value stays exactly as it was.

## How a template becomes responsive

```js
const C = EV, V = C.portrait, pk = C.pick;          // pk(landscapeValue, portraitValue)
const CARD = pk({ x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 },   // original 16:9 pose, untouched
                { x: 190,  y: 900, w: 700, h: 660, r: 36, s: 1.5 });  // 9:16 pose
k.disp(L, 'EVA VIDEO STYLE', '#fff', pk(130, 120), pk(110, 64), pk(120, 230));
if (V) C.fit(titleEl, 952);                          // shrink long lines to the safe width (measured after fonts load)
```

Rules: write `pk(old, new)` instead of editing a 16:9 number; keep text inside `EV.SAFE`; keep the presenter's face above the
`caption` zone; check with `?guides=1`.

## Zone remap (for templates whose 16:9 scenes are a content block beside the presenter)

```js
C.portLayout({ box: [x, y, w, h], cover: [sceneIndex], keep: [sceneIndex], at: { i: { box, top, maxH } }, inbox: [keyIndex] });
C.portFull(el);   // full-frame element (footage, grade) leaves the box and fills 9:16, stretched
C.portCover(el);  // full-frame drawing (canvas floor, rays, sky) leaves the box and covers 9:16 at its own proportions
```

In 9:16 each scene is still built in its 1920×1080 coordinates, inside a box that is scaled into the top content zone
(`box` = the 16:9 rectangle holding the content). The presenter path is then re-laid below the block: full stays full,
circles become a circle and cards a card in the presenter zone; `inbox` keys stay inside the content (presenter inside a
globe, sun or hub). `cover` scenes fill the frame; `at` gives one scene its own box (text over a full-bleed presenter goes
in the lower zone); `keep` leaves a natively 9:16 scene alone. In 16:9 every call is a no-op.

## API (engine/engine.js)

| Name | What it is |
|---|---|
| `EV.W`, `EV.H`, `EV.AR`, `EV.portrait` | stage size and aspect |
| `EV.pick(land, port)` | aspect switch (returns `land` in 16:9) |
| `EV.SAFE` | margins clear of phone UI. 9:16: top 210 (status / tabs), bottom 430 (platform caption, music, buttons), right 150 (like / comment / share rail), left 64. 16:9: title-safe |
| `EV.zone(name)` | `safe`, `head`, `body`, `lower`, `caption` rectangles for the current aspect |
| `EV.pose(name, extra)` | presenter window presets `full`, `card`, `split`, `pip`, `pipTop` for the current aspect |
| `EV.fit(el, maxW, minPx)` | deterministic text fit (runs once, after fonts are ready, before frame 0) |
| `EV.faceRect(windowRect)` | where the face lands on stage for an Eva window, to keep cards off it |
| `EV.src` | presenter footage size; phone footage is `{ w: 1080, h: 1920 }`. Face calibration (`EV.face`) is a fraction of this frame |
| URL `eva=`, `srcw=`, `srch=`, `face=x,y,h` | per-render overrides (renderer / SaaS worker) for the presenter frames, their size and face calibration |
| URL `guides=1` | draws the safe area, phone-UI zones and the caption zone (layout checks only) |

Any footage orientation works with any output aspect: the Eva window covers its rectangle from the source frame and centres on
the calibrated face, capped so the whole head stays visible.

Shared helpers in `kit.js`, `templates.js` and `cards.js` now size their canvases, SVGs and full-frame layers from `EV.W/EV.H`,
and `K.EC.region()` / JSON card positions use the current stage, so the EVA Card System places cards in either aspect.

## Template status (Phase 1)

16:9 regression (re-run after every port): all 29 pages (21 demos, 4 card demos, T24 + layouts, section template, layouts index) were rendered at
8 timestamps before and after the change on identical media and pixel-compared. The only differences are a few dozen pixels
inside the presenter window, the same JPEG-decode jitter seen when the unmodified code is rendered twice.

| Template | 9:16 | Notes |
|---|---|---|
| T01, T09, T17, T20 | ✅ native 9:16 | hand-placed with `pick()`; T09 `?wall=DIR&wallN=FRAMES` builds the opening wall from playing slices of one video |
| T19 Footage Intro | ✅ native 9:16 | cut-out rig re-laid with `pick()`; needs `scripts/matte.py` cut-out frames, `?cut=DIR` |
| T24 Luxury Nude (`template/sample5/t24`) | ✅ native 9:16 | cut-out lower and centred, card groups scaled into the top zone; `?cut=DIR&cutN=FRAMES` |
| T02–T07, T10–T16, T21, T23, T27 | ✅ zone remap | `portLayout` boxes; backgrounds via `portFull` / `portCover` (T07 footage, T14 floor, T15 sky, T16 bursts); T27 keeps the presenter over the video wall |
| T26 Vintage Story (`template/demo/t26`) | ✅ 9:16 only | nine native vertical layouts; Registry rejects 16:9 rather than stretching them |
| Card demos t01 / t09 / t17 / t20 | ✅ zone remap | background scene `cover`, card block top, presenter below |
| `template/cards/layouts`, `template/sample5/t24-layouts` | ⏳ reference pages | layout catalogues, still 16:9 only |
| Burned captions (`scripts/captions.py`, `caption_zones.py`) | ⏳ | still PlayRes 1920×1080; needs a portrait style set using `EV.zone('caption')` |
| SaaS (`saas/worker/*`) | ⏳ | `pipeline.py` rejects portrait input, `planner.py` / `auto.js` assume 1920×1080; needs an `aspect` job field passed through to `--ar` |
