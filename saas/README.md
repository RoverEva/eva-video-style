# EVA Video Studio — paid MVP (`feat/mvp-launch`)

```
site/ (Vercel, static) ──► Modal `eva-api` (saas/web/api.py) ──► R2 presigned PUT (browser → private bucket)
   preview ≤10 s, watermarked ─► Modal render_job: prepare (eva-asr, face, plan) → render_chunk ×N (parallel) → finish
   Stripe Checkout $9.99 ─► signed webhook ─► paid HD render ─► delivered (video page + optional email)
   failure ─► Modal retries ×2 per stage ─► one more full attempt ─► automatic full refund      (reconcile cron, 10 min)
```

| Piece | Where |
|---|---|
| Web API: uploads, previews, rate limits, checkout, webhook, status | `saas/web/api.py` (Starlette) |
| Stripe over REST, webhook HMAC verification, live-key guard | `saas/web/stripe_lite.py` |
| R2 storage, lifecycle (uploads 3 d, outputs 7 d, orders 90 d), CORS | `saas/web/store.py` |
| Render worker (unchanged engine; 9:16/16:9, ≤30 s, 10 s preview) | `saas/worker/pipeline.py`, `auto/`, `planner.py` |
| Music: original rights-cleared beds, 1–3 tracks or AI Auto Mix | `saas/music/compose.py`, `saas/worker/musicbed.py` |
| Modal functions (api, render_job, stages, reconcile, cleanup, setup) | `saas/modal_app.py` |
| Website | `site/` |
| CI: worker image render with real eva-asr (no accounts needed) | `.github/workflows/mvp-worker-render.yml` |
| CI: tests → Modal → R2/Stripe setup → Vercel → live browser purchase | `.github/workflows/mvp-deploy.yml` |

Security: credentials only in the GitHub Environment `production` (required reviewer, branch `feat/mvp-launch`) and in
Modal Secrets per function (stages: R2 only; API: + Stripe key + webhook signing secret). The webhook secret goes from
Stripe straight into Modal Secrets (`saas/deploy/stripe_webhook.py`). R2 is private; signed links live 15 minutes; CORS
(API and bucket) allows only the real site origin, verified by CI before tests run.

Limits: MP4/MOV with speech, ≤ 30 s, ≤ 200 MB (size signed into the upload URL). Free previews: 3 per IP per day,
150 per day in total (`EVA_PREVIEWS_PER_IP`, `EVA_PREVIEWS_PER_DAY`). Live Stripe keys are refused unless `EVA_ALLOW_LIVE=1`.

Local: `python3 saas/tests/test_api.py`, `python3 saas/tests/test_planner.py`,
`python3 saas/tests/local_stack.py STATE --fixture-asr "text"` (site :8080, API :8000, fake signed Stripe),
`python3 saas/tests/browser_e2e.py SITE VIDEO OUT` (works against the live site with Stripe test card 4242…).

---

# EVA Video Studio — cloud SaaS (Phase 1: cloud rendering)

Turns the unchanged Eva Video Style engine into an unattended cloud job. Everything new lives in `saas/`;
`engine/`, `template/`, `scripts/` (ASR, captions, music, assembly) are used as-is.

```
upload ─► validate ─► frames+audio ─► eva-asr ─► face calibration ─► planner ─► render chunks (parallel) ─► SFX
       ─► English captions ─► assemble (-16 LUFS) ─► music (license-gated) ─► checks ─► private R2 + signed URL
```

| File | Role |
|---|---|
| `worker/pipeline.py` | Job runner: `prepare` / `render N` / `finish [--preview]` / `run`. Stage markers make retries skip finished work. |
| `worker/planner.py` | Transcript → sections (T17/T20/T01/T09 cut at pauses) + EVA Card System JSON specs timed on eva-asr word times. One optional LLM call picks the ideas; every word is validated against the transcript; deterministic fallback. |
| `worker/auto/` | Data-driven section page: template stages from `template/cards/*`, cards via `K.EC.fromSchema`. Replaces hand-written `scenes.js`. |
| `worker/face.py` | Automatic face calibration (OpenCV) for the presenter window. |
| `worker/storage.py` | Private Cloudflare R2, presigned URLs, lifecycle deletion (uploads 3 days, outputs 14 days). |
| `modal_app.py` | Modal functions: ingest, prepare, render_chunk (fan-out), finish, run_job, daily cleanup. |
| `Dockerfile` | Worker image (Chromium, FFmpeg, fonts, eva-asr CPU, models baked in). Portable to any Docker host. |

## One-time setup (browser only)
1. **Modal**: create an account → Settings → API tokens → add `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` as GitHub repo secrets.
2. **Cloudflare R2**: create a private bucket (e.g. `eva-video-studio`) and an R2 API token (Object Read & Write, that bucket only).
   In Modal → Secrets create `eva-r2` with `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`.
3. Optional: Modal secret `eva-anthropic` (`ANTHROPIC_API_KEY`) and repo variable `EVA_USE_LLM=1` for the AI planner.
4. GitHub → Actions → **saas · deploy to Modal** → Run. Then **saas · cloud end-to-end test** with a link to a new video.

## Local run (any Linux box with the image's tools)
```bash
python3 saas/worker/pipeline.py run talk.mp4 jobs/1 --options opts.json            # full HD
python3 saas/worker/pipeline.py run talk.mp4 jobs/1 --options opts.json --preview  # 15 s watermarked 720p
python3 saas/tests/test_planner.py
```
`opts.json`: `{"templates": ["T17","T20"], "template_mode": "single|multi|auto", "music": "auto|manual|none", "music_track": null, "paid": false}`

## Rules enforced
- Input: MP4/MOV with audio, ≤ 60 s, ≤ 200 MB, landscape (16:9). Rejections are reported, not retried.
- Paid output never uses a background track whose license is not in `ALLOWED_MUSIC_LICENSES` (Open Lo-Fi is UNVERIFIED);
  music problems never block delivery — the video ships with voice + SFX and the report says why.
- The preview renders only the first chunks; the paid final reuses them and renders the rest.
