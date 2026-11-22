#!/usr/bin/env python3
"""金牛座的内心世界 · 8 分钟 —— same engine as long_aries.py, new protagonist and copy.

The Taurus protagonist is the same rig as the Aries one with STYLE swapped: short golden bull horns, soft curly
hair, a small flower tucked over the ear, no sword. The pre-drop hook is a seed under the soil that grows very slowly
(他的心里 / 埋着一颗种子 / 很慢 / 很慢地长 …), the drop match-cuts from the heart to the hero in a meadow under the
Taurus constellation, and from there every card of src/taurus_v2.txt is a directed shot, with Taurus-only actions
(a tug-of-war he never loses, the bull stomp, the coriander picked out of a bowl, a house with a lit window …).

  python3 template/longform/long_taurus.py --out out/long/v5/金牛座的内心世界_8分钟.mp4 [--stills 10,30] [--list]
"""
import math, os, sys, tempfile, subprocess, types
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
import aries_char as AC
AC.STYLE.update(horns='bull', hair='curly', back=None, flower=True)

import long_aries as L
import first_minute as FM
from first_minute_v4 import (inst, pose, mix, mirror, run_cycle, walk_cycle, heart_live, sparks_live, burst, ground, sh_for, T, E8,
                             _COUNTS, Shot, drift, stars_live, flame_shape)
from engine.core import W, H, Palette, Cam, flame, Text, F, SERIF_B, SERIF_BL, lerp, cl, ramp, eo, eio, pulse, pop
from story_frames import figure, glint, milkyway, meteor, godrays, sp, solid, lamp, window, BLACK, phone_big
from aries_char import draw_aries, skeleton
import sfx, render_long as R

PE, PAM, PV, PA = Palette('earth'), Palette('amber'), L.PV, L.PA
L.STYLE_FLAME[0] = False
L.CH_PAL = {'慢': PE, '稳': PE, '吃': PAM, '倔': PE, '家': PAM, '恋': PV, '爱': PAM, '守': PA, '累': PV, '真': PE}
L.DUR = {1: 18, 2: 20, 3: 24, 4: 28}
MUSIC_START, DROP, HOOK_END = 12, 52, 80


# ================================================================ hook (0 – 80 E8)
def soil(cv, P, y, a=0.6, seed=3):
    rr = np.random.default_rng(seed)
    cv.path([(-300, y), (W + 300, y)], P.LINE, a, 2, smooth=False)
    for k in range(4):
        yy = y + 70 + k * 90
        cv.path([(x, yy + 10 * math.sin(x / 140 + k)) for x in np.linspace(-300, W + 300, 40)], P.LINE, a * (0.35 - 0.06 * k), 1.2, smooth=False)
    for _ in range(40):
        c = (rr.uniform(0, W), rr.uniform(y + 30, H)); s = rr.uniform(4, 12)
        cv.path([(c[0] - s, c[1]), (c[0], c[1] - s * 0.6), (c[0] + s, c[1]), (c[0], c[1] + s * 0.5), (c[0] - s, c[1])], P.LINE, a * 0.3, 1, smooth=False)


def seed_shape(cv, P, c, s, a=1.0, glow=1.0):
    pts = [(c[0] + s * 0.7 * math.cos(q), c[1] + s * math.sin(q) * (1 - 0.15 * math.cos(q))) for q in np.linspace(0, 2 * math.pi, 40)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.WARM * 0.4, a); cv.path(pts, P.GOLD, a, 2.6, smooth=False)
    cv.path([(c[0], c[1] - s * 0.8), (c[0] + s * 0.1, c[1]), (c[0], c[1] + s * 0.8)], P.GOLD, 0.5 * a, 1.2)
    cv.glow(c, s * 2.5, P.GOLD, 0.7 * a * glow)


def roots(cv, P, c, k, a=0.8, seed=1):
    rr = np.random.default_rng(seed)
    for b in range(5):
        p = np.array(c, float); seg = [tuple(p)]; ang = math.pi / 2 + rr.uniform(-0.9, 0.9)
        for _ in range(8):
            ang += rr.uniform(-0.35, 0.35); p = p + np.array([math.cos(ang), math.sin(ang)]) * rr.uniform(16, 30); seg.append(tuple(p))
        cv.path(seg, P.SOFT, a, 1.6, frac=k, smooth=False)


