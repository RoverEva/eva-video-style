"""Solo 'signature' moments for group videos — one per hero, each a beat-by-beat build.

Every function: sig(gs, cv, tx, t, i, b, A, heads, face)
  gs   GroupScene (T(), e8, P, members, cam via cv.cam)
  i    stage slot 0..3 (x = gs.XS[i]);  b = the slot's solo start beat;  A = alpha (fades after the solo)
  heads[i] = (prop head, prop tip) in world coords;  face[i] = face centre
SIG_CAM[name] = (dx, cy, scale): how the camera frames the solo (dx = offset from the hero's x).
"""
import math
import numpy as np
from .core import GY, cl, ramp, eo, eio, lerp, pulse, pop, flame, F, SERIF_B

XS = (480, 800, 1120, 1440)
SIG_CAM = {
    'blueprint': (120, 640, 1.7), 'tree': (120, 560, 1.7), 'formation': (0, 700, 1.45), 'morph': (-160, 520, 1.7),
    'lanterns': (100, 540, 1.6), 'bloom': (120, 540, 1.7), 'lightlink': (0, 700, 1.45), 'fireworks': (-160, 500, 1.6),
    'checklist': (180, 600, 1.6), 'shield': (60, 700, 1.5), 'pillars': (0, 680, 1.45), 'circle': (-60, 720, 1.45),
    'garden': (60, 700, 1.4), 'harvest': (0, 700, 1.4), 'summit': (200, 540, 1.3),
    'planes': (100, 430, 1.4), 'balance': (0, 430, 1.5), 'ripples': (100, 690, 1.4),
    'moonrise': (0, 420, 1.55), 'phoenix': (0, 520, 1.4), 'school': (0, 540, 1.35),
    'ignite': (0, 690, 1.35), 'sunburst': (0, 470, 1.55), 'arrows': (180, 470, 1.4),
    'gears': (160, 600, 1.6), 'brush': (120, 520, 1.7), 'target': (140, 640, 1.5), 'spotlight': (-120, 600, 1.5),
}
# caption anchor (screen x, y) when the default side would cover the effect
SIG_CAP = {'checklist': (420, 260), 'gears': (420, 240), 'target': (420, 240), 'brush': (1500, 880),
           'bloom': (1500, 760), 'fireworks': (1500, 820), 'spotlight': (1560, 300)}
_r = np.random.default_rng(31)
SPARK = [(_r.uniform(0, 2 * math.pi), _r.uniform(0.6, 1.4)) for _ in range(40)]


def _shape(kind, n=40):
    if kind == 'q':
        P = [(0.45 * math.cos(q), -0.35 + 0.45 * math.sin(q)) for q in np.linspace(math.pi * 1.1, math.pi * 2.4, 26)]
        P += [(0.12, 0.1 + 0.3 * s) for s in np.linspace(0, 1, 8)] + [(0.0, 0.62 + 0.06 * math.cos(q)) for q in np.linspace(0, 6.28, 6)]
    elif kind == 'bulb':
        P = [(0.5 * math.cos(q), -0.15 + 0.5 * math.sin(q)) for q in np.linspace(math.pi * 0.75, math.pi * 2.25, 30)]
        P += [(-0.2 + 0.4 * s, 0.45) for s in np.linspace(0, 1, 5)] + [(-0.15 + 0.3 * s, 0.6) for s in np.linspace(0, 1, 5)]
    elif kind == 'arrow':
        P = [(-0.6 + 1.1 * s, 0.0) for s in np.linspace(0, 1, 20)]
        P += [(0.5 - 0.35 * s, -0.35 * s) for s in np.linspace(0, 1, 10)] + [(0.5 - 0.35 * s, 0.35 * s) for s in np.linspace(0, 1, 10)]
    else:
        P = []
        for k in range(10):
            r = 0.6 if k % 2 == 0 else 0.25; q = -math.pi / 2 + k * math.pi / 5
            r2 = 0.25 if k % 2 == 0 else 0.6; q2 = -math.pi / 2 + (k + 1) * math.pi / 5
            for s in np.linspace(0, 1, 4, endpoint=False):
                P.append((lerp(r * math.cos(q), r2 * math.cos(q2), s), lerp(r * math.sin(q), r2 * math.sin(q2), s)))
    P = np.array(P, float); return P[np.linspace(0, len(P) - 1, n).astype(int)]
SHAPES = [_shape(k) for k in ('q', 'bulb', 'arrow', 'star')]


