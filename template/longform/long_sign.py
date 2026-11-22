#!/usr/bin/env python3
"""X 的内心世界 · 8 分钟 —— one engine for every zodiac sign and MBTI type, Chinese + English in one render.

  python3 template/longform/long_sign.py src/gemini_v2.txt --out out/long/final/zh/双子座的内心世界.mp4 \
          --out-en out/long/final/en/The_Inner_World_of_Gemini.mp4 [--stills 5,30] [--list]

Script header (see src/*_v2.txt):
  TITLE 双子座的内心世界 || The Inner World of Gemini
  SUBJ zodiac gemini            (or: SUBJ mbti ENFJ)
  ELEMENT air                   hook visuals: fire | earth | air | water
  PAL air                       main palette
  CONST x,y x,y … | x,y …       constellation polyline(s), drawn behind the title (optional)
  HOOK 他的心里/…(7 lines) || Deep inside him/…
  # 章 palette                  chapters; '?' question beat, '*' reveal, {motif} action, 【】 gold, '||' English
Aries keeps its hand-made first minute (first_minute_v4); every other subject gets the element hook below.
"""
import math, os, re, sys, types
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
SCRIPT = next((a for a in sys.argv[1:] if a.endswith('.txt')), None)
if SCRIPT: sys.argv.remove(SCRIPT)
HDR = {}
for line in open(SCRIPT, encoding='utf-8'):
    for k in ('TITLE', 'SUBJ', 'ELEMENT', 'PAL', 'CONST', 'HOOK'):
        if line.startswith(k + ' '): HDR[k] = line[len(k) + 1:].strip()
SUBJ = HDR['SUBJ'].split()
import aries_char as AC, signs_cfg as SC
AC.STYLE.clear(); AC.STYLE.update(SC.ZODIAC[SUBJ[1]] if SUBJ[0] == 'zodiac' else SC.mbti(SUBJ[1]))

import long_aries as L
import first_minute as FM
from first_minute_v4 import (inst, pose, mix, mirror, run_cycle, walk_cycle, heart_live, sparks_live, burst, ground, sh_for, T, E8,
                             _COUNTS, Shot, drift, stars_live, flame_shape)
from engine.core import W, H, Palette, Cam, flame, Text, F, SERIF_B, SERIF_BL, lerp, cl, ramp, eo, eio, pulse, pop
from story_frames import figure, glint, milkyway, meteor, godrays, sp, solid, lamp, window, BLACK, phone_big
from aries_char import draw_aries, skeleton
import sfx, render_long as R

ELEMENT = HDR.get('ELEMENT', 'fire')
PM = L.PALS[HDR.get('PAL', ELEMENT)]
L.DEFAULT_PAL[0] = PM
L.STYLE_FLAME[0] = ELEMENT == 'fire'
L.DUR = {1: 18, 2: 20, 3: 24, 4: 28}
MUSIC_START, DROP, HOOK_END = 12, 52, 80
TWIN = 'twin' in AC.STYLE.get('extras', ())

# hook lines
_hc, _he = (HDR.get('HOOK', '/'.join(['…'] * 7)).split('||') + [''])[:2]
HL = [L._marks(x.strip()) for x in _hc.split('/')]          # (text, gold, segs)
L.tr_add(_hc.strip(), _he.strip()) if _he.strip() else None
TITLE = L._marks(HDR['TITLE'].split('||')[0].strip())[0]
CONST = []
if HDR.get('CONST'):
    for part in HDR['CONST'].split('|'):
        CONST.append([tuple(float(v) for v in p.split(',')) for p in part.split()])

# twin (Gemini): a translucent second self follows him
_A = L.A
def A2(cv, C, x, gy, h, p, **kw):
    if TWIN and kw.get('a', 1.0) > 0.5:
        k2 = dict(kw); k2['a'] = 0.3; k2['heart'] = 0.0
        _A(cv, C, x - 0.16 * h, gy, h, p, **k2)
    return _A(cv, C, x, gy, h, p, **kw)
L.A = A2