def h_seed(t, n, tx):                                 # 0 – 8 : the seed under the soil
    s = lerp(1.0, 1.3, eio(ramp(n, 0, 8))); ds, dx, dy = drift(t, 0, 0.4)
    sh = sh_for('t_seed', t, 0, Cam(s * ds, 960 + dx, 700 + dy), 1.0, 2.0); cv = sh.cv; P = PE; c = (960, 800)
    soil(cv, P, 640)
    with inst(cv):
        for p0 in (0, 2, 4):
            if T(p0) <= t < T(p0) + 1.2: k = (t - T(p0)) / 1.2; cv.circle(c, 30 + 260 * eo(k), P.GOLD, (1 - k) * 0.6, 1.4)
        seed_shape(cv, P, c, 36 * (1 + 0.15 * pulse(t, FM.quarter(t), 0.3)), 1.0)
        if n > 4: roots(cv, P, (c[0], c[1] + 30), eo(ramp(n, 4, 8)))
        if n > 5: cv.path([(c[0], c[1] - 30), (c[0] + 6 * math.sin(t * 2), lerp(c[1] - 30, 650, eo(ramp(n, 5, 8))))], P.SOFT, 1, 2.4, smooth=False)
    FM.cap(tx, '他的心里', 960, 230, 72, 1, 15.6, 1, t=t)
    FM.cap(tx, '埋着一颗种子', 960, 330, 72, 4, 15.6, 0.5, (4, 5), t=t)
    return sh, P, 0.6, 0.0


def h_face(t, n, tx):                                 # 8 – 16 : leaves open around his profile
    s = lerp(1.0, 1.08, eio(ramp(n, 8, 16))); ds, dx, dy = drift(t, T(8), 0.5)
    sh = sh_for('t_face', t, 8, Cam(s * ds, 900 + dx, 540 + dy), 1.6, 2.4); cv = sh.cv; P = PE
    draw_aries(cv, 900, 1080 + 2000 * 0.6, 2000, pose('hero', mouth='smile', brow='calm', wind=(-0.3, 0.1)), P=P, col=P.SOFT, rim=(1, 0.3), heart=0)
    with inst(cv):
        rr = np.random.default_rng(4)
        for i in range(9):
            c = (rr.uniform(450, 1400), rr.uniform(150, 950)); k = eo(ramp(n, 8.5 + i * 0.6, 11 + i * 0.6)); r = 40 * k
            if k <= 0: continue
            q0 = rr.uniform(0, 6.3) + 0.2 * math.sin(t + i)
            leaf = [(c[0] + r * math.cos(q0) * u + r * 0.35 * math.sin(math.pi * u) * -math.sin(q0), c[1] + r * math.sin(q0) * u + r * 0.35 * math.sin(math.pi * u) * math.cos(q0)) for u in np.linspace(0, 1, 8)]
            leaf2 = [(c[0] + r * math.cos(q0) * u - r * 0.35 * math.sin(math.pi * u) * -math.sin(q0), c[1] + r * math.sin(q0) * u - r * 0.35 * math.sin(math.pi * u) * math.cos(q0)) for u in np.linspace(1, 0, 8)]
            cv.path(leaf + leaf2, P.SOFT, 0.8, 1.6, smooth=False)
        for i in range(14):
            ph = (t * 0.15 + i / 14) % 1; x = 300 + i * 100 + 40 * math.sin(t + i); y = -50 + 1200 * ph
            cv.circle((x, y), 5, P.WARM, 0.6, fill=True)
    FM.cap(tx, '他的心里', 1520, 720, 52, 8, 15.6, 0, t=t)
    FM.cap(tx, '埋着一颗种子', 1520, 810, 64, 8, 15.6, 0, (4, 5), t=t)
    return sh, P, 0.6, 0.0


