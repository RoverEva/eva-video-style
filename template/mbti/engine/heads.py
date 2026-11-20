"""Faces and hairstyles for the hero — every type gets its own look.

look = {"hair": ..., "eyes": ..., "brows": ..., "mouth": ..., "acc": [...]}
hair : hood long_straight long_wavy curly swept tousled side_part spiky crew bun pompadour ponytail headband bob faux_hawk braid
eyes : closed open smile sharp
brows: none soft angled raised straight
mouth: calm smile line grin smirk
acc  : circlet crown star_clip flower glasses earrings beard
Head centre is about (960, 250); the face spans x 924-996, y 198-302.
"""
import math
import numpy as np
from .core import mir

CX, CY = 960, 250
HAIRS = ['hood', 'long_straight', 'long_wavy', 'curly', 'swept', 'tousled', 'side_part', 'spiky', 'crew', 'bun',
         'pompadour', 'ponytail', 'headband', 'bob', 'faux_hawk', 'braid']

HOOD = [(905, 330), (892, 270), (898, 205), (925, 168), (960, 158), (995, 168), (1022, 205), (1028, 270), (1015, 330)]
FACE = [(960, 198), (990, 215), (996, 255), (982, 292), (960, 302), (938, 292), (924, 255), (930, 215)]
JAW = [(924, 238), (926, 268), (940, 293), (960, 303), (980, 293), (994, 268), (996, 238)]
SKULL = [(924, 250), (926, 214), (940, 192), (960, 184), (980, 192), (994, 214), (996, 250)]


def arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(q), cy + ry * math.sin(q)) for q in np.linspace(a0, a1, n)]


def draw_head(sc, cv, look, a, k, kf):
    """k: outline growth 0..1 (with tip dots), kf: face-detail fade 0..1"""
    P = sc.P; S, L, G = P.SOFT, P.LINE, P.GOLD
    tp = sc.tpath
    hair = look.get('hair', 'hood')
    acc = set(look.get('acc', []))
    if hair == 'hood':
        tp(cv, HOOD, S, a, 2.4, k); tp(cv, FACE, S, a * 0.9, 1.8, k, closed=True)
    else:
        tp(cv, JAW, S, a * 0.9, 1.8, k)
        short = hair in ('crew', 'side_part', 'swept', 'tousled', 'spiky', 'headband', 'faux_hawk', 'pompadour', 'curly', 'bun', 'ponytail')
        if short and kf > 0:   # ears
            for sx in (-1, 1):
                cv.path([(CX + sx * 36, 240), (CX + sx * 44, 246), (CX + sx * 43, 264), (CX + sx * 35, 270)], S, a * 0.7 * kf, 1.5)
        _hair(sc, cv, hair, a, k, kf)
    if kf <= 0: return
    a2 = a * kf
    _brows(cv, look.get('brows', 'none'), S, a2)
    _eyes(cv, look.get('eyes', 'closed'), S, P.WARM, a2)
    cv.path([(960, 252), (957, 272), (963, 274)], S, a2 * 0.7, 1.4, smooth=False)       # nose
    _mouth(cv, look.get('mouth', 'calm'), S, a2)
    cv.path([(942, 298), (938, 345)], S, a2 * .8, 1.8, smooth=False); cv.path([(978, 298), (982, 345)], S, a2 * .8, 1.8, smooth=False)  # neck
    _acc(sc, cv, acc, a2, G, P.WARM, S)


