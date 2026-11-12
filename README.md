# EVA Video Style v1.0 · source-only release candidate

This parentless, one-commit branch is the local publication candidate for EVA Core 1.0.0 and 23 independently installable templates. It was reconstructed only from the exact ZIP payloads that passed final integrity, installation and representative rendering validation; it was not copied from the Studio/SaaS tree.

**Publication status: RIGHTS-CLEARED, LOCAL ONLY.** EVA Core and all 23 included templates are MIT, Free and approved for public download. Do not push this branch, create a tag, attach ZIPs or publish a GitHub Release until the owner gives a separate explicit publication instruction.

## Contents

- `EVA-Core/`: Skill, Registry, ASR adapter, Planner, Engine, Renderer, QA, installer, documentation and bundled OFL fonts.
- `templates/TNN/1.0.0/`: one source payload per independently selectable template.
- `download-manifest.json`: exact names and SHA-256 values of the final ZIP set.
- `SHA256SUMS`: outer checksums for `EVA-Core.zip` and all 23 template ZIPs. The archives remain local and are deliberately not tracked here.
- `SOURCE_MANIFEST.sha256`: checksum inventory of this source snapshot.
- `PUBLIC_DISTRIBUTION_CLEARANCE.md`: public, non-sensitive rights-clearance summary.
- `THIRD_PARTY_NOTICES.md`: bundled and host-installed dependency notices.

Release template IDs:

`T01–T07`, `T09–T17`, `T19–T21`, `T23–T24`, `T26–T27`.

T08, T25 and T28 are excluded. T18 and T22 are retired and must not be reused. T26 is Vintage Story / 复古拼贴故事 and supports 9:16 only; T28 remains Real Estate and is not packaged.

## Install and use

Install Core once, then add only the templates you want. Full prerequisites and reproducible commands are in [`EVA-Core/docs/independent-core.md`](EVA-Core/docs/independent-core.md).

```sh
unzip EVA-Core.zip -d eva-video-style

python eva-video-style/EVA-Core/tools/packages/install.py \
  --root eva-video-style install-template T01-1.0.0.zip \
  --id T01 --version 1.0.0

python eva-video-style/EVA-Core/core/pipeline.py edit talk.mp4 jobs/t01 \
  --install-root eva-video-style \
  --templates T01 --aspect 9:16 \
  --asr-python /path/to/eva-asr/.venv/bin/python
```

You may add `--srt talk.srt` instead of running ASR. EVA Core has no fixed duration limit: it edits the complete input (minimum 3 seconds), rendering long videos in 10-second chunks with continuous audio and captions. Only your machine's time, disk and memory set practical limits. No Studio account, billing system or cloud service is included.

## Deliberate exclusions

This branch contains no Studio/SaaS implementation, deployment workflow, generated video, demo media, user media, model weight, music file, credential, log, ZIP archive or unrelated Git history. Registry records contain a few textual provenance paths that name historical Studio files; no referenced Studio source is present.

See [`RELEASE_NOTES.md`](RELEASE_NOTES.md), [`PUBLIC_DISTRIBUTION_CLEARANCE.md`](PUBLIC_DISTRIBUTION_CLEARANCE.md) and [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md) before any publication action.

## License

EVA Core and all 23 included templates are licensed under the [MIT License](LICENSE). Third-party notices and non-bundled runtime dependencies are documented separately.
