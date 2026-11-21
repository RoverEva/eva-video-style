#!/usr/bin/env python3
"""白羊座的内心世界 · 第一分钟 v4 —— animated from the approved 24-frame storyboard (storyboard_min1.py)
with the Aries protagonist (aries_char.py).

Every shot is grown stroke by stroke (GrowCanvas), the camera never stops, and every caption line gets its
own action: the hesitators and the dash, the 明天 page he leaps through, the wall he stops and splits with a
point, the time-freeze, the person turning away, the armour, the trembling heart behind the crack.

  python3 template/longform/first_minute_v4.py --out out/long/v4/白羊座_第一分钟_v4.mp4 [--stills 5,14.2]
"""
import argparse, math, os, subprocess, sys, tempfile, time
from contextlib import contextmanager
from multiprocessing import Process
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import W, H, Palette, Cam, flame, Text, F, SERIF_B, SERIF_BL, lerp, cl, ramp, eo, eio, pulse, pop
import zodiac_signs  # noqa
from vis import heart_pts
import first_minute as FM
from first_minute import Shot, drift, stars_live, rain_live, flame_shape, cap, T, E8, _COUNTS, walk_pose
from story_frames import figure, glint, milkyway, meteor, godrays, sp, solid, lamp, BLACK
from aries_char import draw_aries, POSE
import sfx
import render_long as R

PF, PV = Palette('fire'), Palette('violet')
MUSIC_START, DROP, END = 12, 52, 226


# pen growth: instant strokes must not consume schedule slots; softer pen tips so many growing strokes don't blob
def _f(self):
    if self.instant or self.mode not in self.sched: return 1.0
    k = self.cnt[self.mode]; self.cnt[self.mode] += 1
    t0, dt, dur = self.sched[self.mode]
    return cl((self.t - t0 - k * dt) / dur)


def _path(self, pts, col, a=1., th=2., frac=1., smooth=True, closed=False, layer=None):
    f = self._f()
    if f <= 0: return
    g = eio(f)
    FM.Canvas.path(self, pts, col, a, th, frac * g, smooth, closed, layer)
    if g < 1 and layer is None and len(pts) > 1:
        P = FM.spline(pts, closed=closed) if smooth and len(pts) > 2 else np.array(pts, float)
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
        L = cum[-1] * frac * g; k = int(np.clip(np.searchsorted(cum, L), 1, len(P) - 1)); r = (L - cum[k - 1]) / max(seg[k - 1], 1e-6)
        tip = P[k - 1] + (P[k] - P[k - 1]) * r
        FM.Canvas.circle(self, tuple(tip), th * 0.7, PF.WARM, a, fill=True); FM.Canvas.glow(self, tuple(tip), 5 + 1.5 * th, PF.GOLD, 0.45 * a)


FM.GrowCanvas._f = _f
FM.GrowCanvas.path = _path


@contextmanager
def inst(cv):
    o = cv.instant; cv.instant = True
    try: yield
    finally: cv.instant = o


# ---------------------------------------------------------------- pose helpers
SW = (('uaF', 'uaB'), ('faF', 'faB'), ('thF', 'thB'), ('shF', 'shB'), ('hF', 'hB'))


def pose(name, **kw): p = dict(POSE[name]); p.update(kw); return p


def mirror(p):
    q = dict(p)
    for a, b in SW: q[a], q[b] = p[b], p[a]
    return q


def mix(p, q, w):
    r = {}
    for k in set(p) | set(q):
        a, b = p.get(k, q.get(k)), q.get(k, p.get(k))
        if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool): r[k] = a + (b - a) * w
        elif isinstance(a, tuple): r[k] = tuple(x + (y - x) * w for x, y in zip(a, b))
        else: r[k] = a if w < 0.5 else b
    return r


def run_cycle(u, base='run'):
    w = 0.5 - 0.5 * math.cos(2 * math.pi * u); p = POSE[base]
    return mix(p, mirror(p), w)


WALK = dict(POSE['hero'], uaF=18, faF=26, uaB=-16, faB=-6, thF=18, shF=4, thB=-16, shB=-22, hF='open', hB='open', wind=(-0.5, 0.1))


def walk_cycle(u, **kw):
    w = 0.5 - 0.5 * math.cos(2 * math.pi * u); p = dict(WALK, **kw)
    return mix(p, mirror(p), w)


# ---------------------------------------------------------------- set pieces
def heart_live(cv, c, s, P, a=1.0, glow=1.0, beat=0.0):
    s = s * (1 + 0.12 * beat)
    hp = [(c[0] + s * u, c[1] + s * v) for u, v in heart_pts(0, 0, 1.0, 60)]
    cv.poly(hp, BLACK, 1.0); cv.poly(hp, P.WARM * 0.45, a); cv.path(hp + [hp[0]], P.WARM, a, 3.0, smooth=False)
    cv.glow(c, s * 1.6, P.GOLD, (0.6 + 0.4 * beat) * a * glow)


def sparks_live(cv, c, t, n, r0, r1, P, a=1.0, seed=1, ang=(0, 2 * math.pi), speed=1.0, life=0.7):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        q = rr.uniform(*ang); ph = rr.uniform(0, 1); v = ((t * speed / life) + ph) % 1
        d0 = r0 + (r1 - r0) * v; L = 14 + 30 * (1 - v)
        p0 = (c[0] + d0 * math.cos(q), c[1] + d0 * math.sin(q) + 120 * v * v); p1 = (p0[0] + L * math.cos(q), p0[1] + L * math.sin(q))
        cv.path([p0, p1], P.WARM if rr.random() < 0.6 else P.GOLD, a * (1 - v) * rr.uniform(0.6, 1), rr.uniform(1.2, 2.4), smooth=False)


def burst(cv, c, k, n, R_, P, a=1.0, seed=2, ang=(0, 2 * math.pi), grav=0.0):
    """one-shot explosion, k in 0..1"""
    if k <= 0 or k >= 1: return
    rr = np.random.default_rng(seed)
    for _ in range(n):
        q = rr.uniform(*ang); r = R_ * eo(k) * rr.uniform(0.3, 1); L = 30 * (1 - k) + 6
        p = (c[0] + r * math.cos(q), c[1] + r * math.sin(q) + grav * k * k)
        cv.path([p, (p[0] + L * math.cos(q), p[1] + L * math.sin(q))], P.WARM if rr.random() < 0.6 else P.GOLD, a * (1 - k), 2.2, smooth=False)


def speedlines(cv, P, t, y0, y1, n=40, v=2600, a=0.5, seed=3):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        y = rr.uniform(y0, y1); L = rr.uniform(120, 420); x = (rr.uniform(0, W + 600) - v * t) % (W + 600) - 300
        cv.path([(x, y), (x + L, y)], P.LINE, a * rr.uniform(0.3, 1), rr.uniform(0.8, 1.8), smooth=False)


def ground(cv, y, P, a=0.6, x0=-400, x1=W + 400): cv.path([(x0, y), (x1, y)], P.LINE, a, 1.6, smooth=False)


