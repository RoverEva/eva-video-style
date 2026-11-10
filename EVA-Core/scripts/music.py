#!/usr/bin/env python3
"""Eva Video Style · optional background music + Kenney jingles (off by default: background_music = none).

  music.py import  --lofi DIR --kenney DIR [--copy]          link a downloaded library into music-library/
  music.py analyze [--limit N] [--only a.mp3,b.ogg] [--force]  analyse once, cache in music-library/catalog.json
  music.py plan    VIDEO SRT OUT_DIR [--config c.json] [--cues all_cues.json] [--script talk.txt]
                   [--storyboard sb.json] [--refs DIR] [--mode auto|manual|none]  pick + trim music, write OUT_DIR/music_plan.{json,md}
  music.py show    OUT_DIR/music_plan.json                   print the plan
  music.py preview OUT_DIR/music_plan.json                   audio-only preview (no video work): music_preview.m4a
  music.py apply   OUT_DIR/music_plan.json OUT.mp4 [--video V]  final MP4: video stream copied, audio remixed

Needs FFmpeg/ffprobe and numpy (both already required by eva-video-style). Never overwrites existing outputs.
"""
import argparse, hashlib, itertools, json, os, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIB = Path(os.environ.get("EVA_MUSIC_LIBRARY", ROOT / "music-library"))
AUDIO_EXT = {".mp3", ".ogg", ".wav", ".flac", ".m4a", ".aac", ".opus"}
CATALOG_VERSION = 1
SR_AN = 22050            # analysis sample rate
SR = 48000               # mix sample rate (matches assemble.sh)
DEFAULTS = {
    "background_music": "none",   # auto | manual | none
    "category": "auto",           # auto | tech | business | product | tutorial | general
    "manual": {"file": None, "start": None},
    "jingles": True, "max_jingles": 3,
    "duck_db": -21.0,             # music level under speech, relative to the voice (dB)
    "gap_db": -14.0,              # music level in pauses, relative to the voice (dB)
    "jingle_db": -9.0,            # jingle level relative to the voice (dB)
    "fade_in": 1.5, "fade_out": 2.5,
    "visual_tags": [],
}
SOURCES = {  # library folder -> provenance. Audio is never committed (see .gitignore).
    "background/open-lofi": {"source": "Open Lo-Fi", "license": "UNVERIFIED",
                             "note": "No license file shipped with the download; files are tagged 'made with suno'. "
                                     "Check the Open Lo-Fi terms before publishing; do not redistribute."},
    "jingles/kenney": {"source": "Kenney Music Jingles (kenney.nl)", "license": "CC0-1.0",
                       "note": "Public domain (CC0). Credit to Kenney appreciated, not required."},
}


class MusicError(Exception):
    pass


# ───────────────────────────── audio io ─────────────────────────────
def need(tool):
    if not shutil.which(tool):
        raise MusicError(f"{tool} not found. Install FFmpeg (brew install ffmpeg).")


def decode(path, sr, channels=1, start=0.0, dur=None):
    need("ffmpeg")
    cmd = ["ffmpeg", "-v", "error", "-nostdin"]
    if start: cmd += ["-ss", f"{start:.4f}"]
    cmd += ["-i", str(path)]
    if dur: cmd += ["-t", f"{dur:.4f}"]
    cmd += ["-vn", "-ac", str(channels), "-ar", str(sr), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode or not p.stdout:
        raise MusicError(f"cannot decode {path}: {p.stderr.decode(errors='replace').strip()[:300] or 'no audio stream'}")
    x = np.frombuffer(p.stdout, np.float32)
    return x.reshape(-1, channels).copy() if channels > 1 else x.copy()


def probe_duration(path):
    need("ffprobe")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        raise MusicError(f"cannot read duration of {path}: {p.stderr.strip()[:200]}")


def probe_frames(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets,r_frame_rate", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        s = json.loads(p.stdout)["streams"][0]; n, d = s["r_frame_rate"].split("/")
        return int(s["nb_read_packets"]), float(n) / float(d)
    except Exception:
        return None, None


def stream_times(path):
    """(video duration, audio duration, audio start) from the streams themselves (container length includes AAC padding)."""
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,start_time", "-of", "json", str(path)],
                       capture_output=True, text=True)
    st = {s["codec_type"]: s for s in json.loads(p.stdout or "{}").get("streams", []) if s.get("codec_type") in ("video", "audio")}
    f = lambda k, f2, d=None: float(st.get(k, {}).get(f2, d)) if st.get(k, {}).get(f2) not in (None, "N/A") else d
    return f("video", "duration"), f("audio", "duration"), f("audio", "start_time", 0.0)


def write_wav(path, x, sr=SR):
    import wave
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = x[:, None]
    w = wave.open(str(path), "w"); w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()); w.close()


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