def HC(tx, i, x, y, size, m0, m1, step=0.5, t=0, col=None, gold=None):
    txt, g, _ = HL[i]
    FM.cap(tx, txt, x, y, size, m0, m1, step, g if gold is None else gold, t=t, col=col)


def hero(cv, x, gy, h, p, P, **kw):
    if TWIN:
        k2 = dict(kw); k2.update(a=0.3, heart=0.0); draw_aries(cv, x - 0.16 * h, gy, h, p, P=P, col=P.SOFT, **k2)
    return draw_aries(cv, x, gy, h, p, P=P, col=P.SOFT, **kw)


# ================================================================ element pieces
def soil(cv, P, y, a=0.6, seed=3):
    rr = np.random.default_rng(seed)
    cv.path([(-300, y), (W + 300, y)], P.LINE, a, 2, smooth=False)
    for k in range(4):
        yy = y + 70 + k * 90
        cv.path([(x, yy + 10 * math.sin(x / 140 + k)) for x in np.linspace(-300, W + 300, 40)], P.LINE, a * (0.35 - 0.06 * k), 1.2, smooth=False)
    for _ in range(40):
        c = (rr.uniform(0, W), rr.uniform(y + 30, H)); s = rr.uniform(4, 12)
        cv.path([(c[0] - s, c[1]), (c[0], c[1] - s * 0.6), (c[0] + s, c[1]), (c[0], c[1] + s * 0.5), (c[0] - s, c[1])], P.LINE, a * 0.3, 1, smooth=False)


def seed_shape(cv, P, c, s, a=1.0):
    pts = [(c[0] + s * 0.7 * math.cos(q), c[1] + s * math.sin(q) * (1 - 0.15 * math.cos(q))) for q in np.linspace(0, 2 * math.pi, 40)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.WARM * 0.4, a); cv.path(pts, P.GOLD, a, 2.6, smooth=False)
    cv.glow(c, s * 2.5, P.GOLD, 0.7 * a)


def roots(cv, P, c, k, a=0.8, seed=1):
    rr = np.random.default_rng(seed)
    for b in range(5):
        p = np.array(c, float); seg = [tuple(p)]; ang = math.pi / 2 + rr.uniform(-0.9, 0.9)
        for _ in range(8):
            ang += rr.uniform(-0.35, 0.35); p = p + np.array([math.cos(ang), math.sin(ang)]) * rr.uniform(16, 30); seg.append(tuple(p))
        cv.path(seg, P.SOFT, a, 1.6, frac=k, smooth=False)


def leaf(cv, P, c, r, q0, a=0.8):
    l1 = [(c[0] + r * math.cos(q0) * u - r * 0.35 * math.sin(math.pi * u) * math.sin(q0), c[1] + r * math.sin(q0) * u + r * 0.35 * math.sin(math.pi * u) * math.cos(q0)) for u in np.linspace(0, 1, 8)]
    l2 = [(c[0] + r * math.cos(q0) * u + r * 0.35 * math.sin(math.pi * u) * math.sin(q0), c[1] + r * math.sin(q0) * u - r * 0.35 * math.sin(math.pi * u) * math.cos(q0)) for u in np.linspace(1, 0, 8)]
    cv.path(l1 + l2, P.SOFT, a, 1.6, smooth=False)


def wind(cv, P, t, n=14, y0=150, y1=950, a=0.45, speed=500, seed=3):
    rr = np.random.default_rng(seed)
    for i in range(n):
        y = rr.uniform(y0, y1); x = (rr.uniform(0, W + 600) + speed * t) % (W + 600) - 300; L_ = rr.uniform(160, 360)
        pts = [(x - L_ + u * L_, y + 18 * math.sin(u * 5 + t * 2 + i)) for u in np.linspace(0, 1, 14)]
        cv.path(pts, P.SOFT, a * rr.uniform(0.4, 1), 1.4, smooth=False)
        if i % 3 == 0: cv.path([pts[-1], (pts[-1][0] + 30 * math.cos(t * 3 + i), pts[-1][1] - 30 + 10 * math.sin(t * 3))], P.SOFT, a * 0.6, 1.2)


