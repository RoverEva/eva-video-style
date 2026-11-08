# Release: accounts, 3 lifetime free previews, credits, My Videos (branch `feat/saas-accounts`)

Status: **built and tested locally; NOT deployed.** Live site unchanged (last approved deploy, tag `release/pre-accounts`).

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
- QA hooks (module `feat/video-qa`): report stored with each version; `EVA_QA_GATE=block` makes a blocking FAIL `qa_failed`
  (released, not charged). Defaults to report-only. QA code is NOT merged here.
- Legacy anonymous video links keep working (old routes untouched).

## Evidence (local: real pipeline renders, real Postgres 16, signed webhooks)
- `test_db.py`: lifetime limit, release on failure/cancel/QA-fail, 20 parallel requests → exactly 3 free slots, 20 parallel
  credit spends never negative, top-up idempotent, HD once per version, ownership, deletion, retention, role privileges.
- `test_accounts_e2e.py`: 32/32 (preview 86 s, cached-ASR version 84 s, HD export 25 s on 2 vCPU).
- `browser_accounts.py`: sign-in → free preview → new version → HD confirm → top-up → back on the same version → export
  → 1080×1920 download; phone width; no page errors.
- QA trial (local branch, not pushed): QA v1.0 report stored with the version: 33 PASS / 1 WARN / 0 FAIL, +28 s.

## Needed before release (Eva)
1. Supabase project (free tier) → GitHub environment `production` secrets: `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
   `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL` (Session pooler connection string).
2. Supabase → Authentication → URL configuration: Site URL `https://eva-video-studio.vercel.app`, redirect URL
   `https://eva-video-studio.vercel.app/**`. Email provider on (magic link). Built-in email is rate-limited (few per hour):
   fine for testing; custom SMTP (e.g. Resend + your domain) before public launch.
3. Decide: merge QA v1.0 (report-only) into the release, or ship without it.

## Release steps (after approval)
1. Fast-forward `feat/mvp-launch` to `feat/saas-accounts` (+ QA if approved) and push → deploy run waits for approval.
2. Approve → tests (incl. DB on Postgres 16) → migration → Modal → Vercel → CORS pin → webhook → R2 checks →
   live account test with throwaway users (deleted afterwards).
3. Eva: one manual Stripe sandbox top-up (card 4242…) → HD export → download.

## Rollback
- Site: Vercel → Deployments → previous production deployment → Promote (instant).
- API/workers: `modal app rollback eva-video-studio` (previous version), or re-deploy tag `release/pre-accounts`.
- Database: nothing to undo (additive; old code ignores it). `saas/db/rollback_001.sql` only if no real data exists.
- Data: no existing accounts or balances (none existed); anonymous orders and their files are untouched.