# ───────────────────────────── analysis ─────────────────────────────
def onset_envelope(x, sr=SR_AN, hop=512, n=2048):
    if len(x) < n: x = np.pad(x, (0, n - len(x)))
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n).astype(np.float32)
    mag = np.log1p(10 * np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    flux = np.concatenate([[0], flux]); flux -= np.convolve(flux, np.ones(16) / 16, "same")  # remove slow trend
    return np.maximum(flux, 0), sr / hop


def tempo_and_beats(x, sr=SR_AN):
    """BPM by autocorrelation of the spectral-flux onset envelope (prior centred on 90 BPM, lo-fi range),
    then the beat phase and downbeat (beat 1 of 4) with the strongest onsets."""
    env, fps = onset_envelope(x, sr)
    if env.max() <= 0 or len(env) < 4 * fps * 60 / 55: return 0.0, [], []   # silent or too short (< ~4 slow beats)
    e = (env - env.mean()) / (env.std() + 1e-9)
    ac = np.correlate(e, e, "full")[len(e) - 1:]
    lags = np.arange(int(fps * 60 / 180), int(fps * 60 / 55) + 1)
    bpms = 60 * fps / lags
    score = ac[lags] * np.exp(-0.5 * (np.log2(bpms / 90) / 0.6) ** 2)
    lag = lags[int(np.argmax(score))]
    # refine the (integer-lag) period with parabolic interpolation
    if 1 <= lag < len(ac) - 1:
        a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]; d = (a - c) / (2 * (a - 2 * b + c) + 1e-9)
        period = lag + float(np.clip(d, -.5, .5))
    else:
        period = float(lag)
    for k in (8, 4):  # refine on the 8- (or 4-) beat lag: k times finer than one lag step
        L = k * period; w = np.arange(int(round(L)) - 3, int(round(L)) + 4)
        if w[-1] + 1 < len(ac):
            j = int(w[np.argmax(ac[w])])
            a, b, c = ac[j - 1], ac[j], ac[j + 1]; d = (a - c) / (2 * (a - 2 * b + c) + 1e-9)
            period = (j + float(np.clip(d, -.5, .5))) / k
            break
    bpm = 60 * fps / period
    def at(p0, step):
        return env[np.minimum(np.round(np.arange(p0, len(env) - .5, step)).astype(int), len(env) - 1)].sum()
    phases = [at(p, period) for p in range(int(period))]
    ph = int(np.argmax(phases))
    beats = np.arange(ph, len(env), period) / fps
    sums = [at(ph + k * period, 4 * period) for k in range(4)]
    k = int(np.argmax(sums))
    return float(round(bpm, 2)), [round(float(b), 3) for b in beats], [round(float(b), 3) for b in beats[k::4]]


