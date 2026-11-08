#!/usr/bin/env python3
"""Template Gallery assets from the EXISTING approved 15-second demos — FFmpeg only, nothing is re-rendered and the
originals are only read.

Per demo (16:9 or 9:16):
  <id>_<ar>_5s.mp4     the best-animated 5 s: the window with the most visual change (mean frame difference at 10 fps,
                       first 0.5 s fade-in skipped), muted, H.264 faststart, 640x360 / 360x640
  <id>_<ar>.webp       thumbnail: the frame inside that window with the most detail that is NOT mid-transition
                       (low difference to its neighbours), 640x360 / 360x640, WebP q80
  <id>_<ar>_15s.mp4    optional full preview, web-optimised (960x540 / 540x960, CRF 26; audio kept if present, 96 kb/s)

usage: template_previews.py OUT_DIR ID:AR=/path/demo.mp4 [...]      (AR = 169 | 916)
writes OUT_DIR/<ID>/..., OUT_DIR/gallery_build.json (window, thumb time, sizes, sha256 of source + outputs)
"""
import hashlib, json, subprocess, sys
from pathlib import Path

import numpy as np

SIZES = {"169": {"small": (640, 360), "full": (960, 540)}, "916": {"small": (360, 640), "full": (540, 960)}}


def ff(*a): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *map(str, a)], check=True)


def probe(p):
    r = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                                   "-of", "json", str(p)], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in r["streams"] if s["codec_type"] == "video")
    return float(r["format"]["duration"]), (v["width"], v["height"]), any(s["codec_type"] == "audio" for s in r["streams"])


def frames(p, fps=10, w=96):
    """grayscale frames at `fps`, width w (for motion analysis only)"""
    d, (W, H), _ = probe(p); h = int(round(w * H / W / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def choose(p, win=5.0, fps=10, skip=0.5):
    f = frames(p, fps); diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))          # motion between consecutive samples
    n = int(win * fps); best, s0 = -1.0, 0
    for s in range(int(skip * fps), max(int(skip * fps) + 1, len(diff) - n + 1)):
        v = float(diff[s:s + n].sum())
        if v > best: best, s0 = v, s
    # thumbnail: most content (edge density at 192 px — thin serif type and cards count, flat backgrounds don't) and
    # still (low change to its neighbours: not a cut / whip / fade in progress)
    g = frames(p, fps, 192); edge = np.abs(np.diff(g, axis=1)).mean(axis=(1, 2)) + np.abs(np.diff(g, axis=2)).mean(axis=(1, 2))
    idx = range(s0 + 3, min(len(f) - 2, s0 + n - 3))
    def score(i): return float(edge[i]) - 1.5 * float(diff[max(0, i - 1)] + diff[min(len(diff) - 1, i)])
    ti = max(idx, key=score) if len(idx) else s0
    return s0 / fps, ti / fps, best / n


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(out, tid, ar, src):
    d = Path(out) / tid; d.mkdir(parents=True, exist_ok=True); base = d / f"{tid.lower()}_{ar}"
    dur, size, audio = probe(src); sm, full = SIZES[ar]["small"], SIZES[ar]["full"]
    t0, tt, motion = choose(src)
    fit = lambda wh: f"scale={wh[0]}:{wh[1]}:force_original_aspect_ratio=increase,crop={wh[0]}:{wh[1]},setsar=1"
    ff("-ss", f"{t0:.2f}", "-i", src, "-t", "5", "-an", "-vf", fit(sm) + ",fps=30", "-c:v", "libx264", "-preset", "slow", "-crf", "27",
       "-pix_fmt", "yuv420p", "-movflags", "+faststart", f"{base}_5s.mp4")
    ff("-ss", f"{tt:.2f}", "-i", src, "-frames:v", "1", "-vf", fit(sm), "-c:v", "libwebp", "-quality", "80", "-compression_level", "6", f"{base}.webp")
    ff("-i", src, "-vf", fit(full), "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
       *(["-c:a", "aac", "-b:a", "96k"] if audio else ["-an"]), "-movflags", "+faststart", f"{base}_15s.mp4")
    files = {k: Path(f"{base}{suf}") for k, suf in (("thumb", ".webp"), ("clip5", "_5s.mp4"), ("full15", "_15s.mp4"))}
    rec = {"template_id": tid, "aspect": {"169": "16:9", "916": "9:16"}[ar], "source": Path(src).name, "source_sha256": sha(src),
           "source_duration_s": round(dur, 2), "window_s": [round(t0, 2), round(t0 + 5, 2)], "thumb_t_s": round(tt, 2),
           "motion": round(motion, 2), "audio_in_full": audio,
           "files": {k: {"name": f"{tid}/{p.name}", "bytes": p.stat().st_size, "sha256": sha(p)} for k, p in files.items()}}
    print(tid, rec["aspect"], "window", rec["window_s"], "thumb", tt, {k: v["bytes"] for k, v in rec["files"].items()})
    return rec


def main(out, specs):
    recs = []
    for s in specs:
        key, src = s.split("=", 1); tid, ar = key.split(":")
        recs.append(build(out, tid, ar, src))
    Path(out, "gallery_build.json").write_text(json.dumps(recs, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