def bubbles(cv, P, t, n=24, x0=200, x1=1700, a=0.6, seed=4):
    rr = np.random.default_rng(seed)
    for i in range(n):
        ph = (t * rr.uniform(0.08, 0.2) + rr.uniform(0, 1)) % 1; x = rr.uniform(x0, x1) + 20 * math.sin(t * 2 + i); y = 1100 - 1250 * ph
        cv.circle((x, y), rr.uniform(5, 16), P.SOFT, a * (1 - ph * 0.5), 1.4)


def water(cv, P, y, t, amp=14, a=0.7):
    for k in range(3):
        yy = y + k * 40
        cv.path([(x, yy + amp * (1 - 0.3 * k) * math.sin(x / (120 + 40 * k) + t * (1.5 - 0.3 * k) + k)) for x in np.linspace(-300, W + 300, 70)], P.LINE, a * (1 - 0.3 * k), 2 - 0.4 * k, smooth=False)


def cloud(cv, P, c, s, a=0.8):
    circ = ((-1.1, 0.1, 0.55), (-0.5, -0.35, 0.7), (0.25, -0.45, 0.8), (0.95, -0.05, 0.6), (0.4, 0.3, 0.55), (-0.45, 0.35, 0.55))
    allp = []
    for i, (dx, dy, r) in enumerate(circ):
        seg = []
        for q in np.linspace(0, 2 * math.pi, 40):
            px, py = dx + r * math.cos(q), dy + r * 0.8 * math.sin(q)
            inside = any(((px - ex) / er) ** 2 + ((py - ey) / (er * 0.8)) ** 2 < 0.98 for j, (ex, ey, er) in enumerate(circ) if j != i)
            if inside:
                if len(seg) > 1: cv.path(seg, P.SOFT, a, 2, smooth=False)
                seg = []
            else: seg.append((c[0] + px * s, c[1] + py * s))
        if len(seg) > 1: cv.path(seg, P.SOFT, a, 2, smooth=False)


def element_core(cv, P, t, n, c, k):
    """the thing in his heart at the very start; k = grow 0..1"""
    if ELEMENT == 'earth':
        seed_shape(cv, P, c, 36 * (1 + 0.15 * pulse(t, FM.quarter(t), 0.3)))
        if k > 0: roots(cv, P, (c[0], c[1] + 30), k)
        if k > 0.3: cv.path([(c[0], c[1] - 30), (c[0] + 6 * math.sin(t * 2), c[1] - 30 - 150 * eo(ramp(k, 0.3, 1)))], P.SOFT, 1, 2.4, smooth=False)
    elif ELEMENT == 'fire':
        cv.circle(c, 6 * (1 + 0.5 * pulse(t, FM.quarter(t), 0.3)), P.WARM, 1, fill=True); cv.glow(c, 60, P.GOLD, 1.0)
        if k > 0: flame_shape(cv, (c[0], c[1] - 10), 60 + 160 * eo(k), P, eio(cl(k * 2)), t)
    elif ELEMENT == 'air':
        cv.circle(c, 8, P.WARM, 1, fill=True); cv.glow(c, 70, P.GOLD, 0.9)
        for j in range(5):
            r0 = 30 + 40 * j; q0 = t * (1.6 - 0.2 * j) + j
            cv.path([(c[0] + (r0 + 20 * u) * math.cos(q0 + u * 2.6), c[1] + (r0 + 20 * u) * 0.6 * math.sin(q0 + u * 2.6)) for u in np.linspace(0, 1, 20)], P.SOFT, 0.7 * (0.3 + 0.7 * k), 1.6, smooth=False)
    else:  # water: a drop falls, ripples spread
        fall = ramp(n, 0, 2.5); y = lerp(c[1] - 500, c[1], fall ** 2)
        water(cv, P, c[1] + 6, t, 6, 0.6)
        if fall < 1: cv.poly(sp([(c[0], y - 26), (c[0] + 13, y + 6), (c[0], y + 18), (c[0] - 13, y + 6)], 4, True), P.WARM, 1)
        else:
            for j in range(3):
                u = ((t - T(2.5)) * 0.6 + j / 3) % 1; cv.path([(c[0] + 360 * u * math.cos(q), c[1] + 6 + 50 * u * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 50)], P.GOLD, (1 - u) * 0.8, 1.6, smooth=False)
            cv.glow((c[0], c[1] + 60), 80, P.GOLD, 0.7)


