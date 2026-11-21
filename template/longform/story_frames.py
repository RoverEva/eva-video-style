#!/usr/bin/env python3
"""16 story keyframes for 「白羊座的内心世界」 8-minute cut.

Each keyframe is its own scene (place, shot size, mood), not the same hero standing in the middle:
a line-art protagonist with a small flame-heart at his chest, a second person, and line-art sets
(street, room, phone, rain, track, door, mountain...). Same glowing line language as the rest of the template.

  python3 template/longform/story_frames.py --out out/long/v3/keyframes
"""
import argparse, math, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import W, H, Palette, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, spline, lerp
import zodiac_signs  # registers fire / earth / air / water palettes
from vis import heart_pts

R = np.random.default_rng(11)


# ================================================================ figure
def _off(P, w):
    """offset a polyline by per-point half-widths w (left side, right side)"""
    P = np.asarray(P, float); d = np.gradient(P, axis=0); n = np.stack([-d[:, 1], d[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    w = np.asarray(w, float)[:, None]
    return P + n * w, P - n * w


def limb_shape(pts, w0, w1):
    P = spline(pts, n=10); w = np.linspace(w0, w1, len(P))
    L, Rr = _off(P, w)
    dvec = (P[-1] - P[-2]) / (np.linalg.norm(P[-1] - P[-2]) + 1e-9); nrm = (L[-1] - P[-1]) / (w1 + 1e-9)
    cap = [P[-1] + nrm * w1 * math.cos(q) + dvec * w1 * math.sin(q) for q in np.linspace(0, math.pi, 9)]
    return [tuple(p) for p in L] + [tuple(c) for c in cap] + [tuple(p) for p in Rr[::-1]]


BLACK = np.zeros(3)


def solid(cv, outline, col, a, th, fill=0.0):
    """occluding shape: erase what is behind (black fill), tint, then stroke the contour"""
    cv.poly(outline, BLACK, 1.0)
    if fill > 0: cv.poly(outline, col * fill, a)
    cv.path(outline + [outline[0]], col, a, th, smooth=False)


def limb(cv, pts, w0, w1, col, a, th=2.0):
    solid(cv, limb_shape(pts, w0, w1), col, a, th)


POSES = {
    # joints relative to the hip centre, body height 1 (head top -0.53, feet +0.47); x toward the facing side
    'stand':   dict(sh=(0.0, -0.34), el=(0.03, -0.17), ha=(0.04, -0.02), el2=(-0.03, -0.17), ha2=(-0.04, -0.02), kn=(0.02, 0.23), ft=(0.02, 0.47), kn2=(-0.02, 0.23), ft2=(-0.03, 0.47), head=(0.0, -0.45), tilt=0),
    'walk':    dict(sh=(0.0, -0.34), el=(0.08, -0.18), ha=(0.12, -0.05), el2=(-0.07, -0.18), ha2=(-0.12, -0.06), kn=(0.08, 0.22), ft=(0.13, 0.47), kn2=(-0.03, 0.24), ft2=(-0.13, 0.45), head=(0.01, -0.45), tilt=0),
    'run':     dict(sh=(0.07, -0.33), el=(0.17, -0.25), ha=(0.24, -0.33), el2=(-0.08, -0.2), ha2=(-0.17, -0.1), kn=(0.2, 0.12), ft=(0.15, 0.33), kn2=(-0.07, 0.24), ft2=(-0.26, 0.36), head=(0.1, -0.44), tilt=0.15),
    'lookback': dict(sh=(0.0, -0.34), el=(0.02, -0.17), ha=(0.03, -0.02), el2=(-0.03, -0.17), ha2=(-0.03, -0.02), kn=(0.04, 0.23), ft=(0.06, 0.47), kn2=(-0.02, 0.23), ft2=(-0.04, 0.47), head=(-0.015, -0.45), tilt=-0.1, back=True),
    'phone':   dict(sh=(0.0, -0.34), el=(0.06, -0.2), ha=(0.06, -0.3), el2=(-0.05, -0.2), ha2=(0.03, -0.29), kn=(0.02, 0.23), ft=(0.02, 0.47), kn2=(-0.02, 0.23), ft2=(-0.03, 0.47), head=(0.02, -0.44), tilt=0.35),
    'sitbed':  dict(sh=(0.02, -0.34), el=(0.06, -0.18), ha=(0.12, -0.2), el2=(0.0, -0.18), ha2=(0.1, -0.18), kn=(0.22, 0.0), ft=(0.22, 0.24), kn2=(0.2, 0.01), ft2=(0.18, 0.24), head=(0.05, -0.44), tilt=0.4),
    'hug':     dict(sh=(0.04, -0.3), el=(0.15, -0.12), ha=(0.2, -0.02), el2=(0.12, -0.1), ha2=(0.19, 0.0), kn=(0.2, -0.12), ft=(0.18, 0.08), kn2=(0.18, -0.1), ft2=(0.16, 0.08), head=(0.12, -0.38), tilt=0.55),
    'reach':   dict(sh=(0.0, -0.34), el=(0.13, -0.27), ha=(0.26, -0.25), el2=(-0.03, -0.17), ha2=(-0.04, -0.02), kn=(0.03, 0.23), ft=(0.05, 0.47), kn2=(-0.02, 0.23), ft2=(-0.04, 0.47), head=(0.02, -0.45), tilt=0.05),
    'umbrella': dict(sh=(0.0, -0.34), el=(0.1, -0.42), ha=(0.12, -0.55), el2=(-0.03, -0.17), ha2=(-0.04, -0.02), kn=(0.02, 0.23), ft=(0.02, 0.47), kn2=(-0.02, 0.23), ft2=(-0.03, 0.47), head=(0.01, -0.45), tilt=0.1),
    'argue':   dict(sh=(0.02, -0.34), el=(0.1, -0.22), ha=(0.18, -0.26), el2=(-0.05, -0.2), ha2=(-0.03, -0.05), kn=(0.03, 0.23), ft=(0.06, 0.47), kn2=(-0.03, 0.23), ft2=(-0.06, 0.47), head=(0.04, -0.45), tilt=-0.1),
    'climb':   dict(sh=(0.12, -0.3), el=(0.22, -0.3), ha=(0.3, -0.42), el2=(0.05, -0.17), ha2=(0.12, -0.08), kn=(0.18, 0.05), ft=(0.17, 0.28), kn2=(-0.06, 0.22), ft2=(-0.08, 0.47), head=(0.17, -0.41), tilt=0.25),
    'sit':     dict(sh=(-0.01, -0.34), el=(0.0, -0.17), ha=(0.06, -0.04), el2=(-0.08, -0.17), ha2=(-0.12, 0.0), kn=(0.24, -0.06), ft=(0.32, 0.12), kn2=(0.22, -0.02), ft2=(0.28, 0.12), head=(0.0, -0.45), tilt=-0.15),
    'down':    dict(sh=(0.03, -0.32), el=(0.12, -0.13), ha=(0.2, -0.08), el2=(0.06, -0.12), ha2=(0.15, -0.06), kn=(0.24, -0.05), ft=(0.27, 0.15), kn2=(0.22, -0.03), ft2=(0.24, 0.15), head=(0.09, -0.4), tilt=0.7),
}


def figure(cv, x, y, h, pose, col, a=1.0, d=1, heart=None, hair='short', P=None, th=2.0, coat=True):
    """line-art person drawn as occluding solid shapes; (x, y) = feet line, h = height px, d = facing (+1 right / -1 left)"""
    p = POSES[pose]; hipy = y - 0.47 * h
    J = lambda k: (x + d * p[k][0] * h, hipy + p[k][1] * h)
    hx, hy = J('head'); r = 0.078 * h
    sx, sy = J('sh'); sw = 0.085 * h
    shB = (sx - d * sw * 0.8, sy + 0.02 * h); shF = (sx + d * sw * 0.8, sy + 0.02 * h)
    hipB, hipF = (x - d * 0.035 * h, hipy), (x + d * 0.035 * h, hipy)
    # back arm + back leg
    limb(cv, [shB, J('el2'), J('ha2')], 0.03 * h, 0.02 * h, col * 0.75, a, th)
    limb(cv, [hipB, J('kn2'), J('ft2')], 0.042 * h, 0.024 * h, col * 0.75, a, th)
    # torso / coat
    lean = (sx - x)
    hem = hipy + (0.13 * h if coat else 0.02 * h)
    tor = [(sx - sw, sy + 0.03 * h), (sx - sw * 0.98, sy + 0.15 * h), (x + lean * 0.3 - 0.075 * h, hipy - 0.04 * h), (x - 0.09 * h, hem),
           (x + 0.09 * h, hem), (x + lean * 0.3 + 0.075 * h, hipy - 0.04 * h), (sx + sw * 0.98, sy + 0.15 * h), (sx + sw, sy + 0.03 * h),
           (sx + sw * 0.4, sy - 0.012 * h), (sx - sw * 0.4, sy - 0.012 * h)]
    tor = [tuple(q) for q in spline(tor, n=6, closed=True)]
    # front leg goes over the coat only below the hem
    solid(cv, tor, col, a, th, fill=0.06)
    cv.path([(sx + d * 0.012 * h, sy + 0.01 * h), (x + d * 0.02 * h, hem - 0.01 * h)], col, 0.45 * a, th * 0.8)   # coat opening
    limb(cv, [hipF, J('kn'), J('ft')], 0.044 * h, 0.025 * h, col, a, th)
    if coat: solid(cv, [q for q in tor if q[1] > hipy - 0.06 * h] or tor, col, a, th, fill=0.06) if False else None
    limb(cv, [shF, J('el'), J('ha')], 0.032 * h, 0.021 * h, col, a, th)
    # neck + head
    nk = [(hx - 0.025 * h, hy + r * 0.7), (hx + 0.025 * h, hy + r * 0.7), (sx + 0.03 * h, sy + 0.005 * h), (sx - 0.03 * h, sy + 0.005 * h)]
    solid(cv, nk, col, a, th)
    tilt = p.get('tilt', 0) * d
    head = []
    for q in np.linspace(0, 2 * math.pi, 48):
        ex, ey = r * 0.92 * math.cos(q), r * 1.1 * math.sin(q)
        if ey > 0: ex *= 1 - 0.25 * (ey / (r * 1.1)) ** 2     # narrower jaw
        head.append((hx + ex * math.cos(tilt) - ey * math.sin(tilt), hy + ex * math.sin(tilt) + ey * math.cos(tilt)))
    if not p.get('back'):   # nose bump toward the facing side
        k = int(np.argmax([d * (q[0] - hx) for q in head])); nx, ny = head[k]
        head = head[:k] + [(nx + d * r * 0.16, ny + r * 0.12)] + head[k + 1:]
    solid(cv, head, col, a, th)
    if hair:
        if hair == 'long':
            hp = [(hx + d * r * 0.85, hy - r * 0.55), (hx + d * r * 0.2, hy - r * 1.22), (hx - d * r * 0.8, hy - r * 0.95), (hx - d * r * 1.12, hy + r * 0.3),
                  (hx - d * r * 1.0, hy + r * 2.4), (hx - d * r * 0.55, hy + r * 2.5), (hx - d * r * 0.5, hy + r * 0.2), (hx + d * r * 0.4, hy - r * 0.5)]
        else:
            hp = [(hx + d * r * 0.95, hy - r * 0.35), (hx + d * r * 0.55, hy - r * 1.15), (hx - d * r * 0.4, hy - r * 1.25), (hx - d * r * 1.05, hy - r * 0.6),
                  (hx - d * r * 1.0, hy + r * 0.35), (hx - d * r * 0.55, hy - r * 0.15), (hx + d * r * 0.3, hy - r * 0.55)]
        hp = [tuple(q) for q in spline(hp, n=6, closed=True)]
        cv.poly(hp, col * 0.22, a); cv.path(hp + [hp[0]], col, a, th, smooth=False)
    if not p.get('back'):   # eye
        ex_, ey_ = hx + d * r * 0.45, hy - r * 0.05 + tilt * r * 0.5
        cv.path([(ex_ - r * 0.12, ey_), (ex_ + r * 0.12, ey_ + r * 0.02)], col, a, th * 0.9, smooth=False)
    if heart is not None and P is not None:
        c = (sx + d * 0.012 * h, sy + 0.11 * h); s_ = 0.03 * h * heart
        hpp = [(c[0] + s_ * u, c[1] + s_ * v) for u, v in heart_pts(0, 0, 1.0, 40)]
        cv.poly(hpp, P.WARM, 0.95 * a); cv.glow(c, s_ * 2.4, P.GOLD, 0.5 * a)
    return dict(head=(hx, hy), hand=J('ha'), hand2=J('ha2'), chest=(sx, sy + 0.11 * h), r=r)


# ================================================================ set pieces
def ground(cv, y, P, a=0.6, x0=-50, x1=1970): cv.path([(x0, y), (x1, y)], P.LINE, a, 1.4, smooth=False)


def stars(cv, P, n=80, a=0.5, ymax=600):
    rr = np.random.default_rng(5)
    for _ in range(n):
        cv.circle((rr.uniform(0, W), rr.uniform(0, ymax)), rr.uniform(0.7, 1.7), P.LINE, a * rr.uniform(0.3, 1), fill=True)


def skyline(cv, y, P, a=0.5, seed=2, x0=0, x1=W, hmin=120, hmax=380):
    rr = np.random.default_rng(seed); x = x0
    while x < x1:
        w = rr.uniform(70, 160); h = rr.uniform(hmin, hmax)
        cv.path([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], P.DIM * 1.6, a, 1.3, smooth=False)
        for wy in np.arange(y - h + 22, y - 14, 26):
            for wx in np.arange(x + 14, x + w - 12, 22):
                if rr.random() < 0.18: cv.poly([(wx, wy), (wx + 8, wy), (wx + 8, wy + 11), (wx, wy + 11)], P.WARM, a * 0.7)
        x += w + rr.uniform(4, 20)


def lamp(cv, x, y, h, P, a=1.0, d=1):
    cv.path([(x, y), (x, y - h), (x + d * 30, y - h - 18), (x + d * 60, y - h - 8)], P.LINE, a, 2, smooth=True)
    lx, ly = x + d * 62, y - h
    cv.path([(lx - 14, ly - 6), (lx + 14, ly - 6), (lx + 8, ly + 6), (lx - 8, ly + 6), (lx - 14, ly - 6)], P.GOLD, a, 1.8, smooth=False)
    cv.poly([(lx - 8, ly + 6), (lx + 8, ly + 6), (lx + 150, y), (lx - 150, y)], P.GOLD * 0.12, a, layer=cv.F)
    cv.glow((lx, ly + 4), 40, P.WARM, 0.9 * a)
    cv.path([(lx - 150, y), (lx + 150, y)], P.GOLD, 0.35 * a, 2, smooth=False)


def rain(cv, P, a=0.5, n=260, slant=0.18, seed=4, y0=0, y1=H):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        x = rr.uniform(-100, W + 100); y = rr.uniform(y0, y1); L = rr.uniform(14, 34)
        cv.path([(x, y), (x - slant * L, y + L)], P.LINE, a * rr.uniform(0.3, 1), 1.0, smooth=False)


def window(cv, x, y, w, h, P, a=1.0, moon=True):
    cv.path([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], P.LINE, a, 2, smooth=False)
    cv.path([(x + w / 2, y), (x + w / 2, y + h)], P.LINE, 0.7 * a, 1.4, smooth=False)
    cv.path([(x, y + h / 2), (x + w, y + h / 2)], P.LINE, 0.7 * a, 1.4, smooth=False)
    if moon:
        c = (x + w * 0.72, y + h * 0.28); r = min(w, h) * 0.12
        cv.circle(c, r, P.WARM, a, fill=True); cv.circle((c[0] + r * 0.45, c[1] - r * 0.2), r * 0.95, (0, 0, 0), 1.0, fill=True)
        cv.glow(c, r * 3, P.SOFT, 0.5 * a)


def phone_big(cv, tx, cx, cy, w, h, P, msgs, a=1.0):
    x0, y0 = cx - w / 2, cy - h / 2; r = 46
    pts = []
    for (qx, qy, q0) in ((x0 + w - r, y0 + r, -math.pi / 2), (x0 + w - r, y0 + h - r, 0), (x0 + r, y0 + h - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        pts += [(qx + r * math.cos(q), qy + r * math.sin(q)) for q in np.linspace(q0, q0 + math.pi / 2, 8)]
    cv.path(pts + [pts[0]], P.SOFT, a, 2.6, smooth=False)
    cv.path([(cx - 50, y0 + 26), (cx + 50, y0 + 26)], P.LINE, 0.8 * a, 3, smooth=False)
    cv.poly(pts, P.SOFT * 0.05, a, layer=cv.F)
    for (txt, side, yy, style) in msgs:   # style: 'sent' | 'recv' | 'deleted' | 'typing'
        fs = 40; tw = len(txt) * fs + 60; bx = x0 + w - 30 - tw if side > 0 else x0 + 30
        col = P.GOLD if side > 0 else P.LINE
        al = 0.35 if style == 'deleted' else 1.0
        bpts = [(bx, yy - 34), (bx + tw, yy - 34), (bx + tw, yy + 34), (bx, yy + 34), (bx, yy - 34)]
        cv.path(bpts, col, a * al, 2, smooth=False)
        if style == 'deleted': cv.path([(bx + 20, yy), (bx + tw - 20, yy)], P.WARM, 0.8 * a, 2, smooth=False)
        tx.chars(txt, bx + tw / 2, yy + 14, F(SERIF_B, fs), (240, 240, 235) if style != 'deleted' else (150, 140, 130), 1, 0, 99, stagger=0)
        if style == 'typing':
            cv.path([(bx + tw - 22, yy - 22), (bx + tw - 22, yy + 22)], P.WARM, a, 2.5, smooth=False)


def mountain(cv, P, a=1.0):
    ridge = [(-50, 1000), (250, 860), (480, 900), (760, 620), (980, 520), (1130, 300), (1240, 230), (1380, 360), (1600, 480), (1800, 560), (1980, 620)]
    cv.path(ridge, P.LINE, a, 2.2, smooth=False)
    cv.path([(-50, 1040), (400, 980), (900, 1010), (1400, 960), (1980, 1000)], P.DIM * 1.6, 0.6 * a, 1.4)
    return ridge


def caption(tx, lines, x, y, P, size=64, gold=()):
    for k, l in enumerate(lines):
        g = gold[k] if k < len(gold) else ()
        tx.chars(l, x, y + k * int(size * 1.38), F(SERIF_B, size), P.WHITE, 1, 0, 99, gold=g, stagger=0)


def label(tx, idx, tm, title, P):
    tx.chars(f'{idx:02d}', 70, 78, F(SANS_M, 30), P.TAG, 1, 0, 99, stagger=0, anchor='l')
    tx.chars(f'{tm}  ·  {title}', 120, 78, F(SANS_M, 26), (170, 170, 165), 1, 0, 99, stagger=0, anchor='l')


# ================================================================ the 16 scenes
def scenes():
    PF, PV, PA, PW = Palette('fire'), Palette('violet'), Palette('azure'), Palette('water')
    S = []

    def s01(cv, tx):   # extreme close: one spark
        P = PF; c = (960, 600)
        cv.circle(c, 7, P.WARM, 1, fill=True); cv.glow(c, 46, P.GOLD, 1.0)
        for r_, al in ((120, 0.5), (260, 0.25)): cv.circle(c, r_, P.GOLD, al, 1.4)
        caption(tx, ['他的心里', '住着一团火'], 960, 190, P, 72, [(), (3, 4)])
        return P, '0:00', '开场 · 黑暗里一颗火星'
    S.append(s01)

    def s02(cv, tx):   # inside the flame, a heart
        P = PF; c = (960, 640); h = 620
        for k, (sc, col, th) in enumerate(((1.0, P.GOLD, 2.4), (0.78, P.WARM, 1.8), (1.25, P.GOLD, 1.2))):
            w = h * sc * 0.36; hh = h * sc; base = c[1] + 0.42 * h
            pts = [(c[0] + 0.04 * hh, base - hh), (c[0] + w * 0.55, base - hh * 0.45), (c[0] + w * 0.5, base - hh * 0.15), (c[0], base), (c[0] - w * 0.5, base - hh * 0.15), (c[0] - w * 0.55, base - hh * 0.45)]
            cv.path(list(spline(pts, n=10, closed=True)), col, 0.9 - 0.25 * k, th, smooth=False)
        hp = [(c[0] + 120 * u, c[1] + 120 * v) for u, v in heart_pts(0, 0, 1.0, 60)]
        cv.path(hp, P.WARM, 1, 2.6, smooth=False); cv.poly(hp, P.WARM * 0.35, 0.8, layer=cv.F); cv.glow(c, 130, P.GOLD, 0.7)
        for j in range(22):
            v = j / 22; cv.circle((c[0] + 260 * math.sin(j * 2.3), c[1] - 200 - 300 * v), 2.2, P.WARM, 1 - v, fill=True)
        caption(tx, ['可火的最中间', '藏着一颗很软的心'], 960, 150, P, 72, [(), (4, 5)])
        return P, '0:06', '推进火焰 · 火里有一颗心'
    S.append(s02)

    def s03(cv, tx):   # drop: wide, he stands on a hill above the city, title right
        P = PF; stars(cv, P, 120, 0.6, 700); skyline(cv, 1010, P, 0.35, 3, 0, W, 60, 200)
        cv.path([(-50, 900), (300, 860), (620, 820), (900, 830), (1200, 900), (1500, 960), (1970, 980)], P.LINE, 0.8, 2)
        f = figure(cv, 620, 822, 360, 'stand', P.SOFT, 1.0, 1, heart=1.4, P=P)
        for r_, al in ((160, 0.6), (420, 0.35), (760, 0.18)): cv.circle(f['chest'], r_, P.GOLD, al, 1.6)
        tx.chars('白羊座的内心世界', 1380, 500, F(SERIF_BL, 104), P.HI, 1, 0, 99, stagger=0)
        tx.chars('外表有多倔强  内心就有多柔软', 1380, 600, F(SERIF_B, 46), P.WHITE, 1, 0, 99, gold=(4, 5, 12, 13), stagger=0)
        return P, '0:13', 'drop · 城市之上，标题落下'
    S.append(s03)

    def s04(cv, tx):   # 燃: the start line — others hesitate, he is already gone
        P = PF; ground(cv, 900, P, 0.7)
        for k in range(5): cv.path([(0, 900 + k * 0), (W, 900)], P.LINE, 0.0)
        cv.path([(360, 900), (360, 760)], P.WARM, 0.5, 1.4, smooth=False)
        for k, x in enumerate((180, 250, 320)): figure(cv, x, 900, 250, 'stand', P.DIM * 2.2, 0.7, 1)
        f = figure(cv, 1180, 890, 330, 'run', P.SOFT, 1.0, 1, heart=1.3, P=P)
        for k in range(9):   # flame trail
            y = 650 + k * 22; L = 260 + 60 * math.sin(k)
            cv.path([(1080 - L, y), (1080 - 40, y - 6)], P.GOLD, 0.9 - 0.08 * k, 2, smooth=False)
        flame(cv, 1010, 820, 90, P.GOLD, 0.5); cv.glow(f['chest'], 90, P.GOLD, 0.5)
        caption(tx, ['别人还在犹豫', '他已经冲出去了'], 1360, 300, P, 64, [(), (3, 4, 5)])
        return P, '0:20', '燃 · 起跑线，别人还在原地'
    S.append(s04)

    def s05(cv, tx):   # 燃 reversal: he stops and looks back; far away someone walks away under a lamp
        P = PF
        cv.path([(-50, 1080), (900, 620), (1020, 620), (1970, 1080)], P.LINE, 0.5, 1.4, smooth=False)
        cv.path([(960, 620), (960, 1080)], P.DIM * 1.6, 0.4, 1, smooth=False)
        lamp(cv, 1050, 640, 160, P, 0.8, -1)
        figure(cv, 990, 640, 100, 'walk', P.LINE, 0.65, 1, hair='long')
        f = figure(cv, 560, 1000, 420, 'lookback', P.SOFT, 1.0, -1, heart=0.6, P=P)
        caption(tx, ['跑得最快的人', '最怕的是什么？'], 1420, 300, P, 64)
        caption(tx, ['在乎的人转身'], 1420, 520, P, 72, [(0, 1, 2, 3, 4, 5)])
        return P, '0:40', '燃 · 反转：他停下回头'
    S.append(s05)

    def s06(cv, tx):   # 直: over-the-shoulder phone, message typed and deleted
        P = PF
        hx, hy = 470, 640   # back of his head and shoulder, big, bottom-left
        sh = [(-40, 1100), (60, 900), (200, 820), (330, 800), (420, 760), (520, 760), (610, 800), (720, 830), (860, 900), (960, 1100)]
        solid(cv, [tuple(q) for q in spline(sh, n=6)], P.SOFT, 0.8, 2.2)
        hd = [(hx + 150 * math.cos(q), hy + 175 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 50)]
        solid(cv, hd, P.SOFT, 0.8, 2.2)
        hp = [(hx - 150, hy + 10), (hx - 140, hy - 120), (hx - 30, hy - 182), (hx + 110, hy - 150), (hx + 150, hy - 40), (hx + 60, hy - 90), (hx - 60, hy - 60), (hx - 120, hy + 40)]
        cv.poly([tuple(q) for q in spline(hp, n=6, closed=True)], P.SOFT * 0.2, 0.8)
        cv.path([tuple(q) for q in spline(hp, n=6, closed=True)], P.SOFT, 0.8, 2)
        cv.glow((760, 640), 260, P.SOFT, 0.18)
        phone_big(cv, tx, 1080, 540, 560, 900, P, [('最近还好吗', -1, 300, 'recv'), ('我其实很想你', 1, 430, 'deleted'), ('没事 就是问问', 1, 560, 'deleted'),
                                                  ('在吗', 1, 700, 'typing')])
        cv.glow((1080, 540), 380, P.SOFT, 0.12)
        caption(tx, ['一句话', '删了又删'], 1640, 380, P, 64, [(), (0, 1, 2, 3)])
        return P, '1:10', '直 · 手机特写：删了又删，只剩「在吗」'
    S.append(s06)

    def s07(cv, tx):   # 直: 3 a.m., sitting on the bed edge, phone light on his face
        P = PA; window(cv, 1230, 180, 420, 380, P, 0.9)
        cv.path([(0, 760), (W, 760)], P.LINE, 0.35, 1.2, smooth=False)
        cv.path([(260, 760), (260, 640), (980, 640), (980, 760)], P.LINE, 0.8, 2, smooth=False)
        cv.path([(260, 700), (980, 700)], P.LINE, 0.5, 1.4, smooth=False)
        c = (520, 230); cv.circle(c, 70, P.LINE, 0.8, 2)
        cv.path([c, (c[0], c[1] - 48)], P.WARM, 0.9, 2.4, smooth=False); cv.path([c, (c[0] + 30, c[1] + 18)], P.WARM, 0.9, 2.4, smooth=False)
        f = figure(cv, 560, 940, 500, 'sitbed', P.SOFT, 0.95, 1, heart=0.6, P=PF)
        ph = (f['hand'][0] + 6, f['hand'][1] - 10)
        cv.path([(ph[0] - 18, ph[1] - 30), (ph[0] + 18, ph[1] - 30), (ph[0] + 18, ph[1] + 30), (ph[0] - 18, ph[1] + 30), (ph[0] - 18, ph[1] - 30)], P.WARM, 1, 2, smooth=False)
        cv.glow(ph, 70, P.WARM, 0.35)
        caption(tx, ['然后盯着屏幕', '等了一整晚'], 1440, 760, P, 60, [(), (3, 4, 5)])
        return P, '1:35', '直 · 凌晨三点，坐在床边等回复'
    S.append(s07)

    def s08(cv, tx):   # 软: close-up of two hands passing a warm cup
        P = PF; cx, cy = 960, 560
        cup = [(cx - 110, cy - 90), (cx - 95, cy + 110), (cx - 60, cy + 140), (cx + 60, cy + 140), (cx + 95, cy + 110), (cx + 110, cy - 90)]
        cv.path(cup, P.SOFT, 1, 2.6); cv.path([(cx - 110, cy - 90), (cx + 110, cy - 90)], P.SOFT, 0.9, 2, smooth=False)
        cv.path([(cx + 110, cy - 40), (cx + 170, cy - 30), (cx + 175, cy + 40), (cx + 100, cy + 60)], P.SOFT, 1, 2.4)
        for j in range(3):
            x0 = cx - 50 + 50 * j; cv.path([(x0 + 14 * math.sin(v * 6 + j), cy - 110 - v * 230) for v in np.linspace(0, 1, 20)], P.WARM, 0.8, 1.8)
        for d, col in ((-1, P.LINE), (1, P.GOLD)):   # two forearms in sleeves, hands wrapped around the cup
            el = (cx + d * 760, cy + 420); wr = (cx + d * 150, cy + 90)
            solid(cv, limb_shape([el, (cx + d * 420, cy + 230), wr], 70, 40), col, 1, 2.4, fill=0.05)
            cv.path([(cx + d * 230, cy + 60), (cx + d * 205, cy + 150)], col, 0.8, 2)   # cuff
            hand = [(cx + d * 175, cy + 20), (cx + d * 95, cy - 10), (cx + d * 70, cy + 40), (cx + d * 75, cy + 95), (cx + d * 110, cy + 130), (cx + d * 175, cy + 135)]
            hand = [tuple(q) for q in spline(hand, n=6, closed=True)]
            solid(cv, hand, col, 1, 2.2, fill=0.05)
            for k in range(3): cv.path([(cx + d * 78, cy + 40 + 26 * k), (cx + d * 118, cy + 34 + 26 * k)], col, 0.8, 1.8, smooth=False)
        cv.glow((cx, cy), 260, P.GOLD, 0.35)
        caption(tx, ['你随手递来的一杯热水'], 960, 940, P, 64, [(7, 8)])
        caption(tx, ['他会记很久很久'], 960, 1030, P, 52)
        return P, '1:50', '软 · 手部特写：递来一杯热水'
    S.append(s08)

    def s09(cv, tx):   # 疼: split by a door — party outside, he sits behind the door crying
        P = PV; ground(cv, 900, P, 0.5)
        cv.path([(980, 900), (980, 220), (1260, 220), (1260, 900)], P.LINE, 1, 2.4, smooth=False)
        cv.poly([(990, 225), (1250, 225), (1250, 895), (990, 895)], P.WARM * 0.05, 1, layer=cv.F)
        for k, x in enumerate(np.linspace(80, 860, 7)):
            figure(cv, x, 900, 260 + 30 * math.sin(k), 'walk' if k % 2 else 'stand', PF.GOLD, 0.6, 1 if k % 2 else -1, hair='long' if k % 3 == 0 else 'short')
        for j in range(30): cv.circle((R.uniform(60, 900), R.uniform(250, 560)), 2.4, PF.WARM, R.uniform(0.3, 0.9), fill=True)
        f = figure(cv, 1420, 900 + 0.39 * 420, 420, 'hug', P.SOFT, 1.0, -1, heart=0.5, P=PF)
        for k in range(3):
            tp = (f['head'][0] - 10 - 6 * k, f['head'][1] + 40 + 70 * k)
            cv.poly(list(spline([(tp[0], tp[1] - 12), (tp[0] + 7, tp[1] + 4), (tp[0], tp[1] + 10), (tp[0] - 7, tp[1] + 4)], n=4, closed=True)), P.WARM, 0.9 - 0.25 * k)
        caption(tx, ['关上门', '一个人哭完'], 1640, 330, P, 64, [(), (3, 4)])
        caption(tx, ['打开门', '又是那个没心没肺的他'], 520, 160, P, 44)
        return P, '2:40', '疼 · 一扇门：门外热闹，门内哭'
    S.append(s09)

    def s10(cv, tx):   # 疼: night rain street, walking alone, reflection
        P = PA; skyline(cv, 760, P, 0.45, 9, 0, W, 160, 420)
        cv.path([(0, 760), (W, 760)], P.LINE, 0.6, 1.4, smooth=False)
        lamp(cv, 1500, 760, 300, P, 0.9, -1)
        f = figure(cv, 760, 760, 330, 'walk', P.SOFT, 1.0, 1, heart=0.5, P=PF)
        cvR = Canvas(Cam(1.0))   # reflection: mirrored, faint
        figure(cvR, 760, 760, 330, 'walk', P.SOFT, 0.35, 1)
        refl = cv2.flip(cvR.L, 0)[H - 2 * 760 - 1 + 0: H, :] if False else None
        cv.L[760:1080] += cv2.flip(cvR.L[440:760], 0) * 0.35
        for k in range(6): cv.path([(560 + k * 60, 800 + k * 30), (680 + k * 60, 800 + k * 30)], P.LINE, 0.35, 1.2, smooth=False)
        rain(cv, P, 0.6, 320)
        caption(tx, ['他会笑着说', '“算了”'], 1440, 260, P, 64, [(), (1, 2)])
        return P, '3:05', '疼 · 雨夜街头，一个人走'
    S.append(s10)

    def s11(cv, tx):   # 冲: argument — two profiles, lightning between
        P = PF
        a_ = figure(cv, 660, 1000, 640, 'argue', P.SOFT, 1.0, 1, heart=1.2, P=P)
        b_ = figure(cv, 1260, 1000, 600, 'stand', PV.LINE, 0.9, -1, hair='long')
        zz = [(860, 250), (930, 330), (890, 380), (990, 470), (950, 520), (1060, 620)]
        cv.path(zz, P.WARM, 1, 3, smooth=False); cv.path(zz, P.GOLD, 0.4, 14, smooth=False, layer=cv.F)
        for j in range(14):
            p = (960 + R.uniform(-160, 160), R.uniform(200, 700)); q = R.uniform(0, 6.3); L = R.uniform(14, 34)
            cv.path([p, (p[0] + L * math.cos(q), p[1] + L * math.sin(q))], P.GOLD, 0.8, 2, smooth=False)
        caption(tx, ['吵架时', '专挑最狠的话'], 960, 900, P, 60, [(), (2, 3, 4)])
        return P, '3:35', '冲 · 争吵：两个侧脸之间的闪电'
    S.append(s11)

    def s12(cv, tx):   # 冲: the morning after — breakfast left at the door, sunrise window
        P = PF; window(cv, 1180, 140, 520, 460, P, 0.9, moon=False)
        sc = (1440, 600)
        cv.path([(sc[0] + 170 * math.cos(q), sc[1] + 170 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 40)], P.WARM, 1, 2.4)
        for k in range(9):
            q = math.pi + (k + 0.5) * math.pi / 9; cv.path([(sc[0] + 200 * math.cos(q), sc[1] + 200 * math.sin(q)), (sc[0] + 260 * math.cos(q), sc[1] + 260 * math.sin(q))], P.GOLD, 0.8, 2, smooth=False)
        cv.glow(sc, 300, P.GOLD, 0.35)
        cv.path([(200, 760), (1100, 760)], P.LINE, 1, 2.4, smooth=False); cv.path([(260, 760), (260, 1000)], P.LINE, 0.8, 2, smooth=False); cv.path([(1040, 760), (1040, 1000)], P.LINE, 0.8, 2, smooth=False)
        bag = [(520, 760), (500, 560), (700, 560), (680, 760)]; cv.path(bag + [bag[0]], P.SOFT, 1, 2.4, smooth=False)
        cv.path([(560, 560), (580, 500), (620, 500), (640, 560)], P.SOFT, 1, 2)
        cup = [(780, 760), (790, 620), (880, 620), (890, 760)]; cv.path(cup + [cup[0]], P.SOFT, 1, 2.2, smooth=False)
        note = [(380, 700), (470, 690), (480, 750), (390, 760)]; cv.path(note + [note[0]], P.GOLD, 1, 2, smooth=False)
        hp = [(430 + 14 * u, 722 + 14 * v) for u, v in heart_pts(0, 0, 1.0, 30)]; cv.poly(hp, P.WARM, 1)
        caption(tx, ['第二天', '默默给你带了早餐'], 960, 160, P, 64, [(), (6, 7)])
        caption(tx, ['这就是他的「对不起」'], 640, 900, P, 50, [(6, 7, 8)])
        return P, '4:00', '冲 · 第二天早上：桌上的早餐和小纸条'
    S.append(s12)

    def s13(cv, tx):   # 爱: he holds the umbrella over her, half of him in the rain
        P = PF; ground(cv, 920, P, 0.5)
        f1 = figure(cv, 860, 920, 440, 'umbrella', P.SOFT, 1.0, 1, heart=1.3, P=P)
        figure(cv, 1060, 920, 410, 'stand', PV.SOFT, 0.95, -1, hair='long')
        top = (f1['hand'][0], f1['hand'][1] - 20); cx_ = 1060
        dome = [(cx_ + 230 * math.cos(q), top[1] + 30 + 140 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 40)]
        cv.path(dome, P.GOLD, 1, 2.6); cv.path([dome[0], dome[-1]], P.GOLD, 0.8, 1.6, smooth=False)
        cv.path([(cx_ - 150, top[1] - 80), f1['hand']], P.GOLD, 1, 2.2, smooth=False)
        rr = np.random.default_rng(8)
        for _ in range(380):
            x = rr.uniform(0, W); y = rr.uniform(0, 920); L = rr.uniform(14, 30)
            if cx_ - 225 < x < cx_ + 225 and y > top[1] - 110: continue
            cv.path([(x, y), (x - 4, y + L)], PA.LINE, 0.55 * rr.uniform(0.3, 1), 1, smooth=False)
        for k in range(10):   # rain hits his outer shoulder
            p = (f1['head'][0] - 60 + rr.uniform(-25, 10), f1['head'][1] - 60 + k * 34)
            cv.path([p, (p[0] - 3, p[1] + 18)], PA.LINE, 0.8, 1.2, smooth=False)
        caption(tx, ['下雨了', '伞已经在你头顶'], 1600, 260, P, 64, [(), (4, 5)])
        return P, '4:25', '爱 · 伞全偏向她，他半边在雨里'
    S.append(s13)

    def s14(cv, tx):   # 独: wide — the crowd leaves left, he walks the long lit road alone
        P = PA; stars(cv, P, 60, 0.45, 500)
        cv.path([(-50, 760), (W + 50, 760)], P.LINE, 0.5, 1.2, smooth=False)
        cv.path([(700, 1080), (1330, 760)], P.LINE, 0.7, 1.6, smooth=False); cv.path([(1150, 1080), (1430, 760)], P.LINE, 0.7, 1.6, smooth=False)
        for k, u in enumerate((0.15, 0.4, 0.7)):
            x, y = lerp(1430, 1150, u) + lerp(30, 240, u), lerp(760, 1080, u); sc = lerp(0.35, 1.0, u)
            lamp(cv, x, y, 320 * sc, P, 0.7, -1)
        for k, x in enumerate(np.linspace(120, 560, 6)): figure(cv, x, 790, 150, 'walk', PF.GOLD, 0.55, -1)
        for j in range(20): cv.circle((R.uniform(80, 600), R.uniform(520, 700)), 2, PF.WARM, R.uniform(0.2, 0.7), fill=True)
        figure(cv, 1290, 900, 210, 'walk', P.SOFT, 1.0, 1, heart=1.0, P=PF)
        caption(tx, ['可散场的路上', '他会突然安静'], 760, 260, P, 64, [(), (4, 5)])
        return P, '5:10', '独 · 远景：人群往左散，他一个人往右走'
    S.append(s14)

    def s15(cv, tx):   # 赢: climbing a steep ridge at night toward a flag
        P = PF; stars(cv, P, 140, 0.6, 700)
        ridge = mountain(cv, P, 0.9)
        cv.path([(1240, 230), (1240, 120)], P.GOLD, 1, 2.2, smooth=False)
        cv.path([(1240, 120), (1310, 136), (1300, 160), (1240, 168)], P.WARM, 1, 2, smooth=False); cv.glow((1260, 140), 60, P.GOLD, 0.6)
        figure(cv, 900, 560, 220, 'climb', P.SOFT, 1.0, 1, heart=1.3, P=P)
        for k in range(10): cv.circle((lerp(300, 880, k / 10), lerp(880, 570, k / 10) + 6 * math.sin(k)), 2.2, P.WARM, 0.25 + 0.06 * k, fill=True)
        caption(tx, ['热情会退', '可火小了', '他还在往上走'], 520, 220, P, 60, [(), (), (4, 5, 6)])
        return P, '6:10', '赢 · 夜里爬山，火小了还在往上'
    S.append(s15)

    def s16(cv, tx):   # 真: dawn on the summit, side by side, two lit hearts
        P = PF; c = (1430, 740)
        cv.path([(c[0] + 260 * math.cos(q), c[1] + 260 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 50)], P.WARM, 1, 2.6)
        for k in range(15):
            q = math.pi + (k + 0.5) * math.pi / 15; cv.path([(c[0] + 300 * math.cos(q), c[1] + 300 * math.sin(q)), (c[0] + 400 * math.cos(q), c[1] + 400 * math.sin(q))], P.GOLD, 0.7, 2, smooth=False)
        cv.glow(c, 520, P.GOLD, 0.3)
        cv.poly([(-50, 760), (500, 720), (800, 690), (1100, 690), (1400, 720), (1970, 770), (1970, 1080), (-50, 1080)], BLACK, 1.0)
        cv.path([(-50, 760), (500, 720), (800, 690), (1100, 690), (1400, 720), (1970, 770)], P.LINE, 1, 2.2)
        figure(cv, 700, 700 + 0.12 * 330, 330, 'sit', P.SOFT, 1.0, 1, heart=1.4, P=P)
        figure(cv, 900, 692 + 0.12 * 310, 310, 'sit', PV.SOFT, 0.95, 1, heart=1.0, P=P, hair='long')
        caption(tx, ['如果你身边有白羊', '别只看见他的火', '也看看火中间的那颗心'], 960, 160, P, 60, [(), (6,), (9,)])
        return P, '7:50', '真 · 天亮，山顶并肩，两颗心都亮着'
    S.append(s16)
    return S


def render(scene_fn, idx):
    cv = Canvas(Cam(1.0)); P0 = Palette('fire'); tx = Text(P0)
    P, tm, title = scene_fn(cv, tx)
    label(tx, idx, tm, title, P0)
    img = cv.composite(P.BG * 0.65, 0.0, glow=0.55) * P.VIG
    img = tx.blend(img)
    return np.clip(img * 255, 0, 255).astype(np.uint8), tm, title


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--only')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    S = scenes(); idx = range(1, 17) if not a.only else [int(x) for x in a.only.split(',')]
    for i in idx:
        im, tm, title = render(S[i - 1], i)
        cv2.imwrite(os.path.join(a.out, f'{i:02d}.png'), im); print(i, tm, title, flush=True)


if __name__ == '__main__':
    main()
