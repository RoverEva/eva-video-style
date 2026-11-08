# Consolidated release: accounts, credits, My Videos, QA, launch templates (branch `feat/saas-accounts`)

Status: **staging-verified (real Modal runtime, isolated `staging` environment); NOT deployed to production.** Live site
unchanged (last approved deploy = commit `7428bb0` on `feat/mvp-launch`). Production deploy only after Eva's explicit approval.

## 2026-11-08 additions (this consolidation)
- **QA face fixes — 40/40 QA tests under OpenCV Haar (the image's detector; was 37/40) and under scikit-image LBP.**
  Root causes: (1) Haar also fires on large textured patches (her T-shirt) and QA took the *largest* box, so it tracked
  the shirt and a caption on the chest became "caption covers 5 % of the face" — the education 9:16 CAP_FACE FAIL was this
  false positive, not a layout problem; (2) for half-visible faces the tracker preferred ~15 px random-texture matches.
  Fixes: Haar boxes ranked by cascade confidence; per-sample source detections made consistent across the clip;
  minimum face-patch size; in-frame NCC for partly off-frame faces; FACE_STRETCH judged only on fully visible faces;
  QA cache version 3. The live worker's own face locator (median of 9 frames) was not affected.
- **Launch templates T23 Creative Pop, T21 Clean & Minimal, T17 Sci-Fi Network, T02 Electric Blue, T01 Bold Lime**
  selectable (API v2 + site). T23/T21/T02 stage skins added to the worker page with values from their demos; card themes
  as overrides; engine/templates untouched. T20/T09 stay renderable for saved versions. **T19 Footage Intro: not
  selectable yet** — needs an AI presenter cut-out (Robust Video Matting, GPL-3.0 weights, ≈4 fps CPU) and customer
  B-roll for its background swaps; decision pending.
- **Gallery previews**: `saas/tools/template_previews.py` makes a 5 s muted preview (busiest 5 s window) + WebP
  thumbnail from each existing 15 s demo with FFmpeg only (≈1–2 s per template, no re-render); site shows them on the
  template cards (hover/focus plays) and falls back to plain chips. Pending: the six demo MP4s (not in the repo).
- **Measured costs**: `image_qa_check.py` records CPU-seconds per stage, ASR time, output size, planner tokens;
  `saas/tests/cost_report.py` prices them the way Modal bills (physical cores, reserved vs used, memory) + R2 retention
  storage + AI. Staging covers all five renderable launch templates in both aspects.
- Pricing (credits 12–15 preview / 38–52 HD, $9.99 = 100) and retention (30 / 90 days) unchanged. Music stays optional,
  original rights-cleared beds only (default "none").

### Staging evidence (run 42512013230, real Modal runtime, env `staging`, production app list identical before/after)
OpenCV 4.14 + Haar, QA detector `opencv-haar`, worker face `opencv:9/9`, real eva-asr. 8 renders, all delivered:

| clip · aspect · templates | preview (QA) | HD (QA) | preview $ | HD $ |
|---|---|---|---|---|
| education 9:16 · T23+T21 | 720×1280 (warn) | 1080×1920 (warn) | 0.0048 | 0.0019 |
| education 16:9 · T21+T23 | 1280×720 (warn) | 1920×1080 (warn) | 0.0044 | 0.0016 |
| real estate 16:9 · T17+T02 | 1280×720 (pass) | 1920×1080 (pass) | 0.0043 | 0.0017 |
| real estate 9:16 · T01+T02 | 720×1280 (pass) | 1080×1920 (pass) | 0.0055 | 0.0021 |

0 FAIL anywhere; the only findings are SRT_READ warnings (one 0.26 s caption cue in the education clip). Stage times per
10 s preview on Modal: ASR ≈ 30 s (incl. model load), render ≈ 37–54 s, finish ≈ 14–18 s, QA ≈ 3 s pre + 25–32 s post;
HD export ≈ 38–48 s (transcript, plan and full-res chunk reused). QA is ≈ 25 % of preview and ≈ 55 % of HD compute.
Extrapolated 30 s video: preview ≈ $0.006, HD ≈ $0.006, storage ≈ $0.0005 (HD 90 d); AI planner not measured (no key
in staging; ≈ $0.002–0.005 per new plan if enabled). Stripe's fee on a $9.99 top-up (≈ $0.59) remains the largest cost.

### Local evidence (this consolidation)
- QA suite 40/40 (Haar) and 40/40 (LBP); worker image on CI (run 42512013431): QA 40/40, real renders T23+T21 / T17+T02.
- `test_db.py` ok on Postgres 16 **with Supabase roles created** (anon/authenticated denied, service_role allowed).
- `test_accounts_e2e.py` 34/34 (preview 92 s, cached-ASR version 91 s, HD export 56 s on 2 vCPU); `browser_accounts.py`
  full journey, no page errors, phone width OK; planner + API unit tests ok.
- New skins through the real pipeline, 16:9 + 9:16: T23 34 PASS; T21 33 PASS + 1 WARN (RENDER_FREEZE 1.5 s, T21's slow
  motion); T02 34 PASS (16:9) / 33 + 1 WARN (9:16). 0 FAIL.

## What's in it
- Progress page (real 0–100 %, waveform, stages, regenerate) — commit 4c0af1d, never deployed.
- Supabase sign-in (email link) + Postgres (`saas/db/001_accounts_credits.sql`): atomic functions, RLS on, browser roles revoked.
- 3 free previews per account for life; failed / canceled / critical-QA renders don't consume them.
- Credits: $9.99 = 100. Preview 12–15, HD 38–52 (by duration, max 30 s). Costs shown before anything is charged.
- My Videos: projects → versions, thumbnails, templates, favorites, expiry dates, playback, new version, HD export of any
  saved version (rendered from the original upload + that version's saved plan), free re-download, delete.
- Retention (env): previews + source 30 days, HD 90 days; daily job deletes expired files.
- Reuse: transcript/face cached per project (no second ASR), HD reuses the saved plan (no AI call) and full-res chunks.
- Costs per version: compute (Modal), storage estimate (R2), AI calls, timings.
- Video QA v1.0 (cherry-pick of `feat/video-qa` 377ed15 only, no T27/T28 history), **report mode** (`EVA_QA=report`,
  `EVA_QA_GATE=report`): pre-render QA before rendering, post-render QA after; both reports + summaries saved with each
  version (`qa-pre-report.json`, `qa-report.json`); HD export reuses the version's pre-render report. QA never blocks
  delivery; QA errors are recorded, not fatal; normal render failures still release free previews / credits.
  `EVA_QA_GATE=block` (later) → blocking FAIL = `qa_failed`, released, not charged.
- Worker image fix: OpenCV pinned to 4.x. The unpinned install had moved to OpenCV 5.0, which ships no Haar face cascade,
  so the **live** worker's face locator silently used a default face position. Build now fails if the cascade can't load.
- Legacy anonymous video links keep working (old routes untouched).

## Evidence (local: real pipeline renders, real Postgres 16, signed webhooks)
- `test_db.py`: lifetime limit, release on failure/cancel/QA-fail, 20 parallel requests → exactly 3 free slots, 20 parallel
  credit spends never negative, top-up idempotent, HD once per version, ownership, deletion, retention, role privileges.
- `test_accounts_e2e.py`: 32/32 (preview 86 s, cached-ASR version 84 s, HD export 25 s on 2 vCPU).
- `browser_accounts.py`: sign-in → free preview → new version → HD confirm → top-up → back on the same version → export
  → 1080×1920 download; phone width; no page errors.
- `test_accounts_e2e.py` with QA: 34/34 (preview, regenerate, HD export; pre/post reports saved; failures refunded).
- Worker image on CI (`qa-image-verify.yml`, run 42450195269, no credentials): OpenCV 4.14 + Haar OK, QA detector
  `opencv-haar`, worker face locator `opencv:9/9`, real eva-asr. Real renders, preview + HD export each:
  - real estate 16:9: delivered 1280×720 / 1920×1080; QA pre 24 PASS, post 36 PASS, 0 WARN, 0 FAIL.
  - education 9:16: delivered 720×1280 / 1080×1920; QA post 34 PASS / 1 WARN / 1 FAIL — CAP_FACE "caption covers 5% of
    the presenter's face" (real layout finding, delivered in report mode); FACE_VISIBLE 23 % and SRT_READ 0.26 s cue warnings.
  - QA time per render ≈ 2 s pre + 22–26 s post.
- (superseded 2026-11-08: now 40/40) QA's own tests in the image: 37/40. 3 face tests fail with the OpenCV Haar detector (v1.0 was verified with the
  scikit-image fallback): `test_good_9x16_full_context_passes`, `test_t26_moved_right_and_enlarged_fails`,
  `test_face_not_found_is_unverified_not_pass` → for the QA session; not blocking in report mode.
- **Real Modal runtime** (`staging-modal-qa.yml`, run 42510121699): isolated Modal environment `staging` (created by the
  run), ephemeral app `eva-qa-check` (no secrets/volumes/endpoints; stopped after each run). Staging token valid.
  Production app `eva-video-studio` (env `main`, ap-cvYzf2p632HFomn3ixi2qu, deployed 2026-11-06) identical before/after.
  Same results as the CI image: OpenCV 4.14 + Haar, QA detector opencv-haar, worker face opencv:9/9, real eva-asr;
  real estate 16:9 preview + HD all PASS (24 pre / 36 post); education 9:16 preview + HD delivered, QA FAIL CAP_FACE 5 %
  (report mode), FACE_VISIBLE 27 % + SRT_READ warnings. Per render on Modal (3 CPU): ≈128 s preview incl. ≈30 s QA,
  ≈40 s HD export; image build 150 s (first run only).
## Needed before release (Eva)
1. Supabase project (free tier) → GitHub environment `production` secrets: `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
   `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL` (Session pooler connection string).
2. Supabase → Authentication → URL configuration: Site URL `https://eva-video-studio.vercel.app`, redirect URL
   `https://eva-video-studio.vercel.app/**`. Email provider on (magic link). Built-in email is rate-limited (few per hour):
   fine for testing; custom SMTP (e.g. Resend + your domain) before public launch.
3. ~~Staging Modal check~~ done. ~~3 QA face tests~~ fixed (40/40).
4. The six 15 s demo MP4s (T23, T21, T17, T19, T02, T01) → `template_previews.py` → `site/demos/templates/`.
5. T19 decision: ship later with matte + optional B-roll upload, or keep as gallery-only for launch.
6. Optional: `ANTHROPIC_API_KEY` (Modal secret `eva-anthropic`, `EVA_USE_LLM=1`) for better card text.

## Release steps (after approval)
1. Fast-forward `feat/mvp-launch` to `feat/saas-accounts` and push → deploy run waits for approval.
2. Approve → tests (incl. DB on Postgres 16) → migration → Modal → Vercel → CORS pin → webhook → R2 checks →
   live account test with throwaway users (deleted afterwards).
3. Eva: one manual Stripe sandbox top-up (card 4242…) → HD export → download.

## Rollback
- Site: Vercel → Deployments → previous production deployment → Promote (instant).
- API/workers: `modal app rollback eva-video-studio` (previous version), or re-deploy commit `7428bb0` (reset `feat/mvp-launch` to it and approve the deploy).
- Database: nothing to undo (additive; old code ignores it). `saas/db/rollback_001.sql` only if no real data exists.
- Data: no existing accounts or balances (none existed); anonymous orders and their files are untouched.