def h_slow(t, n, tx):                                 # 16 – 24 : days pass, the sprout barely grows
    sh = sh_for('t_slow', t, 16, Cam(1.0, 960, 560), 0.8, 1.6); cv = sh.cv; P = PE
    ground(cv, 860, P, 0.6)
    lt = t - T(16); day = lt / 1.0
    with inst(cv):
        q = math.pi * (day % 1); up = (day % 2) < 1
        c = (960 - 700 * math.cos(q), 860 - 520 * math.sin(q))
        if up: cv.circle(c, 40, P.WARM, 1, fill=True); cv.glow(c, 120, P.GOLD, 0.6)
        else: cv.circle(c, 30, P.SOFT, 1, fill=True); stars_live(cv, P, t, 80, 600, 4, 0.6)
        L.sprout(cv, types.SimpleNamespace(P=P, t=t, lt=lt), (960, 860), 0.15 + 0.5 * ramp(n, 16, 24))
        L.clockface(cv, types.SimpleNamespace(P=P), (1600, 220), 70, lt * 14, 0.6)
    FM.cap(tx, '很慢', 960, 200, 80, 16, 23.6, 0, t=t)
    FM.cap(tx, '很慢地长', 960, 310, 80, 20, 23.6, 0.5, (2, 3), t=t)
    return sh, P, 0.6, 0.0


def h_think(t, n, tx):                                # 24 – 40 : 你以为他迟钝 / 其实他什么都记得
    s = lerp(1.0, 1.1, eio(ramp(n, 24, 40))); sh = sh_for('t_think', t, 24, Cam(s, 880, 560), 1.2, 2.5); cv = sh.cv; P = PE
    ground(cv, 960, P, 0.5)
    J = draw_aries(cv, 760, 960, 560, pose('hero', mouth='flat', brow='calm'), P=P, col=P.SOFT, rim=(1, -0.3))
    if n < 32:
        wave = math.sin(t * 9)
        figure(cv, 1260, 960, 520, 'argue', P.LINE * 0.95, 0.85, d=-1, hair='long', P=P, th=1.8)
        with inst(cv):
            for i in range(3):
                if n > 25 + i: FM.cap(tx, '?', 640 + i * 70, 300 - 20 * i, 54, 25 + i, 31.8, 0, t=t)
            cv.path([(1180, 540), (1150 + 20 * wave, 480)], P.LINE, 0.6, 2, smooth=False)
        FM.cap(tx, '你以为他迟钝', 1300, 220, 64, 24, 31.8, 0.5, (4, 5), t=t)
    else:
        with inst(cv):
            items = [('cup', (480, 300)), ('umb', (760, 200)), ('cal', (1040, 300))]
            for i, (kind, c) in enumerate(items):
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
        FM.cap(tx, '其实他', 1450, 560, 60, 32, 39.6, 0, t=t)
        FM.cap(tx, '什么都记得', 1450, 650, 70, 32, 39.6, 0.5, (3, 4), t=t)
    return sh, P, 0.6, 0.0


def h_shell(t, n, tx):                                # 40 – 52 : the shell closes; dive in
    s = 1.0 if n < 47 else 1 + 6 * eio(ramp(n, 47, 52)) ** 2.2
    sh = sh_for('t_shell', t, 40, Cam(s, 960, 600), 0.4, 1.0); cv = sh.cv; P = PE; c = (960, 600)
    heart_live(cv, c, 110, P, 1.0, lerp(1.0, 0.5, ramp(n, 41, 44)), pulse(t, FM.quarter(t), 0.25))
    k = eio(ramp(n, 40, 44)) * (1 - eio(ramp(n, 46, 48)))
    for sd in (-1, 1):
        off = sd * lerp(700, 10, k)
        sh_ = [(c[0] + off + sd * 280 * abs(math.cos(q)) * 0.9, c[1] + 300 * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 30)]
        solid(cv, sh_ + [(c[0] + off, c[1] + 300), (c[0] + off, c[1] - 300)], P.LINE, 1.0, 2.6, 0.06)
        for j in range(4): cv.path([(c[0] + off + sd * 40, c[1] - 220 + j * 140), (c[0] + off + sd * 200, c[1] - 200 + j * 130)], P.LINE, 0.4, 1.2, smooth=False)
    FM.cap(tx, '只是不说', 960, 170, 76, 40, 46.6, 0.5, t=t)
    return sh, P, 0.6, ramp(n, 50.5, 52) * 0.9


HX, HGY, HH = 640, 960, 640
TAU = [(1150, 170), (1270, 300), (1310, 360), (1350, 300), (1470, 180)]