def _hair(sc, cv, hair, a, k, kf):
    P = sc.P; S, L, G = P.SOFT, P.LINE, P.GOLD; tp = sc.tpath
    def strands(lines, al=0.5, w=1.2):
        for ln in lines:
            if len(ln) > 1: cv.path(ln, L, a * al * kf, w)
    if hair in ('long_straight', 'long_wavy', 'braid'):
        wav = (lambda y: 7 * math.sin(y / 14)) if hair == 'long_wavy' else (lambda y: 0)
        outer = [(904 + wav(380), 382), (906 + wav(330), 330), (910 + wav(280), 280), (914, 228), (932, 190), (960, 176), (988, 190), (1006, 228)]
        if hair == 'braid':
            outer += [(1010, 262), (1004, 296)]
        else:
            outer += [(1010 - wav(280), 280), (1014 - wav(330), 330), (1016 - wav(380), 382)]
        tp(cv, outer, S, a, 2.3, k)
        inner_l = [(960, 186), (942, 196), (928, 222), (922, 262), (918, 310), (916, 370)]
        tp(cv, inner_l, S, a * 0.8, 1.8, k)
        if hair != 'braid': tp(cv, mir(inner_l), S, a * 0.8, 1.8, k)
        cv.path([(960, 177), (956, 200)], S, a * 0.8 * kf, 1.4)       # parting
        strands([[(912 + wav(y), y) for y in range(250, 380, 26)], [(1008 - wav(y), y) for y in range(250, 380, 26)] if hair != 'braid' else []], 0.4)
        if hair == 'braid':     # side braid hanging over the right shoulder
            for i in range(6):
                y = 270 + i * 22
                cv.circle((1006 + 3 * math.sin(i), y), 11, S, a * 0.85 * kf, 1.6)
            cv.path([(1006, 400), (1000, 418)], S, a * kf, 1.6); cv.path([(1006, 400), (1014, 418)], S, a * kf, 1.6)
    elif hair == 'curly':
        for i, q in enumerate(np.linspace(math.radians(170), math.radians(370), 14)):
            x, y = CX + 52 * math.cos(q), 238 + 58 * math.sin(q)
            if y > 262: continue
            if i / 14 <= k: cv.circle((x, y), 15, S, a, 2)
        for x, y in ((952, 204), (972, 206), (938, 216)):
            cv.circle((x, y), 7, L, a * 0.6 * kf, 1.4)
    elif hair == 'swept':
        tp(cv, [(922, 252), (918, 212), (934, 180), (962, 168), (994, 176), (1006, 206), (1000, 252)], S, a, 2.3, k)
        tp(cv, [(928, 216), (944, 206), (962, 204), (980, 207), (994, 214)], S, a * 0.7, 1.6, k)    # hairline
        strands([[(940, 206), (954, 186), (978, 176)], [(956, 204), (972, 184), (996, 184)], [(974, 206), (990, 192), (1004, 200)]], 0.6)
    elif hair == 'tousled':
        pts = [(922, 250), (916, 214), (928, 200), (922, 186), (944, 182), (946, 166), (966, 176), (984, 162), (990, 182), (1008, 184), (1000, 204), (1006, 222), (998, 250)]
        tp(cv, pts, S, a, 2.2, k)
        strands([[(934, 214), (948, 200), (944, 226)], [(958, 210), (968, 194), (976, 222)], [(980, 214), (994, 204), (990, 226)]], 0.6)
    elif hair == 'side_part':
        tp(cv, [(922, 252), (918, 214), (932, 188), (960, 176), (990, 184), (1004, 210), (1000, 252)], S, a, 2.3, k)
        tp(cv, [(944, 182), (950, 196), (968, 206), (990, 212), (1000, 226)], S, a * 0.85, 1.8, k)   # fringe sweep
        strands([[(944, 182), (928, 206), (924, 230)], [(960, 190), (982, 196), (998, 214)]], 0.5)
    elif hair == 'spiky':
        pts = []
        for i, q in enumerate(np.linspace(math.radians(185), math.radians(355), 15)):
            r = 74 if i % 2 else 50
            pts.append((CX + r * math.cos(q) * 1.0, 248 + r * math.sin(q) * 1.05))
        tp(cv, [(924, 252)] + pts + [(996, 252)], S, a, 2.2, k, smooth=False)
    elif hair in ('crew', 'headband', 'faux_hawk'):
        cap = [(924, 246), (924, 208), (938, 190), (960, 184), (982, 190), (996, 208), (996, 246)]
        if hair == 'faux_hawk':
            tp(cv, cap, S, a * 0.7, 1.8, k)
            tp(cv, [(942, 196), (944, 170), (952, 176), (956, 146), (964, 168), (972, 150), (976, 174), (980, 196)], S, a, 2.2, k, smooth=False)
        else:
            tp(cv, cap, S, a, 2.2, k)
            for x in range(932, 992, 9):
                y = 196 if 940 < x < 980 else 204
                cv.path([(x, y), (x + 3, y - 7)], L, a * 0.5 * kf, 1.1, smooth=False)
        if hair == 'headband':
            for dy in (0, 13):
                cv.path(arc(CX, 300 + dy, 76, 92, math.radians(232), math.radians(308)), sc.P.GOLD, a * kf, 2)
            cv.path([(1004, 236), (1030, 254), (1040, 282)], G, a * kf, 1.8); cv.path([(1004, 242), (1022, 270), (1024, 298)], G, a * kf, 1.8)
    elif hair == 'bun':
        tp(cv, [(924, 250), (922, 212), (936, 190), (960, 182), (984, 190), (998, 212), (996, 250)], S, a, 2.2, k)
        tp(cv, [(928, 224), (944, 204), (960, 198), (976, 204), (992, 224)], S, a * 0.6, 1.5, k)
        if k > 0.7:
            cv.circle((960, 160), 22, S, a, 2.2); cv.path(arc(960, 160, 14, 14, 3.4, 5.6), L, a * 0.6, 1.3)
    elif hair == 'pompadour':
        tp(cv, [(924, 246), (920, 206), (932, 172), (962, 150), (996, 158), (1008, 188), (998, 246)], S, a, 2.3, k)
        strands([[(932, 204), (946, 172), (976, 158)], [(946, 206), (962, 176), (992, 166)], [(962, 206), (980, 182), (1002, 182)]], 0.6)
    elif hair == 'ponytail':
        tp(cv, [(924, 250), (920, 212), (936, 188), (962, 180), (988, 188), (1000, 206), (998, 250)], S, a, 2.2, k)
        tp(cv, [(930, 220), (950, 204), (976, 202), (996, 212)], S, a * 0.6, 1.5, k)
        if k > 0.6:
            cv.circle((1000, 202), 6, sc.P.GOLD, a, 2)
            for off in (-7, 7):
                cv.path([(1004, 202 + off), (1040, 226 + off), (1052, 290 + off * 0.6), (1036, 360)], S, a * 0.9, 2)
    elif hair == 'bob':
        tp(cv, [(918, 306), (912, 252), (918, 210), (936, 186), (960, 178), (984, 186), (1002, 210), (1008, 252), (1002, 306)], S, a, 2.3, k)
        tp(cv, [(926, 226), (944, 222), (960, 224), (976, 222), (994, 226)], S, a * 0.85, 1.8, k)    # straight fringe
        cv.path([(918, 306), (936, 300)], S, a * kf, 1.8, smooth=False); cv.path([(1002, 306), (984, 300)], S, a * kf, 1.8, smooth=False)
        strands([[(924, 236), (920, 290)], [(996, 236), (1000, 290)]], 0.45)


