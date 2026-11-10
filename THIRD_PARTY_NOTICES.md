# Third-party notices

This source-only candidate does not vendor Node/Python packages, browser binaries, FFmpeg, ASR repositories/models, matting models, host fonts, music or demo media.

## Bundled fonts

EVA Core includes unmodified Anton, Archivo Black, Playfair Display and Space Mono font files. Each is distributed under SIL Open Font License 1.1. The corresponding copyright/license texts are in `EVA-Core/engine/fonts/licenses/` and must remain with every copy.

The six files were byte-compared with the official Google Fonts repository. Upstream: <https://github.com/google/fonts>

## Geographic data

`EVA-Core/engine/land.js` contains a rasterized land mask derived from `johan/world.geo.json`, released under the Unlicense/public-domain dedication and based on Natural Earth public-domain data.

- <https://github.com/johan/world.geo.json/blob/master/UNLICENSE>
- <https://www.naturalearthdata.com/about/terms-of-use/>

## Host-installed software

- Playwright: Apache License 2.0 — <https://github.com/microsoft/playwright/blob/main/LICENSE>
- NumPy: BSD 3-Clause — <https://github.com/numpy/numpy/blob/main/LICENSE.txt>
- OpenCV: Apache License 2.0 — <https://github.com/opencv/opencv/blob/4.x/LICENSE>
- ONNX Runtime: MIT — <https://github.com/microsoft/onnxruntime/blob/main/LICENSE>
- eva-asr/WhisperX fork: locked exact commit, BSD 2-Clause LICENSE; transitive packages and downloaded models retain their own terms.
- FFmpeg: LGPL-2.1+ by default, with GPL applying to builds that enable GPL components — <https://ffmpeg.org/legal.html>
- Inter: SIL OFL 1.1 — <https://github.com/rsms/inter/blob/master/LICENSE.txt>
- Noto Sans CJK SC and Noto Color Emoji: host-installed font projects under their upstream terms; no files from these projects are bundled.

## Optional runtime model

The Robust Video Matting MobileNetV3 ONNX model is not bundled. T26 may download the exact hash declared in `EVA-Core/core.lock.json` when presenter cut-out is requested. Upstream uses GPL-3.0: <https://github.com/PeterL1n/RobustVideoMatting/blob/master/LICENSE>. Do not add that model to the MIT release assets without a separate distribution review.

## User-provided material

Users are responsible for rights to their input MP4/SRT, music, fonts and other media. EVA demo media and generated outputs are not part of this release candidate.
