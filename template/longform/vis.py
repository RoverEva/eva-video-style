"""Story inserts for long-form cards: glowing line-art vignettes that grow on the beat.

Each card may name a visual: "{book}…", "{tears@face}…". A visual = static strokes (revealed one per half-eighth,
with a travelling spark at the tip) + an optional dynamic layer (rain falls, pages flip, bubbles pop on quarters…).
Coordinates are unit space (x right, y down, about -1..1) scaled by `S` pixels around a screen point.
"""
import math
import numpy as np
from engine.core import cl, ramp, eo, eio, lerp, pulse, pop, flame, spline

TAU = 2 * math.pi


def arc(cx, cy, rx, ry, a0, a1, n=28): return [(cx + rx * math.cos(q), cy + ry * math.sin(q)) for q in np.linspace(a0, a1, n)]
def circ(cx, cy, r, n=40): return arc(cx, cy, r, r, 0, TAU, n)
def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
def rrect(x0, y0, x1, y1, r):
    p = []
    for cx, cy, a in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        p += arc(cx, cy, r, r, a, a + math.pi / 2, 6)
    return p + [p[0]]
def heart_pts(cx=0, cy=0, s=1.0, n=60):
    return [(cx + s * 0.06 * 16 * math.sin(q) ** 3, cy - s * 0.06 * (13 * math.cos(q) - 5 * math.cos(2 * q) - 2 * math.cos(3 * q) - math.cos(4 * q)))
            for q in np.linspace(0, TAU, n)]
def drop(cx, cy, s): return [(cx, cy - s)] + arc(cx, cy + 0.35 * s, 0.55 * s, 0.6 * s, -0.25 * math.pi, 1.25 * math.pi, 18)[::-1] + [(cx, cy - s)]
def star_pts(cx, cy, r, r2=0.42):
    return [(cx + (r if k % 2 == 0 else r * r2) * math.sin(k * math.pi / 5), cy - (r if k % 2 == 0 else r * r2) * math.cos(k * math.pi / 5)) for k in range(11)]
def person(x, y, s):   # head + shoulders, feet at y
    return [circ(x, y - 1.55 * s, 0.28 * s, 18), [(x - 0.55 * s, y), (x - 0.5 * s, y - 0.7 * s), (x - 0.25 * s, y - 1.1 * s), (x + 0.25 * s, y - 1.1 * s), (x + 0.5 * s, y - 0.7 * s), (x + 0.55 * s, y)]]


# ---------------------------------------------------------------- static stroke sets: list of (pts, colour key, thickness)
def _book():
    L = [(-0.02, -0.45), (-0.4, -0.58), (-0.92, -0.5), (-0.92, 0.5), (-0.4, 0.42), (-0.02, 0.55)]
    R = [(-x, y) for x, y in L]
    s = [(L, 'S', 2.4), (R, 'S', 2.4), ([(0, -0.45), (0, 0.55)], 'G', 2)]
    for k in range(4):
        y = -0.3 + k * 0.18; s += [([(-0.8, y), (-0.15, y + 0.05)], 'L', 1.4), ([(0.15, y + 0.05), (0.8, y)], 'L', 1.4)]
    return s
def _phone(): return [(rrect(-0.48, -0.95, 0.48, 0.95, 0.12), 'S', 2.4), ([(-0.12, -0.84), (0.12, -0.84)], 'L', 2), (circ(0, 0.83, 0.05, 10), 'L', 1.6)]
def _clock():
    s = [(circ(0, 0, 0.85, 60), 'S', 2.4), (circ(0, 0, 0.92, 60), 'L', 1.2)]
    for k in range(12):
        q = k * TAU / 12; r0 = 0.7 if k % 3 else 0.62
        s.append(([(r0 * math.sin(q), -r0 * math.cos(q)), (0.8 * math.sin(q), -0.8 * math.cos(q))], 'G' if k % 3 == 0 else 'L', 1.6))
    return s
def _cloud():
    c = arc(-0.45, 0.0, 0.3, 0.28, math.pi * 0.5, math.pi * 1.5, 12) + arc(-0.1, -0.25, 0.4, 0.38, math.pi, math.pi * 1.95, 14) + \
        arc(0.42, -0.02, 0.33, 0.3, math.pi * 1.3, math.pi * 2.5, 14)
    return [(c + [c[0]], 'S', 2.4)]
def _heart(): return [(heart_pts(0, 0.05, 1.0), 'G', 2.6)]
def _broken():
    zz = [(0, -0.45), (-0.08, -0.2), (0.07, 0.02), (-0.06, 0.25), (0, 0.6)]
    return [(heart_pts(0, 0.05, 1.0)[:31], 'S', 2.4), (heart_pts(0, 0.05, 1.0)[30:], 'S', 2.4), (zz, 'W', 2)]
def _gift():
    return [(rect(-0.62, -0.1, 0.62, 0.8), 'S', 2.4), ([(0, -0.1), (0, 0.8)], 'G', 2.2), ([(-0.62, 0.25), (0.62, 0.25)], 'G', 1.6)]
def _cup():
    return [([(-0.55, -0.2), (-0.45, 0.55), (-0.25, 0.7), (0.25, 0.7), (0.45, 0.55), (0.55, -0.2), (-0.55, -0.2)], 'S', 2.4),
            (arc(0.62, 0.15, 0.2, 0.22, -math.pi / 2, math.pi / 2, 12), 'S', 2.2), (arc(0, 0.82, 0.85, 0.1, 0, math.pi, 20), 'L', 1.6)]
def _letter():
    return [(rect(-0.85, -0.5, 0.85, 0.55), 'S', 2.4), ([(-0.85, -0.5), (0, 0.12), (0.85, -0.5)], 'S', 2), ([(-0.85, 0.55), (-0.2, 0.0)], 'L', 1.2), ([(0.85, 0.55), (0.2, 0.0)], 'L', 1.2)]
