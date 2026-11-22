"""白羊座主角 —— the Aries protagonist for the story cut.

Identity carried over from the zodiac hero card: spiky flame hair, two curled ram horns, a mantle with a wavy
collar, a sword with a ring pommel, and a small flame-heart at the chest. Built for acting: forward-kinematics
skeleton (angles per joint), occluding line-art parts, expressions, cape that streams with motion.

    draw_aries(cv, x, ground_y, h, POSE['run'], d=1, P=palette)
"""
import math
import numpy as np
from engine.core import spline, flame
from vis import heart_pts

BLACK = np.zeros(3)

# protagonist look; other signs swap this dict (long_taurus sets horns='bull', hair='curly', back=None, flower=True)
STYLE = dict(horns='ram', hair='flame', back='sword', flower=False)


def sp_(pts, closed=False): return [tuple(q) for q in spline(pts, n=6, closed=closed)]


def _sp(pts, n=8, closed=False): return [tuple(q) for q in spline(pts, n=n, closed=closed)]


def _solid(cv, outline, col, a, th, fill=0.0, fillcol=None):
    cv.poly(outline, BLACK, 1.0)
    if fill > 0: cv.poly(outline, (fillcol if fillcol is not None else col) * fill, a)
    cv.path(list(outline) + [outline[0]], col, a, th, smooth=False)


