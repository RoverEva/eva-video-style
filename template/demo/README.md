# Template demos

One section per template (`t01` … `t23`; T18 and T22 were retired). Every demo plays the same 15-second self-introduction, so you can compare the 21 styles line by line. The rendered videos (English, and Chinese + English) are attached to the [latest release](https://github.com/RoverEva/eva-video-style/releases).

`intro.js` holds the shared timing: when each spoken line starts (`IN.T`), the four beats (`IN.B`) and the presenter source. Each `tNN/scenes.js` reads those times, so if you record your own intro, update `intro.js` and every demo follows.

## Media

The demos read frames from `template/demo/media/` (not in the repository). To render them yourself, fill it like this:

| Folder | What goes in it | Used by |
|---|---|---|
| `eva/` | The presenter video as 30 fps JPGs: `scripts/extract_frames.sh intro.mp4 template/demo/media/eva` | all |
| `cut/` | AI cut-out of the presenter: `python3 scripts/matte.py template/demo/media/eva 0 450 template/demo/media/cut` (RGBA WebP) | T19 |
| `web/`, `wb/`, `fly/`, `whis/`, `sent/`, `match/` | Screen recordings as 30 fps JPGs (T19 also swaps through these as its fast backgrounds) | T03, T06, T08, T09, T12, T13, T19 |
| `egg/`, `jmw/` | Short cartoon clips as 30 fps JPGs | T07, T09 |

No images ship with the demos: everything here is your own material. Swap in your own footage freely; the folder names are the only contract. Frame counts are set where each clip is played (`C.seq(dir, t, frames)`).

## Render

```bash
node scripts/render.mjs template/demo/t05/index.html --stills check --times 1,6,10,14   # layout check
node scripts/render.mjs template/demo/t05/index.html --out out/t05.mp4                  # silent render
```

Then add the voice and sound effects and burn the captions as described in [`references/pipeline.md`](../../references/pipeline.md).