def _lock(): return [(rrect(-0.55, -0.05, 0.55, 0.85, 0.08), 'S', 2.4), (circ(0, 0.32, 0.09, 12), 'G', 2), ([(0, 0.4), (0, 0.6)], 'G', 2)]
def _key():
    return [(circ(-0.5, 0, 0.3, 30), 'G', 2.4), ([(-0.2, 0), (0.85, 0)], 'G', 2.4), ([(0.55, 0), (0.55, 0.22)], 'G', 2.2), ([(0.75, 0), (0.75, 0.18)], 'G', 2.2)]
def _door(): return [(rect(-0.5, -0.9, 0.5, 0.9), 'S', 2.6), ([(-0.95, 0.9), (0.95, 0.9)], 'L', 1.6)]
def _mountain():
    return [([(-1.0, 0.8), (-0.35, -0.2), (-0.1, 0.15), (0.3, -0.75), (1.0, 0.8)], 'S', 2.4), ([(0.18, -0.48), (0.3, -0.4), (0.42, -0.5)], 'L', 1.6),
            ([(0.3, -0.75), (0.3, -1.15)], 'G', 2)]
def _coins():
    s = []
    for k in range(3):
        y = 0.7 - k * 0.22; s += [(arc(-0.3, y, 0.42, 0.13, 0, TAU, 30), 'G', 2), ([(-0.72, y), (-0.72, y + 0.1)], 'G', 1.6), ([(0.12, y), (0.12, y + 0.1)], 'G', 1.6)]
    return s
def _moon():
    o = arc(0, 0, 0.7, 0.7, math.radians(60), math.radians(300), 40); i = arc(0.28, 0, 0.56, 0.6, math.radians(285), math.radians(75), 40)
    return [(o + i + [o[0]], 'S', 2.4), (star_pts(0.75, -0.6, 0.12), 'G', 1.6), (star_pts(-0.85, 0.5, 0.08), 'G', 1.4)]
def _mask():
    a = arc(-0.32, 0, 0.42, 0.55, 0, TAU, 40); b = arc(0.32, 0.05, 0.42, 0.55, 0, TAU, 40)
    return [(a, 'G', 2.4), (b, 'S', 2.4), (arc(-0.32, 0.12, 0.2, 0.12, 0.1, math.pi - 0.1, 12), 'G', 2), (arc(0.32, 0.36, 0.2, 0.12, math.pi + 0.1, TAU - 0.1, 12), 'S', 2),
            ([(-0.46, -0.12), (-0.36, -0.15)], 'G', 2), ([(-0.28, -0.15), (-0.18, -0.12)], 'G', 2), ([(0.18, -0.06), (0.28, -0.1)], 'S', 2), ([(0.36, -0.1), (0.46, -0.06)], 'S', 2)]
def _mirror(): return [(arc(0, -0.15, 0.55, 0.75, 0, TAU, 50), 'G', 2.6), (arc(0, -0.15, 0.47, 0.67, 0, TAU, 50), 'L', 1.2), ([(0, 0.6), (0, 0.9)], 'S', 2), ([(-0.35, 0.92), (0.35, 0.92)], 'S', 2)]
def _road(): return [([(-1.0, 0.9), (-0.06, -0.55)], 'S', 2.4), ([(1.0, 0.9), (0.06, -0.55)], 'S', 2.4), ([(-1.2, -0.55), (1.2, -0.55)], 'L', 1.2)]
def _question(): return [([(-0.38, -0.42), (-0.3, -0.72), (0.0, -0.85), (0.32, -0.72), (0.38, -0.42), (0.18, -0.18), (0.0, 0.0), (0.0, 0.3)], 'G', 3.2), (circ(0, 0.6, 0.07, 12), 'G', 3)]
def _star(): return [(star_pts(0, 0, 0.8), 'G', 2.6)]
def _scales():
    return [([(0, -0.8), (0, 0.8)], 'S', 2.4), ([(-0.45, 0.8), (0.45, 0.8)], 'S', 2.4), (circ(0, -0.85, 0.06, 10), 'G', 2)]
def _compass():
    s = [(circ(0, 0, 0.85, 60), 'S', 2.4)]
    for k in range(4):
        q = k * math.pi / 2; s.append(([(0.68 * math.sin(q), -0.68 * math.cos(q)), (0.85 * math.sin(q), -0.85 * math.cos(q))], 'G', 2))
    return s
def _eye():
    return [(arc(0, 0.55, 1.0, 0.9, math.radians(213), math.radians(327), 30) + arc(0, -0.55, 1.0, 0.9, math.radians(33), math.radians(147), 30), 'S', 2.4), (circ(0, 0, 0.28, 30), 'G', 2.2)]
def _thought():
    c = []
    for k in range(7):
        q = k * TAU / 7; c += arc(0.6 * math.cos(q), -0.15 + 0.4 * math.sin(q), 0.25, 0.22, q - 1.2, q + 1.2, 8)
    return [(c + [c[0]], 'S', 2.2), (circ(-0.55, 0.55, 0.1, 12), 'S', 2), (circ(-0.75, 0.8, 0.06, 10), 'S', 1.8)]
def _target():
    return [(circ(0, 0, r, 50), 'S' if i % 2 else 'G', 2.2) for i, r in enumerate((0.85, 0.6, 0.35, 0.1))]
def _shield(): return [([(0, -0.85), (0.7, -0.6), (0.62, 0.2), (0, 0.9), (-0.62, 0.2), (-0.7, -0.6), (0, -0.85)], 'S', 2.6), ([(-0.28, 0.02), (-0.06, 0.25), (0.32, -0.25)], 'G', 2.6)]
def _chain():
    return [(arc(-0.65, 0, 0.32, 0.18, 0, TAU, 24), 'S', 2.4), (arc(0.65, 0, 0.32, 0.18, 0, TAU, 24), 'S', 2.4)]