def h_drop(t, n, tx):                                 # 52 – 80 : match cut to the hero in a meadow
    p = pose('hero', mouth='smile', brow='calm', wind=(-0.5 + 0.1 * math.sin(t * 2), 0.0))
    J = skeleton(HX, HGY, HH, p, 1); chest = J['sc'] - J['up'] * 0.075 * HH
    u = eio(ramp(n, DROP, DROP + 6)); s = lerp(8.0, 1.0, u) * (1 + 0.05 * ramp(n, DROP + 6, 80)); ds, dx, dy = drift(t, T(DROP) + 1.6, 0.8 * u)
    cam = Cam(s * ds, lerp(chest[0], 960, u) + dx, lerp(chest[1], 540, u) + dy)
    sh = sh_for('t_drop', t, DROP, cam, 2.2, 4.5); cv = sh.cv; P = PE
    with inst(cv):
        stars_live(cv, P, t, 200, 700, 9, a=u)
        milkyway(cv, P, (-200, 120), (W + 200, 380), 140, 8, 0.6 * u)
        burst(cv, chest, ramp(t, T(DROP), T(DROP) + 1.5), 80, 900, P, 1.0, 12)
        rr = np.random.default_rng(5)
        for i in range(70):                       # meadow grass swaying
            x = rr.uniform(-100, W + 100); hgt = rr.uniform(20, 60); sw = 8 * math.sin(t * 1.6 + x / 120)
            cv.path([(x, HGY), (x + sw * 0.5, HGY - hgt * 0.5), (x + sw, HGY - hgt)], P.SOFT, 0.45 * u, 1.2)
        for i in range(9):
            x = 180 + i * 200 + 30 * math.sin(i); fc = (x, HGY - 40 - 10 * (i % 3))
            for j in range(5):
                q = j / 5 * 2 * math.pi + t * 0.3; cv.circle((fc[0] + 9 * math.cos(q), fc[1] + 9 * math.sin(q)), 6, P.WARM, 0.8 * u, 1.4)
            cv.circle(fc, 3, P.GOLD, u, fill=True)
    cv.path(TAU[:2], P.GOLD, 0.6, 1.4, smooth=False); cv.path(TAU[1:4], P.GOLD, 0.6, 1.4, smooth=False); cv.path(TAU[3:], P.GOLD, 0.6, 1.4, smooth=False)
    ground(cv, HGY, P, 0.5)
    draw_aries(cv, HX, HGY, HH, p, P=P, col=P.SOFT, rim=(-1, -0.3), heart=1 + 0.15 * pulse(t, FM.quarter(t), 0.25))
    with inst(cv):
        if n < DROP + 4: heart_live(cv, chest, 0.026 * HH, P, 1 - ramp(n, DROP + 3, DROP + 4), 1.0)
        for i, q in enumerate(TAU): glint(cv, q, (26 if i == 1 else 14) + 10 * pulse(t, FM.quarter(t) + i * E8 * 0.5, 0.5), P.WARM, 1)
    FM.cap(tx, '金牛座的内心世界', 1340, 560, 96, DROP + 1, 79.6, 0.5, 'all', t=t, col=P.HI)
    return sh, P, 0.6, 0.9 * (1 - ramp(t, T(DROP), T(DROP) + 0.5))


SCENES = [(0, 8, h_seed, 't_seed'), (8, 16, h_face, 't_face'), (16, 24, h_slow, 't_slow'), (24, 40, h_think, 't_think'),
          (40, 52, h_shell, 't_shell'), (52, 80, h_drop, 't_drop')]


def _count():
    orig = Shot.__init__
    for m0, m1, fn, key in SCENES:
        _COUNTS[key] = (10 ** 6, 10 ** 6); box = {}
        def spy(self, *a, **k):
            orig(self, *a, **k); box['cv'] = self.cv
        Shot.__init__ = spy
        try: fn(T(m1) - 0.02, m1 - 0.02 / E8, Text(PE))
        finally: Shot.__init__ = orig
        c = box['cv'].cnt; _COUNTS[key] = (max(c['bg'], 1), max(c['fg'], 1))