def ground_marks(cv, P, y, t, v, a=0.5, seed=4):
    rr = np.random.default_rng(seed)
    for i in range(26):
        x = (rr.uniform(0, W + 400) - v * t) % (W + 400) - 200; L = rr.uniform(20, 90)
        cv.path([(x, y + 14 + rr.uniform(0, 60)), (x + L, y + 14 + rr.uniform(0, 60))], P.LINE, a * rr.uniform(0.2, 0.8), 1.2, smooth=False)


def cal_page(cv, tx, cam, c, w, h, txt, P, a=1.0, rot=0.0, burn=0.0, tcol=(235, 230, 220)):
    cs, sn = math.cos(rot), math.sin(rot)
    Rp = lambda x, y: (c[0] + x * cs - y * sn, c[1] + x * sn + y * cs)
    box = [Rp(-w / 2, -h / 2), Rp(w / 2, -h / 2), Rp(w / 2, h / 2), Rp(-w / 2, h / 2)]
    cv.poly(box, BLACK, 1.0); cv.poly(box, P.SOFT * 0.05, a); cv.path(box + [box[0]], P.SOFT, a, 2.4, smooth=False)
    cv.path([Rp(-w / 2, -h / 2 + h * 0.22), Rp(w / 2, -h / 2 + h * 0.22)], P.WARM, a, 2, smooth=False)
    for k in (-0.3, 0.3): cv.circle(Rp(w * k, -h / 2 - 6), 8, P.LINE, a, 2)
    if txt:
        q = cam([(c[0], c[1] + h * 0.12)])[0]
        tx.chars(txt, q[0], q[1], F(SERIF_BL, max(8, int(h * 0.3 * cam.s))), tcol, 1, 0, 99, stagger=0)


def wall(cv, x, y_top, y_bot, w, P, a=1.0):
    if y_bot - y_top < 4: return
    pts = [(x - w / 2, y_bot), (x - w / 2, y_top), (x + w / 2, y_top), (x + w / 2, y_bot)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.LINE * 0.06, a); cv.path(pts, P.LINE, a, 2.4, smooth=False)
    for i, yy in enumerate(np.arange(y_top + 50, y_bot, 50)):
        cv.path([(x - w / 2, yy), (x + w / 2, yy)], P.LINE, 0.35 * a, 1.2, smooth=False)
        off = 0 if i % 2 else 45
        for xx in np.arange(x - w / 2 + off, x + w / 2, 90): cv.path([(xx, yy - 50), (xx, yy)], P.LINE, 0.3 * a, 1.1, smooth=False)


def cracks(cv, c0, k, P, a=1.0, seed=2):
    rr = np.random.default_rng(seed)
    for b in range(6):
        p = np.array(c0, float); seg = [tuple(p)]; ang = rr.uniform(-0.9, 0.9)
        for _ in range(7):
            ang += rr.uniform(-0.5, 0.5); p = p + np.array([math.cos(ang), math.sin(ang)]) * rr.uniform(40, 80); seg.append(tuple(p))
        cv.path(seg, P.WARM, a, 3, frac=k, smooth=False); cv.path(seg, P.GOLD, 0.6 * a, 12, frac=k, smooth=False, layer=cv.F)


def bolt(cv, p0, p1, P, a=1.0, seed=7, col=None):
    rr = np.random.default_rng(seed); col = P.GOLD if col is None else col
    pts = [p0]
    for k in range(1, 9):
        u = k / 9; pts.append((p0[0] + (p1[0] - p0[0]) * u + rr.uniform(-40, 40), p0[1] + (p1[1] - p0[1]) * u + rr.uniform(-20, 20)))
    pts.append(p1)
    cv.path(pts, P.HI, a, 4, smooth=False); cv.path(pts, col, 0.5 * a, 10, smooth=False, layer=cv.F)
    for k in (3, 6): q = pts[k]; cv.path([q, (q[0] + rr.uniform(-120, 120), q[1] + rr.uniform(40, 120))], col, 0.6 * a, 2, smooth=False)


def qmarks(tx, cam, xs, y, t, t0, step):
    for i, x in enumerate(xs):
        t1 = t0 + i * step
        if t < t1: continue
        k = pop(t, t1, 0.25); q = cam([(x, y - 18 * math.sin((t - t1) * 3 + i))])[0]
        tx.chars('?', q[0], q[1], F(SERIF_BL, int(54 * cam.s * (1 + 0.4 * k))), (220, 215, 205), 1, 0, 99, stagger=0)


# ================================================================ scenes: fn(t, n, tx) -> (sh, P, glow, flash)
def sh_for(key, t, m0, cam, bg=1.2, fg=4.0, dur=0.6):
    return Shot(cam, t, T(m0), key, bg_span=bg, fg_span=fg, dur=dur)


def s_spark(t, n, tx):                                   # 0 – 6 : spark -> first flame
    s = lerp(1.0, 1.35, eio(ramp(n, 0, 6))); ds, dx, dy = drift(t, 0, 0.4)
    sh = sh_for('spark', t, 0, Cam(s * ds, 960 + dx, 580 + dy), 0.8, 1.6); cv = sh.cv; P = PF; c = (960, 600)
    with inst(cv):
        rr = np.random.default_rng(1)
        for i in range(50):
            x, y = rr.uniform(700, 1220), rr.uniform(380, 840); ph = rr.uniform(0, 6.3)
            cv.circle((x + 6 * math.sin(t * 0.7 + ph), y - (t * 8 + ph * 20) % 60), rr.uniform(0.8, 2), P.WARM, 0.45 * (0.5 + 0.5 * math.sin(t * 2 + ph)), fill=True)
        for p0 in (0, 2):
            if T(p0) <= t < T(p0) + 1.2: k = (t - T(p0)) / 1.2; cv.circle(c, 20 + 300 * eo(k), P.GOLD, (1 - k) * 0.7, 1.4)
        r = 6 * (1 + 0.5 * pulse(t, T(0), 0.3) + 0.5 * pulse(t, T(2), 0.3))
        cv.circle(c, r, P.WARM, 1, fill=True); cv.glow(c, 60, P.GOLD, 1.0); glint(cv, c, 40 + 30 * pulse(t, T(0), 0.5), P.WARM, 1, 0.2)
        if n >= 3: flame_shape(cv, (c[0], c[1] - 10), 60 + 110 * eo(ramp(n, 3, 6)), P, eio(ramp(n, 3, 4.5)), t)
    cap(tx, '他的心里', 960, 230, 72, 1, 15.6, 1, t=t)
    return sh, P, 0.6, 0.0


def s_face(t, n, tx):                                    # 6 – 16 : the flame becomes his hair; profile grows
    s = lerp(1.0, 1.1, eio(ramp(n, 6, 16))); ds, dx, dy = drift(t, T(6), 0.5)
    sh = sh_for('face', t, 6, Cam(s * ds, 900 + dx, 540 + dy), 1.6, 2.2); cv = sh.cv; P = PF
    p = pose('hero', mouth='flat', brow='calm', wind=(-0.6 + 0.1 * math.sin(t * 2), 0.1))
    draw_aries(cv, 900, 1080 + 2000 * 0.6, 2000, p, P=P, rim=(1, 0.3), heart=0)
    with inst(cv):
        for k in range(5): flame(cv, 600 + k * 120, 380 - 40 * (k % 2) + 8 * math.sin(t * 6 + k), 150 + 20 * math.sin(t * 5 + k), P.GOLD, 0.3, layer=cv.F)
        sparks_live(cv, (900, 360), t, 30, 60, 520, P, 0.7, 4, (-math.pi * 0.95, -math.pi * 0.05), 0.6, 1.2)
    cap(tx, '住着一团火', 1500, 800, 64, 6, 15.6, 0.5, (3, 4), t=t)
    cap(tx, '他的心里', 1500, 710, 52, 6, 15.6, 0, t=t)
    return sh, P, 0.6, 0.0


