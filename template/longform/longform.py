"""Long-form (8+ min) glow-beat video: one hero, a script of caption cards, a motif per chapter.

Script (JSON):
  {"title": "白羊座的内心世界", "subject": {"zodiac": "aries"} | {"mbti": "ENFJ"},
   "hook": {"q": ["你有没有遇到过", "这样一种人？"], "beats": ["明明天不怕地不怕", "却最怕被在乎的人误解"],
            "tagline": "外表有多【倔强】/内心就有多【柔软】"},
   "chapters": [{"name": "矛盾", "motif": "duality", "cards": ["明明上一秒/还笑得很灿烂", "*有一种人/外表有多倔强", ...]}],
   "outro": ["这里是洞悉", "看见表象之外"]}
Card: lines split by "/", "*" prefix = key card (giant, centred), 【word】 = gold.

Timing: every card starts on the music grid (eighth notes); durations are whole quarter notes sized to reading time.
The first ~10.6 s is a scripted hook (heartbeat -> glyph slam -> prop drop + candle burst -> hero grows -> title).
"""
import json, math, os, re, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import (W, H, GY, cl, ramp, eo, eio, lerp, pulse, pop, Palette, Cam, Canvas, flame, Text, F,
                         SERIF_B, SERIF_BL, SANS_M, spline)
from engine.scene import MBTIScene, ARM_L, ARM_R, lerp_pose, FLAMES, STARS, HILLS, CROWD, SHARDS
from engine.group import SubCam
from engine.signatures import SIGS
import zodiac_signs
from zodiac_signs import glyph_mask, draw_constellation, SIGNS
from vis import draw_vis, draw_face_fx, FACE as VIS_FACE, SCENE as VIS_SCENE, STATIC as VIS_ALL

# shot = (cam scale, cam cx, cam cy, hero x, hero k, hero alpha, icon x, icon y, icon size, motif alpha); cam None = chapter framing
SHOTS = {
    'hero':  (None, 0, 0, 960, 0.78, 1.0, 960, 430, 0, 1.0),
    'wide':  (0.80, 960, 500, 960, 0.78, 1.0, 960, 430, 0, 1.0),
    'side':  (1.0, 960, 540, 600, 0.74, 1.0, 1330, 450, 215, 0.25),
    'sideL': (1.0, 960, 540, 1320, 0.74, 1.0, 590, 450, 215, 0.25),
    'icon':  (1.0, 960, 540, 960, 0.78, 0.14, 960, 440, 290, 0.2),
    'scene': (1.0, 960, 540, 960, 0.78, 0.0, 960, 470, 330, 0.15),
    'face':  (2.6, 960, 410, 960, 0.78, 1.0, 960, 430, 0, 0.0),
    'quest': (1.25, 960, 520, 960, 0.78, 0.35, 960, 470, 330, 0.3),
}

HERO_K = 0.78               # hero scale on stage
HOOK_E8 = 40                # hook length in eighths


def parse_card(s):
    key = q = False; vis = shot = None
    while s and s[0] in '*?{':
        if s[0] == '*': key = True; s = s[1:]
        elif s[0] == '?': q = key = True; s = s[1:]
        else:
            j = s.index('}'); v = s[1:j]; s = s[j + 1:]
            vis, _, shot = v.partition('@'); shot = shot or None
    lines, golds = [], []
    for ln in s.split('/'):
        g = []; out = ''
        for part in re.split(r'(【[^】]*】)', ln):
            if part.startswith('【'):
                w = part[1:-1]; g += list(range(len(out), len(out) + len(w))); out += w
            else: out += part
        lines.append(out); golds.append(tuple(g))
    if q and not vis: vis = 'question'
    return dict(key=key, q=q, vis=vis, shot=shot, lines=lines, golds=golds, chars=sum(len(l) for l in lines))