def element_particles(cv, P, t, n, m0):
    rr = np.random.default_rng(4)
    if ELEMENT == 'earth':
        for i in range(9):
            c = (rr.uniform(450, 1400), rr.uniform(150, 950)); k = eo(ramp(n, m0 + 0.5 + i * 0.6, m0 + 3 + i * 0.6))
            if k > 0: leaf(cv, P, c, 40 * k, rr.uniform(0, 6.3) + 0.2 * math.sin(t + i))
    elif ELEMENT == 'fire': sparks_live(cv, (900, 900), t, 50, 40, 900, P, 0.7, 4, (-math.pi * 0.95, -math.pi * 0.05), 0.4, 1.6)
    elif ELEMENT == 'air': wind(cv, P, t, 12, 120, 1000, 0.4)
    else: bubbles(cv, P, t, 26)


def element_big(cv, P, t, n, m0, m1):
    """the element at full size (beat 3)"""
    k = ramp(n, m0, m1); lt = t - T(m0)
    if ELEMENT == 'earth':
        ground(cv, 860, P, 0.6); day = lt / 1.0; q = math.pi * (day % 1)
        c = (960 - 700 * math.cos(q), 860 - 520 * math.sin(q))
        if (day % 2) < 1: cv.circle(c, 40, P.WARM, 1, fill=True); cv.glow(c, 120, P.GOLD, 0.6)
        else: cv.circle(c, 30, P.SOFT, 1, fill=True); stars_live(cv, P, t, 80, 600, 4, 0.6)
        L.sprout(cv, types.SimpleNamespace(P=P, t=t, lt=lt), (960, 860), 0.15 + 0.8 * k)
    elif ELEMENT == 'fire':
        ground(cv, 980, P, 0.5)
        flame_shape(cv, (960, 700), lerp(220, 520, eo(k)) * (1 + 0.04 * math.sin(t * 9)), P, 1.0, t)
        sparks_live(cv, (960, 600), t, 60, 60, 800, P, 0.9, 7, (-math.pi * 0.95, -math.pi * 0.05), 0.6, 1.0)
        godrays(cv, (960, 600), np.linspace(0, 2 * math.pi, 16) + t * 0.2, 1000, P.GOLD, 0.06 + 0.06 * k)
    elif ELEMENT == 'air':
        wind(cv, P, t, 26, 100, 1000, 0.55, 900 + 600 * k)
        for i in range(12):
            q = t * 2.2 + i * 0.5; r0 = 80 + 26 * i
            leaf(cv, P, (960 + r0 * math.cos(q), 560 + r0 * 0.5 * math.sin(q) - i * 12), 26, q + 1.2, 0.8)
        cloud(cv, P, (500 - 80 * lt, 240), 90, 0.6); cloud(cv, P, (1450 - 60 * lt, 320), 70, 0.5)
    else:
        amp = lerp(14, 120, eo(k)); water(cv, P, 760, t, amp, 0.8)
        cv.path([(x, 760 - amp * 1.4 * math.exp(-((x - 960) / 260) ** 2) + 10 * math.sin(t * 3)) for x in np.linspace(300, 1620, 60)], P.GOLD, 0.9, 2.6, smooth=False)
        bubbles(cv, P, t, 20, 300, 1620, 0.5); stars_live(cv, P, t, 80, 500, 6, 0.6)


