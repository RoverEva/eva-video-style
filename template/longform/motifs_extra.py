"""Extra shot motifs shared by every subject (first written for Taurus) + a few new ones.
install(L) registers them into long_aries.MOTIFS."""
import math, types
import numpy as np
import first_minute as FM
from first_minute_v4 import inst, pose, mix, mirror, run_cycle, walk_cycle, heart_live, sparks_live, burst, ground, T, E8, stars_live
from engine.core import W, H, F, SERIF_B, SERIF_BL, lerp, cl, ramp, eo, eio, pulse, pop
from story_frames import figure, glint, godrays, sp, solid, lamp, window, BLACK, phone_big
L = None


def roots(cv, P, c, k, a=0.8, seed=1):
    rr = np.random.default_rng(seed)
    for b in range(5):
        p = np.array(c, float); seg = [tuple(p)]; ang = math.pi / 2 + rr.uniform(-0.9, 0.9)
        for _ in range(8):
            ang += rr.uniform(-0.35, 0.35); p = p + np.array([math.cos(ang), math.sin(ang)]) * rr.uniform(16, 30); seg.append(tuple(p))
        cv.path(seg, P.SOFT, a, 1.6, frac=k, smooth=False)


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


def m_bubble(C, sh, tx):
    if '很少' in ''.join(C.lines):
        cv = sh.cv; P = C.P; ground(cv, 940, P, 0.5)
        L.Y(cv, C, 1250, 940, 500, 'argue', -1)
        L.A(cv, C, 620, 940, 520, pose('hero', mouth='flat', brow='calm'))
        for k in range(3):
            if C.lt > 0.4 + k * 0.4: L.bubble(cv, tx, sh.cam, (1120 - k * 10, 330 - k * 70), 260, 90, '', P, 0.8, (1, 1))
        if C.lt > 1.8: L.bubble(cv, tx, sh.cam, (760, 400), 140, 90, '…', P, 1.0, (-1, 1), True, 50)
        return 'L2'
    return _ORIG['bubble'](C, sh, tx)


def m_phone(C, sh, tx):
    if '舍不得删' in ''.join(C.lines):
        cv = sh.cv; P = C.P
        L.A(cv, C, 520, 1080 + 700 * 0.5, 1100, pose('hero', mouth='smile', brow='sad', uaF=70, faF=160, hF='open', head=14))
        msgs = [('2019 · 晚安', 1, 260, 'sent'), ('2020 · 生日快乐', -1, 340, 'sent'), ('2021 · 下雨带伞', 1, 420, 'sent')]
        if C.lt > 1.4: msgs.append(('删除聊天记录？', 1, 520, 'deleted' if C.lt > 2.6 else 'typing'))
        phone_big(cv, tx, 1040, 560, 380, 680, P, msgs)
        with inst(cv): cv.glow((1040, 560), 380, P.SOFT, 0.18)
        return 'T'
    return _ORIG['phone'](C, sh, tx)




