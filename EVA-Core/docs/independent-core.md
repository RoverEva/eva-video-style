# Independent EVA Core and template packages

This release-candidate workflow is local and account-free. It does not use EVA Video Studio, Modal, Vercel, R2, Stripe, or a private API.

## What gets installed

- `EVA-Core.zip`: Skill, ASR adapter, Content Planner, Template Registry, Engine, Renderer, captions and QA.
- 23 source-backed `TNN-1.0.0.zip` archives: T01–T07, T09–T17, T19–T21, T23–T24 and T26–T27. Each contains only that template's original scene, automatic-edit registration/configuration, metadata and dependency documentation.
- Model weights are not inside any ZIP. `eva-asr` is installed separately at the exact revision in `core.lock.json`.

The template Registry refuses an absent template, multiple installed versions of the same ID, an incompatible Core/Engine/plan schema, a non-renderable template, or an unsupported aspect ratio. The 23 v1.0 release records are MIT, Free and publicly downloadable; excluded, planned and retired IDs remain closed.

## 1. Install Core

```sh
mkdir eva-video-style
unzip EVA-Core.zip -d eva-video-style
cd eva-video-style/EVA-Core

python3 -m venv .venv
.venv/bin/pip install -r requirements-core.txt
npm ci
```

Install a Chromium-compatible browser. You may use Playwright's Chromium or an existing Chrome executable. FFmpeg must include the `ass` or `subtitles` filter; a minimal FFmpeg build cannot burn or verify captions.

```sh
ffmpeg -hide_banner -filters | grep -E ' ass | subtitles '
```

On macOS, Homebrew's keg-only `ffmpeg-full` supplies libass. Either put its `bin` directory on `PATH` or pass `--ffmpeg-dir /opt/homebrew/opt/ffmpeg-full/bin` to the pipeline.

## 2. Install locked eva-asr

Read `core.lock.json`. For Core 1.0.0 the required Git revision is `91ff24122f1cfed6c166372a597bff83ea3ab405` and the recorded `uv.lock` SHA-256 is `625a250006c58903a09bbbe4b635d770a2dce71d7fd5880a55dd82c0a9f82982`.

```sh
git clone https://github.com/RoverEva/eva-asr.git
cd eva-asr
git checkout 91ff24122f1cfed6c166372a597bff83ea3ab405
shasum -a 256 uv.lock
uv sync --locked
cd ../eva-video-style/EVA-Core
```

Do not install `eva-asr@main` or use an unconstrained `pip install`. The Core and ASR environments are intentionally separate: Core's `.venv` runs face detection, planning and QA; eva-asr's `.venv` runs transcription.

The default local config uses the English `small` Whisper model with word alignment enabled. The first run may download the model and English alignment checkpoint. Advanced users can copy `config/asr.local.json` and choose a larger compatible model.

## 3. Install or remove templates

```sh
python tools/packages/install.py --root .. install-template ../../T01-1.0.0.zip --id T01 --version 1.0.0
python tools/packages/install.py --root .. list
python tools/packages/install.py --root .. uninstall --id T01 --version 1.0.0
```

Install any v1.0 template in the same way. The installer verifies the archive's internal checksum manifest and safe paths. Compare the archive SHA-256 with `SHA256SUMS`. T08/T25/T28 have no v1.0 ZIP; T18/T22 are retired. T26 installs and renders as Vintage Story / 复古拼贴故事 in 9:16 only. The Registry correctly rejects a T26 request with `--aspect 16:9`.

## 4. Edit a raw MP4

Run from `EVA-Core`. This command performs real ASR, word-timed planning, a watermarked preview, the full-resolution final render and QA:

```sh
.venv/bin/python core/pipeline.py edit raw/talk.mp4 jobs/t01 \
  --install-root .. \
  --templates T01 \
  --aspect 9:16 \
  --asr-python ../../eva-asr/.venv/bin/python \
  --browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --ffmpeg-dir /opt/homebrew/opt/ffmpeg-full/bin
```