# ------------------------------------------------------------------ NT
def blueprint(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; X0 = gs.XS[i]; LN, G = P.LINE, P.GOLD
    n = cl((t - T(b + 1)) / gs.e8, 0, 12)
    for k in range(7):
        x = X0 - 360 + k * 120; on = ramp(n, k, k + 0.6)
        cv.path([(x, GY + 4), (X0 + (x - X0) * 1.6, 1080)], LN, 0.5 * A * on, 1.2, on, smooth=False)
    for k in range(4):
        y = GY + 4 + k * 42; on = ramp(n, 6 + k, 6.6 + k); w = 360 + k * 90
        cv.path([(X0 - w, y), (X0 + w, y)], LN, 0.5 * A * on, 1.2, on, smooth=False)
    for k, (bx, bw, bh) in enumerate(((X0 - 330, 70, 150), (X0 - 240, 60, 220), (X0 + 180, 80, 190), (X0 + 280, 60, 260), (X0 + 360, 70, 140), (X0 - 400, 50, 110))):
        up = eo(ramp(t, T(b + 2 + k), T(b + 2.6 + k))); hgt = bh * up
        if up > 0:
            cv.path([(bx, GY), (bx, GY - hgt), (bx + bw, GY - hgt), (bx + bw, GY)], LN, 0.7 * A, 1.6, smooth=False)
            for wy in range(int(GY - hgt + 20), GY - 10, 30): cv.path([(bx + 12, wy), (bx + bw - 12, wy)], G, 0.35 * A, 1.0, smooth=False)


def tree(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; G, Wm = P.GOLD, P.WARM
    if T(b) <= t < T(b + 1): cv.glow((face[i][0] - 9, face[i][1] - 2), 14, Wm, 2.0 * pulse(t, T(b), 0.3))   # glasses glint
    A = A * ramp(t, T(b + 3.5), T(b + 4))
    if A <= 0: return
    levels = [[heads[i][0]]]
    for lv in range(4):
        levels.append([(p[0] + s * 110 / (lv + 1) ** 0.7, p[1] - 70) for p in levels[-1] for s in (-1, 1)])
    for lv in range(1, 5):
        on = eo(ramp(t, T(b + 3 + lv), T(b + 3.4 + lv)))
        if on <= 0: continue
        for k, p in enumerate(levels[lv]):
            cv.path([levels[lv - 1][k // 2], p], G, 0.8 * A, 1.4, on, smooth=False)
            if on >= 1: cv.circle(p, 3.5, Wm, A, fill=True)
    if t >= T(b + 7):
        cam = cv.cam
        for k, p in enumerate(levels[4][::3]):
            q = cam([p])[0]; a = eo(ramp(t, T(b + 7) + k * 0.04, T(b + 7.5) + k * 0.04)) * A
            tx.d.text((q[0], q[1] - 12), '?√∞π'[k % 4], font=F(SERIF_B, int(30 * cam.s / 1.7)), fill=tuple(P.HI) + (int(255 * a),), anchor='ms')


def formation(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; X2 = gs.XS[i]
    for row in range(6):
        tr = T(b + 2 + row)
        if t < tr: continue
        y = GY + 150 - row * 22; s_ = 1 - row * 0.09
        for c in range(9):
            x = X2 + (c - 4) * 52 * s_
            gs.members[i][0].person(cv, x, y + 30, 0.55 * s_ * pop(t, tr, 0.15), P.WARM, A * (0.7 + 0.6 * pulse(t, tr, 0.3)))
            cv.glow((x, y), 14, P.GOLD, 0.5 * A * pulse(t, tr, 0.3))


def morph(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; c0 = np.array([gs.XS[i], 300.]); size = 110
    k = int(cl((t - T(b + 2)) / gs.e8, -1, 3)); s = cl((t - T(b + 2 + max(k, 0))) * 6)
    for idx in range(40):
        q, v = SPARK[idx]; scat = c0 + np.array([math.cos(q), math.sin(q)]) * 160 * v
        if k < 0: p = np.array(heads[i][0]) + (scat - np.array(heads[i][0])) * eo(ramp(t, T(b + 1), T(b + 2)))
        else:
            prev = scat if k == 0 else c0 + SHAPES[k - 1][idx] * size
            p = prev + (c0 + SHAPES[k][idx] * size - prev) * eo(s)
        cv.circle(tuple(p), 3.2, P.WARM, A, fill=True); cv.glow(tuple(p), 9, P.GOLD, 0.5 * A)
    if k >= 0 and s >= 0.99: cv.path([tuple(c0 + p * size) for p in SHAPES[k]], P.GOLD, 0.5 * A, 1.2, smooth=False)


# ------------------------------------------------------------------ NF
def lanterns(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; X = gs.XS[i]
    for k, dx in enumerate((-240, 200, -120, 300, 60, -330)):
        tf = T(b + 1 + k)
        if t < tf: continue
        x = X + dx; y = GY - 60 - (t - tf) * 85 - 30 * (k % 2)
        cv.path([(x - 18, y - 22), (x + 18, y - 22), (x + 14, y + 20), (x - 14, y + 20), (x - 18, y - 22)], P.GOLD, A, 1.8, smooth=False)
        flame(cv, x, y + 12, 20 * pop(t, tf, 0.15), P.WARM, A); cv.glow((x, y), 40, P.GOLD, A * (0.5 + pulse(t, tf, 0.3)))


def bloom(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; cx, cy = gs.XS[i], 320
    for k in range(8):
        tf = T(b + 1 + k // 2) + (k % 2) * 0.05
        if t < tf: continue
        q = k * math.pi / 4 + t * 0.15; g = eo(ramp(t, tf, tf + 0.2)) * pop(t, tf, 0.2)
        L = 70 * g
        pts = [(cx + L * s * math.cos(q) - 22 * g * math.sin(s * math.pi) * math.sin(q), cy + L * s * math.sin(q) + 22 * g * math.sin(s * math.pi) * math.cos(q)) for s in np.linspace(0, 1, 12)]
        pts += [(cx + L * s * math.cos(q) + 22 * g * math.sin(s * math.pi) * math.sin(q), cy + L * s * math.sin(q) - 22 * g * math.sin(s * math.pi) * math.cos(q)) for s in np.linspace(1, 0, 12)]
        cv.path(pts, P.SOFT, A, 1.8, smooth=False); cv.poly(pts, P.LINE * 0.15, A, layer=cv.F)
    if t >= T(b + 1):
        cv.circle((cx, cy), 12, P.WARM, A, fill=True); cv.glow((cx, cy), 60, P.GOLD, A * (0.5 + pulse(t, gs.quarter(t), 0.3)))


def lightlink(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; h = heads[i][0]
    for k, (px, sc) in enumerate(((gs.XS[i] - 300, 1.0), (gs.XS[i] + 300, 1.0), (gs.XS[i] - 170, 0.8), (gs.XS[i] + 170, 0.8), (gs.XS[i], 0.7))):
        tf = T(b + 2 + k)
        if t < tf - 0.15: continue
        tgt = (px, GY + 120 - 30 * sc); kk = eo(ramp(t, tf - 0.15, tf)); m = (lerp(h[0], tgt[0], kk), lerp(h[1], tgt[1], kk))
        cv.path([h, m], P.WARM, A * 0.8, 1.8, smooth=False); cv.path([h, m], P.GOLD, A * 0.3, 8, smooth=False, layer=cv.F)
        if t >= tf:
            gs.members[i][0].person(cv, px, GY + 150, 1.3 * sc * pop(t, tf, 0.15), P.GOLD, A * (0.8 + 0.6 * pulse(t, tf, 0.3)), A, t)
            cv.glow(tgt, 50, P.GOLD, A * pulse(t, tf, 0.4))


def fireworks(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P
    for k, (dx, y) in enumerate(((-260, 260), (60, 180), (-60, 330), (-360, 160), (120, 300))):
        tf = T(b + 1 + k)
        if t < tf - 0.2: continue
        x = gs.XS[i] + dx
        if t < tf:
            yy = lerp(GY - 40, y, eo(ramp(t, tf - 0.2, tf))); cv.circle((x, yy), 4, P.WARM, A, fill=True); continue
        kk = cl((t - tf) / 1.1); r = 20 + 130 * eo(kk); a = A * (1 - kk) ** 1.2
        for j in range(18):
            q = j * 2 * math.pi / 18
            cv.path([(x + r * 0.55 * math.cos(q), y + r * 0.55 * math.sin(q)), (x + r * math.cos(q), y + r * math.sin(q) + 18 * kk)], P.GOLD if j % 2 else P.SOFT, a, 1.6, smooth=False)
        cv.glow((x, y), 70, P.GOLD, 1.2 * pulse(t, tf, 0.3) * A)


# ------------------------------------------------------------------ SJ
def checklist(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; x0, y0 = gs.XS[i] + 230, 400
    if t >= T(b + 1):
        k = eo(ramp(t, T(b + 1), T(b + 1.5)))
        cv.path([(x0 - 30, y0 - 50), (x0 + 250, y0 - 50), (x0 + 250, y0 + 300), (x0 - 30, y0 + 300), (x0 - 30, y0 - 50)], P.LINE, A * 0.7, 1.6, k, smooth=False)
    for k in range(5):
        tf = T(b + 2 + k); y = y0 + k * 56
        if t < T(b + 1.5): continue
        cv.path([(x0, y - 12), (x0 + 24, y - 12), (x0 + 24, y + 12), (x0, y + 12), (x0, y - 12)], P.SOFT, A, 1.4, smooth=False)
        cv.path([(x0 + 44, y), (x0 + 220, y)], P.LINE, A * 0.5, 1.2, smooth=False)
        if t >= tf:
            cv.path([(x0 + 4, y), (x0 + 11, y + 8), (x0 + 28, y - 16)], P.WARM, A, 2.4, eo(ramp(t, tf, tf + 0.1)), smooth=False)
            cv.glow((x0 + 12, y), 20, P.GOLD, A * pulse(t, tf, 0.3) * 1.5)


def shield(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; cx = gs.XS[i] + 60; R = 250
    for k, dx in enumerate((-110, -40, 40, 110)):
        if t >= T(b + 1): gs.members[i][0].person(cv, cx + dx, GY + 140, 0.9, P.SOFT, A * 0.8 * eo(ramp(t, T(b + 1), T(b + 1.5))), 0, t)
    for k in range(6):
        tf = T(b + 2 + k)
        if t < tf: continue
        q0, q1 = math.pi + k * math.pi / 6, math.pi + (k + 1) * math.pi / 6
        seg = [(cx + R * math.cos(q), GY + 150 + R * 0.9 * math.sin(q)) for q in np.linspace(q0, q1, 12)]
        cv.path(seg, P.GOLD, A, 2.4, eo(ramp(t, tf, tf + 0.12)), smooth=False); cv.path(seg, P.GOLD, A * 0.3, 10, smooth=False, layer=cv.F)
        cv.glow(seg[6], 30, P.GOLD, A * pulse(t, tf, 0.3))
    if t >= T(b + 8): cv.glow((cx, GY + 30), R * 0.8, P.GOLD, 0.15 * A)


def pillars(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; cx = gs.XS[i]; xs = [cx - 300, cx - 180, cx + 180, cx + 300]
    for k, x in enumerate(xs):
        tf = T(b + 2 + k); up = eo(ramp(t, tf, tf + 0.15))
        if up <= 0: continue
        h = 360 * up
        cv.path([(x - 18, GY), (x - 18, GY - h), (x + 18, GY - h), (x + 18, GY)], P.SOFT, A, 2, smooth=False)
        for f in (-8, 0, 8): cv.path([(x + f, GY - 10), (x + f, GY - h + 10)], P.LINE, A * 0.4, 1.0, smooth=False)
        cv.glow((x, GY - h), 24, P.GOLD, A * pulse(t, tf, 0.3) * 1.5)
    tl = T(b + 6)
    if t >= tl:
        k = eo(ramp(t, tl, tl + 0.2))
        cv.path([(cx - 340, GY - 372), (cx + 340, GY - 372)], P.GOLD, A, 2.6, k, smooth=False)
        cv.path([(cx - 360, GY - 372), (cx, GY - 470), (cx + 360, GY - 372)], P.GOLD, A, 2.2, k, smooth=False)
        cv.glow((cx, GY - 420), 80, P.GOLD, A * pulse(t, tl, 0.4) * 1.5)


def circle(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; cx, cy, rx, ry = gs.XS[i], GY + 70, 300, 70
    pos = []
    for k in range(10):
        q = math.pi / 2 + (k // 2 + 1) * (1 if k % 2 == 0 else -1) * math.pi / 6
        pos.append((cx + rx * math.cos(q), cy + ry * math.sin(q)))
    for k, p in enumerate(pos):
        tf = T(b + 1 + k // 2)
        if t < tf: continue
        gs.members[i][0].person(cv, p[0], p[1] + 40, 0.9 * pop(t, tf, 0.15), P.WARM, A * (0.8 + 0.6 * pulse(t, tf, 0.3)), A * 0.8, t)
    lk = T(b + 6)
    if t >= lk:
        k = eo(ramp(t, lk, lk + 0.3))
        cv.path([(cx + rx * math.cos(q), cy - 20 + ry * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120)], P.GOLD, A, 2, k, smooth=False)
        cv.glow((cx, cy), 200, P.GOLD, 0.25 * A * (k + pulse(t, lk, 0.4)))


# ------------------------------------------------------------------ SP
def _gear(cv, c, r, teeth, rot, col, a):
    pts = []
    for k in range(teeth * 2):
        q0 = rot + k * math.pi / teeth; rr = r if k % 2 == 0 else r * 0.8
        pts += [(c[0] + rr * math.cos(q0), c[1] + rr * math.sin(q0)), (c[0] + rr * math.cos(q0 + math.pi / teeth), c[1] + rr * math.sin(q0 + math.pi / teeth))]
    cv.path(pts + [pts[0]], col, a, 1.8, smooth=False); cv.circle(c, r * 0.3, col, a, 1.6)


def gears(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; x0 = gs.XS[i] + 260
    G = [((x0, 420), 60, 12, 1), ((x0 + 104, 470), 46, 9, -1.33), ((x0 + 40, 540), 38, 8, 1.6), ((x0 + 170, 380), 40, 8, 1.2), ((x0 + 150, 560), 30, 6, -2)]
    for k, (c, r, n, sp) in enumerate(G):
        tf = T(b + 1 + k)
        if t < tf: continue
        g = pop(t, tf, 0.15); spin = (t - T(b + 1)) * 1.4 * sp if t >= T(b + 6) else 0.0
        _gear(cv, c, r * g, n, spin, P.SOFT if k % 2 else P.GOLD, A); cv.glow(c, r, P.GOLD, A * pulse(t, tf, 0.3))


def brush(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; cx, cy = gs.XS[i] + 40, 470
    cols = (P.GOLD, P.SOFT, P.LINE, P.WARM, P.GOLD)
    for k in range(5):
        tf = T(b + 1 + k)
        if t < tf: continue
        R = 230 + k * 34; fr = eo(ramp(t, tf, tf + 0.25))
        arc_ = [(cx + R * math.cos(q), cy + R * 0.75 * math.sin(q)) for q in np.linspace(math.pi * 1.08, math.pi * 1.92, 60)]
        cv.path(arc_, cols[k], A, 6 - k * 0.6, fr, smooth=False); cv.path(arc_, cols[k], A * 0.35, 18, fr, smooth=False, layer=cv.F)


def target(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; c = (gs.XS[i] + 330, 470); h = heads[i][0]
    if t >= T(b + 1):
        k = eo(ramp(t, T(b + 1), T(b + 1.5)))
        for j, r in enumerate((90, 62, 34, 10)): cv.circle(c, r * k, P.SOFT if j % 2 else P.GOLD, A, 1.8, fill=(j == 3))
    for k in range(4):
        tf = T(b + 2 + k)
        if t < tf - 0.15: continue
        hit = (c[0] + (k - 1.5) * 9, c[1] + ((k * 7) % 5 - 2) * 6)
        kk = eo(ramp(t, tf - 0.15, tf)); p = (lerp(h[0], hit[0], kk), lerp(h[1], hit[1], kk))
        tail = (lerp(h[0], hit[0], max(0, kk - 0.25)), lerp(h[1], hit[1], max(0, kk - 0.25)))
        cv.path([tail, p], P.WARM, A, 2.4, smooth=False)
        if t >= tf: cv.glow(hit, 40, P.GOLD, A * pulse(t, tf, 0.3) * 2); cv.path([(hit[0] - 30, hit[1]), hit], P.WARM, A, 2, smooth=False)


def spotlight(gs, cv, tx, t, i, b, A, heads, face):
    T, P = gs.T, gs.P; tgt = (gs.XS[i], GY - 40)
    for k, sx in enumerate((gs.XS[i] - 520, gs.XS[i] + 420, gs.XS[i] - 220, gs.XS[i] + 160)):
        tf = T(b + 1 + k)
        if t < tf: continue
        a = A * (0.6 + 0.8 * pulse(t, tf, 0.3))
        src = (sx, -40); w = 120
        cone = [src, (tgt[0] - w, tgt[1] + 30), (tgt[0] + w, tgt[1] + 30)]
        cv.poly(cone, P.WARM * 0.06, a, layer=cv.F)
        cv.path([src, cone[1]], P.WARM, a * 0.5, 1.2, smooth=False); cv.path([src, cone[2]], P.WARM, a * 0.5, 1.2, smooth=False)
    if t >= T(b + 5):
        for k in range(60):
            x = gs.XS[i] + ((k * 97) % 700) - 350; y = ((t - T(b + 5)) * (90 + k % 7 * 20) + (k * 53) % 300) % 700 + 80
            cv.circle((x, y), 3, (P.GOLD, P.SOFT, P.WARM)[k % 3], A * 0.9, fill=True)


# ------------------------------------------------------------------ earth signs
def garden(gs, cv, tx, t, i, b, A, heads, face):
    """Taurus: a flower grows and blooms on each beat"""
    T, P = gs.T, gs.P; X = gs.XS[i]
    for k, dx in enumerate((-160, 180, -300, 320, -60, 120, -420)):
        tf = T(b + 1 + k)
        if t < tf: continue
        g = eo(ramp(t, tf, tf + 0.25)); x = X + dx; h = (150 + 40 * (k % 3)) * g; top = (x + 10 * math.sin(t + k), GY - h)
        cv.path([(x, GY), (x + 14, GY - h * 0.5), top], P.LINE, A, 2)
        cv.path([(x + 6, GY - h * 0.4), (x + 34, GY - h * 0.5), (x + 10, GY - h * 0.33)], P.LINE, A * 0.8, 1.6)
        bl = pop(t, tf + 0.15, 0.2)
        for j in range(5):
            q = j * 2 * math.pi / 5 + t * 0.3; cv.circle((top[0] + 16 * bl * math.cos(q), top[1] + 16 * bl * math.sin(q)), 11 * bl, P.SOFT, A, 1.6)
        cv.circle(top, 6 * bl, P.WARM, A, fill=True); cv.glow(top, 34, P.GOLD, A * (0.4 + pulse(t, tf + 0.15, 0.3)))


def harvest(gs, cv, tx, t, i, b, A, heads, face):
    """Virgo: a row of wheat rises on each beat"""
    T, P = gs.T, gs.P; X = gs.XS[i]
    for row in range(6):
        tf = T(b + 1 + row)
        if t < tf: continue
        g = eo(ramp(t, tf, tf + 0.2)); y0 = GY + 140 - row * 24; sc = 1 - row * 0.09
        for c in range(9):
            x = X + (c - 4) * 70 * sc + (row % 2) * 30; h = 120 * sc * g; sway = 8 * math.sin(t * 2 + c + row)
            top = (x + sway, y0 - h); cv.path([(x, y0), top], P.GOLD, A * 0.9, 1.4, smooth=False)
            for j in range(4):
                p = (lerp(x, top[0], 0.7 + j * 0.08), lerp(y0, top[1], 0.7 + j * 0.08))
                cv.path([(p[0] - 5 * sc, p[1] + 5 * sc), p, (p[0] + 5 * sc, p[1] + 5 * sc)], P.WARM, A, 1.3, smooth=False)
        cv.glow((X, y0 - 60), 200, P.GOLD, 0.12 * A * pulse(t, tf, 0.3))


def summit(gs, cv, tx, t, i, b, A, heads, face):
    """Capricorn: a mountain behind; the path to the peak lights one step per beat, then a flag"""
    T, P = gs.T, gs.P; X = gs.XS[i] + 260; peak = (X, 240)
    a0 = eo(ramp(t, T(b), T(b + 1)))
    cv.path([(X - 380, GY), peak, (X + 380, GY)], P.LINE, A * a0, 2.2, a0, smooth=False)
    cv.path([(X - 140, 560), (X - 40, 470), (X + 20, 520), (X + 150, 420)], P.LINE, A * a0 * 0.4, 1.2, smooth=False)
    path = [(X - 300, GY - 10), (X - 120, 800), (X - 220, 690), (X - 40, 580), (X - 130, 470), (X + 20, 380), (X - 30, 300), peak]
    for k in range(len(path) - 1):
        tf = T(b + 1 + k)
        if t < tf: continue
        fr = eo(ramp(t, tf, tf + 0.15))
        cv.path([path[k], path[k + 1]], P.GOLD, A, 2.6, fr, smooth=False); cv.path([path[k], path[k + 1]], P.GOLD, A * 0.3, 10, fr, smooth=False, layer=cv.F)
        cv.circle(path[k + 1], 5, P.WARM, A * fr, fill=True); cv.glow(path[k + 1], 26, P.GOLD, A * pulse(t, tf + 0.15, 0.3) * 1.5)
    tf = T(b + len(path))
    if t >= tf - 0.2:
        g = eo(ramp(t, tf - 0.2, tf)); cv.path([peak, (peak[0], peak[1] - 90 * g)], P.SOFT, A, 2, smooth=False)
        if g >= 1:
            fl = [(peak[0], peak[1] - 90), (peak[0] + 60, peak[1] - 78 + 6 * math.sin(t * 4)), (peak[0], peak[1] - 60)]
            cv.path(fl + [fl[0]], P.GOLD, A, 2, smooth=False); cv.glow(peak, 80, P.GOLD, A * (0.4 + pulse(t, tf, 0.4)))


# ------------------------------------------------------------------ air signs
def planes(gs, cv, tx, t, i, b, A, heads, face):
    """Gemini: a paper plane launches on each beat and loops across the sky"""
    T, P = gs.T, gs.P; X = gs.XS[i]
    for k in range(6):
        tf = T(b + 1 + k)
        if t < tf: continue
        u = t - tf; side = 1 if k % 2 == 0 else -1
        def pos(u_):
            return (X + side * (60 + 260 * u_), 470 - 160 * u_ - 60 * math.sin(u_ * 3 + k) - k * 18)
        p, p2 = np.array(pos(u)), np.array(pos(u + 0.05)); d = p2 - p; d /= (np.linalg.norm(d) + 1e-6); n = np.array([-d[1], d[0]])
        nose = p + d * 24; wl = p - d * 18 + n * 14; wr = p - d * 18 - n * 14; mid = p - d * 10
        cv.path([tuple(wl), tuple(nose), tuple(wr), tuple(mid), tuple(wl)], P.SOFT, A, 1.8, smooth=False)
        trail = [pos(max(0, u - s)) for s in np.linspace(0, 0.6, 10)]
        for j in range(0, 9, 2): cv.path([trail[j], trail[j + 1]], P.GOLD, A * (1 - j / 10) * 0.8, 1.4, smooth=False)


def balance(gs, cv, tx, t, i, b, A, heads, face):
    """Libra: great scales in the sky tip on each beat, smaller each time, then settle level and glow"""
    T, P = gs.T, gs.P; c = (gs.XS[i], 250)
    a0 = eo(ramp(t, T(b), T(b + 1)))
    if a0 <= 0: return
    n = math.floor(cl((t - T(b + 1)) / gs.e8, 0, 6)); amp = 0.22 * (1 - n / 6)
    tilt = amp * (1 if n % 2 == 0 else -1) * eo(cl((t - T(b + 1 + n)) * 6)) if t >= T(b + 1) else 0
    L, R = (c[0] - 260 * math.cos(tilt), c[1] - 260 * math.sin(tilt)), (c[0] + 260 * math.cos(tilt), c[1] + 260 * math.sin(tilt))
    cv.path([(c[0], c[1] + 300), c], P.WARM, A * a0, 2.4, smooth=False); cv.path([L, R], P.WARM, A * a0, 3, smooth=False)
    cv.circle(c, 10, P.GOLD, A * a0, fill=True)
    for e in (L, R):
        py = e[1] + 120
        cv.path([e, (e[0] - 60, py)], P.SOFT, A * a0 * 0.8, 1.4, smooth=False); cv.path([e, (e[0] + 60, py)], P.SOFT, A * a0 * 0.8, 1.4, smooth=False)
        cv.path([(e[0] - 70, py), (e[0] - 46, py + 24), (e[0] + 46, py + 24), (e[0] + 70, py)], P.GOLD, A * a0, 2.4, smooth=False)
    if t >= T(b + 7): cv.glow(c, 200, P.GOLD, A * (0.3 + 1.2 * pulse(t, T(b + 7), 0.5)))


def ripples(gs, cv, tx, t, i, b, A, heads, face):
    """Aquarius: a drop falls on each beat and rings spread across the ground; bubbles rise"""
    T, P = gs.T, gs.P; X = gs.XS[i]
    for k in range(6):
        tf = T(b + 1 + k); x = X + (k - 2.5) * 110
        if t < tf - 0.2: continue
        if t < tf:
            y = lerp(380, GY, eo(ramp(t, tf - 0.2, tf))); cv.circle((x, y), 6, P.SOFT, A, fill=True); continue
        for j in range(3):
            kk = cl((t - tf) / 1.4 - j * 0.15)
            if 0 < kk < 1:
                cv.path([(x + (20 + 260 * kk) * math.cos(q), GY + 20 + (5 + 40 * kk) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 80)],
                        P.SOFT if j else P.GOLD, A * (1 - kk), 1.8, smooth=False)
        cv.glow((x, GY), 40, P.LINE, A * pulse(t, tf, 0.3))
    for k in range(24):
        y = GY - ((t - T(b)) * (60 + k * 5) + k * 37) % 600; x = X + ((k * 53) % 600) - 300
        if t > T(b + 1): cv.circle((x, y), 3 + k % 3, P.SOFT, A * 0.6, 1.2)


# ------------------------------------------------------------------ water signs
def moonrise(gs, cv, tx, t, i, b, A, heads, face):
    """Cancer: the moon above waxes one phase per beat to full"""
    T, P = gs.T, gs.P; c = (gs.XS[i], 170); R = 70
    a0 = eo(ramp(t, T(b), T(b + 1)))
    if a0 <= 0: return
    ph = cl((t - T(b + 1)) / (6 * gs.e8)); step = math.floor(ph * 6) / 6 + eo(cl((ph * 6 % 1) * 4)) / 6 if ph < 1 else 1.0
    outer = [(c[0] + R * math.cos(q), c[1] + R * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 30)]
    w = R * math.cos(step * math.pi)
    inner = [(c[0] + w * math.cos(q), c[1] + R * math.sin(q)) for q in np.linspace(math.pi / 2, -math.pi / 2, 30)]
    lit = outer + inner
    cv.circle(c, R, P.LINE, A * a0 * 0.35, 1.2); cv.path(lit + [lit[0]], P.WARM, A * a0, 2.4, smooth=False)
    cv.poly(lit, P.GOLD * 0.35, A * a0, layer=cv.F); cv.glow(c, R * (1 + step), P.GOLD, A * a0 * (0.2 + 0.5 * step))
    if ph >= 1: cv.glow(c, 220, P.GOLD, A * 0.8 * pulse(t, T(b + 7), 0.5))


def phoenix(gs, cv, tx, t, i, b, A, heads, face):
    """Scorpio: phoenix wings open behind him, one feather pair per beat"""
    T, P = gs.T, gs.P; c = np.array([gs.XS[i], face[i][1] + 120.])
    for k in range(7):
        tf = T(b + 1 + k)
        if t < tf: continue
        g = eo(ramp(t, tf, tf + 0.2)); q = math.radians(200 + k * 16); L = (170 + k * 30) * g
        for sx in (-1, 1):
            d = np.array([sx * -math.cos(q), math.sin(q)]); n = np.array([-d[1], d[0]])
            base = c + np.array([sx * 30, -20]); tip = base + d * L
            pts = [tuple(base), tuple(base + d * L * 0.5 + n * 18 * sx), tuple(tip), tuple(base + d * L * 0.5 - n * 10 * sx), tuple(base)]
            cv.path(pts, P.GOLD if k % 2 == 0 else P.WARM, A, 2, smooth=False); cv.poly(pts, P.GOLD * 0.12, A, layer=cv.F)
        cv.glow(tuple(c), 120 + 30 * k, P.GOLD, A * 0.25 * pulse(t, tf, 0.3))


def school(gs, cv, tx, t, i, b, A, heads, face):
    """Pisces: fish swim in a ring around him, one more fish per beat"""
    T, P = gs.T, gs.P; c = (gs.XS[i], 520)
    for k in range(8):
        tf = T(b + 1 + k * 0.75)
        if t < tf: continue
        q = (t - T(b)) * 0.9 + k * 2 * math.pi / 8; c2 = (c[0] + 300 * math.cos(q), c[1] + 150 * math.sin(q)); d = q + math.pi / 2
        s = 0.8 * pop(t, tf, 0.15)
        body = [(c2[0] + 50 * s * math.cos(u) * math.cos(d) - 20 * s * math.sin(u) * math.sin(d), c2[1] + 50 * s * math.cos(u) * math.sin(d) + 20 * s * math.sin(u) * math.cos(d)) for u in np.linspace(0, 2 * math.pi, 24)]
        tb = (c2[0] - 50 * s * math.cos(d), c2[1] - 50 * s * math.sin(d))
        tl = [(tb[0] - 28 * s * math.cos(d) - 18 * s * math.sin(d), tb[1] - 28 * s * math.sin(d) + 18 * s * math.cos(d)), (tb[0] - 28 * s * math.cos(d) + 18 * s * math.sin(d), tb[1] - 28 * s * math.sin(d) - 18 * s * math.cos(d))]
        cv.path(body, P.SOFT, A, 1.8, smooth=False); cv.path([tl[0], tb, tl[1], tl[0]], P.SOFT, A, 1.6, smooth=False)
        cv.glow(c2, 30, P.GOLD, A * (0.3 + pulse(t, tf, 0.3)))


# ------------------------------------------------------------------ fire signs
def ignite(gs, cv, tx, t, i, b, A, heads, face):
    """Aries: fire pillars burst out along the ground, alternating left/right, one per beat"""
    T, P = gs.T, gs.P; X = gs.XS[i]
    for k in range(7):
        tf = T(b + 1 + k)
        if t < tf: continue
        side = -1 if k % 2 == 0 else 1; x = X + side * (130 + 70 * (k // 2) * 1.6)
        g = pop(t, tf, 0.18); h = (150 + 30 * (k % 3)) * g * (1 + 0.08 * math.sin(t * 9 + k))
        flame(cv, x, GY + 6, h, P.GOLD, A); flame(cv, x, GY + 6, h * 0.6, P.WARM, A)
        flame(cv, x, GY + 6, h * 1.5, P.GOLD, 0.35 * A, layer=cv.F)
        cv.glow((x, GY - h * 0.4), 60, P.GOLD, A * (0.4 + 1.2 * pulse(t, tf, 0.3)))
        for j in range(6):
            q = -math.pi / 2 + (j - 2.5) * 0.35; r = 40 + 160 * cl((t - tf) * 2)
            if t - tf < 0.6:
                cv.circle((x + r * math.cos(q), GY - 40 + r * math.sin(q)), 3, P.WARM, A * (1 - (t - tf) / 0.6), fill=True)


def sunburst(gs, cv, tx, t, i, b, A, heads, face):
    """Leo: a sun rises behind the head; every beat adds a ring of rays"""
    T, P = gs.T, gs.P; c = (gs.XS[i], face[i][1] - 10)
    up = eo(ramp(t, T(b + 1), T(b + 2)))
    if up <= 0: return
    R = 90 * up
    cv.circle(c, R, P.GOLD, A, 2.4); cv.circle(c, R * 0.8, P.WARM, A * 0.5, 1.2); cv.glow(c, R * 1.6, P.GOLD, 0.35 * A)
    for ring in range(5):
        tf = T(b + 2 + ring)
        if t < tf: continue
        n = 12 + ring * 4; r0 = R + 18 + ring * 26; L = (40 + ring * 10) * eo(ramp(t, tf, tf + 0.15))
        for k in range(n):
            q = k * 2 * math.pi / n + ring * 0.2 + t * 0.05 * (1 if ring % 2 else -1)
            cv.path([(c[0] + r0 * math.cos(q), c[1] + r0 * math.sin(q)), (c[0] + (r0 + L) * math.cos(q), c[1] + (r0 + L) * math.sin(q))],
                    P.GOLD if ring % 2 == 0 else P.WARM, A * (0.8 - ring * 0.08), 1.6, smooth=False)
        cv.glow(c, R * 2, P.GOLD, 0.3 * A * pulse(t, tf, 0.3))


def arrows(gs, cv, tx, t, i, b, A, heads, face):
    """Sagittarius: one arrow per beat flies into the sky and becomes a star"""
    T, P = gs.T, gs.P; src = np.array(heads[i][0])
    targets = [(gs.XS[i] + dx, y) for dx, y in ((-260, 130), (-60, 70), (160, 150), (320, 60), (80, 230), (420, 210))]
    stars = []
    for k, tg in enumerate(targets):
        tf = T(b + 1 + k)
        if t < tf - 0.2: continue
        kk = eo(ramp(t, tf - 0.2, tf)); tg = np.array(tg)
        if kk < 1:
            p = src + (tg - src) * kk; tail = src + (tg - src) * max(0, kk - 0.3)
            cv.path([tuple(tail), tuple(p)], P.WARM, A, 2.4, smooth=False); cv.path([tuple(tail), tuple(p)], P.GOLD, A * 0.35, 10, smooth=False, layer=cv.F)
        else:
            gs.members[i][0].star_flare(cv, tuple(tg), 40 * (1 + 1.5 * pulse(t, tf, 0.3)), A)
            stars.append(tuple(tg))
    if len(stars) > 1:
        for k in range(len(stars) - 1):
            cv.path([stars[k], stars[k + 1]], P.LINE, A * 0.6, 1.4, smooth=False)


SIGS = {f.__name__: f for f in (garden, harvest, summit, planes, balance, ripples, moonrise, phoenix, school, ignite, sunburst, arrows, blueprint, tree, formation, morph, lanterns, bloom, lightlink, fireworks,
                                  checklist, shield, pillars, circle, gears, brush, target, spotlight)}