def m_book(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    L.A(cv, C, 520, 960, 540, pose('hero', mouth='smile', brow='calm', uaF=55, faF=95, hF='open'))
    c = (1150, 600)
    left = [(c[0], c[1] + 40), (c[0] - 300, c[1] + 10), (c[0] - 300, c[1] - 200), (c[0], c[1] - 170)]
    right = [(c[0], c[1] + 40), (c[0] + 300, c[1] + 10), (c[0] + 300, c[1] - 200), (c[0], c[1] - 170)]
    solid(cv, left, P.SOFT, 1, 2.4, 0.04); solid(cv, right, P.SOFT, 1, 2.4, 0.04)
    for k in range(5): cv.path([(c[0] - 270, c[1] - 150 + k * 32), (c[0] - 30, c[1] - 130 + k * 32)], P.LINE, 0.3, 1, smooth=False)
    with inst(cv):
        for j in range(3):
            u = ((C.lt * 0.7) + j / 3) % 1; ang = math.pi * eio(u)
            tip = (c[0] + 300 * math.cos(ang), c[1] - 200 + 30 * math.sin(ang) - 60 * math.sin(ang))
            cv.path([(c[0], c[1] - 170), tip, (tip[0], tip[1] + 210), (c[0], c[1] + 40)], P.SOFT, 0.6 * (1 - abs(u - 0.5)), 1.6, smooth=False)
        sparks_live(cv, (c[0], c[1] - 180), C.t, 20, 10, 300, P, 0.6, 3, (-math.pi * 0.9, -math.pi * 0.1), 0.4, 1.4)
    return 'T'


def m_mask(C, sh, tx):
    cv = sh.cv; P = C.P
    J = L.A(cv, C, 760, 1080 + 1500 * 0.55, 1500, pose('hero', mouth='sad', brow='sad', head=6, uaF=95, faF=170, hF='open'), heart=0)
    k = eio(ramp(C.lt, 0.4, 1.4)) * (1 - eio(ramp(C.lt, C.dur * 0.6, C.dur * 0.6 + 0.8)))
    hc = np.array(J['head']); mc = hc + np.array([lerp(260, 40, k), lerp(160, 0, k)])
    mk = [tuple(mc + np.array([120 * math.cos(q) * 0.8, 150 * math.sin(q)])) for q in np.linspace(0, 2 * math.pi, 40)]
    cv.poly(mk, BLACK, 1.0); cv.poly(mk, P.SOFT * 0.08, 1); cv.path(mk, P.GOLD, 1, 3, smooth=False)
    for sd in (-1, 1): cv.path([tuple(mc + np.array([sd * 40 - 18, -30])), tuple(mc + np.array([sd * 40, -40])), tuple(mc + np.array([sd * 40 + 18, -30]))], P.GOLD, 1, 2.4)
    cv.path([tuple(mc + np.array([-50, 50])), tuple(mc + np.array([0, 80])), tuple(mc + np.array([50, 50]))], P.GOLD, 1, 3)
    return 'R'


def m_wave(C, sh, tx):
    cv = sh.cv; P = C.P
    with inst(cv):
        for k in range(4):
            yy = 760 + k * 50; amp = 30 + 20 * math.sin(C.t + k)
            cv.path([(x, yy + amp * math.sin(x / (160 + 30 * k) + C.t * (1.4 - 0.2 * k))) for x in np.linspace(-200, W + 200, 80)], P.LINE, 0.8 - 0.15 * k, 2.2 - 0.3 * k, smooth=False)
        stars_live(cv, P, C.t, 120, 600, 7, 0.6)
        cv.circle((1500, 220), 50, P.SOFT, 0.9, fill=True); cv.glow((1500, 220), 160, P.SOFT, 0.4)
        for j in range(8): cv.path([(1500 - 60 + j * 4, 760 + j * 20), (1500 + 60 - j * 4, 760 + j * 20)], P.SOFT, 0.5 - j * 0.05, 2, smooth=False)
    L.A(cv, C, 700, 780 + 8 * math.sin(C.t * 1.5), 420, pose('hero', mouth='flat', brow='calm', wind=(-0.6, 0.0)))
    return 'L2'


def m_star(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    with inst(cv):
        stars_live(cv, P, C.t, 220, 800, 5 + C.idx % 4, 0.7)
        k = ramp(C.lt, 0.6, 1.6)
        if 0 < k < 1:
            p = (lerp(1700, 900, k), lerp(100, 360, k)); cv.path([p, (p[0] + 300, p[1] - 100)], P.WARM, 1 - k * 0.5, 3, smooth=False); glint(cv, p, 30, P.WARM, 1)
        if k >= 1: glint(cv, (900, 360), 26 + 10 * math.sin(C.t * 4), P.WARM, 1)
    L.A(cv, C, 600, 960, 520, pose('hero', mouth='smile', brow='calm', uaF=150, faF=165, hF='point', head=-14))
    return 'R'


def m_list(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 960, P, 0.4)
    L.A(cv, C, 480, 960, 540, pose('hero', mouth='flat', brow='fierce', uaF=55, faF=95, hF='open'))
    x0, y0 = 900, 260
    solid(cv, [(x0, y0 - 40), (x0 + 560, y0 - 40), (x0 + 560, y0 + 560), (x0, y0 + 560)], P.SOFT, 1, 2.4, 0.03)
    for k in range(6):
        y = y0 + 40 + k * 86
        cv.path([(x0 + 40, y - 22), (x0 + 84, y - 22), (x0 + 84, y + 22), (x0 + 40, y + 22), (x0 + 40, y - 22)], P.SOFT, 0.9, 2, smooth=False)
        cv.path([(x0 + 120, y), (x0 + 500, y)], P.LINE, 0.4, 1.4, smooth=False)
    with inst(cv):
        for k in range(6):
            t1 = 0.6 + k * 0.4
            if C.lt > t1:
                y = y0 + 40 + k * 86; kk = eo(ramp(C.lt, t1, t1 + 0.25))
                cv.path([(x0 + 46, y), (x0 + 60, y + 14), (x0 + 92, y - 26)], P.WARM, 1, 3.4, frac=kk, smooth=False)
    return 'T'


def m_runroad(C, sh, tx):
    cv = sh.cv; P = C.P; ground(cv, 940, P, 0.6)
    with inst(cv):
        rr = np.random.default_rng(3)
        for i in range(20):
            x = (rr.uniform(0, W + 400) - 900 * C.lt) % (W + 400) - 200; cv.path([(x, 960 + rr.uniform(0, 60)), (x + 60, 960 + rr.uniform(0, 60))], P.LINE, 0.4, 1.2, smooth=False)
        for i in range(6):
            x = (300 + i * 400 - 300 * C.lt) % (W + 400) - 200
            cv.path([(x, 940), (x + 120, 760), (x + 240, 940)], P.LINE, 0.35, 1.6, smooth=False)
        stars_live(cv, P, C.t, 120, 600, 3, 0.5)
    L.A(cv, C, 900, 940 - 20 * abs(math.sin(math.pi * C.lt / 0.42)), 440, run_cycle(C.lt / 0.42))
    return 'T'


_ORIG = {}


def install(Lmod, g=None):
    global L
    L = Lmod
    _ORIG['bubble'] = L.MOTIFS['bubble']; _ORIG['phone'] = L.MOTIFS['phone']
    L.MOTIFS.update(seed=m_seed, food=m_food, tug=m_tug, bull=m_bull, home=m_home, calendar=m_calendar, corner=m_corner,
                    bubble=m_bubble, phone=m_phone, book=m_book, mask=m_mask, wave=m_wave, star=m_star, list=m_list, runroad=m_runroad)
