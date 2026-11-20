"""Group video: four heroes of one temperament on one stage (e.g. 紫人组 · NT).

Same beat language as the single-type scene: T(n) = offset + n * eighth (90 BPM reference).
Storyboard: broken star map -> four beams one per beat -> four heroes grow -> title -> four solos
(blueprint / derivation tree / formation / morphing sparks) -> clash -> unite -> raise, star map completes,
crowd rises -> logo.
"""
import json, math, os
import numpy as np, cv2
from .core import (W, H, GY, cl, ramp, eo, eio, lerp, pulse, pop, Palette, Cam, Canvas, flame, Text, F,
                   SERIF_B, SERIF_BL, SANS_M, gold_idx)
from .scene import (MBTIScene, ARM_L, ARM_R, lerp_pose, FLAMES, STARS, CROWD, SHARDS, END_BEAT)

XS = (480, 800, 1120, 1440)      # stage positions, left to right
K = 0.55                          # hero scale on the group stage

_r = np.random.default_rng(23)
# star map: nodes in the sky, edges between near neighbours; four quadrants light separately
NODES = []
while len(NODES) < 26:
    p = (_r.uniform(160, 1760), _r.uniform(70, 400))
    if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 120 ** 2 for q in NODES): NODES.append(p)
EDGES = []
for i, p in enumerate(NODES):
    d = sorted(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2, j) for j, q in enumerate(NODES) if j != i)
    for _, j in d[:2]:
        if (j, i) not in EDGES and (i, j) not in EDGES: EDGES.append((i, j))
BROKEN = [_r.uniform(0.25, 0.6) for _ in EDGES]          # how much of each edge shows before it is completed
def quadrant(p): return min(3, int(p[0] / 480))
SPARK = [(_r.uniform(0, 2 * math.pi), _r.uniform(0.6, 1.4)) for _ in range(40)]


def shape_pts(kind, n=40):
    """outline points for the ENTP morph: question mark, bulb, arrow, star (unit size, centred)"""
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
        for i in range(10):
            r = 0.6 if i % 2 == 0 else 0.25; q = -math.pi / 2 + i * math.pi / 5
            r2 = 0.25 if i % 2 == 0 else 0.6; q2 = -math.pi / 2 + (i + 1) * math.pi / 5
            for s in np.linspace(0, 1, 4, endpoint=False):
                P.append((lerp(r * math.cos(q), r2 * math.cos(q2), s), lerp(r * math.sin(q), r2 * math.sin(q2), s)))
    P = np.array(P, float)
    idx = np.linspace(0, len(P) - 1, n).astype(int)
    return P[idx]
SHAPES = [shape_pts(k) for k in ('q', 'bulb', 'arrow', 'star')]


class SubCam:
    """places a single-hero drawing (world 1920x1080, feet on GY) at stage x with scale k, inside the main camera"""
    def __init__(self, main, x, k):
        self.main, self.x, self.k = main, x, k; self.s = main.s * max(k, 0.85)
        self.cx, self.cy = main.cx, main.cy
    def to_world(self, P): return (np.asarray(P, float) - [960, GY]) * self.k + [self.x, GY]
    def __call__(self, P): return self.main(self.to_world(P))