def element_cover(cv, P, t, n, c, k):
    """the heart hidden away (beat 5); k = closed 0..1"""
    if ELEMENT == 'earth':
        for sd in (-1, 1):
            off = sd * lerp(700, 10, k)
            sh_ = [(c[0] + off + sd * 280 * abs(math.cos(q)) * 0.9, c[1] + 300 * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 30)]
            solid(cv, sh_ + [(c[0] + off, c[1] + 300), (c[0] + off, c[1] - 300)], P.LINE, 1.0, 2.6, 0.06)
    elif ELEMENT == 'fire':
        yh = lerp(-300, c[1] - 220, k)
        hand = [(560, yh - 20), (1360, yh - 20), (1380, yh + 120), (1300, yh + 200), (620, yh + 200), (540, yh + 120)]
        solid(cv, sp(hand, 4, True), P.SOFT, 1.0, 2.4, 0.05)
        for j in range(4): cv.path([(700 + j * 170, yh), (700 + j * 170, yh + 190)], P.SOFT, 0.5, 1.2, smooth=False)
        cv.path([(560, yh), (1360, yh)], P.GOLD, 1, 3, smooth=False)
    elif ELEMENT == 'air':
        for sd in (-1, 1):
            for j in range(3): cloud(cv, P, (c[0] + sd * lerp(900, 120 + 60 * j, k), c[1] - 160 + j * 160), 120, 0.9)
    else:
        lvl = lerp(c[1] + 300, c[1] - 260, k)
        cv.poly([(-300, lvl), (W + 300, lvl), (W + 300, H + 50), (-300, H + 50)], P.LINE * 0.08, 1.0)
        water(cv, P, lvl, t, 16, 0.9)


def element_setting(cv, P, t, u):
    rr = np.random.default_rng(5)
    if ELEMENT == 'earth':
        for i in range(70):
            x = rr.uniform(-100, W + 100); hg = rr.uniform(20, 60); sw = 8 * math.sin(t * 1.6 + x / 120)
            cv.path([(x, HGY), (x + sw * 0.5, HGY - hg * 0.5), (x + sw, HGY - hg)], P.SOFT, 0.45 * u, 1.2)
        for i in range(9):
            fc = (180 + i * 200 + 30 * math.sin(i), HGY - 40 - 10 * (i % 3))
            for j in range(5): q = j / 5 * 2 * math.pi + t * 0.3; cv.circle((fc[0] + 9 * math.cos(q), fc[1] + 9 * math.sin(q)), 6, P.WARM, 0.8 * u, 1.4)
    elif ELEMENT == 'fire':
        sparks_live(cv, (960, 960), t, 60, 40, 1000, P, 0.6 * u, 8, (-math.pi * 0.95, -math.pi * 0.05), 0.3, 2.2)
        godrays(cv, (HX, 560), np.linspace(-math.pi, 0, 12) + 0.05 * math.sin(t), 900, P.GOLD, 0.06 * u)
    elif ELEMENT == 'air':
        wind(cv, P, t, 14, 150, 900, 0.35 * u, 300)
        cloud(cv, P, (1500 - 20 * t % 400, 700), 80, 0.4 * u); cloud(cv, P, (300 + 10 * t % 300, 760), 60, 0.35 * u)
    else:
        water(cv, P, HGY + 10, t, 6, 0.6 * u)
        for j in range(3):
            v = ((t * 0.3) + j / 3) % 1; cv.path([(HX + 300 * v * math.cos(q), HGY + 12 + 30 * v * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 40)], P.GOLD, (1 - v) * 0.6 * u, 1.4, smooth=False)


# ================================================================ hook shots (0 – 80 E8)
def h1(t, n, tx):
    s = lerp(1.0, 1.3, eio(ramp(n, 0, 8))); ds, dx, dy = drift(t, 0, 0.4)
    cy = 700 if ELEMENT in ('earth', 'water') else 560
    sh = sh_for('h1', t, 0, Cam(s * ds, 960 + dx, cy + dy), 1.0, 2.0); cv = sh.cv; P = PM
    c = (960, 800) if ELEMENT == 'earth' else ((960, 700) if ELEMENT == 'water' else (960, 600))
    if ELEMENT == 'earth': soil(cv, P, 640)
    with inst(cv):
        for p0 in (0, 2, 4):
            if T(p0) <= t < T(p0) + 1.2: k = (t - T(p0)) / 1.2; cv.circle(c, 30 + 260 * eo(k), P.GOLD, (1 - k) * 0.6, 1.4)
        element_core(cv, P, t, n, c, ramp(n, 4, 8))
    HC(tx, 0, 960, 230, 72, 1, 15.6, 1, t=t); HC(tx, 1, 960, 330, 72, 4, 15.6, 0.5, t=t)
    return sh, P, 0.6, 0.0