def _eyes(cv, kind, S, Wm, a):
    for ex in (943, 977):
        if kind == 'closed':
            cv.path([(ex - 10, 246), (ex, 250), (ex + 10, 246)], S, a, 1.6)
        elif kind == 'smile':
            cv.path([(ex - 10, 250), (ex, 243), (ex + 10, 250)], S, a, 1.7)
        elif kind == 'sharp':
            s = -1 if ex < 960 else 1
            cv.path([(ex - 11, 248 - 2 * s), (ex, 244), (ex + 11, 248 + 2 * s)], S, a, 1.8)
            cv.path([(ex - 9, 249), (ex + 9, 250)], S, a * 0.6, 1.2)
            cv.circle((ex, 247), 2.6, Wm, a, fill=True)
        else:  # open
            cv.path([(ex - 11, 248), (ex - 4, 242), (ex + 4, 242), (ex + 11, 248)], S, a, 1.6)
            cv.path([(ex - 9, 250), (ex, 253), (ex + 9, 250)], S, a * 0.6, 1.2)
            cv.circle((ex, 247), 3, Wm, a, fill=True)


def _brows(cv, kind, S, a):
    if kind == 'none': return
    for ex in (943, 977):
        s = -1 if ex < 960 else 1
        if kind == 'soft':     pts = [(ex - 11, 234), (ex, 230), (ex + 11, 233)]
        elif kind == 'angled': pts = [(ex - 12 * s, 229), (ex, 232), (ex + 10 * s, 236)]
        elif kind == 'straight': pts = [(ex - 11, 233), (ex + 11, 233)]
        else:                  pts = [(ex - 11, 232 - (6 if s > 0 else 0)), (ex, 227 - (6 if s > 0 else 0)), (ex + 11, 231 - (6 if s > 0 else 0))]
        cv.path(pts, S, a * 0.85, 1.7)