# ================================================================ extra motifs for long form
def duality(gs, cv, tx, t, i, b, A, heads, face):
    """warm sun on the left, cold moon on the right; each card lights one side"""
    T, P = gs.T, gs.P
    n = gs.card_index(t)
    for side, x in ((0, 420), (1, 1500)):
        on = 0.35 + 0.65 * (1 if n % 2 == side else 0)
        c = (x, 300)
        if side == 0:
            cv.circle(c, 70, P.GOLD, A * on, 2.4); cv.glow(c, 140, P.GOLD, 0.4 * A * on)
            for k in range(16):
                q = k * math.pi / 8 + t * 0.1
                cv.path([(c[0] + 85 * math.cos(q), c[1] + 85 * math.sin(q)), (c[0] + 115 * math.cos(q), c[1] + 115 * math.sin(q))], P.WARM, A * on, 1.6, smooth=False)
        else:
            outer = [(c[0] + 70 * math.cos(q), c[1] + 70 * math.sin(q)) for q in np.linspace(math.radians(60), math.radians(300), 40)]
            inner = [(c[0] + 26 + 56 * math.cos(q), c[1] + 62 * math.sin(q)) for q in np.linspace(math.radians(285), math.radians(75), 40)]
            cv.path(outer + inner + [outer[0]], P.SOFT, A * on, 2.4, smooth=False); cv.glow(c, 120, P.SOFT, 0.25 * A * on)
    cv.path([(960, 120), (960, 760)], P.LINE, 0.25 * A, 1.2, smooth=False)


def messages(gs, cv, tx, t, i, b, A, heads, face):
    """chat bubbles: typed, then deleted (a message typed and deleted again)"""
    T, P = gs.T, gs.P
    n = gs.card_index(t)
    for k in range(min(n + 1, 6)):
        t0 = gs.card_start(k); age = t - t0
        x, y = (1330 if k % 2 == 0 else 590), 200 + (k % 3) * 120
        w = 300; g = eo(cl(age * 4))
        deleting = k == n and gs.card_index(t + 0.8) > n
        typed = cl(age * 1.5) if not deleting else cl(1 - (t - (gs.card_start(n + 1) - 0.8)) * 1.5)
        a = A * g * (0.45 if k < n - 2 else 1)
        box = [(x - w / 2, y - 40), (x + w / 2, y - 40), (x + w / 2, y + 40), (x - w / 2 + 40, y + 40), (x - w / 2 + 10, y + 64), (x - w / 2 + 14, y + 40), (x - w / 2, y + 40), (x - w / 2, y - 40)]
        cv.path(box, P.SOFT, a, 2, smooth=False)
        L = (w - 60) * typed
        if L > 2: cv.path([(x - w / 2 + 30, y), (x - w / 2 + 30 + L, y)], P.GOLD, a, 4, smooth=False)
        if typed < 1 and age > 0.1:
            for d in range(3): cv.circle((x + w / 2 - 70 + d * 20, y + 22), 4, P.WARM, a * (0.5 + 0.5 * math.sin(t * 8 + d)), fill=True)


