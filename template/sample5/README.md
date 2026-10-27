# 5-second template samples

New templates (T24 onward) are demoed on one short clip: a 5-second AI-presenter take (`templatechoose_demo.mp4`). Short samples are quicker to render and review than the 15-second intro used by `template/demo/`.

`sample.js` holds the shared settings (`S5.END`, the presenter source, `S5.cut(t)` for the AI cut-out frame at time `t`).

| Folder | What it shows |
|---|---|
| `t24/` | T24 Luxury Nude Motion, 5 s sample |
| `t24-layouts/` | all eight T24 layouts in turn (2 s each), a reference for every layout call |

## Media

Put the clip's frames in `template/sample5/media/` (not in the repository):

```bash
scripts/extract_frames.sh templatechoose_demo.mp4 template/sample5/media/eva
python3 scripts/matte.py template/sample5/media/eva 0 149 template/sample5/media/cut   # cut-out for T24
```

Render with `node scripts/render.mjs template/sample5/t24/index.html --out out/t24.mp4`, then add the voice, SFX and captions as in [`references/pipeline.md`](../../references/pipeline.md).