def _mouth(cv, kind, S, a):
    if kind == 'smile':   cv.path([(948, 283), (960, 290), (972, 283)], S, a * 0.9, 1.6)
    elif kind == 'line':  cv.path([(950, 287), (970, 287)], S, a * 0.85, 1.6, smooth=False)
    elif kind == 'grin':
        cv.path([(946, 282), (974, 282)], S, a * 0.9, 1.5, smooth=False); cv.path([(946, 282), (960, 294), (974, 282)], S, a * 0.9, 1.6)
    elif kind == 'smirk': cv.path([(950, 288), (962, 288), (972, 282)], S, a * 0.9, 1.6)
    else:                 cv.path([(951, 286), (960, 289), (969, 286)], S, a * 0.8, 1.4)


def _acc(sc, cv, acc, a, G, Wm, S):
    if 'circlet' in acc:
        cv.path(arc(CX, 300, 74, 92, math.radians(234), math.radians(306)), G, a, 2)
        cv.circle((960, 212), 4, Wm, a, fill=True); sc_glow(cv, (960, 212), 12, G, 0.6 * a)
    if 'crown' in acc:
        pts = [(932, 190), (938, 160), (950, 176), (960, 150), (970, 176), (982, 160), (988, 190)]
        cv.path(pts + [(932, 190)], G, a, 2, smooth=False)
        for p in ((938, 160), (960, 150), (982, 160)): cv.circle(p, 3, Wm, a, fill=True)
    if 'star_clip' in acc:
        x, y = 994, 204; pts = []
        for i in range(10):
            r = 11 if i % 2 == 0 else 4.5; q = -math.pi / 2 + i * math.pi / 5
            pts.append((x + r * math.cos(q), y + r * math.sin(q)))
        cv.path(pts + [pts[0]], G, a, 1.6, smooth=False); sc_glow(cv, (x, y), 14, G, 0.5 * a)
    if 'flower' in acc:
        x, y = 996, 210
        for i in range(5):
            q = i * 2 * math.pi / 5; cv.circle((x + 7 * math.cos(q), y + 7 * math.sin(q)), 5, G, a, 1.4)
        cv.circle((x, y), 3, Wm, a, fill=True)
    if 'glasses' in acc:
        for ex in (943, 977): cv.circle((ex, 248), 14, S, a, 1.6)
        cv.path([(957, 246), (963, 246)], S, a, 1.4, smooth=False)
        cv.path([(929, 246), (922, 242)], S, a, 1.4, smooth=False); cv.path([(991, 246), (998, 242)], S, a, 1.4, smooth=False)
    if 'earrings' in acc:
        for x in (920, 1000): cv.circle((x, 278), 4, G, a, fill=True); cv.path([(x, 272), (x, 278)], G, a, 1.2, smooth=False)
    if 'beard' in acc:
        cv.path([(928, 262), (934, 292), (950, 310), (960, 314), (970, 310), (986, 292), (992, 262)], S, a * 0.85, 1.8)
        cv.path([(946, 280), (954, 278), (960, 280), (966, 278), (974, 280)], S, a * 0.8, 1.6)


def sc_glow(cv, c, r, col, a): cv.glow(c, r, col, a)