def s_touch(t, n, tx):                                   # 16 – 24 : a finger touches; it ignites
    shake = 14 * pulse(t, T(20), 0.35) * math.sin(t * 90)
    s = lerp(1.15, 1.0, eo(ramp(n, 20, 22))) if n >= 20 else lerp(1.0, 1.15, eio(ramp(n, 16, 20)))
    sh = sh_for('touch', t, 16, Cam(s, 1000 + shake, 580 + shake * 0.6), 0.6, 1.0); cv = sh.cv; P = PF; c = (1080, 600)
    if n >= 20: sh.roll = -3 * pulse(t, T(20), 0.8)
    hx = lerp(-200, 0, eo(ramp(n, 16, 19))) - (lerp(0, 260, eo(ramp(n, 20, 21.5))) if n >= 20 else 0)
    hand = [(hx + a_, b_) for a_, b_ in [(-200, 520), (560, 540), (720, 552), (860, 566), (880, 586), (720, 590), (560, 610), (-200, 640)]]
    solid(cv, sp(hand, 4), P.LINE, 1.0, 2.2, 0.04)
    cv.path(sp([(hx + 720, 552), (hx + 800, 548), (hx + 870, 566)], 4), P.LINE, 0.6, 1.2)
    with inst(cv):
        if n < 20:
            flame_shape(cv, c, 170 * (1 + 0.04 * math.sin(t * 9)) * (1 + 0.25 * pop(t, T(19), 0.3)), P, 1.0, t)
            if n > 18.5: glint(cv, (hx + 880, 580), 30 * pop(t, T(19), 0.4) + 10, P.WARM, 1)
        else:
            k = ramp(t, T(20), T(20) + 1.4); h = lerp(520, 330, eo(ramp(n, 20, 23)))
            flame_shape(cv, c, h * (1 + 0.04 * math.sin(t * 9)), P, 1.0, t)
            for j, r_ in enumerate((180, 300, 440)):
                kk = cl(k * 1.4 - j * 0.15); cv.circle(c, r_ * eo(kk) + 20, P.GOLD, (1 - kk) * 0.9, 3 - j * 0.6)
            burst(cv, c, k, 160, 900, P, 1.0, 6)
            godrays(cv, c, np.linspace(0, 2 * math.pi, 18) + t * 0.2, 1100, P.GOLD, 0.1 * (1 - 0.6 * k))
            sparks_live(cv, (c[0], c[1] - 80), t, 40, 40, 600, P, 0.8, 7, (-math.pi * 0.9, -math.pi * 0.1), 0.6, 1.0)
    cap(tx, '一碰', 960, 230, 76, 16, 19.9, 1, t=t)
    cap(tx, '就燃', 960, 290, 130, 20, 23.6, 0.25, 'all', t=t)
    return sh, P, 0.6, 0.3 * pulse(t, T(20), 0.4)


def s_heart(t, n, tx):                                   # 24 – 40 : flames part; the soft heart
    s = lerp(1.0, 1.25, eio(ramp(n, 24, 40))); ds, dx, dy = drift(t, T(24), 0.6)
    sh = sh_for('heart', t, 24, Cam(s * ds, 960 + dx, 600 + dy), 1.2, 3.0); cv = sh.cv; P = PF; c = (960, 610)
    part = eio(ramp(n, 24, 28))
    with inst(cv):
        for sd in (-1, 1):
            for k in range(6):
                x = 960 + sd * (lerp(60, 260, part) + k * lerp(40, 120, part))
                flame(cv, x, 1020, (520 - k * 50) * (1 + 0.05 * math.sin(t * 7 + k)), P.GOLD, 0.3 - k * 0.03)
        rr = np.random.default_rng(3)
        for i in range(14):
            sh.bokeh((rr.uniform(0, W) + 30 * math.sin(t * 0.3 + i), rr.uniform(0, H)), rr.uniform(20, 70), P.GOLD * 0.6, 0.35)
        if n >= 28:
            for j in range(3): cv.circle(c, 160 + 40 * j + 10 * math.sin(t * 2 + j), P.WARM, 0.18, 1.0)
    if n >= 27:
        heart_live(cv, c, 140, P, eio(ramp(n, 27, 29)), 1.0, pulse(t, FM.quarter(t), 0.25))
        with inst(cv):
            if n >= 29: glint(cv, (c[0] + 70, c[1] - 80), 26 + 18 * pulse(t, FM.quarter(t), 0.4), P.WARM, 1)
    cap(tx, '可火的最中间', 960, 170, 68, 24, 39.6, 0.5, t=t)
    cap(tx, '藏着一颗很软很软的心', 960, 260, 68, 28, 39.6, 0.5, (4, 5, 6, 7), t=t)
    return sh, P, 0.6, 0.0


def s_cover(t, n, tx):                                   # 40 – 52 : a gauntlet closes over it; dive in
    s = 1.0 if n < 47 else 1 + 6 * eio(ramp(n, 47, 52)) ** 2.2
    ds, dx, dy = drift(t, T(40), 0.4)
    sh = sh_for('cover', t, 40, Cam(s * ds, 960 + dx, 640 + dy), 0.4, 1.0); cv = sh.cv; P = PF; c = (960, 640)
    heart_live(cv, c, 120, P, 1.0, lerp(1.0, 0.4, ramp(n, 41, 44)), pulse(t, FM.quarter(t), 0.25))
    yh = lerp(-260, 400, eo(ramp(n, 40, 43)))
    if n >= 46: yh = lerp(400, -500, eio(ramp(n, 46, 49)))
    hand = [(560, yh - 20), (1360, yh - 20), (1380, yh + 120), (1300, yh + 200), (620, yh + 200), (540, yh + 120)]
    solid(cv, sp(hand, 4, True), P.SOFT, 1.0, 2.4, 0.05)
    for k in range(4): cv.path([(700 + k * 170, yh), (700 + k * 170, yh + 190)], P.SOFT, 0.5, 1.2, smooth=False)
    cv.path([(560, yh), (1360, yh)], P.GOLD, 1, 3, smooth=False)
    with inst(cv):
        if 42 < n < 47: godrays(cv, (960, yh + 200), [math.pi / 2 + q + 0.05 * math.sin(t * 3) for q in (-0.5, -0.2, 0.2, 0.5)], 600, P.GOLD, 0.12, 0.02)
    cap(tx, '他从不让人看见', 960, 200, 72, 40, 46.6, 0.5, t=t)
    return sh, P, 0.6, ramp(n, 50.5, 52) * 0.9


HERO_X, HERO_GY, HERO_H = 620, 960, 640


