#!/usr/bin/env python3
"""白羊座的内心世界 · 8 分钟完整版

0 – 60 s is the approved first minute (first_minute_v4.SCENES). From there every card of src/aries_v2.txt becomes
its own directed shot with an action that acts out the line (a phone whose message is typed and deleted, a clock
that spins through the night, an umbrella that arrives over someone's head, stairs climbed one beat at a time …).
Each shot is grown stroke by stroke; the camera keeps moving; '?' cards are dark question beats and '*' cards are
the big reveals with a pull-out and a burst. Same protagonist, same palette logic, same SFX language.

  python3 template/longform/long_aries.py --out out/long/v4/白羊座的内心世界_8分钟.mp4 [--stills 70,95] [--from 60 --to 120]
"""
import argparse, math, os, re, subprocess, sys, tempfile, time
from multiprocessing import Process
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
import first_minute_v4 as V
from first_minute_v4 import (inst, pose, mix, mirror, run_cycle, walk_cycle, heart_live, sparks_live, burst, speedlines, ground,
                             cal_page, wall, cracks, bolt, sh_for, T, E8, PF, PV, _COUNTS, Shot, drift, stars_live, rain_live, flame_shape)
from engine.core import W, H, Palette, Cam, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, lerp, cl, ramp, eo, eio, pulse, pop
from vis import heart_pts
from story_frames import figure, glint, milkyway, meteor, godrays, sp, solid, lamp, window, skyline, BLACK
from aries_char import draw_aries, POSE, skeleton
import first_minute as FM
import sfx
import render_long as R

PA = Palette('azure')
STYLE_FLAME = [True]
FIRST_END = V.END            # 226
CH_PAL = {'直': PF, '软': PF, '疼': PV, '冲': PF, '爱': PF, '独': PA, '赢': PF, '累': PV, '真': PF}


# ================================================================ script -> cards
class Card:
    pass


DUR = {1: 16, 2: 18, 3: 22, 4: 26}


def parse(path, skip_ch=('燃',), first_end=None):
    cards, ch = [], None; skip = True
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('# '):
            ch = line[2:].split()[0]; skip = (ch in skip_ch); continue
        if skip or not line.strip() or line.startswith(('//', 'H ', 'TITLE', 'SUBJ', 'Q ', 'B ', 'TAG', 'STYLE', 'MUSIC')): continue
        kind, motif = 'n', None
        if line[0] == '?': kind, line = 'q', line[1:]
        elif line[0] == '*': kind, line = 'r', line[1:]
        m = re.match(r'\{(\w+)\}(.*)', line)
        if m: motif, line = m.group(1), m.group(2)
        lines, golds = [], []
        for seg in line.split('/'):
            g, out = [], ''
            inside = False
            for chh in seg:
                if chh == '【': inside = True; continue
                if chh == '】': inside = False; continue
                if inside: g.append(len(out))
                out += chh
            lines.append(out); golds.append(tuple(g))
        c = Card(); c.ch, c.kind, c.motif, c.lines, c.golds = ch, kind, motif, lines, golds
        cards.append(c)
    m = FIRST_END if first_end is None else first_end; prev = None
    for i, c in enumerate(cards):
        n = len(c.lines); d = DUR.get(n, DUR[4])
        if c.kind == 'r': d += 10
        if c.kind == 'q': d += 2
        if i == len(cards) - 1: d += 14
        c.m0, c.m1, c.idx = m, m + d, i; c.first = (c.ch != prev); prev = c.ch; m += d
        c.P = CH_PAL.get(c.ch, PF)
    return cards


CARDS = parse(os.path.join(HERE, 'src', 'aries_v2.txt'))
END = CARDS[-1].m1


# ================================================================ shared drawing helpers
def A(cv, C, x, gy, h, p, **kw):
    P = C.P; kw.setdefault('rim', (1, -0.3))
    if P is not PF: kw.setdefault('col', P.SOFT)
    return draw_aries(cv, x, gy, h, p, P=P, **kw)


def Y(cv, C, x, gy, h, pose_='stand', d=-1, a=0.85):
    return figure(cv, x, gy, h, pose_, C.P.LINE * 0.95, a, d=d, hair='long', P=C.P, th=1.8)


def nightsky(cv, C, n=150, ymax=700, a=0.7):
    with inst(cv): stars_live(cv, C.P, C.t, n, ymax, 3 + C.idx % 5, a)


