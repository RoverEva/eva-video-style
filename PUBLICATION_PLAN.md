# Safest publication plan

This plan keeps the existing `RoverEva/eva-video-style` repository so its identity, issues, watchers and Stars remain intact. It does not replace or force-push `main`.

## 1. Freeze the approved local inputs

- Source branch: `codex/v1.0-source-only-rc` at the exact root commit reported with this candidate.
- Release assets: the 24 local ZIPs whose hashes are in `SHA256SUMS`.
- Allowed companion assets: `SHA256SUMS`, `download-manifest.json` and approved release notes.
- Forbidden assets: demos, screenshots containing private media, logs, model weights, internal rights evidence and any file outside the manifest.

No source or asset should be rebuilt between final approval and publication. If anything changes, regenerate hashes and repeat validation under a new candidate.

## 2. Audit external push triggers

The source snapshot has no `.github` workflow, but repository-level Actions, installed GitHub Apps, webhooks, Vercel projects or other integrations may react to any branch push. Immediately before an authorized push:

1. Inspect default-branch workflows, repository rules, installed apps/webhooks and branch deployment settings.
2. Configure them to ignore `codex/v1.0-source-only-rc`, or obtain explicit approval for any unavoidable trigger.
3. Push only the exact local root commit to a new remote branch. Never force-push or merge `main`.

## 3. Verify the remote source

Clone the remote source-only branch into a clean directory. Verify that it has one root commit, no parent, the expected tree and a matching `SOURCE_MANIFEST.sha256`. Repeat the secret/media/workflow scan. Stop if any remote byte or tree entry differs.

## 4. Tag and draft Release

Only after separate approval:

1. Create an annotated/signed `v1.0.0` tag on the exact verified root commit.
2. Push that tag only.
3. Create a draft GitHub Release.
4. Attach `EVA-Core.zip`, the exact 23 template ZIPs, `SHA256SUMS`, `download-manifest.json` and approved release notes.
5. Keep the Release private as a draft while verifying assets.

## 5. Re-download and publish

Download every draft asset into a clean directory, verify all 24 SHA-256 values, install Core plus T01/T17/T26, and smoke-run one raw-MP4 job and one SRT job. Confirm the exact tag and asset count with the owner. Publish the draft only after a final explicit instruction.

## Rollback boundary

Before publication, delete the draft and remote source-only branch if anything is wrong; `main` remains untouched. After publication, do not silently replace assets under v1.0.0. Withdraw the Release and issue a new version/checksum set with a documented reason.