def s_drop(t, n, tx):                                    # 52 – 80 : match cut to the full hero; title
    p = pose('hero', mouth='smile', brow='calm', wind=(-0.9 + 0.15 * math.sin(t * 2.2), -0.2 + 0.05 * math.sin(t * 3)))
    J = draw_aries.__globals__['skeleton'](HERO_X, HERO_GY, HERO_H, p, 1)
    chest = J['sc'] - J['up'] * 0.075 * HERO_H
    u = eio(ramp(n, DROP, DROP + 6))
    s = lerp(8.0, 1.0, u) * (1 + 0.05 * ramp(n, DROP + 6, 80)); ds, dx, dy = drift(t, T(DROP) + 1.6, 0.8 * u)
    cam = Cam(s * ds, lerp(chest[0], 960, u) + dx, lerp(chest[1], 540, u) + dy)
    sh = sh_for('drop', t, DROP, cam, 2.2, 4.5, 0.6); cv = sh.cv; P = PF
    with inst(cv):
        stars_live(cv, P, t, 200, 760, 7, a=u)
        milkyway(cv, P, (-200, 140), (W + 200, 420), 140, 6, 0.7 * u)
        if T(64) < t < T(64) + 1.2: k = (t - T(64)) / 1.2; meteor(cv, (lerp(1700, 1100, k), lerp(80, 300, k)), math.atan2(220, -600), 260, P.WARM, 1 - k)
        godrays(cv, (HERO_X, 560), np.linspace(-math.pi, 0, 12) + 0.05 * math.sin(t), 900, P.GOLD, 0.06 * u)
        burst(cv, chest, ramp(t, T(DROP), T(DROP) + 1.5), 80, 900, P, 1.0, 12)
    cons = [(1180, 260), (1330, 210), (1460, 250), (1520, 330)]
    cv.path(cons, P.GOLD, 0.6, 1.4, smooth=False)
    for q in cons: cv.circle(q, 4, P.WARM, 1, fill=True)
    ground(cv, HERO_GY, P, 0.5)
    draw_aries(cv, HERO_X, HERO_GY, HERO_H, p, P=P, rim=(-1, -0.3), heart=1 + 0.15 * pulse(t, FM.quarter(t), 0.25))
    with inst(cv):
        for i, q in enumerate(cons): glint(cv, q, 14 + 10 * pulse(t, FM.quarter(t) + i * E8 * 0.5, 0.5), P.WARM, 1)
    with inst(cv):
        if n < DROP + 4: heart_live(cv, chest, 0.026 * HERO_H, P, 1 - ramp(n, DROP + 3, DROP + 4), 1.0)
    cap(tx, '白羊座的内心世界', 1340, 560, 96, DROP + 1, 79.6, 0.5, 'all', t=t, col=P.HI)
    return sh, P, 0.6, 0.9 * (1 - ramp(t, T(DROP), T(DROP) + 0.5))


def s_start(t, n, tx):                                   # 80 – 86 : the hesitators; he crouches
    s = lerp(1.08, 1.0, eio(ramp(n, 80, 86))); ds, dx, dy = drift(t, T(80), 0.4)
    cam = Cam(s * ds, 960 + dx - 40 * ramp(n, 80, 86), 560 + dy)
    sh = sh_for('start', t, 80, cam, 1.4, 1.4); cv = sh.cv; P = PF
    ground(cv, 900, P, 0.6)
    cv.path([(150, 905), (1770, 905)], P.WARM, 0.7, 2, smooth=False)
    xs = (380, 560, 1060, 1240, 1420)
    for k, x in enumerate(xs): figure(cv, x, 900, 300, 'stand', P.LINE * 0.9, 0.55, d=1 if (k + int(n / 2)) % 2 else -1, P=P, th=1.6)
    crouch = eio(ramp(n, 83, 86))
    p = mix(pose('hero', mouth='grit', brow='fierce'), pose('burst', mouth='grit'), 0.55 + 0.45 * crouch)
    with inst(cv):
        draw_aries(cv, 800, 900, 380, p, P=P, rim=(1, -0.2))
    with inst(cv):
        if crouch > 0: cv.glow((840, 820), 60 + 40 * crouch, P.GOLD, 0.4 * crouch)
    qmarks(tx, cam, xs, 560, t, T(81), E8)
    cap(tx, '别人还在犹豫', 960, 200, 64, 82, 95.6, t=t)
    return sh, P, 0.6, 0.0


def s_dash(t, n, tx):                                    # 86 – 96 : he's gone
    lt = t - T(86); v = 1400
    shake = 10 * pulse(t, T(86), 0.4) * math.sin(t * 80)
    cam = Cam(1.0 + 0.03 * math.sin(t * 1.3), 960 + shake, 560 + shake * 0.5)
    sh = sh_for('dash', t, 86, cam, 0.9, 1.2); cv = sh.cv; P = PF
    x = lerp(800, 1180, eo(ramp(lt, 0, 0.6)))
    u = lt / 0.42
    p = run_cycle(u) if lt > 0.15 else pose('burst', mouth='shout')
    gy = 920 - 22 * abs(math.sin(math.pi * u))
    ground(cv, 920, P, 0.6)
    for k, x0 in enumerate((380, 560, 1060, 1240, 1420)):
        xx = x0 - v * max(0, lt - 0.1) * (0.4 if k < 2 else 1)
        if -200 < xx < W + 200: figure(cv, xx, 920, 300 if k >= 2 else 240, 'stand', P.LINE * 0.9, 0.45, d=1, P=P, th=1.5)
    with inst(cv):
        draw_aries(cv, x, gy, 440, p, P=P, rim=(1, -0.3))
    with inst(cv):
        speedlines(cv, P, t, 260, 900, 40, 2600, 0.45 * ramp(lt, 0.1, 0.5))
        ground_marks(cv, P, 920, t, 1600)
        for k in range(9):
            fx = x - 120 - k * 70; fl = (60 + k * 12) * (1 + 0.15 * math.sin(t * 12 + k))
            flame(cv, fx, 870 - k * 6, fl, P.GOLD, (0.3 - 0.025 * k) * ramp(lt, 0.0, 0.3), lean=-0.6)
        burst(cv, (800, 920), ramp(lt, 0, 1.0), 90, 420, P, 1.0, 8, (-math.pi, -math.pi * 0.55), 300)
        if lt < 0.6: cv.circle((800, 900), 40 + 400 * eo(lt / 0.6), P.GOLD, (1 - lt / 0.6) * 0.8, 2)
        if int(u * 2) != int((u - 0.07) * 2): pass
        k = (u * 2) % 1
        cv.circle((x - 30 - 200 * k, 925), 10 + 50 * k, P.LINE, 0.4 * (1 - k), 1.2)
    cap(tx, '别人还在犹豫', 1360, 200, 60, 82, 95.6, t=t)
    cap(tx, '他已经冲出去了', 1360, 284, 60, 86, 95.6, 0.5, (3, 4, 5), t=t)
    return sh, P, 0.6, 0.2 * pulse(t, T(86), 0.3)


