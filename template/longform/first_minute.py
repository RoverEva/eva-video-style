#!/usr/bin/env python3
"""白羊座的内心世界 · 8 分钟版的第一分钟（动态样片）

Uses the v2 keyframe art (story_frames.py) and animates it:
  * every scene is drawn stroke by stroke (each path grows in, in drawing order) — the picture grows
  * vector camera moves (push-ins, pull-outs, tracking, a match-cut zoom from the heart into the drop)
  * live effects: twinkling stars, meteors, falling rain, run cycle, flicker, beat-synced glints
  * captions typed on the eighth-note grid; procedural SFX on the big moments; muffled music until the drop

  python3 template/longform/first_minute.py --out out/long/v3/白羊座_第一分钟.mp4 [--stills 3,14,...]
"""
import argparse, math, os, subprocess, sys, tempfile, time
from multiprocessing import Process
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import W, H, Palette, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, spline, lerp, cl, ramp, eo, eio, pulse, pop
import zodiac_signs
from vis import heart_pts
import story_frames as SF
from story_frames import figure, glint, milkyway, meteor, skyline, lamp, sp, solid, POSES, BLACK
import sfx
from short_aries import build_audio as _unused  # noqa: F401  (keeps the music helpers importable)
import render_long as R

E8 = 60 / 112.9117 / 2
MUSIC_START = 12
DROP = 52
END = 226
PF, PV, PA = Palette('fire'), Palette('violet'), Palette('azure')


def T(m): return m * E8


def quarter(t): return 2 * E8 * math.floor(t / (2 * E8))


# ================================================================ growing canvas
class GrowCanvas(Canvas):
    """Every draw call is one stroke. Strokes are drawn in order, like a pen: 'bg' strokes over a short window,
    'fg' strokes spread over the whole scene so something is always being drawn. A growing stroke carries a
    bright pen tip."""
    def __init__(self, cam, t, sched):
        super().__init__(cam); self.t = t; self.sched = sched; self.mode = 'bg'; self.cnt = {'bg': 0, 'fg': 0}; self.instant = False

    def _f(self):
        k = self.cnt[self.mode]; self.cnt[self.mode] += 1
        if self.instant or self.mode not in self.sched: return 1.0
        t0, dt, dur = self.sched[self.mode]
        return cl((self.t - t0 - k * dt) / dur)

    def path(self, pts, col, a=1., th=2., frac=1., smooth=True, closed=False, layer=None):
        f = self._f()
        if f <= 0: return
        g = eio(f)
        super().path(pts, col, a, th, frac * g, smooth, closed, layer)
        if g < 1 and layer is None and len(pts) > 1:   # pen tip
            P = spline(pts, closed=closed) if smooth and len(pts) > 2 else np.array(pts, float)
            seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
            L = cum[-1] * frac * g; k = int(np.clip(np.searchsorted(cum, L), 1, len(P) - 1)); r = (L - cum[k - 1]) / max(seg[k - 1], 1e-6)
            tip = P[k - 1] + (P[k] - P[k - 1]) * r
            super().circle(tuple(tip), th * 0.9, PF.WARM, a, fill=True); super().glow(tuple(tip), 10 + 4 * th, PF.GOLD, 0.9 * a)

    def poly(self, pts, col, a=1., layer=None):
        f = self._f()
        if f > 0: super().poly(pts, col, a * (1 if not np.any(col) else eio(f)), layer)

    def circle(self, c, r, col, a=1., th=2., fill=False, layer=None):
        f = self._f()
        if f > 0: super().circle(c, r, col, a * eio(f), th, fill, layer)

    def glow(self, c, r, col, a=1.):
        f = self._f()
        if f > 0: super().glow(c, r, col, a * eio(f))


_COUNTS = {}


class Shot:
    """scene canvas. bg strokes appear over `bg_span` s from t0; fg strokes are spread over [t0, t0 + fg_span]"""
    def __init__(self, cam, t, t0, key=None, bg_span=1.2, fg_span=6.0, dur=0.7, count_fn=None):
        sched = {}
        if key is not None:
            nb, nf = _COUNTS.get(key, (400, 200))
            sched = {'bg': (t0, bg_span / max(nb, 1), 0.5), 'fg': (t0 + 0.15, max(0.0, fg_span - dur) / max(nf, 1), dur)}
        self.cv = GrowCanvas(cam, t, sched); self.fg = np.zeros((H, W, 3), np.float32); self.roll = 0.0; self.cam = cam

    def bokeh(self, c, r, col, a=0.5):
        q = self.cam([c])[0]
        cv2.circle(self.fg, (int(q[0]), int(q[1])), int(r), tuple(float(v) * a * 0.55 for v in col), -1, cv2.LINE_AA)
        cv2.circle(self.fg, (int(q[0]), int(q[1])), int(r), tuple(float(v) * a for v in col), 2, cv2.LINE_AA)


