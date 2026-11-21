#!/usr/bin/env python3
"""白羊座的内心世界 · 同款短片（模仿双子座参考的结构）

  0–13.8 s  引子：一镜到底，从一颗火星长出整个人；音乐压低 + 低通，字幕逐字打出
  13.8 s    drop：riser → 撞击，白闪三圈光环，标题落在右侧
  之后      每 2 小节一个比喻动效（点星 / 羊角 / 眼泪变烛光 / 光柱换色 / 爆闪 / 两颗心），音效只给大动作

  python3 template/longform/short_aries.py --out out/long/v3/白羊座_同款.mp4 [--stills 1,5,...]
"""
import argparse, math, os, subprocess, sys, tempfile, time
from multiprocessing import Process
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import (W, H, GY, cl, ramp, eo, eio, lerp, pulse, pop, Palette, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, spline)
from engine.scene import ARM_L, ARM_R
from engine.group import SubCam
import zodiac_signs
from zodiac_scene import load
from vis import heart_pts, drop as drop_shape
import sfx

E8 = 60 / 112.9117 / 2          # Vibecoding music grid
DROP = 52                       # eighth of the drop (music starts 12 eighths before the song's own grid point 0)
MUSIC_START = 12
END = 166
HERO_K = 0.78
CORE = (960.0, 569.0)           # world point of the hero's chest

# (text, start eighth, eighths per char, x, y, size, end eighth, gold)  gold: 'all' | list of char indices
CAPS = [
    ('他的心里', 1, 1, 960, 175, 70, 15.6, []),
    ('住着一团火', 8, 0.5, 960, 268, 70, 15.6, [3, 4]),
    ('一碰', 16, 1, 960, 190, 70, 23.6, []),
    ('就燃', 20, 0.25, 960, 300, 112, 23.6, 'all'),
    ('火的最中间', 24, 0.5, 960, 175, 70, 31.6, []),
    ('藏着一颗很软的心', 27, 0.5, 960, 268, 70, 31.6, [4, 5]),
    ('他用火护着它', 32, 0.5, 960, 175, 70, 39.6, [2]),
    ('谁靠近', 40, 0.5, 960, 175, 70, 47.6, []),
    ('都先被烫一下', 42, 0.5, 960, 268, 70, 47.6, [3, 4]),
    ('可偏偏有人', 48, 0.5, 960, 175, 70, 51.7, []),
    ('不怕烫', 50, 0.34, 960, 268, 70, 51.7, 'all'),
    # ---- after the drop: right-hand block, the hero stands left ----
    ('你随口一句鼓励', 68, 0.5, 1400, 430, 64, 83.6, []),
    ('他能记很久', 72, 0.5, 1400, 525, 64, 83.6, [3, 4]),
    ('不服的时候', 84, 0.5, 1400, 430, 64, 99.6, []),
    ('他比谁都倔', 88, 0.5, 1400, 525, 64, 99.6, [4]),
    ('难过的时候', 100, 0.5, 1400, 430, 64, 115.6, []),
    ('他关上门 一个人哭完', 104, 0.5, 1400, 525, 64, 115.6, [6, 7, 8, 9]),
    ('看起来锋芒毕露', 116, 0.5, 1400, 430, 64, 131.6, [3, 4, 5, 6]),
    ('心却软得一塌糊涂', 120, 0.5, 1400, 525, 64, 131.6, [2]),
    ('外表有锋芒', 132, 0.5, 1400, 440, 96, 143.6, [3, 4]),
    ('内心有柔软', 136, 0.5, 1400, 580, 96, 143.6, [3, 4]),
    ('他的火', 144, 0.5, 1400, 400, 64, 166, []),
    ('只为在乎的人烧', 148, 0.5, 1400, 495, 64, 166, [2, 3]),
]
CAM = [(0, 1.7, 960, 569), (8, 1.6, 960, 560), (16, 1.35, 960, 540), (19.6, 1.35, 960, 540), (20.4, 1.05, 960, 520),
       (24, 1.1, 960, 520), (30, 2.1, 960, 520), (32, 2.1, 960, 520), (40, 1.0, 1060, 520), (48, 1.05, 1090, 520),
       (51.8, 1.18, 1070, 540), (52.6, 0.95, 1300, 520), (66, 0.98, 1300, 520), (68, 1.04, 1260, 470), (84, 1.0, 1300, 520),
       (100, 1.0, 1300, 520), (103, 2.3, 1210, 400), (110, 2.3, 1210, 400), (112, 1.0, 1300, 520), (132, 1.1, 1290, 500),
       (144, 1.0, 1300, 520), (166, 0.96, 1300, 520)]


