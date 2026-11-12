# EVA Video Style · release notes

## Core 1.0.1 (corrective, prepared — not yet published)

- **No fixed duration limit.** Core 1.0.0 rejected inputs longer than 30.5 seconds and files over 200 MB. Those were the hosted EVA Video Studio launch limits and never belonged in the open-source Core. 1.0.1 edits the complete input (minimum 3 seconds): transcription, planning, rendering in 10-second chunks with global timestamps, continuous audio and captions, and QA all cover the whole source, including the ending.
- Optional host policy: `--max-seconds` / `--max-bytes` (default: no limit). An over-limit input is rejected before any work; nothing is cropped, sped up or summarised.
- `--preview-seconds` may exceed 30; it only sets the quick preview, the final render is always full length.
- New regression test `EVA-Core/core/tests/test_duration.py` (synthetic media, no network, no paid API).
- Template packages are unchanged (they never contained the limit); only `EVA-Core.zip`, `SHA256SUMS` and `download-manifest.json` change. The published v1.0.0 assets are not replaced.
- Reproducible packaging: `EVA-Core.zip` is now built with `EVA-Core/tools/packages/build_core.py` using stored (uncompressed) members, so every OS, Python version and compression library produces the identical archive (sha256 `cc801a0656d9ae5fedd49ed2a2d549db50747241f5ef7b789405f9f2e72723b8`, about 1.8 MB). Deflate output differs between zlib, zlib-ng and distribution-patched zlib, which made the 1.0.0-style archive impossible to reproduce on a different build host. Archive contents and their internal checksums are unaffected.

# EVA Video Style v1.0.0 · draft release notes

Status: rights-cleared local source-only release candidate; not yet published.

## Included

- EVA Core 1.0.0: real MP4 → locked eva-asr or optional SRT → Content Planner → installed Template Registry → preview → final Renderer → QA.
- Independent installation, discovery and uninstall for 23 versioned template packages.
- MIT / Free / public-download Registry policy for the exact release scope.
- T26 fixed as Vintage Story / 复古拼贴故事, with all nine approved layouts preserved and 9:16-only compatibility enforced.
- Deterministic ZIPs, archive-internal checksums, outer `SHA256SUMS` and a selective `download-manifest.json`.
- Source-only packaging with no Studio/SaaS, private media, generated videos, credentials, models or deployment workflow.

## Final acceptance

- Registry validation: 28/28 IDs; 23 public release IDs; T18/T22 retired; excluded IDs remain closed.
- Package integrity and static public-payload audit: 24/24 PASS, zero blockers.
- Fresh install/discovery/uninstall: 23/23 PASS.
- Deterministic rebuild: all 24 ZIPs and the download manifest are byte-identical across two builds.
- Representative final-package SRT rendering: T01 and T17 in 16:9 and 9:16, plus T26 in 9:16, all PASS.
- Representative final-package raw MP4/no-SRT rendering: T01 and T26 both completed locked ASR, preview, 1080×1920 final output and QA with zero WARN/FAIL.
- All animation, renderer and template runtime code remains byte-identical to the technically accepted baseline; final archive changes are limited to approved Registry/access metadata, public documentation, asset-policy wording and derived checksum files.

## Known limits

- Core 1.0.0 rejected inputs longer than 30.5 seconds. That limit belonged to the hosted EVA Video Studio launch, not to this open-source project; Core 1.0.1 removes it (see below).
- `eva-asr` must use commit `91ff24122f1cfed6c166372a597bff83ea3ab405` and its locked environment. Core and ASR environments remain separate because mismatched Torch/TorchAudio/TorchCodec/FFmpeg ABIs previously failed.
- FFmpeg is host-installed and must include libass and the required H.264/AAC encoders.
- T17 requires host-installed Inter for intended typography. Inter and Noto Sans CJK SC are not bundled.
- A previous longer T01 visual review recorded a non-blocking caption-contrast WARN. The final 10.033-second raw-ASR run has zero WARN, but longer/content-dependent T01 output still merits visual review.
- ASR/alignment model data and the GPL-3.0 RVM matting model are downloaded separately and are not included.

## Not included

Studio/SaaS code, account/billing logic, deployment files, private or sample media, generated MP4/JPG files, credentials, logs, model weights, music and unrelated Git history are not part of this branch or its ZIP payloads.