def drift(t, t0, amp=1.0):
    """the camera never stops: slow continuous dolly + float"""
    u = t - t0
    return 1 + 0.006 * u * amp, 14 * math.sin(t * 0.37) * amp, 9 * math.sin(t * 0.29 + 1) * amp


def stars_live(cv, P, t, n=180, ymax=760, seed=5, a=1.0, glints=7, x0=-400, x1=W + 400, drift=0.0):
    rr = np.random.default_rng(seed)
    for i in range(n):
        x, y, s, ph = rr.uniform(x0, x1), rr.uniform(0, ymax), rr.uniform(0.6, 1.8), rr.uniform(0, 6.3)
        tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * rr.uniform(1, 3) + ph))
        cv.circle((x - drift, y), s, P.WARM if i % 4 == 0 else P.SOFT, a * tw * 0.8, fill=True)
    qt = quarter(t)
    for g in range(glints):
        x, y = rr.uniform(x0 + 300, x1 - 300), rr.uniform(40, ymax * 0.8)
        k = pulse(t, qt + (g % 4) * E8 * 0.5, 0.6)
        glint(cv, (x - drift, y), 10 + 14 * k, P.WARM, a * (0.35 + 0.65 * k), 0.2)


def rain_live(cv, P, t, a=0.55, n=380, slant=0.14, seed=4, ymax=H, light=None, mask=None, speed=1400):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        x0 = rr.uniform(-100, W + 100); y0 = rr.uniform(0, ymax); L = rr.uniform(16, 38)
        y = (y0 + speed * t) % ymax; x = x0 - slant * (speed * t % ymax)
        x = (x + 100) % (W + 200) - 100
        if mask and mask(x, y): continue
        k = 1.0
        if light is not None: k = 1 + 2.5 * math.exp(-(math.hypot(x - light[0], y - light[1]) / 260) ** 2)
        cv.path([(x, y), (x - slant * L, y + L)], P.WARM if k > 1.8 else P.LINE, min(1, a * rr.uniform(0.3, 1) * k), 1.0, smooth=False)


def run_pose(u):
    """blend between the run pose and its mirrored stride; u in [0,1)"""
    a = POSES['run']; b = dict(a)
    for k1, k2 in (('el', 'el2'), ('ha', 'ha2'), ('kn', 'kn2'), ('ft', 'ft2')): b[k1], b[k2] = a[k2], a[k1]
    w = 0.5 - 0.5 * math.cos(2 * math.pi * u)
    POSES['_run'] = {k: (tuple(lerp(np.array(a[k]), np.array(b[k]), w)) if isinstance(a[k], tuple) else a[k]) for k in a}
    POSES['_run']['head'] = (a['head'][0], a['head'][1] - 0.01 * math.sin(4 * math.pi * u))
    return '_run'


def walk_pose(u):
    a = POSES['walk']; b = dict(a)
    for k1, k2 in (('el', 'el2'), ('ha', 'ha2'), ('kn', 'kn2'), ('ft', 'ft2')): b[k1], b[k2] = a[k2], a[k1]
    w = 0.5 - 0.5 * math.cos(2 * math.pi * u)
    POSES['_walk'] = {k: (tuple(lerp(np.array(a[k]), np.array(b[k]), w)) if isinstance(a[k], tuple) else a[k]) for k in a}
    return '_walk'