def s_cal(t, n, tx):                                     # 96 – 112 : 明天 flies at him; he leaps through; 今天
    lt = t - T(96); cam = Cam(1.0 + 0.04 * ramp(n, 96, 112), 960 + 10 * math.sin(t * 0.5), 560)
    sh = sh_for('cal', t, 96, cam, 1.0, 1.6); cv = sh.cv; P = PF
    tl = T(100)  # leap moment
    ground(cv, 940, P, 0.5)
    # page: flies from depth toward him, then hangs and burns when he passes
    k = eio(ramp(t, T(96), tl - 0.1)); pc = (lerp(1500, 1000, k), lerp(380, 540, k)); sc = lerp(0.35, 1.0, k)
    burn = ramp(t, tl + 0.15, tl + 1.1)
    if burn < 1:
        cal_page(cv, tx, cam, pc, 360 * sc, 420 * sc, '明天' if burn < 0.35 else '', P, 1.0 - 0.6 * burn, lerp(0.5, 0.1, k) + 0.1 * math.sin(t * 3) * (1 - k))
    if burn > 0.3:
        g = eo(ramp(burn, 0.3, 1.0)); cal_page(cv, tx, cam, (1000, 540 - 40 * g), 380, 440, '今天', P, g, 0.0, tcol=(255, 214, 130))
    # runner: approaches, leaps through at tl, lands on the far side
    if t < tl - 0.25:
        x = lerp(380, 700, ramp(t, T(96), tl - 0.25)); p = run_cycle(lt / 0.42); gy = 940 - 20 * abs(math.sin(math.pi * lt / 0.42))
    elif t < tl + 0.9:
        a_ = ramp(t, tl - 0.25, tl + 0.9); x = lerp(700, 1350, a_); gy = 940 - 360 * math.sin(math.pi * a_)
        p = mix(pose('burst'), pose('leap'), eo(cl(a_ * 2))) if a_ < 0.5 else mix(pose('leap'), pose('skid', lean=6), eio((a_ - 0.5) * 2))
    else:
        x = 1350 + 260 * (t - tl - 0.9); p = run_cycle((t - tl) / 0.42); gy = 940 - 20 * abs(math.sin(math.pi * (t - tl) / 0.42))
    with inst(cv):
        draw_aries(cv, x, gy, 400, p, P=P, rim=(1, -0.4))
    with inst(cv):
        ground_marks(cv, P, 940, t, 900)
        for i in range(3):
            q = (1600 + i * 90 - 600 * lt * (0.3 + 0.2 * i), 280 + i * 140 + 30 * math.sin(t * 2 + i))
            if q[0] > -200: cal_page(cv, tx, cam, q, 110, 130, '', P, 0.35, -0.3 + i * 0.3 + t * 0.6 * (i - 1))
        if 0 < burn < 1:
            e = (1000, 540 + 220 - 440 * burn)
            for j in range(7): flame(cv, 820 + j * 60, e[1] + 10 * math.sin(t * 10 + j), 40 + 30 * ((j * 0.37) % 1), P.GOLD, 0.8)
            sparks_live(cv, (1000, e[1]), t, 40, 20, 260, P, 0.9, 5, (-math.pi, 0), 0.8, 0.8)
        burst(cv, (1000, 540), ramp(t, tl, tl + 1.0), 70, 520, P, 1.0, 9)
    cap(tx, '想做的事', 960, 170, 64, 96, 111.6, t=t)
    cap(tx, '今天就要开始', 960, 258, 64, 100, 111.6, 0.5, (0, 1, 4, 5), t=t)
    return sh, P, 0.6, 0.25 * pulse(t, tl, 0.35)


def s_wall(t, n, tx):                                    # 112 – 130 : the wall; skid; point; lightning
    lt = t - T(112); shake = 12 * pulse(t, T(112) + 0.5, 0.5) * math.sin(t * 70) + 16 * pulse(t, T(117), 0.4) * math.sin(t * 95)
    s = lerp(1.0, 1.12, eio(ramp(n, 118, 130)))
    cam = Cam(s, 1040 + shake + 60 * ramp(n, 118, 130), 560 + shake * 0.5 - 30 * ramp(n, 118, 130))
    sh = sh_for('wall', t, 112, cam, 1.0, 1.5); cv = sh.cv; P = PF
    ground(cv, 940, P, 0.6)
    top = lerp(940, 140, eo(ramp(lt, 0.0, 0.7)))
    wall(cv, 1440, top, 940, 520, P, 1.0)
    # skid: decelerate from the left
    a_ = eo(ramp(lt, 0.0, 0.9)); x = lerp(260, 840, a_)
    if t < T(115): p = run_cycle(lt / 0.42) if lt < 0.35 else pose('skid')
    else: p = mix(pose('skid'), pose('point'), eio(ramp(t, T(115), T(116))))
    with inst(cv):
        draw_aries(cv, x, 940, 440, p, P=P, rim=(1, -0.3))
    with inst(cv):
        if lt < 1.2:
            sparks_live(cv, (x + 60, 940), t, 50, 10, 220, P, 1 - ramp(lt, 0.9, 1.2), 10, (-math.pi * 0.95, -math.pi * 0.55), 1.4, 0.5)
            cv.path([(260, 946), (x + 40, 946)], P.WARM, 0.9 * (1 - ramp(lt, 0.9, 1.6)), 3, smooth=False)
        burst(cv, (1440, 940), ramp(lt, 0.0, 1.2), 60, 400, P, 0.7, 3, (-math.pi, 0), 300)
        if t >= T(116.6):
            kb = ramp(t, T(116.6), T(116.6) + 0.5)
            if kb < 1: bolt(cv, (1140, -200), (1200, 520), P, 1 - kb, int(t * 20) % 5)
            cracks(cv, (1185, 520), eo(ramp(t, T(116.8), T(116.8) + 1.4)), P, 1.0, 2)
            burst(cv, (1200, 520), ramp(t, T(116.8), T(116.8) + 1.2), 80, 500, P, 1.0, 11)
            if n > 120: godrays(cv, (1210, 520), np.linspace(-0.9, 0.9, 7) + 0.03 * math.sin(t * 2), 700, P.GOLD, 0.08 * ramp(n, 120, 124))
            if n > 121:
                rr = np.random.default_rng(5)
                for j in range(12):
                    t1 = T(121) + rr.uniform(0, 2.5); kk = t - t1
                    if kk > 0:
                        q = (rr.uniform(1200, 1680), rr.uniform(160, 600) + 900 * kk * kk)
                        if q[1] < 940: cv.path([(q[0] - 12, q[1]), (q[0] + 12, q[1] - 8), (q[0] + 8, q[1] + 10), (q[0] - 12, q[1])], P.LINE, 0.8, 1.4, smooth=False)
        if t > T(116): glint(cv, (x + 260, 940 - 440 * 0.62), 20 + 20 * pop(t, T(116.4), 0.4), P.WARM, 1)
    cap(tx, '不服的事', 600, 180, 64, 112, 127.6, t=t)
    cap(tx, '当场就要说清', 600, 268, 64, 116, 127.6, 0.5, (0, 1, 4, 5), t=t)
    return sh, P, 0.6, 0.55 * pulse(t, T(116.6), 0.25)


