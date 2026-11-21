"""Long-form v2: story-first cut modelled on the 双子座 reference.

* Hook = one continuous shot that grows from a single spark: every caption is typed one character per eighth note
  and the picture acts it out (the spark becomes a flame, the flame flares on "就燃", the camera pushes into the
  core where a heart is drawn, the flame wraps the heart and grows into the hero), the music dips, and the title
  lands on the drop (~10.6 s; the music is started so its drop falls there).
* No chapter title cards: a chapter opens with a one-character seal stamped on the downbeat (燃 / 直 / 软 …), which
  then rides as a small badge above every caption of that chapter.
* Captions are typed (2 characters per eighth) instead of faded in; the hero's heart glows at the chest all video.
"""
import math
import numpy as np, cv2
from longform import (LongScene, parse_card, SHOTS, MOTIF_CAM, EXTRA, SIGS, VIS_FACE, HERO_K, BAND, _warn,
                      draw_vis, draw_face_fx, draw_constellation, STARS, HILLS, FLAMES, CROWD, ARM_L, ARM_R, SubCam)
from engine.core import (W, H, GY, cl, ramp, eo, eio, lerp, pulse, pop, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M, spline)
from vis import heart_pts

DROP = 40          # eighth of the music drop / title
CORE = (960.0, 569.0)   # world point of the hero's chest (= the flame core in the hook)


def flame_pts(x, y, h, lean, t):
    w = h * 0.36; wob = 0.04 * math.sin(t * 7)
    pts = [(x + (lean + wob) * h, y - h), (x + w * 0.55, y - h * 0.45), (x + w * 0.5, y - h * 0.15), (x, y),
           (x - w * 0.5, y - h * 0.15), (x - w * 0.55, y - h * 0.45)]
    return list(spline(pts, n=10, closed=True))