def T(m): return m * E8


class AriesShort:
    def __init__(self, logo=None):
        self.hero = load('aries', 0.0, E8, None, {})
        self.PF = self.hero.P; self.PV = Palette('violet')
        self.sign = self.hero.sign; self.logo = logo
        rng = np.random.default_rng(3)
        self.stars = [(rng.uniform(0, W), rng.uniform(0, 700), rng.uniform(0.8, 1.8), rng.uniform(0, 6.3)) for _ in range(70)]
        self.candles = sorted([(960 + s * d, rng.uniform(0.7, 1.1)) for d in np.linspace(90, 900, 22) for s in (-1, 1)], key=lambda c: abs(c[0] - 960))
        self.duration = T(END)

    def quarter(self, t): return 2 * E8 * math.floor(t / (2 * E8))

    def cam(self, t):
        n = t / E8; s, cx, cy = CAM[0][1:]
        for (k0, s0, x0, y0), (k1, s1, x1, y1) in zip(CAM[:-1], CAM[1:]):
            if k0 <= n < k1:
                u = eio(cl((n - k0) / (k1 - k0))); s, cx, cy = lerp(s0, s1, u), lerp(x0, x1, u), lerp(y0, y1, u); break
        else:
            if n >= CAM[-1][0]: s, cx, cy = CAM[-1][1:]
        s *= 1 + 0.10 * pulse(t, T(20), 0.35) + 0.08 * pulse(t, T(DROP), 0.45) + 0.05 * pulse(t, T(132), 0.35)
        if n >= DROP: s *= 1 + 0.01 * pulse(t, self.quarter(t), 0.3)
        return Cam(s, cx, cy)

    # ------------------------------------------------------------ pieces
    def flame_outline(self, cv, x, base, h, P, a, lean, t, close=0.0, fill=True, ws=1.0):
        G, Wm = P.GOLD, P.WARM
        if fill:
            flame(cv, x, base, h * 1.45, G, 0.16 * a, layer=cv.F, lean=lean)
            flame(cv, x, base, h, G, (0.55 - 0.45 * close) * a, lean=lean)
            flame(cv, x, base - 0.05 * h, h * 0.6, Wm, (0.7 - 0.6 * close) * a, lean=lean * 1.3)
        for k, (sc_, col, th) in enumerate(((1.0, G, 2.2), (0.76, Wm, 1.6), (1.2, G, 1.2))):
            w = h * sc_ * 0.36 * ws; hh = h * sc_; wob = 0.04 * math.sin(t * 7 + k)
            pts = [(x + (lean + wob) * hh, base - hh), (x + w * 0.55, base - hh * 0.45), (x + w * 0.5, base - hh * 0.15), (x, base),
                   (x - w * 0.5, base - hh * 0.15), (x - w * 0.55, base - hh * 0.45)]
            cv.path(list(spline(pts, n=10, closed=True)), col, a * (0.35 + 0.65 * close) * (1 - 0.3 * k), th, smooth=False)

    def heart(self, cv, c, size, P, a, t, frac=1.0):
        s = 1 + 0.14 * pulse(t, self.quarter(t), 0.25)
        hp = [(c[0] + size * x * s, c[1] + size * y * s) for x, y in heart_pts(0, 0, 1.0, 50)]
        self.hero.tpath(cv, hp, P.WARM, a, 2.2, frac, smooth=False)
        if frac >= 1: cv.poly(hp, P.WARM * 0.5, 0.6 * a, layer=cv.F)
        cv.glow(c, size * 0.9, P.GOLD, (0.5 + 0.5 * pulse(t, self.quarter(t), 0.3)) * a * frac)

    def visitor(self, cv, x, a, reach, P, t, heart_on=0.0):
        """a simple line figure: head, shoulders, body; the near arm reaches toward the hero by `reach` 0..1"""
        if a <= 0.01: return
        hy = GY - 330; col = P.SOFT
        cv.path([(x + 30 * math.cos(q), hy + 34 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 40)], col, a, 2.0, smooth=False)
        cv.path([(x - 70, GY), (x - 64, hy + 150), (x - 40, hy + 70), (x, hy + 50), (x + 40, hy + 70), (x + 64, hy + 150), (x + 70, GY)], col, a, 2.0)
        sh = (x - 40, hy + 72); hand = (lerp(x - 70, CORE[0] + 70, reach), lerp(hy + 230, CORE[1], reach))
        cv.path([sh, ((sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2 + 22), hand], col, a, 2.0)
        if heart_on > 0: self.heart(cv, (x, hy + 130), 22, P, a * heart_on, t)

    def beam(self, cv, t, t0, x, P):
        if not (t0 - 0.25 <= t < t0 + 0.45): return
        u = (t - (t0 - 0.25)) / 0.7; a = math.sin(math.pi * u)
        for k, (w, al) in enumerate(((3, 1.0), (14, 0.35), (40, 0.12))):
            cv.path([(x, -60), (x, GY + 40)], P.WARM, a * al, w, smooth=False, layer=cv.F if k else None)
        cv.path([(x - 260 * a, GY), (x + 260 * a, GY)], P.GOLD, 0.6 * a, 2, smooth=False)

    # ================================================================ FRAME
    def frame(self, t):
        n = t / E8; hero = self.hero
        swapped = T(118) <= t < T(126)
        P = self.PV if swapped else self.PF
        hero.P = P
        G, Wm, LN, SO = P.GOLD, P.WARM, P.LINE, P.SOFT
        cam = self.cam(t); cv = Canvas(cam); tx = Text(self.PF)
        qt = self.quarter(t); pre = n < DROP
        dip = 1 - 0.5 * ramp(n, 50.5, 51.8) * pre
        # ---- sky: sparse, small, sharp ----
        sk = ramp(n, 0, 12) * (0.45 if pre else 0.8)
        for (x, y, r, ph) in self.stars:
            cv.circle((x, y), r, LN, sk * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 1.3 + ph))) * 0.6, fill=True)
        # ---- ground line wakes on the drop ----
        gl = eo(ramp(n, DROP, DROP + 1))
        if gl > 0: cv.path([(-200, GY), (2200, GY)], LN, 0.55 * gl, 1.4, smooth=False)
        C = CORE
        # ---- hook: spark -> flame -> heart -> hero ----
        if n < DROP + 1:
            h = 0.0
            if n >= 8: h = 40 + 22 * cl(math.floor(n) - 7, 0, 5) * (0.85 + 0.15 * pop(t, T(math.floor(n)), 0.12))
            if n >= 16: h = 170 * (1 + 0.05 * math.sin(t * 20))
            if n >= 20: h = lerp(440, 300, eo(ramp(n, 20, 23)))
            if n >= 23: h = 300 * (1 + 0.04 * math.sin(t * 9))
            if n >= 32: h = lerp(300, 110, eio(ramp(n, 32, 46)))
            if 44 <= n < 47: h *= 1 + 0.9 * pulse(t, T(44), 0.6)
            close = ramp(n, 23, 28) * (1 - ramp(n, 33, 38))
            fa = (1 - ramp(n, 51, 52.6)) * dip
            lean = 0.05 * math.sin(t * 2.3) + (0.35 * pulse(t, T(44), 0.6) if n >= 44 else 0)
            if h > 0: self.flame_outline(cv, C[0], C[1] + 0.42 * h, h, P, fa, lean, t, close)
            if n < 9:   # the first spark + heartbeat rings
                r = 6 * (1 + 0.5 * pulse(t, T(0), 0.3) + 0.5 * pulse(t, T(2), 0.3))
                cv.circle(C, r, Wm, 1.0, fill=True); cv.glow(C, 36, G, 0.8)
            for p0 in (0, 2, 8):
                if T(p0) <= t < T(p0) + 0.9:
                    k = (t - T(p0)) / 0.9; cv.circle(C, 18 + 200 * eo(k), G, (1 - k) * 0.7, 1.6)
            if T(16) <= t < T(20):   # "一碰": an ember flies in
                u = eio((t - T(16)) / (T(20) - T(16)))
                for k in range(8):
                    uu = max(0, u - k * 0.03)
                    p = (lerp(240, C[0], uu), lerp(160, C[1] - 40, uu) - 150 * math.sin(uu * math.pi))
                    cv.circle(p, 5.5 - k * 0.6, Wm if k == 0 else G, 1 - k / 8, fill=True)
            if T(20) <= t < T(20) + 1.3:   # "就燃": flare
                k = (t - T(20)) / 1.3
                for j in range(30):
                    q = j * 2 * math.pi / 30 + 0.2; r = 70 + 560 * eo(k) * (0.7 + 0.3 * math.sin(j * 7))
                    cv.circle((C[0] + r * math.cos(q), C[1] - 60 + r * math.sin(q)), 2.6, Wm, (1 - k), fill=True)
                hero.ring_burst(cv, t, T(20), C, 60, 650, 0.9)
            if 32 <= n < DROP + 1:   # flame tongues wrap the heart
                g = eio(ramp(n, 32, 35)); a = (1 - ramp(n, 46, 50)) * dip
                for sd in (-1, 1):
                    arm = [(C[0] + sd * (90 - 10 * u) * math.sin(u * math.pi * 0.95), C[1] + 85 - 220 * u) for u in np.linspace(0, 1, 30)]
                    cv.path(arm, G, a, 2.2, g, smooth=False)
        # ---- hero grows out of the flame ----
        sub = SubCam(cam, 960, HERO_K); cv.cam = sub
        prog = ramp(n, 33, 46)
        if n >= 33:
            ha = (0.95 if pre else 1.35) * dip
            hero.draw_figure(cv, t, ha, prog, ARM_L['rest'], ARM_R['rest'], 0.0, 0.25 + 0.4 * pulse(t, qt, 0.3) * (not pre))
        eyes = [tuple(sub.to_world([(943, 252)])[0]), tuple(sub.to_world([(977, 252)])[0])]
        cv.cam = cam
        # the heart: appears in the core, then lives at the chest
        if n >= 26:
            self.heart(cv, C, 58 if n < 34 else lerp(58, 24, eio(ramp(n, 34, 44))), P, 1.0 * (dip if pre else 1), t, eio(ramp(n, 26, 29)))
        # ---- the visitor ----
        if 40 <= n < DROP + 0.5:
            x = 1500
            if n < 44: x = lerp(1520, 1290, eio(ramp(n, 40, 44)))
            elif n < 48: x = lerp(1290, 1400, eo(ramp(n, 44, 45.5)))
            else: x = lerp(1400, 1150, eio(ramp(n, 48, 51.5)))
            reach = eio(ramp(n, 50, 51.9))
            self.visitor(cv, x, eo(ramp(n, 40, 41.5)) * (1 - ramp(n, 52, 52.5)), reach, P, t)
        # ---- DROP ----
        if T(DROP) <= t < T(DROP) + 2.2:
            for j, r1 in enumerate((900, 1300, 1750)): hero.ring_burst(cv, t, T(DROP + 2 * j), C, 80, r1, 1.1)
            k = (t - T(DROP)) / 2.2
            for j in range(48):
                q = j * 2 * math.pi / 48; r = 90 + 900 * eo(k) * (0.6 + 0.4 * math.sin(j * 3.7))
                p = (C[0] + r * math.cos(q), C[1] + r * math.sin(q) * 0.8)
                cv.path([p, (p[0] - 18 * math.cos(q), p[1] - 18 * math.sin(q) * 0.8)], Wm, (1 - k) * 0.9, 2, smooth=False)
        # ---- D1: every quarter a ray from the heart lights a star ----
        if 68 <= n < 100:
            sg = self.sign; x0, y0, w, h_ = 700, 70, 520, 230
            pts = [(x0 + u * w, y0 + v * h_) for u, v in sg['stars']]
            a = 1 - ramp(n, 96, 100)
            for k, p in enumerate(pts):
                tk = T(70 + 2 * k)
                if t < tk: continue
                if t < tk + 0.45:
                    u = (t - tk) / 0.45; hd = (lerp(C[0], p[0], eo(u)), lerp(C[1], p[1], eo(u)))
                    cv.path([(lerp(C[0], p[0], max(0, eo(u) - 0.25)), lerp(C[1], p[1], max(0, eo(u) - 0.25))), hd], Wm, 1 - u, 2.2, smooth=False)
                lit = eo(ramp(t, tk + 0.4, tk + 0.5))
                cv.circle(p, 4.5, Wm, a * lit, fill=True); cv.glow(p, 26, G, a * lit * (0.6 + 1.2 * pulse(t, tk + 0.45, 0.4)))
            for k, (i, j) in enumerate(sg['lines']):
                tl = T(70 + 2 * max(i, j)) + 0.5
                cv.path([pts[i], pts[j]], LN, 0.75 * a, 1.4, eo(ramp(t, tl, tl + 0.4)), smooth=False)
        # ---- D2: the fire flares around him, horns curl out ----
        if 84 <= n < 100:
            a = eo(ramp(n, 84, 85)) * (1 - ramp(n, 97, 100))
            hh = 720 * (1 + 0.04 * math.sin(t * 8)) * (0.85 + 0.15 * pulse(t, qt, 0.3))
            self.flame_outline(cv, 960, GY + 10, hh, P, 0.8 * a, 0.03 * math.sin(t * 2), t, 1.0, fill=False, ws=2.5)
            hg = eio(ramp(n, 86, 90)); top = (960, 360)
            for sd in (-1, 1):
                horn = [(top[0] + sd * (20 + 60 * (1 - math.cos(u * 1.7 * math.pi)) * 0.6 + 30 * u), top[1] - 80 * math.sin(u * 1.25 * math.pi) - 30 * u) for u in np.linspace(0, 1, 36)]
                hero.tpath(cv, horn, G, a, 3.0, hg, smooth=False)
        # ---- D3: tears fall to the ground and become candles ----
        for k, m in enumerate((102, 104, 106, 108)):
            if T(m) <= t < T(m) + 1.6:
                ex, ey = eyes[k % 2]; u = (t - T(m)) / 1.6
                y = ey + 10 + (GY - ey) * u ** 1.8
                if y < GY:
                    cv.poly(list(spline(drop_shape(ex + (k % 2 * 2 - 1) * 3, y, 9), n=4, closed=True)), Wm, 0.95)
                    cv.glow((ex, y), 14, G, 0.6)
        if n >= 110:
            a = eo(ramp(n, 110, 112)) * (1 - ramp(n, 158, 164))
            for j, (x, s) in enumerate(self.candles):
                ton = T(110 + min(6, j // 6)) + 0.08 * (j % 6)
                if t < ton: continue
                hh = 34 * s * (1 + 0.12 * math.sin(t * 7 + j)) * pop(t, ton, 0.16) * (1 + 0.3 * pulse(t, qt, 0.3))
                flame(cv, x, GY - 4, hh, G, 0.85 * a); flame(cv, x, GY - 4, hh * 1.6, G, 0.2 * a, layer=cv.F)
        # ---- D4: a beam sweeps through and he changes colour (fire <-> soft) ----
        self.beam(cv, t, T(118), 960, P); self.beam(cv, t, T(126), 960, P)
        # ---- D5: the burst ----
        if T(132) <= t < T(144):
            k = (t - T(132)) / (T(144) - T(132)); hero.ring_burst(cv, t, T(132), C, 60, 1100, 1.0); hero.ring_burst(cv, t, T(136), C, 60, 900, 1.0)
            rng = np.random.default_rng(int(t * 8))
            for j in range(26):
                q = j * 0.83 + t * 0.2; r = 150 + 380 * ((j * 37) % 100) / 100
                p = (C[0] + r * math.cos(q), C[1] - 40 + r * math.sin(q) * 0.7)
                tw = 0.5 + 0.5 * math.sin(t * 6 + j * 2.1)
                cv.circle(p, 2.4, Wm, tw * (1 - ramp(k, 0.8, 1)), fill=True)
        # ---- D6: the visitor comes back; his heart lights hers ----
        if n >= 144:
            a = eo(ramp(n, 144, 146))
            on = eo(ramp(n, 149, 150))
            self.visitor(cv, 1215, a, 0.25, self.PF, t, heart_on=on)
            if T(148) <= t < T(149.5):
                u = (t - T(148)) / (T(149.5) - T(148)); tgt = (1215, GY - 200)
                cv.circle((lerp(C[0], tgt[0], eo(u)), lerp(C[1], tgt[1], eo(u)) - 60 * math.sin(u * math.pi)), 5, Wm, 1, fill=True)

        # ================= text =================
        for (txt, m0, st, x, y, size, m1, gold) in CAPS:
            if n < m0 - 0.1 or n > m1 + 1.2: continue
            g = tuple(range(len(txt))) if gold == 'all' else tuple(gold)
            tx.chars(txt, x, y, F(SERIF_BL if size >= 90 else SERIF_B, size), self.PF.WHITE, t, T(m0), T(m1), gold=g, stagger=E8 * st)
        if DROP <= n < 67.5:   # title block
            tx.chars('白羊座', 1400, 520, F(SERIF_BL, 168), self.PF.HI, t, T(DROP + 1), T(66.5), stagger=E8 * 0.5)
            tx.chars('ARIES  ·  3.21 – 4.19', 1400, 600, F(SANS_M, 34), (235, 225, 210), t, T(DROP + 3), T(66.5), stagger=0.02)
            tx.chars('火象  ·  黄道第一宫', 1400, 652, F(SANS_M, 32), self.PF.TAG, t, T(DROP + 4), T(66.5), stagger=0.03)
        if n >= 154:
            tx.chars('这里是洞悉', 1400, 720, F(SERIF_B, 46), (235, 235, 230), t, T(154), 999, stagger=E8 * 0.5)
            tx.chars('看见表象之外', 1400, 780, F(SANS_M, 32), self.PF.TAG, t, T(156), 999, stagger=E8 * 0.5)

        flash = 0.15 * pulse(t, T(20), 0.35) + 0.4 * pulse(t, T(DROP), 0.6) + 0.12 * pulse(t, T(118), 0.3) + 0.12 * pulse(t, T(126), 0.3) + 0.12 * pulse(t, T(132), 0.4)
        BG = self.PF.BG * 0.65
        img = cv.composite(BG, flash, glow=0.5) * self.PF.VIG
        if self.logo is not None and n >= 154:
            hero.logo = self.logo; img = hero._put_logo(img, 1400, 625, 110, 1.0, eo(ramp(n, 154, 157)))
        img = tx.blend(img)
        img *= ramp(t, 0, 0.1) * (1 - ramp(t, self.duration - 1.0, self.duration - 0.05))
        return np.clip(img * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- audio
def build_audio(music, out, duration):
    import render_long as R
    phase, e8 = R.grid(music); st = phase + MUSIC_START * e8; dr = T(DROP)
    tmp = tempfile.mkdtemp()
    a = os.path.join(tmp, 'a.wav'); b = os.path.join(tmp, 'b.wav')
    # before the drop: muffled and quieter (low-pass opens on the drop)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.4f}', '-t', f'{dr:.4f}', '-i', music, '-af',
                    'lowpass=f=900,volume=0.55,afade=t=in:d=0.3', '-ac', '1', '-ar', str(sfx.SR), a], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st + dr:.4f}', '-t', f'{duration - dr:.4f}', '-i', music, '-af',
                    f'afade=t=out:st={duration - dr - 2.2:.3f}:d=2.2', '-ac', '1', '-ar', str(sfx.SR), b], check=True)
    import wave
    def rd(p):
        w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mus = np.concatenate([rd(a), rd(b)])
    cues = [(T(18.6), sfx.whoosh(0.5), 0.25), (T(20), sfx.burn(1.1), 0.55), (T(26), sfx.chime(990, 1.4), 0.22),
            (T(44), sfx.burn(0.8), 0.35), (T(DROP) - 1.7, sfx.riser(1.7), 0.6), (T(DROP), sfx.impact(1.8), 0.9),
            (T(66.5), sfx.whoosh(0.6, up=False), 0.22)]
    for k, f in enumerate((1047, 1175, 1319, 1568)): cues.append((T(70 + 2 * k) + 0.42, sfx.chime(f, 1.2), 0.24))
    cues += [(T(83.7), sfx.whoosh(0.7, heavy=True), 0.5), (T(88), sfx.burn(1.0), 0.45),
             (T(101.2), sfx.whoosh(0.6), 0.28)]
    for m in (102, 104, 106, 108): cues.append((T(m) + 1.45, sfx.drop(), 0.55))
    cues += [(T(110.3), sfx.whoosh(0.6, up=False), 0.3), (T(110.5), sfx.sparkle(1.4, 16), 0.3),
             (T(118) - 0.3, sfx.whoosh(0.8, heavy=True), 0.55), (T(126) - 0.3, sfx.whoosh(0.8, heavy=True), 0.55),
             (T(132), sfx.impact(1.2), 0.35), (T(132), sfx.sparkle(1.6, 18), 0.35), (T(136), sfx.chime(1568, 1.4), 0.25),
             (T(149.3), sfx.chime(1319, 1.6), 0.28), (T(154), sfx.sparkle(1.6, 12), 0.25)]
    fx = sfx.mix(cues, duration)
    n = min(len(mus), len(fx)); mix = mus[:n] * 0.9 + fx[:n]
    mix = mix / max(1.0, np.abs(mix).max() / 0.97)
    sfx.write_wav(out, mix)


