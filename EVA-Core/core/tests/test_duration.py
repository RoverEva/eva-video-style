#!/usr/bin/env python3
"""Regression: the open-source Core has NO fixed duration cap (a hosted-service launch limit must never leak in).

    python3 EVA-Core/core/tests/test_duration.py            # policy + full-coverage checks (about 1 minute)
    python3 EVA-Core/core/tests/test_duration.py --render   # also renders a 45 s edit end to end (several minutes)
    python3 EVA-Core/core/tests/test_duration.py --render --video talk.mp4   # same with your own >30 s clip

Synthetic media only (ffmpeg testsrc2 + tone, generated SRT). No network, no ASR models, no paid API.
Checks:
  1. a 45 s input is accepted by default; the job covers the whole source (frames, render chunks, captions, plan end)
  2. the plan's sections reach the source ending (not only the beginning)
  3. an explicit host policy (max_seconds=30) rejects the same input before any media work, with a clear message
  4. an environment variable cannot impose a cap on the Core (EVA_MAX_SECONDS is ignored)
  5. --render: final.mp4 lasts the full 45 s, audio and video lengths match, captions include the last cue
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]; ROOT = CORE.parent.parent
sys.path.insert(0, str(CORE))
import pipeline  # noqa: E402

SECONDS = 45.0
OK = True


def check(cond, msg):
    global OK
    print(("PASS " if cond else "FAIL ") + msg); OK = OK and bool(cond)


def stamp(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s - int(s)) * 1000)):03}"


def media(d: Path, video: Path | None):
    if video:
        src = d / "input.mp4"; shutil.copy(video, src)
    else:
        src = d / "input.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=1080x1920:rate=30:duration={SECONDS}",
                        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={SECONDS}",
                        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", src], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout)
    words = "every part of this long talk is edited from the first second to the very end".split()
    cues, t, n = [], 0.5, 1
    while t + 2.4 < dur - .3:   # sentence-sized cues across the WHOLE clip, the last one near the ending
        cues.append(f"{n}\n{stamp(t)} --> {stamp(t + 2.4)}\n" + " ".join(words[(n * 3) % 10:(n * 3) % 10 + 5]) + f" part {n}\n"); t += 3.0; n += 1
    (d / "talk.srt").write_text("\n".join(cues), encoding="utf-8")
    return src, d / "talk.srt", dur, n - 1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--render", action="store_true"); ap.add_argument("--video", type=Path)
    ap.add_argument("--template", default="T03"); a = ap.parse_args()
    with tempfile.TemporaryDirectory(dir=os.environ.get("EVA_TEST_TMP")) as tmp:
        d = Path(tmp); src, srt, dur, ncues = media(d, a.video)
        check(dur > 30, f"test input is {dur:.1f} s (> 30 s)")
        opts = {"aspect": "9:16", "templates": [a.template], "template_mode": "single", "preview_seconds": 10}

        # 3. explicit host policy rejects BEFORE any media work
        try:
            pipeline.prepare(src, d / "policy", ROOT, dict(opts, max_seconds=30), srt); check(False, "max_seconds=30 rejects a 45 s input")
        except pipeline.Reject as e:
            check("exceeds the 30 s limit" in str(e) and not (d / "policy/media").exists(), f"max_seconds=30 rejects before media work: {e}")

        # 4. an environment variable cannot cap the Core; 1. + 2. default accepts and covers everything
        os.environ["EVA_MAX_SECONDS"] = "30"
        job = pipeline.prepare(src, d / "job", ROOT, opts, srt)
        os.environ.pop("EVA_MAX_SECONDS")
        check(job.data["options"]["max_seconds"] is None, "default options carry no duration cap (EVA_MAX_SECONDS ignored)")
        check(abs(job.data["end"] - dur) < .1, f"job covers the source: end {job.data['end']} s vs {dur:.2f} s")
        chunks = job.data["chunks"]
        check(chunks[0][0] == 0 and abs(chunks[-1][1] - job.data["end"]) < 1e-6 and all(abs(x[1] - y[0]) < 1e-9 for x, y in zip(chunks, chunks[1:])),
              f"{len(chunks)} contiguous render chunks reach the ending ({chunks[-1][1]:.2f} s)")
        plan = json.loads((job.d / "plan.json").read_text())
        check(abs(plan["end"] - job.data["end"]) < .01 and abs(plan["sections"][-1]["t1"] - job.data["end"]) < .01,
              f"plan covers 0–{plan['sections'][-1]['t1']:.2f} s in {len(plan['sections'])} section(s)")
        tr = (job.d / "srt/talk.transcript.js").read_text()
        check(f"part {ncues}" in tr, f"transcript keeps the last cue (part {ncues})")

        # 5. full local render
        if a.render:
            rc = pipeline.main(["edit", str(src), str(d / "render"), "--install-root", str(ROOT), "--templates", a.template,
                                "--aspect", "9:16", "--srt", str(srt), "--workers", "2"])
            check(rc == 0, f"edit exit {rc}")
            out = d / "render/out/final.mp4"
            if out.exists():
                p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", out],
                                              capture_output=True, text=True).stdout)
                ds = {s["codec_type"]: float(s["duration"]) for s in p["streams"]}
                check(abs(ds["video"] - dur) < .2, f"final video {ds['video']:.2f} s reaches the source ending ({dur:.2f} s)")
                check(abs(ds["audio"] - ds["video"]) < .2, f"audio {ds['audio']:.2f} s matches video")
                import re
                cap = (d / "render/out/captions.srt").read_text()
                ends = [int(h) * 3600 + int(m) * 60 + int(x) + int(ms) / 1000 for h, m, x, ms in re.findall(r"--> (\d+):(\d+):(\d+),(\d+)", cap)]
                last_src = 0.5 + 3.0 * (ncues - 1) + 2.4
                check(ends and max(ends) >= last_src - .6 and f"{ncues}" in cap.split("-->")[-1],
                      f"delivered captions run to {max(ends or [0]):.2f} s (last source cue ends {last_src:.2f} s) and include its text")
    print("duration tests:", "ok" if OK else "FAILED"); return 0 if OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