def flame_shape(cv, c, h, P, a, t, close=0.0):
    base = c[1] + 0.42 * h
    for k, (scl, col, th) in enumerate(((1.0, P.GOLD, 2.4), (0.78, P.WARM, 1.8), (1.25, P.GOLD, 1.2), (0.55, P.WARM, 1.2))):
        w = h * scl * 0.36; hh = h * scl; wob = 0.04 * math.sin(t * 7 + k)
        pts = [(c[0] + (0.04 + wob) * hh, base - hh), (c[0] + w * 0.55, base - hh * 0.45), (c[0] + w * 0.5, base - hh * 0.15), (c[0], base), (c[0] - w * 0.5, base - hh * 0.15), (c[0] - w * 0.55, base - hh * 0.45)]
        cv.path(sp(pts, 10, True), col, a * (0.9 - 0.2 * k), th, smooth=False)
    if close < 1: flame(cv, c[0], base, h * 0.9, P.GOLD, 0.45 * a * (1 - close)); flame(cv, c[0], base, h * 1.3, P.GOLD, 0.18 * a, layer=cv.F)


def heart(cv, c, s, P, a, frac=1.0, beat=0.0):
    s = s * (1 + 0.12 * beat)
    hp = [(c[0] + s * u, c[1] + s * v) for u, v in heart_pts(0, 0, 1.0, 60)]
    cv.path(hp, P.WARM, a, 2.8, frac, smooth=False)
    if frac >= 1: cv.poly(hp, P.WARM * 0.35, 0.8 * a, layer=cv.F)
    cv.glow(c, s * 1.3, P.GOLD, (0.6 + 0.5 * beat) * a * frac)


def cap(tx, txt, x, y, size, m0, m1, step=0.5, gold=(), t=0, col=None, bold=False):
    g = tuple(range(len(txt))) if gold == 'all' else tuple(gold)
    tx.chars(txt, x, y, F(SERIF_BL if bold or size >= 90 else SERIF_B, size), col or PF.WHITE, t, T(m0), T(m1), gold=g, stagger=E8 * step)