For landscape T17, use `--templates T17 --aspect 16:9`. To mix compatible installed templates, use:

```sh
.venv/bin/python core/pipeline.py edit raw/talk.mp4 jobs/mixed \
  --install-root .. --templates T01,T17 --mode multi --aspect 9:16 \
  --asr-python ../../eva-asr/.venv/bin/python
```

`--mode multi` uses the requested order and cuts at a real pause near each section boundary. `--mode auto` chooses how many of the explicitly supplied installed templates fit the clip. It never reaches into an uninstalled or Studio-private catalog.

T26 requires the Core environment from `requirements-core.txt`. On first use, `scripts/matte.py` downloads the RVM MobileNetV3 ONNX model into the user's cache, verifies the SHA-256 pinned in `core.lock.json`, and creates a private alpha-frame sequence from the user's MP4. The GPL-3.0 model, matte frames and user media are never put in a template ZIP:

```sh
.venv/bin/python core/pipeline.py edit raw/talk.mp4 jobs/t26 \
  --install-root .. --templates T26 --aspect 9:16 \
  --asr-python ../../eva-asr/.venv/bin/python
```

## 5. Use an existing SRT

Add `--srt raw/talk.srt`. The original SRT is copied, never edited. Word times are interpolated inside each cue for planning. ASR is not run, so `--asr-python` is unnecessary.

For best results, use sentence-sized cues rather than one cue covering the entire clip. The QA report flags cues that are too short, too long or extend past the video.

## Outputs and failure handling

- `JOB/out/preview.mp4`: 720×1280 or 1280×720, watermarked, limited to the requested preview duration.
- `JOB/out/final.mp4`: 1080×1920 or 1920×1080, the complete input length, H.264/AAC, captions burned, original voice plus procedural SFX.
- `JOB/out/captions.srt`: editable delivered captions.
- `JOB/out/report_preview.json` and `report_final.json`: dimensions, duration, template versions and QA verdict.
- `JOB/qa/pre` and `JOB/qa/post*`: machine-readable report, summary and evidence.
- `JOB/logs`: every local command and exit code.
- `JOB/out/failure.json`: failed stage, command and log location.

QA FAIL blocks output acceptance. WARN does not silently disappear: inspect its evidence and record the decision. Rerunning the identical command resumes completed stages; changing input, install root or options requires a new job directory.

EVA Core has no fixed duration or file-size cap: the final render always covers the complete input (minimum 3 seconds), split into 10-second render chunks with global timestamps, one continuous audio track and one caption file. `--preview-seconds` only sets the length of the quick watermarked preview. A host application may impose its own policy with `--max-seconds` / `--max-bytes` (or the `max_seconds` / `max_bytes` options); both default to no limit, and an over-limit input is rejected before any work, never cut. Practical limits are your machine's render time, disk space and memory. Inter and Noto Sans CJK SC are host font dependencies. The ZIP includes Anton, Archivo Black, Playfair Display and Space Mono plus their OFL texts.

## Current package boundary

All 23 v1.0 templates pass automatic SRT editing in every declared aspect: 22 pass 16:9 and 9:16, while T26 passes 9:16 and rejects unsupported 16:9. T01 and T26 also pass the raw-MP4/locked-ASR path, and T03+T17 plus T17+T26 pass compatible multi-template jobs. T01/T02/T09/T17/T20/T21/T23 use automatic skins extracted from the existing runtime; T26 loads its own nine-layout runtime library; the remaining templates use the shared Core adapter plus template-owned visual configuration. Original manual scenes are packaged byte-for-byte, but automatic adapter visuals still require product-owner regression approval.

T18/T22 remain retired. T08/T25/T28 are excluded; the historical `template/industry/t26/` directory is identified as T28 Real Estate provenance and is never packaged as T26. T26 and the other 22 release templates are rights-cleared under MIT as Free public downloads. That clearance covers the source-only packages, not generated demos, user footage, separately downloaded model weights, private Studio assets or future templates. The local candidate remains unpublished until the owner separately approves the remote publication action.
