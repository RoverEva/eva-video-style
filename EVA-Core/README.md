# EVA Core 1.0.0 release candidate

Install this archive once, then install independently selected template ZIPs. This candidate runs the account-free MP4 → ASR/SRT → Planner → Registry → Renderer → QA pipeline. EVA Core and the 23 release templates are cleared for MIT/Free public distribution, but this local candidate has not been published. A separate owner approval is required before any push, tag or GitHub Release.

## Prerequisites

Node 20+, Playwright/Chromium, Python 3.10-3.13, libass-enabled FFmpeg, and the exact eva-asr revision in `core.lock.json`. Run `npm ci`, install `requirements-core.txt`, clone eva-asr at the locked commit, verify its uv.lock SHA-256, and run `uv sync --locked`.

## Install and edit

```sh
python EVA-Core/tools/packages/install.py --root /path/to/eva install-template T03-1.0.0.zip --id T03 --version 1.0.0
python EVA-Core/core/pipeline.py edit talk.mp4 jobs/t03 --templates T03 --aspect 9:16 --asr-python /path/to/eva-asr/.venv/bin/python
python EVA-Core/core/pipeline.py edit talk.mp4 jobs/mix --templates T01,T17,T23 --mode multi --aspect 16:9 --srt talk.srt
```

Outputs are `JOB/out/preview.mp4`, `JOB/out/final.mp4`, captions, logs and QA reports. No Studio account, billing or cloud service is used. See `docs/independent-core.md`.