def h2(t, n, tx):
    s = lerp(1.0, 1.08, eio(ramp(n, 8, 16))); ds, dx, dy = drift(t, T(8), 0.5)
    sh = sh_for('h2', t, 8, Cam(s * ds, 900 + dx, 540 + dy), 1.6, 2.4); cv = sh.cv; P = PM
    draw_aries(cv, 900, 1080 + 2000 * 0.6, 2000, pose('hero', mouth='smile', brow='calm', wind=(-0.3, 0.1)), P=P, col=P.SOFT, rim=(1, 0.3), heart=0)
    with inst(cv): element_particles(cv, P, t, n, 8)
    HC(tx, 0, 1520, 720, 52, 8, 15.6, 0, t=t); HC(tx, 1, 1520, 810, 64, 8, 15.6, 0, t=t)
    return sh, P, 0.6, 0.0


def h3(t, n, tx):
    sh = sh_for('h3', t, 16, Cam(1.0 + 0.04 * ramp(n, 16, 24), 960, 560), 0.8, 1.6); cv = sh.cv; P = PM
    with inst(cv): element_big(cv, P, t, n, 16, 24)
    if ELEMENT != 'earth': ground(cv, 980, P, 0.4)
    HC(tx, 2, 960, 200, 80, 16, 23.6, 0, t=t); HC(tx, 3, 960, 310, 80, 20, 23.6, 0.5, t=t)
    return sh, P, 0.6, 0.2 * pulse(t, T(20), 0.3) if ELEMENT == 'fire' else 0.0


def h4(t, n, tx):
    s = lerp(1.0, 1.1, eio(ramp(n, 24, 40))); sh = sh_for('h4', t, 24, Cam(s, 880, 560), 1.2, 2.5); cv = sh.cv; P = PM
    ground(cv, 960, P, 0.5)
    J = hero(cv, 760, 960, 560, pose('hero', mouth='flat', brow='calm'), P, rim=(1, -0.3))
    if n < 32:
        figure(cv, 1260, 960, 520, 'argue', P.LINE * 0.95, 0.85, d=-1, hair='long', P=P, th=1.8)
        with inst(cv):
            for i in range(3):
                if n > 25 + i: FM.cap(tx, '?', 640 + i * 70, 300 - 20 * i, 54, 25 + i, 31.8, 0, t=t)
            cv.path([(1180, 540), (1150 + 20 * math.sin(t * 9), 480)], P.LINE, 0.6, 2, smooth=False)
        HC(tx, 4, 1300, 220, 64, 24, 31.8, 0.5, t=t)
    else:
        with inst(cv):
            for i, (kind, c) in enumerate((('cup', (480, 300)), ('umb', (760, 200)), ('cal', (1040, 300)))):
                t1 = T(33 + i * 2); k = eo(ramp(t, t1, t1 + 0.6))
                if k <= 0: continue
                c = (lerp(J['head'][0], c[0], k), lerp(J['head'][1], c[1], k) + 6 * math.sin(t * 2 + i))
                fr = [(c[0] - 90, c[1] - 70), (c[0] + 90, c[1] - 70), (c[0] + 90, c[1] + 70), (c[0] - 90, c[1] + 70)]
                cv.path(fr + [fr[0]], P.GOLD, k, 2, smooth=False); cv.glow(c, 100, P.GOLD, 0.2 * k)
                if kind == 'cup': L.cup(cv, types.SimpleNamespace(P=P, lt=t, t=t), (c[0], c[1] + 20), 0.6, k, steam=False)
                elif kind == 'umb': cv.path([(c[0] - 60, c[1]), (c[0], c[1] - 50), (c[0] + 60, c[1]), (c[0] - 60, c[1])], P.WARM, k, 2, smooth=False); cv.path([(c[0], c[1]), (c[0], c[1] + 50)], P.WARM, k, 2, smooth=False)
                else:
                    for r_ in range(3):
                        for c_ in range(4): cv.circle((c[0] - 54 + c_ * 36, c[1] - 30 + r_ * 30), 4, P.SOFT, k * 0.6, fill=True)
                    heart_live(cv, (c[0] + 18, c[1]), 14, P, k, 0.6)
                cv.path([J['head'], c], P.GOLD, 0.15 * k, 1, smooth=False)
        HC(tx, 5, 1450, 620, 64, 32, 39.6, 0.5, t=t)
    return sh, P, 0.6, 0.0


