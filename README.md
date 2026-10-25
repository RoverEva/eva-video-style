# Eva Video Style

**An open-source AI video-editing skill for talking-head videos.** Give Claude a raw recording plus its subtitles, pick a style, and get back a finished, motion-designed video with captions in English, or in Chinese and English.

Twenty-two ready-to-use templates cover cinematic, futuristic tech, social media and minimalist looks. Every frame is rendered from code, so results are deterministic and editable.

> Demo reel and per-template demos (English and Chinese + English): see the [latest release](https://github.com/RoverEva/eva-video-style/releases).

## What it does

- **A presenter window that keeps moving.** Full-bleed → card → circle, with face-safe framing: the speaker's whole head is always visible.
- **Kinetic graphics timed to the words.** Cards, giant type, stickers, gauges, maps and real screen recordings pop in exactly when they are said.
- **22 named templates (T01–T22).** From Acid Lime Kinetic and Electric Blue Console to Old Newspaper, Science Network, Footage Intro, Fast-Paced Social, Clean & Minimal and Bold Motion Graphics. See [`references/templates.md`](references/templates.md).
- **Captions your way.** English-only, or bilingual (Chinese line on top, English underneath). Machine-translation slips are fixed in the burned captions only, and your SRT is never edited. On footage-heavy shots, captions move to the clearest part of the frame.
- **Real footage, handled properly (T19).** AI cut-out of the speaker (natural colours), fast background swaps, the clip pushes in, the presenter shrinks into a circle that stays clear of the action.
- **Clean sound.** No background music: the original voice plus short sound effects, normalised to about -16 LUFS.

## Use it as a Claude skill

1. Copy this folder into your skills directory (for example `~/.claude/skills/eva-video-style/`), or upload it as a custom skill.
2. Ask: *"Edit this video in Eva Video Style"*, and attach the raw video plus an SRT (English, or bilingual Chinese + English).
3. Name templates if you like (*"use T19 for the news clips and T21 for the summary"*), or let Claude pick per section.

## Use the toolkit directly

Requirements: Node 18+, Python 3 with `numpy` (plus `opencv-python` and `onnxruntime` for T19), FFmpeg with libx264 and libass, and the system fonts listed in [`engine/fonts/README.md`](engine/fonts/README.md).

```bash
npm install && npx playwright install chromium
pip install numpy opencv-python onnxruntime

scripts/extract_frames.sh my_talk.mp4 media/eva                                  # speaker as 30 fps frames
node scripts/render.mjs template/section/index.html --stills check --times 1,4,8  # layout check
node scripts/render.mjs template/section/index.html --out sec/s1.mp4             # silent render
python3 scripts/captions.py my_talk.srt 0 99999 out/my_talk config.json          # captions (.srt + .ass)
```

The full workflow, from raw video to delivered master, is in [`references/pipeline.md`](references/pipeline.md). The engine API is in [`references/engine-api.md`](references/engine-api.md), and the look and rules are in [`references/style-guide.md`](references/style-guide.md).

## Repository layout

| Path | What it is |
|---|---|
| `SKILL.md` | Skill entry point: rules, deliverables, quick start |
| `engine/` | Small deterministic HTML motion engine: presenter window, scenes, design kit, template helpers, fonts |
| `template/` | A starter section plus a full demo section for every template |
| `scripts/` | Frame extraction, Playwright renderer, sound effects, captions, caption placement, AI cut-out, assembly, contact sheets |
| `references/` | Style guide, pipeline, engine API, template library with sample frames |

## Principles

- The speaker's whole head is always visible; the window never crops the face.
- No background music, ever.
- No invented facts, numbers or screens. Anything conceptual is labelled **ILLUSTRATIVE**.
- Source files and earlier versions are never overwritten.

## License

[MIT](LICENSE) © 2026 RoverEva. Bundled fonts are under the SIL Open Font License 1.1 (see `engine/fonts/licenses/`). The optional T19 cut-out model ([Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting), GPL-3.0) is downloaded on first use and is not part of this repository.

## Credits

`engine/land.js` (the globe land mask) is rasterised from [johan/world.geo.json](https://github.com/johan/world.geo.json), public domain, based on Natural Earth. Demo presenter: an AI-generated model.
