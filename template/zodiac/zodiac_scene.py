"""Zodiac video scene: the MBTI single-type timeline, re-skinned per sign.

Same beats as the MBTI template (T(n) = offset + n * eighth). Per sign: element palette, hero look + emblem,
sign prop (sword / orb / lantern / star / scales / bow / urn / wheat / none), twins for Gemini,
constellation drawn into the sky at the title, glyph badge beside the title, four trait tags.
`variants` (4 letters, MBTI-style) picks the section visuals: [0] E streaks / I calm rings,
[2] F orb / T diagram in the hand, [3] J flags / P sky lanterns.
"""
import math, os, json
import numpy as np, cv2
from zodiac_signs import (SIGNS, draw_emblem, draw_constellation, glyph_mask, ELEMENT_CN, _ENFJ, GY, Cam,
                          F, SERIF_B, SERIF_BL, SANS_M, flame, spline, lerp, cl, ramp, eo, pulse)
from engine.scene import MBTIScene
from engine.group import SubCam

HERE = os.path.dirname(os.path.abspath(__file__))
STD_PROPS = ('sword', 'orb', 'lantern', 'star')


class ZodiacScene(MBTIScene):
    custom_badge = True

    def __init__(self, sign, copy, offset=0.367, eighth=1 / 3., logo=None, brand=None):
        self.sign, self.copy = sign, copy
        cfg = {'code': copy['variants'], 'name_cn': sign['cn'], 'name_en': sign['en'], 'palette': sign['element'],
               'prop': sign['prop'] if sign['prop'] in STD_PROPS else 'orb', 'look': sign['look'],
               'captions': copy['captions'], 'ending_pre': copy.get('ending_pre', '他就是'), 'brand': brand or {}}
        super().__init__(cfg, offset, eighth, logo)
        self.prop = sign['prop']
        self.traits = copy['traits']
        gm = glyph_mask(sign['glyph'], 110)
        self.glyph = gm[..., None] * np.array(self.P.GOLD, np.float32) * 1.1
        if sign['emblem'] == 'twins':
            c2 = dict(cfg); c2['look'] = sign['look2']; self.twin = MBTIScene(c2, offset, eighth)
            self.twin.prop = 'none'

    # ---------------------------------------------------------------- captions: trait tags instead of letters
    def _build_text(self):
        super()._build_text()
        tr = self.copy['traits']
        self.caps = [c if c[8] is None else c[:8] + ((str(k + 1), tr[k]),) for c, k in
                     zip(self.caps, [0, 0, 0, 0, 0, 1, 2, 3, 0, 0])]

    def texts(self, tx, t):
        T, P, s = self.T, self.P, self.sign
        for l1, l2, t1, t2, te, x, y, g2, tag in self.caps:
            if tag: tx.tag(tag[0], tag[1], x, y - 58, t, t1 - 0.03, te)
            fs = 40 if max(len(l1), len(l2)) <= 11 else 36
            tx.chars(l1, x, y, F(SERIF_B, fs), P.WHITE, t, t1, te)
            tx.chars(l2, x, y + 56, F(SERIF_B, fs), P.WHITE, t, t2, te, gold=g2)
        if T(23) <= t < T(31.5):
            te = T(31); x0 = 1500
            tx.chars(' '.join(s['en'].upper()), x0, 645, F(SERIF_B, 52 if len(s['en']) <= 7 else 42), (225, 240, 228), t, T(23), te, stagger=0.03, spacing=4)
            tx.chars(s['cn'], x0, 810, F(SERIF_BL, 150), P.WHITE, t, T(23.5), te, stagger=0.06)
            line = '  ·  '.join(self.traits)
            tx.chars(line, x0, 880, F(SANS_M, 30), (225, 240, 228), t, T(25), te, gold=tuple(range(0, len(line))), stagger=0.012)
            tx.chars(f"{s['dates']}   {ELEMENT_CN[s['element']]}", x0, 930, F(SANS_M, 24), P.TAG, t, T(26), te, stagger=0.01)
        tx.chars(self.cfg.get('ending_pre', '他就是'), 1470, 400, F(SERIF_B, 44), P.WHITE, t, T(77), T(79.6), stagger=0.04)
        tx.chars(s['cn'], 1470, 520, F(SERIF_BL, 110), P.HI, t, T(78), T(79.6), stagger=0.06)
        tx.chars(' '.join(s['en'].upper()), 1470, 590, F(SERIF_B, 36), (225, 235, 230), t, T(78.5), T(79.6), stagger=0.02)
        b = self.cfg.get('brand', {})
        if b.get('cn') or b.get('en'):
            line = '   '.join(x for x in (' '.join(b.get('cn', '')), ' '.join(b.get('en', ''))) if x)
            tx.chars(line, 960, 690, F(SANS_M, 34), (230, 240, 230), t, T(82), 99, stagger=0.02)
        tx.chars(f"星座系列  ·  {s['cn']}", 960, 740, F(SANS_M, 20), P.TAG, t, T(83), 99, stagger=0.015)

    # ---------------------------------------------------------------- sky: constellation draws in at the title
    def extra_sky(self, cv, t):
        T = self.T
        a = ramp(t, T(23), T(24)) * (1 - 0.6 * ramp(t, T(79), T(81)))
        if a > 0:
            draw_constellation(cv, self.sign, (130, 70, 470, 280), self.P, t, a, eo(ramp(t, T(23), T(26))))
            if T(23) <= t < T(24.5): cv.glow((360, 200), 260, self.P.GOLD, 0.25 * pulse(t, T(23), 0.5))

    def title_badge(self, img, t):
        T = self.T
        a = eo(ramp(t, T(23), T(24))) * (1 - ramp(t, T(31), T(31.5)))
        if a <= 0: return img
        g = self.glyph * a; h, w = g.shape[:2]; y0, x0 = 510 - h // 2, 1500 - w // 2
        img[y0:y0 + h, x0:x0 + w] += g + cv2.GaussianBlur(g, (0, 0), 8) * 0.8
        return img

    # ---------------------------------------------------------------- hero: twins / emblem
    def draw_figure(self, cv, t, a, prog, armL, armR, spread=0.0, bright=0.0):
        if self.sign['emblem'] == 'twins':
            main = cv.cam
            for x, sc in ((800, self), (1120, self.twin)):
                cv.cam = SubCam(main, x, 0.92)
                MBTIScene.draw_figure(sc, cv, t, a, prog, armL, armR, spread, bright)
            cv.cam = main
            return
        if self.sign['emblem'] == 'tail' and a > 0: draw_emblem(self, cv, self.sign, t, a * eo(ramp(prog, 0.5, 0.9)))
        super().draw_figure(cv, t, a, prog, armL, armR, spread, bright)
        if self.sign['emblem'] not in ('tail', 'none', 'twins') and a > 0:
            draw_emblem(self, cv, self.sign, t, a * eo(ramp(prog, 0.35, 0.6)))

    # ---------------------------------------------------------------- sign props, held at the grip (follow the raise)
    def draw_prop(self, cv, anchor, ang, a, glow, t):
        if self.prop in STD_PROPS: return super().draw_prop(cv, anchor, ang, a, glow, t)
        P = self.P; S, G, Wm = P.SOFT, P.GOLD, P.WARM; hx, hy = anchor
        if self.prop == 'scales':
            top = (hx, hy - 150); cv.path([(hx, hy + 40), top], Wm, a, 2.4, smooth=False)
            tilt = 0.12 * math.sin(t * 1.5); L_, R_ = (hx - 120, top[1] + 120 * tilt), (hx + 120, top[1] - 120 * tilt)
            cv.path([L_, R_], Wm, a, 2.6, smooth=False); cv.circle(top, 8, G, a, fill=True)
            for e in (L_, R_):
                py = e[1] + 95
                cv.path([e, (e[0] - 42, py)], S, a * 0.8, 1.4, smooth=False); cv.path([e, (e[0] + 42, py)], S, a * 0.8, 1.4, smooth=False)
                cv.path([(e[0] - 48, py), (e[0] - 32, py + 18), (e[0] + 32, py + 18), (e[0] + 48, py)], G, a, 2.2, smooth=False)
            cv.glow(top, 40, G, (0.4 + glow) * a); return top, top
        if self.prop == 'bow':
            top, bot = (hx + 30, hy - 230), (hx + 30, hy + 230)
            arc_ = [(hx + 30 + 90 * math.sin(s * math.pi), lerp(top[1], bot[1], s)) for s in np.linspace(0, 1, 40)]
            cv.path(arc_, G, a, 3, smooth=False); cv.path([top, bot], S, a * 0.8, 1.4, smooth=False)
            tipA = (hx + 30, hy - 260)
            cv.path([(hx + 30, hy + 80), tipA], Wm, a, 2.2, smooth=False)
            cv.path([tipA, (tipA[0] - 12, tipA[1] + 22), (tipA[0] + 12, tipA[1] + 22), tipA], Wm, a, 2, smooth=False)
            cv.glow(tipA, 30, G, (0.5 + glow) * a); return tipA, tipA
        if self.prop == 'urn':
            c = (hx, hy - 60); z = 1.5
            body = [(c[0] - 34 * z, c[1] - 30 * z), (c[0] - 48 * z, c[1] + 10 * z), (c[0] - 30 * z, c[1] + 50 * z), (c[0] + 30 * z, c[1] + 50 * z), (c[0] + 48 * z, c[1] + 10 * z), (c[0] + 34 * z, c[1] - 30 * z)]
            cv.path(body, G, a, 2.6); cv.path([(c[0] - 40 * z, c[1] - 34 * z), (c[0] + 40 * z, c[1] - 34 * z)], G, a, 2.4, smooth=False)
            cv.poly(spline(body, n=6), G * 0.12, a, layer=cv.F)
            for k in range(3):
                pts = [(c[0] - 60 * z - k * 12 - 30 * s + 10 * math.sin(s * 8 + t * 6 + k), lerp(c[1] - 40 * z, GY, s)) for s in np.linspace(0, 1, 30)]
                cv.path(pts, S, a * (0.9 - k * 0.2), 1.8, smooth=False)
            m = (c[0], c[1] - 34 * z); cv.glow(m, 50, G, (0.4 + glow) * a); return m, m
        if self.prop == 'wheat':
            for k, an in enumerate((-0.25, 0.0, 0.25)):
                base = np.array([hx, hy + 100.]); d = np.array([math.sin(an), -math.cos(an)]); top = base + d * 360
                cv.path([tuple(base), tuple(top)], G, a, 2, smooth=False)
                for j in range(7):
                    p_ = base + d * (230 + j * 18)
                    for sx in (-1, 1):
                        n = np.array([-d[1], d[0]]) * sx
                        cv.path([tuple(p_), tuple(p_ + d * 10 + n * 10), tuple(p_ + d * 20)], Wm, a, 1.6, smooth=False)
            top = (hx, hy - 260); cv.glow(top, 60, G, (0.3 + glow) * a); return top, top
        # none: a small shared star between the hands
        c = (hx, hy - 60); cv.circle(c, 6, Wm, a, fill=True); cv.glow(c, 40, G, (0.6 + glow) * a)
        cv.path([(hx - 55, hy - 48), c, (hx + 55, hy - 48)], G, a * 0.8, 1.6, smooth=False); return c, c


def load(key, offset=0.367, eighth=1 / 3., logo=None, brand=None):
    sign = next(s for s in SIGNS if s['key'] == key)
    with open(os.path.join(HERE, 'signs', key + '.json'), encoding='utf-8') as f: copy = json.load(f)
    return ZodiacScene(sign, copy, offset, eighth, logo, brand)