def _crown(): return [([(-0.75, 0.45), (-0.8, -0.35), (-0.4, 0.05), (0, -0.6), (0.4, 0.05), (0.8, -0.35), (0.75, 0.45), (-0.75, 0.45)], 'G', 2.6), ([(-0.75, 0.62), (0.75, 0.62)], 'G', 2)]
def _feather():
    sp = [(-0.5, 0.8), (-0.1, 0.1), (0.25, -0.5), (0.45, -0.85)]
    s = [(sp, 'S', 2.2)]
    for k in range(1, 9):
        u = k / 9; p = (lerp(-0.4, 0.42, u), lerp(0.62, -0.8, u)); w = 0.35 * math.sin(u * math.pi)
        s += [([p, (p[0] - w, p[1] - 0.1)], 'L', 1.4), ([p, (p[0] + w * 0.8, p[1] + 0.12)], 'L', 1.4)]
    return s
def _umbrella():
    c = arc(0, 0, 0.9, 0.6, math.pi, TAU, 30)
    sc = []
    for k in range(4): sc += arc(-0.675 + k * 0.45, 0, 0.225, 0.12, 0, -math.pi, 8)[::-1][::-1]
    return [(c, 'G', 2.6), ([(0.9, 0), (-0.9, 0)], 'G', 1.6), ([(0, 0), (0, 0.8)] + arc(0.12, 0.8, 0.12, 0.12, math.pi, 0, 8), 'S', 2.2)]
def _hourglass():
    return [([(-0.5, -0.85), (0.5, -0.85), (0.06, 0), (0.5, 0.85), (-0.5, 0.85), (-0.06, 0), (-0.5, -0.85)], 'S', 2.4), ([(-0.6, -0.9), (0.6, -0.9)], 'G', 2.2), ([(-0.6, 0.9), (0.6, 0.9)], 'G', 2.2)]
def _rings(): return [(circ(-0.28, 0.1, 0.48, 40), 'G', 2.6), (circ(0.28, 0.1, 0.48, 40), 'S', 2.6), (star_pts(-0.28, -0.42, 0.1), 'W', 1.6)]
def _pen():
    return [(rect(-0.75, -0.85, 0.55, 0.85), 'S', 2.2), ([(0.9, -0.9), (0.2, 0.3), (0.12, 0.48), (0.28, 0.36), (0.98, -0.82), (0.9, -0.9)], 'G', 2.2)]
def _wall():
    s = []
    for r in range(5):
        y = 0.8 - r * 0.32; s.append(([(-0.9, y), (0.9, y)], 'S', 1.8))
        for k in range(5): x = -0.9 + (k + (0.5 if r % 2 else 0)) * 0.4; s.append(([(min(x, 0.9), y), (min(x, 0.9), y - 0.32)], 'L', 1.4)) if x < 0.9 else None
    s.append(([(-0.9, -0.8), (0.9, -0.8)], 'S', 1.8)); return s
def _gem(): return [([(-0.6, -0.3), (-0.3, -0.65), (0.3, -0.65), (0.6, -0.3), (0, 0.75), (-0.6, -0.3)], 'G', 2.4), ([(-0.6, -0.3), (0.6, -0.3)], 'S', 1.6), ([(-0.3, -0.65), (-0.15, -0.3), (0, 0.75)], 'S', 1.4), ([(0.3, -0.65), (0.15, -0.3), (0, 0.75)], 'S', 1.4)]
def _calendar():
    s = [(rect(-0.75, -0.65, 0.75, 0.8), 'S', 2.4), ([(-0.75, -0.35), (0.75, -0.35)], 'S', 2), ([(-0.4, -0.8), (-0.4, -0.5)], 'G', 2), ([(0.4, -0.8), (0.4, -0.5)], 'G', 2)]
    for r in range(3):
        for c in range(4): s.append((rect(-0.6 + c * 0.32, -0.2 + r * 0.32, -0.42 + c * 0.32, -0.04 + r * 0.32), 'L', 1.2))
    return s
def _bolt(): return [([(0.15, -0.95), (-0.35, 0.05), (0.02, 0.05), (-0.18, 0.95), (0.42, -0.2), (0.05, -0.2), (0.3, -0.95), (0.15, -0.95)], 'G', 2.6)]
def _waves(): return []
def _sprout(): return [([(-0.8, 0.8), (0.8, 0.8)], 'S', 2)]
def _stairs():
    p = [(-0.95, 0.85)]
    for k in range(5): p += [(p[-1][0], p[-1][1] - 0.3), (p[-1][0] + 0.38, p[-1][1] - 0.3)]
    return [(p, 'S', 2.4)]
def _spark(): return [(circ(0, 0, 0.12, 12), 'G', 2.4)]
def _eyeclosed(): return []
def _bubble(): return [(rrect(-0.85, -0.55, 0.85, 0.4, 0.25) [:-1] + [(-0.4, 0.4), (-0.6, 0.75), (-0.2, 0.4)], 'S', 2.4)]
def _plane(): return [([(-0.8, 0.1), (0.85, -0.45), (-0.2, 0.25), (-0.8, 0.1)], 'G', 2.4), ([(0.85, -0.45), (-0.05, 0.55), (-0.2, 0.25)], 'G', 2.2)]
def _seesaw(): return []
def _none(): return []

STATIC = dict(book=_book, phone=_phone, clock=_clock, rain=_cloud, heart=_heart, broken=_broken, gift=_gift, cup=_cup, letter=_letter, lock=_lock,
              key=_key, door=_door, mountain=_mountain, coins=_coins, moon=_moon, mask=_mask, mirror=_mirror, road=_road, question=_question,
              star=_star, scales=_scales, compass=_compass, eye=_eye, thought=_thought, target=_target, shield=_shield, chain=_chain, crown=_crown,
              feather=_feather, umbrella=_umbrella, hourglass=_hourglass, rings=_rings, pen=_pen, wall=_wall, gem=_gem, calendar=_calendar,
              bolt=_bolt, waves=_waves, sprout=_sprout, stairs=_stairs, spark=_spark, bubble=_bubble, plane=_plane,
              people2=_none, alone=_none, crowd=_none, flame=_none, fireworks=_none, sun=_none,
              tears=_none, blush=_none, think=_none, sigh=_none, smile=_none, sweat=_none)

