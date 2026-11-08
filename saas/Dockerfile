# EVA Video Studio worker image: the unchanged eva-video-style engine + eva-asr + Chromium + FFmpeg, CPU only.
# Build context = repository root.   docker build -f saas/Dockerfile -t eva-worker .
# Runs the same on Modal (modal_app.py builds from this file), Hetzner, Fly, Cloud Run or any Docker host.
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright HF_HOME=/models/hf TORCH_HOME=/models/torch \
    EVA_ENGINE=/app FONTSDIR=/usr/share/fonts

# FFmpeg (libx264 + libass + loudnorm), fonts used by the engine and captions (Inter, Noto CJK Black, emoji), Node 22
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg fontconfig fonts-inter fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
      curl ca-certificates git xz-utils \
 && curl -fsSL https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz | tar -xJ -C /usr/local --strip-components=1 \
 && fc-cache -f && rm -rf /var/lib/apt/lists/*

# eva-asr (WhisperX fork) on CPU torch, plus the engine's Python deps
ARG EVA_ASR_REF=main
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu "torch~=2.8.0" "torchaudio~=2.8.0" "torchvision~=0.23.0" \
 && pip install "git+https://github.com/RoverEva/eva-asr@${EVA_ASR_REF}" \
 && pip install numpy pillow opencv-python-headless boto3 requests starlette

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund && npx playwright install --with-deps chromium

COPY engine engine
COPY scripts scripts
COPY saas saas
COPY music-library music-library
COPY qa qa
RUN chmod +x scripts/*.sh && python saas/worker/warm_models.py
# original background beds (rights-cleared, see saas/music/compose.py): composed at build time, nothing downloaded
RUN python saas/music/compose.py saas/music/tracks

ENV EVA_MUSIC_LIBRARY=/app/music-library
# Video QA v1.0 (qa/, from feat/video-qa 377ed15): pre-render + post-render checks, reports saved with each version.
# report = record, never block (initial release). Later: EVA_QA_GATE=block makes a blocking FAIL "qa_failed" (released).
ENV EVA_QA=report EVA_QA_GATE=report

CMD ["python", "saas/worker/pipeline.py", "--help"]
