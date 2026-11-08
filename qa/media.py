"""FFmpeg/ffprobe helpers: probing, frame access by frame number, one full decode pass (errors, black, freeze, loudness)."""
import json, os, re, subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")


def probe(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(f"ffprobe cannot read {path}: {r.stderr.strip()[:200]}")
    d = json.loads(r.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = d.get("format", {})
    out = {"path": str(path), "format": fmt.get("format_name", ""), "duration": float(fmt.get("duration") or 0), "bytes": int(fmt.get("size") or 0),
           "bit_rate": int(fmt.get("bit_rate") or 0), "video": None, "audio": None}
    if v:
        w, h = int(v["width"]), int(v["height"])
        rot = 0
        for sd in v.get("side_data_list") or []:
            if "rotation" in sd: rot = int(float(sd["rotation"]))
        if abs(rot) in (90, 270): w, h = h, w
        rate = lambda s: float(Fraction(s)) if s and s != "0/0" else 0.0
        out["video"] = {"codec": v.get("codec_name"), "width": w, "height": h, "rotation": rot, "pix_fmt": v.get("pix_fmt"),
                        "sar": v.get("sample_aspect_ratio", "1:1"), "dar": v.get("display_aspect_ratio"),
                        "fps": rate(v.get("r_frame_rate")), "avg_fps": rate(v.get("avg_frame_rate")),
                        "duration": float(v.get("duration") or out["duration"]), "nb_frames": int(v["nb_frames"]) if str(v.get("nb_frames", "")).isdigit() else None,
                        "bit_rate": int(v.get("bit_rate") or 0)}
    if a:
        out["audio"] = {"codec": a.get("codec_name"), "channels": a.get("channels"), "sample_rate": int(a.get("sample_rate") or 0),
                        "duration": float(a.get("duration") or out["duration"])}
    return out


def read_frames(path, frame_numbers, width=None, gray=False, fps=None):
    """decode the given frame numbers (0-based, sorted or not) in ONE pass. Returns {n: HxWx3 BGR uint8 (or HxW gray)}.
    fps: resample to this constant rate first (frame n = time n/fps), as scripts/extract_frames.sh does; needed for
    variable-frame-rate phone uploads, where frame numbers and times do not line up."""
    want = sorted(set(int(n) for n in frame_numbers if n >= 0))
    if not want: return {}
    p = probe(path)["video"]; W, H = p["width"], p["height"]
    if width and width < W: H = int(round(H * width / W / 2) * 2); W = int(width)
    sel = "+".join(f"eq(n\\,{n})" for n in want)
    vf = (f"fps={fps}," if fps else "") + f"select='{sel}'" + (f",scale={W}:{H}:flags=area" if (W, H) != (p["width"], p["height"]) else "")
    pix, ch = ("gray", 1) if gray else ("bgr24", 3)
    # write the select expression to a script file: a long expression would overflow the command line
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(f"[0:v]{vf}[o]"); script = f.name
    try:
        r = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-filter_complex_script", script, "-map", "[o]", "-vsync", "0",
                            "-f", "rawvideo", "-pix_fmt", pix, "-"], capture_output=True)
    finally:
        os.unlink(script)
    sz = W * H * ch; buf = r.stdout; got = len(buf) // sz
    frames = {}
    for i, n in enumerate(want[:got]):
        a = np.frombuffer(buf[i * sz:(i + 1) * sz], np.uint8)
        frames[n] = a.reshape(H, W) if gray else a.reshape(H, W, 3)
    return frames