def worker(a, b, path, fps, logo):
    sc = AriesShort(logo)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(sc.frame(i / fps).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--music', default=os.path.join(HERE, '..', '..', 'media', 'Vibecoding_music.mp3'))
    ap.add_argument('--stills'); ap.add_argument('--fps', type=int, default=30); ap.add_argument('--workers', type=int, default=2)
    args = ap.parse_args()
    lp = os.path.join(HERE, '..', 'mbti', 'brand', 'logo.png')
    logo = cv2.imread(lp).astype('float32') / 255 if os.path.exists(lp) else None
    if args.stills:
        os.makedirs(args.out, exist_ok=True); sc = AriesShort(logo)
        for s in args.stills.split(','):
            cv2.imwrite(os.path.join(args.out, f'{float(s):06.2f}.jpg'), sc.frame(float(s)), [cv2.IMWRITE_JPEG_QUALITY, 92])
        return
    dur = T(END); N = int(dur * args.fps); k = args.workers; tmp = tempfile.mkdtemp(); t0 = time.time()
    cuts = [N * i // k for i in range(k + 1)]; parts = [os.path.join(tmp, f'p{i}.mp4') for i in range(k)]
    ps = [Process(target=worker, args=(cuts[i], cuts[i + 1], parts[i], args.fps, logo)) for i in range(k)]
    for p in ps: p.start()
    for p in ps: p.join()
    with open(os.path.join(tmp, 'l.txt'), 'w') as f: f.writelines(f"file '{p}'\n" for p in parts)
    v = os.path.join(tmp, 'v.mp4'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', v], check=True)
    au = os.path.join(tmp, 'a.wav'); build_audio(args.music, au, dur)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-i', au, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
                    '-movflags', '+faststart', '-shortest', args.out], check=True)
    print(f'wrote {args.out} ({dur:.1f}s) in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