FACE = {'tears', 'blush', 'think', 'sigh', 'smile', 'sweat'}          # drawn on the hero's face (close-up)
SCENE = {'people2', 'alone', 'crowd', 'road', 'mountain', 'stairs', 'waves', 'rain', 'fireworks', 'sun'}   # full-frame scenes


# ---------------------------------------------------------------- dynamic layers
class Ctx:
    def __init__(s, sc, cv, P, x, y, S, a, t, t0, t1, E8, quarter):
        s.sc, s.cv, s.P, s.x, s.y, s.S, s.a, s.t, s.t0, s.t1, s.E8, s.q = sc, cv, P, x, y, S, a, t, t0, t1, E8, quarter
        s.age = t - t0; s.u = cl((t - t0) / max(0.1, t1 - t0))
    def X(s, pts): return [(s.x + s.S * px, s.y + s.S * py) for px, py in pts]
    def col(s, k): return {'S': s.P.SOFT, 'G': s.P.GOLD, 'W': s.P.WARM, 'L': s.P.LINE}[k]
    def path(s, pts, k='S', a=1.0, th=2.0, frac=1.0, smooth=True, glow=False):
        s.cv.path(s.X(pts), s.col(k), s.a * a, th, frac, smooth=smooth)
        if glow: s.cv.path(s.X(pts), s.col(k), s.a * a * 0.35, th * 5, frac, smooth=smooth, layer=s.cv.F)
    def glow(s, p, r, k='G', a=1.0): s.cv.glow(s.X([p])[0], r * s.S, s.col(k), s.a * a)
    def dot(s, p, r, k='W', a=1.0): s.cv.circle(s.X([p])[0], r * s.S, s.col(k), s.a * a, fill=True)
    def beats(s):   # quarter-note hits since the card started
        return int(max(0, (s.t - s.t0) / (2 * s.E8)))


def d_book(c):
    k = c.beats(); ph = cl(((c.t - c.t0) / (2 * c.E8)) - k)
    if c.age > 0.6:   # a page flips on every quarter
        e = eio(ph); xe = math.cos(e * math.pi) * 0.85
        c.path([(0, -0.45), (xe * 0.5, -0.62 + 0.1 * abs(xe)), (xe, -0.5 + 0.02)], 'G', 0.9 * (1 - abs(e - 0.5) * 0.6), 1.8)
        c.path([(0, 0.55), (xe * 0.5, 0.45 + 0.05 * abs(xe)), (xe, 0.5)], 'G', 0.5, 1.4)
    for j in range(5):   # motes rising from the pages
        v = (c.age * 0.4 + j * 0.2) % 1
        c.dot((-0.5 + j * 0.25 + 0.1 * math.sin(c.t * 2 + j), -0.6 - v * 0.9), 0.02, 'W', (1 - v) * cl(c.age * 2))
    c.glow((0, -0.1), 0.6, 'G', 0.35)


def d_phone(c):
    for k in range(min(c.beats() + 1, 5)):
        tb = c.t0 + 0.3 + k * 2 * c.E8; g = eo(cl((c.t - tb) * 5))
        if g <= 0: continue
        side = 1 if k % 2 else -1; y = 0.55 - (min(c.beats(), 4) - k) * 0.32 - 0.1
        x0, x1 = (0.05, 0.42) if side > 0 else (-0.42, -0.05)
        sc = pop(c.t, tb, 0.15)
        cx = (x0 + x1) / 2; w = (x1 - x0) / 2 * sc
        if y < -0.75: continue
        c.path(rrect(cx - w, y - 0.11, cx + w, y + 0.11, 0.06), 'G' if side > 0 else 'S', g, 1.8, smooth=False)
        c.glow((cx, y), 0.18, 'G', 0.3 * pulse(c.t, tb, 0.3))


def d_clock(c):
    m = c.t * 1.6; h = c.t * 0.13
    c.path([(0, 0), (0.62 * math.sin(m), -0.62 * math.cos(m))], 'G', 1, 2.2, smooth=False, glow=True)
    c.path([(0, 0), (0.4 * math.sin(h), -0.4 * math.cos(h))], 'S', 1, 2.6, smooth=False)
    c.dot((0, 0), 0.04, 'W')


def d_rain(c):
    for j in range(16):
        v = (c.t * 1.4 + j * 0.37) % 1; x = -0.75 + (j * 0.61) % 1.5
        c.path([(x, 0.35 + v * 1.3), (x - 0.04, 0.47 + v * 1.3)], 'L', 0.8 * (1 - v) * cl(c.age * 2), 1.6, smooth=False)


def d_heart(c):
    s = 1 + 0.08 * pulse(c.t, c.q, 0.25) + 0.05 * pulse(c.t, c.q + c.E8, 0.2)
    c.path(heart_pts(0, 0.05, s), 'G', cl(c.age * 2) * 0.6, 4, smooth=False, glow=True)
    c.glow((0, 0), 0.7 * s, 'G', 0.25 + 0.3 * pulse(c.t, c.q, 0.3))


def d_broken(c):
    sp = 0.12 * eo(cl((c.age - 0.8) / 1.0))
    if sp > 0:
        H = heart_pts(0, 0.05, 1.0)
        c.path([(x - sp, y + sp * 0.4) for x, y in H[:31]], 'S', 0.6, 1.6); c.path([(x + sp, y + sp * 0.4) for x, y in H[30:]], 'S', 0.6, 1.6)
        for j in range(5):
            v = cl((c.age - 0.8) * 0.7 - j * 0.1); c.dot((0.05 * math.sin(j * 3), 0.2 + v * 0.9), 0.02, 'W', (1 - v) * 0.9)