def bubble(cv, tx, cam, c, w, h, txt, P, a=1.0, tail=(-1, 1), gold=True, size=None):
    x0, y0 = c[0] - w / 2, c[1] - h / 2; r = min(h / 2, 40)
    pts = []
    for (qx, qy, q0) in ((x0 + w - r, y0 + r, -math.pi / 2), (x0 + w - r, y0 + h - r, 0), (x0 + r, y0 + h - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        pts += [(qx + r * math.cos(q), qy + r * math.sin(q)) for q in np.linspace(q0, q0 + math.pi / 2, 7)]
    tl = (c[0] + tail[0] * w * 0.3, c[1] + h / 2); tip = (tl[0] + tail[0] * 40, tl[1] + 46 * tail[1])
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.SOFT * 0.05, a); cv.path(pts + [pts[0]], P.SOFT, a, 2.4, smooth=False)
    cv.path([(tl[0] - 18, tl[1] - 2), tip, (tl[0] + 18, tl[1] - 2)], P.SOFT, a, 2.4, smooth=False)
    if txt:
        q = cam([(c[0], c[1] + h * 0.16)])[0]; s = size or int(h * 0.46)
        tx.chars(txt, q[0], q[1], F(SERIF_BL, max(8, int(s * cam.s))), (255, 214, 130) if gold else (235, 230, 220), 1, 0, 99, stagger=0)


def tears(cv, C, c, k0, n=3, a=1.0, spd=1.0):
    P = C.P
    for i in range(n):
        ph = ((C.lt * spd * 0.8) + i / n) % 1
        if C.lt < k0 + i * 0.3: continue
        y = c[1] + 260 * ph * ph; x = c[0] + 6 * math.sin(i * 2)
        drop = sp([(x, y - 14), (x + 7, y + 4), (x, y + 11), (x - 7, y + 4)], 4, True)
        cv.poly(drop, P.WARM, a * (1 - ph * 0.6)); cv.glow((x, y), 12, P.GOLD, 0.4 * a)


def ripple(cv, C, c, t0, a=0.6, n=3):
    for k in range(n):
        u = (C.lt - t0 - k * 0.35)
        if u < 0: continue
        u = (u % 1.4) / 1.4
        cv.path([(c[0] + 160 * u * math.cos(q), c[1] + 36 * u * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 40)], C.P.LINE, a * (1 - u), 1.4, smooth=False)


def clockface(cv, C, c, r, spin, a=1.0):
    P = C.P
    cv.circle(c, r, P.SOFT, a, 2.6); cv.circle(c, r * 0.9, P.SOFT, 0.35 * a, 1.2)
    for k in range(12):
        q = k / 12 * 2 * math.pi; cv.path([(c[0] + r * 0.8 * math.cos(q), c[1] + r * 0.8 * math.sin(q)), (c[0] + r * 0.9 * math.cos(q), c[1] + r * 0.9 * math.sin(q))], P.SOFT, a, 2, smooth=False)
    q1 = -math.pi / 2 + spin; q2 = -math.pi / 2 + spin / 12
    cv.path([c, (c[0] + r * 0.75 * math.cos(q1), c[1] + r * 0.75 * math.sin(q1))], P.WARM, a, 3, smooth=False)
    cv.path([c, (c[0] + r * 0.5 * math.cos(q2), c[1] + r * 0.5 * math.sin(q2))], P.GOLD, a, 4, smooth=False)
    cv.circle(c, 6, P.WARM, a, fill=True)


def cup(cv, C, c, s=1.0, a=1.0, steam=True):
    P = C.P; x, y = c
    body = [(x - 40 * s, y - 50 * s), (x + 40 * s, y - 50 * s), (x + 32 * s, y + 40 * s), (x - 32 * s, y + 40 * s)]
    solid(cv, body, P.SOFT, a, 2.4, 0.05)
    cv.path(sp([(x + 40 * s, y - 30 * s), (x + 66 * s, y - 20 * s), (x + 62 * s, y + 10 * s), (x + 36 * s, y + 14 * s)], 6), P.SOFT, a, 2.2)
    if steam:
        with inst(cv):
            for k in range(3):
                ph = (C.lt * 0.6 + k / 3) % 1
                pts = [(x - 20 * s + k * 20 * s + 14 * s * math.sin(C.t * 3 + j + k), y - 60 * s - j * 22 * s - ph * 40 * s) for j in range(5)]
                cv.path(pts, P.WARM, a * 0.7 * (1 - ph), 1.8)


def giftbox(cv, C, c, s=1.0, a=1.0, opened=0.0):
    P = C.P; x, y = c
    box = [(x - 70 * s, y - 50 * s), (x + 70 * s, y - 50 * s), (x + 70 * s, y + 60 * s), (x - 70 * s, y + 60 * s)]
    solid(cv, box, P.SOFT, a, 2.4, 0.05)
    cv.path([(x, y - 50 * s), (x, y + 60 * s)], P.GOLD, a, 3, smooth=False)
    ly = y - 50 * s - 120 * s * eo(opened); lr = -0.5 * opened
    lid = [(x - 78 * s, ly - 26 * s), (x + 78 * s, ly - 26 * s + 40 * s * lr), (x + 78 * s, ly + 40 * s * lr), (x - 78 * s, ly)]
    solid(cv, lid, P.SOFT, a, 2.4, 0.05)
    cv.path(sp([(x - 4, ly - 26 * s), (x - 40 * s, ly - 70 * s), (x - 50 * s, ly - 36 * s), (x - 4, ly - 26 * s)], 5), P.GOLD, a, 2.2)
    cv.path(sp([(x + 4, ly - 26 * s), (x + 40 * s, ly - 70 * s), (x + 50 * s, ly - 36 * s), (x + 4, ly - 26 * s)], 5), P.GOLD, a, 2.2)
    if opened > 0:
        with inst(cv):
            godrays(cv, (x, y - 50 * s), np.linspace(-math.pi * 0.85, -math.pi * 0.15, 9) + 0.05 * math.sin(C.t), 500 * opened, P.GOLD, 0.12 * opened)
            sparks_live(cv, (x, y - 60 * s), C.t, 26, 10, 300, P, opened, 5, (-math.pi * 0.9, -math.pi * 0.1), 0.6, 1.2)


def doorframe(cv, C, x, gy, w, h, openk=0.0, a=1.0, light=True):
    P = C.P
    fr = [(x - w / 2, gy), (x - w / 2, gy - h), (x + w / 2, gy - h), (x + w / 2, gy)]
    cv.path(fr, P.LINE, a, 2.6, smooth=False)
    if light and openk > 0:
        cv.poly([(x - w / 2 + 4, gy), (x - w / 2 + 4, gy - h + 4), (x - w / 2 + 4 + (w - 8) * openk, gy - h + 4), (x - w / 2 + 4 + (w - 8) * openk, gy)], P.WARM * 0.5, a * openk)
        cv.poly([(x - w / 2, gy), (x - w / 2 + w * openk, gy), (x + w * 1.6 * openk, gy + 200), (x - w * 1.2, gy + 200)], P.GOLD * 0.12, a * openk, layer=cv.F)
    dw = w * (1 - 0.8 * openk)
    leaf = [(x + w / 2 - dw, gy), (x + w / 2 - dw, gy - h), (x + w / 2, gy - h - 10 * openk), (x + w / 2, gy + 10 * openk)]
    solid(cv, leaf, P.LINE, a, 2.4, 0.05)
    cv.circle((x + w / 2 - dw + 16, gy - h * 0.48), 5, P.GOLD, a, fill=True)


def chain(cv, C, p0, p1, n, a=1.0, broken=0.0, seed=0):
    P = C.P; rr = np.random.default_rng(seed)
    for k in range(n):
        u = (k + 0.5) / n; c = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
        if broken > 0: c = (c[0] + rr.uniform(-1, 1) * 300 * broken, c[1] + 400 * broken * broken * rr.uniform(0.5, 1))
        rot = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + (math.pi / 2 if k % 2 else 0) + broken * rr.uniform(-3, 3)
        pts = [(c[0] + 26 * math.cos(q) * math.cos(rot) - 14 * math.sin(q) * math.sin(rot), c[1] + 26 * math.cos(q) * math.sin(rot) + 14 * math.sin(q) * math.cos(rot)) for q in np.linspace(0, 2 * math.pi, 18)]
        cv.path(pts, P.SOFT, a * (1 - broken), 2.4, smooth=False)


def feather(cv, C, c, s, rot, a=1.0):
    P = C.P; cs, sn = math.cos(rot), math.sin(rot)
    R_ = lambda x, y: (c[0] + (x * cs - y * sn) * s, c[1] + (x * sn + y * cs) * s)
    cv.path([R_(0, -60), R_(0, 70)], P.SOFT, a, 2, smooth=False)
    out = [R_(0, -62), R_(16, -30), R_(20, 10), R_(10, 50), R_(0, 56), R_(-12, 40), R_(-18, 0), R_(-14, -36)]
    cv.path(sp(out, 5, True), P.SOFT, a, 2, smooth=False)
    for k in range(7): y = -40 + k * 13; cv.path([R_(0, y), R_(15, y - 10)], P.SOFT, 0.5 * a, 1, smooth=False); cv.path([R_(0, y), R_(-15, y - 10)], P.SOFT, 0.5 * a, 1, smooth=False)


def mountain(cv, C, a=1.0):
    P = C.P
    cv.path([(-200, 980), (400, 620), (640, 760), (980, 260), (1300, 700), (1500, 560), (W + 200, 980)], P.LINE, a, 2.4, smooth=False)
    cv.path([(980, 260), (900, 420), (960, 400), (1040, 470), (980, 260)], P.SOFT, 0.6 * a, 1.4, smooth=False)
    cv.path([(980, 260), (980, 170)], P.LINE, a, 2, smooth=False); cv.poly([(980, 170), (1060, 190), (980, 214)], P.WARM, a)


def stairs(cv, C, n=8, x0=300, y0=960, sw=150, shh=80, a=1.0):
    pts = [(x0 - 200, y0)]
    for k in range(n): x = x0 + k * sw; y = y0 - k * shh; pts += [(x, y), (x, y - shh)]
    pts.append((x0 + n * sw + 200, y0 - n * shh)); cv.path(pts, C.P.LINE, a, 2.4, smooth=False)
    return lambda k: (x0 + k * sw + sw * 0.5, y0 - (k + 1) * shh)


def hourglass(cv, C, c, s, k, a=1.0):
    P = C.P; x, y = c
    fr = [(x - 90 * s, y - 150 * s), (x + 90 * s, y - 150 * s), (x + 10 * s, y), (x + 90 * s, y + 150 * s), (x - 90 * s, y + 150 * s), (x - 10 * s, y)]
    cv.path(fr + [fr[0]], P.SOFT, a, 2.6, smooth=False)
    cv.path([(x - 110 * s, y - 160 * s), (x + 110 * s, y - 160 * s)], P.GOLD, a, 4, smooth=False); cv.path([(x - 110 * s, y + 160 * s), (x + 110 * s, y + 160 * s)], P.GOLD, a, 4, smooth=False)
    top = lerp(130, 10, k) * s; bot = lerp(10, 130, k) * s
    cv.poly([(x - top * 0.62, y - top), (x + top * 0.62, y - top), (x, y)], P.WARM * 0.7, a)
    cv.poly([(x - 80 * s, y + 150 * s), (x + 80 * s, y + 150 * s), (x, y + 150 * s - bot)], P.WARM * 0.7, a)
    with inst(cv): cv.path([(x, y), (x, y + 150 * s - bot)], P.WARM, a, 1.6, smooth=False)


def target(cv, C, c, r, a=1.0):
    for k in range(4): cv.circle(c, r * (1 - k * 0.24), C.P.LINE if k % 2 == 0 else C.P.WARM, a, 2.4)
    cv.circle(c, r * 0.12, C.P.GOLD, a, fill=True)


def compass(cv, C, c, r, ang, a=1.0):
    P = C.P; cv.circle(c, r, P.SOFT, a, 2.6); cv.circle(c, r * 0.86, P.SOFT, 0.4 * a, 1.2)
    for k in range(16):
        q = k / 16 * 2 * math.pi; L = 0.2 if k % 4 == 0 else 0.08
        cv.path([(c[0] + r * 0.86 * math.cos(q), c[1] + r * 0.86 * math.sin(q)), (c[0] + r * (0.86 - L) * math.cos(q), c[1] + r * (0.86 - L) * math.sin(q))], P.SOFT, a, 1.6, smooth=False)
    tip = (c[0] + r * 0.72 * math.cos(ang), c[1] + r * 0.72 * math.sin(ang)); tl = (c[0] - r * 0.5 * math.cos(ang), c[1] - r * 0.5 * math.sin(ang))
    nv = (-math.sin(ang) * r * 0.08, math.cos(ang) * r * 0.08)
    cv.poly([tip, (c[0] + nv[0], c[1] + nv[1]), (c[0] - nv[0], c[1] - nv[1])], P.WARM, a)
    cv.path([tip, (c[0] + nv[0], c[1] + nv[1]), tl, (c[0] - nv[0], c[1] - nv[1]), tip], P.GOLD, a, 2, smooth=False)


def mirrorframe(cv, C, c, w, h, a=1.0):
    pts = [(c[0] + w / 2 * math.cos(q), c[1] + h / 2 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 70)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, C.P.SOFT * 0.04, a); cv.path(pts, C.P.GOLD, a, 4, smooth=False)
    cv.path([(c[0] + (w / 2 + 16) * math.cos(q), c[1] + (h / 2 + 16) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 70)], C.P.GOLD, 0.5 * a, 1.6, smooth=False)


def keyhole(cv, C, c, s, a=1.0):
    pts = [(c[0] + 30 * s * math.cos(q), c[1] - 20 * s + 30 * s * math.sin(q)) for q in np.linspace(-1.1 * math.pi / 2 + math.pi, 2.6 * math.pi, 30)]
    pts += [(c[0] + 18 * s, c[1] + 60 * s), (c[0] - 18 * s, c[1] + 60 * s)]
    cv.poly(pts, C.P.WARM * 0.6, a); cv.path(pts + [pts[0]], C.P.GOLD, a, 2.4, smooth=False)


def jar_coins(cv, C, c, k, a=1.0):
    P = C.P; x, y = c
    jar = [(x - 90, y - 140), (x - 100, y - 100), (x - 110, y + 120), (x + 110, y + 120), (x + 100, y - 100), (x + 90, y - 140)]
    cv.path(sp(jar, 6), P.SOFT, a, 2.6)
    lvl = y + 110 - 160 * k
    for j in range(int(14 * k) + 1):
        cv.path([(x - 90 + (j % 5) * 40, y + 110 - (j // 5) * 26), (x - 60 + (j % 5) * 40, y + 108 - (j // 5) * 26)], P.GOLD, a, 4, smooth=False)
    with inst(cv):
        for j in range(4):
            ph = (C.lt * 1.2 + j / 4) % 1; cv.circle((x - 20 + j * 14, y - 400 + 400 * ph * ph), 14, P.GOLD, a * (1 - ph * 0.3), 3)
    return lvl


def sprout(cv, C, c, k, a=1.0):
    P = C.P; x, y = c; h = 260 * eo(k)
    st = [(x, y), (x + 10 * math.sin(C.t), y - h * 0.5), (x - 6, y - h)]
    cv.path(st, P.SOFT, a, 3)
    if k > 0.3:
        lk = eo(ramp(k, 0.3, 0.7))
        for sd in (-1, 1):
            b = (x, y - h * 0.45); L = 90 * lk
            cv.path(sp([b, (b[0] + sd * L * 0.6, b[1] - L * 0.5), (b[0] + sd * L, b[1] - L * 0.2), (b[0] + sd * L * 0.4, b[1] + 4), b], 6, True), P.SOFT, a, 2.2, smooth=False)
    if k > 0.7:
        fk = eo(ramp(k, 0.7, 1.0)); c2 = (x - 6, y - h)
        for j in range(6):
            q = j / 6 * 2 * math.pi; cv.path(sp([c2, (c2[0] + 40 * fk * math.cos(q - 0.3), c2[1] + 40 * fk * math.sin(q - 0.3)), (c2[0] + 50 * fk * math.cos(q), c2[1] + 50 * fk * math.sin(q)), (c2[0] + 40 * fk * math.cos(q + 0.3), c2[1] + 40 * fk * math.sin(q + 0.3)), c2], 5), P.WARM, a, 2)
        cv.glow(c2, 60 * fk, P.GOLD, 0.6 * fk)


def sunrise(cv, C, c, r, k, a=1.0):
    P = C.P; y = c[1] + 200 * (1 - eo(k))
    pts = [(c[0] + r * math.cos(q), y + r * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 50)]
    cv.poly(pts, P.WARM * 0.5, a * k); cv.path(pts, P.GOLD, a, 3, smooth=False); cv.glow((c[0], y), r * 1.6, P.GOLD, 0.6 * k * a)
    with inst(cv): godrays(cv, (c[0], y), np.linspace(-math.pi * 0.95, -math.pi * 0.05, 14) + 0.03 * math.sin(C.t), 1400, P.GOLD, 0.07 * k)


# ================================================================ motif shots: fn(C, sh, tx) -> caption layout
def m_bubble(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 940, P, 0.5)
    last = C.lines[-1]; g = C.golds[-1]
    word = ''.join(last[i] for i in g) if g else last[-4:]
    if '在吗' in word:                                  # the only thing that was sent
        A(cv, C, 380, 940, 520, pose('hero', mouth='flat', brow='sad', head=12, uaF=60, faF=150, hF='open'))
        bubble(cv, tx, sh.cam, (980, 420), 300, 150, '在吗', P, 1.0, (-1, 1))
        with inst(cv):
            for k in range(3):
                kk = ramp(C.lt, 1.2 + k * 0.4, 1.6 + k * 0.4); cv.circle((900 + k * 60, 560), 8, P.SOFT, kk * (0.5 + 0.5 * math.sin(C.t * 6 + k)), fill=True)
        return 'R'
    A(cv, C, 420, 940, 520, pose('point', mouth='open', brow='fierce'))
    for k in range(3):
        if C.lt < 0.6 + k * 0.5: break
        bubble(cv, tx, sh.cam, (900 + k * 280, 460 - k * 70), 220, 110, word if k == 2 else '', P, 1.0, (-1, 1))
    with inst(cv):
        x = 700 + 900 * ramp(C.lt, 0.4, 2.2); cv.path([(640, 520), (x, 520 - (x - 640) * 0.2)], P.GOLD, 0.9, 3, smooth=False)
        glint(cv, (x, 520 - (x - 640) * 0.2), 20, P.WARM, 1)
    return 'T'


def m_heart(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    J = A(cv, C, 640, 960, 600, pose('hero', mouth='smile', uaF=60, faF=95, hF='open', uaB=-10))
    c = (J['haF'][0] + 80, J['haF'][1] - 60)
    with inst(cv):
        b = pulse(C.t, FM.quarter(C.t), 0.25); s = 50 + 30 * eo(ramp(C.lt, 0.6, 1.6))
        heart_live(cv, c, s, P, eio(ramp(C.lt, 0.5, 1.0)), 1.2, b)
        for k in range(3):
            u = ((C.lt - 1.0) * 0.6 + k / 3) % 1
            if C.lt > 1.0: cv.circle(c, s + 300 * u, P.GOLD, (1 - u) * 0.5, 1.6)
    return 'R'


def m_bolt(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    for k in range(3): cv.path(sp([(200 + k * 500, 150), (300 + k * 500, 90), (430 + k * 500, 120), (540 + k * 500, 80), (640 + k * 500, 150), (200 + k * 500, 150)], 6), P.LINE, 0.4, 1.4)
    A(cv, C, 560, 960, 580, pose('point', mouth='shout', brow='angry'))
    with inst(cv):
        for k, tb in enumerate((0.8, 1.9, 3.0)):
            kb = ramp(C.lt, tb, tb + 0.35)
            if 0 < kb < 1: bolt(cv, (1100 + k * 160, 120), (1180 + k * 120, 960), P, 1 - kb, k + 3)
            if C.lt > tb: burst(cv, (1180 + k * 120, 960), ramp(C.lt, tb, tb + 0.9), 40, 260, P, 1.0, k, (-math.pi, 0), 200)
    C.flash = 0.35 * max(pulse(C.t, C.t0 + 0.8, 0.2), pulse(C.t, C.t0 + 1.9, 0.2))
    return 'L2'


def m_phone(C, sh, tx):
    cv = sh.cv; P = C.P
    txt = ''.join(C.lines)
    if '电话' in txt:                                   # midnight call: he is already out of the door
        nightsky(cv, C); ground(cv, 960, P, 0.5)
        doorframe(cv, C, 420, 960, 180, 380, 0.8)
        if C.lt < 1.6:
            A(cv, C, 560, 960, 460, pose('hero', uaF=150, faF=170, hF='open', mouth='open'))
            with inst(cv):
                for k in range(3):
                    u = (C.lt * 1.5 + k / 3) % 1; cv.path([(640 + 40 * u + 20 * k, 400 - 30 * k), (660 + 40 * u + 20 * k, 380 - 30 * k)], P.WARM, 1 - u, 2.4, smooth=False)
        else:
            x = 560 + 700 * (C.lt - 1.6); A(cv, C, x, 960, 460, run_cycle((C.lt - 1.6) / 0.42))
            with inst(cv): speedlines(cv, P, C.t, 600, 940, 20, 1800, 0.35)
        return 'R'
    J = A(cv, C, 520, 1080 + 700 * 0.5, 1100, pose('hero', mouth='flat', brow='sad', uaF=70, faF=160, hF='open', head=14))
    from story_frames import phone_big
    msgs = [('在吗', 1, 300, 'sent')]
    if C.lt > 1.0: msgs.append(('其实我', 1, 400, 'deleted' if C.lt > 2.4 else 'typing'))
    if C.lt > 2.8: msgs.append(('没事', 1, 500, 'typing'))
    phone_big(cv, tx, 1040, 560, 380, 680, P, msgs)
    with inst(cv): cv.glow((1040, 560), 380, P.SOFT, 0.18)
    return 'T'


def m_think(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    A(cv, C, 480, 960, 560, pose('hero', mouth='flat', brow='calm', uaF=120, faF=200, hF='fist', head=-6))
    for k, (x, y, r) in enumerate(((640, 420, 14), (700, 360, 22), (780, 300, 30))):
        if C.lt > 0.4 + k * 0.3: cv.circle((x, y), r, P.SOFT, 1, 2)
    if C.lt > 1.3:
        k = eo(ramp(C.lt, 1.3, 1.8)); c = (1080, 260)
        pts = [(c[0] + (260 + 30 * math.sin(q * 7)) * k * math.cos(q), c[1] + (130 + 20 * math.sin(q * 7)) * k * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 80)]
        cv.poly(pts, BLACK, 1.0); cv.path(pts, P.SOFT, 1, 2.4, smooth=False)
        g = C.golds[-1]; word = ''.join(C.lines[-1][i] for i in g) if g else C.lines[-1]
        q = sh.cam([(c[0], c[1] + 20)])[0]
        tx.chars(word, q[0], q[1], F(SERIF_BL, int(min(64, 420 / max(1, len(word))) * sh.cam.s)), (255, 214, 130), C.t, C.t0 + 1.7, 10 ** 6, stagger=0.06)
    return 'B'


def m_letter(C, sh, tx):
    cv = sh.cv; P = C.P
    pg = [(560, 200), (1360, 200), (1360, 900), (560, 900)]
    solid(cv, pg, P.SOFT, 1, 2.4, 0.03)
    for k in range(9): cv.path([(620, 300 + k * 66), (1300, 300 + k * 66)], P.LINE, 0.25, 1, smooth=False)
    with inst(cv):
        rr = np.random.default_rng(C.idx)
        for k in range(5):
            t1 = 0.4 + k * 0.6
            if C.lt < t1: break
            L = 640 * eo(ramp(C.lt, t1, t1 + 0.5)); y = 290 + k * 66
            cv.path([(640 + x, y + 8 * math.sin(x / 9 + k)) for x in np.linspace(0, L, 60)], P.WARM, 0.9, 2, smooth=False)
            if k < 4 and C.lt > t1 + 0.7: cv.path([(630, y - 10), (640 + L, y + 6)], P.GOLD, 0.9, 3, smooth=False)
        k = min(4, int((C.lt - 0.4) / 0.6)); px = 640 + 640 * eo(ramp(C.lt, 0.4 + k * 0.6, 0.9 + k * 0.6)); py = 290 + k * 66
        cv.path([(px, py), (px + 160, py - 260)], P.GOLD, 1, 5, smooth=False); glint(cv, (px, py), 18, P.WARM, 1)
    return 'R2'


def m_clock(C, sh, tx):
    cv = sh.cv; P = C.P
    window(cv, 1240, 220, 360, 320, P, 1.0, moon=False, curtain=True)
    with inst(cv):
        u = C.u; mc = (1290 + 260 * u, 330 - 80 * math.sin(u * math.pi)); cv.circle(mc, 22, P.WARM, 1, fill=True); cv.glow(mc, 60, P.SOFT, 0.5)
        clockface(cv, C, (720, 360), 150, C.lt * 9)
        if u > 0.75: godrays(cv, (1420, 380), np.linspace(math.pi * 0.6, math.pi * 0.9, 6), 900, P.GOLD, 0.06 * ramp(u, 0.75, 1))
    A(cv, C, 1000, 900, 400, pose('sit_hug', mouth='flat', brow='sad'))
    ground(cv, 900, P, 0.4)
    with inst(cv): cv.glow((1100, 830), 50, P.SOFT, 0.5 * (0.8 + 0.2 * math.sin(C.t * 3)))
    return 'L'


def m_cup(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    k = eio(ramp(C.lt, 0.3, 1.6))
    Y(cv, C, 1380, 960, 520, 'stand', -1)
    A(cv, C, 560, 960, 540, pose('hero', mouth='smile', uaF=55, faF=80, hF='open'))
    cup(cv, C, (lerp(1220, 830, k), 640), 1.0)
    with inst(cv):
        if k >= 1: cv.glow((830, 640), 120, P.GOLD, 0.25 * (0.8 + 0.2 * math.sin(C.t * 2)))
    return 'T'


def m_spark(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    Y(cv, C, 1340, 960, 520, 'argue', -1)
    J = A(cv, C, 620, 960, 540, pose('hero', mouth='open', brow='calm', heart=1.0), heart=1 + 0.6 * ramp(C.lt, 1.6, 2.0))
    with inst(cv):
        k = eio(ramp(C.lt, 0.6, 1.7)); p = (lerp(1250, J['chest'][0], k), lerp(620, J['chest'][1], k) - 120 * math.sin(k * math.pi))
        if k < 1:
            for j in range(8): cv.circle((p[0] + j * 10, p[1] + j * 2), 7 - j * 0.7, P.WARM, 1 - j / 8, fill=True)
            glint(cv, p, 22, P.WARM, 1)
        else: burst(cv, J['chest'], ramp(C.lt, 1.7, 2.6), 50, 300, P, 1.0, 3)
    return 'T'


def m_pen(C, sh, tx):
    cv = sh.cv; P = C.P
    pg = [(420, 260), (960, 230), (960, 880), (420, 900)]; pg2 = [(960, 230), (1500, 260), (1500, 900), (960, 880)]
    solid(cv, pg, P.SOFT, 1, 2.4, 0.03); solid(cv, pg2, P.SOFT, 1, 2.4, 0.03)
    for k in range(8): cv.path([(1010, 330 + k * 66), (1450, 330 + k * 66)], P.LINE, 0.25, 1, smooth=False)
    first = C.lines[1] if len(C.lines) > 1 else C.lines[0]
    with inst(cv):
        n = int(ramp(C.lt, 0.5, 2.6) * 7)
        quote = '“你可以的”'
        q = sh.cam([(1230, 360)])[0]
        tx.chars(quote[:max(0, n)], q[0], q[1], F(SERIF_B, int(52 * sh.cam.s)), (255, 214, 130), 1, 0, 99, stagger=0)
        px = 1040 + 380 * ramp(C.lt, 0.5, 2.6); cv.path([(px, 350), (px + 120, 150)], P.GOLD, 1, 5, smooth=False); glint(cv, (px, 350), 16, P.WARM, 1)
        heart_live(cv, (690, 560), 60, P, ramp(C.lt, 2.6, 3.0), 1.0, pulse(C.t, FM.quarter(C.t), 0.25))
    return 'B'


def m_blush(C, sh, tx):
    cv = sh.cv; P = C.P
    hd = -6 + 14 * eio(ramp(C.lt, 0.8, 1.6))
    J = A(cv, C, 860, 1080 + 1700 * 0.55, 1700, pose('hero', mouth='smile', brow='calm', head=hd, wind=(-0.4, 0.1)), heart=0)
    with inst(cv):
        c = J['head']; k = ramp(C.lt, 0.9, 1.6)
        for j in range(3): cv.path([(c[0] + 40 + j * 22, c[1] + 50), (c[0] + 30 + j * 22, c[1] + 70)], P.WARM, k, 3, smooth=False)
        cv.glow((c[0] + 60, c[1] + 60), 60, P.WARM, 0.4 * k)
        for j in range(5):
            ph = (C.lt * 0.4 + j / 5) % 1; hp = (c[0] + 260 + j * 40, c[1] - 100 - 300 * ph)
            if C.lt > 1.2: heart_live(cv, hp, 14, P, (1 - ph) * 0.8, 0.5)
    return 'R'


def m_gift(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    txt = ''.join(C.lines)
    Y(cv, C, 1380, 960, 520, 'stand', -1)
    A(cv, C, 560, 960, 540, pose('hero', mouth='smile', uaF=58, faF=78, hF='open'))
    k = eio(ramp(C.lt, 0.2, 1.4)); c = (lerp(820, 1120, k), 650)
    if '早餐' in txt:
        bag = [(c[0] - 60, c[1] - 60), (c[0] + 60, c[1] - 60), (c[0] + 70, c[1] + 70), (c[0] - 70, c[1] + 70)]
        solid(cv, bag, P.SOFT, 1, 2.4, 0.05); cv.path(sp([(c[0] - 30, c[1] - 60), (c[0], c[1] - 110), (c[0] + 30, c[1] - 60)], 5), P.SOFT, 1, 2.2)
        cup(cv, C, (c[0] + 120, c[1] + 20), 0.7)
        with inst(cv): heart_live(cv, (c[0], c[1] + 5), 22, P, ramp(C.lt, 1.4, 1.8), 0.6)
    else:
        giftbox(cv, C, c, 1.0, 1.0, ramp(C.lt, 1.6, 2.4))
        if '加倍' in txt:
            with inst(cv):
                for j in range(int(ramp(C.lt, 2.2, 3.4) * 4)):
                    giftbox(cv, C, (c[0] - 160 + j * 110, c[1] - 220 - 40 * (j % 2)), 0.45, 0.8)
    return 'T'


def m_umbrella(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    with inst(cv): rain_live(cv, P, C.t, 0.45, 320, 0.12, 4)
    Y(cv, C, 1180, 960, 520, 'turned' if '难过' in ''.join(C.lines) else 'stand', -1)
    if C.lt < 1.4:
        x = lerp(200, 1000, eo(ramp(C.lt, 0, 1.4))); A(cv, C, x, 960, 540, run_cycle(C.lt / 0.42))
    else:
        x = 1000; A(cv, C, x, 960, 540, pose('hero', uaF=165, faF=175, hF='fist', mouth='smile'))
    hx = x + 0.07 * 540; top = (hx + 60, 960 - 540 * 1.05)
    k = eio(ramp(C.lt, 1.2, 1.8))
    ur = 300 * k
    cv.path([(hx, 960 - 540 * 0.62), (hx + 30, top[1] + 20)], P.LINE, 1, 2.4, smooth=False)
    if ur > 10:
        can = [(top[0] + ur * math.cos(q), top[1] + 40 + ur * 0.45 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 30)]
        sc = [can[0]] + [(top[0] - ur + j * 2 * ur / 6 + ur / 6, top[1] + 40 + 22 * (1 - abs(j - 2.5) / 3)) for j in range(6)] + [can[-1]]
        cv.poly(can + sc[::-1], BLACK, 1.0); cv.path(can, P.WARM, 1, 3, smooth=False); cv.path(sc, P.WARM, 1, 2, smooth=False)
        with inst(cv): cv.glow((top[0], top[1] + 200), 220, P.GOLD, 0.25 * k)
    return 'R'


def m_flame(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    with inst(cv):
        for k in range(9):
            x = 260 + k * 170; h = (200 + 160 * ((k * 0.37) % 1)) * (0.6 + 0.4 * eo(ramp(C.lt, 0.2 + 0.08 * k, 1.0 + 0.08 * k))) * (1 + 0.06 * math.sin(C.t * 8 + k))
            flame(cv, x, 960, h, P.GOLD, 0.25)
        sparks_live(cv, (900, 900), C.t, 50, 20, 800, P, 0.8, 9, (-math.pi * 0.9, -math.pi * 0.1), 0.5, 1.4)
    txt = ''.join(C.lines)
    p = pose('stand_arm', mouth='grit') if '不服输' in txt else pose('burst', mouth='shout') if '来劲' in txt else pose('point', mouth='shout', brow='angry')
    A(cv, C, 700, 960, 600, p)
    return 'R'


def m_wall(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    wall(cv, 1000, 180, 960, 120, P, 1.0)
    txt = ''.join(C.lines)
    if '低不下头' in txt:
        Y(cv, C, 1340, 960, 520, 'turned', -1)
        A(cv, C, 680, 960, 560, pose('stand_arm', head=-12, mouth='grit', brow='fierce'), d=1)
        with inst(cv):
            if C.lt > 1.2: cv.path(sp([(780, 520), (820, 470), (860, 520)], 5), P.WARM, 0.7, 2)
    else:
        A(cv, C, 1130, 960, 440, pose('sit_hug', mouth='sad', brow='sad'), tear=True)
        Y(cv, C, 600, 960, 520, 'walk', 1, 0.55)
        with inst(cv):
            tears(cv, C, (1210, 640), 0.8, 2, 0.8)
    return 'L' if '低不下头' not in txt else 'T'


def m_tears(C, sh, tx):
    cv = sh.cv; P = C.P
    txt = ''.join(C.lines)
    J = A(cv, C, 760, 1080 + 1700 * 0.55, 1700, pose('hero', mouth='sad', brow='sad', head=10), tear=False, heart=0)
    with inst(cv):
        c = J['head']; tears(cv, C, (c[0] + 0.078 * 1700 * 0.46, c[1] + 40), 0.5, 3, 1.0)
        if '关上门' in txt:
            cv.poly([(1300, 0), (W, 0), (W, H), (1300, H)], BLACK, 0.6 * ramp(C.lt, 0, 0.8))
        if '歇一歇' in txt:
            hand = [(W + 50, 300), (1250, 320), (1150, 330), (1120, 360), (1250, 380), (W + 50, 400)]
            k = eo(ramp(C.lt, 1.6, 2.6)); hand = [(x + 500 * (1 - k), y + 300) for x, y in hand]; solid(cv, sp(hand, 4), P.SOFT, 1, 2.2, 0.05)
    return 'R'


def m_smile(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    txt = ''.join(C.lines)
    if '打开门' in txt:
        doorframe(cv, C, 760, 960, 260, 520, eio(ramp(C.lt, 0.3, 1.2)))
        A(cv, C, 760, 960, 480, pose('hero', mouth='smile', uaF=150, faF=170, hF='open'))
        with inst(cv): burst(cv, (760, 600), ramp(C.lt, 1.0, 2.0), 40, 300, P, 1.0, 4)
        return 'R'
    A(cv, C, 760, 960, 600, pose('hero', mouth='smile', brow='calm'), heart=1.3)
    with inst(cv):
        Y(cv, C, 1300, 960, 500, 'stand', -1, 0.8)
        cv.glow((1050, 600), 300, P.GOLD, 0.12)
    return 'T'


def m_broken(C, sh, tx):
    cv = sh.cv; P = C.P
    k = eio(ramp(C.lt, 1.0, 2.2)); c = (960, 560); s = 200
    for sd in (-1, 1):
        hp = [(c[0] + s * u, c[1] + s * v) for u, v in heart_pts(0, 0, 1.0, 60) if (u >= 0) == (sd > 0)]
        crack = [(c[0], c[1] - s * 0.55), (c[0] - 20, c[1] - s * 0.2), (c[0] + 20, c[1] + s * 0.1), (c[0] - 10, c[1] + s * 0.45), (c[0], c[1] + s * 0.95)]
        hp = hp + crack[::-1] if sd > 0 else hp + crack
        hp = [(x + sd * 60 * k, y + 30 * k * k) for x, y in hp]
        rot = sd * 0.15 * k; hp = [(c[0] + (x - c[0]) * math.cos(rot) - (y - c[1]) * math.sin(rot), c[1] + (x - c[0]) * math.sin(rot) + (y - c[1]) * math.cos(rot)) for x, y in hp]
        cv.poly(hp, P.WARM * 0.4, 1); cv.path(hp + [hp[0]], P.WARM, 1, 3, smooth=False)
    with inst(cv):
        if C.lt > 1.0: burst(cv, c, ramp(C.lt, 1.0, 2.0), 40, 300, P, 1, 5)
    return 'T'


def m_mirror(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    mirrorframe(cv, C, (1180, 520), 420, 640)
    A(cv, C, 600, 960, 560, pose('hero', mouth='smile', brow='calm'), d=1)
    with inst(cv):
        a = 0.5 * ramp(C.lt, 0.8, 1.6)
        A(cv, C, 1180, 820, 380, pose('sit_hug', mouth='sad', brow='sad'), d=-1, a=a, heart=1.4)
        cv.glow((1180, 560), 200, P.SOFT, 0.15 * ramp(C.lt, 0.8, 1.6))
    return 'B'


def m_sigh(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    lamp(cv, 1260, 960, 420, P, 0.8, -1)
    k = eio(ramp(C.lt, 0.8, 1.6))
    A(cv, C, 720, 960, 560, mix(pose('hero', mouth='smile'), pose('hero', mouth='smile', brow='sad', lean=6, head=14, uaF=2, uaB=-2), k))
    with inst(cv):
        for j in range(3):
            ph = ramp(C.lt, 1.1 + j * 0.15, 2.4 + j * 0.15); c = (800 + 120 * ph, 460 - 60 * ph)
            if 0 < ph < 1: cv.circle(c, 20 + 40 * ph, P.SOFT, (1 - ph) * 0.6, 1.6)
    return 'R'


def m_moon(C, sh, tx):
    cv = sh.cv; P = C.P; nightsky(cv, C, 160, 600)
    window(cv, 1080, 160, 480, 420, P, 1.0, moon=True, curtain=True)
    bed = [(300, 820), (1000, 820), (1000, 900), (300, 900)]; solid(cv, bed, P.LINE, 0.8, 2, 0.04)
    A(cv, C, 640, 830, 420, pose('sit_hug', mouth='flat', brow='sad'))
    with inst(cv):
        cv.poly([(1080, 580), (1560, 580), (1300, 960), (760, 960)], P.SOFT * 0.06, 1, layer=cv.F)
    return 'L2'


def m_sprout(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 940, P, 0.5)
    sunrise(cv, C, (1400, 940), 180, eio(ramp(C.lt, 0.0, 2.5)))
    sprout(cv, C, (1000, 940), ramp(C.lt, 0.5, 2.8))
    k = eio(ramp(C.lt, 1.6, 2.6))
    A(cv, C, 620, 940, 540, mix(pose('sit_hug', mouth='sad', brow='sad'), pose('hero', mouth='smile', brow='calm'), k))
    return 'L2'


def m_chain(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    txt = ''.join(C.lines)
    if '最狠' in txt:
        Y(cv, C, 1340, 960, 520, 'turned', -1)
        A(cv, C, 640, 960, 560, pose('point', mouth='shout', brow='angry'))
        with inst(cv):
            for k in range(4):
                t1 = 0.4 + k * 0.45; x = 860 + 500 * eo(ramp(C.lt, t1, t1 + 0.4))
                if C.lt > t1: cv.path([(x - 60, 470 + k * 30), (x, 470 + k * 30), (x - 20, 450 + k * 30)], P.WARM, 1, 3, smooth=False); glint(cv, (x, 470 + k * 30), 18, P.WARM, 1)
        return 'T'
    A(cv, C, 900, 960, 560, pose('stand_arm', mouth='grit', brow='angry'))
    brk = ramp(C.lt, 2.0, 3.2)
    with inst(cv):
        for j, (p0, p1) in enumerate((((300, 400), (1500, 700)), ((300, 760), (1500, 460)), ((400, 580), (1400, 600)))):
            chain(cv, C, p0, p1, 14, eio(ramp(C.lt, 0.3 + j * 0.3, 0.9 + j * 0.3)), brk, j)
        if brk > 0: burst(cv, (900, 600), brk, 80, 600, P, 1, 4)
    C.flash = 0.25 * pulse(C.t, C.t0 + 2.0, 0.3)
    return 'T'


def m_feather(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    A(cv, C, 700, 960, 560, pose('hero', mouth='flat', brow='calm', uaF=40, faF=110, hF='open'))
    with inst(cv):
        y = lerp(80, 560, eio(ramp(C.lt, 0, 3.4))); x = 850 + 80 * math.sin(C.lt * 1.8)
        feather(cv, C, (x, y), 1.4, 0.5 * math.sin(C.lt * 1.8))
        if '三秒' in ''.join(C.lines):
            for k in range(3):
                tk = 1.2 + k * 0.7
                if C.lt > tk:
                    q = sh.cam([(1100 + k * 90, 300)])[0]
                    tx.chars(str(3 - k), q[0], q[1], F(SERIF_BL, int(70 * (1 + 0.3 * pop(C.t, C.t0 + tk, 0.3)))), (255, 214, 130), 1, 0, 99, stagger=0)
    return 'R'


def m_people2(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    txt = ''.join(C.lines)
    Y(cv, C, 1180, 960, 520, 'stand', -1)
    if '掉眼泪' in txt or '信任' in txt:
        J = A(cv, C, 820, 960, 540, pose('hero', mouth='sad', brow='sad', head=12), tear='掉眼泪' in txt)
        with inst(cv):
            cv.glow((1000, 600), 260, P.GOLD, 0.15)
            if '信任' in txt: heart_live(cv, (1000, 440), 40, P, ramp(C.lt, 1.0, 1.6), 1.0, pulse(C.t, FM.quarter(C.t), 0.3))
        return 'L'
    A(cv, C, 700, 960, 540, pose('hero', mouth='smile', uaF=60, faF=80, hF='open'))
    with inst(cv):
        for j in range(3):
            t1 = 0.6 + j * 0.7; k = eo(ramp(C.lt, t1, t1 + 0.6))
            if C.lt > t1:
                if j == 0: cup(cv, C, (lerp(820, 1040, k), 640), 0.5, steam=False)
                elif j == 1: giftbox(cv, C, (lerp(820, 1040, k), 540), 0.5)
                else: heart_live(cv, (lerp(820, 1040, k), 430), 30, P, 1.0, 0.8)
    return 'T'


def m_road(C, sh, tx):
    cv = sh.cv; P = C.P
    hz = 480
    cv.path([(960, hz), (200, 1080)], P.LINE, 0.8, 2.4, smooth=False); cv.path([(960, hz), (1720, 1080)], P.LINE, 0.8, 2.4, smooth=False)
    cv.path([(-200, hz), (W + 200, hz)], P.LINE, 0.4, 1.4, smooth=False)
    with inst(cv):
        for k in range(10):
            u = ((k / 10) + C.lt * 0.25) % 1; y = hz + (1080 - hz) * u ** 2; w = 8 * u + 1
            cv.path([(960, y), (960, y + 60 * u * u)], P.WARM, 0.8, w, smooth=False)
        stars_live(cv, P, C.t, 100, 420, 6, 0.5)
        for k in range(3):
            t1 = 0.8 + k * 0.6; pin = (1200 - k * 260, 520 + k * 50)
            if C.lt > t1:
                s = 0.8 + 0.4 * pop(C.t, C.t0 + t1, 0.3)
                cv.path(sp([(pin[0], pin[1]), (pin[0] - 20 * s, pin[1] - 40 * s), (pin[0], pin[1] - 62 * s), (pin[0] + 20 * s, pin[1] - 40 * s), (pin[0], pin[1])], 5), P.GOLD, 1, 2.4)
                cv.circle((pin[0], pin[1] - 40 * s), 7 * s, P.WARM, 1, fill=True)
    A(cv, C, 960, 900 + 40 * math.sin(C.lt * 0.5), 300, walk_cycle(C.lt / 0.9), d=1)
    return 'T'


def m_compass(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    ang = -math.pi / 2 + 6 * math.exp(-C.lt * 0.9) * math.sin(C.lt * 5)
    compass(cv, C, (1180, 440), 220, ang)
    A(cv, C, 600, 960, 560, pose('hero', mouth='smile', brow='calm', wind=(-1.2, -0.3)))
    with inst(cv):
        rr = np.random.default_rng(3)
        for k in range(14):
            y = rr.uniform(200, 900); x = (rr.uniform(0, W) + 900 * C.lt) % (W + 400) - 200
            cv.path(sp([(x - 200, y), (x - 100, y - 10 * math.sin(C.t + k)), (x, y)], 5), P.SOFT, 0.35, 1.4)
    return 'B'


def m_rings(C, sh, tx):
    cv = sh.cv; P = C.P; nightsky(cv, C, 120, 700)
    ground(cv, 960, P, 0.4)
    A(cv, C, 620, 960, 520, pose('hero', mouth='smile', uaF=110, faF=130, hF='open'))
    with inst(cv):
        u = C.lt / max(1, C.dur - 0.3); q = u * 2 * math.pi
        bx, by = 620 + 600 * math.sin(q), 380 - 200 * math.sin(2 * q) * 0.5 - 100 * (1 - math.cos(q)) * 0.5
        wing = 30 * math.sin(C.t * 14)
        cv.path([(bx - 40, by - wing), (bx, by), (bx + 40, by - wing)], P.WARM, 1, 3)
        glint(cv, (bx, by), 16, P.WARM, 0.8)
        for k in range(30):
            uu = max(0, u - k * 0.006); qq = uu * 2 * math.pi
            cv.circle((620 + 600 * math.sin(qq), 380 - 100 * math.sin(2 * qq) - 50 * (1 - math.cos(qq))), 2, P.GOLD, (1 - k / 30) * 0.6, fill=True)
    return 'R'


def m_crowd(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    for k in range(10): cv.circle((160 + k * 170, 200 + 30 * math.sin(k)), 6, P.WARM, 1, fill=True)
    cv.path(sp([(160 + k * 170, 200 + 30 * math.sin(k)) for k in range(10)], 4), P.LINE, 0.5, 1.2)
    for k, x in enumerate((240, 420, 1120, 1300, 1480)): figure(cv, x, 960, 420, 'argue' if k % 2 else 'stand', P.LINE * 0.9, 0.6, d=1 if x < 960 else -1, P=P, th=1.6)
    A(cv, C, 780, 960, 480, pose('hero', mouth='open', uaF=150, faF=165, hF='open', uaB=-150, faB=-165, hB='open'))
    with inst(cv):
        for k in range(10): cv.glow((160 + k * 170, 200 + 30 * math.sin(k)), 30, P.GOLD, 0.5 + 0.5 * math.sin(C.t * 3 + k))
        sparks_live(cv, (780, 300), C.t, 30, 10, 500, P, 0.6, 2, (0, 2 * math.pi), 0.3, 1.6)
    return 'T'


def m_alone(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    skyline(cv, 960, P, 0.35, 4, -200, W + 200, 160, 420, 0.1)
    off = -260 * C.lt
    for k in range(4): lamp(cv, 400 + k * 520 + off * 0.2, 960, 380, P, 0.8, -1, cone=True)
    A(cv, C, 900, 960, 460, walk_cycle(C.lt / 1.1, mouth='flat', brow='sad', head=10))
    with inst(cv):
        for k in range(6):
            x = 900 - 80 - k * 90 - (C.lt * 80) % 90; cv.path([(x, 966), (x + 26, 966)], P.LINE, 0.4 * (1 - k / 6), 2, smooth=False)
    return 'T'


def m_key(C, sh, tx):
    cv = sh.cv; P = C.P
    hp = [(960 + 260 * u, 560 + 260 * v) for u, v in heart_pts(0, 0, 1.0, 60)]
    cv.path(hp + [hp[0]], P.WARM, 1, 3, smooth=False)
    keyhole(cv, C, (960, 560), 1.4)
    with inst(cv):
        k = eio(ramp(C.lt, 0.5, 1.6)); kx = lerp(1500, 1020, k); rot = ramp(C.lt, 1.7, 2.3) * math.pi / 2
        cv.circle((kx + 120, 540), 40, P.GOLD, 1, 3)
        cv.path([(kx + 80, 540), (kx, 540)], P.GOLD, 1, 4, smooth=False)
        for j in range(2): cv.path([(kx + 20 + j * 24, 540), (kx + 20 + j * 24, 540 + 24 * math.cos(rot))], P.GOLD, 1, 4, smooth=False)
        if C.lt > 2.3:
            kk = ramp(C.lt, 2.3, 3.2); godrays(cv, (960, 560), np.linspace(0, 2 * math.pi, 16), 900 * kk, P.GOLD, 0.1 * kk)
            cv.poly(hp, P.WARM * 0.35, kk)
    return 'B'


def m_door(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    doorframe(cv, C, 1200, 960, 260, 520, 0.35)
    with inst(cv):
        for k in range(4): figure(cv, 1160 + k * 30 - 60, 900, 220, 'argue', P.LINE * 0.7, 0.3, d=1 if k % 2 else -1, P=P, th=1.2)
    A(cv, C, 600 - 60 * C.lt, 960, 540, walk_cycle(C.lt / 1.1, mouth='flat'), d=-1)
    return 'L2'


def m_target(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    target(cv, C, (1380, 520), 200)
    A(cv, C, 560, 960, 560, pose('point', mouth='grit', brow='fierce'))
    with inst(cv):
        k = ramp(C.lt, 1.4, 1.9)
        x = lerp(760, 1370, k); cv.path([(x - 120, 520), (x, 520)], P.GOLD, 1, 3, smooth=False); cv.path([(x - 120, 520), (x - 140, 505)], P.GOLD, 1, 2, smooth=False)
        if k >= 1: burst(cv, (1380, 520), ramp(C.lt, 1.9, 2.8), 40, 300, P, 1, 6)
    return 'T'


def m_mountain(C, sh, tx):
    cv = sh.cv; P = C.P; nightsky(cv, C, 100, 400)
    mountain(cv, C)
    k = eio(ramp(C.lt, 0.4, C.dur - 0.5)); x = lerp(640, 900, k); y = lerp(760, 380, k)
    A(cv, C, x, y, 220, run_cycle(C.lt / 0.6, base='run'), d=1)
    with inst(cv): glint(cv, (980, 170), 24 + 10 * math.sin(C.t * 3), P.WARM, 1)
    return 'R'


def m_hourglass(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    k = ramp(C.lt, 0.3, C.dur)
    hourglass(cv, C, (1260, 560), 1.3, k)
    A(cv, C, 600, 960, 540, pose('hero', mouth='flat', brow='sad'), heart=lerp(1.0, 0.5, k))
    with inst(cv): flame(cv, 640, 360, lerp(160, 50, k), P.GOLD, 0.6)
    return 'L2'


def m_stairs(C, sh, tx):
    cv = sh.cv; P = C.P
    step = stairs(cv, C, 8, 300, 980, 150, 80)
    k = min(7.0, C.lt / (E8 * 4))                    # one step per beat-group, legs alternate, body glides up the diagonal
    w = 0.5 - 0.5 * math.cos(math.pi * k)
    p = mix(pose('climb'), mirror(pose('climb')), w)
    x = 300 + (k + 0.35) * 150; y = 980 - k * 80 - 6 * abs(math.sin(math.pi * k))
    A(cv, C, x, y, 360, p, heart=0.7)
    with inst(cv): flame(cv, x + 10, y - 300, 50 + 10 * math.sin(C.t * 8), P.GOLD, 0.5) if STYLE_FLAME[0] else glint(cv, (x + 10, y - 300), 20, P.WARM, 0.8)
    return 'L'


def m_coins(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    jar_coins(cv, C, (1220, 820), ramp(C.lt, 0.2, C.dur))
    A(cv, C, 600, 960, 540, pose('hero', mouth='smile', uaF=150, faF=165, hF='open', wind=(-1.0, -0.2)))
    with inst(cv):
        for k in range(3):
            q = C.lt * 0.6 + k; bx, by = 600 + 400 * math.cos(q) - 100, 260 + 60 * math.sin(q * 2)
            wing = 22 * math.sin(C.t * 12 + k); cv.path([(bx - 30, by - wing), (bx, by), (bx + 30, by - wing)], P.WARM, 0.9, 2.4)
    return 'T'


def m_sweat(C, sh, tx):
    cv = sh.cv; P = C.P
    J = A(cv, C, 860, 1080 + 1500 * 0.55, 1500, pose('hero', mouth='smile', brow='sad', uaF=80, faF=150, hF='fist', head=-4), heart=0)
    with inst(cv):
        c = J['head']; ph = (C.lt * 0.5) % 1
        drop = sp([(c[0] - 80, c[1] - 60 + 120 * ph), (c[0] - 66, c[1] - 30 + 120 * ph), (c[0] - 80, c[1] - 16 + 120 * ph), (c[0] - 94, c[1] - 30 + 120 * ph)], 4, True)
        cv.path(drop + [drop[0]], P.SOFT, 1 - ph * 0.5, 2.2, smooth=False)
    return 'R'


def m_sun(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    sunrise(cv, C, (960, 960), 260, eio(ramp(C.lt, 0, 2.6)))
    A(cv, C, 960, 960, 520, pose('hero', mouth='smile', brow='calm'), heart=1.5)
    with inst(cv):
        J = skeleton(960, 960, 520, pose('hero'), 1); c = J['sc'] - J['up'] * 0.075 * 520
        heart_live(cv, (c[0], c[1]), 40 + 20 * eo(ramp(C.lt, 1.6, 2.6)), P, ramp(C.lt, 1.4, 2.0), 1.4, pulse(C.t, FM.quarter(C.t), 0.3))
    return 'T'


def m_shield(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    A(cv, C, 760, 960, 560, pose('stand_arm', mouth='grit', brow='fierce', uaF=70, faF=60), armor=1.0, heart=1.2)
    sc = (1000, 600)
    sh_pts = [(sc[0] - 110, sc[1] - 170), (sc[0] + 110, sc[1] - 170), (sc[0] + 110, sc[1] + 20), (sc[0], sc[1] + 170), (sc[0] - 110, sc[1] + 20)]
    solid(cv, sp(sh_pts, 4, True), P.GOLD, 1, 3, 0.1)
    with inst(cv):
        rr = np.random.default_rng(C.idx)
        for k in range(6):
            t1 = 0.8 + k * 0.4; y = 480 + rr.uniform(0, 240)
            if C.lt < t1: x = 1120 + (t1 - C.lt) * 2400; cv.path([(x, y), (x + 120, y)], P.LINE, 0.8, 1.8, smooth=False)
            else: burst(cv, (1110, y), ramp(C.lt, t1, t1 + 0.5), 14, 120, P, 1, k)
    return 'T'


def m_mask(C, sh, tx): return m_shield(C, sh, tx)


# ---------------------------------------------------------------- '?' and '*' beats
def m_question(C, sh, tx):
    cv = sh.cv; P = PV; v = C.idx % 3
    with inst(cv): stars_live(cv, P, C.t, 220, 1000, 2 + C.idx % 7, 0.7)
    if v == 0:                                       # constellation question mark over a small figure
        q = [(840, 360), (850, 260), (930, 200), (1030, 220), (1070, 300), (1020, 380), (960, 430), (960, 520)]
        ground(cv, 1000, P, 0.5); draw_aries(cv, 960, 1000, 220, pose('lookback'), P=P, col=P.SOFT, heart=0.6)
        with inst(cv):
            for i in range(len(q)):
                t1 = 0.4 + i * E8
                if C.lt < t1: continue
                glint(cv, q[i], 22 + 16 * pop(C.t, C.t0 + t1, 0.3), P.WARM, 1)
                if i: cv.path([q[i - 1], q[i]], P.SOFT, 0.8, 1.6, frac=eo(ramp(C.lt, t1, t1 + 0.2)), smooth=False)
            if C.lt > 0.4 + 9 * E8: glint(cv, (960, 610), 30, P.WARM, 1)
        return 'Rq'
    if v == 1:                                       # high angle: tiny figure in a circle of light, the ? drawn on the ground
        cv.path([(960 + 520 * math.cos(q), 620 + 200 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 90)], P.SOFT, 0.5, 1.6, smooth=False)
        qm = sp([(880, 520), (900, 470), (960, 450), (1020, 470), (1030, 520), (980, 570), (960, 610), (960, 660)], 6)
        cv.path(qm, P.WARM, 1, 5); cv.circle((960, 720), 10, P.WARM, 1, fill=True)
        draw_aries(cv, 1180, 700, 140, pose('lookback'), P=P, col=P.SOFT, heart=0.6)
        with inst(cv): cv.glow((960, 620), 400, P.SOFT, 0.1)
        return 'Tq'
    # v == 2: extreme close-up of the eye, a star reflected in it
    J = draw_aries(cv, 700, 1080 + 3400 * 0.66, 3400, pose('hero', mouth='flat', brow='calm', head=-14), P=P, col=P.SOFT, heart=0)
    with inst(cv): glint(cv, (J['head'][0] + 0.078 * 3400 * 0.5, J['head'][1] - 40), 30 + 10 * math.sin(C.t * 3), P.WARM, 1)
    return 'Rq'


def m_reveal(C, sh, tx):
    cv = sh.cv; P = C.P; v = C.idx % 3
    k = eio(ramp(C.lt, 0, 2.0))
    with inst(cv):
        stars_live(cv, P, C.t, 200, 800, 5 + C.idx % 4, 0.8)
        milkyway(cv, P, (-200, 160), (W + 200, 380), 140, 6 + C.idx % 3, 0.6)
    ground(cv, 980, P, 0.5)
    txt = ''.join(C.lines)
    two = any(w in txt for w in ('你', '在乎', '有我', '真心', '对不起'))
    if two: Y(cv, C, 940, 980, 420, 'stand', -1, 0.8)
    A(cv, C, 560 if two else 700, 980, 440, pose('hero', mouth='smile', brow='calm', wind=(-0.8 + 0.1 * math.sin(C.t * 2), -0.2)), heart=1.4)
    with inst(cv):
        c = (700, 330) if not two else (750, 340)
        if v == 0:
            hs = 90 * k * (1 + 0.08 * pulse(C.t, FM.quarter(C.t), 0.3))
            heart_live(cv, c, hs, P, k, 1.6)
            godrays(cv, c, np.linspace(0, 2 * math.pi, 20) + C.t * 0.1, 1200, P.GOLD, 0.07 * k)
        elif v == 1:
            cv.poly([(c[0] - 40, 0), (c[0] + 40, 0), (c[0] + 160, 980), (c[0] - 160, 980)], P.GOLD * 0.12, k, layer=cv.F)
            sparks_live(cv, (c[0], 900), C.t, 50, 10, 900, P, 0.8 * k, 3, (-math.pi * 0.6, -math.pi * 0.4), 0.4, 2.0)
        else:
            for j in range(3):
                u = ((C.lt * 0.35) + j / 3) % 1; cv.circle(c, 60 + 700 * u, P.GOLD, (1 - u) * 0.6 * k, 2)
            heart_live(cv, c, 50 * k, P, k, 1.4)
        burst(cv, c, ramp(C.lt, 0, 1.6), 120, 900, P, 1, C.idx)
    C.flash = 0.35 * pulse(C.t, C.t0, 0.4)
    return 'Cr'


MOTIFS = {k[2:]: v for k, v in globals().items() if k.startswith('m_') and callable(v)}


# ================================================================ card -> frame
LAYOUT = {  # x, y0, size
    'R': (1460, 300, 62), 'L': (460, 260, 62), 'L2': (480, 200, 62), 'R2': (1600, 260, 54), 'T': (960, 170, 62), 'B': (960, 860, 58),
    'Rq': (1460, 720, 58), 'Tq': (960, 170, 62), 'Cr': (1450, 380, 72),
}


def card_scene(C, t, n, tx):
    C.t, C.lt, C.t0, C.dur = t, t - T(C.m0), T(C.m0), T(C.m1) - T(C.m0); C.u = cl(C.lt / C.dur); C.flash = 0.0
    mv = C.idx % 5; u = eio(C.u)
    s, cx, cy = [(lerp(1.0, 1.1, u), 960, 560), (lerp(1.12, 1.0, u), 960, 540), (1.05, lerp(900, 1020, u), 550),
                 (1.05, lerp(1020, 900, u), 550), (lerp(1.0, 1.08, u), 960, lerp(600, 520, u))][mv]
    if C.kind == 'r': s, cx, cy = lerp(1.35, 1.0, eio(ramp(C.lt, 0, 2.4))), 960, lerp(420, 540, eio(ramp(C.lt, 0, 2.4)))
    if C.kind == 'q': s, cx, cy = lerp(1.0, 1.15, u), 960, 560
    if C.dur > 5.6 and C.kind == 'n' and C.lt > C.dur * 0.55:        # second angle on long cards
        s *= 1.12
    sh = sh_for(f'c{C.idx}', t, C.m0, Cam(s, cx, cy), 1.3, 2.2, 0.6)
    if C.kind == 'q': fn = m_question
    elif C.kind == 'r': fn = m_reveal
    else: fn = MOTIFS.get(C.motif, m_heart)
    lay = fn(C, sh, tx)
    P = PV if C.kind == 'q' else C.P
    x, y0, size = LAYOUT[lay]
    col = P.WHITE
    for k, (line, g) in enumerate(zip(C.lines, C.golds)):
        m_in = C.m0 + 1 + 4 * k
        FM.cap(tx, line, x, y0 + k * int(size * 1.42), size if C.kind != 'r' or k else size - 10, m_in, C.m1 - 0.4, 0.5, g, t=t, col=col)
    return sh, P, 0.6, C.flash + (0.15 * pulse(t, C.t0, 0.3) if C.first else 0.0)


def _count():
    V._count()
    orig = Shot.__init__
    for C in CARDS:
        key = f'c{C.idx}'; _COUNTS[key] = (10 ** 6, 10 ** 6); box = {}
        def spy(self, *a, **k):
            orig(self, *a, **k); box['cv'] = self.cv
        Shot.__init__ = spy
        try: card_scene(C, T(C.m1) - 0.02, C.m1 - 0.02 / E8, Text(PF))
        finally: Shot.__init__ = orig
        c = box['cv'].cnt; _COUNTS[key] = (max(c['bg'], 1), max(c['fg'], 1))


def frame(t):
    if not _COUNTS: _count()
    n = t / E8
    if n < FIRST_END:
        img = V.frame(t)
        return img
    tx = Text(PF)
    C = CARDS[-1]
    for c in CARDS:
        if n < c.m1: C = c; break
    sh, P, glow, flash = card_scene(C, t, n, tx)
    img = sh.cv.composite(P.BG * 0.6, flash, glow=glow) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    img = tx.blend(np.clip(img, 0, 1.6).astype(np.float32))
    img *= (1 - ramp(t, T(END) - 2.5, T(END) - 0.05))
    return np.clip(img * 255, 0, 255).astype(np.uint8)


# ================================================================ audio
def build_audio(music, out, duration):
    """first minute exactly as approved, then the track keeps looping on whole bars; dips on '?' beats, lifts on '*'"""
    import wave
    phase, e8 = R.grid(music); st = phase + V.MUSIC_START * e8; dr = T(V.DROP)
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, 'a.wav'); full = os.path.join(tmp, 'f.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.4f}', '-t', f'{dr:.4f}', '-i', music, '-af', 'lowpass=f=900,volume=0.55,afade=t=in:d=0.3', '-ac', '1', '-ar', str(sfx.SR), a], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', music, '-ac', '1', '-ar', str(sfx.SR), full], check=True)
    def rd(p):
        w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    pre, src = rd(a), rd(full)
    s0 = int((st + dr) * sfx.SR); bar = 8 * e8
    nb = int((len(src) / sfx.SR - (st + dr) - 0.05) / bar); s1 = s0 + int(nb * bar * sfx.SR)
    loop = src[s0:s1].copy(); xf = int(0.02 * sfx.SR); loop[:xf] *= np.linspace(0, 1, xf); loop[-xf:] *= np.linspace(1, 0, xf)
    need = int((duration - dr) * sfx.SR) + 1
    body = np.tile(loop, need // len(loop) + 1)[:need]
    mus = np.concatenate([pre, body])
    tt = np.arange(len(mus)) / sfx.SR
    g = np.ones_like(mus)
    def env(t0, t1, depth, fade=0.25):
        return depth * np.clip((tt - t0) / fade, 0, 1) * np.clip((t1 - tt) / fade, 0, 1)
    for (a_, b_, dep, fd) in getattr(V, 'DUCKS', [(130, 138, 0.75, 0.1), (156, 178, 0.35, 0.3)]): g -= env(T(a_), T(b_), dep, fd)
    for C in CARDS:
        if C.kind == 'q': g -= env(T(C.m0), T(C.m1), 0.45)
    g = np.clip(g, 0.15, 1); fo = np.clip((duration - tt) / 3.0, 0, 1); mus = mus * g * fo
    # first-minute effects + card effects
    V_cues = []
    V2 = V
    cues = []
    thump = lambda d=0.4: (np.sin(2 * np.pi * 55 * np.arange(int(d * sfx.SR)) / sfx.SR) * np.exp(-np.arange(int(d * sfx.SR)) / sfx.SR * 9)).astype(np.float32)
    for C in CARDS:
        t0 = T(C.m0); d = T(C.m1) - t0
        if C.first: cues.append((t0 - 0.3, sfx.whoosh(0.6, heavy=True), 0.35))
        else: cues.append((t0 - 0.2, sfx.whoosh(0.4), 0.14))
        if C.kind == 'q': cues += [(t0, sfx.chime(784, 2.0), 0.3)] + [(t0 + 0.4 + i * E8, sfx.chime(1046 + 60 * i, 0.5), 0.08) for i in range(0, 8, 2)]
        elif C.kind == 'r': cues += [(t0 - 1.2, sfx.riser(1.2), 0.4), (t0, sfx.impact(1.6), 0.6), (t0 + 0.2, sfx.sparkle(1.6, 14), 0.3)]
        else:
            m = C.motif
            if m == 'bolt': cues += [(t0 + 0.8, sfx.impact(1.0), 0.45), (t0 + 1.9, sfx.impact(0.8), 0.35), (t0 + 3.0, sfx.impact(0.8), 0.3)]
            elif m in ('heart', 'spark', 'sun'): cues += [(t0 + 0.6, thump(), 0.45), (t0 + 1.1, thump(), 0.4), (t0 + 1.7, sfx.chime(1320, 1.2), 0.2)]
            elif m in ('tears', 'wall', 'sigh', 'moon', 'mirror'): cues += [(t0 + 0.8, sfx.chime(660, 1.6), 0.18)]
            elif m in ('phone', 'letter', 'pen', 'think', 'bubble'): cues += [(t0 + 0.4 + k * 0.5, sfx.tick(), 0.25) for k in range(5)]
            elif m in ('gift', 'cup', 'key'): cues += [(t0 + 1.6, sfx.sparkle(1.2, 10), 0.3), (t0 + 1.6, sfx.chime(1568, 1.0), 0.15)]
            elif m in ('flame', 'target', 'chain'): cues += [(t0 + 0.3, sfx.burn(1.0), 0.4), (t0 + (2.0 if m == 'chain' else 1.9), sfx.impact(1.0), 0.4)]
            elif m in ('umbrella', 'road', 'alone', 'door', 'rings', 'compass', 'feather'): cues += [(t0 + 0.3, sfx.whoosh(0.9), 0.2)]
            elif m == 'clock': cues += [(t0 + k * 0.25, sfx.tick(), 0.18) for k in range(int(d / 0.25))]
            elif m == 'stairs': cues += [(t0 + k * 4 * E8, thump(0.3), 0.35) for k in range(8)]
            elif m == 'broken': cues += [(t0 + 1.0, sfx.impact(1.0), 0.5), (t0 + 1.0, sfx.drop(0.35), 0.3)]
            elif m in ('mountain', 'hourglass', 'coins', 'crowd', 'sprout', 'shield', 'smile', 'blush', 'people2', 'sweat'): cues += [(t0 + 1.2, sfx.chime(1175, 1.0), 0.15)]
    fx = sfx.mix(cues, duration)
    first = os.path.join(tmp, 'first.wav'); V2.build_audio(music, first, T(V2.END))
    fm = rd(first)
    mx = mus * 0.9
    mx[:len(fx)] += fx[:len(mx)]
    k0 = len(fm); fade = int(0.05 * sfx.SR)
    mx[:k0] = fm[:k0]
    mx[k0:k0 + fade] = mx[k0:k0 + fade] * np.linspace(0, 1, fade) + fm[-1] * 0
    sfx.write_wav(out, mx / max(1.0, np.abs(mx).max() / 0.97))


# ================================================================ render
def worker(a, b, path, fps):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    last = np.zeros((H, W, 3), np.uint8)
    for i in range(a, b):
        try: last = frame(i / fps)
        except Exception as e: print(f'frame {i / fps:.2f}s: {e!r}', flush=True)
        p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--stills'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2); ap.add_argument('--parts', help='directory to keep/reuse per-chunk files')
    ap.add_argument('--music', default=os.path.join(HERE, '..', '..', 'media', 'Vibecoding_music.mp3')); ap.add_argument('--list', action='store_true')
    args = ap.parse_args()
    if args.list:
        for C in CARDS: print(f'{T(C.m0):6.1f}-{T(C.m1):6.1f} {C.ch} {C.kind} {C.motif or "":10s} {" / ".join(C.lines)}')
        print('END', T(END)); return
    if args.stills:
        os.makedirs(args.out, exist_ok=True)
        for s in args.stills.split(','): cv2.imwrite(os.path.join(args.out, f'{float(s):06.2f}.jpg'), frame(float(s)), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    dur = T(END); N = int(dur * args.fps); t0 = time.time()
    tmp = args.parts or tempfile.mkdtemp(); os.makedirs(tmp, exist_ok=True)
    CH = 600; chunks = [(i, min(N, i + CH)) for i in range(0, N, CH)]
    parts = [os.path.join(tmp, f'p{i:03d}.mp4') for i in range(len(chunks))]
    todo = [k for k in range(len(chunks)) if not os.path.exists(parts[k])]
    def run(ks):
        for k in ks: worker(chunks[k][0], chunks[k][1], parts[k], args.fps); print('chunk', k, 'done', f'{time.time() - t0:.0f}s', flush=True)
    ps = [Process(target=run, args=(todo[j::args.jobs],)) for j in range(args.jobs)]
    for p in ps: p.start()
    for p in ps: p.join()
    if not all(os.path.exists(p) for p in parts): print('missing chunks'); return
    with open(os.path.join(tmp, 'l.txt'), 'w') as f: f.writelines(f"file '{p}'\n" for p in parts)
    v = os.path.join(tmp, 'v.mp4'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', v], check=True)
    au = os.path.join(tmp, 'a.wav'); build_audio(args.music, au, dur)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-i', au, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', args.out], check=True)
    print(f'wrote {args.out} ({dur:.1f}s) in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
