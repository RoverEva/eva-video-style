#!/usr/bin/env python3
"""Image build step: download the eva-asr models used by saas/config/asr.en.json into the image, so cloud jobs
never wait for (or fail on) a Hugging Face download. Same calls scripts/asr.py makes."""
import json, sys
from pathlib import Path

cfg = json.loads((Path(__file__).resolve().parent.parent / "config/asr.en.json").read_text())
import whisperx
whisperx.load_model(cfg["model"], device="cpu", compute_type=cfg["compute_type"], language=cfg["language"], vad_method=cfg["vad_method"])
whisperx.load_align_model(cfg["language"], "cpu")
print("models cached:", cfg["model"], "+ align", cfg["language"]); sys.exit(0)