def energy_curve(x, sr=SR_AN):
    """Loudness per second, 0..100 relative to the track's own loud level (95th percentile)."""
    n = max(1, len(x) // sr)
    r = np.array([rms(x[i * sr:(i + 1) * sr]) for i in range(n)])
    d = db(r); ref = np.percentile(d, 95)
    return [int(v) for v in np.clip((d - (ref - 30)) / 30 * 100, 0, 100)]


MOOD_WORDS = {  # filename words -> mood tags (Open Lo-Fi titles are descriptive)
    "night": "midnight night neon dusk evening moon starlight lanterns streetlights headlights terminal static after-midnight overpass rearview",
    "morning": "morning coffee dawn sunrise kettle pages first-light teacup",
    "focus": "pages notes graphite books hardcovers margin fieldnotes stacks keys clicks cursor quiet work desk",
    "tech": "electric neon pixel terminal cursor satellite antenna orbiting space static signal vhs elevator high-rise clicks",
    "space": "space orbit orbiting satellite constellations stars starlight moon polar weightless floating",
    "warm": "warm golden honey sun sunset candle fireplace amber porchlight soft-gold",
    "groove": "groove jam funk roller mirrorball jukebox offbeat basement slow-jam dance",
    "upbeat": "summer lemonade picnic pancakes breezy spring sunny pixel quest roller",
    "dreamy": "dream dreams dreamscape daydream misty mist haze weightless lullaby floating underwater",
    "rain": "rain puddles storm thunder misty",
    "nature": "garden petals leaves moss mountain ridge fields tide sea savanna bamboo dunes",
    "nostalgic": "polaroids vhs cassette record needle turntable jukebox photos dust old",
}
JINGLE_FAMILY = {"8-bit": "8bit", "8bit": "8bit", "hit": "hit", "pizzicato": "pizzicato", "sax": "sax", "steel": "steel"}


def mood_tags(name):
    s = name.lower().replace("_", "-")
    words = set(re.split(r"[-\s.]+", s))
    return sorted({m for m, ws in MOOD_WORDS.items() if any((w in words) if "-" not in w else (w in s) for w in ws.split())})


def analyze_track(path):
    x = decode(path, SR_AN)
    dur = len(x) / SR_AN
    bpm, beats, downbeats = tempo_and_beats(x)
    en = energy_curve(x)
    arr = np.array(en, float)
    med = float(np.median(arr)) if len(arr) else 0
    intro = next((i for i, v in enumerate(en) if v >= .8 * med), 0)
    outro = len(en) - next((i for i, v in enumerate(reversed(en)) if v >= .8 * med), 0)
    bar = 4 * 60 / bpm if bpm else 8
    w = max(1, int(round(8 * bar)))                     # climax = loudest 8-bar window
    if len(arr) > w:
        m = np.convolve(arr, np.ones(w) / w, "valid"); c = int(np.argmax(m)); climax = [c, c + w]
    else:
        climax = [0, len(arr)]
    phrases = [t for t in downbeats[::2] if intro - .5 <= t <= dur - 4]          # every 2 bars inside the body
    level = "calm" if med < 55 else "upbeat" if med > 75 and bpm >= 88 else "medium"
    variance = float(np.std(arr[intro:outro])) if outro > intro else 0.0
    tags = mood_tags(Path(path).stem) + [level] + (["steady"] if variance < 8 else [])
    return {"type": "background", "duration": round(dur, 2), "bpm": bpm, "beat": round(60 / bpm, 4) if bpm else None,
            "first_beat": beats[0] if beats else 0, "downbeats": downbeats, "phrase_starts": phrases[:200],
            "energy": en, "energy_median": round(med, 1), "energy_std": round(variance, 1),
            "intro_end": intro, "outro_start": outro, "climax": climax, "tags": sorted(set(tags)),
            "loudness_db": round(float(db(rms(x))), 2)}


def analyze_jingle(path, family):
    x = decode(path, SR_AN)
    dur = len(x) / SR_AN
    env = np.abs(x); pk = int(np.argmax(env)) / SR_AN
    above = np.where(env > env.max() * .05)[0]
    tail = (len(x) - above[-1]) / SR_AN if len(above) else 0
    if family == "hit" or dur < 1.0:
        roles = ["transition", "highlight"]
    elif dur < 1.8:
        roles = ["highlight", "transition", "opening", "ending"]
    else:
        roles = ["opening", "ending"]
    return {"type": "jingle", "family": family, "duration": round(dur, 3), "peak_at": round(pk, 3),
            "tail": round(tail, 3), "roles": roles, "loudness_db": round(float(db(rms(x))), 2)}


def lib_files():
    out = []
    for sub in SOURCES:
        d = LIB / sub
        if d.is_dir():
            out += sorted(p for p in d.rglob("*") if p.suffix.lower() in AUDIO_EXT and p.is_file())
    return out


def source_of(rel):
    for sub, meta in SOURCES.items():
        if rel.startswith(sub + "/"): return sub, meta
    return None, {"source": "unknown", "license": "UNVERIFIED", "note": ""}


def family_of(rel):
    s = rel.lower()
    return next((v for k, v in JINGLE_FAMILY.items() if k in s), "other")


def load_catalog():
    p = LIB / "catalog.json"
    if p.is_file():
        try:
            c = json.loads(p.read_text())
            if c.get("version") == CATALOG_VERSION: return c
        except json.JSONDecodeError:
            print(f"warning: {p} is corrupt, rebuilding", file=sys.stderr)
    return {"version": CATALOG_VERSION, "tracks": {}}


def cmd_analyze(a):
    files = lib_files()
    if not files:
        raise MusicError(f"no audio under {LIB}/background/open-lofi or {LIB}/jingles/kenney. "
                         f"Run: python3 scripts/music.py import --lofi ~/Downloads/openlofi --kenney ~/Downloads/kenney_music-jingles")
    only = set(filter(None, (a.only or "").split(",")))
    if only: files = [f for f in files if f.name in only]
    if a.limit:  # MVP: N per library, spread across sub-folders (e.g. one jingle per Kenney family)
        picked = []
        for sub in SOURCES:
            groups = {}
            for g in files:
                if str(g.relative_to(LIB)).startswith(sub): groups.setdefault(g.parent, []).append(g)
            rr = [f for row in itertools.zip_longest(*groups.values()) for f in row if f]
            picked += rr[:a.limit]
        files = picked
    cat = load_catalog(); tracks = cat["tracks"]; new = cached = failed = 0
    overrides = {}
    if (LIB / "tags.json").is_file():
        overrides = json.loads((LIB / "tags.json").read_text())
    for f in files:
        rel = str(f.relative_to(LIB)); st = f.stat(); key = f"{st.st_size}:{int(st.st_mtime)}"
        if not a.force and tracks.get(rel, {}).get("key") == key:
            cached += 1
        else:
            sub, meta = source_of(rel)
            try:
                info = analyze_jingle(f, family_of(rel)) if sub == "jingles/kenney" else analyze_track(f)
            except Exception as e:  # one bad file must not stop the library
                e = e if isinstance(e, MusicError) else f"{type(e).__name__}: {e}"
                print(f"  skip {rel}: {e}", file=sys.stderr); failed += 1; continue
            info.update({"key": key, "source": meta["source"], "license": meta["license"]})
            tracks[rel] = info; new += 1
            print(f"  analysed {rel}: " + (f"{info['bpm']} BPM, {info['duration']} s, {','.join(info['tags'])}"
                                           if info["type"] == "background" else f"{info['family']} {info['duration']} s {info['roles']}"))
        if rel in overrides:  # manual mood/scene tags always win
            tracks[rel]["tags"] = sorted(set(overrides[rel].get("tags", tracks[rel].get("tags", []))))
            for k in ("scenes", "roles"):
                if k in overrides[rel]: tracks[rel][k] = overrides[rel][k]
    for rel in [r for r in tracks if not (LIB / r).exists()]:
        del tracks[rel]
    cat["licenses"] = SOURCES
    (LIB / "catalog.json").write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")))
    print(f"catalog: {LIB / 'catalog.json'}  ({new} analysed, {cached} cached, {failed} failed, {len(tracks)} total)")
    if failed and not (new or cached): raise MusicError("no file could be analysed")


def cmd_import(a):
    pairs = []
    if a.lofi: pairs += [(Path(a.lofi).expanduser(), LIB / "background/open-lofi", None)]
    if a.kenney: pairs += [(Path(a.kenney).expanduser(), LIB / "jingles/kenney", True)]
    if not pairs: raise MusicError("give --lofi DIR and/or --kenney DIR")
    for src, dst, keep_family in pairs:
        if not src.is_dir(): raise MusicError(f"not a folder: {src}")
        files = sorted(p for p in src.rglob("*") if p.suffix.lower() in AUDIO_EXT and p.stem.lower() != "preview")
        if not files: raise MusicError(f"no audio files in {src}")
        n = 0
        for f in files:
            sub = dst / (family_of(str(f.relative_to(src))) if keep_family else "")
            sub.mkdir(parents=True, exist_ok=True); t = sub / f.name
            if t.exists() or t.is_symlink(): continue
            shutil.copy2(f, t) if a.copy else t.symlink_to(f.resolve()); n += 1
        lic = next(iter(src.glob("[Ll]icen[sc]e*")), None)
        if lic: shutil.copy2(lic, dst / "SOURCE_LICENSE.txt")
        print(f"{'copied' if a.copy else 'linked'} {n} new files into {dst} ({len(files)} in source)")


# ───────────────────────────── video analysis ─────────────────────────────
def parse_srt(path):
    txt = Path(path).read_text(encoding="utf-8-sig")
    cues = []
    for blk in re.split(r"\n\s*\n", txt.strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", blk)
        if not m: continue
        g = [int(v) for v in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(blk[m.end():].strip().splitlines())
        cues.append((a, b, text))
    if not cues: raise MusicError(f"no subtitle cues in {path}")
    return sorted(cues)


CATEGORY_WORDS = {
    "tech": "tech technology software code coding developer api chip model gpu robot app digital 科技 技术 软件 代码 芯片 模型 程序 开发 算力",
    "business": "business market revenue growth strategy company profit sales investor startup data analysis economy brand 商业 市场 营收 增长 战略 公司 利润 销售 投资 创业 分析 经济 品牌 数据",
    "product": "product launch feature design new price buy review unbox showcase version release customer 产品 发布 功能 设计 新品 价格 评测 开箱 展示 版本 上线",
    "tutorial": "how step tutorial learn guide tip prompt workflow click template choose create setup use 教程 步骤 学习 指南 技巧 提示词 工作流 点击 模板 选择 创建 设置 使用 怎么 如何",
}
AI_WORDS = "ai gpt chatgpt claude llm agent automation 人工智能 大模型 智能体 自动化"
TEMPLATE_CATEGORY = {"T13": "tech", "T17": "tech", "T14": "tech", "T10": "product", "T06": "product", "T03": "product",
                     "T21": "business", "T02": "business", "T11": "tutorial", "T08": "tutorial", "T15": "tutorial",
                     "T23": "tutorial", "T24": "product", "T20": "product"}
PROFILES = {  # what each video kind wants from a lo-fi bed
    "tech":     {"bpm": (80, 96),  "tags": {"tech": 3, "night": 2, "space": 2, "focus": 1, "steady": 1}, "energy": "medium",
                 "jingles": ["8bit", "hit"]},
    "business": {"bpm": (70, 86),  "tags": {"focus": 3, "morning": 2, "calm": 2, "steady": 2, "warm": 1}, "energy": "calm",
                 "jingles": ["pizzicato", "hit"]},
    "product":  {"bpm": (86, 102), "tags": {"groove": 3, "upbeat": 3, "warm": 2, "medium": 1}, "energy": "upbeat",
                 "jingles": ["steel", "sax", "hit"]},
    "tutorial": {"bpm": (74, 92),  "tags": {"focus": 3, "steady": 3, "morning": 1, "tech": 1, "medium": 1}, "energy": "medium",
                 "jingles": ["pizzicato", "8bit"]},
    "general":  {"bpm": (72, 95),  "tags": {"steady": 2, "warm": 1, "medium": 1}, "energy": "medium",
                 "jingles": ["pizzicato", "hit"]},
}


def classify(text, storyboard, cfg):
    if cfg.get("category", "auto") in PROFILES: return cfg["category"], {"forced": cfg["category"]}
    t = text.lower(); score = {}
    for k, ws in CATEGORY_WORDS.items():
        score[k] = sum(len(re.findall(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])" if w.isascii() else re.escape(w), t))
                       for w in ws.split())
    ai = sum(len(re.findall(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])" if w.isascii() else re.escape(w), t)) for w in AI_WORDS.split())
    score["tech"] += ai; score["tutorial"] += ai * .5          # "AI tutorial" leans tutorial + tech
    for s in storyboard.get("sections", []):
        c = TEMPLATE_CATEGORY.get(str(s.get("template", "")).upper()[:3])
        if c: score[c] += 2
        if s.get("category") in PROFILES: score[s["category"]] += 3
    best = max(score, key=score.get)
    return (best if score[best] > 0 else "general"), score


def image_stats(folder):
    """Mean brightness / saturation of reference images (0..1), via ffmpeg -> 16x16 RGB."""
    vals = []
    for p in sorted(Path(folder).glob("*"))[:24]:
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}: continue
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", "scale=16:16", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-frames:v", "1", "-"], capture_output=True)
        if r.returncode or len(r.stdout) != 768: continue
        px = np.frombuffer(r.stdout, np.uint8).reshape(-1, 3) / 255
        mx, mn = px.max(1), px.min(1)
        vals.append((float(mx.mean()), float(((mx - mn) / np.maximum(mx, 1e-6)).mean())))
    if not vals: return None
    b, s = np.mean(vals, 0)
    return {"brightness": round(float(b), 3), "saturation": round(float(s), 3), "images": len(vals)}


def load_events(cues_path, storyboard):
    """Storyboard events: existing SFX cues (from render.mjs --cues / merge_cues.py) + storyboard sections."""
    sfx, transitions, highlights = [], [], []
    if cues_path:
        for c in json.loads(Path(cues_path).read_text()):
            kind, t = c[0], float(c[1]); sfx.append(t)
            (highlights if kind in ("impact", "ding", "applause") else transitions if kind in ("whoosh", "riser") else []).append(t)
    for s in storyboard.get("sections", [])[1:]:
        if "start" in s: transitions.append(float(s["start"]))
    for h in storyboard.get("highlights", []):
        highlights.append(float(h["t"] if isinstance(h, dict) else h))
    return sorted(set(sfx)), sorted(set(transitions)), sorted(set(highlights))


# ───────────────────────────── selection ─────────────────────────────
def score_track(info, prof, vdur, pace, visual):
    s = 0.0; why = []
    lo, hi = prof["bpm"]; bpm = info.get("bpm") or 0
    if bpm:  # also accept half/double time
        dist = min(abs(b - min(max(b, lo), hi)) for b in (bpm, bpm / 2, bpm * 2))
        s += 3 * np.exp(-dist / 8); why.append(f"bpm {bpm:.0f}")
    tags = set(info.get("tags", []))
    tag_s = sum(w for t, w in prof["tags"].items() if t in tags); s += tag_s
    if tag_s: why.append("tags " + ",".join(t for t in prof["tags"] if t in tags))
    if prof["energy"] in tags: s += 1.5
    if "rain" in tags or "nostalgic" in tags: s -= .5                    # keep beds neutral behind speech
    s -= info.get("energy_std", 10) / 10                                # steady beds are kinder to the voice
    usable = info["duration"] - info.get("intro_end", 0)
    if usable < vdur + 2: s -= 2 + (vdur - usable) / 30; why.append("short (will loop)")
    if pace > 12 and "upbeat" in tags: s += 1
    if visual:
        if visual["brightness"] > .6 and visual["saturation"] > .45 and tags & {"upbeat", "groove", "warm"}: s += 1
        if visual["brightness"] < .4 and tags & {"night", "tech", "space"}: s += 1
    return round(float(s), 3), why


def choose_start(info, vdur, speech, transitions, highlights, fade_out):
    """Best start offset (on a phrase start) for a vdur-long cut: steady, mid energy, phrase boundaries on cuts."""
    dur, beat = info["duration"], info.get("beat") or .5
    en = np.array(info["energy"], float); bar = 4 * beat
    cands = [t for t in info.get("phrase_starts", []) if t + vdur + fade_out * .5 <= dur] or [float(info.get("intro_end", 0))]
    downs = np.array(info.get("downbeats") or [0.0])
    def e(a, b):
        a, b = int(max(0, a)), int(min(len(en), max(a + 1, b))); return en[a:b] if b > a else np.array([0.0])
    best = None
    for s in cands:
        seg = e(s, s + vdur)
        sc = -np.std(seg) / 10 - abs(np.mean(seg) - 70) / 25            # steady and not too loud or empty
        sc += .5 * (np.mean(e(s, s + 2)) >= .9 * np.mean(e(s - 2, s) if s >= 2 else seg))  # starts on a rise / phrase
        for t in transitions:                                           # cuts land on downbeats / phrase boundaries
            d = np.min(np.abs(downs - (s + t))) if len(downs) else 1
            sc += .6 * np.exp(-(d / .08) ** 2)
            if np.min(np.abs((s + t) - np.array(info.get("phrase_starts") or [-99]))) < .1: sc += .3
        for h in highlights:                                            # highlights meet the track's high-energy part
            c0, c1 = info.get("climax", [0, 0]); sc += .5 * (c0 <= s + h <= c1)
        end = s + vdur
        if len(downs) and np.min(np.abs(downs - end)) < bar / 4: sc += .2
        if best is None or sc > best[0]: best = (sc, s)
    return round(float(best[1]), 3), round(float(best[0]), 3)


def gaps_of(speech, vdur, min_gap):
    g, t = [], 0.0
    for a, b, _ in speech:
        if a - t >= min_gap: g.append((t, a))
        t = max(t, b)
    if vdur - t >= min_gap: g.append((t, vdur))
    return g


def place_jingles(cat, prof, cfg, vdur, speech, sfx, transitions, highlights):
    """Few accents, only in pauses, never on top of an existing SFX cue. Returns (placed, skipped-with-reasons)."""
    placed, skipped = [], []
    if not cfg.get("jingles", True): return placed, ["jingles disabled in config"]
    jin = {r: i for r, i in cat.items() if i["type"] == "jingle"}
    if not jin: return placed, ["no Kenney jingles in catalog"]
    fams = prof["jingles"]
    def pick(role, maxlen):
        used = {j["file"] for j in placed}
        c = [(r in used, fams.index(i["family"]) if i["family"] in fams else 9, abs(i["duration"] - maxlen * .7), r)
             for r, i in jin.items() if role in i.get("roles", []) and i["duration"] <= maxlen + .3]
        return sorted(c)[0][3] if c else None
    def clear(t, ln):
        return all(not (t - .4 < x < t + ln + .1) for x in sfx)
    first, last = speech[0][0], max(b for _, b, _ in speech)
    def add(role, t, maxlen):
        if len(placed) >= cfg.get("max_jingles", 3): skipped.append(f"{role} @{t:.2f}s: max_jingles reached"); return
        r = pick(role, maxlen)
        if not r: skipped.append(f"{role} @{t:.2f}s: no jingle short enough ({maxlen:.1f}s)"); return
        ln = min(jin[r]["duration"], maxlen)
        if not clear(t, ln): skipped.append(f"{role} @{t:.2f}s: existing SFX there"); return
        placed.append({"role": role, "file": r, "at": round(t, 3), "length": round(ln, 3), "family": jin[r]["family"]})
    # opening: only before the first word
    (add("opening", 0.0, first - .1) if first >= .9 else skipped.append(f"opening: speech starts at {first:.2f}s (needs ≥0.9s pause)"))
    # highlights: in a pause right after an emphasised cue / storyboard highlight, ≤1 per 30 s
    pauses = gaps_of(speech, vdur, .45)
    emph = re.compile(r"\d|!|！|key|most important|remember|关键|重点|最重要|记住|一定", re.I)
    hl = sorted(set(highlights) | {b for a, b, t in speech if emph.search(t)})
    last_hl = -99
    for t in hl:
        g = next(((a, b) for a, b in pauses if a - .05 <= t <= b and b < vdur - .5), None)
        if not g: skipped.append(f"highlight @{t:.2f}s: no pause there"); continue
        if t - last_hl < 30: skipped.append(f"highlight @{t:.2f}s: too close to previous accent"); continue
        n = len(placed); add("highlight", g[0] + .05, min(1.2, g[1] - g[0] - .1))
        if len(placed) > n: last_hl = t
    # transitions: storyboard cuts or long pauses, ≤1 per 45 s
    long_pauses = [a for a, b in gaps_of(speech, vdur, 1.2) if a > first and b < vdur - .5]
    last_tr = -99
    for t in sorted(set(transitions) | set(long_pauses)):
        g = next(((a, b) for a, b in pauses if a - .05 <= t <= b), None)
        if not g: continue                                     # cut during speech: silent by design
        if t - last_tr < 45: skipped.append(f"transition @{t:.2f}s: too close to previous accent"); continue
        n = len(placed); add("transition", max(t, g[0]), min(1.0, g[1] - max(t, g[0]) - .05))
        if len(placed) > n: last_tr = t
    # ending: after the last word
    room = vdur - last - .15
    (add("ending", last + .15, room) if room >= .8 else skipped.append(f"ending: only {max(room, 0):.2f}s after the last word (needs ≥0.8s)"))
    return sorted(placed, key=lambda j: j["at"]), skipped


def load_cfg(path):
    cfg = json.loads(json.dumps(DEFAULTS))
    if path:
        user = json.loads(Path(path).read_text())
        for k, v in user.items():
            if k.startswith("_"): continue
            if k not in DEFAULTS: raise MusicError(f"unknown key in {path}: {k}")
            cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg[k], dict) else v
    if cfg["background_music"] not in ("auto", "manual", "none"):
        raise MusicError("background_music must be auto, manual or none")
    return cfg


