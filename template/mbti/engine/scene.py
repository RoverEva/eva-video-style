"""MBTI glowing line-art music video — one continuous scene, every beat-locked moment defined in beats.

All times below are in *eighth-note beats* n and converted with T(n) = offset + n * eighth,
so the template follows any track once its grid is measured (see beats.py).
"""
import math
import numpy as np, cv2
from .heads import draw_head
from .core import (W, H, GY, cl, ramp, eo, eio, lerp, pulse, pop, spline, mir, offset_line, Palette,
                   GROUP_PALETTE, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, gold_idx)

TRAITS = {'E': '外向', 'I': '内向', 'N': '直觉', 'S': '实感', 'T': '思考', 'F': '情感', 'J': '判断', 'P': '感知'}
END_BEAT = 87          # video length in eighths (29.37 s at 90 BPM)

# ---------------------------------------------------------------- static random fields (seeded)
_rng = np.random.default_rng(7)
STARS = [(_rng.uniform(0, W), _rng.uniform(0, 860), _rng.uniform(1, 3.2), _rng.uniform(0, 6.28), _rng.uniform(0.6, 2.2),
          _rng.random() < 0.35) for _ in range(110)]
FLAMES = []
for _ in range(150):
    x = _rng.uniform(-20, 1940); row = _rng.random()
    FLAMES.append((x, 935 + row * 70, 12 + row * 14, _rng.uniform(0, 6.28), _rng.uniform(0, 1)))
FLAMES.sort(key=lambda f: f[0])
HILLS = [[(x, 735 + 22 * math.sin(x / 210 + k) + 14 * math.sin(x / 77 + 2 * k) + k * 18) for x in range(-40, 1980, 60)] for k in range(2)]
_r2 = np.random.default_rng(11)
CROWD = []
for row, (y, s, n) in enumerate(((952, 1.3, 30), (1000, 1.7, 24), (1062, 2.2, 18))):
    for i in range(n):
        CROWD.append(((i + 0.5 + _r2.uniform(-0.3, 0.3)) * W / n, y, s, row))
STREAKS = [(_r2.uniform(0, 2 * math.pi), _r2.uniform(0, 1), _r2.uniform(0.7, 1.4)) for _ in range(70)]
SHARDS = [(_r2.uniform(0, 2 * math.pi), _r2.uniform(250, 900), _r2.uniform(8, 18), _r2.uniform(0, 6.28)) for _ in range(40)]
SKY = [(_r2.uniform(1150, 1880), _r2.uniform(0, 1)) for _ in range(6)]

# ---------------------------------------------------------------- figure geometry (front view, hooded hero)
HOOD = [(905, 330), (892, 270), (898, 205), (925, 168), (960, 158), (995, 168), (1022, 205), (1028, 270), (1015, 330)]
FACE = [(960, 198), (990, 215), (996, 255), (982, 292), (960, 302), (938, 292), (924, 255), (930, 215)]
DRAPE_L = [(905, 330), (880, 352), (842, 374), (815, 398)]
TUNIC_L = [(872, 405), (862, 600), (852, 780), (846, 905)]
MANTLE = [(838, 378), (862, 420), (902, 438), (930, 428), (960, 444), (990, 428), (1018, 438), (1058, 420), (1082, 378)]
ARM_L = {'rest': [(860, 410), (842, 480), (884, 520), (945, 500)],
         'offer': [(860, 410), (820, 470), (790, 530), (760, 560)],
         'open': [(860, 410), (800, 460), (730, 510), (670, 528)]}
ARM_R = {'rest': mir(ARM_L['rest']), 'up': [(1060, 410), (1112, 340), (1128, 255), (1124, 178)]}


def lerp_pose(A, B, k): return [(lerp(a[0], b[0], k), lerp(a[1], b[1], k)) for a, b in zip(A, B)]
def cloak_pts(sp): return [(815, 398), (792 - 60 * sp, 500), (772 - 160 * sp, 650), (750 - 260 * sp, 800), (728 - 330 * sp, 905)]


