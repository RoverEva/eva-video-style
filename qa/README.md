# Eva Video QA (v1.0)

Automatic quality checks for every Eva Video Style render, for all templates (T01–T28 and future Eva Talk / Ads /
Science / Explain templates). Everything runs locally with FFmpeg, NumPy and OpenCV (plus Playwright for page checks).
No frames are sent to an LLM, and no paid APIs are used.

| Stage | When | What it looks at |
|---|---|---|
| **A · pre-render** `python3 -m qa pre` | before the final render | input video, SRT / ASR word times, plan, face calibration, presenter frames, and a **trace of the section page** (every scene stepped with `renderAt(t)`, no screenshots): missing images / fonts / scripts / frames, JavaScript errors, the presenter's head vs. her window and the frame, presenter scale, text drawn over her face, text overflow, the caption zone, scenes that never animate |
| **Guard in `scripts/render.mjs`** | during every `--out` render | a missing file or a JavaScript error stops the render (exit 4) and removes the partial file. `--no-qa` turns this off |
| **B · post-render** `python3 -m qa post` (run automatically by `scripts/assemble.sh`) | after assembly | the real frames: streams, codec, size, fps, SAR, duration, decode errors, black / blank / frozen spans, loudness, **face tracking** (crop, forehead / chin, enlargement, stretch, visibility, sharpness vs. the source), **burned captions** (exact libass masks: frame edge, safe area, over the face, line count, contrast, burned or not, timing vs. the delivered .srt), caption / speech timing |

Severity: **FAIL** = confirmed critical defect, blocks delivery (exit code 1). **WARN** = uncertain or subjective
(low-confidence face, possible blur, suspicious motion, ambiguous timing). **PASS** = verified. A check that could
not run (no source, no captions, no detector) is listed under **Not run (unverified)**. It is never counted as passed.
QA never changes a layout, font, crop or animation. It only reports, with a suggested fix.

## Commands

```bash
# finished video (the full set of inputs gives the most checks)
python3 -m qa post out/NAME_CN-EN.mp4 --clean out/NAME_Clean.mp4 --source raw/talk.mp4 \
    --ass out/NAME_CN-EN.ass --srt out/NAME_CN-EN.srt --aspect 16:9 --template T17 --out out/NAME_qa
#   --plan plan.json (scenes/templates/cards)  --static 2,5 or --static 12.0-15.5 (intended still parts)
#   --size 720x1280 (non-standard deliverable)  --expected-frames N  --kind preview  --config my_thresholds.json

# section page before rendering
python3 -m qa pre --page s1/index.html --input raw/talk.mp4 --srt raw/talk.srt --aspect 9:16 --template T26 \
    --query "eva=../media/eva&srcw=1080&srch=1920&face=.5,.36,.26" --out check/s1_qa

python3 -m qa srt raw/talk.srt --duration 73.6          # SRT syntax + timing only
python3 -m qa job JOB_DIR pre|post [--preview]          # EVA Video Studio job folder (saas/worker layout)
```

Exit code: 0 = PASS or WARN, 1 = FAIL, 2 = usage / input error.
Output: `qa-report.json` (schema `eva-qa/1`), `qa-summary.md`, `evidence/*.jpg` (marked-up frames for visual
problems, at most 3 per check).

`scripts/assemble.sh` runs Stage B on its two masters and writes `OUT_BASENAME_qa/`.
`EVA_QA=block` (the default) exits with code 3 on FAIL. `EVA_QA=report` reports and never fails. `EVA_QA=off` skips QA.
`EVA_QA_ARGS="--template T17 --plan plan.json --aspect 9:16"` passes extra options.

## Issue format (qa-report.json)

```json
{"check": "CAP_FACE", "severity": "FAIL", "t": [0.6, 1.6], "scene": 0, "template": "T17",
 "message": "caption covers 12% of the presenter's face: \"Hi, I'm Eva.\"",
 "evidence": "evidence/cap_face_0001.10.jpg",
 "fix": "keep captions in the caption zone below the face for this pose (raise MarginV or move the presenter window); do not cover the face",
 "data": {"worst_cover": 0.12, "samples": 3, "confidence": "high"}}
```

## Thresholds

`qa/thresholds.json` sets them in this order: `defaults` < `categories` (talk, ads, science, explain) < `templates`
(T17, T26 …) < a `--config` file of the same shape. A template that crops or zooms on purpose declares it there
(`"face": {"allow_crop": true, "max_subject_scale": 2.0}`), and QA honours it. A plan scene can also carry `static`,
`allow_crop` or `allow_face_hidden`. New templates need no entry; they get the defaults.

Template rules built in: T17 / T19 / T26 / T27 keep text off the face (`face_safe_text`). T26 keeps the footage's own
scale (enlargement > 1.08× warns, > 1.2× on consecutive confident frames fails). T28 must not be resized. T24 / T25
are clarity references (stricter sharpness, applied only to those templates).

## How the face checks work, and their limits

The face is detected in the **source** footage (OpenCV Haar, else scikit-image LBP, else the job's face
calibration). That face patch is then **tracked into each rendered frame** with multi-scale normalised
cross-correlation. This gives position, scale (enlargement), width/height distortion (stretch), the part outside the
frame (crop) and per-cell visibility. Rendered frames are stylised (cut-outs, rings, grades, text), and that is where
generic face detectors are weakest. A FAIL needs high-confidence matches on consecutive samples outside transitions;
anything less is a WARN. If no frame matches with confidence, every face check is marked unverified.

- Frontal-face detection only: profile shots, heavy occlusion, or no presenter on screen give "unverified", not PASS.
- The hair line and chin are estimated from the brows-to-chin face box. A forehead or chin cut is a FAIL only when it
  is deep (≥ 20 % of the head); shallower cuts WARN.
- Caption / speech timing uses an energy-based voice detector (when someone is speaking). It is **not** word
  alignment, and timing problems are only ever WARN. Word-level alignment needs eva-asr word times (`PRE_TRANSCRIPT`).
- Compression damage is judged by detail lost against the source (`QUALITY_SHARPNESS`) plus a conservative bitrate
  floor. There is no no-reference blockiness metric, because the ones tried were not reliable on H.264.
- Animation checks only warn. A low frame difference alone never fails a video.

## Tests

```bash
python3 -m pytest qa/tests -q     # ≈ 5 min the first time (fixtures are built once and cached; EVA_QA_FIXTURES=DIR)
```

The fixtures (`qa/tests/fixtures.py`) are built from a real presenter clip (`saas/tests/media/education.mp4`), each
with one known, synthetic defect, plus engine renders of `qa/tests/pages/case/`. The tests also use the committed real
worker renders in `site/demos/`, both as-is (they must pass) and with defects added (they must fail). The tests cover
the QA logic and its thresholds. They do **not** establish face-detection accuracy on arbitrary real footage.

Measurements are cached in `~/.cache/eva-qa` (decode pass, face tracking), so re-running QA with other thresholds is
fast. `EVA_QA_CACHE=off` disables the cache.