def cmd_plan(a):
    cfg = load_cfg(a.config); out = Path(a.out_dir)
    if a.mode: cfg["background_music"] = a.mode
    out.mkdir(parents=True, exist_ok=True)
    plan_p = out / "music_plan.json"
    if plan_p.exists() and not a.replan: raise MusicError(f"{plan_p} exists (use --replan to replace it)")
    video = Path(a.video).resolve(); vdur = probe_duration(video)
    speech = parse_srt(a.srt)
    plan = {"mode": cfg["background_music"], "video": str(video), "video_duration": round(vdur, 3), "config": cfg}
    if cfg["background_music"] == "none":
        plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=1)); write_md(plan, out)
        print("background_music = none: no music will be added (set it to auto or manual in the music config)."); return
    storyboard = json.loads(Path(a.storyboard).read_text()) if a.storyboard else {}
    text = " ".join(t for _, _, t in speech) + " " + (Path(a.script).read_text() if a.script else "")
    text += " " + " ".join(cfg.get("visual_tags", []))
    category, cat_scores = classify(text, storyboard, cfg)
    prof = PROFILES[category]
    sfx, transitions, highlights = load_events(a.cues, storyboard)
    visual = image_stats(a.refs) if a.refs else None
    pace = len(transitions) / max(vdur / 60, .25)
    if cfg["background_music"] == "auto" or cfg.get("jingles"):     # analyse new/changed files once (cached)
        if lib_files(): cmd_analyze(argparse.Namespace(only=None, limit=None, force=False))
    catalog = load_catalog()["tracks"]
    bgs = {r: i for r, i in catalog.items() if i["type"] == "background"}
    if cfg["background_music"] == "manual":
        mf = cfg["manual"].get("file")
        if not mf: raise MusicError("background_music = manual needs manual.file (a path, or a name in music-library)")
        rel = next((r for r in bgs if r == mf or Path(r).name == mf), None)
        if rel is None:
            p = Path(mf).expanduser()
            if not p.is_file(): raise MusicError(f"manual music not found: {mf}")
            info = analyze_track(p); rel = str(p.resolve()); info.update(source="manual", license="user-supplied")
        else:
            info = bgs[rel]
        ranked = [(None, rel, ["chosen manually"])]
    else:
        if not bgs: raise MusicError("catalog has no background tracks: run `python3 scripts/music.py analyze` first")
        ranked = sorted(((score_track(i, prof, vdur, pace, visual)[0], r, score_track(i, prof, vdur, pace, visual)[1])
                         for r, i in bgs.items()), key=lambda x: (-x[0], x[1]))
        rel = ranked[0][1]; info = bgs[rel]
    if cfg["background_music"] == "manual" and cfg["manual"].get("start") is not None:
        start, sscore = float(cfg["manual"]["start"]), None
    else:
        start, sscore = choose_start(info, vdur, speech, transitions, highlights, cfg["fade_out"])
    jingles, skipped = place_jingles(catalog, prof, cfg, vdur, speech, sfx, transitions, highlights)
    plan.update({
        "category": category, "category_scores": cat_scores, "visual": visual,
        "background": {"file": rel, "path": str(LIB / rel) if not Path(rel).is_absolute() else rel,
                       "bpm": info.get("bpm"), "start": start, "end": round(start + vdur, 3),
                       "loops": start + vdur > info["duration"], "start_score": sscore,
                       "source": info.get("source"), "license": info.get("license"), "tags": info.get("tags")},
        "alternatives": [{"file": r, "score": s, "why": w} for s, r, w in ranked[1:4]],
        "why": ranked[0][2],
        "levels": {k: cfg[k] for k in ("duck_db", "gap_db", "jingle_db", "fade_in", "fade_out")},
        "jingles": jingles, "jingles_skipped": skipped,
        "events": {"sfx": sfx, "transitions": transitions, "highlights": highlights},
        "srt": str(Path(a.srt).resolve()),
    })
    plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=1)); write_md(plan, out)
    print((out / "music_plan.md").read_text())