# ================================================================ scenes (each returns palette, glow)
def hook(t, n, tx):
    """0 – 13.8 s: spark -> flame -> heart, then the camera dives into the heart"""
    c = (960, 610)
    s = lerp(1.0, 1.12, eio(ramp(n, 0, 16)))
    if n >= 24: s = lerp(1.12, 1.55, eio(ramp(n, 24, 34)))
    if n >= 44: s = 1.55 * (1 + 7 * eio(ramp(n, 44, 52)) ** 2.2)
    s *= 1 + 0.08 * pulse(t, T(20), 0.35)
    ds, dx, dy = drift(t, 0, 0.6)
    cam = Cam(s * ds, 960 + dx, (lerp(610, 560, ramp(n, 24, 34)) if n < 44 else 560) + dy)
    sh = Shot(cam, t, 0); cv = sh.cv; P = PF; qt = quarter(t)
    # dust + bokeh
    rr = np.random.default_rng(1)
    for i in range(60):
        x, y = rr.uniform(650, 1270), rr.uniform(380, 840); ph = rr.uniform(0, 6.3)
        cv.circle((x + 6 * math.sin(t * 0.7 + ph), y - (t * 8 + ph * 20) % 60), rr.uniform(0.8, 2), P.WARM, 0.5 * (0.5 + 0.5 * math.sin(t * 2 + ph)), fill=True)
    for i in range(10):
        sh.bokeh((rr.uniform(0, W) + 30 * math.sin(t * 0.3 + i), rr.uniform(0, H)), rr.uniform(30, 90), P.GOLD * 0.5, 0.3)
    # the spark and its heartbeat rings
    h = 0.0
    if n >= 8: h = 40 + 26 * cl(math.floor(n) - 7, 0, 5) * (0.85 + 0.15 * pop(t, T(math.floor(n)), 0.12))
    if n >= 16: h = 190 * (1 + 0.05 * math.sin(t * 20))
    if n >= 20: h = lerp(520, 360, eo(ramp(n, 20, 23)))
    if n >= 23: h = 360 * (1 + 0.04 * math.sin(t * 9))
    if n >= 40: h = lerp(360, 300, ramp(n, 40, 48))
    if n < 10:
        r = 6 * (1 + 0.5 * pulse(t, T(0), 0.3) + 0.5 * pulse(t, T(2), 0.3))
        cv.circle(c, r, P.WARM, 1, fill=True); cv.glow(c, 60, P.GOLD, 1.0); glint(cv, c, 50 + 30 * pulse(t, T(0), 0.5) + 30 * pulse(t, T(2), 0.5), P.WARM, 1, 0.2)
    for p0 in (0, 2, 8):
        if T(p0) <= t < T(p0) + 1.2:
            k = (t - T(p0)) / 1.2; cv.circle(c, 20 + 300 * eo(k), P.GOLD, (1 - k) * 0.7, 1.4)
    close = ramp(n, 24, 30)
    if h > 0: flame_shape(cv, c, h, P, 1.0, t, close)
    if T(16) <= t < T(20):   # an ember flies in
        u = eio((t - T(16)) / (T(20) - T(16)))
        for k in range(10):
            uu = max(0, u - k * 0.025); p = (lerp(200, c[0], uu), lerp(150, c[1] - 40, uu) - 160 * math.sin(uu * math.pi))
            cv.circle(p, 6 - k * 0.5, P.WARM if k == 0 else P.GOLD, 1 - k / 10, fill=True)
        glint(cv, (lerp(200, c[0], u), lerp(150, c[1] - 40, u) - 160 * math.sin(u * math.pi)), 22, P.WARM, 1)
    if T(20) <= t < T(20) + 1.6:   # flare
        k = (t - T(20)) / 1.6; rr2 = np.random.default_rng(9)
        for j in range(40):
            q = rr2.uniform(0, 6.3); r = 80 + 700 * eo(k) * rr2.uniform(0.5, 1)
            p = (c[0] + r * math.cos(q), c[1] - 60 + r * math.sin(q)); cv.circle(p, 2.6, P.WARM, 1 - k, fill=True)
        for r1 in (700, 1100): cv.circle(c, 60 + r1 * eo(k), P.GOLD, (1 - k) * 0.8, 1.6)
    # sparks rising out of the flame
    if n >= 20:
        rr3 = np.random.default_rng(4)
        for j in range(50):
            ph = rr3.uniform(0, 1); v = (t * 0.35 + ph) % 1; x = c[0] + rr3.normal(0, 90) * (0.4 + v)
            y = c[1] - 100 - 600 * v; cv.path([(x, y), (x, y - 14)], P.WARM, (1 - v) * 0.9, 1.6, smooth=False)
    if n >= 26:
        heart(cv, c, 118, P, 1.0, eio(ramp(n, 26, 29)), pulse(t, qt, 0.25))
        if n >= 29: glint(cv, (c[0] + 66, c[1] - 74), 30 + 20 * pulse(t, qt, 0.4), P.WARM, 1)
    # captions (screen)
    cap(tx, '他的心里', 960, 190, 72, 1, 15.6, 1, t=t)
    cap(tx, '住着一团火', 960, 290, 72, 6, 15.6, 0.5, (3, 4), t=t)
    cap(tx, '一碰', 960, 210, 72, 16, 23.6, 1, t=t)
    cap(tx, '就燃', 960, 330, 120, 20, 23.6, 0.25, 'all', t=t)
    cap(tx, '可火的最中间', 960, 170, 72, 24, 39.6, 0.5, t=t)
    cap(tx, '藏着一颗很软很软的心', 960, 270, 72, 28, 39.6, 0.5, (4, 5, 6, 7), t=t)
    cap(tx, '他从不让人看见', 960, 200, 76, 40, 47.6, 0.5, t=t)
    white = ramp(n, 50, 52)
    return sh, P, 0.6, 0.25 * pulse(t, T(20), 0.4) + white * 0.9


