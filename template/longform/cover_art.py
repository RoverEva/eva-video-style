"""Golden line-art of the 12 zodiac signs for the 3:4 covers (zodiac_cover.py).

Each creature is drawn in a unit box (x 0..1 right, y 0..1 down, ground at y≈0.97) that the cover maps onto
x ∈ [cx-450, cx+450], y ∈ [cy-450, cy+390]. Outline = translucent fill + crisp line; inner lines give the
sculpted "light-woven" look of the reference.
"""
import math
import numpy as np


def mapper(cx, cy, w=980, h=890):
    x0, y0 = cx - w / 2, 1668 - 0.97 * h
    def T(pts):
        return [(x0 + x * w, y0 + y * h) for x, y in pts]
    return T


def matplotlib_path_contains(poly, pts):
    from matplotlib.path import Path
    return Path(poly).contains_points(pts)


def body(art, T, pts, w=3.2, fill=0.32, sm=True):
    P = T(pts); art.fill(P, fill, sm=sm); art.line(P, w, 1.0, closed=True, sm=sm)
    return P


def stroke(art, T, pts, w=2.0, a=0.8, sm=True):
    art.line(T(pts), w, a, sm=sm)


def tapered(art, T, pts, w0, w1, a=1.0, fill=0.4):
    """a horn / tail / limb drawn as a tapered filled shape (widths in unit coords)"""
    from zodiac_cover import smooth
    P = smooth(np.array(pts), False, 60)
    d = np.gradient(P, axis=0); n = np.stack([-d[:, 1], d[:, 0]], 1); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    wv = np.linspace(w0, w1, len(P))[:, None]
    poly = np.vstack([P + n * wv, (P - n * wv)[::-1]])
    Q = T(poly.tolist()); art.fill(Q, fill, sm=False); art.line(Q, 2.4, a, closed=True, sm=False)
    return P


def spiral(c, r0, r1, a0, a1, n=60, sx=1.0, sy=1.0):
    return [(c[0] + sx * (r0 + (r1 - r0) * u) * math.cos(a0 + (a1 - a0) * u), c[1] + sy * (r0 + (r1 - r0) * u) * math.sin(a0 + (a1 - a0) * u)) for u in np.linspace(0, 1, n)]


def ring_marks(art, T, P, k=5, L=0.012, a=0.6):
    """short cross strokes along a path (horn ridges)"""
    P = np.asarray(P)
    for i in np.linspace(3, len(P) - 4, k).astype(int):
        d = P[i + 1] - P[i - 1]; d /= np.linalg.norm(d) + 1e-9; n = np.array([-d[1], d[0]])
        stroke(art, T, [tuple(P[i] + n * L), tuple(P[i] - n * L)], 1.6, a, sm=False)


def eye(art, T, c, r=0.008):
    q = T([c])[0]; art.dot(q, r * 900, 1.0)