def s_freeze(t, n, tx):                                  # 130 – 134 : time freezes; crane up
    s = lerp(1.7, 1.0, eio(ramp(n, 130, 134))); ds, dx, dy = drift(t, T(130), 0.3)
    sh = sh_for('freeze', t, 130, Cam(s * ds, 960 + dx, lerp(700, 560, eio(ramp(n, 130, 134))) + dy), 0.8, 0.9); cv = sh.cv; P = PV
    cv.path(sp([(-200, 820), (960, 700), (W + 200, 820)], 8), P.LINE, 0.4, 1.4)
    draw_aries(cv, 960, 760, 150, pose('point', mouth='flat'), P=P, col=P.SOFT, heart=0.6)
    with inst(cv):
        rr = np.random.default_rng(4)
        for _ in range(70):
            c = (rr.uniform(200, 1720), rr.uniform(200, 900)); s_ = rr.uniform(4, 14); r0 = rr.uniform(0, 6) + 0.05 * t
            pts = [(c[0] + s_ * math.cos(r0 + q), c[1] + s_ * math.sin(r0 + q)) for q in (0, 2.1, 4.0)]
            cv.path(pts + [pts[0]], P.LINE, 0.6, 1.2, smooth=False)
        for k in range(3):
            cv.path([(960 + 70 * math.cos(q), 700 + 70 * (1 + k * 0.4) * math.sin(q) * 0.3 + k * 6) for q in np.linspace(0, 2 * math.pi, 50)], P.LINE, 0.25, 1, smooth=False)
        kk = ramp(t, T(130), T(130) + 1.0)
        if kk < 1: cv.circle((960, 700), 40 + 1400 * eo(kk), P.SOFT, (1 - kk) * 0.6, 2)
    cap(tx, '可你知道吗', 960, 200, 64, 130, 133.9, t=t, col=P.WHITE)
    return sh, P, 0.6, 0.3 * pulse(t, T(130), 0.3)


def s_ghosts(t, n, tx):                                  # 134 – 138 : afterimages of the whole run
    cam = Cam(1.0, lerp(900, 1020, ramp(n, 134, 138)), 540)
    sh = sh_for('ghosts', t, 134, cam, 0.5, 1.0); cv = sh.cv; P = PV
    ground(cv, 900, P, 0.5)
    for k in range(5):
        if n < 134 + k * 0.8: continue
        draw_aries(cv, 300 + k * 230, 900, 380, run_cycle(0.12 * k), P=P, col=P.SOFT, a=0.2 + 0.18 * k, heart=0.3 + 0.15 * k, th=1.8 + 0.15 * k)
    cap(tx, '可你知道吗', 1500, 200, 60, 134, 137.9, 0, t=t, col=P.WHITE)
    cap(tx, '跑得最快的人', 1500, 290, 60, 134, 137.9, 0.5, t=t, col=P.WHITE)
    return sh, P, 0.6, 0.0


def s_qmark(t, n, tx):                                   # 138 – 152 : stars join into a question mark
    s = lerp(1.0, 1.08, ramp(n, 138, 152)); cam = Cam(s, 960, lerp(600, 520, eio(ramp(n, 138, 152))))
    sh = sh_for('qmark', t, 138, cam, 1.0, 2.0); cv = sh.cv; P = PV
    ground(cv, 1000, P, 0.5)
    draw_aries(cv, 960, 1000, 220, pose('lookback', d=1), P=P, col=P.SOFT, heart=0.6)
    q = [(840, 360), (850, 260), (930, 200), (1030, 220), (1070, 300), (1020, 380), (960, 430), (960, 520)]
    with inst(cv):
        stars_live(cv, P, t, 200, 900, 2, 0.7)
        for i in range(len(q)):
            t1 = T(139) + i * E8
            if t < t1: continue
            glint(cv, q[i], 22 + 16 * pop(t, t1, 0.3), P.WARM, 1)
            if i > 0: cv.path([q[i - 1], q[i]], P.SOFT, 0.8, 1.6, frac=eo(ramp(t, t1, t1 + 0.2)), smooth=False)
        if t > T(139) + 9 * E8: glint(cv, (960, 610), 30 + 10 * math.sin(t * 4), P.WARM, 1)
    cap(tx, '跑得最快的人', 1460, 760, 56, 138, 151.6, 0, t=t, col=P.WHITE)
    cap(tx, '最怕的是什么？', 1460, 840, 56, 138, 151.6, 0.5, t=t, col=P.WHITE)
    return sh, P, 0.6, 0.0


def s_notlose(t, n, tx):                                 # 152 – 156 : walks past the finish; the medal drops
    lt = t - T(152); cam = Cam(1.0, 960 + 40 * lt, 540)
    sh = sh_for('notlose', t, 152, cam, 0.3, 0.5); cv = sh.cv; P = PF
    ground(cv, 940, P, 0.5)
    cv.path([(1000, 600), (1000, 940)], P.LINE, 0.6, 2, smooth=False); cv.path([(1600, 600), (1600, 940)], P.LINE, 0.6, 2, smooth=False)
    x = 900 + 300 * lt
    br = eo(ramp(lt, 0.15, 0.6))
    if br <= 0: cv.path(sp([(1000, 640), (1300, 660), (1600, 640)], 6), P.WARM, 0.9, 2.4)
    else:
        cv.path(sp([(1000, 640), (1300 - 140 * br, 660 + 60 * br), (1300 - 160 * br, 680 + 120 * br)], 6), P.WARM, 0.9, 2.4)
        cv.path(sp([(1600, 640), (1300 + 140 * br, 660 + 60 * br), (1300 + 160 * br, 680 + 140 * br)], 6), P.WARM, 0.9, 2.4)
    with inst(cv):
        draw_aries(cv, x, 940, 420, walk_cycle(lt / 0.9, mouth='flat'), P=P, rim=(-1, -0.3))
    with inst(cv):
        my = lerp(560, 900, ramp(lt, 0.2, 0.7) ** 2); sh.bokeh((420, my), 110, P.GOLD, 0.8); sh.bokeh((420, my), 60, P.WARM, 0.6)
    cap(tx, '不是输', 600, 260, 84, 152, 155.9, t=t)
    return sh, P, 0.6, 0.0


def s_turn(t, n, tx):                                    # 156 – 178 : the one he cares about turns away
    s = lerp(1.0, 1.12, eio(ramp(n, 156, 178))); cam = Cam(s, lerp(900, 960, ramp(n, 156, 178)), 560)
    sh = sh_for('turn', t, 156, cam, 1.6, 3.0); cv = sh.cv; P = PV
    ground(cv, 960, P, 0.4)
    lamp(cv, 1320, 960, 420, P, 0.9, -1)
    lt = t - T(156); fx = 1300 + 26 * max(0, lt - 1.0)
    figure(cv, fx, 960, 220, walk_pose(lt / 1.1) if lt > 1.0 else 'stand', P.LINE * 0.95, 0.75, d=1 if lt > 0.6 else -1, P=P, th=1.6)
    dim = lerp(1.0, 0.3, eio(ramp(n, 158, 166)))
    J = draw_aries(cv, 520, 1110, 900, pose('lookback', d=-1), d=-1, P=P, col=P.SOFT, heart=dim, rim=(1, -0.2))
    with inst(cv):
        rain_live(cv, P, t, 0.35 * ramp(n, 157, 162), 260, 0.12, 3, light=(1258, 560))
        c = J['chest']
        for j in range(16):
            ph = (t * 0.5 + j / 16) % 1
            if n > 159: cv.circle((c[0] + 40 * math.sin(j * 2.3) - 8 * ph, c[1] + 380 * ph), 2.4, P.WARM, (1 - ph) * 0.8 * ramp(n, 159, 162), fill=True)
    cap(tx, '不是输', 1380, 230, 60, 156, 175.6, 0, t=t, col=P.WHITE)
    cap(tx, '是在乎的人转身', 1380, 320, 64, 156, 175.6, 0.5, 'all', t=t, col=P.WHITE)
    return sh, P, 0.6, 0.0