def h5(t, n, tx):
    s = 1.0 if n < 47 else 1 + 6 * eio(ramp(n, 47, 52)) ** 2.2
    sh = sh_for('h5', t, 40, Cam(s, 960, 600), 0.4, 1.0); cv = sh.cv; P = PM; c = (960, 600)
    heart_live(cv, c, 110, P, 1.0, lerp(1.0, 0.5, ramp(n, 41, 44)), pulse(t, FM.quarter(t), 0.25))
    k = eio(ramp(n, 40, 44)) * (1 - eio(ramp(n, 46, 48)))
    element_cover(cv, P, t, n, c, k)
    HC(tx, 6, 960, 170, 76, 40, 46.6, 0.5, t=t)
    return sh, P, 0.6, ramp(n, 50.5, 52) * 0.9


HX, HGY, HH = 640, 960, 640


def h_drop(t, n, tx):
    p = pose('hero', mouth='smile', brow='calm', wind=(-0.5 + 0.1 * math.sin(t * 2), 0.0))
    J = skeleton(HX, HGY, HH, p, 1); chest = J['sc'] - J['up'] * 0.075 * HH
    u = eio(ramp(n, DROP, DROP + 6)); s = lerp(8.0, 1.0, u) * (1 + 0.05 * ramp(n, DROP + 6, 80)); ds, dx, dy = drift(t, T(DROP) + 1.6, 0.8 * u)
    cam = Cam(s * ds, lerp(chest[0], 960, u) + dx, lerp(chest[1], 540, u) + dy)
    sh = sh_for('hdrop', t, DROP, cam, 2.2, 4.5); cv = sh.cv; P = PM
    with inst(cv):
        stars_live(cv, P, t, 200, 700, 9, a=u)
        milkyway(cv, P, (-200, 120), (W + 200, 380), 140, 8, 0.6 * u)
        burst(cv, chest, ramp(t, T(DROP), T(DROP) + 1.5), 80, 900, P, 1.0, 12)
        element_setting(cv, P, t, u)
    for part in CONST: cv.path(part, P.GOLD, 0.6, 1.4, smooth=False)
    ground(cv, HGY, P, 0.5)
    hero(cv, HX, HGY, HH, p, P, rim=(-1, -0.3), heart=1 + 0.15 * pulse(t, FM.quarter(t), 0.25))
    with inst(cv):
        if n < DROP + 4: heart_live(cv, chest, 0.026 * HH, P, 1 - ramp(n, DROP + 3, DROP + 4), 1.0)
        i = 0
        for part in CONST:
            for q in part: glint(cv, q, 14 + 10 * pulse(t, FM.quarter(t) + i * E8 * 0.5, 0.5), P.WARM, 1); i += 1
    FM.cap(tx, TITLE, 1340, 560, 96, DROP + 1, 79.6, 0.5, 'all', t=t, col=P.HI)
    return sh, P, 0.6, 0.9 * (1 - ramp(t, T(DROP), T(DROP) + 0.5))


SCENES = [(0, 8, h1, 'h1'), (8, 16, h2, 'h2'), (16, 24, h3, 'h3'), (24, 40, h4, 'h4'), (40, 52, h5, 'h5'), (52, 80, h_drop, 'hdrop')]