class Source:
    """presenter source footage: a video file or a 30 fps JPG folder (f_00000.jpg, scripts/extract_frames.sh)"""
    def __init__(self, path, offset_s=0.0, fps=30):
        self.path, self.offset, self.fps = Path(path), float(offset_s or 0), fps
        self.is_dir = self.path.is_dir()
        if self.is_dir:
            fs = sorted(self.path.glob("f_*.jpg")); self.count = len(fs)
            import cv2
            im = cv2.imread(str(fs[0])) if fs else None
            self.size = (im.shape[1], im.shape[0]) if im is not None else (0, 0)
        else:
            pr = probe(self.path)["video"]; self.size = (pr["width"], pr["height"])
            self.count = int(round(pr["duration"] * fps))   # read through an fps filter: constant rate, like extract_frames.sh

    def frames_at(self, times):
        """{t: BGR frame} for output times t (source time = t + offset)"""
        import cv2
        if self.is_dir:
            out = {}
            for t in times:
                n = int(round((t + self.offset) * self.fps)); f = self.path / f"f_{max(0, min(self.count - 1, n)):05d}.jpg"
                im = cv2.imread(str(f)) if f.exists() else None
                if im is not None: out[t] = im
            return out
        idx = {t: min(self.count - 1, int(round((t + self.offset) * self.fps))) for t in times}
        fr = read_frames(self.path, idx.values(), fps=self.fps)
        return {t: fr[n] for t, n in idx.items() if n in fr}


def decode_pass(path, black_pix_th=0.10, black_min_s=0.1, freeze_noise=0.003, freeze_min_s=1.0, audio=True):
    """one full decode: decoder errors, black spans, frozen spans, decoded frame count, loudness (EBU R128)."""
    vf = f"blackdetect=d={black_min_s}:pix_th={black_pix_th},freezedetect=n={freeze_noise}:d={freeze_min_s}"
    cmd = [FFMPEG, "-nostats", "-v", "info", "-i", str(path), "-map", "0:v:0", "-vf", vf, "-f", "null", "-"]
    if audio: cmd = cmd[:-3] + ["-map", "0:a:0?", "-af", "ebur128=peak=true", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    log = r.stderr
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", log)]
    fs = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    fe = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
    freezes = [(a, fe[i] if i < len(fe) else None) for i, a in enumerate(fs)]
    frames = re.findall(r"frame=\s*(\d+)", log)
    errors = [l for l in log.splitlines() if re.search(r"(error|corrupt|invalid|non-existing PPS|concealing|missing)", l, re.I)
              and not l.lstrip().startswith(("Stream", "Input", "Output", "Metadata"))]
    lufs = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", log, re.M)
    peak = re.findall(r"^\s+Peak:\s+(-?[\d.inf]+) dBFS", log, re.M)
    return {"returncode": r.returncode, "errors": errors[:20], "blacks": blacks, "freezes": freezes,
            "frames": int(frames[-1]) if frames else None, "lufs": float(lufs[-1]) if lufs else None,
            "true_peak": float(peak[-1]) if peak and peak[-1] not in ("-inf", "inf") else None}


def audio_pcm(path, rate=16000):
    """mono float32 PCM of the first audio stream (None if there is none)"""
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"], capture_output=True)
    if r.returncode or not r.stdout: return None
    return np.frombuffer(r.stdout, np.float32)


def render_ass_alpha(ass, size, frame_numbers, fps=30, fontsdir=None):
    """render ONLY the captions (.ass) with libass on a transparent canvas: {n: HxW uint8 alpha mask}.
    Exact pixels of the burned subtitles (same renderer as scripts/assemble.sh), no OCR."""
    want = sorted(set(int(n) for n in frame_numbers if n >= 0))
    if not want: return {}
    W, H = size; dur = (want[-1] + 2) / fps
    fontsdir = fontsdir or os.environ.get("FONTSDIR", "/usr/share/fonts")
    esc = lambda p: str(p).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    sel = "+".join(f"eq(n\\,{n})" for n in want)
    graph = (f"color=c=black@0.0:s={W}x{H}:r={fps}:d={dur:.3f},format=rgba,ass=filename='{esc(ass)}':fontsdir='{esc(fontsdir)}':alpha=1,"
             f"select='{sel}',alphaextract[o]")
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(graph); script = f.name
    try:
        r = subprocess.run([FFMPEG, "-v", "error", "-filter_complex_script", script, "-map", "[o]", "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                           capture_output=True)
    finally:
        os.unlink(script)
    if r.returncode: raise RuntimeError("libass render failed: " + r.stderr.decode(errors="replace")[-300:])
    sz = W * H; buf = r.stdout
    return {n: np.frombuffer(buf[i * sz:(i + 1) * sz], np.uint8).reshape(H, W) for i, n in enumerate(want[:len(buf) // sz])}