def s_resolve(t, n, tx):                                 # 178 – 182 : turns back, fists close, chin up
    s = lerp(1.0, 1.1, eio(ramp(n, 178, 182))); cam = Cam(s, 920, 560)
    sh = sh_for('resolve', t, 178, cam, 0.8, 1.0); cv = sh.cv; P = PF
    k = eio(ramp(n, 179, 181))
    p = mix(pose('hero', mouth='sad', brow='sad', hF='open', hB='open'), pose('stand_arm'), k)
    draw_aries(cv, 900, 1080 + 260, 1100, p, P=P, rim=(1, -0.3), heart=0.6)
    with inst(cv): stars_live(cv, P, t, 120, 600, 3, 0.4)
    cap(tx, '所以他把自己', 1500, 300, 64, 178, 181.9, t=t)
    return sh, P, 0.6, 0.0


def s_armor(t, n, tx):                                   # 182 – 196 : armour assembles, plate by plate
    lt = t - T(182); s = lerp(1.15, 1.0, eio(ramp(n, 182, 196)))
    cam = Cam(s, 820 + 60 * math.sin(lt * 0.4), 600)
    sh = sh_for('armor', t, 182, cam, 1.0, 1.5); cv = sh.cv; P = PF
    ground(cv, 960, P, 0.5)
    arm = eio(ramp(n, 183, 193))
    with inst(cv):
        draw_aries(cv, 820, 960, 560, pose('hero', mouth='flat', brow='fierce', hF='fist', hB='fist'), P=P, armor=max(0.001, arm), rim=(1, -0.3))
    with inst(cv):
        c = (820, 620)
        for k in range(12):
            t1 = T(183) + k * E8 * 0.8; kk = eio(ramp(t, t1, t1 + 0.6)); q = k / 12 * 2 * math.pi
            r = 320 * (1 - kk)
            if kk >= 1: continue
            p_ = (c[0] + r * math.cos(q), c[1] + r * 0.8 * math.sin(q))
            pl = [(p_[0] + 26 * math.cos(q + s_ + t * 3), p_[1] + 18 * math.sin(q + s_ + t * 3)) for s_ in (0, 1.8, 3.2, 4.6)]
            cv.path(pl + [pl[0]], P.GOLD, 0.9, 2, smooth=False)
        for k in range(4):
            tb = T(184 + k * 2.6)
            if tb < t < tb + 0.4: glint(cv, (820 + 60 * math.cos(k * 2), 560 + 120 * math.sin(k * 1.3)), 40 * pop(t, tb, 0.3) + 10, P.WARM, 1)
        godrays(cv, (820, 500), np.linspace(-math.pi, 0, 10) + 0.04 * math.sin(t), 900, P.GOLD, 0.07 * arm)
    cap(tx, '所以他把自己', 1440, 300, 60, 182, 195.6, 0, t=t)
    cap(tx, '包装成刀枪不入', 1440, 390, 62, 182, 195.6, 0.5, (3, 4, 5, 6), t=t)
    return sh, P, 0.6, 0.25 * pulse(t, T(193), 0.35)


def s_bounce(t, n, tx):                                  # 196 – 200 : everything bounces off
    cam = Cam(1.0 + 0.02 * math.sin(t), 960, 560)
    sh = sh_for('bounce', t, 196, cam, 0.5, 0.6); cv = sh.cv; P = PF
    ground(cv, 960, P, 0.5)
    with inst(cv):
        draw_aries(cv, 900, 960, 560, pose('stand_arm'), P=P, armor=1.0, rim=(1, -0.3), heart=0.5)
    with inst(cv):
        rr = np.random.default_rng(6)
        for k in range(9):
            t1 = T(196) + k * 0.11 + rr.uniform(0, 0.05); q = rr.uniform(-math.pi, 0); hit = (900 + 120 * math.cos(q), 650 + 200 * math.sin(q) * 0.8)
            dirv = np.array([math.cos(q), math.sin(q)])
            if t < t1:
                d_ = (t1 - t) * 2200
                if d_ < 1600: p0 = np.array(hit) + dirv * d_; cv.path([tuple(p0), tuple(p0 + dirv * 120)], P.LINE, 0.8, 1.8, smooth=False)
            else:
                kk = ramp(t, t1, t1 + 0.7); refl = np.array([dirv[0], -abs(dirv[1])])
                p0 = np.array(hit) + refl * 900 * kk + np.array([0, 300 * kk * kk])
                cv.path([tuple(p0), tuple(p0 + refl * 60)], P.LINE, 0.7 * (1 - kk), 1.6, smooth=False)
                burst(cv, hit, ramp(t, t1, t1 + 0.4), 14, 80, P, 1.0, k)
    cap(tx, '越怕受伤', 1500, 300, 70, 196, 199.9, t=t)
    return sh, P, 0.6, 0.0


def s_end(t, n, tx):                                     # 200 – 226 : close-up smile; push into the crack
    lt = t - T(200)
    p = pose('hero', mouth='smile', brow='fierce', head=-8, wind=(-0.6 + 0.1 * math.sin(t * 2), 0.1))
    X, GY, HH = 780, 1080 + 1500 * 0.45, 1500
    J = draw_aries.__globals__['skeleton'](X, GY, HH, p, 1)
    c = J['sc'] - J['up'] * 0.075 * HH + np.array([20, 40])
    u = eio(ramp(n, 206, 222))
    cam = Cam(lerp(1.0, 2.6, u), lerp(960, c[0], u), lerp(540, c[1], u))
    sh = sh_for('end', t, 200, cam, 1.6, 2.4); cv = sh.cv; P = PF
    draw_aries(cv, X, GY, HH, p, P=P, armor=1.0, rim=(1, -0.3), heart=0)
    kc = eo(ramp(n, 205, 210))
    cr = [(c[0] - 20, c[1] - 110), (c[0] + 10, c[1] - 60), (c[0] - 15, c[1] - 10), (c[0] + 15, c[1] + 40), (c[0] - 5, c[1] + 100)]
    if kc > 0: cv.path(cr, P.WARM, 1, 3, frac=kc, smooth=False)
    with inst(cv):
        if kc > 0: cv.path(cr, P.GOLD, 0.7, 14, frac=kc, smooth=False, layer=cv.F)
        if n > 209:
            tremble = 2.5 * math.sin(t * 38) * ramp(n, 212, 216)
            heart_live(cv, (c[0] - 2 + tremble, c[1] - 10), 34, P, eio(ramp(n, 209, 211)), 1.0, pulse(t, FM.quarter(t), 0.2) * (1 + ramp(n, 214, 222)))
    cap(tx, '越怕受伤', 1480, 300, 70, 200, 225, 0, t=t)
    cap(tx, '越要装作不怕', 1480, 405, 70, 200, 225, 0.5, (4, 5), t=t)
    return sh, P, 0.6, 0.0