def drop_scene(t, n, tx):
    """13.8 – 21.3 s: match-cut from inside the heart to the wide sky; title"""
    chest = (640 + 0.014 * 380, 814 - 0.47 * 380 - 0.34 * 380 + 0.115 * 380)
    u = eio(ramp(n, DROP, DROP + 5))
    s = lerp(7.0, 1.0, u) * (1 + 0.04 * ramp(n, DROP + 5, 80))
    ds, dx, dy = drift(t, T(DROP) + 1.5, 0.8 * u)
    cam = Cam(s * ds, lerp(chest[0], 960, u) + dx, lerp(chest[1], 540, u) + dy)
    sh = Shot(cam, t, T(DROP), 'drop', 3.0, T(78) - T(DROP), 0.9); cv = sh.cv; P = PF
    if T(58) <= t < T(58) + 1.2:
        k = (t - T(58)) / 1.2; meteor(cv, (lerp(1900, 1300, k), lerp(60, 260, k)), math.radians(160), 300, P.WARM, 1 - 0.6 * k)
    skyline(cv, 1040, P, 0.45, 3, 0, W, 60, 220, 0.3)
    rr = np.random.default_rng(5)
    for i in range(26): sh.bokeh((rr.uniform(0, W) + 10 * math.sin(t + i), rr.uniform(900, 1080)), rr.uniform(10, 26), [P.WARM, P.GOLD][i % 2], 0.6)
    hill = sp([(-50, 920), (300, 870), (560, 820), (760, 812), (980, 840), (1260, 910), (1500, 960), (1970, 990)], 8)
    cv.poly(hill + [(1970, 1080), (-50, 1080)], BLACK, 1.0); cv.path(hill, P.LINE, 0.9, 2.2, smooth=False)
    cv.instant = True
    heart(cv, (chest[0] + 6, chest[1]), 12, P, 1.0, 1.0, pulse(t, quarter(t), 0.25)); cv.glow((chest[0] + 6, chest[1]), 60, P.GOLD, 0.8)
    cv.instant = False
    milkyway(cv, P, (200, 0), (1500, 700), 170, 6, 0.9)
    stars_live(cv, P, t, 220, 760, 5, 0.9, 8)
    cv.mode = 'fg'   # he is drawn outward from the heart, stroke after stroke, for the whole scene
    f = figure(cv, 640, 814, 380, 'stand', P.SOFT, 1.0, 1, heart=1.5 * (1 + 0.15 * pulse(t, quarter(t), 0.25)), P=P, rim=(1, -0.3))
    cv.mode = 'bg'
    for j, r1 in enumerate((900, 1300, 1750)):
        tj = T(DROP + 2 * j)
        if tj <= t < tj + 1.4:
            k = (t - tj) / 1.4; cv.circle(f['chest'], 60 + r1 * eo(k), P.GOLD, (1 - k) * 1.0, 2)
    for r_, al in ((150, 0.5), (380, 0.25)): cv.circle(f['chest'], r_ * (1 + 0.03 * pulse(t, quarter(t), 0.4)), P.GOLD, al * ramp(n, DROP + 3, DROP + 6), 1.4)
    cap(tx, '白羊座的内心世界', 1380, 500, 104, DROP + 1, 79.6, 0.5, 'all', t=t, col=PF.HI)
    tx.chars('外表有多倔强  内心就有多柔软', 1380, 600, F(SERIF_B, 46), PF.WHITE, t, T(60), T(79.6), gold=(4, 5, 12, 13), stagger=E8 * 0.5)
    return sh, P, 0.6, 0.6 * pulse(t, T(DROP), 0.7)