# ------------------------------------------------------------------ figures
def person(art, T, x, g, h, f=1, hair='short', hand=None, hand2=None, robe=1.0, fill=0.28):
    """a robed figure standing on ground g, height h, facing f (+1 right / -1 left)"""
    hc = (x + 0.01 * f * h, g - 0.90 * h); r = 0.06 * h
    sh = g - 0.80 * h
    # robe silhouette
    hem = 0.17 * h * robe
    rb = [(x - 0.10 * h, sh), (x - 0.13 * h, g - 0.55 * h), (x - hem, g - 0.02 * h), (x - hem * 0.4, g), (x + hem * 0.4, g),
          (x + hem, g - 0.02 * h), (x + 0.13 * h, g - 0.55 * h), (x + 0.10 * h, sh), (x + 0.03 * h, sh - 0.03 * h), (x - 0.03 * h, sh - 0.03 * h)]
    body(art, T, rb, 3.0, fill)
    for k in (-0.6, -0.15, 0.3, 0.7):        # folds
        stroke(art, T, [(x + k * 0.08 * h, g - 0.6 * h), (x + k * 0.12 * h, g - 0.3 * h), (x + k * 0.16 * h, g - 0.03 * h)], 1.4, 0.45)
    stroke(art, T, [(x - 0.12 * h, g - 0.52 * h), (x, g - 0.5 * h), (x + 0.12 * h, g - 0.52 * h)], 2.0, 0.8)   # belt
    # head + face profile
    face = [(hc[0] + r * math.cos(t), hc[1] + r * 1.15 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    body(art, T, face, 2.6, fill)
    stroke(art, T, [(hc[0] + f * r * 0.55, hc[1] - r * 0.1), (hc[0] + f * r * 0.62, hc[1] - r * 0.05)], 2.2, 1.0, sm=False)
    stroke(art, T, [(hc[0] + f * r * 0.35, hc[1] + r * 0.55), (hc[0] + f * r * 0.6, hc[1] + r * 0.5)], 1.6, 0.8, sm=False)
    if hair == 'long':
        hp = [(hc[0] + f * r * 0.7, hc[1] - r * 0.7), (hc[0], hc[1] - r * 1.3), (hc[0] - f * r * 1.1, hc[1] - r * 0.6), (hc[0] - f * r * 1.4, hc[1] + r * 1.2),
              (hc[0] - f * r * 1.6, g - 0.62 * h), (hc[0] - f * r * 1.0, g - 0.6 * h), (hc[0] - f * r * 0.7, hc[1] + r * 1.4), (hc[0] - f * r * 0.2, hc[1] - r * 0.4)]
        body(art, T, hp, 2.4, fill * 0.8)
        for k in range(3): stroke(art, T, [(hc[0] - f * r * (0.3 + 0.3 * k), hc[1] - r * 0.9), (hc[0] - f * r * (1.0 + 0.2 * k), hc[1] + r * 0.8), (hc[0] - f * r * (1.2 + 0.1 * k), g - 0.64 * h)], 1.3, 0.5)
    else:
        hp = [(hc[0] + f * r * 0.9, hc[1] - r * 0.5), (hc[0] + f * r * 0.2, hc[1] - r * 1.25), (hc[0] - f * r * 0.9, hc[1] - r * 0.9), (hc[0] - f * r * 1.1, hc[1] + r * 0.3), (hc[0] - f * r * 0.5, hc[1] - r * 0.3)]
        body(art, T, hp, 2.4, fill * 0.8)
    # arms (sleeves)
    def arm(sx, tgt):
        s0 = (sx, sh + 0.02 * h); e = ((s0[0] + tgt[0]) / 2 + 0.02 * h * (1 if sx < x else -1), (s0[1] + tgt[1]) / 2 + 0.05 * h)
        tapered(art, T, [s0, e, tgt], 0.028 * h, 0.016 * h, 1.0, fill)
        art.fill(T([(tgt[0] + 0.018 * h * math.cos(t), tgt[1] + 0.018 * h * math.sin(t)) for t in np.linspace(0, 6.28, 16)]), fill, sm=False)
    arm(x + 0.1 * h * f, hand or (x + 0.16 * h * f, g - 0.45 * h))
    arm(x - 0.1 * h * f, hand2 or (x - 0.15 * h * f, g - 0.46 * h))
    return hc


def wheat(art, T, base, top, a=1.0):
    stroke(art, T, [base, ((base[0] + top[0]) / 2 + 0.01, (base[1] + top[1]) / 2), top], 2.0, a)
    dx, dy = top[0] - base[0], top[1] - base[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    for k in range(7):
        p = (top[0] - ux * k * 0.028, top[1] - uy * k * 0.028)
        for sd in (-1, 1):
            g = [p, (p[0] + nx * sd * 0.02 + ux * 0.012, p[1] + ny * sd * 0.02 + uy * 0.012), (p[0] + ux * 0.03, p[1] + uy * 0.03)]
            art.fill(T(g), 0.5, sm=False); stroke(art, T, g + [p], 1.4, a, sm=False)


def fish(art, T, c, L, ang, flip=1, fill=0.3):
    ca, sa = math.cos(ang), math.sin(ang)
    R = lambda x, y: (c[0] + (x * ca - flip * y * sa) * L, c[1] + (x * sa + flip * y * ca) * L)
    out = [R(0.5, 0), R(0.35, -0.16), R(0.05, -0.22), R(-0.25, -0.15), R(-0.42, -0.02), R(-0.42, 0.02), R(-0.25, 0.14), R(0.05, 0.2), R(0.35, 0.14)]
    body(art, T, out, 3.0, fill)
    tail = [R(-0.4, 0), R(-0.62, -0.2), R(-0.58, 0), R(-0.62, 0.2)]
    body(art, T, tail, 2.6, fill)
    for k in range(4): stroke(art, T, [R(-0.44, 0), R(-0.6, -0.15 + 0.1 * k)], 1.2, 0.5, sm=False)
    stroke(art, T, [R(0.05, -0.21), R(-0.05, -0.34), R(-0.2, -0.17)], 2.0, 0.9)           # dorsal fin
    stroke(art, T, [R(0.1, 0.16), R(0.0, 0.28), R(-0.1, 0.15)], 1.8, 0.8)
    stroke(art, T, [R(0.28, -0.13), R(0.24, 0), R(0.28, 0.12)], 2.0, 0.9)                 # gill
    eye(art, T, R(0.38, -0.03), 0.007)
    for i in range(3):
        for j in range(4):
            x0, y0 = 0.15 - i * 0.14, -0.1 + j * 0.07
            stroke(art, T, [R(x0, y0 - 0.03), R(x0 - 0.04, y0), R(x0, y0 + 0.03)], 1.1, 0.4)
    return R


# ------------------------------------------------------------------ the twelve
def aries(art, cx, cy):
    T = mapper(cx, cy)
    sil = [(0.20, 0.42), (0.34, 0.38), (0.50, 0.38), (0.60, 0.34), (0.65, 0.26), (0.69, 0.18), (0.75, 0.15), (0.81, 0.18), (0.86, 0.24), (0.88, 0.29),
           (0.85, 0.32), (0.80, 0.33), (0.75, 0.32), (0.71, 0.38), (0.70, 0.50), (0.71, 0.63), (0.72, 0.80), (0.73, 0.97), (0.66, 0.97), (0.65, 0.80),
           (0.63, 0.66), (0.56, 0.65), (0.42, 0.67), (0.34, 0.66), (0.35, 0.82), (0.34, 0.97), (0.27, 0.97), (0.27, 0.86), (0.23, 0.76), (0.18, 0.63), (0.16, 0.51)]
    stroke(art, T, [(0.60, 0.64), (0.59, 0.80), (0.60, 0.97)], 2.4, 0.6); stroke(art, T, [(0.28, 0.66), (0.24, 0.82), (0.22, 0.97)], 2.4, 0.6)
    P = body(art, T, sil)
    # wool curls inside the body
    rr = np.random.default_rng(3); poly = np.array(sil)
    pts = np.c_[rr.uniform(0.18, 0.70, 400), rr.uniform(0.36, 0.66, 400)]
    ins = matplotlib_path_contains(poly, pts)
    for (x, y) in pts[ins][:38]:
        if x > 0.68 and y < 0.4: continue
        r = rr.uniform(0.012, 0.022); a0 = rr.uniform(0, 6.3)
        stroke(art, T, spiral((x, y), r, r * 0.3, a0, a0 + 4.5, 14), 1.2, 0.35)
    # face
    stroke(art, T, [(0.80, 0.21), (0.84, 0.235)], 1.6, 0.7); eye(art, T, (0.79, 0.205)); stroke(art, T, [(0.86, 0.27), (0.87, 0.285)], 2, 0.9, sm=False)
    stroke(art, T, [(0.70, 0.22), (0.64, 0.24), (0.69, 0.27)], 2.2, 0.9)    # ear
    # the spiral horn
    hp = spiral((0.70, 0.25), 0.115, 0.03, -1.25, -1.25 - 2 * math.pi * 1.05, 80, 1.0, 1.05)
    P = tapered(art, T, hp, 0.034, 0.008, 1.0, 0.45); ring_marks(art, T, P, 12, 0.03, 0.55)
    # tail + hooves
    stroke(art, T, [(0.18, 0.44), (0.13, 0.48), (0.12, 0.54)], 3.0, 0.9)
    for x in (0.665, 0.275): stroke(art, T, [(x, 0.94), (x + 0.065, 0.94)], 2, 0.8, sm=False)


def taurus(art, cx, cy):
    T = mapper(cx, cy)
    stroke(art, T, [(0.60, 0.63), (0.58, 0.80), (0.57, 0.97)], 2.4, 0.55); stroke(art, T, [(0.27, 0.66), (0.24, 0.82), (0.22, 0.97)], 2.4, 0.55)
    sil = [(0.20, 0.36), (0.32, 0.33), (0.45, 0.31), (0.56, 0.27), (0.62, 0.20), (0.66, 0.13), (0.71, 0.10), (0.77, 0.12), (0.82, 0.17), (0.86, 0.22), (0.875, 0.26),
           (0.845, 0.29), (0.79, 0.295), (0.74, 0.30), (0.70, 0.36), (0.69, 0.45), (0.72, 0.52), (0.77, 0.58), (0.83, 0.65), (0.81, 0.73), (0.84, 0.80), (0.78, 0.815),
           (0.745, 0.72), (0.725, 0.655), (0.665, 0.62), (0.645, 0.80), (0.66, 0.97), (0.59, 0.975), (0.58, 0.80), (0.56, 0.645), (0.45, 0.665), (0.35, 0.655),
           (0.33, 0.70), (0.35, 0.83), (0.34, 0.97), (0.28, 0.975), (0.28, 0.88), (0.25, 0.80), (0.21, 0.68), (0.17, 0.52)]
    body(art, T, sil, 3.4, 0.34)
    for seg in ([(0.62, 0.33), (0.66, 0.47), (0.64, 0.60)], [(0.55, 0.30), (0.58, 0.44), (0.57, 0.55)], [(0.43, 0.38), (0.45, 0.50), (0.44, 0.60)],
                [(0.25, 0.40), (0.30, 0.52), (0.31, 0.63)], [(0.66, 0.24), (0.69, 0.32)], [(0.48, 0.46), (0.40, 0.50), (0.35, 0.45)],
                [(0.73, 0.58), (0.78, 0.64)], [(0.30, 0.70), (0.31, 0.80)], [(0.63, 0.66), (0.62, 0.78)], [(0.52, 0.33), (0.38, 0.36), (0.26, 0.38)]):
        stroke(art, T, seg, 1.6, 0.55)
    for p in ((0.55, 0.40), (0.38, 0.55), (0.62, 0.52)):
        stroke(art, T, spiral(p, 0.035, 0.012, 0, 4.2, 20), 1.2, 0.4)
    eye(art, T, (0.785, 0.165)); stroke(art, T, [(0.765, 0.155), (0.805, 0.16)], 1.6, 0.8)
    stroke(art, T, [(0.855, 0.245), (0.865, 0.26)], 2.2, 0.9, sm=False); stroke(art, T, [(0.80, 0.27), (0.845, 0.275)], 1.4, 0.6)
    stroke(art, T, [(0.67, 0.15), (0.60, 0.16), (0.645, 0.20)], 2.2, 0.9)
    P = tapered(art, T, [(0.69, 0.12), (0.63, 0.07), (0.60, 0.00), (0.62, -0.06), (0.67, -0.09)], 0.022, 0.004); ring_marks(art, T, P, 6, 0.02)
    P = tapered(art, T, [(0.745, 0.11), (0.775, 0.05), (0.77, -0.01), (0.745, -0.05)], 0.018, 0.004); ring_marks(art, T, P, 4, 0.016)
    stroke(art, T, [(0.19, 0.40), (0.12, 0.50), (0.10, 0.66), (0.12, 0.78)], 2.6, 0.9)
    for k in range(4): stroke(art, T, [(0.12, 0.77), (0.10 + 0.015 * k, 0.84)], 1.4, 0.7, sm=False)


def gemini(art, cx, cy):
    T = mapper(cx, cy)
    person(art, T, 0.32, 0.97, 0.88, 1, 'short', hand=(0.5, 0.47), hand2=(0.19, 0.55))
    person(art, T, 0.68, 0.97, 0.88, -1, 'long', hand=(0.5, 0.47), hand2=(0.81, 0.55))
    q = T([(0.5, 0.47)])[0]; art.star(q, 60, 1.0)
    art.star(T([(0.5, 0.05)])[0], 40, 1.0)
    stroke(art, T, [(0.30, 0.10), (0.5, 0.04), (0.70, 0.10)], 1.4, 0.5)


def cancer(art, cx, cy):
    T = mapper(cx, cy)
    c = (0.5, 0.62)
    for sd in (-1, 1):
        for k in range(4):     # legs
            b = (c[0] + sd * (0.16 + 0.02 * k), c[1] + 0.02 + 0.03 * k)
            kn = (b[0] + sd * (0.12 + 0.02 * k), b[1] - 0.08 + 0.04 * k); tip = (kn[0] + sd * (0.06 + 0.01 * k), 0.97)
            tapered(art, T, [b, kn, tip], 0.014, 0.004, 0.9, 0.3)
        arm0 = (c[0] + sd * 0.17, c[1] - 0.06); el = (c[0] + sd * 0.30, c[1] - 0.18); wr = (c[0] + sd * 0.27, c[1] - 0.34)
        tapered(art, T, [arm0, el, wr], 0.03, 0.022, 1.0, 0.35)
        cl = [(wr[0] - sd * 0.04, wr[1]), (wr[0] - sd * 0.06, wr[1] - 0.08), (wr[0] - sd * 0.02, wr[1] - 0.2), (wr[0] + sd * 0.02, wr[1] - 0.24),
              (wr[0] + sd * 0.01, wr[1] - 0.14), (wr[0] + sd * 0.07, wr[1] - 0.19), (wr[0] + sd * 0.08, wr[1] - 0.08), (wr[0] + sd * 0.04, wr[1] + 0.01)]
        body(art, T, cl, 3.0, 0.38)
        stroke(art, T, [(wr[0] + sd * 0.005, wr[1] - 0.06), (wr[0] + sd * 0.012, wr[1] - 0.13)], 1.4, 0.6)
        stroke(art, T, [(c[0] + sd * 0.05, c[1] - 0.12), (c[0] + sd * 0.07, c[1] - 0.2)], 2.4, 1.0)    # eye stalks
        art.dot(T([(c[0] + sd * 0.07, c[1] - 0.205)])[0], 8, 1.0)
    shell = []
    for t in np.linspace(math.pi, 3 * math.pi, 40):
        r = 1 + (0.06 * math.sin(t * 8) if math.sin(t) < 0.2 else 0)
        shell.append((c[0] + 0.23 * r * math.cos(t), c[1] + 0.14 * r * math.sin(t)))
    body(art, T, shell, 3.4, 0.38)
    stroke(art, T, [(c[0] - 0.14, c[1] - 0.03), (c[0], c[1] - 0.08), (c[0] + 0.14, c[1] - 0.03)], 1.6, 0.6)
    stroke(art, T, [(c[0] - 0.1, c[1] + 0.04), (c[0], c[1] + 0.01), (c[0] + 0.1, c[1] + 0.04)], 1.6, 0.5)
    for sd in (-1, 1): stroke(art, T, spiral((c[0] + sd * 0.09, c[1] - 0.01), 0.04, 0.015, 0, sd * 4, 20), 1.3, 0.45)


def leo(art, cx, cy):
    T = mapper(cx, cy)
    stroke(art, T, [(0.60, 0.62), (0.59, 0.80), (0.60, 0.97)], 2.4, 0.55); stroke(art, T, [(0.27, 0.64), (0.24, 0.82), (0.23, 0.97)], 2.4, 0.55)
    sil = [(0.18, 0.44), (0.30, 0.41), (0.48, 0.42), (0.60, 0.40), (0.68, 0.48), (0.70, 0.62), (0.71, 0.80), (0.73, 0.97), (0.65, 0.97), (0.64, 0.80),
           (0.62, 0.68), (0.55, 0.62), (0.40, 0.63), (0.33, 0.62), (0.35, 0.80), (0.35, 0.97), (0.28, 0.97), (0.27, 0.85), (0.22, 0.74), (0.18, 0.58)]
    body(art, T, sil, 3.2, 0.32)
    for seg in ([(0.28, 0.45), (0.31, 0.55), (0.31, 0.62)], [(0.45, 0.44), (0.47, 0.56)], [(0.66, 0.52), (0.67, 0.62)]):
        stroke(art, T, seg, 1.5, 0.5)
    # mane: flame tufts around the head
    hc = (0.72, 0.30)
    for k in range(22):
        t = -math.pi * 0.95 + k * (math.pi * 1.75 / 21)
        r0, r1 = 0.09, 0.20 + 0.03 * math.sin(k * 1.7)
        b0 = (hc[0] + r0 * math.cos(t - 0.12), hc[1] + r0 * math.sin(t - 0.12)); b1 = (hc[0] + r0 * math.cos(t + 0.12), hc[1] + r0 * math.sin(t + 0.12))
        tip = (hc[0] + r1 * math.cos(t + 0.15), hc[1] + r1 * math.sin(t + 0.15))
        tuft = [b0, ((b0[0] + tip[0]) / 2 + 0.01 * math.cos(t + 1.6), (b0[1] + tip[1]) / 2), tip, ((b1[0] + tip[0]) / 2, (b1[1] + tip[1]) / 2), b1]
        art.fill(T(tuft), 0.3); art.line(T(tuft), 2.2, 0.9)
    face = [(0.70, 0.20), (0.78, 0.21), (0.83, 0.26), (0.85, 0.32), (0.83, 0.37), (0.78, 0.39), (0.72, 0.38), (0.67, 0.32)]
    body(art, T, face, 3.0, 0.38)
    eye(art, T, (0.775, 0.27)); stroke(art, T, [(0.755, 0.26), (0.795, 0.262)], 1.6, 0.9)
    stroke(art, T, [(0.83, 0.31), (0.85, 0.315), (0.84, 0.33)], 2.4, 1.0); stroke(art, T, [(0.84, 0.33), (0.82, 0.355), (0.79, 0.355)], 1.6, 0.8)
    for k in range(3): art.dot(T([(0.805 + 0.012 * k, 0.335)])[0], 2.5, 0.8)
    stroke(art, T, [(0.18, 0.46), (0.10, 0.55), (0.07, 0.42), (0.11, 0.33)], 2.6, 0.9)
    tuft = [(0.11, 0.33), (0.09, 0.28), (0.12, 0.25), (0.14, 0.29)]; art.fill(T(tuft), 0.4); art.line(T(tuft), 2.2, 0.9, closed=True)


def virgo(art, cx, cy):
    T = mapper(cx, cy)
    for sd, ox in ((-1, 0.38),):     # wing behind
        wing = [(0.44, 0.30), (0.30, 0.12), (0.18, 0.06), (0.12, 0.14), (0.16, 0.30), (0.24, 0.42), (0.36, 0.44)]
        body(art, T, wing, 2.6, 0.22)
        for k in range(6): stroke(art, T, [(0.42, 0.32), (0.18 + 0.02 * k, 0.12 + 0.05 * k)], 1.3, 0.5)
    hc = person(art, T, 0.50, 0.97, 0.92, 1, 'long', hand=(0.60, 0.42), hand2=(0.41, 0.56))
    wheat(art, T, (0.58, 0.56), (0.70, 0.12)); wheat(art, T, (0.60, 0.55), (0.76, 0.18)); wheat(art, T, (0.59, 0.56), (0.64, 0.10))
    art.star(T([(0.30, 0.08)])[0], 30, 1.0)


def libra(art, cx, cy):
    T = mapper(cx, cy)
    body(art, T, [(0.40, 0.97), (0.60, 0.97), (0.56, 0.90), (0.44, 0.90)], 3.0, 0.35, sm=False)
    body(art, T, [(0.47, 0.90), (0.53, 0.90), (0.52, 0.22), (0.48, 0.22)], 2.6, 0.35, sm=False)
    for y in (0.40, 0.60, 0.80): stroke(art, T, [(0.465, y), (0.535, y)], 1.6, 0.6, sm=False)
    body(art, T, [(0.5, 0.08), (0.53, 0.14), (0.5, 0.20), (0.47, 0.14)], 2.4, 0.4, sm=False)
    art.star(T([(0.5, 0.06)])[0], 36, 1.0)
    beam = [(0.12, 0.24), (0.5, 0.20), (0.88, 0.24)]
    tapered(art, T, beam, 0.012, 0.012, 1.0, 0.4)
    for sd in (-1, 1):
        stroke(art, T, spiral((0.5 + sd * 0.12, 0.27), 0.035, 0.01, 0, sd * 5, 24), 1.6, 0.7)
        e = (0.5 + sd * 0.38, 0.24); pan_c = (e[0], 0.62)
        for k in (-1, 0, 1): stroke(art, T, [e, (pan_c[0] + k * 0.11, pan_c[1] - 0.01)], 1.4, 0.75, sm=False)
        pan = [(pan_c[0] - 0.13, pan_c[1]), (pan_c[0] - 0.08, pan_c[1] + 0.07), (pan_c[0] + 0.08, pan_c[1] + 0.07), (pan_c[0] + 0.13, pan_c[1])]
        body(art, T, pan, 3.0, 0.4)
        art.dot(T([e])[0], 9, 1.0)


def scorpio(art, cx, cy):
    T = mapper(cx, cy)
    segs = [(0.62, 0.80, 0.07), (0.53, 0.81, 0.075), (0.44, 0.81, 0.07), (0.36, 0.80, 0.06)]
    for sd in (-1, 1):
        for k in range(4):
            b = (0.58 - k * 0.07, 0.83); kn = (b[0] + 0.03 - 0.02 * k, 0.74 if sd < 0 else 0.89); tip = (b[0] + 0.07 - 0.05 * k, 0.97 if sd > 0 else 0.93)
            if sd < 0: kn = (b[0] + 0.05 - 0.03 * k, 0.72); tip = (b[0] + 0.09 - 0.06 * k, 0.95)
            tapered(art, T, [b, kn, tip], 0.009, 0.003, 0.8, 0.3)
    for x, y, r in segs:
        body(art, T, [(x + r * math.cos(t), y + r * 0.65 * math.sin(t)) for t in np.linspace(0, 6.28, 30)], 3.0, 0.36)
    head = [(0.67, 0.78), (0.74, 0.76), (0.76, 0.81), (0.72, 0.85), (0.66, 0.84)]; body(art, T, head, 3.0, 0.38)
    for sd in (-1, 1):
        arm = [(0.73, 0.80), (0.80, 0.80 + sd * 0.06), (0.86, 0.78 + sd * 0.10)]
        tapered(art, T, arm, 0.014, 0.012, 1.0, 0.35)
        pc = (0.86, 0.78 + sd * 0.10)
        claw = [(pc[0] - 0.02, pc[1] - 0.02), (pc[0] + 0.06, pc[1] - 0.04 * sd - 0.02), (pc[0] + 0.11, pc[1] - 0.03 * sd), (pc[0] + 0.06, pc[1] + 0.005 * sd), (pc[0] + 0.1, pc[1] + 0.03 * sd), (pc[0] + 0.03, pc[1] + 0.035 * sd), (pc[0] - 0.02, pc[1] + 0.02)]
        body(art, T, claw, 2.6, 0.38)
    tail = spiral((0.40, 0.42), 0.36, 0.24, math.pi * 0.62, -math.pi * 0.12, 10, 0.75, 1.0)
    for i, (x, y) in enumerate(tail[1:]):
        r = 0.05 - 0.003 * i
        body(art, T, [(x + r * math.cos(t), y + r * 0.8 * math.sin(t)) for t in np.linspace(0, 6.28, 24)], 2.6, 0.36)
    x, y = tail[-1]
    sting = [(x + 0.03, y - 0.03), (x + 0.10, y + 0.02), (x + 0.12, y + 0.10), (x + 0.09, y + 0.05), (x + 0.03, y + 0.04)]
    body(art, T, sting, 2.6, 0.45)
    art.star(T([(x + 0.12, y + 0.10)])[0], 30, 1.0)


def sagittarius(art, cx, cy):
    T = mapper(cx, cy)
    stroke(art, T, [(0.56, 0.63), (0.54, 0.80), (0.55, 0.97)], 2.4, 0.55); stroke(art, T, [(0.22, 0.64), (0.19, 0.82), (0.17, 0.97)], 2.4, 0.55)
    horse = [(0.16, 0.48), (0.28, 0.45), (0.45, 0.46), (0.56, 0.44), (0.62, 0.48), (0.65, 0.58), (0.68, 0.66), (0.74, 0.72), (0.73, 0.80), (0.76, 0.86),
             (0.70, 0.87), (0.67, 0.78), (0.62, 0.70), (0.60, 0.80), (0.61, 0.97), (0.55, 0.97), (0.54, 0.80), (0.52, 0.66), (0.38, 0.67), (0.30, 0.66),
             (0.31, 0.82), (0.30, 0.97), (0.24, 0.97), (0.24, 0.86), (0.20, 0.76), (0.15, 0.62)]
    body(art, T, horse, 3.2, 0.32)
    stroke(art, T, [(0.16, 0.50), (0.08, 0.58), (0.06, 0.72), (0.09, 0.80)], 2.4, 0.8)
    for k in range(4): stroke(art, T, [(0.15, 0.52), (0.06 + 0.01 * k, 0.70 + 0.03 * k)], 1.2, 0.5)
    torso = [(0.56, 0.46), (0.55, 0.32), (0.56, 0.22), (0.60, 0.19), (0.66, 0.20), (0.68, 0.30), (0.66, 0.46)]
    body(art, T, torso, 3.0, 0.34)
    hc = (0.615, 0.12); body(art, T, [(hc[0] + 0.045 * math.cos(t), hc[1] + 0.055 * math.sin(t)) for t in np.linspace(0, 6.28, 30)], 2.6, 0.34)
    body(art, T, [(0.58, 0.10), (0.60, 0.05), (0.65, 0.06), (0.67, 0.10), (0.63, 0.08)], 2.0, 0.3)
    # drawing the bow: front arm out to the bow, back arm pulling the string
    tapered(art, T, [(0.66, 0.22), (0.74, 0.20), (0.82, 0.17)], 0.016, 0.012, 1.0, 0.35)
    tapered(art, T, [(0.57, 0.22), (0.58, 0.16), (0.63, 0.15)], 0.016, 0.012, 1.0, 0.35)
    bow = [(0.80, 0.00), (0.86, 0.08), (0.865, 0.17), (0.84, 0.26), (0.77, 0.33)]
    tapered(art, T, bow, 0.008, 0.008, 1.0, 0.5)
    stroke(art, T, [(0.80, 0.00), (0.63, 0.15), (0.77, 0.33)], 1.2, 0.8, sm=False)
    stroke(art, T, [(0.63, 0.15), (0.97, 0.13)], 2.0, 1.0, sm=False)
    body(art, T, [(0.97, 0.13), (0.93, 0.115), (0.935, 0.145)], 2.0, 0.6)
    art.star(T([(0.98, 0.13)])[0], 34, 1.0)


def capricorn(art, cx, cy):
    T = mapper(cx, cy)
    sil = [(0.58, 0.30), (0.62, 0.20), (0.68, 0.15), (0.74, 0.16), (0.79, 0.22), (0.81, 0.28), (0.77, 0.31), (0.72, 0.31), (0.70, 0.38), (0.68, 0.48),
           (0.66, 0.56), (0.58, 0.64), (0.48, 0.70), (0.38, 0.80), (0.32, 0.90), (0.36, 0.96), (0.46, 0.95), (0.52, 0.88), (0.48, 0.84), (0.40, 0.88),
           (0.42, 0.80), (0.50, 0.74), (0.40, 0.70), (0.30, 0.74), (0.22, 0.84), (0.20, 0.72), (0.26, 0.60), (0.38, 0.50), (0.48, 0.40)]
    body(art, T, sil, 3.2, 0.33)
    fin = [(0.36, 0.96), (0.30, 1.0), (0.28, 0.92), (0.32, 0.90)]
    for k in range(5):     # scales along the tail
        stroke(art, T, [(0.30 + 0.05 * k, 0.62 + 0.02 * k), (0.32 + 0.05 * k, 0.66 + 0.02 * k), (0.30 + 0.05 * k, 0.70 + 0.02 * k)], 1.3, 0.45)
    tailfan = [(0.21, 0.84), (0.10, 0.80), (0.04, 0.88), (0.12, 0.92), (0.06, 0.98), (0.20, 0.95), (0.24, 0.88)]
    body(art, T, tailfan, 2.6, 0.32)
    for k in range(4): stroke(art, T, [(0.22, 0.87), (0.06 + 0.02 * k, 0.82 + 0.05 * k)], 1.2, 0.5)
    # front legs folded
    tapered(art, T, [(0.64, 0.50), (0.74, 0.58), (0.72, 0.68), (0.78, 0.70)], 0.022, 0.012, 1.0, 0.35)
    tapered(art, T, [(0.60, 0.55), (0.66, 0.66), (0.62, 0.74), (0.68, 0.77)], 0.02, 0.011, 0.8, 0.3)
    eye(art, T, (0.735, 0.21)); stroke(art, T, [(0.78, 0.245), (0.79, 0.255)], 2, 0.9, sm=False)
    beard = [(0.74, 0.31), (0.72, 0.38), (0.70, 0.43), (0.73, 0.36)]; body(art, T, beard, 2.0, 0.35)
    stroke(art, T, [(0.66, 0.20), (0.58, 0.22), (0.63, 0.25)], 2.2, 0.9)
    P = tapered(art, T, [(0.68, 0.15), (0.62, 0.06), (0.52, 0.02), (0.42, 0.04), (0.36, 0.10)], 0.022, 0.005); ring_marks(art, T, P, 9, 0.022)
    P = tapered(art, T, [(0.71, 0.15), (0.67, 0.08), (0.58, 0.05), (0.50, 0.08)], 0.016, 0.004, 0.8); ring_marks(art, T, P, 6, 0.016, 0.4)
    for k in range(3): stroke(art, T, spiral((0.30 + 0.12 * k, 0.99), 0.03, 0.01, 0, 4, 16), 1.2, 0.4)


def aquarius(art, cx, cy):
    T = mapper(cx, cy)
    hc = person(art, T, 0.42, 0.90, 0.86, 1, 'long', hand=(0.56, 0.20), hand2=(0.62, 0.36))
    jar = [(0.56, 0.18), (0.60, 0.13), (0.66, 0.14), (0.70, 0.20), (0.74, 0.24), (0.76, 0.30), (0.72, 0.38), (0.64, 0.38), (0.58, 0.32)]
    body(art, T, jar, 3.0, 0.4)
    stroke(art, T, [(0.60, 0.22), (0.72, 0.22)], 1.4, 0.6); stroke(art, T, [(0.59, 0.30), (0.74, 0.30)], 1.4, 0.6)
    for k in range(4):
        stroke(art, T, [(0.75, 0.27 + 0.01 * k), (0.82 + 0.01 * k, 0.40), (0.84 + 0.02 * k, 0.62), (0.80 + 0.03 * k, 0.86)], 2.2 - 0.3 * k, 0.9 - 0.12 * k)
    for k in range(9):
        x0 = 0.04 + k * 0.11
        stroke(art, T, [(x0, 0.95), (x0 + 0.03, 0.92), (x0 + 0.06, 0.93), (x0 + 0.07, 0.96), (x0 + 0.055, 0.975)], 1.6, 0.7)
    art.fill(T([(0.0, 0.95), (1.0, 0.95), (1.0, 0.99), (0.0, 0.99)]), 0.15, sm=False)
    for k in range(10):
        p = (0.82 + 0.03 * math.sin(k), 0.45 + 0.05 * k); art.dot(T([p])[0], 4, 0.8)


def pisces(art, cx, cy):
    T = mapper(cx, cy)
    c = (0.5, 0.55)
    stroke(art, T, [(c[0] + 0.32 * math.cos(t), c[1] + 0.32 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 120)], 1.4, 0.4)
    R1 = fish(art, T, (0.36, 0.33), 0.5, math.pi + 0.35, 1)
    R2 = fish(art, T, (0.64, 0.77), 0.5, 0.35, 1)
    stroke(art, T, [R1(-0.6, 0), (0.12, 0.55), (0.30, 0.80), R2(-0.6, 0)], 1.8, 0.8)
    stroke(art, T, [R2(-0.6, 0), (0.88, 0.55), (0.70, 0.30), R1(-0.6, 0)], 1.8, 0.8)
    art.star(T([c])[0], 46, 1.0)
    for k in range(12):
        t = k / 12 * 2 * math.pi; art.dot(T([(c[0] + 0.32 * math.cos(t), c[1] + 0.32 * math.sin(t))])[0], 4, 0.7)


CREATURES = dict(aries=aries, taurus=taurus, gemini=gemini, cancer=cancer, leo=leo, virgo=virgo, libra=libra, scorpio=scorpio,
                 sagittarius=sagittarius, capricorn=capricorn, aquarius=aquarius, pisces=pisces)