SCENES = [(0, 6, s_spark, 'spark'), (6, 16, s_face, 'face'), (16, 24, s_touch, 'touch'), (24, 40, s_heart, 'heart'), (40, 52, s_cover, 'cover'),
          (52, 80, s_drop, 'drop'), (80, 86, s_start, 'start'), (86, 96, s_dash, 'dash'), (96, 112, s_cal, 'cal'), (112, 130, s_wall, 'wall'),
          (130, 134, s_freeze, 'freeze'), (134, 138, s_ghosts, 'ghosts'), (138, 152, s_qmark, 'qmark'), (152, 156, s_notlose, 'notlose'),
          (156, 178, s_turn, 'turn'), (178, 182, s_resolve, 'resolve'), (182, 196, s_armor, 'armor'), (196, 200, s_bounce, 'bounce'), (200, END, s_end, 'end')]


def _count():
    orig = Shot.__init__
    for m0, m1, fn, key in SCENES:
        _COUNTS[key] = (10 ** 6, 10 ** 6); box = {}
        def spy(self, *a, **k):
            orig(self, *a, **k); box['cv'] = self.cv
        Shot.__init__ = spy
        try: fn(T(m1) - 0.02, m1 - 0.02 / E8, Text(PF))
        finally: Shot.__init__ = orig
        c = box['cv'].cnt; _COUNTS[key] = (c['bg'], max(c['fg'], 1))


def frame(t):
    if not _COUNTS: _count()
    n = t / E8; tx = Text(PF)
    for m0, m1, fn, key in SCENES:
        if n < m1 or fn is s_end: break
    sh, P, glow, flash = fn(t, n, tx)
    img = sh.cv.composite(P.BG * 0.6, flash, glow=glow) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    if sh.roll:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), sh.roll, 1.06); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    img = tx.blend(np.clip(img, 0, 1.6).astype(np.float32))
    img *= ramp(t, 0, 0.15) * (1 - ramp(t, T(END) - 1.0, T(END) - 0.05))
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
    # duck the music during the time-freeze and under the person turning away
    tt = np.arange(len(mus)) / sfx.SR
    duck = 1 - 0.75 * np.clip((tt - T(130)) / 0.1, 0, 1) * np.clip((T(138) - tt) / 0.4, 0, 1) - 0.35 * np.clip((tt - T(156)) / 0.3, 0, 1) * np.clip((T(178) - tt) / 0.5, 0, 1)
    mus = mus * duck
    thump = lambda d=0.4: (np.sin(2 * np.pi * 55 * np.arange(int(d * sfx.SR)) / sfx.SR) * np.exp(-np.arange(int(d * sfx.SR)) / sfx.SR * 9)).astype(np.float32)
    cues = [(T(0), thump(), 0.6), (T(2), thump(), 0.5), (T(3), sfx.burn(0.8), 0.2), (T(6), sfx.whoosh(0.9), 0.2),
            (T(19), sfx.tick(), 0.5), (T(20), sfx.burn(1.1), 0.6), (T(20), sfx.impact(1.0), 0.35), (T(24), sfx.whoosh(0.8), 0.25),
            (T(27), thump(), 0.45), (T(29), thump(), 0.4), (T(28), sfx.chime(990, 1.4), 0.2),
            (T(40), sfx.whoosh(0.5, up=False), 0.25), (T(43), thump(), 0.5), (T(45), thump(), 0.45),
            (T(DROP) - 1.9, sfx.riser(1.9), 0.65), (T(DROP), sfx.impact(1.8), 0.9), (T(DROP + 1), sfx.sparkle(1.6, 16), 0.3), (T(64), sfx.whoosh(0.6), 0.15),
            (T(81), sfx.tick(), 0.3), (T(82), sfx.tick(), 0.3), (T(83), sfx.tick(), 0.3), (T(84), sfx.tick(), 0.3), (T(85), sfx.riser(0.5), 0.3),
            (T(86), sfx.whoosh(0.7, heavy=True), 0.6), (T(86), sfx.impact(0.8), 0.4),
            (T(96), sfx.whoosh(0.5), 0.25), (T(100), sfx.whoosh(0.6, heavy=True), 0.4), (T(100) + 0.2, sfx.burn(1.0), 0.45), (T(102), sfx.chime(1320, 1.2), 0.25),
            (T(112), sfx.impact(1.2), 0.5), (T(112) + 0.1, sfx.burn(0.8), 0.3), (T(116.6), sfx.impact(1.4), 0.7), (T(116.6), sfx.drop(0.35), 0.4),
            (T(130), sfx.chime(784, 2.2), 0.4), (T(134), sfx.whoosh(0.8, up=False), 0.25)] + \
           [(T(139) + i * E8, sfx.chime(1046 + 80 * i, 0.6), 0.12) for i in range(8)] + \
           [(T(152) + 0.3, sfx.tick(), 0.4), (T(152) + 0.6, sfx.chime(660, 0.6), 0.2), (T(156), thump(0.8), 0.6), (T(158), sfx.whoosh(1.0, up=False), 0.2),
            (T(180), sfx.tick(), 0.4)] + \
           [(T(183) + k * E8 * 0.8 + 0.6 * 1.0, sfx.tick(), 0.35) for k in range(0, 12, 2)] + \
           [(T(193), sfx.impact(1.0), 0.5)] + [(T(196) + k * 0.11, sfx.chime(2093, 0.25), 0.15) for k in range(9)] + \
           [(T(209), thump(), 0.5), (T(211), thump(), 0.5), (T(213), thump(), 0.55), (T(214.5), thump(), 0.55), (T(216), thump(), 0.6), (T(217), thump(), 0.6),
            (T(222), sfx.sparkle(1.4, 12), 0.3)]
    fx = sfx.mix(cues, duration); n = min(len(mus), len(fx)); mx = mus[:n] * 0.9 + fx[:n]
    sfx.write_wav(out, mx / max(1.0, np.abs(mx).max() / 0.97))


def worker(a, b, path, fps):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    for i in range(a, b):
        try: im = frame(i / fps)
        except Exception as e: print('frame', i, e, flush=True); im = np.zeros((H, W, 3), np.uint8)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--stills'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--music', default=os.path.join(HERE, '..', '..', 'media', 'Vibecoding_music.mp3'))
    args = ap.parse_args()
    if args.stills:
        os.makedirs(args.out, exist_ok=True)
        for s in args.stills.split(','): cv2.imwrite(os.path.join(args.out, f'{float(s):06.2f}.jpg'), frame(float(s)), [cv2.IMWRITE_JPEG_QUALITY, 90])
        return
    dur = T(END); N = int(dur * args.fps); k = args.jobs; tmp = tempfile.mkdtemp(); t0 = time.time()
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
