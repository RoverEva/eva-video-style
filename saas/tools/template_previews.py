#!/usr/bin/env python3
"""Template gallery assets from the EXISTING 15-second AI Eva demos (no re-rendering).

For each demo MP4: a 5-second muted 640x360 H.264 preview (the 5 s window with the most visual change, so it shows the
template's motion, not a static intro) and a 640x360 WebP thumbnail from the middle of that window. Pure FFmpeg stream
work: ~1-2 s per template on one CPU.

usage: template_previews.py OUT_DIR T23=/path/T23.mp4 T21=/path/T21.mp4 ...
writes OUT_DIR/<t>_5s.mp4, OUT_DIR/<t>.webp, OUT_DIR/templates.json (sizes, chosen window)
"""
import json, re, subprocess, sys
from pathlib import Path


def ff(*a): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *map(str, a)], check=True)


def duration(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout)


def busiest_window(p, win=5.0):
    """start of the 5 s window with the most scene change (ffmpeg scene score, sampled at 5 fps)"""
    r = subprocess.run(["ffmpeg", "-i", str(p), "-vf", "fps=5,scale=320:-2,select='gte(scene,0)',metadata=print:key=lavfi.scene_score", "-f", "null", "-"],
                       capture_output=True, text=True)
    pts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]; sc = [float(x) for x in re.findall(r"scene_score=([\d.]+)", r.stderr)]
    d = duration(p)
    if not sc or d <= win: return 0.0
    best, t0 = -1, 0.0
    for s in [x * .5 for x in range(int((d - win) / .5) + 1)]:
        v = sum(c for t, c in zip(pts, sc) if s <= t < s + win)
        if v > best: best, t0 = v, s
    return t0


def main(out, pairs):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); meta = {}
    for pr in pairs:
        tid, src = pr.split("=", 1); lc = tid.lower(); src = Path(src)
        t0 = busiest_window(src)
        ff("-ss", f"{t0:.2f}", "-i", src, "-t", "5", "-an", "-vf", "scale=640:360:force_original_aspect_ratio=increase,crop=640:360,fps=30",
           "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out / f"{lc}_5s.mp4")
        ff("-ss", f"{t0 + 2.5:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=640:360:force_original_aspect_ratio=increase,crop=640:360",
           "-c:v", "libwebp", "-quality", "78", out / f"{lc}.webp")
        meta[tid] = {"source": src.name, "window_s": [t0, t0 + 5], "preview_bytes": (out / f"{lc}_5s.mp4").stat().st_size, "thumb_bytes": (out / f"{lc}.webp").stat().st_size}
        print(tid, meta[tid])
    (out / "templates.json").write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