def _count():
    orig = Shot.__init__
    for m0, m1, fn, key in SCENES:
        _COUNTS[key] = (10 ** 6, 10 ** 6); box = {}
        def spy(self, *a, **k):
            orig(self, *a, **k); box['cv'] = self.cv
        Shot.__init__ = spy
        try: fn(T(m1) - 0.02, m1 - 0.02 / E8, L.DualText(PM))
        finally: Shot.__init__ = orig
        c = box['cv'].cnt; _COUNTS[key] = (max(c['bg'], 1), max(c['fg'], 1))


def base(t, tx):
    n = t / E8; fn = SCENES[-1][2]
    for m0, m1, f, key in SCENES:
        if n < m1: fn = f; break
    sh, P, glow, flash = fn(t, n, tx)
    img = sh.cv.composite(P.BG * 0.6, flash, glow=glow) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    return np.clip(img, 0, 1.6).astype(np.float32), ramp(t, 0, 0.15)


def build_audio(music, out, duration):
    import subprocess, tempfile, wave
    phase, e8 = R.grid(music); st = phase + MUSIC_START * e8; dr = T(DROP)
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, 'a.wav'); b = os.path.join(tmp, 'b.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.4f}', '-t', f'{dr:.4f}', '-i', music, '-af', 'lowpass=f=900,volume=0.55,afade=t=in:d=0.3', '-ac', '1', '-ar', str(sfx.SR), a], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st + dr:.4f}', '-t', f'{duration - dr:.4f}', '-i', music, '-ac', '1', '-ar', str(sfx.SR), b], check=True)
    def rd(p):
        w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mus = np.concatenate([rd(a), rd(b)])
    thump = lambda d=0.4: (np.sin(2 * np.pi * 55 * np.arange(int(d * sfx.SR)) / sfx.SR) * np.exp(-np.arange(int(d * sfx.SR)) / sfx.SR * 9)).astype(np.float32)
    el = {'earth': sfx.chime(880, 1.2), 'fire': sfx.burn(1.0), 'air': sfx.whoosh(1.0), 'water': sfx.chime(660, 1.6)}[ELEMENT]
    cues = [(T(0), thump(), 0.6), (T(2), thump(), 0.5), (T(4), thump(), 0.5), (T(4), el, 0.3), (T(8), sfx.whoosh(0.8), 0.2),
            (T(9), sfx.sparkle(1.4, 10), 0.2), (T(16), sfx.whoosh(0.6, up=False), 0.25), (T(20), sfx.impact(0.8) if ELEMENT == 'fire' else sfx.whoosh(0.8), 0.3)] + \
           [(T(25 + i), sfx.tick(), 0.3) for i in range(3)] + [(T(33 + 2 * i), sfx.chime(1046 + 120 * i, 1.0), 0.22) for i in range(3)] + \
           [(T(42), sfx.impact(0.8), 0.35), (T(43), thump(), 0.5), (T(45), thump(), 0.45),
            (T(DROP) - 1.9, sfx.riser(1.9), 0.65), (T(DROP), sfx.impact(1.8), 0.9), (T(DROP + 1), sfx.sparkle(1.6, 16), 0.3)]
    fx = sfx.mix(cues, duration); n = min(len(mus), len(fx)); mx = mus[:n] * 0.9 + fx[:n]
    sfx.write_wav(out, mx / max(1.0, np.abs(mx).max() / 0.97))


HOOK = types.SimpleNamespace(END=HOOK_END, MUSIC_START=MUSIC_START, DROP=DROP, DUCKS=[], base=base, _count=_count, build_audio=build_audio)

# ================================================================ extra motifs (shared by every subject)
import motifs_extra as MX
MX.install(L, globals())

# ================================================================ wire up
if SUBJ[1] == 'aries':
    L.DUR = {1: 16, 2: 18, 3: 22, 4: 26}
    L.CARDS = L.parse(SCRIPT)                       # first minute = first_minute_v4, chapter 燃 lives inside it
else:
    L.V = HOOK; L.FIRST_END = HOOK_END; L.CH_PAL = {}; L.TARGET[0] = 486.0
    L.CARDS = L.parse(SCRIPT, skip_ch=(), first_end=HOOK_END)
L.END = L.CARDS[-1].m1

if __name__ == '__main__':
    L.main()
