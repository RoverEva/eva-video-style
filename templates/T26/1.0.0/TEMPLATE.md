# T26 · Vintage Story · 1.0.0 (9:16)

Vintage paper collage: torn paper stage, newspaper statement cards, tape, red pen marks and the real presenter as a
cream-outlined AI cut-out on top of the text. No sound in the template (SFX are designed per video with `K.cue`).
Implementation reused unchanged from branch `t26-rebuild` (`04f6842`, `7e0aa32`); the additive auto-mode options
(`w.auto`, `fitW`, layout 0) are only used by the automatic-edit skin and do not change the 9 layouts or the demo.

| File | Role |
|---|---|
| `t26.js` | template-owned library (`K.T.vt*`): palette, stage, cards, marks, cut-out presenter, 9 layouts + animations. Packaged as `runtime/lib.js`. |
| `scenes.js` / `index.html` | design sheet: all 9 layouts, 1.6 s each (manual scene) |
| `demo-5s.js` / `demo-5s.html` | approved 5 s demo: layouts 01 → 03 → 05 → 09 |
| `auto-skin.js` + `skin.json` | EVA Core automatic-edit skin (`presenter: own`, `ownsCards`, `portrait: native`) |
| `test-16x9.html` | 16:9 harness for separate testing only (not registered; needs 16:9 footage + landscape layout pass) |

Layouts: 01 giant title · 02 two-column notes · 03 story card · 04 chart · 05 newspaper statement · 06 photo prints ·
07 icon tips · 08 how-it-works · 09 end card. Presenter: whole head visible, never scaled above the footage (s = 1).

## Media
`EVA_TEMPLATE_MEDIA` (default `../../sample5/media26`) must contain `eva/f_%05d.jpg` (HD frames, `extract_frames.sh`)
and `cut/f_%05d.webp` (`scripts/matte.py FRAMES 0 N OUT`). In EVA Core the pipeline writes both under `JOB/media/`.
Sample media is local only and not shipped.

## Render
```sh
node scripts/render.mjs template/demo/t26/index.html   --ar 9:16 --out t26_layouts.mp4
node scripts/render.mjs template/demo/t26/demo-5s.html --ar 9:16 --out t26_demo.mp4
python3 core/pipeline.py edit talk_9x16.mp4 jobs/t26 --templates T26 --aspect 9:16 --srt talk.srt
```

## Dependencies
Core `>=1.0.0 <2.0.0`, engine API `legacy-1`, plan schema `legacy-v1`. Fonts from Core: Anton, Playfair Display
(+ italic, used as the handwritten accent; Kaushan Script was the intended face and is not bundled). Cut-out:
`numpy`, `opencv-python`, `onnxruntime`; RVM MobileNetV3 ONNX (GPL-3.0) downloads on first use from GitHub releases.
Core verifies model SHA-256 `88d4531297118f595bf2fd60f6f566aec2e559393802d1f436c380f0cbbd2828` from `core.lock.json`.
Code/design distribution: owner-cleared under the repository MIT license (see
`docs/releases/T26-1.0.0-release-record.md`). Free/Pro tier is unconfirmed and `public_download: false` remains fail-closed
until the final GitHub Release approval.