def write_md(plan, out):
    L = ["# 配乐方案 · Music plan", "", f"- 视频：`{plan['video']}`（{plan['video_duration']} s）", f"- 模式：**{plan['mode']}**"]
    if plan["mode"] != "none":
        b, lv = plan["background"], plan["levels"]
        L += [f"- 视频类型：**{plan['category']}**", "",
              "## 背景音乐", "", f"- 文件：`{b['file']}`（{b['bpm']} BPM；{', '.join(b['tags'] or [])}）",
              f"- 截取：{b['start']:.2f}s → {b['end']:.2f}s" + ("（曲长不够，交叉淡化循环）" if b["loops"] else ""),
              f"- 使用位置：0.00s → {plan['video_duration']:.2f}s（整条视频一首曲子）",
              f"- 音量：口播时比人声低 {-lv['duck_db']:.0f} dB；停顿时低 {-lv['gap_db']:.0f} dB；淡入 {min(lv['fade_in'], .15 * plan['video_duration']):.2f}s，淡出 {min(lv['fade_out'], .2 * plan['video_duration']):.2f}s",
              f"- 来源 / 许可：{b['source']} / {b['license']}", f"- 选择理由：{'; '.join(plan['why'])}", ""]
        if plan["alternatives"]:
            L += ["备选：", *[f"- `{x['file']}`（score {x['score']}）" for x in plan["alternatives"]], ""]
        L += ["## Kenney 音效", ""]
        L += [f"- {j['at']:.2f}s · {j['role']} · `{j['file']}`（{j['length']:.2f}s，比人声低 {-lv['jingle_db']:.0f} dB）" for j in plan["jingles"]] or ["- 无（宁少勿多）"]
        L += [f"- 未使用：{s}" for s in plan["jingles_skipped"]]
    (out / "music_plan.md").write_text("\n".join(L) + "\n")