def frame(t):
    n = t / E8; tx = Text(PE)
    fn = SCENES[-1][2]
    for m0, m1, f, key in SCENES:
        if n < m1: fn = f; break
    sh, P, glow, flash = fn(t, n, tx)
    img = sh.cv.composite(P.BG * 0.6, flash, glow=glow) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    img = tx.blend(np.clip(img, 0, 1.6).astype(np.float32))
    img *= ramp(t, 0, 0.15)
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def build_audio(music, out, duration):
    phase, e8 = R.grid(music); st = phase + MUSIC_START * e8; dr = T(DROP)
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, 'a.wav'); b = os.path.join(tmp, 'b.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.4f}', '-t', f'{dr:.4f}', '-i', music, '-af', 'lowpass=f=900,volume=0.55,afade=t=in:d=0.3', '-ac', '1', '-ar', str(sfx.SR), a], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st + dr:.4f}', '-t', f'{duration - dr:.4f}', '-i', music, '-ac', '1', '-ar', str(sfx.SR), b], check=True)
    import wave
    def rd(p):
        w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mus = np.concatenate([rd(a), rd(b)])
    thump = lambda d=0.4: (np.sin(2 * np.pi * 55 * np.arange(int(d * sfx.SR)) / sfx.SR) * np.exp(-np.arange(int(d * sfx.SR)) / sfx.SR * 9)).astype(np.float32)
    cues = [(T(0), thump(), 0.6), (T(2), thump(), 0.5), (T(4), thump(), 0.5), (T(5), sfx.chime(880, 1.2), 0.2), (T(8), sfx.whoosh(0.8), 0.2),
            (T(9), sfx.sparkle(1.4, 10), 0.2), (T(16), sfx.whoosh(0.6, up=False), 0.2)] + [(T(16) + k * 0.25, sfx.tick(), 0.15) for k in range(8)] + \
           [(T(25 + i), sfx.tick(), 0.3) for i in range(3)] + [(T(33 + 2 * i), sfx.chime(1046 + 120 * i, 1.0), 0.22) for i in range(3)] + \
           [(T(42), sfx.impact(0.8), 0.35), (T(43), thump(), 0.5), (T(45), thump(), 0.45),
            (T(DROP) - 1.9, sfx.riser(1.9), 0.65), (T(DROP), sfx.impact(1.8), 0.9), (T(DROP + 1), sfx.sparkle(1.6, 16), 0.3)]
    fx = sfx.mix(cues, duration); n = min(len(mus), len(fx)); mx = mus[:n] * 0.9 + fx[:n]
    sfx.write_wav(out, mx / max(1.0, np.abs(mx).max() / 0.97))


HOOK = types.SimpleNamespace(END=HOOK_END, MUSIC_START=MUSIC_START, DROP=DROP, DUCKS=[], frame=frame, _count=_count, build_audio=build_audio)


# ================================================================ Taurus-only motifs
def bowl(cv, P, c, s=1.0, a=1.0):
    x, y = c
    b = [(x - 90 * s, y - 20 * s)] + [(x + 90 * s * math.cos(q), y - 20 * s + 70 * s * math.sin(q)) for q in np.linspace(math.pi, 0, 20)[::-1]] + [(x + 90 * s, y - 20 * s)]
    pts = [(x + 90 * s * math.cos(q), y - 20 * s + 70 * s * math.sin(q)) for q in np.linspace(0, math.pi, 20)]
    solid(cv, pts, P.SOFT, a, 2.4, 0.06)
    cv.path([(x + 90 * s * math.cos(q), y - 20 * s + 14 * s * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 30)], P.SOFT, a, 2, smooth=False)


def m_food(C, sh, tx):
    cv = sh.cv; P = C.P; txt = ''.join(C.lines)
    two = any(w in txt for w in ('你', '一起'))
    if two: L.Y(cv, C, 1250, 960, 500, 'sit', -1)
    L.A(cv, C, 680, 960, 520, pose('hero', mouth='smile', uaF=60, faF=95, hF='open'))
    table = [(380, 760), (1540, 760), (1540, 790), (380, 790)]; solid(cv, table, P.LINE, 1, 2.4, 0.06)
    cv.path([(460, 790), (460, 960)], P.LINE, 1, 2.4, smooth=False); cv.path([(1460, 790), (1460, 960)], P.LINE, 1, 2.4, smooth=False)
    bowl(cv, P, (960, 720), 1.1)
    with inst(cv):
        for k in range(3):
            ph = (C.lt * 0.5 + k / 3) % 1
            cv.path([(920 + k * 40 + 12 * math.sin(C.t * 3 + j + k), 680 - j * 26 - ph * 40) for j in range(5)], P.WARM, 0.7 * (1 - ph), 1.8)
        ck = ramp(C.lt, 0.8, 2.6)
        cx = lerp(960, 1180, eio(ck % 0.34 / 0.34)) if ck < 1 else 1180
        cv.path([(cx - 10, 700), (cx + 160, 560)], P.GOLD, 1, 3, smooth=False); cv.path([(cx + 10, 704), (cx + 180, 570)], P.GOLD, 1, 3, smooth=False)
        if '香菜' in txt:
            for j in range(int(ck * 3) + 1):
                lc = (1180 + j * 34, 744); cv.path(sp([lc, (lc[0] + 12, lc[1] - 14), (lc[0] + 24, lc[1]), (lc[0] + 12, lc[1] + 6), lc], 4), P.SOFT, 1, 1.6)
        else:
            heart_live(cv, (960, 600), 26, P, ramp(C.lt, 1.4, 2.0), 0.8, pulse(C.t, FM.quarter(C.t), 0.3))
    return 'T'


