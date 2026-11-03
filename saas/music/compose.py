#!/usr/bin/env python3
"""EVA Video Studio · original background beds, composed in code.

Why: paid videos may only carry music whose commercial rights are confirmed. No track in music-library/background has a
verified license (Open Lo-Fi = UNVERIFIED), so the MVP ships its own instrumental beds. Every sample below is synthesized
from oscillators and noise by this file (no samples, loops or third-party audio), so the output is an original work owned
by the repository owner and is cleared for customer videos. License id written to the manifest: "eva-original".

    python3 saas/music/compose.py OUT_DIR [--seconds 34] [--mp3]     writes OUT_DIR/<id>.wav (+ .mp3) and manifest.json

Deterministic: same code + seed = same audio, so the image build and the website demo use identical tracks.
"""
import argparse, json, subprocess, sys, zlib
from pathlib import Path
import numpy as np

SR = 48000
TRACKS = [   # id, title, bpm, key root (MIDI), chord progression (scale degrees + quality), style, pace
    {"id": "bright-pop", "title": "Bright Pop", "bpm": 112, "root": 60, "prog": [(0, "maj"), (7, "maj"), (9, "min"), (5, "maj")],
     "style": "pop", "pace": "fast", "mood": "upbeat, beauty, lifestyle, product"},
    {"id": "calm-lofi", "title": "Calm Lo-fi", "bpm": 84, "root": 57, "prog": [(0, "min7"), (5, "min7"), (10, "maj7"), (3, "maj7")],
     "style": "lofi", "pace": "slow", "mood": "relaxed, education, tips, tutorial"},
    {"id": "inspire", "title": "Inspire", "bpm": 100, "root": 62, "prog": [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj")],
     "style": "corporate", "pace": "medium", "mood": "business, education, explainer, confident"},
    {"id": "luxury-ambient", "title": "Luxury Ambient", "bpm": 72, "root": 55, "prog": [(0, "maj7"), (5, "maj7"), (9, "min7"), (4, "min7")],
     "style": "ambient", "pace": "slow", "mood": "real estate, luxury, calm, premium"},
]
QUAL = {"maj": [0, 4, 7], "min": [0, 3, 7], "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10]}


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=.01, d=.1, s=.6, r=.2, length=None):
    """ADSR envelope of n samples; `length` = gate length in seconds (release after it)."""
    t = np.arange(n) / SR; g = length if length is not None else n / SR - r
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel = t > g
    e[rel] = s * np.exp(-(t[rel] - g) / max(r / 4, 1e-3))
    return e


def osc(f, n, kind="sine", detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    if kind == "sine": return np.sin(2 * np.pi * f * t + phase)
    if kind == "tri": return sum(((-1) ** k) * np.sin(2 * np.pi * f * (2 * k + 1) * t) / (2 * k + 1) ** 2 for k in range(5)) * 8 / np.pi ** 2
    if kind == "saw":   # band-limited: harmonics below 12 kHz only
        out = np.zeros(n)
        for k in range(1, int(12000 / f) + 1): out += np.sin(2 * np.pi * f * k * (1 + detune) * t) / k
        return out * 2 / np.pi
    if kind == "epiano":   # FM-ish electric piano
        return np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 3) * np.sin(2 * np.pi * f * 2 * t))
    raise ValueError(kind)


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # vectorised one-pole via lfilter-free recursion in chunks would be faster; tracks are short, a loop is fine
    for i, v in enumerate(x): acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def reverb(x, seconds=1.6, mix=.25, seed=1):
    rng = np.random.default_rng(seed); n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 5.5 / seconds); ir[0] = 0
    m = len(x) + n; F = 1 << (m - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    wet /= (np.abs(wet).max() + 1e-9); return x * (1 - mix) + wet * mix * np.abs(x).max()


def place(buf, x, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]


def kick(): n = int(.35 * SR); t = np.arange(n) / SR; f = 45 + 80 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def snare(rng): n = int(.22 * SR); t = np.arange(n) / SR; return (rng.standard_normal(n) * .7 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t * 18)
def hat(rng, open_=False):
    n = int((.18 if open_ else .05) * SR); x = rng.standard_normal(n); x = x - lowpass(x, 7000)
    return x * np.exp(-np.arange(n) / SR * (18 if open_ else 70))


def compose(tr, seconds, seed=7):
    rng = np.random.default_rng(seed + zlib.crc32(tr["id"].encode()) % 1000)   # not hash(): salted per process
    beat = 60 / tr["bpm"]; bar = 4 * beat; n = int(seconds * SR)
    chords, bass, lead, drums, pad = (np.zeros(n) for _ in range(5))
    bars = int(np.ceil(seconds / bar))
    for b in range(bars):
        deg, q = tr["prog"][b % len(tr["prog"])]; t0 = b * bar; root = tr["root"] + deg
        notes = [root + i for i in QUAL[q]]
        st = tr["style"]
        # harmony
        if st in ("pop", "corporate"):
            hits = [0, 1.5, 2, 3.5] if st == "pop" else [0, 2]
            for h in hits:
                ln = int(beat * (1.4 if st == "pop" else 2.0) * SR)
                for m in notes: place(chords, osc(hz(m), ln, "saw" if st == "pop" else "tri") * env(ln, .005, .25, .35, .3) * .10, t0 + h * beat)
        if st in ("lofi", "ambient"):
            ln = int(bar * SR * 1.05)
            for m in notes:
                k = "epiano" if st == "lofi" else "sine"
                x = osc(hz(m), ln, k) + (.5 * osc(hz(m) * 1.003, ln, "sine") if st == "ambient" else 0)
                place(pad, x * env(ln, .05 if st == "lofi" else .9, .6, .55, .9) * (.12 if st == "lofi" else .09), t0)
        # arpeggio / lead
        if st in ("corporate", "pop", "ambient"):
            step = beat / (2 if st != "ambient" else 1)
            seq = (notes + [notes[0] + 12, notes[1] + 12]) if st != "ambient" else [notes[-1] + 12, notes[1] + 12]
            for i in range(int(bar / step)):
                m = seq[i % len(seq)] + 12 * (st == "pop"); ln = int(step * SR * (1.0 if st != "ambient" else 2.5))
                place(lead, osc(hz(m), ln, "epiano" if st == "corporate" else "sine") * env(ln, .004, .15, .2, .2) * (.07 if st != "ambient" else .05), t0 + i * step)
        # bass
        bl = [0, 2] if st in ("lofi", "ambient") else [0, 1, 2, 3]
        for i in bl:
            ln = int(beat * (2 if len(bl) == 2 else .9) * SR)
            place(bass, osc(hz(root - 24), ln, "tri" if st != "ambient" else "sine") * env(ln, .01, .2, .7, .15) * .32, t0 + i * beat)
        # drums
        if st == "ambient": continue
        swing = .08 * beat if st == "lofi" else 0
        for i in range(4):
            if st == "pop" or i in (0, 2) or (st == "corporate" and i == 2): place(drums, kick() * (.9 if st != "lofi" else .7), t0 + i * beat)
            if i in (1, 3): place(drums, snare(rng) * (.22 if st != "lofi" else .15), t0 + i * beat)
            for h in (0, .5):
                place(drums, hat(rng, open_=(st == "pop" and h == .5 and i == 3)) * (.035 if st != "lofi" else .025), t0 + (i + h) * beat + (swing if h else 0))
    st = tr["style"]
    if st == "lofi": pad = lowpass(pad, 2600); drums = lowpass(drums, 5000)
    mix = chords + pad + lead
    mix = reverb(mix, 2.4 if st == "ambient" else 1.4, .45 if st == "ambient" else .22)
    mix = mix + lowpass(bass, 900) + drums
    if st == "lofi": mix += lowpass(rng.standard_normal(n), 3000) * .006   # soft vinyl hiss
    st_l = mix + reverb(lead, 1.0, .5, seed=3) * .15; st_r = mix + reverb(chords + pad, 1.0, .5, seed=4) * .15   # gentle stereo width
    out = np.stack([st_l, st_r], 1)
    fade = int(.02 * SR); out[:fade] *= np.linspace(0, 1, fade)[:, None]; out[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))[:, None]
    rms = np.sqrt((out ** 2).mean()); out *= (10 ** (-18 / 20)) / (rms + 1e-9)   # ≈ -18 dBFS RMS
    pk = np.abs(out).max()
    if pk > .89: out *= .89 / pk
    return out.astype(np.float32)


def write_wav(p, x):
    import wave
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out"); ap.add_argument("--seconds", type=float, default=34.0); ap.add_argument("--mp3", action="store_true")
    a = ap.parse_args(argv); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    man = {"license": "eva-original", "note": "Composed procedurally by saas/music/compose.py (oscillators + noise, no samples or "
           "third-party audio). Original work of the repository owner; cleared for use in customer videos.", "tracks": []}
    for tr in TRACKS:
        x = compose(tr, a.seconds); wav = out / f"{tr['id']}.wav"; write_wav(wav, x)
        if a.mp3:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-c:a", "libmp3lame", "-b:a", "128k", out / f"{tr['id']}.mp3"], check=True)
        man["tracks"].append({k: tr[k] for k in ("id", "title", "bpm", "style", "pace", "mood")} | {"file": wav.name, "license": "eva-original"})
        print("composed", wav, f"{len(x) / SR:.1f}s")
    (out / "manifest.json").write_text(json.dumps(man, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
