# Final publication approval checklist

Technical, rights and source-isolation gates are complete locally. Section E remains a hard stop until the owner gives separate publication approval.

## A. Frozen release scope and rights

- [x] Scope is exactly T01–T07, T09–T17, T19–T21, T23–T24, T26–T27.
- [x] T08/T25/T28 are excluded; T18/T22 remain retired and unused.
- [x] T26 is Vintage Story / 复古拼贴故事, 9:16 only; T28 remains Real Estate.
- [x] Core and all 23 release templates are approved as MIT, Free and public-downloadable.
- [x] ShadowByteKS machine-identity provenance was owner-confirmed as authorized Codex work.
- [x] Claude commit provenance was manually reviewed and accepted by the owner.
- [x] Owner aliases, third-party input, employer/contractor/client and contractual restriction confirmations were recorded privately.
- [x] Bundled and non-bundled third-party dependencies are separately documented.

## B. Final rebuilt bytes

- [x] Registry exact access policy validates for all 23 release IDs.
- [x] EVA-Core.zip plus 23 template ZIPs were rebuilt twice deterministically.
- [x] `download-manifest.json` and 24-line `SHA256SUMS` were regenerated.
- [x] 24/24 archives pass inner/outer integrity, source fidelity, secret, private-payload, media/model and license scans.
- [x] 23/23 fresh install/discovery/uninstall checks pass.
- [x] Representative T01/T17/T26 SRT rendering passes all declared tested aspects.
- [x] Representative T01 and T26 raw-MP4/locked-ASR preview/final/QA runs pass.
- [x] Final code/runtime bytes match the accepted technical baseline; only approved metadata/docs/policy/checksum members changed.

## C. Source-only isolation

- [x] Branch is `codex/v1.0-source-only-rc`.
- [x] Branch has one root commit and no parent history.
- [x] Source was reconstructed only from the final verified ZIP payloads.
- [x] No ZIP, Studio/SaaS source, workflow, private media, generated video, model, log or credential is tracked.
- [x] No `.github` workflow is present in this snapshot.
- [x] `SOURCE_MANIFEST.sha256` inventories the complete public source tree.
- [x] Existing repository/default branch remains untouched, preserving repository identity and Stars.

## D. Final local review

- [x] README, installation guide, release notes, clearance summary and third-party notices are present.
- [x] Technical source commit and outer package hashes are recorded.
- [x] T01 contrast review, 30.5-second limit, T17 Inter dependency and ASR/FFmpeg ABI constraints are disclosed.
- [x] Package and rendered evidence remain local/private and ignored.

## E. Publication — separate explicit approval required

- [ ] Owner approves pushing exact branch `codex/v1.0-source-only-rc` and its exact root commit SHA.
- [ ] Pre-push audit confirms GitHub Actions, installed apps/webhooks, Vercel and other integrations will not trigger an unapproved deployment.
- [ ] Owner approves exact tag `v1.0.0` and its target commit.
- [ ] Owner approves creating a draft GitHub Release and attaching the exact checksum-verified 24 ZIPs plus manifests.
- [ ] Remote branch/tree and downloaded assets are reverified against the local approved hashes.
- [ ] Owner approves changing the draft Release to published.

Until every applicable item in section E is checked: **do not push, tag, merge or publish**.