def m_tug(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.5)
    J = L.A(cv, C, 560, 960, 540, pose('stand_arm', lean=-8, uaF=70, faF=80, uaB=60, faB=75, thF=30, shF=10, thB=-18, shB=-10, mouth='grit', brow='fierce'))
    hand = J['haF']
    wob = 6 * math.sin(C.t * 11)
    pullers = [1000, 1180, 1360, 1540] if C.idx % 2 == 0 else [1060]
    end = (pullers[-1] + 40, 600)
    cv.path(sp([tuple(hand), ((hand[0] + end[0]) / 2, 600 + wob), end], 6), P.WARM, 1, 3)
    for i, x in enumerate(pullers):
        slip = 20 * math.sin(C.t * 3 + i) * ramp(C.lt, 0.5, 1.2)
        figure(cv, x + slip, 960, 440, 'climb', P.LINE * 0.9, 0.6, d=-1, P=P, th=1.6)
    with inst(cv):
        for i, x in enumerate(pullers):
            k = (C.lt * 1.3 + i * 0.3) % 1; cv.circle((x + 60 + 60 * k, 950), 8 + 26 * k, P.LINE, 0.4 * (1 - k), 1.2)
        if len(pullers) > 1:
            for i in range(10):
                q = i / 10 * math.pi; cv.path([(560 + 20 * i - 90, 966), (560 + 20 * i - 100, 975)], P.LINE, 0.5, 1.2, smooth=False)
        cv.path([(640, 300), (600, 360), (650, 360), (610, 420)], P.WARM, 0.6 + 0.4 * math.sin(C.t * 6), 2, smooth=False)
    return 'T'


def m_bull(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.6)
    stomp = [0.7, 1.8, 2.9]
    lift = max(0.0, max(math.sin(math.pi * cl((C.lt - (s0 - 0.35)) / 0.35)) for s0 in stomp))
    p = pose('stand_arm', lean=14, head=22, thF=14 + 40 * lift, shF=4 - 10 * lift, mouth='grit', brow='angry', wind=(-0.9, -0.2))
    L.A(cv, C, 760, 960, 600, p)
    shake = 0.0
    with inst(cv):
        for i, s0 in enumerate(stomp):
            k = ramp(C.lt, s0, s0 + 0.9)
            if 0 < k < 1:
                burst(cv, (840, 960), k, 50, 380, P, 1.0, i, (-math.pi, 0), 260)
                cv.path([(840 + 500 * eo(k) * math.cos(q), 960 + 40 * eo(k) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 50)], P.WARM, 1 - k, 2, smooth=False)
            if C.lt > s0: L.cracks(cv, (840, 962), 0.45 * eo(ramp(C.lt, s0, s0 + 0.6)), P, 0.45, 10 + i)
        for j in range(2):
            ph = (C.lt * 1.4 + j * 0.5) % 1; c = (900 + 120 * ph, 420 + 10 * j)
            cv.circle(c, 10 + 30 * ph, P.SOFT, 0.6 * (1 - ph), 1.6)
    C.flash = 0.18 * max(pulse(C.t, C.t0 + s0, 0.2) for s0 in stomp)
    return 'R'