def d_gift(c):
    lift = eo(cl((c.age - 0.6) / 0.5))
    dy = -0.45 * lift; rot = 0.25 * lift
    lid = [(-0.7, -0.35), (0.7, -0.35), (0.7, -0.1), (-0.7, -0.1), (-0.7, -0.35)]
    lid = [(x * math.cos(rot) - y * math.sin(rot) + 0.15 * lift, x * math.sin(rot) + y * math.cos(rot) + dy) for x, y in lid]
    c.path(lid, 'G', 1, 2.4, smooth=False)
    c.path([(-0.15, -0.35 + dy), (-0.35, -0.6 + dy), (0, -0.4 + dy), (0.35, -0.6 + dy), (0.15, -0.35 + dy)], 'W', 1 - lift, 2)
    if lift > 0:
        for k in range(9):
            q = -math.pi / 2 + (k - 4) * 0.22
            c.path([(0, -0.15), (1.3 * math.cos(q) * lift, -0.15 + 1.3 * math.sin(q) * lift)], 'G', 0.5 * lift, 1.4, smooth=False, glow=True)


def d_cup(c):
    for j in range(3):
        x0 = -0.2 + j * 0.2; ph = c.t * 2 + j
        pts = [(x0 + 0.06 * math.sin(ph + v * 6), -0.3 - v * 0.75) for v in np.linspace(0, 1, 12)]
        c.path(pts, 'L', 0.7 * cl(c.age * 1.5), 1.6, frac=cl(c.age))


def d_letter(c):
    g = pop(c.t, c.t0 + 0.9, 0.2)
    if c.age > 0.9: c.path(heart_pts(0, 0.12, 0.28 * g), 'W', 1, 2.2, smooth=False); c.glow((0, 0.1), 0.3, 'G', 0.5 * pulse(c.t, c.t0 + 0.9, 0.5))
    for j in range(4):
        v = (c.age * 0.5 + j * 0.25) % 1; c.dot((0.9 + v * 0.3, -0.6 - v * 0.4 + 0.1 * j), 0.02, 'G', (1 - v) * cl(c.age - 0.9))


def d_lock(c):
    op = eo(cl((c.age - 1.2) / 0.35))
    sh = arc(0, -0.05 - 0.3 * op, 0.36, 0.45, math.pi, TAU, 20)
    c.path([(-0.36, -0.05)] + sh + [(0.36, -0.05 - 0.3 * op)], 'S', 1, 2.6, smooth=False)
    if op > 0: c.glow((0, 0.3), 0.6, 'G', 0.6 * pulse(c.t, c.t0 + 1.2, 0.5))


def d_key(c): c.glow((-0.5, 0), 0.4, 'G', 0.2 + 0.3 * pulse(c.t, c.q, 0.3))


def d_door(c):
    op = eo(cl((c.age - 0.5) / 0.8)); xe = 0.5 - 0.85 * op
    c.path([(-0.5, -0.9), (xe, -0.82), (xe, 0.84), (-0.5, 0.9)], 'G', 1, 2.2, smooth=False)
    if op > 0:
        c.glow((0.1, 0), 0.9, 'G', 0.7 * op)
        for k in range(7): c.path([(0.15 * op, -0.6 + k * 0.2), (1.4, -0.9 + k * 0.3)], 'W', 0.25 * op, 1.2, smooth=False, glow=True)


def d_mountain(c):
    w = math.sin(c.t * 5)
    c.path([(0.3, -1.15), (0.55, -1.08 + 0.04 * w), (0.75, -1.12 - 0.03 * w), (0.68, -0.98), (0.45, -0.95 + 0.03 * w), (0.3, -0.98)], 'W', cl(c.age - 0.6), 2, smooth=False)
    # tiny climber walking up
    u = cl(c.age / max(1, c.t1 - c.t0)); p = (lerp(-0.85, 0.22, u), lerp(0.7, -0.68, u))
    c.dot((p[0], p[1] - 0.06), 0.035, 'W'); c.glow(p, 0.12, 'G', 0.6)


def d_coins(c):
    for k in range(min(c.beats(), 3)):
        tb = c.t0 + (k + 1) * 2 * c.E8; y = 0.04 - k * 0.22; f = eo(cl((c.t - tb) / 0.18))
        yy = lerp(-1.4, y, f)
        c.path(arc(-0.3, yy, 0.42, 0.13, 0, TAU, 30), 'G', 1, 2, smooth=False); c.glow((-0.3, y), 0.3, 'G', 0.5 * pulse(c.t, tb + 0.18, 0.3))
    for j in range(3):
        v = (c.age * 0.5 + j / 3) % 1; c.dot((0.5 + 0.1 * j, -0.2 - v * 0.6), 0.025, 'W', 0.7 * (1 - v))


def d_moon(c):
    for j in range(3):
        v = (c.age * 0.35 + j / 3) % 1; s = 0.08 + 0.06 * v; x, y = 0.55 + v * 0.5, -0.1 - v * 0.8
        c.path([(x - s, y - s), (x + s, y - s), (x - s, y + s), (x + s, y + s)], 'L', (1 - v) * cl(c.age), 1.6, smooth=False)
    c.glow((0, 0), 0.7, 'S', 0.25)


def d_mask(c):
    sw = 0.5 + 0.5 * math.sin(c.t * 1.6)
    c.glow((-0.32, 0), 0.5, 'G', 0.4 * sw); c.glow((0.32, 0), 0.5, 'S', 0.4 * (1 - sw))


def d_mirror(c):
    u = ((c.t - c.t0) * 0.6) % 1.6 - 0.3
    c.path([(-0.4 + u, -0.7), (-0.1 + u, 0.3)], 'W', 0.5 * cl(c.age - 0.5) * (1 - abs(u - 0.5)), 3, smooth=False, glow=True)


def d_road(c):
    for k in range(min(c.beats() + 1, 8)):
        tb = c.t0 + k * 2 * c.E8; v = k / 8; y = 0.8 - v * 1.25; sx = 1 - v * 0.9
        side = -1 if k % 2 else 1; p = (0.08 * side * sx, y)
        c.path(arc(p[0], p[1], 0.05 * sx, 0.08 * sx, 0, TAU, 10), 'G', pop(c.t, tb, 0.15), 1.8, smooth=False)
    c.glow((0, -0.55), 0.35, 'G', 0.5 + 0.3 * pulse(c.t, c.q, 0.3))