def cmd_show(a):
    p = Path(a.plan); md = p.with_suffix(".md")
    if not p.is_file(): raise MusicError(f"no plan at {p}")
    if not md.is_file(): write_md(json.loads(p.read_text()), p.parent)
    print(md.read_text())


# ───────────────────────────── mixing ─────────────────────────────
def smooth_gain(target_db, fps, attack, release):
    """One-pole smoothing in dB: fast going down (duck), slow coming back up (no pumping)."""
    out = np.empty_like(target_db); g = target_db[0]
    ka, kr = 1 - np.exp(-1 / (attack * fps)), 1 - np.exp(-1 / (release * fps))
    for i, t in enumerate(target_db):
        g += (t - g) * (ka if t < g else kr); out[i] = g
    return out


def speech_mask(voice, speech, vdur, fps=100):
    n = int(np.ceil(vdur * fps)); m = np.zeros(n, bool)
    for a, b, _ in speech: m[max(0, int((a - .15) * fps)):min(n, int((b + .15) * fps))] = True
    hop = SR // fps; fr = voice[:n * hop].reshape(-1, hop) if len(voice) >= n * hop else np.pad(voice, (0, n * hop - len(voice))).reshape(-1, hop)
    lv = db(np.sqrt((fr ** 2).mean(1)))
    ref = np.percentile(lv[m], 80) if m.any() else np.percentile(lv, 90)
    m |= lv > ref - 12                                   # also duck for audible speech the SRT missed
    # close short pauses so the music doesn't pump between words
    gap = 0; out = m.copy()
    for i in range(n + 1):
        if i < n and not m[i]: gap += 1; continue
        if 0 < gap < int(.8 * fps) and i - gap > 0 and i < n: out[i - gap:i] = True
        gap = 0
    return out, fps