def _off(P, w):
    P = np.asarray(P, float); dd = np.gradient(P, axis=0); n = np.stack([-dd[:, 1], dd[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    w = np.asarray(w, float)[:, None]
    return P + n * w, P - n * w


def _limb(pts, widths, n=8):
    """tapered limb outline through joints; widths per joint (half widths)"""
    P = spline(pts, n=n); idx = np.linspace(0, len(widths) - 1, len(P)); w = np.interp(idx, np.arange(len(widths)), widths)
    L, R = _off(P, w)
    dv = P[-1] - P[-2]; dv /= np.linalg.norm(dv) + 1e-9; nv = np.array([-dv[1], dv[0]])
    cap = [P[-1] + nv * w[-1] * math.cos(q) + dv * w[-1] * 0.7 * math.sin(q) for q in np.linspace(0, math.pi, 8)]
    return [tuple(q) for q in L] + [tuple(c) for c in cap] + [tuple(q) for q in R[::-1]], P


# ------------------------------------------------------------------ poses (degrees from straight down, + = toward facing side)
POSE = {
    'hero':     dict(lean=0, head=0, uaF=10, faF=22, uaB=-10, faB=8, thF=7, shF=-2, thB=-7, shB=-5, hF='fist', hB='fist', mouth='smile', brow='calm', wind=(-0.25, 0.1), sword='back'),
    'run':      dict(lean=18, head=8, uaF=-60, faF=15, uaB=55, faB=150, thF=75, shF=8, thB=-38, shB=-85, hF='fist', hB='fist', mouth='grit', brow='fierce', wind=(-1.0, -0.25), sword='back', air=True),
    'burst':    dict(lean=35, head=15, uaF=-80, faF=-40, uaB=35, faB=120, thF=95, shF=40, thB=-30, shB=-30, hF='open', hB='fist', mouth='shout', brow='fierce', wind=(-1.2, -0.1), sword='back', air=True),
    'leap':     dict(lean=10, head=-5, uaF=150, faF=175, uaB=-120, faB=-150, thF=90, shF=-10, thB=-60, shB=-120, hF='open', hB='open', mouth='open', brow='fierce', wind=(-0.6, 0.9), sword='back', air=True),
    'skid':     dict(lean=-18, head=-8, uaF=75, faF=95, uaB=-55, faB=-85, thF=45, shF=35, thB=-8, shB=-55, hF='open', hB='fist', mouth='grit', brow='fierce', wind=(0.9, -0.4), sword='back'),
    'point':    dict(lean=6, head=4, uaF=86, faF=88, uaB=-22, faB=35, thF=28, shF=12, thB=-28, shB=-18, hF='point', hB='fist', mouth='shout', brow='angry', wind=(-0.9, -0.15), sword='back'),
    'lookback': dict(lean=-2, head=0, uaF=6, faF=14, uaB=-6, faB=6, thF=10, shF=4, thB=-8, shB=-14, hF='open', hB='open', mouth='sad', brow='sad', wind=(0.3, 0.1), sword='back', turn=True),
    'stand_arm': dict(lean=-3, head=-6, uaF=12, faF=30, uaB=-12, faB=-25, thF=14, shF=4, thB=-14, shB=-6, hF='fist', hB='fist', mouth='flat', brow='fierce', wind=(-0.4, 0.05), sword='back'),
    'climb':    dict(lean=14, head=4, uaF=-28, faF=-6, uaB=30, faB=70, thF=62, shF=4, thB=-12, shB=-20, hF='fist', hB='fist', mouth='grit', brow='fierce', wind=(-0.7, 0.0), sword='back'),
    'sit_hug':  dict(lean=22, head=40, uaF=60, faF=12, uaB=52, faB=8, thF=140, shF=14, thB=134, shB=10, hF='open', hB='open', mouth='sad', brow='sad', wind=(-0.1, 0.4), sword='back', sit=True),
}


def _dir(a, d): r = math.radians(a); return np.array([d * math.sin(r), math.cos(r)])


def skeleton(x, gy, h, p, d):
    lean = math.radians(p['lean']); up = np.array([d * math.sin(lean), -math.cos(lean)]); right = np.array([-up[1], up[0]]) * d
    hip = np.array([0.0, 0.0])
    neck = hip + up * 0.30 * h
    sc = hip + up * 0.265 * h
    shF, shB = sc + right * 0.07 * h * d * d + up * 0, sc - right * 0.05 * h
    hpF, hpB = hip + right * 0.04 * h, hip - right * 0.035 * h
    J = dict(hip=hip, neck=neck, sc=sc, shF=shF, shB=shB, hpF=hpF, hpB=hpB)
    J['elF'] = shF + _dir(p['uaF'], d) * 0.16 * h; J['haF'] = J['elF'] + _dir(p['faF'], d) * 0.15 * h
    J['elB'] = shB + _dir(p['uaB'], d) * 0.16 * h; J['haB'] = J['elB'] + _dir(p['faB'], d) * 0.15 * h
    J['knF'] = hpF + _dir(p['thF'], d) * 0.245 * h; J['ftF'] = J['knF'] + _dir(p['shF'], d) * 0.245 * h
    J['knB'] = hpB + _dir(p['thB'], d) * 0.245 * h; J['ftB'] = J['knB'] + _dir(p['shB'], d) * 0.245 * h
    hl = math.radians(p['lean'] + p.get('head', 0)); hup = np.array([d * math.sin(hl), -math.cos(hl)])
    J['head'] = neck + up * 0.03 * h + hup * 0.085 * h; J['hup'] = hup
    if p.get('sit'): base = gy - 0.02 * h
    else: base = gy - max(J['ftF'][1], J['ftB'][1]) - (0.09 * h if p.get('air') else 0.0) if False else None
    if p.get('sit'): oy = gy - 0.03 * h
    else: oy = gy - max(J['ftF'][1], J['ftB'][1]) - (0.08 * h if p.get('air') else 0.0)
    for k in list(J):
        if k != 'hup': J[k] = np.array([x, oy]) + J[k]
    J['up'], J['right'] = up, right
    return J


def draw_aries(cv, x, gy, h, p, d=1, P=None, col=None, a=1.0, th=2.4, heart=1.0, armor=0.0, rim=None, tear=False):
    """the protagonist. armor 0..1 assembles plate armour; returns joints"""
    col = P.SOFT if col is None else col; G, Wm = P.GOLD, P.WARM; thin = th * 0.55; dc = col * 0.72
    J = skeleton(x, gy, h, p, d); up, right = J['up'], J['right']
    T = lambda v: tuple(v)
    # ---------------- cape (behind everything) ----------------
    wx, wy = p.get('wind', (-0.3, 0.1))
    s1, s2 = J['shB'] - right * 0.03 * h + up * 0.01 * h, J['shF'] + right * 0.01 * h
    tail = J['hip'] + np.array([d * wx * 0.42 * h, 0.32 * h + wy * 0.3 * h])
    ctrl = J['sc'] + np.array([d * wx * 0.3 * h, 0.12 * h])
    hem = []
    for k in range(7):
        u = k / 6; base = s1 + (s2 - s1) * 0.0
        hem.append(tail + np.array([-d * 0.16 * h * (u - 0.5) * (1 - abs(wx) * 0.3), (0.03 * h) * math.sin(u * math.pi * 3)]))
    cape = [T(s2), T(ctrl + right * 0.12 * h), T(hem[0])] + [T(q) for q in hem[1:]] + [T(ctrl - right * 0.14 * h), T(s1)]
    cape = _sp(cape, 6, True)
    _solid(cv, cape, P.LINE, a, th, 0.08, G)
    for k in (2, 4):
        cv.path(_sp([T(J['sc'] + right * (0.02 * h * (k - 3))), T(ctrl + right * 0.03 * h * (k - 3)), T(hem[k])], 6), P.LINE, 0.45 * a, thin)
    # ---------------- sword on the back: ring pommel over the shoulder ----------------
    if p.get('sword') == 'back' and STYLE.get('back') == 'sword':
        bdir = (up * 0.9 - right * 0.45); bdir /= np.linalg.norm(bdir)
        hilt = J['sc'] - right * 0.02 * h + up * 0.06 * h; tip = hilt - bdir * 0.62 * h
        bw = np.array([-bdir[1], bdir[0]]) * 0.016 * h
        blade = [T(hilt - bdir * 0.06 * h + bw), T(tip + bw * 0.3), T(tip - bdir * 0.03 * h), T(tip - bw * 0.3), T(hilt - bdir * 0.06 * h - bw)]
        _solid(cv, blade, P.WARM, a, th * 0.8, 0.12)
        g = hilt - bdir * 0.06 * h; cv.path([T(g + bw * 3.2), T(g - bw * 3.2)], G, a, th, smooth=False)
        cv.path([T(g), T(hilt + bdir * 0.02 * h)], G, a, th * 1.2, smooth=False)
        cv.circle(T(hilt + bdir * 0.045 * h), 0.022 * h, G, a, th * 0.9)
    ex_b = STYLE.get('extras', ())
    if STYLE.get('back') == 'bow':
        bdir = (up * 0.9 - right * 0.45); bdir /= np.linalg.norm(bdir); nb = np.array([-bdir[1], bdir[0]])
        c0 = J['sc'] - right * 0.05 * h; p0, p1 = c0 + bdir * 0.32 * h, c0 - bdir * 0.32 * h
        arc = [T(p0 + (p1 - p0) * u + nb * 0.12 * h * math.sin(math.pi * u)) for u in np.linspace(0, 1, 20)]
        cv.path(arc, G, a, th * 1.1, smooth=False); cv.path([T(p0), T(p1)], P.SOFT, 0.7 * a, thin, smooth=False)
        for k_ in range(3): q0 = c0 + right * (0.02 * k_ - 0.03) * h; cv.path([T(q0 - up * 0.05 * h), T(q0 + up * 0.22 * h)], Wm, a, thin * 1.2, smooth=False)
    if 'shell' in ex_b:
        c0 = J['sc'] - right * 0.06 * h - up * 0.06 * h
        sh_ = [T(c0 + right * 0.09 * h * math.cos(q) + up * 0.15 * h * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 40)]
        _solid(cv, sh_, G, a, th, 0.1, Wm)
        for k_ in range(3): cv.path([T(c0 + up * (0.1 - 0.1 * k_) * h - right * 0.08 * h), T(c0 + up * (0.12 - 0.1 * k_) * h + right * 0.02 * h)], G, 0.6 * a, thin, smooth=False)
    if 'tail' in ex_b:
        seg = [J['hip'] - right * 0.06 * h]; ang = math.pi * 0.8
        for k_ in range(9):
            ang -= 0.32; seg.append(seg[-1] + (-right * math.cos(ang) * 0.6 + up * math.sin(ang)) * 0.06 * h)
        for k_ in range(len(seg) - 1): cv.circle(T(seg[k_]), 0.02 * h * (1 - k_ / 14), G, a, th * 0.8)
        tip = seg[-1]; cv.path([T(tip), T(tip + right * 0.05 * h - up * 0.02 * h), T(tip + up * 0.03 * h)], Wm, a, th, smooth=False)
    # ---------------- back arm + back leg ----------------
    def hand(c, kind, dirv, colr):
        dirv = dirv / (np.linalg.norm(dirv) + 1e-9); nv = np.array([-dirv[1], dirv[0]])
        r = 0.026 * h
        if kind == 'point':
            palm = [T(c + nv * r * 0.8), T(c + dirv * r * 1.1 + nv * r * 0.7), T(c + dirv * r * 1.2 - nv * r * 0.6), T(c - nv * r * 0.8), T(c - dirv * r * 0.5)]
            _solid(cv, _sp(palm, 4, True), colr, a, th * 0.85, 0.05)
            fing = [T(c + dirv * r * 1.0 + nv * r * 0.35), T(c + dirv * r * 3.0 + nv * r * 0.25), T(c + dirv * r * 3.0 - nv * r * 0.05), T(c + dirv * r * 1.0 - nv * r * 0.1)]
            _solid(cv, fing, colr, a, th * 0.8)
            cv.path([T(c + nv * r * 0.6), T(c + dirv * r * 0.9 + nv * r * 1.1)], colr, a, thin)
        else:
            k = 1.0 if kind == 'fist' else 1.25
            palm = [T(c + nv * r * 0.85 - dirv * r * 0.3), T(c + dirv * r * k + nv * r * 0.8), T(c + dirv * r * k * 1.1 - nv * r * 0.75), T(c - nv * r * 0.85 - dirv * r * 0.2)]
            _solid(cv, _sp(palm, 5, True), colr, a, th * 0.85, 0.05)
            for j in range(3): cv.path([T(c + dirv * r * (0.4 + 0.2 * j) + nv * r * 0.7), T(c + dirv * r * (0.6 + 0.2 * j) - nv * r * 0.2)], colr, 0.7 * a, thin * 0.9)
    def arm(sh, el, ha, kind, colr):
        out, axis = _limb([T(sh), T(el), T(ha)], [0.04 * h, 0.03 * h, 0.024 * h])
        _solid(cv, out, colr, a, th, 0.05)
        k = len(axis) - 5; tv = axis[k] - axis[k - 1]; tv /= np.linalg.norm(tv) + 1e-9; nv = np.array([-tv[1], tv[0]])
        for j in (0, 3): cv.path([T(axis[k - j] + nv * 0.028 * h), T(axis[k - j] - nv * 0.028 * h)], G, 0.9 * a, thin * 1.2, smooth=False)   # bracer
        hand(ha, kind, ha - el, colr)
        if armor > 0:
            pa = [T(sh + up * 0.03 * h - right * 0.05 * h), T(sh + up * 0.05 * h), T(sh + up * 0.02 * h + right * 0.06 * h), T(sh - up * 0.06 * h + right * 0.05 * h), T(sh - up * 0.07 * h - right * 0.04 * h)]
            cv.path(_sp(pa, 4, True) + [_sp(pa, 4, True)[0]], G, a * armor, th, frac=armor, smooth=False)
    def leg(hp, kn, ft, colr):
        out, axis = _limb([T(hp), T(kn), T(ft)], [0.055 * h, 0.04 * h, 0.03 * h])
        _solid(cv, out, colr, a, th, 0.05)
        k = int(len(axis) * 0.72); tv = axis[k] - axis[k - 1]; tv /= np.linalg.norm(tv) + 1e-9; nv = np.array([-tv[1], tv[0]])
        cv.path([T(axis[k] + nv * 0.036 * h), T(axis[k] - nv * 0.036 * h)], colr, a * 0.9, thin, smooth=False)   # boot cuff
        sv = ft - kn; sv /= np.linalg.norm(sv) + 1e-9; fwd = np.array([d * 1.0, 0.0]); fwd = fwd - sv * np.dot(fwd, sv) * 0.6; fwd /= np.linalg.norm(fwd)
        boot = [T(ft - fwd * 0.03 * h - sv * 0.02 * h), T(ft + fwd * 0.075 * h - sv * 0.005 * h), T(ft + fwd * 0.08 * h + sv * 0.018 * h), T(ft - fwd * 0.035 * h + sv * 0.02 * h)]
        _solid(cv, _sp(boot, 4, True), colr, a, th, 0.12)
    arm(J['shB'], J['elB'], J['haB'], p['hB'], dc)
    leg(J['hpB'], J['knB'], J['ftB'], dc)
    leg(J['hpF'], J['knF'], J['ftF'], col)
    # ---------------- torso: tunic, belt, skirt flaps ----------------
    sc, hip = J['sc'], J['hip']
    tor = [T(J['shB'] - right * 0.035 * h + up * 0.01 * h), T(J['shB'] - right * 0.03 * h - up * 0.1 * h), T(hip - right * 0.06 * h + up * 0.03 * h),
           T(hip - right * 0.07 * h - up * 0.11 * h), T(hip + right * 0.075 * h - up * 0.11 * h), T(hip + right * 0.065 * h + up * 0.03 * h),
           T(J['shF'] + right * 0.03 * h - up * 0.1 * h), T(J['shF'] + right * 0.04 * h + up * 0.01 * h), T(sc + up * 0.03 * h)]
    tor = _sp(tor, 5, True)
    _solid(cv, tor, col, a, th, 0.07)
    vn = [T(J['neck'] - right * 0.035 * h - up * 0.01 * h), T(sc - up * 0.07 * h), T(J['neck'] + right * 0.035 * h - up * 0.01 * h)]
    cv.path(vn, col, a * 0.85, thin * 1.2)
    bl = [T(hip - right * 0.064 * h + up * 0.02 * h), T(hip + right * 0.068 * h + up * 0.02 * h)]
    cv.path(bl, G, a, th * 1.3, smooth=False); cv.path([T(q + up * 0.022 * h * 0 + np.array([0, 0.014 * h])) for q in map(np.array, bl)], G, 0.6 * a, thin, smooth=False)
    bk = hip + up * 0.014 * h + right * 0.01 * h
    cv.circle(T(bk), 0.016 * h, G, a, thin * 1.4)
    for k in range(3):
        u = -0.06 + 0.06 * k
        cv.path([T(hip + right * u * h - up * 0.0), T(hip + right * (u * 1.25) * h - up * 0.1 * h)], col, 0.4 * a, thin)
    # wavy mantle collar (from the zodiac card)
    coll = [T(J['shB'] - right * 0.04 * h + up * 0.0)]
    for k in range(1, 8):
        u = k / 8; q = J['shB'] + (J['shF'] - J['shB']) * u - right * 0.04 * h * (1 - u) + right * 0.04 * h * u
        coll.append(T(q - up * (0.035 * h + 0.012 * h * math.sin(u * math.pi * 4))))
    coll.append(T(J['shF'] + right * 0.04 * h))
    cv.path(coll, G, a, th, smooth=True)
    cv.path([T(J['shB'] - right * 0.04 * h), T(J['neck'] - right * 0.03 * h + up * 0.015 * h)], G, 0.8 * a, thin)
    cv.path([T(J['shF'] + right * 0.04 * h), T(J['neck'] + right * 0.03 * h + up * 0.015 * h)], G, 0.8 * a, thin)
    # armour plates
    if armor > 0:
        ch = [T(sc - right * 0.06 * h - up * 0.02 * h), T(sc + right * 0.065 * h - up * 0.02 * h), T(sc + right * 0.055 * h - up * 0.17 * h), T(sc - up * 0.2 * h), T(sc - right * 0.05 * h - up * 0.17 * h)]
        cv.path(_sp(ch, 4, True) + [_sp(ch, 4, True)[0]], G, a, th * 1.1, frac=armor, smooth=False)
        cv.path([T(sc - up * 0.02 * h), T(sc - up * 0.19 * h)], G, 0.6 * a * armor, thin)
    # front arm
    arm(J['shF'], J['elF'], J['haF'], p['hF'], col)
    # ---------------- head ----------------
    hd = 1 if not p.get('turn') else -1
    hc, hu = J['head'], J['hup']; hr = np.array([-hu[1], hu[0]]) * d * hd; r = 0.078 * h
    R = lambda px, py: T(hc + hr * px + (-hu) * py)       # local: +x = face side, +y = down
    # horns: big curled ram horns — far one peeks above the skull, near one spirals back and down around the ear
    def horn(cx_, cy_, r0, r1, w0, w1, th0, th1, alpha, near):
        pts = []
        for k in range(40):
            u = k / 39; q = math.radians(th0 + (th1 - th0) * u); rr_ = r * (r0 + (r1 - r0) * u)
            pts.append((cx_ * r + rr_ * math.cos(q), cy_ * r + rr_ * math.sin(q)))
        P_ = [R(px, py) for px, py in pts]
        out, ax_ = _limb(P_, [w0 * r, (w0 + w1) * 0.5 * r, w1 * r], n=3)
        _solid(cv, out, G, alpha, th * (1.0 if near else 0.8), 0.12, Wm)
        for k in range(4, 36, 3):            # ridges across the horn
            i = int(k / 39 * (len(ax_) - 1)); tv = ax_[min(i + 1, len(ax_) - 1)] - ax_[max(i - 1, 0)]
            tv /= np.linalg.norm(tv) + 1e-9; nv = np.array([-tv[1], tv[0]]); ww = (w0 + (w1 - w0) * k / 39) * r * 0.85
            cv.path([T(ax_[i] + nv * ww), T(ax_[i] - nv * ww)], G, 0.55 * alpha, thin * 0.8, smooth=False)
        cv.path(P_, G, 0.3 * alpha, th * 5, layer=cv.F)
    def bull_horn(pts, w0, alpha, near):
        P_ = [R(px * r, py * r) for px, py in pts]
        out, ax_ = _limb(P_, [w0 * r, w0 * 0.6 * r, 0.025 * r], n=8)
        _solid(cv, out, G, alpha, th * (1.0 if near else 0.8), 0.14, Wm)
        for k in (0.2, 0.35):
            i = int(k * (len(ax_) - 1)); tv = ax_[i + 1] - ax_[i - 1]; tv /= np.linalg.norm(tv) + 1e-9; nv = np.array([-tv[1], tv[0]])
            ww = w0 * r * (1 - k * 0.8); cv.path([T(ax_[i] + nv * ww), T(ax_[i] - nv * ww)], G, 0.6 * alpha, thin * 0.9, smooth=False)
        cv.path(P_, G, 0.3 * alpha, th * 5, layer=cv.F)
    hz = STYLE['horns']
    if hz == 'ram': horn(0.18, -0.68, 0.5, 0.14, 0.14, 0.04, -55, -330, 0.75 * a, False)
    elif hz == 'bull': bull_horn([(0.3, -0.85), (0.62, -1.05), (0.85, -1.35), (0.8, -1.72)], 0.15, 0.75 * a, False)
    elif hz == 'goat': bull_horn([(0.25, -0.9), (0.05, -1.35), (-0.4, -1.65), (-0.9, -1.6)], 0.12, 0.75 * a, False)
    if STYLE['hair'] in ('long', 'wave'):          # hair that falls behind the neck, drawn before the face
        L_ = 1.9 if STYLE['hair'] == 'long' else 1.2
        bh = [(0.5, -0.7), (-0.4, -1.1), (-1.08, -0.55), (-1.25, 0.6), (-1.15, L_), (-0.75, L_ + 0.15), (-0.45, L_ - 0.1), (-0.4, 0.4), (0.2, -0.2)]
        bh = [R(px * r, py * r) for px, py in sp_(bh)]
        cv.poly(bh, BLACK, 1.0); cv.poly(bh, Wm * 0.14, a); cv.path(bh + [bh[0]], col, a, th, smooth=False)
        for k_ in range(3): cv.path([R((-0.7 - 0.15 * k_) * r, -0.3 * r), R((-0.9 - 0.12 * k_ + 0.1 * math.sin(k_)) * r, 0.7 * r), R((-0.8 - 0.12 * k_) * r, (L_ - 0.1) * r)], col, 0.4 * a, thin)
    neck = [T(J['neck'] - right * 0.022 * h), T(J['neck'] + right * 0.022 * h), R(0.3 * r, 0.95 * r), R(-0.35 * r, 0.9 * r)]
    _solid(cv, neck, col, a, th)
    face = []
    for q in np.linspace(0, 2 * math.pi, 60):
        ex, ey = r * 0.86 * math.cos(q), r * 1.1 * math.sin(q)
        if ey > 0: ex *= 1 - 0.32 * (ey / (r * 1.1)) ** 2
        if ex > r * 0.55 and -0.3 * r < ey < 0.2 * r: ex += r * 0.14 * math.cos((ey + 0.05 * r) / (0.25 * r) * math.pi / 2) ** 2
        face.append(R(ex, ey))
    _solid(cv, face, col, a, th, 0.04)
    if STYLE['hair'] in ('flame', 'mane'):
        # spiky flame hair swept back
        # flame hair: curved locks swept up and back like a fire
        sw = p.get('wind', (0, 0))[0] * 0.25
        base = [(0.72, -0.42), (0.55, -0.78), (0.25, -0.98), (-0.12, -1.02), (-0.48, -0.9), (-0.78, -0.62), (-0.95, -0.2), (-0.9, 0.18)]
        tips = [(0.62, -1.18), (0.3, -1.45), (-0.12, -1.55), (-0.62, -1.4), (-1.05, -1.08), (-1.3, -0.55), (-1.25, -0.05)]
        if STYLE['hair'] == 'mane':     # lion: a bigger, fuller mane that wraps the jaw
            base = base + [(-0.6, 0.6), (-0.1, 0.95)]
            tips = [(x_ * 1.25, y_ * 1.2) for x_, y_ in tips] + [(-1.2, 0.75), (-0.5, 1.25)]
        hp = [base[0]]
        for i, (tx_, ty_) in enumerate(tips):
            b0, b1 = np.array(base[i]), np.array(base[i + 1]); tp = np.array([tx_ + sw - 0.1, ty_])
            m0 = (b0 + tp) / 2 + np.array([0.12, 0.0]); m1 = (b1 + tp) / 2 + np.array([0.06, 0.1])
            for u in np.linspace(0, 1, 6)[1:]: hp.append(tuple((1 - u) ** 2 * b0 + 2 * u * (1 - u) * m0 + u * u * tp))
            for u in np.linspace(0, 1, 6)[1:]: hp.append(tuple((1 - u) ** 2 * tp + 2 * u * (1 - u) * m1 + u * u * b1))
        hp += [(-0.55, 0.05), (-0.2, -0.5), (0.4, -0.45)]
        hp = [R(px * r, py * r) for px, py in hp]
        cv.poly(hp, BLACK, 1.0); cv.poly(hp, Wm * 0.2, a); cv.path(hp + [hp[0]], col, a, th, smooth=False)
        for i in range(len(tips)):   # inner lock lines
            b0 = np.array(base[i]) * 0.55 + np.array(base[i + 1]) * 0.45; tp = np.array(tips[i]) * 0.8 + b0 * 0.2 + np.array([sw - 0.08, 0])
            cv.path([R(*(b0 * r * 0.85)), R(*(((b0 + tp) / 2 + [0.08, 0]) * r)), R(*(tp * r))], col, 0.45 * a, thin)
    elif STYLE['hair'] in ('short', 'long', 'wave'):
        # neat cap with a side-swept fringe
        hp = [(0.85, -0.3), (0.78, -0.82), (0.35, -1.18), (-0.25, -1.22), (-0.8, -0.95), (-1.02, -0.4), (-0.95, 0.2), (-0.62, 0.05), (-0.45, -0.45), (0.1, -0.62), (0.55, -0.5)]
        hp = [R(px * r, py * r) for px, py in sp_(hp, True)]
        cv.poly(hp, BLACK, 1.0); cv.poly(hp, Wm * 0.16, a); cv.path(hp + [hp[0]], col, a, th, smooth=False)
        for k_ in range(3): cv.path([R((0.6 - 0.35 * k_) * r, (-1.05 + 0.05 * k_) * r), R((0.2 - 0.3 * k_) * r, -0.72 * r), R((0.0 - 0.3 * k_) * r, -0.55 * r)], col, 0.45 * a, thin)
    else:
        # soft curly hair: a cap of round curls
        cb = [(0.8, -0.38), (0.7, -0.82), (0.4, -1.12), (0.0, -1.24), (-0.42, -1.16), (-0.8, -0.92), (-1.04, -0.54), (-1.1, -0.1), (-0.95, 0.3)]
        hp = [cb[0]]
        for i in range(len(cb) - 1):
            b0, b1 = np.array(cb[i]), np.array(cb[i + 1]); mvec = (b0 + b1) / 2; dv = b1 - b0; nv = np.array([dv[1], -dv[0]])
            nv = nv / (np.linalg.norm(nv) + 1e-9); L = np.linalg.norm(dv) / 2
            for q in np.linspace(math.pi, 0, 7)[1:]: hp.append(tuple(mvec + (-dv / 2 / max(L, 1e-6)) * L * math.cos(q) + nv * L * 0.95 * math.sin(q)))
        hp += [(-0.6, 0.1), (-0.25, -0.5), (0.4, -0.42)]
        hp = [R(px * r, py * r) for px, py in hp]
        cv.poly(hp, BLACK, 1.0); cv.poly(hp, Wm * 0.18, a); cv.path(hp + [hp[0]], col, a, th, smooth=False)
        for (qx, qy) in ((0.3, -0.75), (-0.1, -0.85), (-0.5, -0.7), (-0.72, -0.3), (0.05, -0.55)):
            cv.path([R((qx + 0.12 * math.cos(q)) * r, (qy + 0.12 * math.sin(q)) * r) for q in np.linspace(0.3, 5.2, 10)], col, 0.45 * a, thin)
    if hz == 'ram': horn(-0.3, -0.22, 0.56, 0.14, 0.17, 0.045, -75, -400, a, True)
    elif hz == 'bull': bull_horn([(-0.35, -0.78), (-0.78, -0.95), (-1.12, -1.25), (-1.08, -1.66)], 0.19, a, True)
    elif hz == 'goat': bull_horn([(-0.1, -0.95), (-0.45, -1.4), (-1.0, -1.7), (-1.55, -1.55), (-1.75, -1.2)], 0.17, a, True)
    ex_list = STYLE.get('extras', ())
    if 'crown' in ex_list:
        cw = [(-0.55, -1.12), (-0.6, -1.55), (-0.32, -1.32), (-0.05, -1.68), (0.2, -1.32), (0.48, -1.55), (0.45, -1.1)]
        cw = [R(px * r, py * r) for px, py in cw]; cv.poly(cw, BLACK, 1.0); cv.poly(cw, G * 0.3, a); cv.path(cw + [cw[0]], G, a, th, smooth=False)
        for q_ in (cw[1], cw[3], cw[5]): cv.circle(q_, r * 0.06, Wm, a, fill=True); cv.glow(q_, r * 0.3, G, 0.4 * a)
    if STYLE.get('flower'):           # a small flower tucked above the ear
        fc = np.array(R(-0.55 * r, -0.62 * r))
        for j in range(5):
            q = j / 5 * 2 * math.pi; pc = fc + np.array([math.cos(q), math.sin(q)]) * r * 0.13
            cv.poly([T(pc + np.array([math.cos(t_), math.sin(t_)]) * r * 0.1) for t_ in np.linspace(0, 2 * math.pi, 10)], BLACK, 1.0)
            cv.path([T(pc + np.array([math.cos(t_), math.sin(t_)]) * r * 0.1) for t_ in np.linspace(0, 2 * math.pi, 11)], Wm, a, thin * 1.2, smooth=False)
        cv.circle(T(fc), r * 0.06, G, a, fill=True); cv.glow(T(fc), r * 0.3, G, 0.4 * a)
    if 'glasses' in ex_list:
        gc = np.array(R(0.48 * r, -0.08 * r))
        cv.path([T(gc + np.array(R(0.2 * r * math.cos(q), 0.17 * r * math.sin(q))) - np.array(R(0, 0))) for q in np.linspace(0, 2 * math.pi, 24)], col, a, thin * 1.2, smooth=False)
        cv.path([R(0.28 * r, -0.12 * r), R(-0.25 * r, -0.2 * r)], col, a, thin, smooth=False)
    # ear, brow, eye, mouth
    cv.path([R(-0.12 * r, -0.12 * r), R(-0.32 * r, -0.2 * r), R(-0.34 * r, 0.12 * r), R(-0.15 * r, 0.2 * r)], col, 0.7 * a, thin)
    brow = {'calm': (0.0, 0.0), 'fierce': (0.1, -0.06), 'angry': (0.16, -0.1), 'sad': (-0.12, 0.08)}[p.get('brow', 'calm')]
    ex_, ey_ = 0.48 * r, -0.08 * r
    cv.path([R(ex_ - 0.2 * r, ey_ - 0.2 * r - brow[0] * r), R(ex_ + 0.18 * r, ey_ - 0.2 * r + brow[0] * r)], col, a, th * 0.9, smooth=False)
    if p.get('brow') == 'sad':
        cv.path([R(ex_ - 0.13 * r, ey_), R(ex_, ey_ + 0.05 * r), R(ex_ + 0.12 * r, ey_)], col, a, thin * 1.3)
    else:
        eye = [R(ex_ - 0.14 * r, ey_), R(ex_, ey_ - 0.08 * r + brow[1] * r * 0.3), R(ex_ + 0.13 * r, ey_), R(ex_, ey_ + 0.05 * r)]
        cv.path(eye, col, a, thin * 1.2, closed=True); cv.circle(R(ex_ + 0.03 * r, ey_ - 0.01 * r), r * 0.045, col, a, fill=True)
    m = p.get('mouth', 'flat'); mx, my = 0.5 * r, 0.52 * r
    if m == 'smile': cv.path([R(mx - 0.15 * r, my - 0.04 * r), R(mx, my + 0.05 * r), R(mx + 0.14 * r, my - 0.05 * r)], col, a, thin * 1.2)
    elif m in ('shout', 'open'):
        cv.path([R(mx - 0.12 * r, my - 0.06 * r), R(mx + 0.13 * r, my - 0.07 * r), R(mx + 0.08 * r, my + 0.14 * r), R(mx - 0.08 * r, my + 0.12 * r)], col, a, thin * 1.2, closed=True)
    elif m == 'grit':
        cv.path([R(mx - 0.14 * r, my), R(mx + 0.14 * r, my - 0.02 * r)], col, a, thin * 1.3, smooth=False)
        cv.path([R(mx - 0.1 * r, my + 0.03 * r), R(mx + 0.1 * r, my + 0.02 * r)], col, 0.6 * a, thin, smooth=False)
    elif m == 'sad': cv.path([R(mx - 0.13 * r, my + 0.04 * r), R(mx, my - 0.02 * r), R(mx + 0.12 * r, my + 0.04 * r)], col, a, thin * 1.2)
    else: cv.path([R(mx - 0.12 * r, my), R(mx + 0.12 * r, my)], col, a, thin * 1.2, smooth=False)
    if tear:
        for k in range(2):
            tp = np.array(R(ex_ - 0.02 * r, ey_ + 0.25 * r + k * 0.5 * r))
            cv.poly(_sp([T(tp + [0, -0.12 * r]), T(tp + [0.06 * r, 0.03 * r]), T(tp + [0, 0.09 * r]), T(tp + [-0.06 * r, 0.03 * r])], 4, True), Wm, a * (1 - 0.4 * k))
    if armor > 0:   # horned helm closes over the hair
        helm = [R(0.85 * r, -0.2 * r), R(0.7 * r, -0.95 * r), R(0.0, -1.25 * r), R(-0.8 * r, -1.0 * r), R(-0.95 * r, -0.1 * r), R(-0.6 * r, 0.25 * r)]
        cv.path(_sp(helm, 5), G, a, th * 1.1, frac=armor)
        cv.path([R(0.85 * r, -0.2 * r), R(0.3 * r, -0.25 * r)], G, a * armor, th, smooth=False)
    # rim light
    if rim is not None:
        lx, ly = rim
        for poly in (face, tor, cape):
            seg = [q for q in poly if (q[0] - J['hip'][0]) * lx + (q[1] - J['hip'][1]) * ly > 0]
            if len(seg) > 2: cv.path(seg, col, 0.45 * a, th * 4, smooth=False, layer=cv.F)
    # flame heart at the chest
    if heart > 0:
        c = sc - up * 0.075 * h + right * 0.012 * h; s_ = 0.026 * h * heart
        hpp = [(c[0] + s_ * u, c[1] + s_ * v) for u, v in heart_pts(0, 0, 1.0, 40)]
        cv.poly(hpp, Wm, 0.95 * a); cv.glow(T(c), s_ * 2.6, G, 0.55 * a)
        flame(cv, c[0], c[1] - s_ * 0.6, s_ * 2.2, G, 0.35 * a, layer=cv.F)
    for em in ('fish', 'jar', 'scales', 'wheat', 'twinstar'):
        if em in STYLE.get('extras', ()): emblem(cv, em, J['head'] - right * 0.2 * h - up * 0.05 * h, 0.06 * h, P, a, th)
    J['chest'] = sc - up * 0.075 * h
    return J


def emblem(cv, kind, c, s, P, a=1.0, th=2.0):
    G, Wm = P.GOLD, P.WARM; c = np.array(c, float); T = tuple
    if kind == 'fish':
        for k, sg in ((0, 1), (1, -1)):
            o = c + np.array([0, sg * s * 0.7])
            body = [T(o + np.array([sg * s * math.cos(q), s * 0.45 * math.sin(q)])) for q in np.linspace(0, 2 * math.pi, 24)]
            cv.path(body, G, a, th * 0.8, smooth=False)
            tl = o - np.array([sg * s, 0]); cv.path([T(tl), T(tl - np.array([sg * s * 0.5, s * 0.4])), T(tl - np.array([sg * s * 0.5, -s * 0.4])), T(tl)], G, a, th * 0.8, smooth=False)
            cv.circle(T(o + np.array([sg * s * 0.5, -s * 0.1])), s * 0.08, Wm, a, fill=True)
        cv.glow(T(c), s * 2.2, G, 0.3 * a)
    elif kind == 'jar':
        jar = [(-0.4, -1.0), (-0.3, -0.7), (-0.75, -0.2), (-0.6, 0.6), (0.6, 0.6), (0.75, -0.2), (0.3, -0.7), (0.4, -1.0)]
        cv.path([T(c + np.array(q) * s) for q in sp_(jar)], G, a, th * 0.9, smooth=False)
        for k in range(3):
            cv.path([T(c + np.array([0.4 + 0.25 * k, -1.0 + 0.1 * k]) * s), T(c + np.array([0.9 + 0.3 * k, -0.3]) * s), T(c + np.array([1.0 + 0.3 * k, 0.9]) * s)], Wm, 0.7 * a, th * 0.6)
        cv.glow(T(c), s * 2.2, G, 0.3 * a)
    elif kind == 'scales':
        cv.path([T(c + np.array([0, -1.0]) * s), T(c + np.array([0, 0.9]) * s)], G, a, th * 0.9, smooth=False)
        cv.path([T(c + np.array([-1.1, -0.7]) * s), T(c + np.array([1.1, -0.7]) * s)], G, a, th * 0.9, smooth=False)
        for sg in (-1, 1):
            p0 = c + np.array([sg * 1.1, -0.7]) * s
            cv.path([T(p0), T(p0 + np.array([-0.4, 0.8]) * s)], G, 0.7 * a, th * 0.6, smooth=False); cv.path([T(p0), T(p0 + np.array([0.4, 0.8]) * s)], G, 0.7 * a, th * 0.6, smooth=False)
            cv.path([T(p0 + np.array([-0.5 + 0.1 * math.cos(q) * 5 * 0 + q / math.pi, 0.8 + 0.25 * math.sin(q)]) * s) for q in np.linspace(0, math.pi, 10)], G, a, th * 0.8, smooth=False)
        cv.path([T(c + np.array([-0.5, 0.9]) * s), T(c + np.array([0.5, 0.9]) * s)], G, a, th, smooth=False)
        cv.glow(T(c), s * 2.2, G, 0.3 * a)
    elif kind == 'wheat':
        cv.path([T(c + np.array([0.3, 1.2]) * s), T(c + np.array([0, -0.2]) * s), T(c + np.array([-0.1, -1.2]) * s)], G, a, th * 0.8)
        for k in range(5):
            p = c + np.array([-0.02 * k, -0.1 - 0.22 * k]) * s
            for sg in (-1, 1): cv.path([T(p + np.array([sg * 0.05, 0]) * s), T(p + np.array([sg * 0.35, -0.25]) * s), T(p + np.array([sg * 0.1, -0.3]) * s), T(p)], Wm, a, th * 0.7, smooth=False)
        cv.glow(T(c), s * 2.2, G, 0.3 * a)
    elif kind == 'twinstar':
        for sg in (-1, 1):
            o = c + np.array([sg * 0.6 * s, 0]); cv.circle(T(o), s * 0.25, Wm, a, fill=True); cv.glow(T(o), s * 0.9, G, 0.6 * a)
        cv.path([T(c + np.array([-0.6 * s, 0])), T(c + np.array([0.6 * s, 0]))], G, 0.5 * a, th * 0.6, smooth=False)