def house(cv, P, x, gy, s=1.0, a=1.0, lit=1.0, t=0.0):
    w, hh = 320 * s, 220 * s
    body = [(x - w / 2, gy), (x - w / 2, gy - hh), (x + w / 2, gy - hh), (x + w / 2, gy)]
    solid(cv, body, P.LINE, a, 2.4, 0.04)
    roof = [(x - w / 2 - 30 * s, gy - hh), (x, gy - hh - 150 * s), (x + w / 2 + 30 * s, gy - hh)]
    cv.path(roof, P.LINE, a, 2.6, smooth=False)
    cv.path([(x + 70 * s, gy - hh - 80 * s), (x + 70 * s, gy - hh - 150 * s), (x + 110 * s, gy - hh - 150 * s), (x + 110 * s, gy - hh - 50 * s)], P.LINE, a, 2, smooth=False)
    win = [(x - 120 * s, gy - 170 * s), (x - 20 * s, gy - 170 * s), (x - 20 * s, gy - 90 * s), (x - 120 * s, gy - 90 * s)]
    cv.poly(win, P.WARM * 0.6, a * lit); cv.path(win + [win[0]], P.WARM, a, 2, smooth=False)
    cv.path([(x - 70 * s, gy - 170 * s), (x - 70 * s, gy - 90 * s)], P.WARM, a, 1.4, smooth=False)
    door = [(x + 30 * s, gy), (x + 30 * s, gy - 130 * s), (x + 110 * s, gy - 130 * s), (x + 110 * s, gy)]
    cv.path(door, P.LINE, a, 2.2, smooth=False)
    return (x - 70 * s, gy - 130 * s), (x + 90 * s, gy - 260 * s - 150 * s)


def m_home(C, sh, tx):
    cv = sh.cv; P = C.P; L.nightsky(cv, C, 120, 600); ground(cv, 960, P, 0.5)
    wc, chim = house(cv, P, 1300, 960, 1.4, 1.0)
    with inst(cv):
        cv.glow(wc, 160, P.GOLD, 0.5 * (0.85 + 0.15 * math.sin(C.t * 2))); cv.glow(wc, 60, P.WARM, 0.5)
        for k in range(4):
            ph = (C.lt * 0.3 + k / 4) % 1; cv.circle((chim[0] + 40 * math.sin(C.t + k) + 60 * ph, chim[1] - 200 * ph), 14 + 30 * ph, P.SOFT, 0.4 * (1 - ph), 1.4)
    k = ramp(C.lt, 0, 2.6)
    if k < 1: L.A(cv, C, lerp(300, 980, k), 960, 460, walk_cycle(C.lt / 1.0, mouth='smile'))
    else: L.A(cv, C, 980, 960, 460, pose('lookback', mouth='smile', brow='calm'))
    return 'T'