def load_music_segment(path, start, vdur, info_dur):
    need_len = vdur + .05
    if start + need_len <= info_dur + .01:
        x = decode(path, SR, 2, start, need_len)
    else:  # loop with 2 s crossfade
        x = decode(path, SR, 2, start); full = decode(path, SR, 2); xf = int(2 * SR)
        while len(x) < need_len * SR:
            r = np.linspace(0, 1, xf)[:, None]; x[-xf:] = x[-xf:] * (1 - r) + full[:xf] * r; x = np.concatenate([x, full[xf:]])
    n = int(round(vdur * SR)); return np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]


def build_stem(plan, voice):
    """Background bed (trimmed, ducked, faded) + jingles -> stereo 48 kHz stem. Returns (stem, metrics)."""
    vdur = plan["video_duration"]; lv = plan["levels"]; n = int(round(vdur * SR))
    speech = parse_srt(plan["srt"])
    mask, fps = speech_mask(voice, speech, vdur)
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    vidx = np.repeat(mask, SR // fps)[:n]
    voice_db = float(db(rms(voice[vidx]))) if vidx.any() else float(db(rms(voice)))
    b = plan["background"]
    cat = load_catalog()["tracks"]; dur = cat.get(b["file"], {}).get("duration") or probe_duration(b["path"])
    if not Path(b["path"]).exists(): raise MusicError(f"music file missing: {b['path']}")
    mus = load_music_segment(b["path"], b["start"], vdur, dur)
    mus_db = float(db(rms(mus.mean(1))))
    target = np.where(mask, lv["duck_db"], lv["gap_db"]).astype(float) + voice_db - mus_db
    for j in plan["jingles"]:                             # dip the bed under each accent
        target[int(j["at"] * fps):int((j["at"] + j["length"]) * fps)] -= 5
    g = smooth_gain(target, fps, .12, .7)
    t = np.arange(len(g)) / fps
    fi, fo = min(lv["fade_in"], .15 * vdur), min(lv["fade_out"], .2 * vdur)      # short clips get short fades
    fade = np.minimum(1, np.minimum(t / max(fi, .01), (vdur - t) / max(fo, .01)))
    gain = 10 ** (g / 20) * np.clip(fade, 0, 1) ** 1.5
    gs = np.interp(np.arange(n) / SR, t, gain)
    stem = mus * gs[:, None]
    for j in plan["jingles"]:
        jp = LIB / j["file"]; x = decode(jp, SR, 2)[:int(j["length"] * SR)]
        k = min(len(x), int(.05 * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]          # no clicks at the cut
        jg = 10 ** ((voice_db + lv["jingle_db"] - float(db(rms(x.mean(1))))) / 20)
        i = int(j["at"] * SR); e = min(n, i + len(x)); stem[i:e] += x[:e - i] * jg
    peak = float(np.abs(stem).max()) if len(stem) else 0
    if peak > .89: stem *= .89 / peak                      # never clip the stem
    mono = stem.mean(1); sidx = np.repeat(mask, SR // fps)[:n]
    m_speech = float(db(rms(mono[sidx]))) if sidx.any() else -120
    m_gap = float(db(rms(mono[~sidx]))) if (~sidx).any() else None
    metrics = {"voice_db": round(voice_db, 2), "music_under_speech_db": round(m_speech, 2),
               "speech_to_music_db": round(voice_db - m_speech, 2), "music_in_pauses_db": None if m_gap is None else round(m_gap, 2),
               "stem_peak": round(min(peak, .89), 3), "fade_in_start_gain": round(float(gs[0]), 4), "fade_out_end_gain": round(float(gs[-1]), 4)}
    return stem, metrics


def voice_of(video):
    return decode(video, SR, 1)


def stem_for(plan_p, plan, video):
    stem_p = plan_p.parent / "music_stem.wav"
    h = hashlib.sha1(json.dumps({k: plan[k] for k in ("background", "jingles", "levels", "video_duration")}, sort_keys=True).encode()).hexdigest()[:12]
    meta_p = plan_p.parent / "music_stem.json"
    if stem_p.exists() and meta_p.exists():
        meta = json.loads(meta_p.read_text())
        if meta.get("hash") == h: return stem_p, meta["metrics"]
    stem, metrics = build_stem(plan, voice_of(video))
    write_wav(stem_p, stem); meta_p.write_text(json.dumps({"hash": h, "metrics": metrics}, indent=1))
    return stem_p, metrics


def report(metrics):
    ok = metrics["speech_to_music_db"] >= 15
    print(f"voice {metrics['voice_db']} dBFS · music under speech {metrics['music_under_speech_db']} dBFS · "
          f"speech-to-music {metrics['speech_to_music_db']} dB {'✅' if ok else '⚠️ (<15 dB: lower duck_db)'} · stem peak {metrics['stem_peak']}")
    return ok


def cmd_preview(a):
    plan_p = Path(a.plan); plan = json.loads(plan_p.read_text())
    if plan["mode"] == "none": print("background_music = none: nothing to preview."); return
    video = Path(a.video or plan["video"]); stem_p, metrics = stem_for(plan_p, plan, video)
    out = plan_p.parent / "music_preview.m4a"
    if out.exists(): out.unlink()                        # the preview is a scratch file; it is always rebuilt
    r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(video), "-i", str(stem_p), "-filter_complex",
                        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",
                        "-vn", "-c:a", "aac", "-b:a", "96k", str(out)], capture_output=True, text=True)
    if r.returncode: raise MusicError(f"preview mix failed: {r.stderr.strip()[:400]}")
    report(metrics)
    print(f"preview: {out}\nlisten, then run the apply step to write the final MP4.")


def cmd_apply(a):
    plan_p = Path(a.plan); plan = json.loads(plan_p.read_text()); out = Path(a.out)
    if plan["mode"] == "none": print("background_music = none: video left unchanged, nothing written."); return
    if out.exists(): raise MusicError(f"Refusing to overwrite {out}")
    video = Path(a.video or plan["video"])
    if abs(probe_duration(video) - plan["video_duration"]) > .05:
        raise MusicError(f"{video} is not the video this plan was made for (duration differs)")
    stem_p, metrics = stem_for(plan_p, plan, video)
    _, a_src, _ = stream_times(video)        # loudnorm flushes ~0.1 s of tail: trim back to the source audio length
    r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(video), "-i", str(stem_p), "-filter_complex",
                        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0:duration=first,"
                        f"loudnorm=I=-16:TP=-1.5:LRA=7,aformat=sample_rates=48000:channel_layouts=stereo,atrim=end={a_src or plan['video_duration']:.4f}[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-movflags", "+faststart", str(out)], capture_output=True, text=True)
    if r.returncode:
        try: out.unlink(missing_ok=True)
        except OSError: pass
        raise MusicError(f"final mix failed: {r.stderr.strip()[:400]}")
    ok = report(metrics)
    fi, rate = probe_frames(video); fo, _ = probe_frames(out)
    (d_in, a_in, _), (d_out, a_out, a_start) = stream_times(video), stream_times(out)
    lufs = subprocess.run(["ffmpeg", "-nostats", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs); P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lufs)
    frame = 1 / (rate or 30)
    sync = fi == fo and abs(d_in - d_out) < frame / 2 and abs(a_out - (a_in or d_out)) < 2 * frame and abs(a_start) < frame
    res = {"output": str(out), "frames_in": fi, "frames_out": fo, "duration_in": d_in, "duration_out": d_out,
           "audio_duration_out": a_out, "audio_start": a_start,
           "sync_ok": sync, "lufs": float(I[-1]) if I else None, "true_peak_dbfs": float(P[-1]) if P else None,
           "speech_clear": ok, **metrics}
    (plan_p.parent / "music_check.json").write_text(json.dumps(res, indent=1))
    print(f"frames {fi} → {fo} · video {d_in:.3f}s → {d_out:.3f}s · audio {a_out:.3f}s from {a_start:.3f}s · {'✅ in sync' if sync else '❌ length changed'} · "
          f"{res['lufs']} LUFS · true peak {res['true_peak_dbfs']} dBFS\nwrote {out}")
    if not sync: raise MusicError("output length differs from the input video")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("import"); p.add_argument("--lofi"); p.add_argument("--kenney"); p.add_argument("--copy", action="store_true")
    p = sp.add_parser("analyze"); p.add_argument("--limit", type=int); p.add_argument("--only"); p.add_argument("--force", action="store_true")
    p = sp.add_parser("plan"); p.add_argument("video"); p.add_argument("srt"); p.add_argument("out_dir")
    for o in ("--config", "--cues", "--script", "--storyboard", "--refs"): p.add_argument(o)
    p.add_argument("--mode", choices=["auto", "manual", "none"], help="override background_music from the config")
    p.add_argument("--replan", action="store_true")
    p = sp.add_parser("show"); p.add_argument("plan")
    p = sp.add_parser("preview"); p.add_argument("plan"); p.add_argument("--video")
    p = sp.add_parser("apply"); p.add_argument("plan"); p.add_argument("out"); p.add_argument("--video")
    a = ap.parse_args(argv)
    try:
        {"import": cmd_import, "analyze": cmd_analyze, "plan": cmd_plan, "show": cmd_show,
         "preview": cmd_preview, "apply": cmd_apply}[a.cmd](a)
    except (MusicError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"music.py {a.cmd}: {e}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
