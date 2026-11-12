"""EVA Video Studio (hosted SaaS) launch policy — NOT a limit of the open-source EVA Video Style engine.

The shared worker pipeline (saas/worker/pipeline.py, like EVA Core) processes the complete input with no fixed duration
cap. The hosted Studio applies its launch limits here, explicitly, at its own boundary:
  - API (api_v2 / api): declared duration and size checked before a project is created (user-facing message)
  - worker jobs started by modal_app: `worker_limits()` is added to every job's options, so the worker re-checks the
    ACTUAL media duration (ffprobe) before any transcription, planning or rendering; an over-limit job is rejected and
    its credit / free-preview reservation released. Nothing is ever cropped, sped up or summarised.
Change the launch limit with EVA_STUDIO_MAX_SECONDS (pricing in api_v2 is unchanged by this module)."""
import os

MAX_SECONDS = float(os.environ.get("EVA_STUDIO_MAX_SECONDS", "30"))   # launch limit shown to users
TOLERANCE_S = 0.5                                                     # container rounding (a "30 s" phone clip is 30.0x s)
MAX_BYTES = 200 * 1024 * 1024
PREVIEW_SECONDS = int(os.environ.get("EVA_PREVIEW_SECONDS", "30"))   # full-length watermarked 720p preview (≤ the limit)


def too_long(seconds):
    return seconds is not None and float(seconds) > MAX_SECONDS + TOLERANCE_S


def message(seconds):
    return f"This video is {round(float(seconds))} seconds long. The limit is {MAX_SECONDS:g} seconds."   # wording matched by site/i18n.js


def worker_limits():
    """Options the Studio adds to every worker job (the worker itself has no default cap)."""
    return {"max_seconds": MAX_SECONDS + TOLERANCE_S, "max_bytes": MAX_BYTES}