class MBTIScene:
    def __init__(self, cfg, offset=0.367, eighth=1 / 3., logo=None):
        self.cfg = cfg
        self.code = cfg['code'].upper()
        self.L = list(self.code)
        group = ('N' + self.L[2]) if self.L[1] == 'N' else ('S' + self.L[3])
        self.P = Palette(cfg.get('palette') or GROUP_PALETTE[group])
        self.prop = cfg.get('prop', 'sword')
        self.look = cfg.get('look', {'hair': 'hood'})
        self.off, self.e8 = offset, eighth
        self.duration = self.T(END_BEAT)
        self.logo = logo     # optional BGR float image (brand logo), else a drawn eye
        T = self.T
        # camera keyframes: (start, duration, scale, cx, cy)
        self.CAMK = [(0, 0, 1.10, 960, 470), (T(1.5), 0.25, 1.0, 960, 540), (T(10), 1.0, 1.75, 960, 560),
                     (T(13), 0.01, 2.3, 960, 560), (T(13.2), 1.4, 2.1, 960, 300), (T(17.5), 1.6, 1.12, 960, 520),
                     (T(23), 0.35, 1.0, 960, 540), (T(38), 0.25, 2.1, 960, 330), (T(41), 0.4, 1.0, 1060, 560),
                     (T(46), 0.3, 1.45, 880, 470), (T(54), 0.35, 0.78, 1240, 600), (T(62), 0.3, 1.22, 960, 520),
                     (T(70.5), 0.35, 0.92, 960, 520), (T(79), 1.2, 0.98, 960, 540)]
        # candles: three singles first, then waves by distance from the centre
        self.single = {}
        for tt, x0 in ((T(3), 1010), (T(5), 900), (T(6), 1080)):
            j = int(np.argmin([abs(f[0] - x0) + (0 if f[1] < 960 else 500) for f in FLAMES])); self.single[j] = tt
        self._build_text()

    def T(self, n): return self.off + n * self.e8

    # hooks for derived series (zodiac): extra sky drawing and a custom title badge
    custom_badge = False
    def extra_sky(self, cv, t): pass
    def title_badge(self, img, t): return img

    # ------------------------------------------------------------ captions
    def _build_text(self):
        T, c, L = self.T, self.cfg['captions'], self.L
        slots = [  # key, t_line1, t_line2, t_end, x, y, tag
            ('open', T(0), T(2), T(6.5), 700, 300, None),
            ('light', T(7), T(8), T(12.5), 1460, 300, None),
            ('speak', T(13.5), T(17), T(21.8), 1480, 520, None),
            ('title', T(25), T(26.5), T(30.6), 470, 470, None),
            ('s1', T(32), T(34), T(37.6), 1500, 440, 0),
            ('s2', T(38.5), T(42), T(45.6), 1480, 440, 1),
            ('s3', T(47), T(49.5), T(53.6), 1430, 470, 2),
            ('s4', T(55), T(57), T(61.6), 1450, 290, 3),
            ('low', T(62.5), T(65), T(70.4), 1500, 420, None),
            ('climax', T(71), T(73), T(76.6), 1460, 300, None)]
        self.caps = []
        for key, t1, t2, te, x, y, tag in slots:
            l1, l2, g = c[key][0], c[key][1], (c[key][2] if len(c[key]) > 2 else '')
            tg = (L[tag], TRAITS[L[tag]]) if tag is not None else None
            self.caps.append((l1, l2, t1, t2, te, x, y, gold_idx(l2, g), tg))

    def texts(self, tx, t):
        T, P, cfg = self.T, self.P, self.cfg
        for l1, l2, t1, t2, te, x, y, g2, tag in self.caps:
            if tag: tx.tag(tag[0], tag[1], x, y - 58, t, t1 - 0.03, te)
            fs = 40 if max(len(l1), len(l2)) <= 11 else 36
            tx.chars(l1, x, y, F(SERIF_B, fs), P.WHITE, t, t1, te)
            tx.chars(l2, x, y + 56, F(SERIF_B, fs), P.WHITE, t, t2, te, gold=g2)
        if T(23) <= t < T(31.5):
            te = T(31); x0 = 1500
            tx.chars(' '.join(self.L), x0, 645, F(SERIF_B, 64), (225, 240, 228), t, T(23), te, stagger=0.03, spacing=8)
            name = cfg['name_cn']
            tx.chars(name, x0, 810, F(SERIF_BL, 150 if len(name) <= 3 else 120), P.WHITE, t, T(23.5), te, stagger=0.06)
            tags = '  ·  '.join(f'{l} {TRAITS[l]}' for l in self.L)
            tx.chars(tags, x0, 880, F(SANS_M, 30), (225, 240, 228), t, T(25), te, gold=(0, 7, 14, 21), stagger=0.012)
        pre = cfg.get('ending_pre', '他就是')
        tx.chars(pre, 1470, 400, F(SERIF_B, 44), P.WHITE, t, T(77), T(79.6), stagger=0.04)
        tx.chars(f"{self.code} {cfg['name_cn']}", 1470, 520, F(SERIF_BL, 100), P.HI, t, T(78), T(79.6), stagger=0.05)
        b = cfg.get('brand', {})
        if b.get('cn') or b.get('en'):
            line = '   '.join(x for x in (' '.join(b.get('cn', '')), ' '.join(b.get('en', ''))) if x)
            tx.chars(line, 960, 690, F(SANS_M, 34), (230, 240, 230), t, T(82), 99, stagger=0.02)
        tx.chars(f"MBTI 系列  ·  {self.code} {cfg['name_cn']}", 960, 740, F(SANS_M, 20), P.TAG, t, T(83), 99, stagger=0.015)

    # ------------------------------------------------------------ camera
    def camera(self, t):
        T = self.T
        s, cx, cy = self.CAMK[0][2:]
        for (t0, d, s1, x1, y1) in self.CAMK[1:]:
            if t < t0: break
            k = eio(cl((t - t0) / d)) if d > 0 else 1
            s, cx, cy = lerp(s, s1, k), lerp(cx, x1, k), lerp(cy, y1, k)
        q = math.floor((t - self.off) / (2 * self.e8))
        if t > 1.0: s *= 1 + 0.012 * pulse(t, T(2 * q), 0.35)          # quarter-beat bump
        for th in (T(2), T(7), T(23), T(72)):                          # micro shake on big hits
            p = pulse(t, th, 0.25)
            if p > 0.01: cx += 6 * p * math.sin(t * 97); cy += 6 * p * math.cos(t * 83)
        return Cam(s, cx, cy)

    def quarter(self, t):
        return self.T(2 * math.floor((t - self.off) / (2 * self.e8)))

    # ------------------------------------------------------------ drawing helpers
    def tpath(self, cv, pts, col, a, th, frac, smooth=True, closed=False):
        cv.path(pts, col, a, th, frac, smooth=smooth, closed=closed)
        if 0 < frac < 1 and a > 0.05:
            P = spline(pts, closed=closed) if smooth and len(pts) > 2 else np.array(pts, float)
            seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
            Ln = cum[-1] * frac; k = min(max(1, int(np.searchsorted(cum, Ln))), len(P) - 1)
            r = (Ln - cum[k - 1]) / max(seg[k - 1], 1e-6); p = P[k - 1] + (P[k] - P[k - 1]) * r
            cv.circle(tuple(p), 4.5, self.P.WARM, a, fill=True); cv.glow(tuple(p), 16, self.P.GOLD, 0.8 * a)

    def ring_burst(self, cv, t, t0, c, r0, r1, dur=0.9):
        if t < t0 or t > t0 + dur: return
        G = self.P.GOLD; k = (t - t0) / dur; r = lerp(r0, r1, eo(k)); a = (1 - k) ** 1.3
        P = [(c[0] + r * math.cos(q), c[1] + r * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 220)]
        cv.path(P, G, a, 2.2, smooth=False); cv.path(P, G, a * 0.3, 8, smooth=False, layer=cv.F)
        for i in range(24):
            q = i / 24 * 2 * math.pi
            cv.path([(c[0] + (r + 8) * math.cos(q), c[1] + (r + 8) * math.sin(q)),
                     (c[0] + (r + 26) * math.cos(q), c[1] + (r + 26) * math.sin(q))], G, a * 0.8, 1.6, smooth=False)

    def star_flare(self, cv, c, size, a):
        if a <= 0.01: return
        x, y = c; G, Wm = self.P.GOLD, self.P.WARM
        cv.glow(c, size * 0.1, Wm, 1.4 * a); cv.glow(c, size * 0.35, G, 0.5 * a)
        for ang, Ln in ((0, 1.0), (math.pi / 2, 0.85), (math.pi / 4, 0.35), (-math.pi / 4, 0.35)):
            dx, dy = math.cos(ang) * size * Ln, math.sin(ang) * size * Ln
            cv.path([(x - dx, y - dy), (x + dx, y + dy)], G, a * 0.5, 3, smooth=False, layer=cv.F)
            cv.path([(x - dx * .6, y - dy * .6), (x + dx * .6, y + dy * .6)], Wm, a * 0.9, 1.6, smooth=False)

    # ------------------------------------------------------------ prop (sword / lantern / star / orb staff)
    def draw_prop(self, cv, anchor, ang, a, glow, t):
        """anchor = grip point.  Returns (head, beam_tip): head receives the falling beam and emits rays,
        beam_tip is where the sky beam starts after the raise."""
        P = self.P; G, Wm = P.GOLD, P.WARM
        h = np.array(anchor, float)
        if self.prop == 'sword':
            d = np.array([math.cos(ang), math.sin(ang)]); n = np.array([-d[1], d[0]])
            tip = h + d * 330; w = 14
            blade = [h + n * w + d * 6, tip - d * 30 + n * w * 0.9, tip, tip - d * 30 - n * w * 0.9, h - n * w + d * 6]
            cv.poly(blade, G * (0.08 + 0.4 * glow), a, layer=cv.F)
            cv.path(blade, Wm, a, 2.2, smooth=False); cv.path([h + d * 10, tip - d * 36], Wm, a * 0.55, 1.2, smooth=False)
            cv.path([h + n * 66 - d * 4, h + n * 60 + d * 4, h - n * 60 + d * 4, h - n * 66 - d * 4], Wm, a, 2.4, smooth=False)
            g0, g1 = h - d * 8, h - d * 52
            cv.path([g0 + n * 6, g1 + n * 6], G, a, 2, smooth=False); cv.path([g0 - n * 6, g1 - n * 6], G, a, 2, smooth=False)
            pm = h - d * 64; cv.circle(tuple(pm), 12, Wm, a, 2.2)
            if glow > 0:
                cv.path([h, tip], Wm, glow * a, 6, smooth=False, layer=cv.F)
                cv.glow(tuple((h + tip) / 2), 150, G, 0.35 * glow * a)
            return pm, tip
        # staffs stay vertical: rod from the head down to the ground
        top = h + np.array([0, -120.]); bottom = h + np.array([0, 340.])
        cv.path([tuple(top + [0, 24]), tuple(bottom)], Wm, a, 2.4, smooth=False)
        cv.path([tuple(top + [-5, 30]), tuple(bottom + [-5, 0])], G, a * 0.4, 1.2, smooth=False)
        if glow > 0:
            cv.path([tuple(top), tuple(bottom)], Wm, glow * a * 0.6, 6, smooth=False, layer=cv.F)
        x, y = top
        if self.prop == 'lantern':
            k = 0.95
            S = lambda Q: [(x + px * k, y + py * k) for px, py in Q]
            cv.path(S([(-26, -48), (26, -48), (36, -38), (-36, -38), (-26, -48)]), G, a, 2.2, smooth=False)
            cv.path(S([(-30, -38), (-25, 38), (25, 38), (30, -38)]), G, a, 2.2, smooth=False)
            for px in (-10, 10): cv.path(S([(px, -38), (px * 0.85, 38)]), G, a * 0.6, 1.5, smooth=False)
            cv.path(S([(-34, 38), (34, 38), (24, 50), (-24, 50), (-34, 38)]), G, a, 2.2, smooth=False)
            cv.circle((x, y - 64 * k), 6, G, a, 2)
            fl = 1 + 0.06 * math.sin(t * 40)
            flame(cv, x, y + 22, 40 * fl, Wm, a, layer=cv.F); flame(cv, x, y + 18, 28 * fl, np.array([0.85, 1, 1.0]), a)
            cv.glow((x, y), 60, G, 0.55 * a); cv.glow((x, y), 200, G, 0.12 * a + 0.2 * glow * a)
        elif self.prop == 'star':
            r = 34 + 4 * math.sin(t * 3)
            pts = []
            for i in range(8):
                rr = r if i % 2 == 0 else r * 0.32; q = i * math.pi / 4 - math.pi / 2
                pts.append((x + rr * math.cos(q), y + rr * math.sin(q)))
            cv.path(pts + [pts[0]], Wm, a, 2.2, smooth=False); cv.poly(pts, G * 0.3, a, layer=cv.F)
            cv.circle((x, y), 46, G, a * 0.5, 1.2); cv.glow((x, y), 60, G, 0.6 * a + 0.4 * glow * a)
        else:  # orb
            cv.circle((x, y), 26, Wm, a, 2.2); cv.circle((x, y), 12, Wm, a, fill=True, layer=cv.F)
            q0 = t * 1.2
            ring = [(x + 46 * math.cos(q), y + 14 * math.sin(q)) for q in np.linspace(q0, q0 + 2 * math.pi, 60)]
            cv.path(ring, G, a * 0.8, 1.6, smooth=False)
            cv.path([(x - 18, y + 26), (x, y + 40), (x + 18, y + 26)], G, a, 2, smooth=False)
            cv.glow((x, y), 60, G, 0.6 * a + 0.4 * glow * a)
        return tuple(top), tuple(top)

    # ------------------------------------------------------------ figure
    def draw_arm(self, cv, pts, a, frac):
        A, B = offset_line(pts, 20, 13)
        self.tpath(cv, A, self.P.LINE, a, 2.2, frac, smooth=False); self.tpath(cv, B, self.P.LINE, a, 2.2, frac, smooth=False)
        if frac >= 0.98: cv.circle(tuple(np.array(pts[-1])), 11, self.P.SOFT, a * 0.9, 2)

    def draw_figure(self, cv, t, a, prog, armL, armR, spread=0.0, bright=0.0):
        if a <= 0: return
        P = self.P; tp = self.tpath
        st = lambda i, n=8: eio(ramp(prog, i / n, (i + 2.0) / n))
        cb = P.LINE * (1 + 0.6 * bright)
        self.draw_arm(cv, armL, a, st(0)); self.draw_arm(cv, armR, a, st(0))
        tp(cv, DRAPE_L, cb, a, 2.2, st(1)); tp(cv, mir(DRAPE_L), cb, a, 2.2, st(1))
        tp(cv, MANTLE, P.GOLD, a, 2.4, st(1.5))
        cv.poly(spline(MANTLE + [(1060, 390), (960, 360), (860, 390)], closed=True), P.GOLD * 0.08, a * st(1.5), layer=cv.F)
        draw_head(self, cv, self.look, a, st(2.5), st(3) if st(3) > 0.3 else 0.0)
        c_ = cloak_pts(spread)
        tp(cv, c_, cb, a, 2.4, st(4)); tp(cv, mir(c_), cb, a, 2.4, st(4))
        hem = [c_[-1], (800 - 200 * spread, 916), (880, 906), (960, 917), (1040, 906), (1120 + 200 * spread, 916), (W - c_[-1][0], c_[-1][1])]
        tp(cv, hem, cb, a, 2.2, st(5.5))
        tp(cv, TUNIC_L, cb, a * 0.75, 1.8, st(4.5)); tp(cv, mir(TUNIC_L), cb, a * 0.75, 1.8, st(4.5))
        tp(cv, [(925, 322), (960, 382), (995, 322)], P.SOFT, a * 0.8, 1.8, st(3))
        for xx in (800, 1120):
            cv.path([(xx + (960 - xx) * 0.35, 430), (lerp(xx, 960 + (xx - 960) * 1.6, spread), 900)], P.LINE, a * 0.25, 1.2, st(5.5), smooth=False)
        body = spline(HOOD[:1] + DRAPE_L[1:] + c_[1:] + hem[1:-1] + mir(c_)[::-1][:-1] + mir(DRAPE_L)[::-1][:-1] + HOOD[-1:][::-1], n=4)
        cv.poly(body, P.LINE * (0.05 + 0.08 * bright), a * st(5), layer=cv.F)
        if bright > 0: cv.glow((960, 480), 320, P.LINE, 0.12 * bright * a)

    def person(self, cv, x, y, s, col, a, flame_a=0.0, t=0):
        head = [(x + 11 * s * math.cos(q), y - 62 * s + 13 * s * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 18)]
        body = [(x - 26 * s, y), (x - 22 * s, y - 30 * s), (x - 10 * s, y - 44 * s), (x + 10 * s, y - 44 * s),
                (x + 22 * s, y - 30 * s), (x + 26 * s, y)]
        cv.path(head, col, a, 1.6, smooth=False); cv.path(body, col, a, 1.6)
        if flame_a > 0:
            flame(cv, x + 16 * s, y - 30 * s, 16 * s * (1 + 0.1 * math.sin(t * 9 + x)), self.P.GOLD, flame_a)
            cv.glow((x + 16 * s, y - 36 * s), 14 * s, self.P.GOLD, 0.5 * flame_a)

    def flag(self, cv, x, y, h, a, unfurl, t):
        L = self.P.LINE
        cv.path([(x, y), (x, y - h)], L, a, 2, smooth=False)
        if unfurl > 0:
            w = 90 * unfurl; Pp = [(x, y - h)]
            for s in np.linspace(0, 1, 10): Pp.append((x + w * s, y - h + 6 + 8 * math.sin(s * 4 + t * 3) * s))
            for s in np.linspace(1, 0, 10): Pp.append((x + w * s, y - h + 52 + 8 * math.sin(s * 4 + t * 3 + 0.5) * s))
            cv.path(Pp + [(x, y - h + 52)], L, a, 2, smooth=False); cv.poly(Pp + [(x, y - h + 52)], L * 0.15, a, layer=cv.F)
            cv.circle((x + w * 0.45, y - h + 30), 5, self.P.SOFT, a * unfurl, 1.4)

    def eye_logo(self, cv, c, sc, a, frac=1.0):
        x, y = c; S, G = self.P.SOFT, self.P.GOLD
        top = [(x - 46 * sc, y), (x - 20 * sc, y - 20 * sc), (x, y - 25 * sc), (x + 20 * sc, y - 20 * sc), (x + 46 * sc, y)]
        bot = [(px, 2 * y - py) for px, py in top]
        cv.path(top, S, a, 2.2 * sc, frac); cv.path(bot, S, a, 2.2 * sc, frac)
        cv.circle((x, y), 13 * sc, S, a * min(1, frac * 1.5), 2 * sc); cv.circle((x, y), 5 * sc, G, a * min(1, frac * 2), fill=True)

    def candle_on(self, j, x):
        T = self.T
        if j in self.single: return self.single[j]
        d = abs(x - 960)
        if d < 260: return T(7)
        if d < 620: return T(8)
        return T(9) + (0.0 if d < 900 else 0.034)

    # ================================================================ FRAME
    def frame(self, t):
        T, P = self.T, self.P
        G, Wm, LN, SO = P.GOLD, P.WARM, P.LINE, P.SOFT
        cv = Canvas(self.camera(t)); tx = Text(P)
        endF = eio(ramp(t, T(79), T(81))); amb = 1 - 0.72 * endF

        # ---- sky ----
        for (x, y, r, ph, sp, gold) in STARS:
            tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph)); a = tw * (0.6 + 0.4 * ramp(t, T(7), T(9))) * amb
            yy = y + 4 * math.sin(t * 0.4 + ph)
            cv.circle((x, yy), r, G if gold else LN, a * 0.5, fill=True, layer=cv.F); cv.circle((x, yy), r * 0.45, SO, a * 0.55, fill=True)
        if t < T(2.5):
            self.star_flare(cv, (960, 90), 60 * (1 + 0.3 * math.sin(t * 9)), (1 - ramp(t, T(1), T(2))) * eo(ramp(t, 0, 0.3)))
        self.extra_sky(cv, t)
        hk = ramp(t, T(7), T(10))
        for k, hp in enumerate(HILLS): cv.path(hp, P.DIM, 0.5 * hk * amb * (1 - 0.3 * k), 1.4, hk, smooth=False)

        # ---- ground, landing ring, ripples ----
        gl = eo(ramp(t, T(1.8), T(3)))
        cv.path([(-100, GY), (2020, GY)], LN, 0.7 * amb * gl, 1.6, smooth=False)
        cv.path([(-100, GY), (2020, GY)], LN, 0.22 * amb * gl, 6, smooth=False, layer=cv.F)
        if t >= T(2):
            k = pulse(t, T(2), 0.5)
            Pr = [(960 + 260 * math.cos(q), GY + 22 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 160)]
            cv.path(Pr, Wm, 0.5 + 1.2 * k, 3, smooth=False); cv.path(Pr, G, 0.6 * k + 0.1, 12, smooth=False, layer=cv.F)
            cv.glow((960, GY), 140, G, 0.6 * k)
        for t0, rr in ((T(2), 1.0), (T(2.6), 1.2), (T(31), 1.3), (T(72), 2.2)):
            if t0 <= t < t0 + 1.4:
                for j in range(3):
                    kk = cl((t - t0) / 1.4 * 1.3 - j * 0.15)
                    if kk <= 0: continue
                    ax, ay = 120 + kk * 900 * rr, 12 + kk * 60 * rr
                    cv.path([(960 + ax * math.cos(q), GY + ay * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 140)],
                            G if j == 0 else LN, (1 - kk) * 0.8, 2, smooth=False)

        # ---- candles: singles, then waves on T(7) T(8) T(9) ----
        qt = self.quarter(t)
        for j, (x, y, h, ph, r) in enumerate(FLAMES):
            ton = self.candle_on(j, x)
            if t < ton: continue
            beatb = 0.25 * pulse(t, qt, 0.3) if t > T(10) else 0
            boost = 1 + 0.5 * ramp(t, T(72), T(72) + 0.3) + 2.0 * pulse(t, ton, 0.25) + beatb
            a = min(1.6, boost) * amb; hh = h * (1 + 0.12 * math.sin(t * 7 + ph)) * pop(t, ton, 0.16)
            flame(cv, x, y, hh, G, 0.95 * a, lean=0.08 * math.sin(t * 2 + ph)); flame(cv, x, y, hh * 1.6, G, 0.25 * a, layer=cv.F)

        # ---- prop anchor (grip), needed for beam / rays ----
        kUp = eio(ramp(t, T(71), T(72)))
        grip_rest = np.array([960, 578.]) if self.prop == 'sword' else np.array([960, 540.])
        head_rest = (960, 514) if self.prop == 'sword' else (960, 420)

        # ---- beam falls on the prop head (T7) ----
        if t >= T(6.6):
            bh = eo(ramp(t, T(6.6), T(7))); ba = (0.4 + 1.6 * pulse(t, T(7), 0.5)) * (1 - ramp(t, T(10), T(12)))
            if ba > 0.01:
                yb = lerp(-100, head_rest[1] - 40, bh)
                cv.path([(960, -100), (960, yb)], Wm, ba, 3, smooth=False); cv.path([(960, -100), (960, yb)], G, ba * 0.5, 30, smooth=False, layer=cv.F)
                cv.glow((960, head_rest[1] - 40), 90, Wm, 0.8 * ba)
        # ---- rays fan out (T10) ----
        ra = eo(ramp(t, T(10), T(10.6))) * (1 - ramp(t, T(13), T(14)))
        if ra > 0:
            hy = head_rest[1] - 60
            for i in range(36):
                q = math.pi * (0.04 + 0.92 * i / 35); X = 960 - 1500 * math.cos(q)
                cv.path([(960, hy), (lerp(960, X, ra), lerp(hy, GY + 20, ra))], G, 0.5 + 0.3 * math.sin(i * 2.3), 1.3, smooth=False)
            cv.glow((960, hy), 50 + 40 * pulse(t, T(12), 0.5), Wm, 0.5 + 0.7 * pulse(t, T(12), 0.5))

        # ---- mandorla, halo, ground ring (title on) ----
        md = eio(ramp(t, T(23.3), T(24.6))); spread = eio(ramp(t, T(67), T(67.7)))
        if md > 0:
            ma = md * amb
            def egg(sc):
                out = []
                for q in np.linspace(-math.pi, math.pi, 180):
                    w = (300 + 120 * spread) * sc * (1 - 0.13 * math.cos(q))
                    out.append((960 + w * math.sin(q), 495 - 420 * sc * math.cos(q) + (1 - sc) * 420))
                return out
            E1 = egg(1.0)
            cv.path(E1, LN, 0.85 * ma, 2.2, md, smooth=False); cv.path(egg(0.93), LN, 0.3 * ma, 1.2, md, smooth=False)
            for i in range(0, 180, 6):
                x, y = E1[i]
                if y < GY - 10 and i / 6 < int(md * 30):
                    flame(cv, x, y + 6, 15 * pop(t, T(23.3) + (i / 180) * 1.3 * self.e8 * 3, 0.15) * (1 + 0.1 * math.sin(t * 6 + i)), G, 0.9 * ma)
            hc = (960, 238)
            cv.circle(hc, 92, G, 0.7 * ma, 1.6); cv.circle(hc, 104, G, 0.25 * ma, 1)
            for i in range(16):
                q = i / 16 * 2 * math.pi + t * 0.15
                cv.path([(hc[0] + 112 * math.cos(q), hc[1] + 112 * math.sin(q)), (hc[0] + 124 * math.cos(q), hc[1] + 124 * math.sin(q))], G, 0.5 * ma, 1.2, smooth=False)
            cv.path([(960 + 330 * math.cos(q), GY + 6 + 34 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 140)], G, 0.8 * ma, 1.8, md, smooth=False)

        # ---- light rings on section downbeats ----
        for t0, c, r0, r1 in ((T(23), (960, 430), 80, 720), (T(31), (960, 480), 150, 900), (T(35), (960, 480), 150, 900),
                              (T(38), (960, 250), 120, 560), (T(47), (960, 480), 150, 800), (T(55), (960, 480), 150, 700),
                              (T(63), (960, 480), 150, 800), (T(72), (1124, 120), 60, 900)):
            self.ring_burst(cv, t, t0, c, r0, r1, 0.9)

        # ---- slot 1: E = streaks fly in / I = calm rings close in ----
        sI = ramp(t, T(32), T(33)) * (1 - ramp(t, T(37), T(38)))
        bright1 = ramp(t, T(32), T(36)) * (1 - ramp(t, T(37), T(39)))
        if sI > 0:
            if self.L[0] == 'E':
                for (q, ph, v) in STREAKS:
                    k = ((t - T(32)) * 0.55 * v + ph) % 1.0; r = lerp(1100, 200, k ** 1.6)
                    x, y = 960 + r * math.cos(q), 470 + r * 0.7 * math.sin(q)
                    x2, y2 = 960 + (r + 70) * math.cos(q), 470 + (r + 70) * 0.7 * math.sin(q)
                    a = sI * math.sin(k * math.pi)
                    cv.path([(x2, y2), (x, y)], G, a * 0.7, 1.4, smooth=False); cv.circle((x, y), 3, Wm, a, fill=True)
            else:
                for j in range(4):
                    k = ((t - T(32)) / (4 * self.e8) + j / 4) % 1.0; r = lerp(1000, 260, eo(k))
                    cv.path([(960 + r * math.cos(q), 480 + r * 0.75 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 160)],
                            SO, sI * math.sin(k * math.pi) * 0.6, 1.6, smooth=False)

        # ---- slot 2 (N/S): beam to the ground, people light one per beat ----
        nb = ramp(t, T(42), T(42.6)) * (1 - ramp(t, T(53.5), T(54.5)))
        if nb > 0 and t < T(55):
            s0, s1 = np.array([1010, 470.]), np.array([1430, 915.]); k = eo(ramp(t, T(42), T(43))); p = s0 + (s1 - s0) * k
            cv.path([tuple(s0), tuple(p)], Wm, nb * 0.9, 2, smooth=False); cv.path([tuple(s0), tuple(p)], G, nb * 0.4, 9, smooth=False, layer=cv.F)
            if k < 1: cv.glow(tuple(p), 24, Wm, 1.0)
            for px, sc, tp_ in ((1430, 1.35, T(43)), (1320, 1.15, T(44)), (1550, 1.2, T(45))):
                if t >= tp_:
                    self.person(cv, px, GY, sc * 3.0 * pop(t, tp_, 0.15), G, nb * (0.85 + 0.6 * pulse(t, tp_, 0.3)), 0.0, t)
                    cv.glow((px, GY - 70 * sc), 60, G, 0.5 * pulse(t, tp_, 0.4))

        # ---- slot 4: J = flags one per beat / P = sky lanterns one per beat ----
        fA = ramp(t, T(55), T(56)) * amb
        if fA > 0:
            if self.L[3] == 'J':
                for x, hgt, tf in ((1260, 230, T(56)), (1400, 250, T(57)), (1530, 220, T(58)), (1650, 260, T(59)), (1760, 235, T(60)), (1860, 250, T(61))):
                    if t < tf - 0.1: continue
                    yo = lerp(-200, GY - hgt, eo(ramp(t, tf - 0.1, tf)))
                    if t < tf + 0.25: cv.circle((x, yo), 10, Wm, 1, fill=True); cv.glow((x, yo), 30, G, 1.0)
                    if t >= tf:
                        self.flag(cv, x, GY, hgt * eo(ramp(t, tf, tf + 0.12)), fA, eo(ramp(t, tf + 0.1, tf + 0.4)), t)
                        cv.circle((x, GY - hgt), 6, Wm, fA, fill=True); cv.glow((x, GY - hgt), 22, G, 0.6 + 1.2 * pulse(t, tf, 0.3))
            else:
                for i, (x, ph) in enumerate(SKY):
                    tf = T(56 + i)
                    if t < tf: continue
                    rise = (t - tf) * 70 + 40 * ph; y = GY - 30 - rise; pp = pop(t, tf, 0.15)
                    cv.circle((x, GY), 8, Wm, fA * pulse(t, tf, 0.3), fill=True)
                    cv.path([(x - 16, y - 20), (x + 16, y - 20), (x + 12, y + 18), (x - 12, y + 18), (x - 16, y - 20)], G, fA, 1.8, smooth=False)
                    flame(cv, x, y + 10, 18 * pp, Wm, fA); cv.glow((x, y), 36, G, fA * (0.5 + pulse(t, tf, 0.3)))

        # ---- figure ----
        kOffer = eio(ramp(t, T(47), T(48))) * (1 - eio(ramp(t, T(53.5), T(54.5))))
        aL = lerp_pose(ARM_L['rest'], ARM_L['offer'], kOffer); aL = lerp_pose(aL, ARM_L['open'], kUp)
        aR = lerp_pose(ARM_R['rest'], ARM_R['up'], kUp)
        pglow = eo(ramp(t, T(65), T(65.5))) * (1 - 0.3 * endF) + 1.2 * pulse(t, T(65), 0.4)
        self.draw_figure(cv, t, (1.0 if t >= T(13) else 0.0) * (1 - 0.8 * endF), ramp(t, T(13), T(21)), aL, aR, spread,
                         bright=bright1 + 0.6 * pglow * (t < T(71)))

        # ---- prop: drop, rest, raise ----
        if t >= T(1.2):
            fall = eo(ramp(t, T(1.2), T(2))); off = lerp(-1100, 0, fall)
            grip = grip_rest.copy(); ang = math.pi / 2
            if kUp > 0:
                hand = np.array(aR[-1]); grip = grip + (hand - grip) * kUp
                if self.prop == 'sword':
                    ang = math.pi / 2 - math.pi * kUp
                    if 0 < kUp < 1:
                        Pa = [(grip[0] + 330 * math.cos(q), grip[1] + 330 * math.sin(q)) for q in np.linspace(math.pi / 2, ang, 30)]
                        cv.path(Pa, Wm, 0.9, 3, smooth=False); cv.path(Pa, G, 0.5, 14, smooth=False, layer=cv.F)
            if fall < 1:
                for k in range(5):
                    cv.path([(960 + (k - 2) * 6, 230 + off - 300), (960 + (k - 2) * 6, 230 + off + 200)], G, 0.25, 2, smooth=False, layer=cv.F)
            g = pglow if t < T(80) else 0.5
            head, tip = self.draw_prop(cv, (grip[0], grip[1] + off), ang, 1.0 * (1 - 0.6 * endF), 0.3 + g + (0.8 if kUp >= 1 else 0), t)
            if t < T(10): cv.glow(tuple(head), 22, Wm, 0.6)
            if t >= T(72):
                sb = (0.6 + 1.6 * pulse(t, T(72), 0.6)) * (1 - 0.7 * endF)
                cv.path([tuple(tip), (tip[0], -200)], Wm, sb, 4, smooth=False); cv.path([tuple(tip), (tip[0], -200)], G, sb * 0.5, 40, smooth=False, layer=cv.F)
                cv.glow(tuple(tip), 70, Wm, sb)
        self.star_flare(cv, (960, 430), 420, pulse(t, T(23), 0.7) * 1.4)
        self.star_flare(cv, (960, 470), 260, pulse(t, T(65), 0.5))

        # ---- slot 3: F = orb in hand / T = rotating wireframe in hand ----
        if kOffer > 0.05:
            hx, hy = aL[-1][0] - 30, aL[-1][1] - 10; ob = 1 + 0.5 * pulse(t, qt, 0.3)
            if self.L[2] == 'F':
                cv.circle((hx, hy), 16 * ob, Wm, kOffer, fill=True, layer=cv.F); cv.circle((hx, hy), 8, Wm, kOffer, fill=True)
                cv.glow((hx, hy), 50 * ob, G, 0.7 * kOffer)
                for j in range(2):
                    q0 = t * (1.8 + j) + j * 2; rw = eo(ramp(t, T(48), T(49)))
                    if rw > 0:
                        cv.path([(hx + (60 + 18 * j) * math.cos(q), hy + (60 + 18 * j) * math.sin(q)) for q in np.linspace(q0, q0 + 2 * math.pi * rw, 80)], G, kOffer * 0.8, 1.6, smooth=False)
            else:
                rot = t * 1.1; R = 46 * ob
                hexa = [(hx + R * math.cos(rot + i * math.pi / 3), hy + R * math.sin(rot + i * math.pi / 3)) for i in range(7)]
                tri = [(hx + R * 0.7 * math.cos(-rot * 1.5 + i * 2 * math.pi / 3), hy + R * 0.7 * math.sin(-rot * 1.5 + i * 2 * math.pi / 3)) for i in range(4)]
                cv.path(hexa, Wm, kOffer, 1.8, smooth=False); cv.path(tri, G, kOffer, 1.6, smooth=False)
                for p_ in hexa[:6]: cv.circle(p_, 3.5, Wm, kOffer, fill=True); cv.path([(hx, hy), p_], G, kOffer * 0.35, 1, smooth=False)
                cv.glow((hx, hy), 50 * ob, G, 0.5 * kOffer)

        # ---- shards (T69) ----
        if T(69) <= t < T(69) + 1.2:
            k = (t - T(69)) / 1.2
            for (q, r, s, ph) in SHARDS:
                rr = r * eo(k) + 100; x, y = 960 + rr * math.cos(q), 480 + rr * 0.8 * math.sin(q)
                Pp = [(x + s * math.cos(ph + t * 3 + i * 2.1), y + s * math.sin(ph + t * 3 + i * 2.1)) for i in range(3)]
                cv.path(Pp + [Pp[0]], G, 1 - k, 1.6, smooth=False)
        # ---- crowd rises (T72, then one eighth per band outward) ----
        if t >= T(71.5):
            for (x, y, s, row) in CROWD:
                d = abs(x - 960) / 960
                tr = T(72) + (0 if d < 0.25 else (self.e8 if d < 0.6 else 2 * self.e8)) + row * 0.03
                if t < tr: continue
                up = eo(ramp(t, tr, tr + 0.18)); a = (0.9 + 0.8 * pulse(t, tr, 0.3)) * (1 - 0.6 * endF)
                self.person(cv, x, y + (1 - up) * 90, s, SO * 0.6 + LN * 0.4, a * up, a * up, t)
        # ---- end ring ----
        if t >= T(81) - 0.1:
            ec = cv.cam; cv.cam = Cam(1.0)
            self.ring_burst(cv, t, T(81), (960, 560), 60, 260, 1.0)
            k = eo(ramp(t, T(81), T(82)))
            cv.path([(960 + 175 * math.cos(q), 560 + 175 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120)], G, 0.45 * k, 1.4, smooth=False)
            for i in range(36):
                q = i / 36 * 2 * math.pi
                cv.path([(960 + 182 * math.cos(q), 560 + 182 * math.sin(q)), (960 + 194 * math.cos(q), 560 + 194 * math.sin(q))], G, 0.5 * k, 1.2, smooth=False)
            if self.logo is None: self.eye_logo(cv, (960, 560), 2.2, 1.0, k)
            cv.cam = ec
        if self.logo is None:
            wm = ramp(t, T(31), T(32)) * (1 - ramp(t, T(79), T(80)))
            ec = cv.cam; cv.cam = Cam(1.0)
            if wm > 0: self.eye_logo(cv, (70, 52), 0.42, 0.8 * wm)
            if T(23) <= t < T(31.5) and not self.custom_badge:
                self.eye_logo(cv, (1500, 545), 0.6, eo(ramp(t, T(23), T(24))) * (1 - ramp(t, T(31), T(31.5))), eo(ramp(t, T(23), T(24.5))))
            cv.cam = ec

        self.texts(tx, t)
        flash = 0.10 * pulse(t, T(2), 0.3) + 0.12 * pulse(t, T(7), 0.4) + 0.16 * pulse(t, T(23), 0.5) + \
                0.10 * pulse(t, T(38), 0.3) + 0.10 * pulse(t, T(69), 0.4) + 0.20 * pulse(t, T(72), 0.6)
        img = cv.composite(P.BG, flash) * P.VIG
        if self.logo is not None:
            if t >= T(81): img = self._put_logo(img, 960, 560, 170, 1.0, eo(ramp(t, T(81), T(82))))
            wm = ramp(t, T(31), T(32)) * (1 - ramp(t, T(79), T(80)))
            if wm > 0: img = self._put_logo(img, 70, 52, 34, 0.8 * wm)
            if T(23) <= t < T(31.5) and not self.custom_badge:
                img = self._put_logo(img, 1500, 545, 52, eo(ramp(t, T(23), T(24))) * (1 - ramp(t, T(31), T(31.5))), eo(ramp(t, T(23), T(24))))
        img = self.title_badge(img, t)
        img = tx.blend(img)
        img *= 1 - ramp(t, self.duration - 0.35, self.duration - 0.05)
        return np.clip(img * 255, 0, 255).astype(np.uint8)

    def _put_logo(self, img, cx, cy, h, a, reveal=1.0):
        Lg = self.logo
        w = int(Lg.shape[1] * h / Lg.shape[0]); lg = cv2.resize(Lg, (w, h), interpolation=cv2.INTER_AREA)
        xx = np.linspace(0, 1, w)[None, :]; m = np.clip((lerp(-0.2, 1.2, reveal) - xx) * 6, 0, 1)
        lg = lg * m[..., None] * a; y0, x0 = int(cy - h / 2), int(cx - w / 2)
        img[y0:y0 + h, x0:x0 + w] += lg + cv2.GaussianBlur(lg, (0, 0), 8) * 0.6
        return img