def run_scene(t, n, tx):
    """21.3 – 34 s: side tracking shot, he is already running"""
    P = PF; gy = 900; v = 260.0
    t0 = T(80); dtm = t - t0
    rx = 1150 + v * dtm
    zoom = 1 + 0.35 * eio(ramp(n, 104, 108)) * (1 - eio(ramp(n, 110, 114)))
    ds, dx, dy = drift(t, t0, 0.7)
    cam = Cam(zoom * ds * (1 + 0.012 * pulse(t, quarter(t), 0.3)), rx - 190 + (100 if zoom > 1.01 else 0) * (zoom - 1) / 0.35 + dx, 540 + 80 * (zoom - 1) + dy)
    sh = Shot(cam, t, t0, 'run', 2.5, T(126) - t0, 1.0); cv = sh.cv
    stars_live(cv, P, t, 90, 600, 7, 0.6, 4, x0=rx - 1400, x1=rx + 1400, drift=-0.0)
    cv.path([(rx - 1500, gy), (rx + 1500, gy)], P.LINE, 0.8, 1.6, smooth=False)
    for k in range(1, 5): cv.path([(rx - 1500, gy + k * 34), (rx + 1500, gy + k * 34)], P.LINE, 0.25 / k, 1, smooth=False)
    for xm in np.arange(math.floor((rx - 1400) / 160) * 160, rx + 1400, 160): cv.path([(xm, gy + 34), (xm + 50, gy + 34)], P.LINE, 0.5, 2, smooth=False)
    cv.path([(1020, gy), (1020, gy + 140)], P.WARM, 0.7, 3, smooth=False)
    cv.mode = 'fg'
    for k, x in enumerate((810, 890, 970)): figure(cv, x, gy, 250, 'stand', P.DIM * 2.4, 0.75, 1, hair='long' if k == 1 else 'short')
    cv.mode = 'bg'
    u = (dtm / (4 * E8)) % 1
    y_b = -10 * abs(math.sin(math.pi * u * 2))
    cv.instant = True
    figure(cv, rx, gy - 8 + y_b, 360, run_pose(u), P.SOFT, 1.0, 1, heart=1.4 * (1 + 0.15 * pulse(t, quarter(t), 0.25)), P=P, rim=(-1, 0))
    cv.instant = False
    for k in range(12):
        y = 620 + k * 22; L = 320 + 90 * math.sin(k * 1.7 + t * 6)
        cv.path([(rx - 100 - L, y), (rx - 140, y - 4)], P.GOLD, 0.85 - 0.06 * k, 1.8 - 0.08 * k, smooth=False)
    rr = np.random.default_rng(2)
    for j in range(40):
        ph = rr.uniform(0, 1); w = (t * 1.5 + ph) % 1
        cv.circle((rx - 120 - 500 * w, rr.uniform(600, 880) - 40 * w), rr.uniform(1, 2.6), P.WARM, (1 - w), fill=True)
    if n >= 116:   # lightning on "当场就要说清"
        k = ramp(t, T(116), T(116) + 0.08) * (1 - ramp(t, T(116) + 0.3, T(116) + 0.9))
        zz = [(rx + 300, 80), (rx + 360, 220), (rx + 310, 290), (rx + 400, 430), (rx + 350, 500), (rx + 450, 650)]
        cv.path(zz, P.WARM, k, 3.2, smooth=False); cv.path(zz, P.GOLD, 0.5 * k, 18, smooth=False, layer=cv.F)
    cap(tx, '别人还在犹豫', 1420, 300, 64, 82, 95.6, t=t)
    cap(tx, '他已经冲出去了', 1420, 390, 64, 86, 95.6, gold=(3, 4, 5), t=t)
    cap(tx, '想做的事', 1420, 300, 64, 96, 111.6, t=t)
    cap(tx, '今天就要开始', 1420, 390, 64, 100, 111.6, gold=(0, 1, 4, 5), t=t)
    cap(tx, '不服的事', 1420, 300, 64, 112, 127.6, t=t)
    cap(tx, '当场就要说清', 1420, 390, 64, 116, 127.6, gold=(0, 1, 4, 5), t=t)
    return sh, P, 0.6, 0.12 * pulse(t, T(80), 0.3) + 0.3 * pulse(t, T(116), 0.4)