def d_question(c):
    c.glow((0, -0.3), 0.8, 'G', 0.3 + 0.5 * pulse(c.t, c.t0, 0.5))


def d_star(c):
    r = 0.9 + 0.3 * pulse(c.t, c.q, 0.3)
    for k in range(8):
        q = k * math.pi / 4 + c.t * 0.3; c.path([(0.9 * math.cos(q), 0.9 * math.sin(q)), (r * 1.2 * math.cos(q), r * 1.2 * math.sin(q))], 'W', 0.7, 1.4, smooth=False)
    c.glow((0, 0), 0.8, 'G', 0.4)


def d_scales(c):
    tilt = 0.18 * math.sin(c.t * 1.3) * (1 - cl((c.age - 2.5) / 1.5))
    for side in (-1, 1):
        x = 0.85 * side; y = -0.62 + tilt * side
        c.path([(0, -0.62), (x, y)], 'S', 1, 2.2, smooth=False)
        c.path([(x, y), (x - 0.28, y + 0.55), (x + 0.28, y + 0.55), (x, y)], 'L', 0.8, 1.4, smooth=False)
        c.path(arc(x, y + 0.55, 0.3, 0.1, 0, math.pi, 12), 'G', 1, 2, smooth=False)


def d_compass(c):
    q = 0.9 * math.sin(c.age * 3) * math.exp(-c.age * 0.6)
    c.path([(0.55 * math.sin(q), -0.55 * math.cos(q)), (-0.55 * math.sin(q), 0.55 * math.cos(q))], 'G', 1, 2.6, smooth=False, glow=True)


def d_eye(c):
    bl = pulse(c.t, c.t0 + 1.5, 0.25)
    c.dot((0, 0), 0.12 * (1 - bl), 'W'); c.glow((0, 0), 0.5, 'G', 0.4)


def d_thought(c):
    for d in range(3): c.dot((-0.3 + d * 0.3, -0.15), 0.06, 'G', 0.4 + 0.6 * pulse(c.t, c.q + d * c.E8 * 0.6, 0.3))


def d_target(c):
    f = eo(cl((c.age - 0.6) / 0.25)); x = lerp(-2.2, 0, f)
    c.path([(x - 0.9, -0.35 * (1 - f) - 0.0), (x, 0)], 'W', cl(c.age - 0.5), 2.4, smooth=False, glow=True)
    if f >= 1: c.glow((0, 0), 0.5, 'G', 0.8 * pulse(c.t, c.t0 + 0.85, 0.5))


def d_shield(c): c.glow((0, 0), 0.7, 'G', 0.25 + 0.4 * pulse(c.t, c.q, 0.3))


def d_chain(c):
    br = eo(cl((c.age - 1.0) / 0.3)); dx = 0.15 * br
    c.path(arc(-0.12 - dx, 0, 0.32, 0.18, 0.3 if br else 0, TAU - (0.3 if br else 0), 24), 'G', 1, 2.4)
    c.path(arc(0.12 + dx, 0, 0.32, 0.18, math.pi + (0.3 if br else 0), math.pi + TAU - (0.3 if br else 0), 24), 'G', 1, 2.4)
    if br: c.glow((0, 0), 0.4, 'W', pulse(c.t, c.t0 + 1.0, 0.4))


def d_crown(c):
    for x, y in ((-0.8, -0.35), (0, -0.6), (0.8, -0.35)): c.dot((x, y - 0.05), 0.05, 'W'); c.glow((x, y), 0.15, 'G', 0.5 + 0.5 * pulse(c.t, c.q, 0.3))


def d_feather(c): pass


def d_umbrella(c):
    for j in range(14):
        v = (c.t * 1.2 + j * 0.41) % 1; x = -1.2 + (j * 0.53) % 2.4
        if abs(x) < 0.95 and v > 0.3: continue
        c.path([(x, -1.1 + v * 2), (x - 0.03, -1.0 + v * 2)], 'L', 0.7 * (1 - v), 1.4, smooth=False)


def d_hourglass(c):
    u = c.u; top = 0.75 * (1 - u); bot = 0.75 * u
    c.path([(-0.42 * (1 - u * 0.8), -0.75 + (1 - top / 0.75) * 0.7), (0.42 * (1 - u * 0.8), -0.75 + (1 - top / 0.75) * 0.7)], 'G', 0.9, 2, smooth=False)
    c.path([(0, 0), (0, 0.8)], 'G', 0.5, 1.2, smooth=False)
    c.path([(-0.42 * u, 0.82), (0, 0.82 - 0.35 * bot), (0.42 * u, 0.82)], 'G', 0.9, 2, smooth=False)


def d_rings(c): c.glow((0, 0.1), 0.7, 'G', 0.3 + 0.4 * pulse(c.t, c.q, 0.3))


def d_pen(c):
    for r in range(5):
        f = cl((c.age - 0.4) * 1.2 - r * 0.6)
        if f > 0: c.path([(-0.6, -0.6 + r * 0.25), (-0.6 + 0.95 * f, -0.6 + r * 0.25 + 0.02 * math.sin(f * 20))], 'G', 0.9, 1.6)


def d_wall(c):
    cr = eo(cl((c.age - 1.2) / 0.4))
    if cr > 0:
        c.path([(0.1, -0.8), (0.0, -0.4), (0.15, -0.1), (-0.05, 0.3), (0.08, 0.8)], 'W', 1, 2.2, frac=cr, smooth=False)
        c.glow((0.05, 0), 0.6, 'G', 0.6 * cr)


def d_gem(c):
    for k in range(4):
        q = c.t * 0.8 + k * math.pi / 2; c.dot((0.75 * math.cos(q), -0.1 + 0.75 * math.sin(q)), 0.025, 'W', 0.8)
    c.glow((0, 0), 0.6, 'G', 0.4 + 0.3 * pulse(c.t, c.q, 0.3))