def heart(gs, cv, tx, t, i, b, A, heads, face):
    """small lights gather, one per card, into a glowing heart"""
    T, P = gs.T, gs.P; c = (960, 300); S = 9.0
    pts = [(c[0] + S * 16 * math.sin(q) ** 3, c[1] - S * (13 * math.cos(q) - 5 * math.cos(2 * q) - 2 * math.cos(3 * q) - math.cos(4 * q))) for q in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    n = gs.card_index(t)
    got = min(24, (n + 1) * 3)
    for k in range(got):
        tf = gs.card_start(k // 3) + (k % 3) * 0.12
        src = (960 + 900 * math.cos(k * 2.4), 540 + 500 * math.sin(k * 1.7)); g = eo(cl((t - tf) * 1.6))
        p = (lerp(src[0], pts[k][0], g), lerp(src[1], pts[k][1], g))
        cv.circle(p, 5, P.WARM, A, fill=True); cv.glow(p, 16, P.GOLD, 0.6 * A)
    if got >= 24:
        cv.path(pts + [pts[0]], P.GOLD, A, 2.4); cv.glow(c, 160, P.GOLD, 0.3 * A)


def bolts(gs, cv, tx, t, i, b, A, heads, face):
    """quick tempers: a bolt strikes on each card, then a calm ring"""
    T, P = gs.T, gs.P
    n = gs.card_index(t); t0 = gs.card_start(n); age = t - t0
    if age < 0.5:
        rng = np.random.default_rng(n * 7 + int(age * 24))
        x0 = 400 + (n * 397) % 1100; pts = [(x0, -20)]
        for k in range(8): pts.append((pts[-1][0] + rng.uniform(-40, 40), pts[-1][1] + 70))
        a = A * (1 - age / 0.5)
        cv.path(pts, P.WARM, a, 2.6, smooth=False); cv.path(pts, P.GOLD, a * 0.5, 12, smooth=False, layer=cv.F)
    if age > 0.6:
        k = cl((age - 0.6) / 1.5)
        cv.circle((960, 560), 200 + 500 * eo(k), P.SOFT, A * (1 - k) * 0.6, 1.6)


EXTRA = dict(duality=duality, messages=messages, heart=heart, bolts=bolts)
MOTIF_CAM = {  # (scale, cx, cy) framing per motif
    'duality': (1.0, 960, 520), 'ignite': (1.1, 960, 640), 'messages': (1.0, 960, 500), 'heart': (1.05, 960, 470),
    'ripples': (1.1, 960, 640), 'bolts': (1.0, 960, 520), 'bloom': (1.25, 960, 430), 'circle': (1.1, 960, 680),
    'summit': (1.05, 1080, 560), 'pillars': (1.1, 960, 620), 'moonrise': (1.2, 960, 420), 'sunburst': (1.2, 960, 470),
    'lanterns': (1.1, 960, 560), 'fireworks': (1.1, 960, 480), 'lightlink': (1.15, 960, 680), 'garden': (1.1, 960, 650),
    'harvest': (1.1, 960, 660), 'gears': (1.1, 1060, 560), 'brush': (1.2, 960, 500), 'target': (1.1, 1050, 560),
    'spotlight': (1.1, 960, 560), 'shield': (1.1, 980, 660), 'checklist': (1.1, 1060, 560), 'balance': (1.1, 960, 450),
    'planes': (1.1, 960, 460), 'school': (1.1, 960, 520), 'phoenix': (1.1, 960, 520), 'arrows': (1.1, 1040, 470),
    'formation': (1.1, 960, 680), 'blueprint': (1.1, 1000, 620), 'tree': (1.2, 1000, 480), 'morph': (1.1, 960, 430),
}


class LongScene:
    def __init__(self, script, offset=0.0, eighth=60 / 112.9 / 2, logo=None, brand=None, target=(482, 505)):
        self.s = script; self.off, self.e8 = offset, eighth; self.E8 = eighth; self.logo = logo; self.brand = brand or {}
        sub = script['subject']
        if 'zodiac' in sub:
            from zodiac_scene import load
            self.hero = load(sub['zodiac'], offset, eighth, None, brand)
            self.sign = self.hero.sign
            self.glyph = glyph_mask(self.sign['glyph'], 300)
        else:
            with open(os.path.join(HERE, '..', 'mbti', 'types', sub['mbti'] + '.json'), encoding='utf-8') as f: cfg = json.load(f)
            self.hero = MBTIScene(cfg, offset, eighth); self.sign = None
            from PIL import Image, ImageDraw
            im = Image.new('L', (900, 360), 0); ImageDraw.Draw(im).text((450, 130), sub['mbti'], font=F(SERIF_BL, 200), fill=255, anchor='mm')
            self.glyph = np.asarray(im, np.float32) / 255
        self.P = self.hero.P
        self.XS = (960,)
        self.members = [(self.hero, None)]
        self._build_timeline(target)

    def T(self, n): return self.off + n * self.e8

    # ------------------------------------------------------------ timeline
    def _build_timeline(self, target):
        chapters = self.s['chapters']
        for ch in chapters: ch['_cards'] = [parse_card(c) for c in ch['cards']]
        def layout(cps):
            n = HOOK_E8; segs = []
            for ci, ch in enumerate(chapters):
                ch_start = n; n += 8                               # chapter title card: 2 bars of quarter... 8 eighths
                cards = []
                for c in ch['_cards']:
                    secs = c['chars'] / cps + (1.6 if c['key'] else 0.9)
                    e = int(math.ceil(secs / self.e8 / 2.0)) * 2
                    e = max(e, 14 if c['key'] else 10); e = min(e, 30)
                    cards.append((n, e, c)); n += e
                segs.append(dict(ci=ci, start=ch_start, end=n, cards=cards, motif=ch['motif'], name=ch['name']))
            end_n = n; n += 24                                     # outro / brand
            return segs, end_n, n
        lo, hi = 2.0, 9.0
        for _ in range(30):
            cps = (lo + hi) / 2; segs, end_n, total = layout(cps)
            dur = self.T(total)
            if dur < target[0]: hi = cps
            elif dur > target[1]: lo = cps
            else: break
        self.cps = cps; self.segs, self.outro_n, self.total_n = segs, end_n, total
        self._assign_shots()
        self.duration = self.T(self.total_n) + 1.0

    def _assign_shots(self):
        """every card gets a different framing from the one before it (wide / medium / close-up / insert / two-shot)"""
        prev = 'hero'; nside = 0; nvis = 0
        for sg in self.segs:
            prev = 'hero'
            for (cn, ce, c) in sg['cards']:
                v = c['vis']; sh = c['shot']
                if v and v not in VIS_ALL: v = c['vis'] = None
                if not sh:
                    if c['q']: sh = 'quest'
                    elif v in VIS_FACE: sh = 'face'
                    elif c['key']: sh = 'icon' if v else ('wide' if prev == 'hero' else 'hero')
                    elif v in VIS_SCENE: sh = 'scene'
                    elif v:
                        nvis += 1
                        sh = 'icon' if nvis % 3 == 0 else ('side' if nside % 2 == 0 else 'sideL'); nside += sh != 'icon'
                    else: sh = 'wide' if prev in ('hero', 'face') else 'hero'
                    if sh == prev and sh in ('hero', 'wide'): sh = 'wide' if sh == 'hero' else 'hero'
                c['_shot'] = sh; c['_shot2'] = None
                if ce * self.e8 > 5.0:
                    c['_shot2'] = {'side': 'icon', 'sideL': 'icon', 'icon': 'side', 'scene': 'icon', 'hero': 'wide', 'wide': 'hero',
                                   'face': 'hero', 'quest': None}.get(sh)
                    if c['_shot2'] == 'wide' and not v and not c['key']: c['_shot2'] = 'face'
                prev = c['_shot2'] or sh

    def shot_at(self, t, seg, card):
        """interpolated shot parameters (eased cut over ~0.3 s at each card start, punch-in halfway through long cards)"""
        def params(sh):
            p = list(SHOTS[sh])
            if p[0] is None:
                s1, x1, y1 = MOTIF_CAM.get(seg['motif'], (1.05, 960, 540)) if seg else (1.08, 960, 520)
                p[0], p[1], p[2] = s1, x1, y1
            return p
        if seg is None or card is None:
            return params('hero'), 0.0
        idx = [c[0] for c in seg['cards']].index(card[0])
        sh = card[2]['_shot']
        pre = params(seg['cards'][idx - 1][2].get('_shot2') or seg['cards'][idx - 1][2]['_shot']) if idx > 0 else params('hero')
        t0 = self.T(card[0]); dur = card[1] * self.e8
        alt = card[2].get('_shot2')
        tm = self.T(card[0] + 2 * int(card[1] / 4)) if alt else 1e9
        if t >= tm:   # second angle halfway through a long card
            pre, cur, ts = params(sh), params(alt), tm
        else:
            cur, ts = params(sh), t0
        k = eio(cl((t - ts) / 0.32))
        out = [lerp(a, b, k) for a, b in zip(pre, cur)]
        out[0] *= 1 + 0.045 * cl((t - ts) / max(dur / 2, 1))
        return out, pulse(t, ts, 0.3)

    def seg_at(self, t):
        n = (t - self.off) / self.e8
        for s in self.segs:
            if s['start'] <= n < s['end']: return s
        return None

    # signature adapter: T(b + j) = start of card j-1 inside the current chapter
    def _bind(self, seg):
        self._seg = seg
        starts = [self.T(seg['start'])] + [self.T(c[0]) for c in seg['cards']] + [self.T(seg['end'])]
        self._starts = np.array(starts)
        nc = max(1, len(seg['cards'])); self._avg = (starts[-1] - starts[1]) / nc

    def _card_at(self, seg, t):
        n = (t - self.off) / self.e8
        for c in seg['cards']:
            if c[0] <= n < c[0] + c[1]: return c
        return None

    def card_index(self, t):
        st = self._starts[1:-1]
        return max(0, int(np.searchsorted(st, t, side='right')) - 1)

    def card_start(self, k):
        st = self._starts[1:-1]
        return st[min(k, len(st) - 1)] if k < len(st) else self._starts[-1] + (k - len(st)) * self._avg

    def quarter(self, t): return self.off + 2 * self.E8 * math.floor((t - self.off) / (2 * self.E8))

    # ------------------------------------------------------------ camera
    def camera(self, t):
        T = self.T; n = (t - self.off) / self.e8
        if n < HOOK_E8:
            keys = [(0, 1.6, 960, 540), (10, 1.6, 960, 540), (12, 1.0, 960, 560), (14, 2.2, 960, 560), (22, 1.7, 960, 400), (24, 1.0, 960, 520), (40, 1.08, 960, 520)]
            s, cx, cy = keys[0][1:]
            for (k, s1, x1, y1), (k0) in zip(keys[1:], keys[:-1]):
                if n < k0[0]: break
                kk = eio(cl((n - k0[0]) / max(1e-6, (k - k0[0])))) if n < k else 1
                s, cx, cy = lerp(k0[1], s1, kk), lerp(k0[2], x1, kk), lerp(k0[3], y1, kk)
        else:
            seg = self.seg_at(t)
            card = self._card_at(seg, t) if seg else None
            if seg is None: s, cx, cy = 1.0, 960, 540
            elif card is not None:
                sp, _ = self.shot_at(t, seg, card); s, cx, cy = sp[0], sp[1], sp[2]
            else:
                s1, x1, y1 = MOTIF_CAM.get(seg['motif'], (1.05, 960, 540))
                prev = self.segs[seg['ci'] - 1]['motif'] if seg['ci'] > 0 else None
                s0, x0, y0 = MOTIF_CAM.get(prev, (1.08, 960, 520)) if prev else (1.08, 960, 520)
                k = eio(cl((t - T(seg['start'])) / 0.45))
                s, cx, cy = lerp(s0, s1, k), lerp(x0, x1, k), lerp(y0, y1, k)
                # slow drift within the chapter
                u = (t - T(seg['start'])) / max(1.0, T(seg['end']) - T(seg['start']))
                s *= 1 + 0.05 * u; cx += 30 * math.sin(u * math.pi)
                # chapter entry whip
                s *= 1 + 0.12 * pulse(t, T(seg['start']), 0.35)
        if t > 0.6: s *= 1 + 0.012 * pulse(t, self.quarter(t), 0.35)
        return Cam(s, cx, cy)

    # ------------------------------------------------------------ text
    def card_text(self, tx, t, c, t0, t1):
        P = self.P
        if c['key']:
            n = len(c['lines']); ml = max(len(l) for l in c['lines'])
            fs = 96 if ml <= 9 else (84 if ml <= 11 else 72); gap = int(fs * 1.35)
            y0 = 520 - (n - 1) * gap / 2 + fs * 0.35
            for k, (l, g) in enumerate(zip(c['lines'], c['golds'])):
                tx.chars(l, 960, int(y0 + k * gap), F(SERIF_BL, fs), P.WHITE, t, t0 + k * 2 * self.e8, t1, gold=g, stagger=0.045)
        else:
            n = len(c['lines']); ml = max(len(l) for l in c['lines'])
            fs = 72 if ml <= 11 else (64 if ml <= 13 else 56); gap = int(fs * 1.38)
            y0 = 1000 - (n - 1) * gap
            for k, (l, g) in enumerate(zip(c['lines'], c['golds'])):
                tx.chars(l, 960, int(y0 + k * gap), F(SERIF_B, fs), P.WHITE, t, t0 + k * 2 * self.e8, t1, gold=g, stagger=0.03)

    # ================================================================ FRAME
    def frame(self, t):
        T, P, hero = self.T, self.P, self.hero
        G, Wm, LN, SO = P.GOLD, P.WARM, P.LINE, P.SOFT
        n = (t - self.off) / self.e8
        cam = self.camera(t); cv = Canvas(cam); tx = Text(P)
        seg = self.seg_at(t)
        end_n = self.outro_n; endF = eio(ramp(n, end_n + 6, end_n + 14)); amb = 1 - 0.7 * endF
        card = None; key_dim = 0.0
        if seg is not None:
            for (cn, ce, c) in seg['cards']:
                if cn <= n < cn + ce: card = (cn, ce, c)
            if card and card[2]['key']: key_dim = eo(cl((n - card[0]) / 2)) * (1 - eo(cl((n - card[0] - card[1] + 2) / 2)))
            if card is None:   # chapter title card: dim the world so the title reads cleanly over the hero
                key_dim = 1.15 * eo(cl((n - seg['start']) / 1.5)) * (1 - eo(cl((n - seg['start'] - 6.5) / 1.5)))
        world = amb * (1 - 0.55 * key_dim)
        qt = self.quarter(t)
        # ---- sky ----
        for (x, y, r, ph, sp, gold) in STARS:
            tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph))
            cv.circle((x, y + 4 * math.sin(t * 0.4 + ph)), r, G if gold else LN, tw * 0.45 * ramp(n, 2, 8), fill=True, layer=cv.F)
        if self.sign and n >= 24:
            draw_constellation(cv, self.sign, (120, 70, 470, 260), P, t, 0.85 * amb * ramp(n, 24, 26), eo(ramp(n, 24, 30)))
        hk = ramp(n, 12, 20)
        for k, hp in enumerate(HILLS): cv.path(hp, P.DIM, 0.5 * hk * world * (1 - 0.3 * k), 1.4, hk, smooth=False)
        # ---- ground + candles ----
        gl = eo(ramp(n, 10, 11))
        cv.path([(-100, GY), (2020, GY)], LN, 0.7 * world * gl, 1.6, smooth=False)
        cv.path([(-100, GY), (2020, GY)], LN, 0.22 * world * gl, 6, smooth=False, layer=cv.F)
        if n >= 10:
            k = pulse(t, T(10), 0.5)
            Pr = [(960 + 260 * math.cos(q), GY + 22 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 100)]
            cv.path(Pr, Wm, (0.4 + 1.2 * k) * world, 3, smooth=False); cv.glow((960, GY), 140, G, 0.6 * k)
        for j, (x, y, h, ph, r) in enumerate(FLAMES):
            d = abs(x - 960); ton = T(10 + (0 if d < 260 else (1 if d < 620 else 2)))
            if t < ton: continue
            boost = 1 + 2.0 * pulse(t, ton, 0.25) + 0.25 * pulse(t, qt, 0.3)
            a = min(1.6, boost) * world; hh = h * (1 + 0.12 * math.sin(t * 7 + ph)) * pop(t, ton, 0.16)
            flame(cv, x, y, hh, G, 0.95 * a, lean=0.08 * math.sin(t * 2 + ph)); flame(cv, x, y, hh * 1.6, G, 0.25 * a, layer=cv.F)
        # ---- hook: heartbeat, glyph slam, prop drop ----
        if n < HOOK_E8 + 2:
            for p0 in (0, 1, 4, 5):
                if T(p0) <= t < T(p0) + 0.8:
                    k = (t - T(p0)) / 0.8
                    cv.circle((960, 540), 60 + 380 * eo(k), G, (1 - k) * 0.9, 2.4); cv.glow((960, 540), 120, G, 0.6 * pulse(t, T(p0), 0.3))
        # ---- hero ----
        prog = ramp(n, 14, 22)
        shp, cut = self.shot_at(t, seg, card) if n >= HOOK_E8 else (list(SHOTS['hero']), 0.0)
        hx, hkk, ha = (shp[3], shp[4], shp[5]) if n >= HOOK_E8 else (960, HERO_K, 1.0)
        self.XS = (hx,)
        sub = SubCam(cam, hx, hkk)
        cv.cam = sub
        aL, aR = ARM_L['rest'], ARM_R['rest']
        bright = 0.25 + 0.5 * pulse(t, qt, 0.3) * (seg is not None)
        if n >= 14 and ha > 0.01: hero.draw_figure(cv, t, world * ha, prog, aL, aR, 0.0, bright)
        if n >= 9:
            fall = eo(ramp(n, 9, 10)); off = lerp(-1400, 0, fall)
            grip = (960, 578) if hero.prop == 'sword' else (960, 540)
            if ha <= 0.01: fall = 1.0
            if fall < 1:
                for k in range(5): cv.path([(960 + (k - 2) * 6, 230 + off - 300), (960 + (k - 2) * 6, 230 + off + 200)], G, 0.25, 2, smooth=False, layer=cv.F)
            if ha > 0.01: head, tip = hero.draw_prop(cv, (grip[0], grip[1] + off), math.pi / 2, world * ha, 0.4 + 0.4 * key_dim, t)
        if card is not None and card[2]['vis'] in VIS_FACE:
            draw_face_fx(self, cv, card[2]['vis'], t, T(card[0]), T(card[0] + card[1]), amb * ha)
        cv.cam = cam
        face = [tuple(sub.to_world([(960, 250)])[0])]
        heads = [(tuple(sub.to_world([(960, 470)])[0]),) * 2]
        if n < 10.5 and n >= 9:   # beam on the prop
            cv.path([(960, -100), (960, GY - 300)], Wm, 1.2 * pulse(t, T(10), 0.4) + 0.3, 3, smooth=False)
        # mandorla + halo after the title
        md = eio(ramp(n, 24, 27))
        if md > 0:
            ma = md * world * ha
            def egg(sc_):
                return [(hx + 300 * hkk * sc_ * (1 - 0.13 * math.cos(q)) * math.sin(q), GY - (GY - 495) * hkk - 420 * hkk * sc_ * math.cos(q)) for q in np.linspace(-math.pi, math.pi, 160)]
            cv.path(egg(1.0), LN, 0.7 * ma, 2.0, md, smooth=False)
            for k, p in enumerate(egg(1.0)[::6]):
                if p[1] < GY - 10: flame(cv, p[0], p[1] + 5, 12 * (1 + 0.1 * math.sin(t * 6 + k)), G, 0.8 * ma)
        # ---- chapter motif ----
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
                finally: self.T, self.e8 = saveT, save8
            # chapter entry: ring + flash
            hero.ring_burst(cv, t, T(seg['start']), (960, 520), 100, 900, 0.9)
            if card and card[2]['vis'] and card[2]['vis'] not in VIS_FACE and shp[8] > 0:
                ec = cv.cam; cv.cam = Cam(1.0)
                va = amb * (0.5 if card[2]['key'] and not card[2]['q'] else 1.0) * (0.55 if card[2]['q'] else 1.0)
                draw_vis(self, cv, card[2]['vis'], t, T(card[0]), T(card[0] + card[1]), shp[6], shp[7], shp[8], va)
                cv.cam = ec
            if card and card[2]['key'] and card[2]['_shot'] not in ('face',):
                hero.star_flare(cv, (960, 470), 380, pulse(t, T(card[0]), 0.6) * 1.2)
            elif card:
                cv.glow((960, 600), 300, G, 0.12 * pulse(t, T(card[0]), 0.3))
        # ---- outro: crowd rises, sunburst-free calm, logo ----
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
        hk_ = self.s['hook']
        if n < HOOK_E8 + 1:
            q = hk_['q']
            tx.chars(q[0], 960, 470, F(SERIF_BL, 88), P.WHITE, t, T(2), T(8.6), stagger=0.04)
            tx.chars(q[1], 960, 600, F(SERIF_BL, 88), P.WHITE, t, T(4), T(8.6), stagger=0.04)
            bt = hk_['beats']
            tx.chars(bt[0], 960, 900, F(SERIF_B, 64), P.WHITE, t, T(14), T(23.6), stagger=0.03)
            tx.chars(bt[1], 960, 990, F(SERIF_B, 64), P.WHITE, t, T(18), T(23.6), stagger=0.03)
            tt = self.s['title']
            tx.chars(tt, 960, 560, F(SERIF_BL, 132 if len(tt) <= 8 else 110), P.HI, t, T(24), T(HOOK_E8 - 0.4), stagger=0.05)
            tg = parse_card(hk_['tagline'])
            for k, (l, g) in enumerate(zip(tg['lines'], tg['golds'])):
                tx.chars(l, 960, 700 + k * 92, F(SERIF_B, 68), P.WHITE, t, T(31 + 2 * k), T(HOOK_E8 - 0.4), gold=g, stagger=0.04)
        if seg is not None:
            st = T(seg['start'])
            tx.chars(f"CHAPTER {seg['ci'] + 1:02d}", 960, 400, F(SANS_M, 44), P.TAG, t, st, T(seg['start'] + 7.6), stagger=0.03)
            tx.chars(seg['name'], 960, 580, F(SERIF_BL, 150), P.WHITE, t, st + 0.05, T(seg['start'] + 7.6), stagger=0.06)
            if card:
                self.card_text(tx, t, card[2], T(card[0]), T(card[0] + card[1] - 0.8))
        if n >= end_n:
            ol = self.s.get('outro', [])
            if ol: tx.chars(ol[0], 960, 760, F(SERIF_B, 56), (235, 240, 235), t, T(end_n + 12), 999, stagger=0.04)
            if len(ol) > 1: tx.chars(ol[1], 960, 840, F(SANS_M, 40), P.TAG, t, T(end_n + 14), 999, stagger=0.04)
            if len(ol) > 2: tx.chars(ol[2], 960, 910, F(SANS_M, 34), (220, 225, 220), t, T(end_n + 16), 999, stagger=0.04)

        flash = 0.12 * pulse(t, T(6), 0.4) + 0.12 * pulse(t, T(10), 0.4) + 0.18 * pulse(t, T(24), 0.5)
        if seg is not None: flash += 0.08 * pulse(t, T(seg['start']), 0.3)
        if card is not None: flash += (0.10 if card[2]['q'] else 0.035) * pulse(t, T(card[0]), 0.25)
        img = cv.composite(P.BG, flash) * P.VIG
        # glyph slam in the hook (and faint behind key cards)
        if self.glyph is not None:
            ga = 0.0
            if 6 <= n < 14: ga = (1 + 1.5 * pulse(t, T(6), 0.3)) * (1 - ramp(n, 12, 14))
            if card and card[2]['key']: ga = max(ga, 0.18 * key_dim)
            if ga > 0.01:
                sz = 1.0 + 0.25 * pulse(t, T(6), 0.25) if n < 14 else 1.0
                gm = cv2.resize(self.glyph, None, fx=sz, fy=sz); h, w = gm.shape
                gl = gm[..., None] * np.array(P.GOLD, np.float32) * ga
                cy, cx = (330 if n < 14 else 520), 960
                y0, x0 = max(0, cy - h // 2), max(0, cx - w // 2); gl = gl[: H - y0, : W - x0]
                img[y0:y0 + gl.shape[0], x0:x0 + gl.shape[1]] += gl + cv2.GaussianBlur(gl, (0, 0), 14) * 0.9
        if self.logo is not None and n >= end_n + 10:
            hero.logo = self.logo; img = hero._put_logo(img, 960, 470, 170, 1.0, eo(ramp(n, end_n + 10, end_n + 13)))
        # caption band (mobile legibility)
        if card is not None and not card[2]['key']:
            band = BAND * eo(cl((t - T(card[0])) * 4))
            img = img * (1 - 0.6 * band)
        img = tx.blend(img)
        img *= ramp(t, 0, 0.15) * 0 + 1
        img *= 1 - ramp(t, self.duration - 1.2, self.duration - 0.1)
        return np.clip(img * 255, 0, 255).astype(np.uint8)


_yy = np.mgrid[0:H, 0:1][0].astype(np.float32)
BAND = (np.clip((_yy - 780) / 220, 0, 1) ** 1.2)[..., None]