def road_scene(t, n, tx):
    """34 – 60 s: one-point road; he stops and looks back; the 'armour' grows around him"""
    P = PF
    s = lerp(1.0, 1.1, eio(ramp(n, 128, 176)))
    if n >= 176: s = lerp(1.1, 1.7, eio(ramp(n, 176, 186)))
    if n >= 214: s = lerp(1.7, 1.4, eio(ramp(n, 214, 226)))
    head = (430 - 0.01 * 760 * -1, 1130 - 0.47 * 760 - 0.45 * 760)
    cx = lerp(960, head[0] + 330, eio(ramp(n, 176, 186))); cy = lerp(540, head[1] + 130, eio(ramp(n, 176, 186)))
    ds, dx, dy = drift(t, T(128), 0.6)
    cam = Cam(s * ds * (1 + 0.01 * pulse(t, quarter(t), 0.3)), cx + dx, cy + dy)
    sh = Shot(cam, t, T(128), 'road', 3.0, T(176) - T(128), 1.1); cv = sh.cv
    vp = (1000, 600)
    for xb in (-300, 300, 2220, 1620): cv.path([vp, (xb, 1080)], P.LINE, 0.55, 1.4, smooth=False)
    for k in range(1, 9):
        u = (k / 9) ** 2; y = lerp(vp[1], 1080, u)
        cv.path([(lerp(vp[0], 920, u), y), (lerp(vp[0], 1080, u), y + 30 * u)], P.LINE, 0.4, 2, smooth=False)
    lamp(cv, 1060, 610, 120, P, 0.85 * (0.85 + 0.15 * math.sin(t * 13) ** 2), -1)
    stars_live(cv, P, t, 90, 560, 11, 0.6, 4)
    # the one who leaves: walks toward the vanishing point
    w = ramp(n, 140, 168)
    if w < 1:
        fx = lerp(1015, 1000, w); fy = lerp(612, 602, w); fh = lerp(80, 30, w)
        figure(cv, fx, fy, fh, walk_pose((t / (4 * E8)) % 1), P.LINE, 0.75 * (1 - ramp(n, 160, 168)), -1, hair='long', dress=True)
    cv.mode = 'fg'
    beat = pulse(t, quarter(t), 0.25)
    hs = 0.6 * (1 - 0.4 * ramp(n, 152, 158))
    f = figure(cv, 430, 1130, 760, 'lookback', P.SOFT, 1.0, -1, heart=hs * (1 + 0.15 * beat), P=P, rim=(1, -0.2))
    cv.mode = 'bg'
    # armour: arcs grow around him, then crack and leak light
    if n >= 182:
        g = eio(ramp(n, 182, 190)); crack = ramp(n, 204, 210)
        for k in range(4):
            r_ = 300 + 70 * k
            arc = [(f['chest'][0] + r_ * 0.6 * math.cos(q), f['chest'][1] + r_ * math.sin(q)) for q in np.linspace(-math.pi * 0.9, math.pi * 0.9, 60)]
            cv.path(arc, P.GOLD, (0.8 - 0.15 * k) * (1 - 0.5 * crack), 2.2 - 0.3 * k, g, smooth=False)
        if crack > 0:
            rr = np.random.default_rng(8)
            for j in range(9):
                q = rr.uniform(-2.4, 2.4); r_ = 300 + rr.uniform(0, 200)
                p = (f['chest'][0] + r_ * 0.6 * math.cos(q), f['chest'][1] + r_ * math.sin(q))
                cv.path([p, (p[0] + 40 * math.cos(q + 0.4), p[1] + 40 * math.sin(q + 0.4)), (p[0] + 70 * math.cos(q - 0.2), p[1] + 70 * math.sin(q - 0.2))], P.WARM, crack, 2, smooth=False)
                glint(cv, p, 16 * crack * (1 + pulse(t, quarter(t), 0.4)), P.WARM, crack)
            cv.glow(f['chest'], 200, P.GOLD, 0.5 * crack)
    rr = np.random.default_rng(9)
    for i in range(6): sh.bokeh((1500 + rr.uniform(0, 400), 760 + rr.uniform(0, 300)), rr.uniform(40, 90), P.GOLD * 0.7, 0.4)
    cap(tx, '可你知道吗', 1480, 260, 62, 130, 151.6, t=t)
    cap(tx, '跑得最快的人', 1480, 350, 62, 134, 151.6, t=t)
    cap(tx, '最怕的是什么？', 1480, 440, 62, 138, 151.6, t=t)
    cap(tx, '不是输', 1480, 360, 80, 152, 175.6, t=t)
    cap(tx, '是在乎的人转身', 1480, 480, 80, 156, 175.6, 0.5, 'all', t=t)
    cap(tx, '所以他把自己', 1480, 330, 64, 178, 195.6, t=t)
    cap(tx, '包装成刀枪不入', 1480, 425, 64, 182, 195.6, gold=(3, 4, 5, 6), t=t)
    cap(tx, '越怕受伤', 1480, 330, 72, 196, 225, t=t)
    cap(tx, '越要装作不怕', 1480, 435, 72, 200, 225, gold=(4, 5), t=t)
    return sh, P, 0.6, 0.14 * pulse(t, T(128), 0.3) + 0.12 * pulse(t, T(152), 0.4) + 0.1 * pulse(t, T(204), 0.4)


def _count():
    for key, fn, tt in (('drop', drop_scene, T(79)), ('run', run_scene, T(127)), ('road', road_scene, T(225))):
        _COUNTS[key] = (10 ** 6, 10 ** 6)
        tx = Text(PF); sh = None
        import builtins
        orig = Shot.__init__
        cnt = {}
        def spy(self, *a, **k):
            orig(self, *a, **k); cnt['cv'] = self.cv
        Shot.__init__ = spy
        try: fn(tt, tt / E8, tx)
        finally: Shot.__init__ = orig
        c = cnt['cv'].cnt; _COUNTS[key] = (c['bg'], c['fg'])


def frame(t):
    if not _COUNTS: _count()
    n = t / E8; tx = Text(PF)
    if n < DROP: sh, P, glow, flash = hook(t, n, tx)
    elif n < 80: sh, P, glow, flash = drop_scene(t, n, tx)
    elif n < 128: sh, P, glow, flash = run_scene(t, n, tx)
    else: sh, P, glow, flash = road_scene(t, n, tx)
    img = sh.cv.composite(P.BG * 0.6, flash, glow=glow) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    img = tx.blend(np.clip(img, 0, 1.6).astype(np.float32))
    img *= ramp(t, 0, 0.15) * (1 - ramp(t, T(END) - 1.2, T(END) - 0.05))
    return np.clip(img * 255, 0, 255).astype(np.uint8)


