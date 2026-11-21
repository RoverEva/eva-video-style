#!/usr/bin/env python3
"""16 story keyframes for 「白羊座的内心世界」 8-minute cut — v2, directed.

Each keyframe is a designed shot (shot size, angle, light, depth, effects), not the same hero in the middle:
detailed occluding line-art people (coat, lapels, trousers, shoes, face, hair strands, hands), sets, and a
light-effects layer (glints, bokeh, god rays, milky way, meteors, lens flares, dust in beams, rain highlights).
A blurred foreground layer gives shallow depth of field; some shots use a dutch angle.

  python3 template/longform/story_frames.py --out out/long/v3/keyframes [--only 3,11]
"""
import argparse, math, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import W, H, Palette, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, spline, lerp
import zodiac_signs  # registers fire / earth / air / water palettes
from vis import heart_pts

BLACK = np.zeros(3)


# ================================================================ geometry helpers
def _off(P, w):
    P = np.asarray(P, float); d = np.gradient(P, axis=0); n = np.stack([-d[:, 1], d[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    w = np.asarray(w, float)[:, None]
    return P + n * w, P - n * w


def limb_shape(pts, w0, w1, n=10):
    P = spline(pts, n=n); w = np.linspace(w0, w1, len(P))
    L, Rr = _off(P, w)
    dvec = (P[-1] - P[-2]) / (np.linalg.norm(P[-1] - P[-2]) + 1e-9); nrm = (L[-1] - P[-1]) / (w1 + 1e-9)
    cap = [P[-1] + nrm * w1 * math.cos(q) + dvec * w1 * 0.8 * math.sin(q) for q in np.linspace(0, math.pi, 9)]
    return [tuple(p) for p in L] + [tuple(c) for c in cap] + [tuple(p) for p in Rr[::-1]], P


def solid(cv, outline, col, a, th, fill=0.0):
    """occluding shape: erase what is behind, tint, stroke the contour"""
    cv.poly(outline, BLACK, 1.0)
    if fill > 0: cv.poly(outline, col * fill, a)
    cv.path(outline + [outline[0]], col, a, th, smooth=False)


def sp(pts, n=8, closed=False): return [tuple(q) for q in spline(pts, n=n, closed=closed)]


# ================================================================ people
POSES = {
    'stand':   dict(sh=(0.0, -0.34), el=(0.035, -0.17), ha=(0.05, -0.03), el2=(-0.035, -0.17), ha2=(-0.05, -0.03), kn=(0.02, 0.23), ft=(0.03, 0.47), kn2=(-0.02, 0.23), ft2=(-0.03, 0.47), head=(0.005, -0.45), tilt=0),
    'walk':    dict(sh=(0.01, -0.34), el=(0.08, -0.18), ha=(0.12, -0.05), el2=(-0.07, -0.18), ha2=(-0.12, -0.06), kn=(0.08, 0.22), ft=(0.14, 0.47), kn2=(-0.03, 0.24), ft2=(-0.13, 0.45), head=(0.02, -0.45), tilt=0.05),
    'run':     dict(sh=(0.07, -0.33), el=(0.17, -0.25), ha=(0.24, -0.33), el2=(-0.08, -0.2), ha2=(-0.17, -0.1), kn=(0.2, 0.12), ft=(0.15, 0.33), kn2=(-0.07, 0.24), ft2=(-0.26, 0.36), head=(0.1, -0.44), tilt=0.15),
    'lookback': dict(sh=(0.0, -0.34), el=(0.03, -0.17), ha=(0.04, -0.03), el2=(-0.03, -0.17), ha2=(-0.04, -0.03), kn=(0.04, 0.23), ft=(0.06, 0.47), kn2=(-0.02, 0.23), ft2=(-0.04, 0.47), head=(-0.01, -0.45), tilt=-0.15),
    'sitbed':  dict(sh=(0.02, -0.34), el=(0.07, -0.18), ha=(0.13, -0.22), el2=(0.0, -0.18), ha2=(0.11, -0.2), kn=(0.22, 0.0), ft=(0.22, 0.24), kn2=(0.2, 0.01), ft2=(0.18, 0.24), head=(0.06, -0.44), tilt=0.45),
    'hug':     dict(sh=(0.04, -0.3), el=(0.15, -0.12), ha=(0.2, -0.02), el2=(0.12, -0.1), ha2=(0.19, 0.0), kn=(0.2, -0.12), ft=(0.18, 0.08), kn2=(0.18, -0.1), ft2=(0.16, 0.08), head=(0.12, -0.38), tilt=0.6),
    'umbrella': dict(sh=(0.0, -0.34), el=(0.1, -0.42), ha=(0.12, -0.55), el2=(-0.03, -0.17), ha2=(-0.04, -0.03), kn=(0.02, 0.23), ft=(0.03, 0.47), kn2=(-0.02, 0.23), ft2=(-0.03, 0.47), head=(0.015, -0.45), tilt=0.12),
    'argue':   dict(sh=(0.03, -0.34), el=(0.11, -0.22), ha=(0.2, -0.27), el2=(-0.05, -0.2), ha2=(-0.04, -0.05), kn=(0.03, 0.23), ft=(0.07, 0.47), kn2=(-0.03, 0.23), ft2=(-0.07, 0.47), head=(0.05, -0.45), tilt=-0.12),
    'turned':  dict(sh=(0.0, -0.34), el=(0.02, -0.17), ha=(0.03, -0.03), el2=(-0.04, -0.17), ha2=(-0.05, -0.03), kn=(0.01, 0.23), ft=(0.02, 0.47), kn2=(-0.03, 0.23), ft2=(-0.04, 0.47), head=(-0.01, -0.45), tilt=0.25),
    'climb':   dict(sh=(0.12, -0.3), el=(0.22, -0.3), ha=(0.3, -0.42), el2=(0.05, -0.17), ha2=(0.12, -0.08), kn=(0.18, 0.05), ft=(0.17, 0.28), kn2=(-0.06, 0.22), ft2=(-0.08, 0.47), head=(0.17, -0.41), tilt=0.25),
    'sit':     dict(sh=(-0.01, -0.34), el=(0.01, -0.17), ha=(0.07, -0.04), el2=(-0.08, -0.17), ha2=(-0.13, 0.0), kn=(0.24, -0.06), ft=(0.32, 0.12), kn2=(0.22, -0.02), ft2=(0.28, 0.12), head=(0.0, -0.45), tilt=-0.2),
}


def glint(cv, p, s, col, a=1.0, rot=0.0):
    """4-point star sparkle"""
    for k, (L, w) in enumerate(((s, 1.4), (s * 0.45, 1.0))):
        for q in (rot + k * math.pi / 4, rot + k * math.pi / 4 + math.pi / 2):
            dx, dy = L * math.cos(q), L * math.sin(q)
            cv.path([(p[0] - dx, p[1] - dy), (p[0] + dx, p[1] + dy)], col, a * (1 - 0.4 * k), w, smooth=False)
            cv.path([(p[0] - dx * 0.6, p[1] - dy * 0.6), (p[0] + dx * 0.6, p[1] + dy * 0.6)], col, a * 0.5, w * 4, smooth=False, layer=cv.F)
    cv.circle(p, max(1.2, s * 0.08), col, a, fill=True)


def figure(cv, x, y, h, pose, col, a=1.0, d=1, heart=None, hair='short', P=None, th=2.2, rim=None, dress=False):
    """detailed line-art person; (x, y) = feet line, h = height px, d = facing (+1 right / -1 left).
       rim: (dx, dy) direction of a key light -> the contour facing it gets a glow"""
    p = POSES[pose]; hipy = y - 0.47 * h
    J = lambda k: (x + d * p[k][0] * h, hipy + p[k][1] * h)
    hx, hy = J('head'); r = 0.074 * h
    sx, sy = J('sh'); sw = 0.088 * h
    shB = (sx - d * sw * 0.78, sy + 0.022 * h); shF = (sx + d * sw * 0.78, sy + 0.022 * h)
    hipB, hipF = (x - d * 0.035 * h, hipy - 0.01 * h), (x + d * 0.035 * h, hipy - 0.01 * h)
    thin = th * 0.55; dc = col * 0.75

    def shoe(ft, front):
        fx, fy = ft; L = 0.07 * h
        pts = sp([(fx - d * 0.02 * h, fy - 0.03 * h), (fx + d * L, fy - 0.012 * h), (fx + d * L * 1.05, fy + 0.006 * h), (fx - d * 0.03 * h, fy + 0.006 * h)], 5, True)
        solid(cv, pts, col if front else dc, a, th, fill=0.12)

    def arm(sh, el, ha, front):
        c = col if front else dc
        out, axis = limb_shape([sh, el, ha], 0.034 * h, 0.024 * h)
        solid(cv, out, c, a, th, fill=0.05)
        k = len(axis) - 4; t_ = axis[k] - axis[k - 1]; t_ /= np.linalg.norm(t_) + 1e-9; nn = np.array([-t_[1], t_[0]])
        cv.path([tuple(axis[k] + nn * 0.026 * h), tuple(axis[k] - nn * 0.026 * h)], c, a * 0.8, thin, smooth=False)
        e = len(axis) // 2; cv.path([tuple(axis[e] + nn * 0.02 * h), tuple(axis[e + 2] - nn * 0.008 * h)], c, a * 0.45, thin, smooth=False)
        hand = sp([(ha[0] - 0.018 * h, ha[1] - 0.004 * h), (ha[0] + d * 0.02 * h, ha[1] + 0.012 * h), (ha[0] + d * 0.012 * h, ha[1] + 0.045 * h),
                   (ha[0] - d * 0.012 * h, ha[1] + 0.05 * h), (ha[0] - d * 0.022 * h, ha[1] + 0.02 * h)], 5, True)
        solid(cv, hand, c, a, th * 0.85)
        cv.path([(ha[0] + d * 0.016 * h, ha[1] + 0.01 * h), (ha[0] + d * 0.03 * h, ha[1] + 0.028 * h)], c, a * 0.8, thin)

    def leg(hp, kn, ft, front):
        c = col if front else dc
        out, axis = limb_shape([hp, kn, ft], 0.047 * h, 0.03 * h)
        solid(cv, out, c, a, th, fill=0.05)
        cv.path([tuple(q) for q in axis[len(axis) // 3: -3]], c, a * 0.35, thin)
        shoe(ft, front)

    arm(shB, J('el2'), J('ha2'), False)
    leg(hipB, J('kn2'), J('ft2'), False)
    leg(hipF, J('kn'), J('ft'), True)
    # ---- coat drawn over the legs, so the thighs sit inside it ----
    lean = (sx - x); hem = hipy + (0.2 * h if dress else 0.15 * h); flare_ = 0.13 * h if dress else 0.1 * h
    tor = [(sx - sw, sy + 0.035 * h), (sx - sw * 0.97, sy + 0.16 * h), (x + lean * 0.3 - 0.078 * h, hipy - 0.05 * h), (x - flare_, hem),
           (x + flare_, hem), (x + lean * 0.3 + 0.078 * h, hipy - 0.05 * h), (sx + sw * 0.97, sy + 0.16 * h), (sx + sw, sy + 0.035 * h),
           (sx + sw * 0.45, sy - 0.01 * h), (sx - sw * 0.45, sy - 0.01 * h)]
    tor = sp(tor, 6, True)
    solid(cv, tor, col, a, th, fill=0.07)
    cx_ = sx + d * 0.012 * h
    cv.path([(sx - d * 0.035 * h, sy - 0.005 * h), (cx_ - d * 0.01 * h, sy + 0.1 * h), (x + d * 0.012 * h, hem - 0.01 * h)], col, a * 0.75, thin)
    cv.path([(sx + d * 0.035 * h, sy - 0.005 * h), (cx_ + d * 0.03 * h, sy + 0.07 * h), (cx_ + d * 0.0 * h, sy + 0.1 * h)], col, a * 0.75, thin)
    for k in range(2): cv.circle((cx_ + d * 0.006 * h, sy + 0.15 * h + k * 0.07 * h), 0.006 * h, col, a * 0.8, thin)
    cv.path([(x + d * 0.03 * h, hipy - 0.02 * h), (x + d * 0.07 * h, hipy - 0.025 * h)], col, a * 0.55, thin, smooth=False)
    cv.path([(x - d * 0.05 * h, hipy + 0.02 * h), (x - d * 0.035 * h, hem - 0.03 * h)], col, a * 0.35, thin)
    cv.path([(sx - sw * 0.6, sy + 0.1 * h), (sx - sw * 0.75, sy + 0.2 * h)], col, a * 0.3, thin)
    arm(shF, J('el'), J('ha'), True)
    # ---- neck + shirt collar ----
    nk = [(hx - 0.022 * h, hy + r * 0.75), (hx + 0.022 * h, hy + r * 0.75), (sx + 0.028 * h, sy + 0.005 * h), (sx - 0.028 * h, sy + 0.005 * h)]
    solid(cv, nk, col, a, th)
    cv.path([(sx - 0.03 * h, sy - 0.004 * h), (sx, sy + 0.03 * h), (sx + 0.03 * h, sy - 0.004 * h)], col, a * 0.85, thin, smooth=False)
    # ---- head ----
    tilt = p.get('tilt', 0) * d
    def rot(px, py): return (hx + px * math.cos(tilt) - py * math.sin(tilt), hy + px * math.sin(tilt) + py * math.cos(tilt))
    head = []
    for q in np.linspace(0, 2 * math.pi, 56):
        ex, ey = r * 0.9 * math.cos(q), r * 1.12 * math.sin(q)
        if ey > 0: ex *= 1 - 0.28 * (ey / (r * 1.12)) ** 2
        if d * ex > r * 0.6 and -0.3 * r < ey < 0.15 * r: ex += d * r * 0.12 * math.cos((ey + 0.07 * r) / (0.22 * r) * math.pi / 2) ** 2
        head.append(rot(ex, ey))
    solid(cv, head, col, a, th, fill=0.04)
    ear = [rot(-d * r * 0.15, -r * 0.05), rot(-d * r * 0.3, -r * 0.12), rot(-d * r * 0.32, r * 0.15), rot(-d * r * 0.16, r * 0.2)]
    cv.path(ear, col, a * 0.7, thin)
    ex_, ey_ = d * r * 0.5, -r * 0.05
    eye = [rot(ex_ - d * r * 0.13, ey_), rot(ex_, ey_ - r * 0.07), rot(ex_ + d * r * 0.12, ey_ + r * 0.01), rot(ex_, ey_ + r * 0.04)]
    cv.path(eye, col, a, thin * 1.2, closed=True)
    cv.circle(rot(ex_ + d * r * 0.02, ey_ - r * 0.01), r * 0.035, col, a, fill=True)
    cv.path([rot(ex_ - d * r * 0.16, ey_ - r * 0.17), rot(ex_ + d * r * 0.02, ey_ - r * 0.22), rot(ex_ + d * r * 0.16, ey_ - r * 0.17)], col, a * 0.85, thin)
    cv.path([rot(d * r * 0.52, r * 0.52), rot(d * r * 0.68, r * 0.5)], col, a * 0.8, thin, smooth=False)
    if hair == 'long':
        hp = [(d * r * 0.85, -r * 0.45), (d * r * 0.35, -r * 1.2), (-d * r * 0.6, -r * 1.12), (-d * r * 1.12, -r * 0.2), (-d * r * 1.15, r * 1.6),
              (-d * r * 0.9, r * 3.0), (-d * r * 0.45, r * 3.1), (-d * r * 0.35, r * 1.0), (-d * r * 0.2, -r * 0.1), (d * r * 0.4, -r * 0.55)]
        strands = [[(d * r * 0.2, -r * 1.1), (-d * r * 0.6, -r * 0.4), (-d * r * 0.75, r * 1.5), (-d * r * 0.6, r * 2.9)],
                   [(-d * r * 0.2, -r * 1.15), (-d * r * 0.95, -r * 0.1), (-d * r * 1.0, r * 2.0)]]
    else:
        hp = [(d * r * 0.95, -r * 0.3), (d * r * 0.75, -r * 1.05), (d * r * 0.1, -r * 1.3), (-d * r * 0.75, -r * 1.05), (-d * r * 1.05, -r * 0.3),
              (-d * r * 0.95, r * 0.4), (-d * r * 0.6, r * 0.05), (-d * r * 0.25, -r * 0.4), (d * r * 0.35, -r * 0.55)]
        strands = [[(d * r * 0.7, -r * 1.0), (d * r * 0.2, -r * 0.75), (-d * r * 0.3, -r * 0.6)], [(d * r * 0.2, -r * 1.25), (-d * r * 0.4, -r * 0.95), (-d * r * 0.85, -r * 0.4)],
                   [(-d * r * 0.3, -r * 1.2), (-d * r * 0.9, -r * 0.8)]]
    hp = sp([rot(*q) for q in hp], 6, True)
    cv.poly(hp, col * 0.16, a); cv.path(hp + [hp[0]], col, a, th, smooth=False)
    for s_ in strands: cv.path([rot(*q) for q in s_], col, a * 0.55, thin)
    if rim is not None:
        lx, ly = rim
        for poly in (head, tor):
            seg = [q for q in poly if (q[0] - x) * lx + (q[1] - hipy) * ly > 0]
            if len(seg) > 2: cv.path(seg, col, 0.5 * a, th * 4, smooth=False, layer=cv.F)
    if heart is not None and P is not None:
        c = (sx + d * 0.014 * h, sy + 0.115 * h); s_ = 0.028 * h * heart
        hpp = [(c[0] + s_ * u, c[1] + s_ * v) for u, v in heart_pts(0, 0, 1.0, 40)]
        cv.poly(hpp, P.WARM, 0.95 * a); cv.glow(c, s_ * 2.6, P.GOLD, 0.55 * a)
        glint(cv, (c[0] + s_ * 0.6, c[1] - s_ * 0.7), s_ * 1.6, P.WARM, 0.8 * a)
    return dict(head=(hx, hy), hand=J('ha'), hand2=J('ha2'), chest=(sx, sy + 0.115 * h), r=r, eye=rot(ex_, ey_))


# ================================================================ light effects
def starfield(cv, P, n=160, ymax=700, seed=5, a=1.0, glints=6, x0=0, x1=W):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        q = (rr.uniform(x0, x1), rr.uniform(0, ymax)); s = rr.uniform(0.6, 1.8)
        cv.circle(q, s, P.WARM if rr.random() < 0.25 else P.SOFT, a * rr.uniform(0.25, 0.9), fill=True)
    for _ in range(glints): glint(cv, (rr.uniform(x0 + 60, x1 - 60), rr.uniform(40, ymax * 0.8)), rr.uniform(10, 22), P.WARM, a * 0.9, rr.uniform(0, 0.4))


def milkyway(cv, P, p0, p1, width=160, seed=6, a=1.0):
    rr = np.random.default_rng(seed); p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; L = np.linalg.norm(v); v /= L; n = np.array([-v[1], v[0]])
    for k in range(14):
        c = p0 + v * L * (k + 0.5) / 14 + n * rr.normal(0, width * 0.15)
        cv.glow(tuple(c), width * rr.uniform(0.6, 1.1), P.SOFT * 0.55 if k % 3 else P.GOLD * 0.5, 0.16 * a)
    for _ in range(700):
        c = p0 + v * rr.uniform(0, L) + n * rr.normal(0, width * 0.32)
        cv.circle(tuple(c), rr.uniform(0.5, 1.4), P.SOFT, a * rr.uniform(0.2, 0.8), fill=True)


def meteor(cv, p, ang, L, col, a=1.0):
    dx, dy = math.cos(ang), math.sin(ang)
    for k in range(12):
        u0, u1 = k / 12, (k + 1) / 12
        cv.path([(p[0] - dx * L * u0, p[1] - dy * L * u0), (p[0] - dx * L * u1, p[1] - dy * L * u1)], col, a * (1 - u0) ** 1.5, 2.2 * (1 - u0) + 0.6, smooth=False)
    cv.glow(p, 18, col, a); glint(cv, p, 14, col, a)


def godrays(cv, src, angles, length, col, a=0.18, width=0.05):
    for q in angles:
        w = width * (0.6 + 0.8 * ((q * 7.3) % 1))
        pts = [src, (src[0] + length * math.cos(q - w), src[1] + length * math.sin(q - w)), (src[0] + length * math.cos(q + w), src[1] + length * math.sin(q + w))]
        cv.poly(pts, col * a, 1.0, layer=cv.F)


def flare(cv, src, col, a=1.0, length=900, toward=(960, 540)):
    cv.path([(src[0] - length, src[1]), (src[0] + length, src[1])], col, 0.25 * a, 2, smooth=False, layer=cv.F)
    cv.path([(src[0] - length * 0.4, src[1]), (src[0] + length * 0.4, src[1])], col, 0.6 * a, 1, smooth=False)
    v = np.array(toward, float) - np.array(src, float)
    for k, (u, r_) in enumerate(((0.55, 30), (0.8, 14), (1.25, 46), (1.6, 22))):
        c = np.array(src) + v * u
        hexa = [(c[0] + r_ * math.cos(q), c[1] + r_ * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 7)]
        cv.poly(hexa, col * 0.08, a, layer=cv.F); cv.path(hexa, col, 0.18 * a, 1, smooth=False)
    glint(cv, src, 60, col, a)


def dust(cv, region, n, col, a=0.7, seed=3):
    rr = np.random.default_rng(seed); x0, y0, x1, y1 = region
    for _ in range(n):
        q = (rr.uniform(x0, x1), rr.uniform(y0, y1)); cv.circle(q, rr.uniform(0.8, 2.2), col, a * rr.uniform(0.2, 1), fill=True)


class Shot:
    """canvas + blurred foreground (bokeh) layer + camera roll"""
    def __init__(self):
        self.cv = Canvas(Cam(1.0)); self.fg = np.zeros((H, W, 3), np.float32); self.roll = 0.0

    def bokeh(self, c, r, col, a=0.5):
        cv2.circle(self.fg, (int(c[0]), int(c[1])), int(r), tuple(float(v) * a * 0.55 for v in col), -1, cv2.LINE_AA)
        cv2.circle(self.fg, (int(c[0]), int(c[1])), int(r), tuple(float(v) * a for v in col), 2, cv2.LINE_AA)

    def bokeh_field(self, n, region, rmin, rmax, cols, a=0.5, seed=1):
        rr = np.random.default_rng(seed); x0, y0, x1, y1 = region
        for _ in range(n): self.bokeh((rr.uniform(x0, x1), rr.uniform(y0, y1)), rr.uniform(rmin, rmax), cols[rr.integers(len(cols))], a * rr.uniform(0.4, 1))


# ================================================================ set pieces
def skyline(cv, y, P, a=0.5, seed=2, x0=0, x1=W, hmin=120, hmax=380, lit=0.2):
    rr = np.random.default_rng(seed); x = x0
    while x < x1:
        w = rr.uniform(70, 170); h = rr.uniform(hmin, hmax)
        cv.poly([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], BLACK, 1.0)
        cv.path([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], P.DIM * 1.7, a, 1.3, smooth=False)
        if rr.random() < 0.3:
            cv.path([(x + w * 0.5, y - h), (x + w * 0.5, y - h - 40)], P.DIM * 1.7, a, 1, smooth=False); cv.circle((x + w * 0.5, y - h - 42), 2.5, P.WARM, a, fill=True)
        for wy in np.arange(y - h + 22, y - 14, 24):
            for wx in np.arange(x + 12, x + w - 12, 20):
                if rr.random() < lit: cv.poly([(wx, wy), (wx + 8, wy), (wx + 8, wy + 11), (wx, wy + 11)], P.WARM, a * rr.uniform(0.4, 1))
        x += w + rr.uniform(4, 20)


def lamp(cv, x, y, h, P, a=1.0, d=1, cone=True):
    pole = sp([(x, y), (x, y - h), (x + d * 24, y - h - 22), (x + d * 58, y - h - 14)], 8)
    cv.path(pole, P.LINE, a, 2.2, smooth=False); cv.path([(x - 10, y), (x + 10, y)], P.LINE, a, 2.2, smooth=False)
    lx, ly = x + d * 62, y - h - 6
    cv.path([(lx - 16, ly - 8), (lx + 16, ly - 8), (lx + 9, ly + 6), (lx - 9, ly + 6), (lx - 16, ly - 8)], P.GOLD, a, 1.8, smooth=False)
    if cone: cv.poly([(lx - 9, ly + 6), (lx + 9, ly + 6), (lx + 170, y), (lx - 170, y)], P.GOLD * 0.11, a, layer=cv.F)
    cv.glow((lx, ly + 4), 46, P.WARM, a); glint(cv, (lx, ly + 6), 26, P.WARM, a)
    cv.path(sp([(lx - 170, y + 4), (lx, y + 14), (lx + 170, y + 4)], 6), P.GOLD, 0.4 * a, 2)
    return (lx, ly)


def rain(cv, P, a=0.5, n=300, slant=0.18, seed=4, y0=0, y1=H, light=None, mask=None):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        x = rr.uniform(-100, W + 100); y = rr.uniform(y0, y1); L = rr.uniform(16, 38)
        if mask and mask(x, y): continue
        k = 1.0
        if light is not None:
            dd = math.hypot(x - light[0], y - light[1]); k = 1 + 2.5 * math.exp(-(dd / 260) ** 2)
        cv.path([(x, y), (x - slant * L, y + L)], P.WARM if k > 1.8 else P.LINE, min(1, a * rr.uniform(0.3, 1) * k), 1.0, smooth=False)


def ripples(cv, P, region, n=10, seed=9, a=0.5):
    rr = np.random.default_rng(seed); x0, y0, x1, y1 = region
    for _ in range(n):
        c = (rr.uniform(x0, x1), rr.uniform(y0, y1)); r_ = rr.uniform(8, 30)
        for k in range(2):
            cv.path([(c[0] + r_ * (1 + 0.6 * k) * math.cos(q), c[1] + r_ * 0.25 * (1 + 0.6 * k) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 24)], P.LINE, a * (1 - 0.5 * k), 1, smooth=False)


def window(cv, x, y, w, h, P, a=1.0, moon=True, curtain=True):
    cv.path([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], P.LINE, a, 2.4, smooth=False)
    cv.path([(x - 14, y + h + 8), (x + w + 14, y + h + 8)], P.LINE, a, 2, smooth=False)
    cv.path([(x + w / 2, y), (x + w / 2, y + h)], P.LINE, 0.7 * a, 1.4, smooth=False)
    cv.path([(x, y + h / 2), (x + w, y + h / 2)], P.LINE, 0.7 * a, 1.4, smooth=False)
    if curtain:
        for sd in (-1, 1):
            bx = x if sd < 0 else x + w
            cv.path(sp([(bx + sd * 10, y - 20), (bx - sd * 40, y + h * 0.4), (bx - sd * 20, y + h * 0.8), (bx - sd * 50, y + h + 30)], 8), P.SOFT, 0.7 * a, 1.6)
            cv.path(sp([(bx + sd * 30, y - 20), (bx - sd * 10, y + h * 0.5), (bx - sd * 25, y + h + 30)], 8), P.SOFT, 0.4 * a, 1.2)
    if moon:
        c = (x + w * 0.72, y + h * 0.28); r = min(w, h) * 0.11
        cv.circle(c, r, P.WARM, a, fill=True); cv.circle((c[0] + r * 0.45, c[1] - r * 0.2), r * 0.95, (0, 0, 0), 1.0, fill=True)
        cv.glow(c, r * 3, P.SOFT, 0.5 * a)


def phone_big(cv, tx, cx, cy, w, h, P, msgs, a=1.0):
    x0, y0 = cx - w / 2, cy - h / 2; r = 50
    pts = []
    for (qx, qy, q0) in ((x0 + w - r, y0 + r, -math.pi / 2), (x0 + w - r, y0 + h - r, 0), (x0 + r, y0 + h - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        pts += [(qx + r * math.cos(q), qy + r * math.sin(q)) for q in np.linspace(q0, q0 + math.pi / 2, 8)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.SOFT * 0.06, a)
    cv.path(pts + [pts[0]], P.SOFT, a, 2.8, smooth=False)
    inner = [(x0 + 18 + (q[0] - x0) * (w - 36) / w, y0 + 18 + (q[1] - y0) * (h - 36) / h) for q in pts]
    cv.path(inner + [inner[0]], P.SOFT, 0.35 * a, 1.2, smooth=False)
    cv.path([(cx - 50, y0 + 36), (cx + 50, y0 + 36)], P.LINE, 0.8 * a, 4, smooth=False)
    tx.chars('03:12', cx, y0 + 90, F(SANS_M, 30), (200, 200, 195), 1, 0, 99, stagger=0)
    cv.path([(x0 + 40, y0 + 120), (x0 + w - 40, y0 + 120)], P.LINE, 0.3 * a, 1, smooth=False)
    for (txt, side, yy, style) in msgs:
        fs = 38; tw = len(txt) * fs + 56; bx = x0 + w - 40 - tw if side > 0 else x0 + 40
        col = P.GOLD if side > 0 else P.LINE
        al = 0.35 if style == 'deleted' else 1.0
        bp = []
        for (qx, qy, q0) in ((bx + tw - 26, yy - 8, -math.pi / 2), (bx + tw - 26, yy + 8, 0), (bx + 26, yy + 8, math.pi / 2), (bx + 26, yy - 8, math.pi)):
            bp += [(qx + 26 * math.cos(q), qy + 26 * math.sin(q)) for q in np.linspace(q0, q0 + math.pi / 2, 6)]
        cv.path(bp + [bp[0]], col, a * al, 2, smooth=False)
        if style == 'deleted': cv.path([(bx + 18, yy), (bx + tw - 18, yy)], P.WARM, 0.85 * a, 2, smooth=False)
        tx.chars(txt, bx + tw / 2, yy + 13, F(SERIF_B, fs), (240, 240, 235) if style != 'deleted' else (140, 130, 120), 1, 0, 99, stagger=0)
        if style == 'typing':
            cv.path([(bx + tw - 20, yy - 20), (bx + tw - 20, yy + 20)], P.WARM, a, 2.6, smooth=False); glint(cv, (bx + tw + 6, yy - 30), 14, P.WARM, a)
    for k in range(3):
        cv.path([(x0 + 40, y0 + h - 220 + k * 56), (x0 + w - 40, y0 + h - 220 + k * 56)], P.LINE, 0.18 * a, 1, smooth=False)


def caption(tx, lines, x, y, P, size=64, gold=()):
    for k, l in enumerate(lines):
        g = gold[k] if k < len(gold) else ()
        tx.chars(l, x, y + k * int(size * 1.38), F(SERIF_B, size), P.WHITE, 1, 0, 99, gold=g, stagger=0)


def label(tx, idx, tm, title, shot, P):
    tx.chars(f'{idx:02d}', 70, 74, F(SANS_M, 30), P.TAG, 1, 0, 99, stagger=0, anchor='l')
    tx.chars(f'{tm}  ·  {title}', 120, 74, F(SANS_M, 26), (190, 190, 185), 1, 0, 99, stagger=0, anchor='l')
    tx.chars(f'镜头：{shot}', 120, 112, F(SANS_M, 22), (140, 140, 135), 1, 0, 99, stagger=0, anchor='l')


# ================================================================ the 16 shots
def scenes():
    PF, PV, PA = Palette('fire'), Palette('violet'), Palette('azure')
    S = []

    def s01(sh, tx):
        P = PF; cv = sh.cv; c = (960, 610)
        cv.circle(c, 6, P.WARM, 1, fill=True); cv.glow(c, 60, P.GOLD, 1.0); glint(cv, c, 70, P.WARM, 1.0, 0.2)
        for r_, al in ((110, 0.5), (230, 0.22), (380, 0.1)): cv.circle(c, r_, P.GOLD, al, 1.2)
        dust(cv, (700, 400, 1220, 820), 60, P.WARM, 0.6)
        sh.bokeh_field(9, (0, 0, W, H), 30, 90, [P.GOLD * 0.5, P.SOFT * 0.4], 0.35, 2)
        caption(tx, ['他的心里', '住着一团火'], 960, 190, P, 72, [(), (3, 4)])
        return P, '0:00', '开场 · 黑暗里一颗火星', '微距大特写，浅景深，前景虚焦光斑（维伦纽瓦式极简开场）'
    S.append(s01)

    def s02(sh, tx):
        P = PF; cv = sh.cv; c = (960, 640); h = 640
        for k, (scl, col, th) in enumerate(((1.0, P.GOLD, 2.4), (0.78, P.WARM, 1.8), (1.25, P.GOLD, 1.2), (0.55, P.WARM, 1.2))):
            w = h * scl * 0.36; hh = h * scl; base = c[1] + 0.42 * h
            pts = [(c[0] + 0.04 * hh, base - hh), (c[0] + w * 0.55, base - hh * 0.45), (c[0] + w * 0.5, base - hh * 0.15), (c[0], base), (c[0] - w * 0.5, base - hh * 0.15), (c[0] - w * 0.55, base - hh * 0.45)]
            cv.path(sp(pts, 10, True), col, 0.9 - 0.2 * k, th, smooth=False)
        hp = [(c[0] + 115 * u, c[1] + 115 * v) for u, v in heart_pts(0, 0, 1.0, 60)]
        cv.path(hp, P.WARM, 1, 2.8, smooth=False); cv.poly(hp, P.WARM * 0.35, 0.8, layer=cv.F); cv.glow(c, 150, P.GOLD, 0.7)
        hp2 = [(c[0] + 80 * u, c[1] + 80 * v) for u, v in heart_pts(0, 0, 1.0, 50)]; cv.path(hp2, P.WARM, 0.4, 1.2, smooth=False)
        glint(cv, (c[0] + 60, c[1] - 70), 40, P.WARM, 1)
        rr = np.random.default_rng(4)
        for j in range(60):
            v = rr.random(); x = c[0] + rr.normal(0, 150) * (0.4 + v); y = c[1] - 120 - 520 * v
            cv.path([(x, y), (x + rr.normal(0, 4), y - 10 - 20 * rr.random())], P.WARM, (1 - v) * 0.9, 1.6, smooth=False)
        sh.bokeh_field(12, (0, 0, W, H), 40, 120, [P.GOLD * 0.6, P.WARM * 0.4], 0.35, 3)
        caption(tx, ['可火的最中间', '藏着一颗很软的心'], 960, 150, P, 72, [(), (4, 5)])
        return P, '0:06', '推进火焰 · 火里有一颗心', '缓慢推轨进火焰内部，火星上升，焦点停在心上'
    S.append(s02)

    def s03(sh, tx):
        P = PF; cv = sh.cv
        milkyway(cv, P, (200, 0), (1500, 700), 170, 6, 0.9); starfield(cv, P, 220, 760, 5, 0.9, 8)
        meteor(cv, (1700, 140), math.radians(160), 260, P.WARM, 0.9)
        skyline(cv, 1040, P, 0.45, 3, 0, W, 60, 220, 0.3)
        sh.bokeh_field(26, (0, 900, W, 1080), 10, 26, [P.WARM, P.GOLD], 0.6, 5)
        hill = sp([(-50, 920), (300, 870), (560, 820), (760, 812), (980, 840), (1260, 910), (1500, 960), (1970, 990)], 8)
        cv.poly(hill + [(1970, 1080), (-50, 1080)], BLACK, 1.0); cv.path(hill, P.LINE, 0.9, 2.2, smooth=False)
        f = figure(cv, 640, 814, 380, 'stand', P.SOFT, 1.0, 1, heart=1.5, P=P, rim=(1, -0.3))
        for r_, al in ((150, 0.6), (380, 0.32), (700, 0.16), (1050, 0.08)): cv.circle(f['chest'], r_, P.GOLD, al, 1.4)
        tx.chars('白羊座的内心世界', 1380, 500, F(SERIF_BL, 104), P.HI, 1, 0, 99, stagger=0)
        tx.chars('外表有多倔强  内心就有多柔软', 1380, 600, F(SERIF_B, 46), P.WHITE, 1, 0, 99, gold=(4, 5, 12, 13), stagger=0)
        return P, '0:13', 'drop · 城市上空，标题落下', '低机位仰拍，背后银河斜贯，流星划过，城市灯火做前景虚焦（新海诚式天空）'
    S.append(s03)

    def s04(sh, tx):
        P = PF; cv = sh.cv; gy = 900
        starfield(cv, P, 70, 600, 7, 0.5, 3)
        cv.path([(-50, gy), (1970, gy)], P.LINE, 0.8, 1.6, smooth=False)
        for k in range(1, 5): cv.path([(-50, gy + k * 34), (1970, gy + k * 34)], P.LINE, 0.25 / k, 1, smooth=False)
        cv.path([(420, gy), (420, gy + 140)], P.WARM, 0.7, 3, smooth=False)
        for k, x in enumerate((210, 290, 370)): figure(cv, x, gy, 250, 'stand', P.DIM * 2.4, 0.75, 1, hair='long' if k == 1 else 'short')
        figure(cv, 1250, 892, 360, 'run', P.SOFT, 1.0, 1, heart=1.4, P=P, rim=(-1, 0))
        for k in range(12):
            y = 620 + k * 22; L = 320 + 90 * math.sin(k * 1.7)
            cv.path([(1150 - L, y), (1110, y - 4)], P.GOLD, 0.85 - 0.06 * k, 1.8 - 0.08 * k, smooth=False)
        rr = np.random.default_rng(2)
        for j in range(40):
            q = (rr.uniform(700, 1150), rr.uniform(600, 900)); cv.circle(q, rr.uniform(1, 2.6), P.WARM, rr.uniform(0.3, 1), fill=True)
        for j in range(8): cv.path([(1180 + 20 * j, gy + 4), (1120 + 20 * j, gy - 30 - 10 * j)], P.LINE, 0.3, 1, smooth=False)
        sh.bokeh_field(6, (0, 700, 600, 1080), 50, 110, [P.DIM * 2], 0.5, 8)
        caption(tx, ['别人还在犹豫', '他已经冲出去了'], 1420, 300, P, 64, [(), (3, 4, 5)])
        return P, '0:20', '燃 · 起跑线，别人还在原地', '侧面跟拍，低机位，速度线 + 扬起的尘土；前景人群虚焦'
    S.append(s04)

    def s05(sh, tx):
        P = PF; cv = sh.cv
        starfield(cv, P, 90, 560, 11, 0.6, 4)
        vp = (1000, 600)
        for xb in (-300, 300, 2220, 1620): cv.path([vp, (xb, 1080)], P.LINE, 0.55, 1.4, smooth=False)
        for k in range(1, 9):
            u = (k / 9) ** 2; y = lerp(vp[1], 1080, u)
            cv.path([(lerp(vp[0], 920, u), y), (lerp(vp[0], 1080, u), y + 30 * u)], P.LINE, 0.4, 2, smooth=False)
        lamp(cv, 1060, 610, 120, P, 0.85, -1)
        figure(cv, 1015, 612, 80, 'walk', P.LINE, 0.75, 1, hair='long', dress=True)
        figure(cv, 430, 1130, 760, 'lookback', P.SOFT, 1.0, -1, heart=0.6, P=P, rim=(1, -0.2))
        sh.bokeh_field(5, (1400, 700, W, 1080), 40, 90, [P.GOLD * 0.7], 0.4, 9)
        caption(tx, ['跑得最快的人', '最怕的是什么？'], 1480, 300, P, 62)
        caption(tx, ['在乎的人转身'], 1480, 520, P, 72, [(0, 1, 2, 3, 4, 5)])
        return P, '0:40', '燃 · 反转：他停下回头', '一点透视（库布里克式对称纵深），他在前景左三分之一回头，远处路灯下有人转身离开'
    S.append(s05)

    def s06(sh, tx):
        P = PF; cv = sh.cv
        sh.bokeh_field(30, (0, 0, W, 600), 12, 46, [P.WARM, P.GOLD * 0.8, PV.LINE * 0.7], 0.5, 12)
        cv.path([(0, 620), (W, 620)], P.LINE, 0.3, 1.2, smooth=False)
        hx, hy = 470, 660
        shl = sp([(-60, 1100), (40, 920), (190, 840), (330, 815), (420, 780), (520, 780), (620, 820), (740, 850), (880, 930), (980, 1100)], 6)
        solid(cv, shl + [(980, 1100), (-60, 1100)], P.SOFT, 0.85, 2.2, fill=0.05)
        cv.path(sp([(330, 815), (380, 900), (360, 1080)], 6), P.SOFT, 0.4, 1.2)
        hd = [(hx + 150 * math.cos(q), hy + 178 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 60)]
        solid(cv, hd, P.SOFT, 0.85, 2.2, fill=0.04)
        hp = sp([(hx - 152, hy + 10), (hx - 142, hy - 120), (hx - 30, hy - 186), (hx + 110, hy - 156), (hx + 152, hy - 40), (hx + 70, hy - 92), (hx - 60, hy - 64), (hx - 124, hy + 40)], 6, True)
        cv.poly(hp, P.SOFT * 0.2, 0.85); cv.path(hp + [hp[0]], P.SOFT, 0.85, 2)
        for k in range(5): cv.path(sp([(hx - 120 + 50 * k, hy - 160 + 10 * k), (hx - 80 + 50 * k, hy - 100), (hx - 100 + 40 * k, hy - 40)], 5), P.SOFT, 0.4, 1.1)
        cv.path(sp([(hx + 150, hy - 30), (hx + 165, hy + 10), (hx + 150, hy + 60)], 5), P.SOFT, 0.7, 1.6)
        rim = [(hx + 150 * math.cos(q), hy + 178 * math.sin(q)) for q in np.linspace(-1.1, 0.6, 20)]
        cv.path(rim, P.WARM, 0.8, 8, smooth=False, layer=cv.F)
        phone_big(cv, tx, 1100, 560, 560, 920, P, [('最近还好吗', -1, 330, 'recv'), ('我其实很想你', 1, 450, 'deleted'), ('没事 就是问问', 1, 560, 'deleted'), ('在吗', 1, 690, 'typing')])
        cv.glow((1100, 560), 420, P.SOFT, 0.1)
        caption(tx, ['一句话', '删了又删'], 1650, 400, P, 64, [(), (0, 1, 2, 3)])
        return P, '1:10', '直 · 过肩看手机：删了又删，只剩「在吗」', '过肩镜头，手机光勾出他耳朵和发梢的轮廓光，背后窗外城市虚成光斑'
    S.append(s06)

    def s07(sh, tx):
        P = PA; cv = sh.cv
        cv.path([(0, 780), (W, 780)], P.LINE, 0.35, 1.2, smooth=False)
        window(cv, 1240, 160, 440, 420, P, 0.9)
        cv.poly([(1240, 580), (1680, 580), (1520, 1080), (980, 1080)], P.SOFT * 0.045, 1.0, layer=cv.F)
        dust(cv, (1100, 300, 1600, 900), 70, P.SOFT, 0.6, 7)
        bed = [(180, 780), (180, 650), (1000, 650), (1000, 780)]
        cv.path(bed, P.LINE, 0.8, 2, smooth=False); cv.path(sp([(180, 650), (260, 620), (420, 640), (600, 625), (1000, 650)], 8), P.SOFT, 0.6, 1.6)
        cv.path(sp([(200, 650), (210, 560), (330, 540), (360, 640)], 6), P.SOFT, 0.6, 1.6)
        c = (560, 230); cv.circle(c, 70, P.LINE, 0.8, 2); cv.circle(c, 62, P.LINE, 0.3, 1)
        for k in range(12):
            q = k * math.pi / 6; cv.path([(c[0] + 54 * math.cos(q), c[1] + 54 * math.sin(q)), (c[0] + 62 * math.cos(q), c[1] + 62 * math.sin(q))], P.LINE, 0.6, 1.2, smooth=False)
        cv.path([c, (c[0] + 34, c[1])], P.WARM, 0.9, 2.6, smooth=False); cv.path([c, (c[0] + 8, c[1] - 50)], P.WARM, 0.9, 2, smooth=False)
        f = figure(cv, 560, 960, 520, 'sitbed', P.SOFT, 0.95, 1, heart=0.6, P=PF, rim=(1, -0.2))
        ph = (f['hand'][0] + 8, f['hand'][1] - 14)
        cv.poly([(ph[0] - 16, ph[1] - 28), (ph[0] + 16, ph[1] - 28), (ph[0] + 16, ph[1] + 28), (ph[0] - 16, ph[1] + 28)], PF.WARM * 0.6, 1)
        cv.glow(ph, 60, PF.WARM, 0.35); glint(cv, ph, 18, PF.WARM, 0.8)
        cv.poly([ph, (f['head'][0] + 50, f['head'][1] - 60), (f['head'][0] + 70, f['head'][1] + 40)], PF.WARM * 0.05, 1, layer=cv.F)
        caption(tx, ['然后盯着屏幕', '等了一整晚'], 1460, 800, P, 60, [(), (3, 4, 5)])
        return P, '1:35', '直 · 凌晨三点，坐在床边等回复', '王家卫式冷蓝室内，月光在地板上切出窗格，空气里的尘；唯一的暖光是手机'
    S.append(s07)

    def s08(sh, tx):
        P = PF; cv = sh.cv; cx, cy = 960, 540
        sh.bokeh_field(24, (0, 0, W, H), 30, 120, [P.GOLD * 0.7, P.WARM * 0.5, P.LINE * 0.5], 0.4, 14)
        cup = sp([(cx - 120, cy - 100), (cx - 104, cy + 120), (cx - 66, cy + 150), (cx + 66, cy + 150), (cx + 104, cy + 120), (cx + 120, cy - 100)], 6)
        solid(cv, cup + [(cx + 120, cy - 100)], P.SOFT, 1, 2.6, fill=0.05)
        cv.path([(cx + 120 * math.cos(q), cy - 100 + 22 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 50)], P.SOFT, 1, 2, smooth=False)
        cv.path([(cx + 112 * math.cos(q), cy - 96 + 18 * math.sin(q)) for q in np.linspace(0, math.pi, 30)], P.WARM, 0.7, 1.4, smooth=False)
        cv.path(sp([(cx + 118, cy - 50), (cx + 180, cy - 40), (cx + 186, cy + 40), (cx + 108, cy + 64)], 6), P.SOFT, 1, 2.4)
        cv.path(sp([(cx - 70, cy - 40), (cx - 76, cy + 80)], 4), P.WARM, 0.5, 6, layer=cv.F)
        for j in range(3):
            x0 = cx - 50 + 50 * j; cv.path([(x0 + 16 * math.sin(v * 6 + j), cy - 130 - v * 260) for v in np.linspace(0, 1, 24)], P.WARM, 0.75, 1.8)
        for d, col in ((-1, P.LINE), (1, P.GOLD)):
            el = (cx + d * 780, cy + 440); wr = (cx + d * 160, cy + 90)
            out, _ = limb_shape([el, (cx + d * 430, cy + 240), wr], 76, 44); solid(cv, out, col, 1, 2.4, fill=0.05)
            cv.path([(cx + d * 240, cy + 50), (cx + d * 212, cy + 160)], col, 0.8, 1.6); cv.path([(cx + d * 262, cy + 70), (cx + d * 236, cy + 170)], col, 0.5, 1.2)
            for k in range(3): cv.path(sp([(cx + d * (520 - 90 * k), cy + 300 - 40 * k), (cx + d * (470 - 90 * k), cy + 250 - 40 * k), (cx + d * (440 - 90 * k), cy + 300 - 40 * k)], 4), col, 0.3, 1)
            hand = sp([(cx + d * 185, cy + 20), (cx + d * 100, cy - 14), (cx + d * 72, cy + 40), (cx + d * 78, cy + 100), (cx + d * 116, cy + 134), (cx + d * 188, cy + 140)], 6, True)
            solid(cv, hand, col, 1, 2.2, fill=0.05)
            for k in range(3): cv.path([(cx + d * 80, cy + 40 + 28 * k), (cx + d * 124, cy + 34 + 28 * k)], col, 0.8, 1.6, smooth=False)
            cv.path(sp([(cx + d * 150, cy + 10), (cx + d * 112, cy - 30), (cx + d * 92, cy - 20)], 4), col, 0.9, 2)
        cv.glow((cx, cy), 300, P.GOLD, 0.3); glint(cv, (cx - 90, cy - 104), 30, P.WARM, 1)
        caption(tx, ['你随手递来的一杯热水'], 960, 950, P, 62, [(7, 8)])
        caption(tx, ['他会记很久很久'], 960, 1040, P, 50)
        return P, '1:50', '软 · 手部特写：递来一杯热水', '静物插入镜头，极浅景深，背景全虚成暖色光斑'
    S.append(s08)

    def s09(sh, tx):
        P = PV; cv = sh.cv; gy = 920
        cv.path([(-50, gy), (1970, gy)], P.LINE, 0.5, 1.4, smooth=False)
        cv.path(sp([(0, 200), (240, 260), (480, 210), (720, 270), (900, 220)], 8), PF.LINE, 0.5, 1.2)
        for k in range(16):
            cv.glow((k * 58, 200 + 50 * math.sin(k * 0.9 + 0.5)), 16, PF.WARM, 0.8); cv.circle((k * 58, 206 + 50 * math.sin(k * 0.9 + 0.5)), 4, PF.WARM, 1, fill=True)
        for k, x in enumerate(np.linspace(70, 860, 7)):
            figure(cv, x, gy, 270 + 30 * math.sin(k), 'walk' if k % 2 else 'stand', PF.GOLD, 0.55, 1 if k % 2 else -1, hair='long' if k % 3 == 0 else 'short', dress=k % 3 == 0)
        rr = np.random.default_rng(3)
        for j in range(60):
            q = (rr.uniform(40, 920), rr.uniform(260, 620)); a_ = rr.uniform(0, 3)
            cv.path([q, (q[0] + 8 * math.cos(a_), q[1] + 8 * math.sin(a_))], [PF.WARM, PF.GOLD, PV.LINE][j % 3], rr.uniform(0.4, 1), 2, smooth=False)
        cv.poly([(980, 200), (1260, 200), (1260, gy), (980, gy)], BLACK, 1.0)
        cv.path([(980, gy), (980, 200), (1260, 200), (1260, gy)], P.LINE, 1, 2.6, smooth=False)
        cv.path([(1000, gy), (1000, 220), (1240, 220), (1240, gy)], P.LINE, 0.4, 1.2, smooth=False)
        cv.circle((1215, 580), 8, P.LINE, 0.9, 2)
        cv.poly([(980, gy - 4), (1260, gy - 4), (1560, gy + 60), (680, gy + 60)], PF.WARM * 0.12, 1, layer=cv.F)
        cv.path([(980, gy - 3), (1260, gy - 3)], PF.WARM, 0.9, 2, smooth=False)
        f = figure(cv, 1430, gy + 0.39 * 430, 430, 'hug', P.SOFT, 1.0, -1, heart=0.45, P=PF)
        e = f['eye']
        for k in range(3):
            tp = (e[0] - 8 - 5 * k, e[1] + 30 + 60 * k)
            cv.poly(sp([(tp[0], tp[1] - 14), (tp[0] + 7, tp[1] + 4), (tp[0], tp[1] + 11), (tp[0] - 7, tp[1] + 4)], 4, True), P.WARM, 0.95 - 0.25 * k); glint(cv, tp, 10, P.WARM, 0.6 - 0.15 * k)
        caption(tx, ['关上门', '一个人哭完'], 1660, 330, P, 64, [(), (3, 4)])
        caption(tx, ['打开门  又是那个没心没肺的他'], 470, 1010, P, 40)
        return P, '2:40', '疼 · 一扇门：门外热闹，门内哭', '韦斯·安德森式对称分割：门框居中，左暖右冷，门缝漏出一线暖光'
    S.append(s09)

    def s10(sh, tx):
        P = PA; cv = sh.cv; gy = 760
        skyline(cv, gy, P, 0.5, 9, 0, W, 180, 460, 0.22)
        for (x, y, txt, col) in ((300, 420, '便利店', PF.WARM), (1780, 560, '24H', PV.LINE)):
            tx.chars(txt, x, y, F(SANS_M, 40), tuple(int(c) for c in (np.array(col[::-1]) * 255)), 1, 0, 99, stagger=0)
            w_ = len(txt) * 22 + 30
            cv.poly([(x - w_, y - 46), (x + w_, y - 46), (x + w_, y + 12), (x - w_, y + 12)], BLACK, 1.0)
            cv.path([(x - w_, y - 46), (x + w_, y - 46), (x + w_, y + 12), (x - w_, y + 12), (x - w_, y - 46)], col, 0.9, 2, smooth=False)
            cv.glow((x, y - 14), 110, col, 0.45)
        cv.path([(0, gy), (W, gy)], P.LINE, 0.6, 1.4, smooth=False)
        lp = lamp(cv, 1460, gy, 330, P, 0.95, -1)
        figure(cv, 760, gy, 360, 'walk', P.SOFT, 1.0, 1, heart=0.45, P=PF, rim=(1, -0.5))
        refl = Shot(); figure(refl.cv, 760, gy, 360, 'walk', P.SOFT, 1.0, 1); lamp(refl.cv, 1460, gy, 330, P, 0.95, -1, cone=False)
        R_ = cv2.flip(refl.cv.L[gy - 400:gy], 0)
        R_ = cv2.GaussianBlur(R_, (0, 0), 2.5)
        for k in range(0, 320, 6): R_[k:k + 3] *= 0.5
        cv.L[gy:gy + 320] += R_[:320] * 0.35
        ripples(cv, P, (300, gy + 40, 1700, 1060), 18, 9, 0.5)
        rain(cv, P, 0.55, 420, 0.16, 4, 0, H, light=lp)
        sh.bokeh_field(10, (0, 0, W, 300), 20, 60, [PF.WARM, PV.LINE, P.SOFT], 0.4, 10)
        caption(tx, ['他会笑着说', '“算了”'], 1500, 250, P, 64, [(), (1, 2)])
        return P, '3:05', '疼 · 雨夜街头，一个人走', '王家卫 / 银翼杀手式雨夜：霓虹招牌、被路灯打亮的雨丝、积水倒影'
    S.append(s10)

    def s11(sh, tx):
        P = PF; cv = sh.cv
        sh.roll = -7.0
        figure(cv, 640, 1160, 860, 'argue', P.SOFT, 1.0, 1, heart=1.2, P=P, rim=(1, 0))
        figure(cv, 1300, 1160, 820, 'turned', PV.SOFT, 0.95, -1, hair='long', dress=True, rim=(-1, 0))
        zz = [(930, 120), (1010, 260), (950, 330), (1060, 470), (1000, 540), (1120, 700)]
        cv.path(zz, P.WARM, 1, 3.2, smooth=False); cv.path(zz, P.GOLD, 0.5, 18, smooth=False, layer=cv.F)
        cv.path([(1010, 260), (1080, 300), (1110, 280)], P.WARM, 0.7, 1.6, smooth=False); cv.path([(1060, 470), (1130, 450)], P.WARM, 0.6, 1.4, smooth=False)
        rr = np.random.default_rng(6)
        for j in range(26):
            p = (1000 + rr.normal(0, 110), rr.uniform(150, 760)); q = rr.uniform(0, 6.3); L = rr.uniform(14, 40)
            cv.path([p, (p[0] + L * math.cos(q), p[1] + L * math.sin(q))], P.GOLD, 0.85, 2, smooth=False)
        for j in range(5): glint(cv, (1000 + rr.normal(0, 140), rr.uniform(150, 700)), rr.uniform(12, 24), P.WARM, 0.9)
        caption(tx, ['吵架时', '专挑最狠的话'], 960, 900, P, 60, [(), (2, 3, 4)])
        return P, '3:35', '冲 · 争吵：两个侧脸之间的闪电', '荷兰角倾斜构图，近景双人对峙，各自被闪电从内侧打出轮廓光'
    S.append(s11)

    def s12(sh, tx):
        P = PF; cv = sh.cv
        window(cv, 1180, 120, 540, 480, P, 0.9, moon=False)
        sc = (1450, 580)
        cv.path([(sc[0] + 170 * math.cos(q), sc[1] + 170 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 40)], P.WARM, 1, 2.4)
        godrays(cv, (1450, 420), np.linspace(math.radians(140), math.radians(205), 7), 1500, P.GOLD, 0.16, 0.035)
        dust(cv, (300, 300, 1400, 900), 120, P.WARM, 0.8, 12)
        cv.path([(180, 760), (1120, 760)], P.LINE, 1, 2.6, smooth=False)
        cv.path([(170, 776), (1130, 776)], P.LINE, 0.5, 1.4, smooth=False)
        for xl in (250, 1050): cv.path([(xl, 776), (xl - 10, 1060)], P.LINE, 0.8, 2.2, smooth=False)
        bag = [(500, 760), (480, 540), (720, 540), (700, 760)]; solid(cv, bag, P.SOFT, 1, 2.4, fill=0.05)
        cv.path([(480, 540), (520, 520), (680, 520), (720, 540)], P.SOFT, 0.7, 1.6, smooth=False)
        cv.path(sp([(560, 520), (575, 460), (625, 460), (640, 520)], 6), P.SOFT, 1, 2)
        cv.path([(500, 610), (700, 610)], P.SOFT, 0.35, 1.2, smooth=False)
        cup = [(790, 760), (800, 610), (890, 610), (900, 760)]; solid(cv, cup, P.SOFT, 1, 2.2, fill=0.05)
        cv.path([(790, 610), (900, 610)], P.SOFT, 1, 3, smooth=False); cv.path([(845, 610), (850, 560)], P.SOFT, 0.8, 2, smooth=False)
        for j in range(2): cv.path([(830 + 30 * j + 10 * math.sin(v * 5 + j), 550 - v * 160) for v in np.linspace(0, 1, 18)], P.WARM, 0.6, 1.6)
        note = [(330, 700), (450, 685), (462, 752), (342, 762)]; solid(cv, note, P.GOLD, 1, 2, fill=0.08)
        hp = [(400 + 16 * u, 722 + 16 * v) for u, v in heart_pts(0, 0, 1.0, 30)]; cv.poly(hp, P.WARM, 1); glint(cv, (420, 706), 12, P.WARM, 1)
        caption(tx, ['第二天', '默默给你带了早餐'], 700, 250, P, 64, [(), (6, 7)])
        caption(tx, ['这就是他的「对不起」'], 640, 920, P, 50, [(6, 7, 8)])
        return P, '4:00', '冲 · 第二天早上：桌上的早餐和小纸条', '静物空镜，晨光从窗口斜射成光柱，光里有浮尘；没有人，只有他留下的东西'
    S.append(s12)

    def s13(sh, tx):
        P = PF; cv = sh.cv; gy = 940
        lp = lamp(cv, 1650, gy, 520, PA, 0.8, -1)
        cv.path([(-50, gy), (1970, gy)], P.LINE, 0.5, 1.4, smooth=False)
        cx_ = 1150; topy = 330
        f1 = figure(cv, 880, gy, 470, 'umbrella', P.SOFT, 1.0, 1, heart=1.3, P=P, rim=(1, -0.6))
        figure(cv, 1150, gy, 430, 'stand', PV.SOFT, 0.95, -1, hair='long', dress=True)
        dome = [(cx_ + 230 * math.cos(q), topy + 140 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 48)]
        cv.poly(dome + [(cx_ + 230, topy), (cx_ - 230, topy)], BLACK, 1.0)
        cv.path(dome, P.GOLD, 1, 2.6, smooth=False)
        cv.path(sp([(cx_ - 230, topy), (cx_ - 115, topy + 16), (cx_, topy), (cx_ + 115, topy + 16), (cx_ + 230, topy)], 6), P.GOLD, 0.9, 2)
        for q in np.linspace(math.pi * 1.15, math.pi * 1.85, 4): cv.path([(cx_, topy - 140), (cx_ + 230 * math.cos(q), topy + 4)], P.GOLD, 0.35, 1.2, smooth=False)
        cv.path([(cx_, topy - 140), (cx_, topy - 170)], P.GOLD, 1, 2, smooth=False)
        cv.path([(cx_ - 60, topy - 60), f1['hand']], P.GOLD, 1, 2.2, smooth=False)
        inside = lambda x, y: (cx_ - 225 < x < cx_ + 225 and y > topy - 130 and y < gy)
        rain(cv, PA, 0.6, 520, 0.08, 8, 0, gy, light=lp, mask=inside)
        rr = np.random.default_rng(3)
        for k in range(14):
            p = (f1['head'][0] - 70 + rr.uniform(-25, 10), f1['head'][1] - 40 + k * 32)
            cv.path([p, (p[0] - 2, p[1] + 18)], PA.WARM, 0.9, 1.2, smooth=False)
            if k % 3 == 0: glint(cv, p, 8, PA.WARM, 0.8)
        for k in range(9): glint(cv, (cx_ - 220 + 55 * k, topy + 4), 6, PA.WARM, 0.7)
        ripples(cv, PA, (200, gy + 20, 1800, 1060), 16, 5, 0.5)
        caption(tx, ['下雨了', '伞已经在你头顶'], 520, 260, P, 64, [(), (4, 5)])
        return P, '4:25', '爱 · 伞全偏向她，他半边在雨里', '低机位仰拍，路灯逆光把雨丝打亮，伞沿滴水，他外侧肩膀落满雨点'
    S.append(s13)

    def s14(sh, tx):
        P = PA; cv = sh.cv
        milkyway(cv, P, (0, 300), (1920, 80), 140, 2, 0.7); starfield(cv, P, 160, 640, 13, 0.8, 6)
        meteor(cv, (520, 120), math.radians(200), 220, P.WARM, 0.7)
        hz = 700; cv.path([(-50, hz), (1970, hz)], P.LINE, 0.5, 1.2, smooth=False)
        vp = (1500, hz)
        cv.path([vp, (700, 1080)], P.LINE, 0.7, 1.6, smooth=False); cv.path([vp, (1260, 1080)], P.LINE, 0.7, 1.6, smooth=False)
        for k in range(1, 7):
            u = (k / 7) ** 2; y = lerp(hz, 1080, u); cv.path([(lerp(vp[0], 975, u), y), (lerp(vp[0], 985, u), y + 24 * u)], P.LINE, 0.5, 2, smooth=False)
        for u in (0.12, 0.35, 0.7):
            x = lerp(vp[0], 1260, u) + lerp(20, 120, u); y = lerp(hz, 1080, u); lamp(cv, x, y, lerp(70, 380, u), P, 0.8, -1)
        for k, x in enumerate(np.linspace(140, 620, 7)): figure(cv, x, hz + 30, 110, 'walk', PF.GOLD, 0.5, -1, hair='long' if k % 2 else 'short')
        dust(cv, (100, 600, 700, 700), 30, PF.WARM, 0.5, 4)
        figure(cv, 1300, 860, 150, 'walk', P.SOFT, 1.0, 1, heart=1.2, P=PF)
        caption(tx, ['可散场的路上', '他会突然安静'], 640, 360, P, 64, [(), (4, 5)])
        return P, '5:10', '独 · 远景：人群往左散，他一个人往右走', '极远景高机位（北野武 / 是枝裕和式留白）：大片星空压着一个很小的人'
    S.append(s14)

    def s15(sh, tx):
        P = PF; cv = sh.cv
        milkyway(cv, P, (600, 0), (1700, 900), 200, 8, 0.9); starfield(cv, P, 240, 800, 21, 0.9, 10)
        meteor(cv, (1640, 200), math.radians(150), 320, P.WARM, 0.9)
        ridge = [(-50, 1080), (250, 900), (480, 930), (760, 640), (980, 560), (1130, 330), (1240, 250), (1380, 380), (1600, 500), (1800, 580), (1980, 640), (1980, 1080)]
        cv.poly(ridge, BLACK, 1.0); cv.path(ridge[:-1], P.LINE, 1, 2.4, smooth=False)
        cv.path([(980, 560), (1050, 600), (1100, 520)], P.LINE, 0.4, 1.2, smooth=False); cv.path([(760, 640), (820, 700), (880, 650)], P.LINE, 0.4, 1.2, smooth=False)
        cv.path([(1240, 250), (1240, 130)], P.GOLD, 1, 2.4, smooth=False)
        cv.path(sp([(1240, 132), (1290, 140), (1320, 128), (1316, 160), (1280, 170), (1240, 166)], 6), P.WARM, 1, 2)
        cv.glow((1270, 150), 80, P.GOLD, 0.6); glint(cv, (1240, 128), 30, P.WARM, 1)
        figure(cv, 905, 600, 230, 'climb', P.SOFT, 1.0, 1, heart=1.4, P=P, rim=(0.4, -1))
        for k in range(14): cv.circle((lerp(260, 890, k / 14), lerp(900, 610, k / 14) + 8 * math.sin(k)), 2.2, P.WARM, 0.2 + 0.05 * k, fill=True)
        caption(tx, ['热情会退', '可火小了', '他还在往上走'], 480, 260, P, 60, [(), (), (4, 5, 6)])
        return P, '6:10', '赢 · 夜里爬山，火小了还在往上', '大仰角，人物是星空下的剪影；身后留下一串小火光的脚印'
    S.append(s15)

    def s16(sh, tx):
        P = PF; cv = sh.cv; c = (1430, 730)
        godrays(cv, c, np.linspace(math.radians(190), math.radians(350), 14), 1500, P.GOLD, 0.12, 0.03)
        cv.path([(c[0] + 260 * math.cos(q), c[1] + 260 * math.sin(q)) for q in np.linspace(math.pi, 2 * math.pi, 60)], P.WARM, 1, 2.6, smooth=False)
        cv.glow(c, 560, P.GOLD, 0.35)
        for k in range(5):
            bx, by = 420 + 110 * k, 260 + 30 * math.sin(k * 1.7)
            cv.path(sp([(bx - 18, by - 6), (bx - 6, by), (bx, by + 4), (bx + 6, by), (bx + 18, by - 6)], 4), P.SOFT, 0.8, 1.6)
        ridge = sp([(-50, 760), (500, 720), (800, 694), (1100, 694), (1400, 722), (1970, 772)], 8)
        cv.poly(ridge + [(1970, 1080), (-50, 1080)], BLACK, 1.0); cv.path(ridge, P.LINE, 1, 2.2, smooth=False)
        for k in range(30):
            gx = lerp(-50, 1970, k / 30); gy_ = np.interp(gx, [q[0] for q in ridge], [q[1] for q in ridge])
            cv.path([(gx + 6, gy_ - 2), (gx, gy_ - 18)], P.LINE, 0.35, 1, smooth=False)
        figure(cv, 700, 700 + 0.12 * 340, 340, 'sit', P.SOFT, 1.0, 1, heart=1.4, P=P, rim=(1, 0))
        figure(cv, 905, 692 + 0.12 * 320, 320, 'sit', PV.SOFT, 0.95, 1, heart=1.0, P=P, hair='long', rim=(1, 0))
        flare(cv, (1430, 560), P.WARM, 0.8, 1100, (600, 700))
        caption(tx, ['如果你身边有白羊', '别只看见他的火', '也看看火中间的那颗心'], 760, 240, P, 60, [(), (6,), (9,)])
        return P, '7:50', '真 · 天亮，山顶并肩，两颗心都亮着', '马利克式魔幻时刻逆光：太阳光芒、镜头光晕、飞鸟，两人剪影并肩'
    S.append(s16)
    return S


def render(scene_fn, idx):
    sh = Shot(); P0 = Palette('fire'); tx = Text(P0)
    P, tm, title, shot = scene_fn(sh, tx)
    img = sh.cv.composite(P.BG * 0.6, 0.0, glow=0.6) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    if sh.roll:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), sh.roll, 1.1); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    img = tx.blend(np.clip(img, 0, 1.5).astype(np.float32))
    lab = Text(P0); label(lab, idx, tm, title, shot, P0); img = lab.blend(img)
    return np.clip(img * 255, 0, 255).astype(np.uint8), tm, title, shot


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--only')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    S = scenes(); idx = range(1, 17) if not a.only else [int(x) for x in a.only.split(',')]
    for i in idx:
        im, tm, title, shot = render(S[i - 1], i)
        cv2.imwrite(os.path.join(a.out, f'{i:02d}.png'), im); print(i, tm, title, '|', shot, flush=True)


if __name__ == '__main__':
    main()
