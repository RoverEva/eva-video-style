# Release: accounts, 3 lifetime free previews, credits, My Videos (branch `feat/saas-accounts`)

Status: **built and tested locally; NOT deployed.** Live site unchanged (last approved deploy = commit `7428bb0` on `feat/mvp-launch`).

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
- QA's own tests in the image: 37/40. 3 face tests fail with the OpenCV Haar detector (v1.0 was verified with the
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
3. ~~Staging Modal check~~ done. 4. Whether the 3 QA face tests must be fixed by the QA session before release (report mode either way).

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