def d_calendar(c):
    for k in range(min(c.beats() + 1, 12)):
        r, col = divmod(k, 4); x, y = -0.51 + col * 0.32, -0.12 + r * 0.32
        c.path([(x - 0.06, y), (x - 0.01, y + 0.05), (x + 0.07, y - 0.06)], 'G', pop(c.t, c.t0 + k * 2 * c.E8, 0.15), 2, smooth=False)


def d_bolt(c): c.glow((0, 0), 0.9, 'W', 0.9 * pulse(c.t, c.q, 0.25) + 0.2)


def d_waves(c):
    for k in range(4):
        y = -0.4 + k * 0.35; ph = c.t * (1.2 + 0.3 * k) + k
        c.path([(x, y + 0.08 * math.sin(x * 4 + ph)) for x in np.linspace(-1.3, 1.3, 40)], 'S' if k % 2 else 'G', cl(c.age * 2 - k * 0.3), 2, smooth=False)


def d_sprout(c):
    g = eo(cl((c.age - 0.2) / 1.6)); top = 0.8 - 1.2 * g
    c.path([(0, 0.8), (0.06, 0.4), (-0.04, 0.1), (0, top)], 'G', 1, 2.4, frac=g)
    for k, (yy, sd) in enumerate(((0.35, -1), (0.0, 1), (-0.3, -1))):
        f = eo(cl((c.age - 0.6 - k * 0.4) / 0.5))
        if f > 0 and top < yy:
            c.path([(0, yy), (sd * 0.2 * f, yy - 0.18 * f), (sd * 0.45 * f, yy - 0.12 * f), (sd * 0.22 * f, yy + 0.02), (0, yy)], 'S', 1, 2)
    c.glow((0, top), 0.25, 'G', 0.6 * g)


def d_stairs(c):
    u = cl(c.age / max(1.0, (c.t1 - c.t0) * 0.9)); k = u * 5; i = int(min(k, 4.99)); f = k - i
    x = -0.95 + 0.38 * i + 0.38 * f; y = 0.85 - 0.3 * (i + (1 if f > 0.5 else 0)) - 0.12
    c.dot((x + 0.19, y - 0.05), 0.05, 'W'); c.glow((x + 0.19, y), 0.18, 'G', 0.8)
    c.path(star_pts(0.95, -0.95, 0.12), 'G', cl(u * 3), 1.8, smooth=False)


def d_spark(c):
    nb = c.beats()
    for k in range(max(0, nb - 2), nb + 1):
        tb = c.t0 + k * 2 * c.E8; g = eo(cl((c.t - tb) / 0.4)); fa = 1 - cl((c.t - tb - 0.3) / 0.8)
        if fa <= 0: continue
        cx, cy = ((-0.5, -0.3), (0.5, -0.5), (0, 0.1), (-0.6, 0.35), (0.6, 0.2))[k % 5]
        for j in range(12):
            q = j * TAU / 12; c.path([(cx + 0.15 * g * math.cos(q), cy + 0.15 * g * math.sin(q)), (cx + 0.45 * g * math.cos(q), cy + 0.45 * g * math.sin(q))], 'G' if j % 2 else 'W', fa, 1.8, smooth=False, glow=True)


def d_bubble(c):
    for d in range(3): c.dot((-0.35 + d * 0.35, -0.07), 0.07, 'G', 0.4 + 0.6 * pulse(c.t, c.q + d * c.E8 * 0.6, 0.3))


def d_plane(c):
    u = (c.age * 0.25) % 1
    pts = [(lerp(-1.6, 1.6, v), -0.2 + 0.4 * math.sin(v * 5)) for v in np.linspace(0, u, 30)]
    if len(pts) > 1: c.path(pts, 'L', 0.5, 1.2, smooth=False)


def d_feather_scene(c): pass


def d_people(c, kind):
    sc, P = c.sc, c.P
    if kind == 'people2':
        g = eo(cl(c.age * 2))
        for side in (-1, 1):
            x = side * lerp(0.9, 0.45, g)
            for p in person(x, 0.8, 0.55): c.path(p, 'S' if side < 0 else 'G', 1, 2.2, smooth=False)
        if c.age > 0.7:
            s = pop(c.t, c.t0 + 0.7, 0.2) * (1 + 0.08 * pulse(c.t, c.q, 0.25))
            c.path(heart_pts(0, -0.45, 0.35 * s), 'W', 1, 2.2, smooth=False, glow=True)
    elif kind == 'alone':
        for k in range(5):
            for p in person(-1.4 + k * 0.32, 0.8, 0.42): c.path(p, 'L', 0.55, 1.6, smooth=False)
        for p in person(1.0, 0.8, 0.5): c.path(p, 'G', 1, 2.2, smooth=False)
        c.path([(1.0, -1.4), (0.6, 0.85), (1.4, 0.85), (1.0, -1.4)], 'W', 0.08, 1, smooth=False)
        c.glow((1.0, 0.3), 0.6, 'G', 0.25 + 0.2 * pulse(c.t, c.q, 0.4))
    elif kind == 'crowd':
        for k in range(9):
            x = -1.6 + k * 0.4; tb = c.t0 + (abs(k - 4)) * c.E8; on = pop(c.t, tb, 0.15)
            for p in person(x, 0.85, 0.4 if k != 4 else 0.55): c.path(p, 'G' if k == 4 else 'S', on, 2 if k == 4 else 1.6, smooth=False)
            c.glow((x, 0.3), 0.25, 'G', 0.6 * pulse(c.t, tb, 0.4))


def d_flame(c):
    for k, (x, h) in enumerate(((-0.55, 0.5), (0, 0.9), (0.55, 0.6))):
        on = c.t > c.t0 + k * c.E8
        if not on: continue
        hh = h * (1 + 0.1 * math.sin(c.t * 8 + k)) * pop(c.t, c.t0 + k * c.E8, 0.18)
        X, Y = c.X([(x, 0.8)])[0]
        flame(c.cv, X, Y, hh * c.S, c.P.GOLD, c.a); flame(c.cv, X, Y, hh * c.S * 1.6, c.P.GOLD, 0.3 * c.a, layer=c.cv.F)