def m_calendar(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    L.A(cv, C, 480, 960, 540, pose('point', mouth='smile', brow='calm'))
    x0, y0, cw, chh = 820, 300, 110, 90
    solid(cv, [(x0 - 20, y0 - 110), (x0 + 7 * cw + 20, y0 - 110), (x0 + 7 * cw + 20, y0 + 5 * chh + 20), (x0 - 20, y0 + 5 * chh + 20)], P.SOFT, 1, 2.4, 0.03)
    cv.path([(x0 - 20, y0 - 30), (x0 + 7 * cw + 20, y0 - 30)], P.WARM, 1, 2.4, smooth=False)
    for r_ in range(5):
        for c_ in range(7): cv.circle((x0 + c_ * cw + cw / 2, y0 + r_ * chh + chh / 2), 4, P.SOFT, 0.6, fill=True)
    with inst(cv):
        tc = (x0 + 4 * cw + cw / 2, y0 + 2 * chh + chh / 2); k = eo(ramp(C.lt, 1.0, 2.0))
        cv.path([(tc[0] + 46 * math.cos(q), tc[1] + 38 * math.sin(q)) for q in np.linspace(-1.6, -1.6 + 2 * math.pi * 1.05 * k, 40)], P.WARM, 1, 3.2, smooth=False)
        if k >= 1: heart_live(cv, tc, 18, P, 1.0, 0.8, pulse(C.t, FM.quarter(C.t), 0.3)); glint(cv, (tc[0] + 40, tc[1] - 40), 20, P.WARM, 1)
    return 'T'


def m_corner(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    for k in range(8): cv.circle((700 + k * 150, 200 + 30 * math.sin(k)), 6, P.WARM, 1, fill=True)
    cv.path(sp([(700 + k * 150, 200 + 30 * math.sin(k)) for k in range(8)], 4), P.LINE, 0.5, 1.2)
    for k, x in enumerate((900, 1060, 1220, 1380, 1540)): figure(cv, x, 960, 400, 'argue' if k % 2 else 'stand', P.LINE * 0.9, 0.5, d=1 if k % 2 else -1, P=P, th=1.5)
    chair = [(330, 960), (330, 820), (510, 820), (510, 960)]; cv.path(chair, P.LINE, 0.8, 2, smooth=False); cv.path([(330, 820), (330, 640)], P.LINE, 0.8, 2, smooth=False)
    L.A(cv, C, 420, 830, 420, pose('sit_hug', mouth='smile', brow='calm', head=10))
    with inst(cv):
        for k in range(8): cv.glow((700 + k * 150, 200 + 30 * math.sin(k)), 30, P.GOLD, 0.5 + 0.5 * math.sin(C.t * 3 + k))
        sparks_live(cv, (1220, 400), C.t, 24, 10, 400, P, 0.5, 2, (0, 2 * math.pi), 0.3, 1.6)
    return 'T'


def m_seed(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 900, P, 0.6)
    day = C.lt / 1.3
    with inst(cv):
        q = math.pi * (day % 1); up = (day % 2) < 1
        c = (1100 - 600 * math.cos(q), 900 - 420 * math.sin(q))
        if up: cv.circle(c, 34, P.WARM, 1, fill=True); cv.glow(c, 110, P.GOLD, 0.5)
        else: cv.circle(c, 26, P.SOFT, 1, fill=True); stars_live(cv, P, C.t, 80, 500, 4, 0.6)
        L.sprout(cv, C, (1100, 900), 0.1 + 0.9 * ramp(C.lt, 0.3, C.dur - 0.3))
        roots(cv, P, (1100, 905), eo(ramp(C.lt, 0.3, C.dur)), 0.5, C.idx)
    L.A(cv, C, 700, 900, 420, pose('sit_hug', mouth='smile', brow='calm', head=20))
    return 'T'


_bubble = L.m_bubble
def m_bubble(C, sh, tx):
    if '很少' in ''.join(C.lines):
        cv = sh.cv; P = C.P; ground(cv, 940, P, 0.5)
        L.Y(cv, C, 1250, 940, 500, 'argue', -1)
        L.A(cv, C, 620, 940, 520, pose('hero', mouth='flat', brow='calm'))
        for k in range(3):
            if C.lt > 0.4 + k * 0.4: L.bubble(cv, tx, sh.cam, (1120 - k * 10, 330 - k * 70), 260, 90, '', P, 0.8, (1, 1))
        if C.lt > 1.8: L.bubble(cv, tx, sh.cam, (760, 400), 140, 90, '…', P, 1.0, (-1, 1), True, 50)
        return 'L2'
    return _bubble(C, sh, tx)


_phone = L.m_phone
def m_phone(C, sh, tx):
    if '舍不得删' in ''.join(C.lines):
        cv = sh.cv; P = C.P
        L.A(cv, C, 520, 1080 + 700 * 0.5, 1100, pose('hero', mouth='smile', brow='sad', uaF=70, faF=160, hF='open', head=14))
        msgs = [('2019 · 晚安', 1, 260, 'sent'), ('2020 · 生日快乐', -1, 340, 'sent'), ('2021 · 下雨带伞', 1, 420, 'sent')]
        if C.lt > 1.4: msgs.append(('删除聊天记录？', 1, 520, 'deleted' if C.lt > 2.6 else 'typing'))
        phone_big(cv, tx, 1040, 560, 380, 680, P, msgs)
        with inst(cv): cv.glow((1040, 560), 380, P.SOFT, 0.18)
        return 'T'
    return _phone(C, sh, tx)


L.MOTIFS.update(seed=m_seed, food=m_food, tug=m_tug, bull=m_bull, home=m_home, calendar=m_calendar, corner=m_corner, bubble=m_bubble, phone=m_phone)

# ================================================================ wire into the long engine
L.V = HOOK
L.FIRST_END = HOOK_END
L.CARDS = L.parse(os.path.join(HERE, 'src', 'taurus_v2.txt'), skip_ch=(), first_end=HOOK_END)
L.END = L.CARDS[-1].m1

if __name__ == '__main__':
    L.main()