# ================================================================ audio
def build_audio(music, out, duration):
    phase, e8 = R.grid(music); st = phase + MUSIC_START * e8; dr = T(DROP)
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, 'a.wav'); b = os.path.join(tmp, 'b.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.4f}', '-t', f'{dr:.4f}', '-i', music, '-af', 'lowpass=f=900,volume=0.55,afade=t=in:d=0.3', '-ac', '1', '-ar', str(sfx.SR), a], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st + dr:.4f}', '-t', f'{duration - dr:.4f}', '-i', music, '-af', f'afade=t=out:st={duration - dr - 1.5:.3f}:d=1.5', '-ac', '1', '-ar', str(sfx.SR), b], check=True)
    import wave
    def rd(p):
        w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mus = np.concatenate([rd(a), rd(b)])
    thump = lambda: (np.sin(2 * np.pi * 55 * np.arange(int(0.4 * sfx.SR)) / sfx.SR) * np.exp(-np.arange(int(0.4 * sfx.SR)) / sfx.SR * 9)).astype(np.float32)
    cues = [(T(0), thump(), 0.6), (T(2), thump(), 0.5), (T(16.5), sfx.whoosh(0.6), 0.25), (T(20), sfx.burn(1.1), 0.55), (T(26), sfx.chime(990, 1.4), 0.25),
            (T(29), sfx.chime(1320, 1.2), 0.15), (T(DROP) - 1.9, sfx.riser(1.9), 0.65), (T(DROP), sfx.impact(1.8), 0.9), (T(DROP + 1), sfx.sparkle(1.6, 16), 0.3),
            (T(58), sfx.whoosh(0.8, up=False), 0.3), (T(80) - 0.25, sfx.whoosh(0.6, heavy=True), 0.5), (T(104), sfx.whoosh(0.5), 0.2),
            (T(116), sfx.impact(1.0), 0.45), (T(116), sfx.burn(0.6), 0.25), (T(128) - 0.25, sfx.whoosh(0.6, heavy=True), 0.45),
            (T(152), sfx.chime(784, 1.6), 0.3), (T(176), sfx.whoosh(0.7), 0.3), (T(182), sfx.riser(1.2), 0.2), (T(186), sfx.impact(0.8), 0.25),
            (T(204), sfx.sparkle(1.4, 14), 0.35), (T(204), sfx.chime(1568, 1.2), 0.2)]
    fx = sfx.mix(cues, duration); n = min(len(mus), len(fx)); mix = mus[:n] * 0.9 + fx[:n]
    sfx.write_wav(out, mix / max(1.0, np.abs(mix).max() / 0.97))


def worker(a, b, path, fps):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(frame(i / fps).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--stills'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--music', default=os.path.join(HERE, '..', '..', 'media', 'Vibecoding_music.mp3'))
    args = ap.parse_args()
    if args.stills:
        os.makedirs(args.out, exist_ok=True)
        for s in args.stills.split(','): cv2.imwrite(os.path.join(args.out, f'{float(s):06.2f}.jpg'), frame(float(s)), [cv2.IMWRITE_JPEG_QUALITY, 90])
        return
    dur = T(END); N = int(dur * args.fps); k = 2; tmp = tempfile.mkdtemp(); t0 = time.time()
    cuts = [N * i // k for i in range(k + 1)]; parts = [os.path.join(tmp, f'p{i}.mp4') for i in range(k)]
    ps = [Process(target=worker, args=(cuts[i], cuts[i + 1], parts[i], args.fps)) for i in range(k)]
    for p in ps: p.start()
    for p in ps: p.join()
    with open(os.path.join(tmp, 'l.txt'), 'w') as f: f.writelines(f"file '{p}'\n" for p in parts)
    v = os.path.join(tmp, 'v.mp4'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', v], check=True)
    au = os.path.join(tmp, 'a.wav'); build_audio(args.music, au, dur)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-i', au, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', args.out], check=True)
    print(f'wrote {args.out} ({dur:.1f}s) in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