class LongSceneV2(LongScene):
    HOOK = 56
    CH_E8 = 4

    # ------------------------------------------------------------ camera
    def camera(self, t):
        n = (t - self.off) / self.e8
        if n >= self.HOOK: return super().camera(t)
        keys = [(0, 1.7, 960, 569), (5, 1.7, 960, 569), (12, 1.25, 960, 520), (15.6, 1.25, 960, 520), (16.4, 0.95, 960, 500),
                (19, 1.05, 960, 520), (25, 2.1, 960, 500), (31, 2.3, 960, 500), (33, 2.3, 960, 500), (39.5, 1.2, 960, 540),
                (40.5, 0.92, 1300, 520), (52, 0.98, 1320, 520), (56, 1.08, 960, 520)]
        s, cx, cy = keys[0][1:]
        for (k0, s0, x0, y0), (k1, s1, x1, y1) in zip(keys[:-1], keys[1:]):
            if k0 <= n < k1:
                u = eio(cl((n - k0) / (k1 - k0))); s, cx, cy = lerp(s0, s1, u), lerp(x0, x1, u), lerp(y0, y1, u); break
        else:
            if n >= keys[-1][0]: s, cx, cy = keys[-1][1:]
        T = self.T
        s *= 1 + 0.10 * pulse(t, T(16), 0.35) + 0.08 * pulse(t, T(DROP), 0.4)
        if n >= DROP: s *= 1 + 0.012 * pulse(t, self.quarter(t), 0.35)
        return Cam(s, cx, cy)

    # ------------------------------------------------------------ captions
    def seal(self, tx, ch, x, y, size, t, t0, t1):
        """gold seal with one character (chapter marker without words)"""
        if t < t0 or t > t1 + 0.25: return
        k = eo(ramp(t, t0, t0 + 0.18)) * (1 - ramp(t, t1, t1 + 0.25)); al = int(255 * k)
        sc = 1 + 0.35 * (1 - eo(ramp(t, t0, t0 + 0.22)))
        sz = size * sc; hr, hg, hb = self.P.HI
        tx.d.rounded_rectangle([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], int(sz * 0.14), fill=(hr, int(hg * 0.82), int(hb * 0.5), al))
        tx.d.rounded_rectangle([x - sz / 2 + 4, y - sz / 2 + 4, x + sz / 2 - 4, y + sz / 2 - 4], int(sz * 0.12), outline=(40, 25, 10, int(al * 0.6)), width=2)
        tx.d.text((x, y + sz * 0.02), ch, font=F(SERIF_BL, int(sz * 0.66)), fill=(35, 22, 12, al), anchor='mm')

    def card_text(self, tx, t, c, t0, t1):
        P = self.P; st = self.e8 * 0.5          # typed: two characters per eighth note
        seg = self.seg_at(t)
        if c['key']:
            n = len(c['lines']); ml = max(len(l) for l in c['lines'])
            fs = 96 if ml <= 9 else (84 if ml <= 11 else 72); gap = int(fs * 1.35)
            y0 = 520 - (n - 1) * gap / 2 + fs * 0.35
            tt = t0
            for k, (l, g) in enumerate(zip(c['lines'], c['golds'])):
                tx.chars(l, 960, int(y0 + k * gap), F(SERIF_BL, fs), P.WHITE, t, tt, t1, gold=g, stagger=st)
                tt += len(l) * st + self.e8
        else:
            n = len(c['lines']); ml = max(len(l) for l in c['lines'])
            fs = 72 if ml <= 11 else (64 if ml <= 13 else 56); gap = int(fs * 1.38)
            y0 = 1000 - (n - 1) * gap
            if seg: self.seal(tx, seg['name'][0], 960, int(y0 - fs - 40), 64, t, t0, t1)
            tt = t0
            for k, (l, g) in enumerate(zip(c['lines'], c['golds'])):
                tx.chars(l, 960, int(y0 + k * gap), F(SERIF_B, fs), P.WHITE, t, tt, t1, gold=g, stagger=st)
                tt += len(l) * st + 0.5 * self.e8

    # ------------------------------------------------------------ hook pieces
    def _hook_world(self, cv, t, n):
        """the spark → flame → heart → hero sequence (world space, before the drop)"""
        T, P = self.T, self.P; G, Wm, SO = P.GOLD, P.WARM, P.SOFT
        C = CORE
        if n >= DROP + 1: return
        dim = 1 - 0.55 * ramp(n, 37.5, 39.5) * (n < DROP)
        # flame height
        chars = cl(math.floor(n) - 4, 0, 7) if n >= 5 else 0
        h = 0.0
        if n >= 5: h = 40 + 22 * chars * (0.85 + 0.15 * pop(t, T(math.floor(n)), 0.12))
        if n >= 14: h = 200 * (1 + 0.05 * math.sin(t * 20))
        if n >= 16: h = lerp(430, 300, eo(ramp(n, 16, 19)))
        if n >= 19: h = 300 * (1 + 0.04 * math.sin(t * 9))
        if n >= 33: h = lerp(300, 200, eio(ramp(n, 33, 39)))
        fa = (1 - ramp(n, 38.5, 40.5)) * dim
        if h > 0 and fa > 0:
            base = C[1] + 0.42 * h
            lean = 0.06 * math.sin(t * 2.3)
            close = ramp(n, 19, 25) * (1 - ramp(n, 37, 39.5))       # line-art when the camera is inside the flame
            flame(cv, C[0], base, h * 1.5, G, 0.22 * fa, layer=cv.F, lean=lean)
            flame(cv, C[0], base, h, G, (0.75 - 0.6 * close) * fa, lean=lean)
            flame(cv, C[0], base - 0.05 * h, h * 0.62, Wm, (0.9 - 0.75 * close) * fa, lean=lean * 1.3)
            for k, (sc_, col, th) in enumerate(((1.0, G, 2.6), (0.78, Wm, 2.0), (1.22, G, 1.4))):
                fp = flame_pts(C[0], base, h * sc_, lean, t + k)
                cv.path(fp, col, fa * (0.35 + 0.65 * close) * (1 - 0.3 * k), th, smooth=False)
            cv.glow(C, 0.55 * h, G, (0.45 - 0.25 * close) * fa)
            for j in range(14):   # embers drifting up
                v = (t * 0.55 + j * 0.137) % 1
                x = C[0] + (j * 37 % 120 - 60) * (0.4 + v) + 12 * math.sin(t * 3 + j)
                cv.circle((x, base - h * 0.6 - v * 320), 2.4, Wm, fa * (1 - v) * 0.9, fill=True)
        # the first spark + heartbeat rings
        if n < 6:
            r = 7 * (1 + 0.5 * pulse(t, T(0), 0.3) + 0.5 * pulse(t, T(2), 0.3))
            cv.circle(C, r, Wm, 1.0, fill=True); cv.glow(C, 40, G, 0.9)
        for p0 in (0, 2):
            if T(p0) <= t < T(p0) + 0.9:
                k = (t - T(p0)) / 0.9; cv.circle(C, 20 + 220 * eo(k), G, (1 - k) * 0.8, 2)
        # "一碰": an ember flies in and strikes on "就燃"
        if T(14) <= t < T(16):
            u = eio((t - T(14)) / (T(16) - T(14)))
            p = (lerp(260, C[0], u), lerp(180, C[1] - 40, u) - 140 * math.sin(u * math.pi))
            cv.circle(p, 6, Wm, 1, fill=True); cv.glow(p, 30, G, 0.9)
            for k in range(1, 8):
                uu = max(0, u - k * 0.03); q = (lerp(260, C[0], uu), lerp(180, C[1] - 40, uu) - 140 * math.sin(uu * math.pi))
                cv.circle(q, 4 - k * 0.4, G, 0.6 * (1 - k / 8), fill=True)
        if T(16) <= t < T(16) + 1.4:   # the flare: embers burst outward + rings
            k = (t - T(16)) / 1.4
            for j in range(28):
                q = j * 2 * math.pi / 28 + 0.3; r = 60 + 520 * eo(k) * (0.7 + 0.3 * math.sin(j * 7))
                cv.circle((C[0] + r * math.cos(q), C[1] - 60 + r * math.sin(q)), 3.2, Wm, (1 - k), fill=True)
            self.hero.ring_burst(cv, t, T(16), C, 60, 700, 0.9)
        # the heart inside the core
        if n >= 26:
            g = eio(ramp(n, 26, 29)); s = 1.1 * (1 + 0.12 * pulse(t, self.quarter(t), 0.25) * (n >= 29))
            hp = [(C[0] + 60 * x, C[1] + 60 * y) for x, y in heart_pts(0, 0, s)]
            self.hero.tpath(cv, hp, Wm, 1.0, 2.6, g, smooth=False)
            cv.poly(hp, Wm * 0.25, 0.8 * g, layer=cv.F); cv.glow(C, 50, Wm, 0.9 * g * (1 + 0.6 * pulse(t, self.quarter(t), 0.3)))
        # the flame wraps the heart, horns curl out of its tip
        if 33 <= n < DROP + 1:
            g = eio(ramp(n, 33, 36)); a = 1 - ramp(n, 39.5, 40.5)
            for sd in (-1, 1):
                arm = [(C[0] + sd * (95 - 10 * u) * math.sin(u * math.pi * 0.95), C[1] + 90 - 230 * u) for u in np.linspace(0, 1, 30)]
                cv.path(arm, G, a, 2.6, g, smooth=False); cv.path(arm, G, 0.3 * a, 10, g, smooth=False, layer=cv.F)
            hg = eio(ramp(n, 34, 37)); top = (C[0], C[1] - 140)
            for sd in (-1, 1):
                horn = [(top[0] + sd * 70 * (1 - math.cos(u * 1.6 * math.pi)) * 0.55 + sd * 20 * u, top[1] - 70 * math.sin(u * 1.3 * math.pi)) for u in np.linspace(0, 1, 30)]
                cv.path(horn, G, a, 3, hg, smooth=False)

    def _hook_text(self, tx, t, n):
        T, P = self.T, self.P
        for (txt, m0, step, y, size, m1, gold) in self.s.get('hook2', []):
            if n > m1 + 1: continue
            col = P.HI if gold == 'all' else P.WHITE
            g = tuple(range(len(txt))) if gold == 'all' else tuple(gold)
            tx.chars(txt, 960, y, F(SERIF_BL if size >= 90 else SERIF_B, size), col, t, T(m0), T(m1), gold=g, stagger=self.e8 * step)
        if n >= DROP:   # title on the drop, at the right of the hero
            tt = self.s['title']; X = 1400
            fs = 118 if len(tt) <= 8 else 100
            tx.chars(tt, X, 470, F(SERIF_BL, fs), P.HI, t, T(DROP + 1), T(self.HOOK - 1.4), stagger=self.e8 * 0.5)
            tg = parse_card(self.s['hook']['tagline'])
            for k, (l, gg) in enumerate(zip(tg['lines'], tg['golds'])):
                tx.chars(l, X, 600 + k * 92, F(SERIF_B, 66), P.WHITE, t, T(DROP + 8 + 4 * k), T(self.HOOK - 1.4), gold=gg, stagger=self.e8 * 0.5)

    # ================================================================ FRAME
    def frame(self, t):
        T, P, hero = self.T, self.P, self.hero
        G, Wm, LN, SO = P.GOLD, P.WARM, P.LINE, P.SOFT
        n = (t - self.off) / self.e8
        cam = self.camera(t); cv = Canvas(cam); tx = Text(P)
        seg = self.seg_at(t)
        end_n = self.outro_n; endF = eio(ramp(n, end_n + 6, end_n + 14)); amb = 1 - 0.7 * endF
        card = self._card_at(seg, t) if seg else None
        key_dim = 0.0
        if card and card[2]['key']: key_dim = eo(cl((n - card[0]) / 2)) * (1 - eo(cl((n - card[0] - card[1] + 2) / 2)))
        if seg is not None and card is None:   # seal stamp at a chapter start
            key_dim = 0.8 * eo(cl((n - seg['start']) / 0.8)) * (1 - eo(cl((n - seg['start'] - 3) / 1.0)))
        hook = n < self.HOOK
        pre = n < DROP
        dip = 1 - 0.6 * ramp(n, 37.5, 39.5) * pre
        world = amb * (1 - 0.55 * key_dim) * dip
        qt = self.quarter(t)
        # ---- sky ----
        sky = ramp(n, 0, 10) * (0.5 if pre else 1.0)
        for (x, y, r, ph, sp, gold) in STARS:
            tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph))
            cv.circle((x, y + 4 * math.sin(t * 0.4 + ph)), r, G if gold else LN, tw * 0.45 * sky * dip, fill=True, layer=cv.F)
        if self.sign and n >= DROP:
            draw_constellation(cv, self.sign, (120, 70, 470, 260), P, t, 0.85 * amb * ramp(n, DROP, DROP + 2), eo(ramp(n, DROP, DROP + 6)))
        hk = ramp(n, DROP, DROP + 4)
        for k, hp in enumerate(HILLS): cv.path(hp, P.DIM, 0.5 * hk * world * (1 - 0.3 * k), 1.4, hk, smooth=False)
        # ---- ground + candles: they wake on the drop ----
        gl = eo(ramp(n, DROP, DROP + 1))
        if gl > 0:
            cv.path([(-100, GY), (2020, GY)], LN, 0.7 * world * gl, 1.6, smooth=False)
            cv.path([(-100, GY), (2020, GY)], LN, 0.22 * world * gl, 6, smooth=False, layer=cv.F)
        if n >= DROP:
            k = pulse(t, T(DROP), 0.5)
            Pr = [(960 + 260 * math.cos(q), GY + 22 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 100)]
            cv.path(Pr, Wm, (0.4 + 1.2 * k) * world, 3, smooth=False); cv.glow((960, GY), 140, G, 0.6 * k)
        for j, (x, y, h, ph, r) in enumerate(FLAMES):
            d = abs(x - 960); ton = T(DROP + (0 if d < 260 else (1 if d < 620 else 2)))
            if t < ton: continue
            boost = 1 + 2.0 * pulse(t, ton, 0.25) + 0.25 * pulse(t, qt, 0.3)
            a = min(1.6, boost) * world; hh = h * (1 + 0.12 * math.sin(t * 7 + ph)) * pop(t, ton, 0.16)
            flame(cv, x, y, hh, G, 0.95 * a, lean=0.08 * math.sin(t * 2 + ph)); flame(cv, x, y, hh * 1.6, G, 0.25 * a, layer=cv.F)
        if hook: self._hook_world(cv, t, n)
        # ---- hero ----
        prog = ramp(n, 33, 39.5)
        shp, cut = self.shot_at(t, seg, card) if not hook else (list(SHOTS['hero']), 0.0)
        hx, hkk, ha = (shp[3], shp[4], shp[5]) if not hook else (960, HERO_K, 1.0)
        self.XS = (hx,)
        sub = SubCam(cam, hx, hkk); cv.cam = sub
        aL, aR = ARM_L['rest'], ARM_R['rest']
        bright = 0.25 + 0.5 * pulse(t, qt, 0.3) * (not pre)
        if n >= 33 and ha > 0.01: hero.draw_figure(cv, t, world * ha * (0.6 + 0.4 * (not pre)), prog, aL, aR, 0.0, bright)
        if n >= DROP and ha > 0.01:
            grip = (960, 578) if hero.prop == 'sword' else (960, 540)
            hero.draw_prop(cv, grip, math.pi / 2, world * ha * eo(ramp(n, DROP, DROP + 1)), 0.4 + 0.4 * key_dim + pulse(t, T(DROP), 0.6), t)
        if card is not None and card[2]['vis'] in VIS_FACE:
            try: draw_face_fx(self, cv, card[2]['vis'], t, T(card[0]), T(card[0] + card[1]), amb * ha)
            except Exception as e: _warn(f'face {card[2]["vis"]} @ {t:.2f}s: {e!r}')
        cv.cam = cam
        chest = tuple(sub.to_world([(960, 450)])[0])
        if n >= DROP and ha > 0.01:   # the heart keeps glowing at the chest all video
            hb = 1 + 0.15 * pulse(t, qt, 0.25)
            hp = [(chest[0] + 22 * hkk / HERO_K * x * hb, chest[1] + 22 * hkk / HERO_K * y * hb) for x, y in heart_pts(0, 0, 1.0, 30)]
            cv.poly(hp, Wm, 0.9 * world * ha); cv.glow(chest, 30, G, (0.6 + 0.6 * pulse(t, qt, 0.3)) * world * ha)
        face = [tuple(sub.to_world([(960, 250)])[0])]
        heads = [(tuple(sub.to_world([(960, 470)])[0]),) * 2]
        md = eio(ramp(n, DROP + 1, DROP + 4))
        if md > 0:
            ma = md * world * ha
            def egg(sc_):
                return [(hx + 300 * hkk * sc_ * (1 - 0.13 * math.cos(q)) * math.sin(q), GY - (GY - 495) * hkk - 420 * hkk * sc_ * math.cos(q)) for q in np.linspace(-math.pi, math.pi, 160)]
            cv.path(egg(1.0), LN, 0.7 * ma, 2.0, md, smooth=False)
            for k, p in enumerate(egg(1.0)[::6]):
                if p[1] < GY - 10: flame(cv, p[0], p[1] + 5, 12 * (1 + 0.1 * math.sin(t * 6 + k)), G, 0.8 * ma)
        if T(DROP) <= t < T(DROP) + 2.0:
            for j, r1 in enumerate((900, 1300, 1700)):
                hero.ring_burst(cv, t, T(DROP + 2 * j), CORE, 80, r1, 1.0)
        # ---- chapter motif + story inserts ----
        if seg is not None:
            self._bind(seg)
            f = EXTRA.get(seg['motif']) or SIGS.get(seg['motif'])
            A = ramp(t, T(seg['start']), T(seg['start'] + 2)) * (1 - ramp(t, T(seg['end'] - 2), T(seg['end']))) * world * (shp[9] if card else 1.0)
            if f and A > 0:
                saveT, save8 = self.T, self.e8
                b = 1000
                def Tm(x, _st=self._starts):
                    j = x - b; idx = np.arange(len(_st))
                    if j <= len(_st) - 1: return float(np.interp(j, idx, _st))
                    return float(_st[-1] + (j - len(_st) + 1) * self._avg)
                self.T = Tm; self.e8 = self._avg
                try: f(self, cv, tx, t, 0, b, A, heads, face)
                except Exception as e: _warn(f'motif {seg["motif"]} @ {t:.2f}s: {e!r}')
                finally: self.T, self.e8 = saveT, save8
            hero.ring_burst(cv, t, T(seg['start']), (960, 470), 80, 1000, 0.9)
            if card and card[2]['vis'] and card[2]['vis'] not in VIS_FACE and shp[8] > 0:
                ec = cv.cam; cv.cam = Cam(1.0)
                va = amb * (0.5 if card[2]['key'] and not card[2]['q'] else 1.0) * (0.55 if card[2]['q'] else 1.0)
                try: draw_vis(self, cv, card[2]['vis'], t, T(card[0]), T(card[0] + card[1]), shp[6], shp[7], shp[8], va)
                except Exception as e: _warn(f'vis {card[2]["vis"]} @ {t:.2f}s: {e!r}')
                cv.cam = ec
            if card and card[2]['key'] and card[2]['_shot'] not in ('face',):
                hero.star_flare(cv, chest, 380, pulse(t, T(card[0]), 0.6) * 1.2)
            elif card:
                cv.glow(chest, 200, G, 0.15 * pulse(t, T(card[0]), 0.3))
        # ---- outro ----
        if n >= end_n:
            for (x, y, s, row) in CROWD:
                d = abs(x - 960) / 960; tr = T(end_n + (0 if d < 0.25 else (1 if d < 0.6 else 2)))
                if t < tr: continue
                up = eo(ramp(t, tr, tr + 0.18)); a = (0.9 + 0.8 * pulse(t, tr, 0.3)) * (1 - 0.6 * endF)
                hero.person(cv, x, y + (1 - up) * 90, s, SO * 0.6 + LN * 0.4, a * up, a * up, t)
            ec = cv.cam; cv.cam = Cam(1.0)
            if n >= end_n + 10:
                hero.ring_burst(cv, t, T(end_n + 10), (960, 470), 60, 260, 1.0)
                k = eo(ramp(n, end_n + 10, end_n + 13))
                cv.path([(960 + 175 * math.cos(q), 470 + 175 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 120)], G, 0.45 * k, 1.4, smooth=False)
                if self.logo is None: hero.eye_logo(cv, (960, 470), 2.2, 1.0, k)
            cv.cam = ec

        # ================= text =================
        if hook: self._hook_text(tx, t, n)
        if seg is not None:
            if card is None:   # chapter seal stamped on the downbeat
                self.seal(tx, seg['name'][0], 960, 500, 170, t, T(seg['start']), T(seg['start'] + self.CH_E8 - 0.6))
            else:
                self.card_text(tx, t, card[2], T(card[0]), T(card[0] + card[1] - 0.8))
        if n >= end_n:
            ol = self.s.get('outro', [])
            if ol: tx.chars(ol[0], 960, 760, F(SERIF_B, 56), (235, 240, 235), t, T(end_n + 12), 999, stagger=self.e8 * 0.5)
            if len(ol) > 1: tx.chars(ol[1], 960, 840, F(SANS_M, 40), P.TAG, t, T(end_n + 14), 999, stagger=self.e8 * 0.5)
            if len(ol) > 2: tx.chars(ol[2], 960, 910, F(SANS_M, 34), (220, 225, 220), t, T(end_n + 16), 999, stagger=self.e8 * 0.5)

        flash = 0.16 * pulse(t, T(16), 0.4) + 0.30 * pulse(t, T(DROP), 0.6)
        if seg is not None: flash += 0.10 * pulse(t, T(seg['start']), 0.3)
        if card is not None: flash += (0.10 if card[2]['q'] else 0.035) * pulse(t, T(card[0]), 0.25)
        img = cv.composite(P.BG, flash) * P.VIG
        if self.logo is not None and n >= end_n + 10:
            hero.logo = self.logo; img = hero._put_logo(img, 960, 470, 170, 1.0, eo(ramp(n, end_n + 10, end_n + 13)))
        if card is not None and not card[2]['key']:
            img = img * (1 - 0.6 * BAND * eo(cl((t - T(card[0])) * 4)))
        img = tx.blend(img)
        img *= ramp(t, 0, 0.12)
        img *= 1 - ramp(t, self.duration - 1.2, self.duration - 0.1)
        return np.clip(img * 255, 0, 255).astype(np.uint8)