def d_sun(c):
    g = eo(cl(c.age / 1.2)); y = lerp(0.8, -0.1, g)
    c.path(arc(0, y, 0.55, 0.55, math.pi, TAU, 30), 'G', 1, 2.6, smooth=False, glow=True)
    for k in range(11):
        q = math.pi + k * math.pi / 10; r1 = 0.7 + 0.08 * pulse(c.t, c.q, 0.3)
        c.path([(0.65 * math.cos(q), y + 0.65 * math.sin(q)), (r1 * 1.4 * math.cos(q), y + r1 * 1.4 * math.sin(q))], 'W', g, 1.6, smooth=False)
    c.path([(-1.6, 0.8), (1.6, 0.8)], 'S', 1, 2, smooth=False)


DYN = dict(book=d_book, phone=d_phone, clock=d_clock, rain=d_rain, heart=d_heart, broken=d_broken, gift=d_gift, cup=d_cup, letter=d_letter,
           lock=d_lock, key=d_key, door=d_door, mountain=d_mountain, coins=d_coins, moon=d_moon, mask=d_mask, mirror=d_mirror, road=d_road,
           question=d_question, star=d_star, scales=d_scales, compass=d_compass, eye=d_eye, thought=d_thought, target=d_target, shield=d_shield,
           chain=d_chain, crown=d_crown, umbrella=d_umbrella, hourglass=d_hourglass, rings=d_rings, pen=d_pen, wall=d_wall, gem=d_gem,
           calendar=d_calendar, bolt=d_bolt, waves=d_waves, sprout=d_sprout, stairs=d_stairs, spark=d_spark, bubble=d_bubble, plane=d_plane,
           people2=lambda c: d_people(c, 'people2'), alone=lambda c: d_people(c, 'alone'), crowd=lambda c: d_people(c, 'crowd'),
           flame=d_flame, fireworks=d_spark, sun=d_sun)
_CACHE = {}


def draw_vis(sc, cv, name, t, t0, t1, x, y, S, a):
    """draw visual `name` for a card shown t0..t1 at screen point (x,y), scale S px (canvas must use a screen camera)"""
    if a <= 0.01 or name not in STATIC: return
    a = a * (1 - ramp(t, t1 - 0.25, t1 + 0.05))
    if a <= 0.01: return
    E8 = sc.E8; P = sc.P
    if name not in _CACHE: _CACHE[name] = STATIC[name]()
    strokes = _CACHE[name]
    S = S * (0.82 + 0.18 * eo(cl((t - t0) / 0.35))) * (1 + 0.025 * pulse(t, sc.quarter(t), 0.3))
    c = Ctx(sc, cv, P, x, y, S, a, t, t0, t1, E8, sc.quarter(t))
    nst = max(1, len(strokes)); step = min(E8 * 0.5, 1.4 / nst)
    for k, (pts, ck, th) in enumerate(strokes):
        ts = t0 + k * step; f = eio(cl((t - ts) / (E8 * 1.4)))
        if f <= 0: continue
        P_ = c.X(pts); col = c.col(ck)
        sc.hero.tpath(cv, P_, col, a, th, f, smooth=False)
        cv.path(P_, col, a * 0.3, th * 4, f, smooth=False, layer=cv.F)
    # landing flash on the card's first beat
    cv.glow((x, y), S * 0.9, P.GOLD, 0.35 * a * pulse(t, t0, 0.35))
    f = DYN.get(name)
    if f: f(c)


def draw_face_fx(sc, cv, name, t, t0, t1, a):
    """effects on the hero's face, in hero-local coordinates (cv.cam must be the hero SubCam)"""
    P = sc.P; E8 = sc.E8
    a = a * (1 - ramp(t, t1 - 0.25, t1 + 0.05))
    if a <= 0.01: return
    age = t - t0
    if name == 'tears':
        for side, ex in ((0, 943), (1, 977)):
            for j in range(3):
                period = 2 * E8 * 2; ph = ((age - 0.4 - side * E8 - j * period / 3) % period) / period if age > 0.4 + side * E8 else -1
                if ph < 0: continue
                yy = 258 + ph * 120 + 40 * ph * ph; xx = ex + (side * 2 - 1) * (4 + 6 * ph)
                cv.poly(spline(drop(xx, yy, 6), n=4, closed=True), P.WARM, a * (1 - ph) * 1.2); cv.glow((xx, yy), 10, P.GOLD, 0.6 * a * (1 - ph))
            cv.path([(ex - 3, 256), (ex - 5, 275)], P.WARM, a * 0.6 * cl(age - 0.3), 1.4, smooth=False)
    elif name in ('blush', 'smile'):
        for ex in (932, 988): cv.glow((ex, 272), 16, P.GOLD, a * (0.5 + 0.3 * pulse(t, sc.quarter(t), 0.4)))
        if name == 'smile':
            for k in range(6):
                q = k * math.pi / 3 + t * 0.6; cv.circle((960 + 120 * math.cos(q), 250 + 100 * math.sin(q)), 2.2, P.WARM, a * 0.8, fill=True)
    elif name == 'think':
        for d in range(3):
            p = (1010 + d * 26, 190 - d * 30); cv.circle(p, 5 + d * 3, P.GOLD, a * (0.4 + 0.6 * pulse(t, sc.quarter(t) + d * E8 * 0.5, 0.3)), 2)
    elif name == 'sigh':
        for j in range(3):
            v = ((age * 0.5) + j / 3) % 1
            cv.path([(975 + v * 80, 290 - v * 20 + 6 * math.sin(v * 9 + k)) for k in range(1)] + [(990 + v * 90, 285 - v * 25)], P.LINE, a * (1 - v) * 0.7, 1.4, smooth=False)
    elif name == 'sweat':
        v = cl(age / 1.2); cv.poly(spline(drop(1000, 215 + v * 30, 7), n=4, closed=True), P.SOFT, a * (1 - v * 0.5))
