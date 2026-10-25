#!/usr/bin/env python3
"""Eva Video Style SFX: synthesizes a short sound-effects stem from a cue list (never music).
Cues: [[kind, seconds, gain, {args}], ...] with kind in whoosh|pop|click|impact|riser|ding|applause.
usage: sfx.py cues.json DURATION_SECONDS out.wav   (requires numpy)"""
import json, sys, wave
import numpy as np
SR = 48000
cues, DUR, OUT = json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3]
L = int(SR * DUR); out = np.zeros(L, np.float32); rng = np.random.default_rng(21)
def env(n, a, d):
    e = np.ones(n, np.float32); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def lp_sweep(x, f0, f1):
    n = len(x); fc = np.geomspace(f0, f1, n); a = 1 - np.exp(-2 * np.pi * fc / SR); y = np.zeros(n, np.float32); s = 0.0
    for k in range(n): s += a[k] * (x[k] - s); y[k] = s
    return y
def whoosh(d=.32, f0=3500, f1=400):
    n = int(d * SR); y = lp_sweep(rng.normal(0, 1, n).astype(np.float32), f0, f1); return y * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 / (abs(y).max() + 1e-9)
def pop(f=900, d=.09):
    n = int(d * SR); t = np.arange(n) / SR; fr = f * (1 + 1.4 * np.exp(-t * 60)); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, .002, .025)
def click(d=.025):
    n = int(d * SR); return rng.normal(0, 1, n) * env(n, .0004, .003)
def impact(d=.7):
    n = int(d * SR); t = np.arange(n) / SR; fr = 48 + 110 * np.exp(-t * 22)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, .002, .22) + rng.normal(0, 1, n) * env(n, .001, .025) * .4
def riser(d=.8):
    n = int(d * SR); t = np.arange(n) / SR; tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(250, 1300, n)) / SR) * .3
    return (tone + whoosh(d, 300, 7000) * .7) * np.linspace(0, 1, n) ** 2
def ding(f=1320, d=.6):
    n = int(d * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.01 * t)) * env(n, .002, .18)
def applause(d=1.5):
    n = int(d * SR); y = np.zeros(n, np.float32)
    for k in range(int(d * 55)):
        i = int(rng.random() * (n - 2400)); m = 1600 + int(rng.random() * 800)
        y[i:i + m] += (rng.normal(0, 1, m) * env(m, .0005, .006)).astype(np.float32) * (.4 + .6 * rng.random())
    return y * np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(5, 0, n))
GEN = {'applause': applause, 'whoosh': whoosh, 'pop': pop, 'click': click, 'impact': impact, 'riser': riser, 'ding': ding}
for c in cues:
    kind, t, g = c[0], c[1], c[2]; args = c[3] if len(c) > 3 else {}
    sig = GEN[kind](**args).astype(np.float32); i = int(t * SR); j = min(L, i + len(sig))
    if i < L: out[i:j] += sig[:j - i] * g
out = np.tanh(out * 1.1) * .9
w = wave.open(OUT, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print(OUT, len(cues), 'cues')
