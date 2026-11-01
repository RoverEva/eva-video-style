#!/usr/bin/env python3
"""Test fixture for environments without eva-asr (no torch): a synthetic 1920x1080 clip plus a timed English
transcript in exactly the files scripts/asr.py writes (talk.en.srt, talk.transcript.js), and the `asr` stage
marker, so `pipeline.py prepare` skips ASR and runs everything else for real. NOT a speech-recognition test.

usage: make_fixture.py JOB_DIR VIDEO_OUT|- [SECONDS]   (- = transcript only, no FFmpeg needed)
"""
import json, re, subprocess, sys
from pathlib import Path

SCRIPT = ("Hi, I'm Eva, and this is EVA Video Studio. "
          "You upload a raw talking-head video, and the studio edits it for you. "
          "First it listens, then it plans, then it renders every frame. "
          "Captions, motion cards and music are added automatically. "
          "There is no timeline to learn and no software to install. "
          "Pick a style, check the free preview, and download your finished video in minutes. "
          "Less editing, more creating.")


def fmt(t):
    ms = round(t * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main(job, video, seconds=40.0):
    job = Path(job); (job / "srt").mkdir(parents=True, exist_ok=True); (job / "stages").mkdir(exist_ok=True)
    if str(video) != "-": subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate=30:duration={seconds}",
                    "-f", "lavfi", "-i", f"sine=frequency=220:duration={seconds}", "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", video], check=True)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", SCRIPT) if s.strip()]
    nwords = sum(len(s.split()) for s in sents); per = (seconds - 1.0 - .6 * len(sents)) / nwords
    t, segs = .4, []
    for s in sents:
        ws = []
        for w in s.split(): ws.append({"w": w, "start": round(t, 3), "end": round(t + per * .85, 3)}); t += per
        segs.append({"start": ws[0]["start"], "end": ws[-1]["end"], "text": s, "words": ws}); t += .6
    data = {"source": "fixture (not eva-asr)", "language": "en", "segments": segs, "en": []}
    (job / "srt/talk.transcript.js").write_text("window.EV_ASR = " + json.dumps(data) + ";\n")
    srt, i = [], 1
    for s in segs:      # ~42-char cues, like asr.en.json's max_line_width
        cur = []
        for w in s["words"] + [None]:
            if w is None or (cur and len(" ".join(x["w"] for x in cur + [w])) > 42):
                if cur: srt.append(f"{i}\n{fmt(cur[0]['start'])} --> {fmt(cur[-1]['end'])}\n{' '.join(x['w'] for x in cur)}\n"); i += 1
                cur = []
            if w: cur.append(w)
    (job / "srt/talk.en.srt").write_text("\n".join(srt))
    (job / "stages/asr.json").write_text(json.dumps({"ok": True, "fixture": True, "wall_s": 0, "cpu_s": 0}))
    print(f"fixture: {len(segs)} segments, {nwords} words -> {job}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 40.0)