class GroupScene:
    def __init__(self, gcfg, types_dir, offset=0.367, eighth=1 / 3., logo=None):
        self.g = gcfg; self.off, self.e8 = offset, eighth; self.logo = logo
        self.P = Palette(gcfg.get('palette', 'violet'))
        self.members = []
        for m in gcfg['members']:
            with open(os.path.join(types_dir, m['code'] + '.json'), encoding='utf-8') as f: cfg = json.load(f)
            cfg['palette'] = self.P.name
            sc = MBTIScene(cfg, offset, eighth)
            self.members.append((sc, m['signature']))
        self.duration = self.T(END_BEAT)
        T = self.T
        self.CAMK = [(0, 0, 1.08, 960, 420), (T(1.5), 0.3, 1.0, 960, 520), (T(10), 0.6, 1.25, 960, 600),
                     (T(13), 0.01, 2.6, XS[0], 560), (T(15), 0.18, 2.6, XS[1], 560), (T(17), 0.18, 2.6, XS[2], 560),
                     (T(19), 0.18, 2.6, XS[3], 560), (T(20.5), 0.9, 1.0, 960, 540),
                     (T(31), 0.3, 1.7, XS[0] + 120, 640), (T(38), 0.2, 3.0, XS[1], 560), (T(41), 0.35, 1.7, XS[1] + 120, 560),
                     (T(46), 0.3, 1.45, XS[2], 700), (T(54), 0.3, 1.7, XS[3] - 160, 520),
                     (T(62), 0.25, 1.0, 960, 540), (T(70.5), 0.35, 0.95, 960, 500), (T(79), 1.2, 1.0, 960, 540)]
        c = gcfg['captions']
        def cap(key, t1, t2, te, x, y, tag=None, big2=False):
            l1, l2, g = c[key]; return (l1, l2, t1, t2, te, x, y, gold_idx(l2, g), tag, big2)
        names = [(sc.code, sc.cfg['name_cn']) for sc, _ in self.members]
        self.caps = [cap('open', T(0), T(2), T(6.5), 960, 640), cap('light', T(7), T(8), T(12.5), 960, 640),
                     cap('four', T(13.5), T(15.5), T(22.6), 960, 160),
                     cap('title2', T(26), T(27.5), T(30.6), 330, 170),
                     cap('m0', T(32), T(34), T(37.6), 1460, 300, names[0]), cap('m1', T(38.5), T(42), T(45.6), 1460, 300, names[1]),
                     cap('m2', T(47), T(49), T(53.6), 1660, 190, names[2]), cap('m3', T(55), T(57), T(61.6), 460, 300, names[3]),
                     cap('clash', T(62), T(64), T(66.6), 960, 160), cap('unite', T(67), T(68.5), T(70.6), 960, 160),
                     cap('climax', T(73), T(75), T(76.8), 960, 130), cap('end', T(77), T(78), T(80.4), 960, 300, big2=True)]

    def T(self, n): return self.off + n * self.e8

    # ------------------------------------------------------------ camera
    def camera(self, t):
        T = self.T
        s, cx, cy = self.CAMK[0][2:]
        for (t0, d, s1, x1, y1) in self.CAMK[1:]:
            if t < t0: break
            k = eio(cl((t - t0) / d)) if d > 0 else 1
            s, cx, cy = lerp(s, s1, k), lerp(cx, x1, k), lerp(cy, y1, k)
        q = math.floor((t - self.off) / (2 * self.e8))
        if t > 1.0: s *= 1 + 0.012 * pulse(t, T(2 * q), 0.35)
        if T(62) <= t < T(67):                                   # clash: whip left/right each beat
            n = math.floor((t - T(62)) / self.e8); cx += (90 if n % 2 == 0 else -90) * eo(cl((t - T(62 + n)) * 6))
        for th in (T(2), T(7), T(8), T(9), T(10), T(23), T(72)):
            p = pulse(t, th, 0.25)
            if p > 0.01: cx += 6 * p * math.sin(t * 97); cy += 6 * p * math.cos(t * 83)
        return Cam(s, cx, cy)

    def quarter(self, t): return self.T(2 * math.floor((t - self.off) / (2 * self.e8)))

    # ------------------------------------------------------------ text
    def texts(self, tx, t):
        T, P = self.T, self.P
        for (l1, l2, t1, t2, te, x, y, g2, tag, big2) in self.caps:
            if tag: tx.tag(self.g['group'], f'{tag[0]} {tag[1]}', x, y - 58, t, t1 - 0.03, te)
            tx.chars(l1, x, y, F(SERIF_B, 40), P.WHITE, t, t1, te)
            if big2: tx.chars(l2, x, y + 120, F(SERIF_BL, 96), P.WHITE, t, t2, te, gold=g2, stagger=0.06)
            else: tx.chars(l2, x, y + 56, F(SERIF_B, 40), P.WHITE, t, t2, te, gold=g2)
        if T(23) <= t < T(31.5):
            te = T(31)
            tx.chars(self.g['title'], 960, 330, F(SERIF_BL, 150), P.WHITE, t, T(23), te, stagger=0.07)
            tx.chars(self.g.get('subtitle', ''), 960, 395, F(SERIF_B, 40), (225, 240, 228), t, T(24), te, stagger=0.03, spacing=6)
            names = '  ·  '.join(f"{sc.code} {sc.cfg['name_cn']}" for sc, _ in self.members)
            tx.chars(names, 960, 445, F(SANS_M, 28), P.TAG, t, T(25), te, stagger=0.012)
        b = self.members[0][0].cfg.get('brand', {})
        if b.get('cn') or b.get('en'):
            line = '   '.join(x for x in (' '.join(b.get('cn', '')), ' '.join(b.get('en', ''))) if x)
            tx.chars(line, 960, 690, F(SANS_M, 34), (230, 240, 230), t, T(82), 99, stagger=0.02)
        tx.chars(f"MBTI 系列  ·  {self.g['title']}", 960, 740, F(SANS_M, 20), P.TAG, t, T(83), 99, stagger=0.015)

    # ------------------------------------------------------------ helpers
    def bolt(self, cv, a, b, t, alpha):
        a, b = np.array(a, float), np.array(b, float); d = b - a
        rng = np.random.default_rng(int(t * 30)); lift = 0.35 * abs(d[0])
        pts = [a + d * s + np.array([rng.uniform(-14, 14), -lift * math.sin(s * math.pi) + (rng.uniform(-22, 22) if 0 < s < 1 else 0)]) for s in np.linspace(0, 1, 16)]
        cv.path(pts, self.P.WARM, alpha, 2.4, smooth=False); cv.path(pts, self.P.GOLD, alpha * 0.5, 10, smooth=False, layer=cv.F)
        cv.glow(tuple(pts[8]), 60, self.P.GOLD, alpha)

    # ================================================================ FRAME
    def frame(self, t):
        T, P = self.T, self.P
        G, Wm, LN, SO = P.GOLD, P.WARM, P.LINE, P.SOFT
        cam = self.camera(t); cv = Canvas(cam); tx = Text(P)
        endF = eio(ramp(t, T(79), T(81))); amb = 1 - 0.72 * endF
        qt = self.quarter(t)
        # ---- sky ----
        for (x, y, r, ph, sp, gold) in STARS:
            tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph)); a = tw * 0.6 * amb
            cv.circle((x, y), r * 0.8, LN, a * 0.4, fill=True, layer=cv.F)
        # ---- star map: broken -> quadrants at the title -> complete at T72 ----
        rot = 0.0 if t < T(77) else (t - T(77)) * 0.08
        def node(i):
            x, y = NODES[i]
            if rot: x, y = 960 + (x - 960) * math.cos(rot) - (y - 240) * 0.25 * math.sin(rot), y + (x - 960) * 0.04 * math.sin(rot)
            return (x, y)
        full = eo(ramp(t, T(72), T(72.6)))
        for e, (i, j) in enumerate(EDGES):
            pi_, pj = node(i), node(j); qd = quadrant(NODES[i])
            q_on = eo(ramp(t, T(23) + qd * 0.05, T(23.6) + qd * 0.05)) if t >= T(23) else 0
            frac = max(BROKEN[e], q_on * 0.85, full)
            a = (0.35 + 0.35 * q_on + 0.5 * full + 1.2 * pulse(t, T(72), 0.6)) * amb * eo(ramp(t, 0, 0.8))
            cv.path([pi_, pj], LN if full < 1 else G, a, 1.6, frac, smooth=False)
            if frac < 1: cv.path([pj, pi_], LN, a * 0.6, 1.2, BROKEN[e] * 0.4, smooth=False)
        for i in range(len(NODES)):
            p = node(i); a = (0.6 + 0.6 * full + 0.3 * pulse(t, T(2), 0.4)) * amb
            cv.circle(p, 3.5, Wm, a, fill=True); cv.glow(p, 10, G, 0.35 * a)
        if t < T(7):
            fl = (1 - ramp(t, T(6), T(7))) * eo(ramp(t, 0, 0.3)) * (1 + 0.6 * pulse(t, T(2), 0.4))
            self.members[0][0].star_flare(cv, (960, 240), 70, fl)
        # ---- ground + candles (waves from each landing) ----
        gl = eo(ramp(t, T(6.6), T(7.6)))
        cv.path([(-100, GY), (2020, GY)], LN, 0.7 * amb * gl, 1.6, smooth=False)
        cv.path([(-100, GY), (2020, GY)], LN, 0.22 * amb * gl, 6, smooth=False, layer=cv.F)
        for j, (x, y, h, ph, r) in enumerate(FLAMES):
            ton = min(T(7 + i) + (0 if abs(x - X) < 120 else (self.e8 if abs(x - X) < 320 else 2 * self.e8)) for i, X in enumerate(XS))
            if t < ton: continue
            boost = 1 + 0.5 * ramp(t, T(72), T(72) + 0.3) + 2.0 * pulse(t, ton, 0.25) + (0.25 * pulse(t, qt, 0.3) if t > T(12) else 0)
            a = min(1.6, boost) * amb; hh = h * (1 + 0.12 * math.sin(t * 7 + ph)) * pop(t, ton, 0.16)
            flame(cv, x, y, hh, G, 0.95 * a, lean=0.08 * math.sin(t * 2 + ph)); flame(cv, x, y, hh * 1.6, G, 0.25 * a, layer=cv.F)
        # ---- four beams, one per beat; landing rings ----
        for i, X in enumerate(XS):
            tb = T(7 + i)
            if t >= tb - 0.12:
                bh = eo(ramp(t, tb - 0.12, tb)); ba = (0.4 + 1.6 * pulse(t, tb, 0.5)) * (1 - ramp(t, T(12), T(13)))
                if ba > 0.01:
                    yb = lerp(-100, GY, bh)
                    cv.path([(X, -100), (X, yb)], Wm, ba, 3, smooth=False); cv.path([(X, -100), (X, yb)], G, ba * 0.5, 24, smooth=False, layer=cv.F)
            if t >= tb:
                k = pulse(t, tb, 0.5)
                Pr = [(X + 150 * math.cos(q), GY + 14 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 100)]
                cv.path(Pr, Wm, (0.3 + 1.2 * k) * amb, 2.4, smooth=False); cv.glow((X, GY), 90, G, 0.6 * k)
                if t < tb + 1.2:
                    kk = (t - tb) / 1.2
                    cv.path([(X + (150 + 500 * kk) * math.cos(q), GY + (14 + 40 * kk) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120)], G, (1 - kk) * 0.7, 1.6, smooth=False)

        # ---- per-hero poses ----
        kUp = eio(ramp(t, T(71), T(72)))
        spread = 0.35 * eio(ramp(t, T(67), T(67.7)))
        prog = ramp(t, T(13), T(21))
        heads = []
        for i, ((sc, sig), X) in enumerate(zip(self.members, XS)):
            sub = SubCam(cam, X, K)
            # solo highlight + climax roll-call
            solo = (i == 0 and T(31) <= t < T(38)) or (i == 1 and T(38) <= t < T(46)) or (i == 2 and T(46) <= t < T(54)) or (i == 3 and T(54) <= t < T(62))
            call = pulse(t, T(73 + i), 0.5) * 2.0 if t >= T(73) else 0
            bright = (0.6 if solo else 0) + call + 0.5 * pulse(t, T(65), 0.4)
            kU = kUp
            if sig == 'formation': kU = max(kU, 0.75 * eio(ramp(t, T(47), T(47.6))) * (1 - eio(ramp(t, T(53), T(54)))))
            aL = lerp_pose(ARM_L['rest'], ARM_L['open'], kUp); aR = lerp_pose(ARM_R['rest'], ARM_R['up'], kU)
            cv.cam = sub
            sc.draw_figure(cv, t, (1.0 if t >= T(13) else 0.0) * (1 - 0.8 * endF), prog, aL, aR, spread, bright)
            # prop: drops with its beam
            tb = T(7 + i); fall = eo(ramp(t, tb - 0.12, tb))
            if fall > 0:
                grip = np.array([960, 578.]) if sc.prop == 'sword' else np.array([960, 540.])
                ang = math.pi / 2
                if kU > 0:
                    hand = np.array(aR[-1]); grip = grip + (hand - grip) * kU
                    if sc.prop == 'sword': ang = math.pi / 2 - math.pi * kU
                off = lerp(-1600, 0, fall)
                glow = 0.3 + 0.6 * pulse(t, T(65), 0.4) + (0.8 if kUp >= 1 else 0) + call * 0.4
                head, tip = sc.draw_prop(cv, (grip[0], grip[1] + off), ang, 1.0 * (1 - 0.6 * endF), glow, t)
                if sig == 'tree':      # INTP: extra tilted formula ring around the orb
                    hx, hy = head
                    cv.path([(hx + 40 * math.cos(q) * math.cos(0.9) - 14 * math.sin(q) * math.sin(0.9), hy + 40 * math.cos(q) * math.sin(0.9) + 14 * math.sin(q) * math.cos(0.9))
                             for q in np.linspace(t * 1.6, t * 1.6 + 2 * math.pi, 50)], G, 0.8 * (1 - 0.6 * endF), 1.4, smooth=False)
                heads.append((tuple(sub.to_world([head])[0]), tuple(sub.to_world([tip])[0])))
            else:
                heads.append(((X, 600.), (X, 600.)))
            cv.cam = cam
        face = [(X, GY - (GY - 250) * K) for X in XS]

        # ---- rays linking the four heads (T10) ----
        ra = eo(ramp(t, T(10), T(10.6))) * (1 - ramp(t, T(13), T(14)))
        if ra > 0:
            for i in range(3):
                a, b = np.array(heads[i][0]), np.array(heads[i + 1][0]); m = a + (b - a) * ra
                cv.path([tuple(a), tuple(m)], G, 0.9, 1.8, smooth=False)
            for (h, _) in heads:
                for k in range(10):
                    q = math.pi * (0.1 + 0.8 * k / 9); X = h[0] - 420 * math.cos(q)
                    cv.path([h, (lerp(h[0], X, ra), lerp(h[1], GY + 20, ra))], G, 0.4, 1.1, smooth=False)
        # ---- light rings ----
        for t0, c, r0, r1 in ((T(23), (960, 560), 80, 800), (T(31), (XS[0], 640), 80, 600), (T(38), face[1], 50, 360),
                              (T(47), (XS[2], 640), 80, 600), (T(55), (XS[3], 560), 60, 500), (T(72), (960, 300), 100, 1100)):
            self.members[0][0].ring_burst(cv, t, t0, c, r0, r1, 0.9)
        self.members[0][0].star_flare(cv, (960, 600), 420, pulse(t, T(23), 0.7) * 1.4)

        # ---- solo signatures ----
        X0 = XS[0]; bA = ramp(t, T(31), T(32)) * (1 - 0.75 * ramp(t, T(38), T(39)) - 0.25 * ramp(t, T(61), T(63))) * amb
        if bA > 0:        # INTJ blueprint grid (one cell per beat) + rising city
            n = cl((t - T(32)) / self.e8, 0, 12)
            for k in range(7):
                x = X0 - 360 + k * 120; on = ramp(n, k, k + 0.6)
                cv.path([(x, GY + 4), (X0 + (x - X0) * 1.6, 1080)], LN, 0.5 * bA * on, 1.2, on, smooth=False)
            for k in range(4):
                y = GY + 4 + k * 42; on = ramp(n, 6 + k, 6.6 + k); w = 360 + k * 90
                cv.path([(X0 - w, y), (X0 + w, y)], LN, 0.5 * bA * on, 1.2, on, smooth=False)
            for k, (bx, bw, bh) in enumerate(((X0 - 330, 70, 150), (X0 - 240, 60, 220), (X0 + 180, 80, 190), (X0 + 280, 60, 260), (X0 + 360, 70, 140), (X0 - 400, 50, 110))):
                up = eo(ramp(t, T(33 + k), T(33.6 + k))); hgt = bh * up
                if up > 0:
                    cv.path([(bx, GY), (bx, GY - hgt), (bx + bw, GY - hgt), (bx + bw, GY)], LN, 0.7 * bA, 1.6, smooth=False)
                    for wy in range(int(GY - hgt + 20), GY - 10, 30):
                        cv.path([(bx + 12, wy), (bx + bw - 12, wy)], G, 0.35 * bA, 1.0, smooth=False)
        X1 = XS[1]; tA = ramp(t, T(41.5), T(42)) * (1 - 0.8 * ramp(t, T(46), T(47)) - 0.2 * ramp(t, T(61), T(63))) * amb
        if t >= T(38) and t < T(39):     # glasses glint on the punch-in
            cv.glow((face[1][0] - 9, face[1][1] - 2), 14, P.WARM, 2.0 * pulse(t, T(38), 0.3))
        if tA > 0:        # INTP derivation tree, one level per beat
            root = heads[1][0]; levels = [[root]]
            for lv in range(4):
                nxt = []
                for p in levels[-1]:
                    for s in (-1, 1): nxt.append((p[0] + s * 110 / (lv + 1) ** 0.7, p[1] - 70))
                levels.append(nxt)
            for lv in range(1, 5):
                on = eo(ramp(t, T(41 + lv), T(41.4 + lv)))
                if on <= 0: continue
                for k, p in enumerate(levels[lv]):
                    par = levels[lv - 1][k // 2]
                    cv.path([par, p], G, 0.8 * tA, 1.4, on, smooth=False)
                    if on >= 1: cv.circle(p, 3.5, Wm, tA, fill=True)
            if t >= T(45):
                for k, p in enumerate(levels[4][::3]):
                    q = cam([p])[0]; sym = '?√∞π'[k % 4]
                    a = eo(ramp(t, T(45) + k * 0.04, T(45.5) + k * 0.04)) * tA
                    tx.d.text((q[0], q[1] - 12), sym, font=F(SERIF_B, int(30 * cam.s / 1.7)), fill=tuple(P.HI) + (int(255 * a),), anchor='ms')
        X2 = XS[2]; fA = ramp(t, T(47), T(48)) * (1 - 0.7 * ramp(t, T(54), T(55)) - 0.3 * ramp(t, T(61), T(63))) * amb
        if fA > 0:        # ENTJ formation: a row of light points per beat, marching forward
            for row in range(6):
                tr = T(48 + row)
                if t < tr: continue
                y = GY + 150 - row * 22; sc_ = 1 - row * 0.09
                for c_ in range(9):
                    x = X2 + (c_ - 4) * 52 * sc_
                    self.members[2][0].person(cv, x, y + 30, 0.55 * sc_ * pop(t, tr, 0.15), Wm, fA * (0.7 + 0.6 * pulse(t, tr, 0.3)))
                    cv.glow((x, y), 14, G, 0.5 * fA * pulse(t, tr, 0.3))
        X3 = XS[3]; mA = ramp(t, T(55), T(55.5)) * (1 - ramp(t, T(61), T(63))) * amb
        if mA > 0:        # ENTP sparks: scatter, then a new shape each beat
            c0 = np.array([X3, 300.]); size = 110
            k = int(cl((t - T(56)) / self.e8, -1, 3)); s = cl((t - T(56 + max(k, 0))) * 6)
            for idx in range(40):
                q, v = SPARK[idx]
                scat = c0 + np.array([math.cos(q), math.sin(q)]) * 160 * v
                if k < 0: p = heads[3][0] + (scat - np.array(heads[3][0])) * eo(ramp(t, T(55), T(56)))
                else:
                    prev = scat if k == 0 else c0 + SHAPES[k - 1][idx] * size
                    p = prev + (c0 + SHAPES[k][idx] * size - prev) * eo(s)
                cv.circle(tuple(p), 3.2, Wm, mA, fill=True); cv.glow(tuple(p), 9, G, 0.5 * mA)
            if k >= 0 and s >= 0.99:
                cv.path([tuple(c0 + p * size) for p in SHAPES[k]], G, 0.5 * mA, 1.2, smooth=False)

        # ---- clash (one bolt per beat, pairs alternate) ----
        if T(62) <= t < T(67):
            n = math.floor((t - T(62)) / self.e8); a = pulse(t, T(62 + n), 0.25) + 0.25
            pair = ((0, 3), (2, 1))[n % 2]
            self.bolt(cv, heads[pair[0]][0], heads[pair[1]][0], t, a)
        # ---- unite: lines converge to one point ----
        ua = eo(ramp(t, T(67), T(68))) * (1 - ramp(t, T(71), T(72)))
        if ua > 0:
            ctr = (960, 380)
            for (h, _) in heads:
                m = (lerp(h[0], ctr[0], ua), lerp(h[1], ctr[1], ua)); cv.path([h, m], Wm, 0.9, 2, smooth=False)
            cv.glow(ctr, 40 + 40 * ua, G, ua)
        if T(69) <= t < T(69) + 1.2:
            k = (t - T(69)) / 1.2
            for (q, r, s_, ph) in SHARDS:
                rr = r * eo(k) + 100; x, y = 960 + rr * math.cos(q), 480 + rr * 0.8 * math.sin(q)
                Pp = [(x + s_ * math.cos(ph + t * 3 + i * 2.1), y + s_ * math.sin(ph + t * 3 + i * 2.1)) for i in range(3)]
                cv.path(Pp + [Pp[0]], G, 1 - k, 1.6, smooth=False)
        # ---- climax: four sky beams into the star map ----
        if t >= T(72) - 0.1:
            sb = (0.5 + 1.6 * pulse(t, T(72), 0.6)) * (1 - 0.7 * endF)
            up = eo(ramp(t, T(72) - 0.1, T(72)))
            for (_, tip) in heads:
                yb = lerp(tip[1], -100, up)
                cv.path([tip, (tip[0], yb)], Wm, sb, 3, smooth=False); cv.path([tip, (tip[0], yb)], G, sb * 0.45, 26, smooth=False, layer=cv.F)
        if t >= T(71.5):
            for (x, y, s, row) in CROWD:
                d = abs(x - 960) / 960
                tr = T(72) + (0 if d < 0.25 else (self.e8 if d < 0.6 else 2 * self.e8)) + row * 0.03
                if t < tr: continue
                up = eo(ramp(t, tr, tr + 0.18)); a = (0.9 + 0.8 * pulse(t, tr, 0.3)) * (1 - 0.6 * endF)
                self.members[0][0].person(cv, x, y + 40 + (1 - up) * 90, s * 0.8, SO * 0.6 + LN * 0.4, a * up, a * up, t)
        # ---- end ring + logo ----
        lead = self.members[0][0]
        if t >= T(81) - 0.1:
            ec = cv.cam; cv.cam = Cam(1.0)
            lead.ring_burst(cv, t, T(81), (960, 560), 60, 260, 1.0)
            k = eo(ramp(t, T(81), T(82)))
            cv.path([(960 + 175 * math.cos(q), 560 + 175 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120)], G, 0.45 * k, 1.4, smooth=False)
            for i in range(36):
                q = i / 36 * 2 * math.pi
                cv.path([(960 + 182 * math.cos(q), 560 + 182 * math.sin(q)), (960 + 194 * math.cos(q), 560 + 194 * math.sin(q))], G, 0.5 * k, 1.2, smooth=False)
            if self.logo is None: lead.eye_logo(cv, (960, 560), 2.2, 1.0, k)
            cv.cam = ec
        self.texts(tx, t)
        flash = 0.06 * sum(pulse(t, T(7 + i), 0.3) for i in range(4)) + 0.16 * pulse(t, T(23), 0.5) + 0.08 * pulse(t, T(38), 0.3) + \
                0.10 * pulse(t, T(69), 0.4) + 0.22 * pulse(t, T(72), 0.6)
        img = cv.composite(P.BG, flash) * P.VIG
        if self.logo is not None and t >= T(81):
            lead.logo = self.logo; img = lead._put_logo(img, 960, 560, 170, 1.0, eo(ramp(t, T(81), T(82))))
        img = tx.blend(img)
        img *= 1 - ramp(t, self.duration - 0.35, self.duration - 0.05)
        return np.clip(img * 255, 0, 255).astype(np.uint8)
