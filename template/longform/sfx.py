"""Procedural sound effects (no samples needed): riser, impact, whoosh, burn, chime, sparkle, water drop, tick.
All return float32 mono arrays at SR; `mix(cues, duration)` places them on a timeline."""
import numpy as np

SR = 44100
_rng = np.random.default_rng(7)


def _t(d): return np.arange(int(d * SR)) / SR


def _sweep_noise(d, f0, f1, bw=0.6, shape=None):
    """white noise through a band-pass whose centre glides f0 -> f1 (log), via STFT masking"""
    n = int(d * SR); x = _rng.standard_normal(n + 2048).astype(np.float32)
    N, hop = 2048, 512; win = np.hanning(N).astype(np.float32)
    out = np.zeros(n + 2048, np.float32); f = np.fft.rfftfreq(N, 1 / SR)
    frames = range(0, n, hop)
    for k, i in enumerate(frames):
        u = i / max(1, n - 1); u = shape(u) if shape else u
        fc = f0 * (f1 / f0) ** u
        m = np.exp(-0.5 * (np.log(np.maximum(f, 1) / fc) / bw) ** 2)
        X = np.fft.rfft(x[i:i + N] * win) * m
        out[i:i + N] += np.fft.irfft(X).astype(np.float32) * win
    out = out[:n]; return out / (np.abs(out).max() + 1e-9)


def riser(d=1.6):
    t = _t(d); env = (t / d) ** 2.2
    nz = _sweep_noise(d, 400, 9000, 0.5) * env
    tone = np.sin(2 * np.pi * np.cumsum(220 * 4 ** (t / d)) / SR) * env * 0.25
    return (0.8 * nz + tone).astype(np.float32)


def impact(d=1.6):
    t = _t(d)
    boom = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 3) + 38) / SR) * np.exp(-t * 3.2)
    hit = _rng.standard_normal(len(t)) * np.exp(-t * 28)
    tail = _sweep_noise(d, 3000, 400, 0.7) * np.exp(-t * 2.5) * 0.5
    return (1.0 * boom + 0.45 * hit + tail).astype(np.float32)


def whoosh(d=0.7, up=True, heavy=False):
    t = _t(d); env = np.sin(np.pi * t / d) ** (1.5 if heavy else 2.2)
    f0, f1 = (300, 2600) if up else (2600, 300)
    w = _sweep_noise(d, f0, f1, 0.45 if not heavy else 0.8) * env
    if heavy: w += np.sin(2 * np.pi * np.cumsum(70 + 40 * t / d) / SR) * env * 0.5
    return w.astype(np.float32)


def burn(d=1.1):
    t = _t(d); env = np.minimum(1, t / 0.04) * np.exp(-t * 2.2)
    roar = _sweep_noise(d, 250, 900, 0.9) * env
    crack = (_rng.random(len(t)) > 0.9985) * _rng.standard_normal(len(t)) * 3 * np.exp(-t * 1.5)
    return (roar + 0.35 * np.convolve(crack, np.exp(-np.arange(200) / 30), 'same')).astype(np.float32)


def chime(f=1320.0, d=1.6):
    t = _t(d); s = np.zeros_like(t)
    for k, (r, a) in enumerate(((1, 1.0), (2.76, 0.5), (5.4, 0.25), (8.93, 0.12))):
        s += a * np.sin(2 * np.pi * f * r * t + k) * np.exp(-t * (3 + 2.5 * k))
    return (s * np.minimum(1, t / 0.004) * 0.6).astype(np.float32)


def sparkle(d=1.4, n=14):
    out = np.zeros(int(d * SR), np.float32)
    for i in range(n):
        st = int(_rng.uniform(0, d - 0.4) * SR); c = chime(_rng.uniform(2500, 6000), 0.4) * _rng.uniform(0.2, 0.5)
        out[st:st + len(c)] += c[: len(out) - st]
    return out


def drop(d=0.35):
    t = _t(d); f = 1400 * np.exp(-t * 9) + 500
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.8).astype(np.float32)


def tick(d=0.05):
    t = _t(d); return (np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 160) * 0.35).astype(np.float32)


def mix(cues, duration):
    """cues: [(time_s, array, gain)] -> mono float32 track"""
    out = np.zeros(int(duration * SR) + SR, np.float32)
    for (t0, a, g) in cues:
        i = int(t0 * SR)
        if i < 0: a = a[-i:]; i = 0
        j = min(len(out), i + len(a)); out[i:j] += a[: j - i] * g
    return out[: int(duration * SR)]


def write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1); y = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
