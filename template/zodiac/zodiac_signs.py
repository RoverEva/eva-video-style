"""12 zodiac signs — data + drawing (hero emblems, sign props, constellations, glyphs).

Reuses the MBTI drawing engine (template/mbti/engine): same canvas, glow, hero figure, faces and props.
Element palettes: fire / earth / air / water.
"""
import math, os, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mbti'))
from engine.core import (W, H, GY, PALETTES, Palette, Cam, Canvas, flame, Text, F, SERIF_B, SERIF_BL, SANS_M,
                         spline, mir, lerp, cl, ramp, eo, pulse)
from engine.scene import MBTIScene, ARM_L, ARM_R, lerp_pose, FLAMES, STARS
from engine.group import SubCam

# ---------------------------------------------------------------- element palettes (BGR)
PALETTES.update({
    'fire':  dict(line=(0.32, 0.58, 1.00), soft=(0.66, 0.84, 1.00), gold=(0.42, 0.86, 1.00), warm=(0.76, 0.95, 1.00),
                  dim=(0.18, 0.28, 0.55), bg=(0.015, 0.02, 0.055), bg_c=(0.02, 0.035, 0.09),
                  hi_rgb=(255, 214, 120), tag_rgb=(255, 170, 120)),
    'earth': dict(line=(0.36, 0.78, 0.62), soft=(0.70, 0.92, 0.86), gold=(0.40, 0.80, 0.98), warm=(0.74, 0.94, 1.00),
                  dim=(0.22, 0.42, 0.36), bg=(0.02, 0.04, 0.035), bg_c=(0.03, 0.06, 0.055),
                  hi_rgb=(240, 214, 140), tag_rgb=(190, 220, 150)),
    'air':   dict(line=(0.90, 0.95, 0.86), soft=(1.00, 1.00, 0.96), gold=(0.55, 0.88, 1.00), warm=(0.90, 0.98, 1.00),
                  dim=(0.45, 0.48, 0.42), bg=(0.045, 0.045, 0.04), bg_c=(0.075, 0.075, 0.065),
                  hi_rgb=(255, 228, 160), tag_rgb=(225, 235, 235)),
    'water': dict(line=(1.00, 0.60, 0.20), soft=(1.00, 0.86, 0.62), gold=(0.62, 0.90, 1.00), warm=(0.88, 0.98, 1.00),
                  dim=(0.50, 0.28, 0.10), bg=(0.07, 0.03, 0.01), bg_c=(0.11, 0.045, 0.012),
                  hi_rgb=(240, 230, 170), tag_rgb=(120, 225, 230)),
})
ELEMENT_CN = {'fire': '火象星座', 'earth': '土象星座', 'air': '风象星座', 'water': '水象星座'}
ELEMENT_EN = {'fire': 'Fire', 'earth': 'Earth', 'air': 'Air', 'water': 'Water'}

# ---------------------------------------------------------------- the 12 signs
SIGNS = [
    dict(key='aries', cn='白羊座', en='Aries', glyph='♈', dates='3.21 – 4.19', element='fire', prop='sword', emblem='ram',
         look=dict(hair='spiky', eyes='sharp', brows='angled', mouth='grin', acc=[]),
         stars=[(0.0, 0.62), (0.42, 0.40), (0.74, 0.44), (0.96, 0.62)], lines=[(0, 1), (1, 2), (2, 3)]),
    dict(key='taurus', cn='金牛座', en='Taurus', glyph='♉', dates='4.20 – 5.20', element='earth', prop='orb', emblem='bull',
         look=dict(hair='crew', eyes='open', brows='straight', mouth='calm', acc=['earrings']),
         stars=[(0.08, 0.10), (0.30, 0.38), (0.42, 0.52), (0.50, 0.62), (0.60, 0.50), (0.72, 0.36), (0.92, 0.16), (0.38, 0.58), (0.96, 0.82)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)]),
    dict(key='gemini', cn='双子座', en='Gemini', glyph='♊', dates='5.21 – 6.21', element='air', prop='none', emblem='twins',
         look=dict(hair='side_part', eyes='smile', brows='soft', mouth='smile', acc=[]),
         look2=dict(hair='tousled', eyes='open', brows='raised', mouth='smirk', acc=[]),
         stars=[(0.22, 0.08), (0.25, 0.45), (0.30, 0.90), (0.55, 0.06), (0.58, 0.45), (0.64, 0.88), (0.12, 0.62), (0.78, 0.62)],
         lines=[(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 6), (4, 7)]),
    dict(key='cancer', cn='巨蟹座', en='Cancer', glyph='♋', dates='6.22 – 7.22', element='water', prop='lantern', emblem='moon',
         look=dict(hair='hood', eyes='closed', brows='soft', mouth='smile', acc=[]),
         stars=[(0.50, 0.50), (0.28, 0.14), (0.76, 0.18), (0.50, 0.92)], lines=[(0, 1), (0, 2), (0, 3)]),
    dict(key='leo', cn='狮子座', en='Leo', glyph='♌', dates='7.23 – 8.22', element='fire', prop='sword', emblem='mane',
         look=dict(hair='swept', eyes='sharp', brows='angled', mouth='smile', acc=['crown']),
         stars=[(0.22, 0.12), (0.12, 0.28), (0.18, 0.46), (0.34, 0.56), (0.70, 0.44), (0.92, 0.62), (0.70, 0.68)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)]),
    dict(key='virgo', cn='处女座', en='Virgo', glyph='♍', dates='8.23 – 9.22', element='earth', prop='wheat', emblem='none',
         look=dict(hair='braid', eyes='closed', brows='soft', mouth='calm', acc=['flower']),
         stars=[(0.06, 0.30), (0.28, 0.40), (0.48, 0.46), (0.68, 0.62), (0.86, 0.88), (0.54, 0.18), (0.76, 0.08)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (5, 6)]),
    dict(key='libra', cn='天秤座', en='Libra', glyph='♎', dates='9.23 – 10.23', element='air', prop='scales', emblem='none',
         look=dict(hair='long_straight', eyes='open', brows='soft', mouth='smile', acc=['circlet']),
         stars=[(0.50, 0.10), (0.26, 0.46), (0.74, 0.46), (0.22, 0.84), (0.78, 0.78)], lines=[(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)]),
    dict(key='scorpio', cn='天蝎座', en='Scorpio', glyph='♏', dates='10.24 – 11.22', element='water', prop='sword', emblem='tail',
         look=dict(hair='hood', eyes='sharp', brows='angled', mouth='smirk', acc=[]),
         stars=[(0.06, 0.08), (0.12, 0.20), (0.06, 0.32), (0.28, 0.30), (0.40, 0.46), (0.46, 0.62), (0.52, 0.78), (0.66, 0.88), (0.82, 0.82), (0.88, 0.66)],
         lines=[(0, 1), (1, 2), (1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]),
    dict(key='sagittarius', cn='射手座', en='Sagittarius', glyph='♐', dates='11.23 – 12.21', element='fire', prop='bow', emblem='none',
         look=dict(hair='ponytail', eyes='open', brows='raised', mouth='grin', acc=[]),
         stars=[(0.16, 0.52), (0.34, 0.34), (0.50, 0.40), (0.60, 0.26), (0.70, 0.40), (0.66, 0.62), (0.40, 0.66), (0.86, 0.46), (0.82, 0.64)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 4), (2, 4), (4, 5), (5, 6), (6, 0), (4, 7), (7, 8), (8, 5)]),
    dict(key='capricorn', cn='摩羯座', en='Capricorn', glyph='♑', dates='12.22 – 1.19', element='earth', prop='star', emblem='goat',
         look=dict(hair='side_part', eyes='sharp', brows='straight', mouth='line', acc=[]),
         stars=[(0.06, 0.24), (0.36, 0.58), (0.66, 0.76), (0.90, 0.46), (0.74, 0.34), (0.40, 0.30)], lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]),
    dict(key='aquarius', cn='水瓶座', en='Aquarius', glyph='♒', dates='1.20 – 2.18', element='air', prop='urn', emblem='none',
         look=dict(hair='faux_hawk', eyes='open', brows='raised', mouth='smile', acc=['glasses']),
         stars=[(0.06, 0.30), (0.28, 0.24), (0.44, 0.40), (0.56, 0.28), (0.70, 0.50), (0.60, 0.70), (0.80, 0.88)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]),
    dict(key='pisces', cn='双鱼座', en='Pisces', glyph='♓', dates='2.19 – 3.20', element='water', prop='none', emblem='fish',
         look=dict(hair='long_wavy', eyes='closed', brows='soft', mouth='smile', acc=['earrings']),
         stars=[(0.08, 0.14), (0.16, 0.08), (0.20, 0.20), (0.12, 0.26), (0.50, 0.90), (0.84, 0.40), (0.92, 0.32), (0.96, 0.46)],
         lines=[(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 5)]),
]

_ENFJ = json.load(open(os.path.join(HERE, '..', 'mbti', 'types', 'ENFJ.json'), encoding='utf-8'))


def hero(sign, look=None):
    cfg = dict(_ENFJ); cfg['palette'] = sign['element']; cfg['look'] = look or sign['look']
    cfg['prop'] = sign['prop'] if sign['prop'] in ('sword', 'orb', 'lantern', 'star') else 'none'
    return MBTIScene(cfg)


# ---------------------------------------------------------------- emblems (drawn in hero coordinates)
def draw_emblem(sc, cv, sign, t, a=1.0):
    P = sc.P; S, G, Wm, L = P.SOFT, P.GOLD, P.WARM, P.LINE
    e = sign['emblem']
    if e == 'ram':
        for sx in (-1, 1):
            c = (960 + sx * 52, 214); pts = []
            for k in range(60):
                q = k / 60 * 2.4 * math.pi; r = 34 * (1 - k / 75)
                pts.append((c[0] + sx * r * math.cos(q + math.pi), c[1] + r * math.sin(q + math.pi) * 0.95))
            cv.path(pts, G, a, 3); cv.path(pts, G, a * 0.3, 10, layer=cv.F)
    elif e == 'bull':
        for sx in (-1, 1):
            pts = [(960 + sx * 30, 196), (960 + sx * 70, 176), (960 + sx * 104, 140), (960 + sx * 112, 96), (960 + sx * 98, 70)]
            cv.path(pts, G, a, 3.2); cv.path([(960 + sx * 40, 204), (960 + sx * 80, 190), (960 + sx * 112, 150), (960 + sx * 116, 110), (960 + sx * 98, 70)], G, a * 0.8, 2)
    elif e == 'goat':
        for sx in (-1, 1):
            pts = [(960 + sx * 18, 188), (960 + sx * 34, 140), (960 + sx * 62, 100), (960 + sx * 100, 84), (960 + sx * 132, 96)]
            cv.path(pts, G, a, 3)
            for k in range(1, 4):
                p = spline(pts)[k * 10]; cv.path([(p[0] - 8, p[1] - 6), (p[0] + 8, p[1] + 6)], G, a * 0.6, 1.4, smooth=False)
    elif e == 'mane':
        pts = []
        for k in range(29):
            q = math.radians(150 + k * 240 / 28); r = 96 if k % 2 == 0 else 128 + 8 * math.sin(t * 3 + k)
            pts.append((960 + r * math.cos(q), 250 + r * 1.05 * math.sin(q)))
        cv.path(pts, G, a, 2.6, smooth=False); cv.poly(pts + [(960, 250)], G * 0.06, a, layer=cv.F)
        for k in range(0, 29, 2):
            q = math.radians(150 + k * 240 / 28)
            cv.path([(960 + 96 * math.cos(q), 250 + 100 * math.sin(q)), (960 + 116 * math.cos(q), 250 + 122 * math.sin(q))], L, a * 0.5, 1.2, smooth=False)
    elif e == 'moon':
        c, R = (960, 92), 46
        outer = [(c[0] + R * math.cos(q), c[1] + R * math.sin(q)) for q in np.linspace(math.radians(60), math.radians(300), 40)]
        inner = [(c[0] + 18 + R * 0.78 * math.cos(q), c[1] + R * 0.86 * math.sin(q)) for q in np.linspace(math.radians(285), math.radians(75), 40)]
        cv.path(outer + inner, Wm, a, 2.4, smooth=False); cv.poly(outer + inner, G * 0.25, a, layer=cv.F); cv.glow(c, 70, G, 0.4 * a)
    elif e == 'tail':
        from engine.core import offset_line
        base = [(1030, 780), (1150, 720), (1220, 580), (1215, 420), (1170, 280), (1110, 190), (1060, 160)]
        A_, B_ = offset_line(base, 26, 9)
        cv.path(A_, S, a, 2.2, smooth=False); cv.path(B_, S, a, 2.2, smooth=False)
        Pp = spline(base, n=8)
        for k in range(4, len(Pp) - 2, 6):
            cv.path([tuple(A_[min(k, len(A_) - 1)]), tuple(B_[min(k, len(B_) - 1)])], S, a * 0.8, 1.6, smooth=False)
        tip = Pp[-1]
        st = [(tip[0], tip[1] - 6), (tip[0] - 30, tip[1] - 30), (tip[0] - 58, tip[1] - 20), (tip[0] - 34, tip[1] + 2), (tip[0], tip[1] + 8)]
        cv.path(st + [st[0]], Wm, a, 2.4, smooth=False); cv.poly(st, G * 0.3, a, layer=cv.F)
        cv.glow((tip[0] - 50, tip[1] - 22), 30, G, 0.9 * a)
    elif e == 'fish':
        for k in range(2):
            q = t * 0.8 + k * math.pi; c = (960 + 175 * math.cos(q), 300 + 95 * math.sin(q)); d = q + math.pi / 2
            body = []
            for s in np.linspace(0, 2 * math.pi, 30):
                body.append((c[0] + 64 * math.cos(s) * math.cos(d) - 28 * math.sin(s) * math.sin(d), c[1] + 64 * math.cos(s) * math.sin(d) + 28 * math.sin(s) * math.cos(d)))
            tail = [(c[0] - 64 * math.cos(d), c[1] - 64 * math.sin(d))]
            tl = [(tail[0][0] - 36 * math.cos(d) - 26 * math.sin(d), tail[0][1] - 36 * math.sin(d) + 26 * math.cos(d)), (tail[0][0] - 36 * math.cos(d) + 26 * math.sin(d), tail[0][1] - 36 * math.sin(d) - 26 * math.cos(d))]
            cv.path(body, S, a, 2.2, smooth=False); cv.path([tl[0], tail[0], tl[1], tl[0]], S, a, 2, smooth=False)
            cv.circle((c[0] + 38 * math.cos(d), c[1] + 38 * math.sin(d)), 4.5, Wm, a, fill=True); cv.poly(body, P.LINE * 0.12, a, layer=cv.F); cv.glow(c, 50, G, 0.5 * a)


# ---------------------------------------------------------------- sign props (held in the left 'offer' hand)
def draw_sign_prop(sc, cv, sign, hand, t, a=1.0, glow=0.3):
    P = sc.P; S, G, Wm = P.SOFT, P.GOLD, P.WARM; hx, hy = hand
    p = sign['prop']
    if p == 'scales':
        top = (hx, hy - 30); cv.path([(hx, hy), top], Wm, a, 2.2, smooth=False)
        tilt = 0.12 * math.sin(t * 1.5)
        L, R = (hx - 110, top[1] + 110 * tilt), (hx + 110, top[1] - 110 * tilt)
        cv.path([L, R], Wm, a, 2.6, smooth=False); cv.circle(top, 7, G, a, fill=True)
        for e in (L, R):
            pan_y = e[1] + 90
            cv.path([e, (e[0] - 40, pan_y)], S, a * 0.8, 1.4, smooth=False); cv.path([e, (e[0] + 40, pan_y)], S, a * 0.8, 1.4, smooth=False)
            cv.path([(e[0] - 46, pan_y), (e[0] - 30, pan_y + 18), (e[0] + 30, pan_y + 18), (e[0] + 46, pan_y)], G, a, 2.2, smooth=False)
        cv.glow(top, 40, G, (0.4 + glow) * a)
    elif p == 'bow':
        top, bot = (hx + 10, hy - 200), (hx + 10, hy + 200)
        arc_ = [(hx + 10 - 80 * math.sin(s * math.pi), lerp(top[1], bot[1], s)) for s in np.linspace(0, 1, 40)]
        cv.path(arc_, G, a, 3, smooth=False); cv.path([top, bot], S, a * 0.8, 1.4, smooth=False)
        cv.path([(hx + 10, hy), (hx - 200, hy)], Wm, a, 2.2, smooth=False)
        cv.path([(hx - 200, hy), (hx - 180, hy - 12), (hx - 180, hy + 12), (hx - 200, hy)], Wm, a, 2, smooth=False)
        cv.glow((hx - 200, hy), 30, G, (0.5 + glow) * a)
    elif p == 'urn':
        c = (hx - 30, hy - 70); z = 1.6
        body = [(c[0] - 34 * z, c[1] - 30 * z), (c[0] - 48 * z, c[1] + 10 * z), (c[0] - 30 * z, c[1] + 50 * z), (c[0] + 30 * z, c[1] + 50 * z), (c[0] + 48 * z, c[1] + 10 * z), (c[0] + 34 * z, c[1] - 30 * z)]
        cv.path(body, G, a, 2.6); cv.path([(c[0] - 40 * z, c[1] - 34 * z), (c[0] + 40 * z, c[1] - 34 * z)], G, a, 2.4, smooth=False)
        cv.poly(spline(body, n=6), G * 0.12, a, layer=cv.F); cv.glow(c, 60, G, 0.5 * a)
        for k in range(3): cv.path([(c[0] - 40 * z, c[1] + (k - 1) * 14), (c[0] + 40 * z, c[1] + (k - 1) * 14)], G, a * 0.4, 1.2, smooth=False)
        for k in range(3):     # water pouring down to the ground
            pts = [(c[0] - 70 - k * 12 - 40 * s + 10 * math.sin(s * 8 + t * 6 + k), lerp(c[1] - 40, GY, s)) for s in np.linspace(0, 1, 30)]
            cv.path(pts, S, a * (0.9 - k * 0.2), 1.8, smooth=False)
        cv.glow((c[0] - 70, GY - 10), 60, P.LINE, 0.4 * a)
    elif p == 'wheat':
        for k, ang in enumerate((-0.25, 0.0, 0.25)):
            base = np.array([hx, hy + 120.]); d = np.array([math.sin(ang), -math.cos(ang)])
            top = base + d * 330; cv.path([tuple(base), tuple(top)], G, a, 2, smooth=False)
            for j in range(7):
                p_ = base + d * (200 + j * 18)
                for sx in (-1, 1):
                    n = np.array([-d[1], d[0]]) * sx
                    grain = [tuple(p_), tuple(p_ + d * 10 + n * 10), tuple(p_ + d * 20)]
                    cv.path(grain, Wm, a, 1.6, smooth=False)
        cv.glow((hx, hy - 120), 60, G, (0.3 + glow) * a)


# ---------------------------------------------------------------- glyph + constellation + card
def glyph_mask(ch, size):
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    im = Image.new('L', (size * 2, size * 2), 0); ImageDraw.Draw(im).text((size, size), ch, font=f, fill=255, anchor='mm')
    return np.asarray(im, np.float32) / 255


def draw_constellation(cv, sign, box, P, t, a=1.0, frac=1.0):
    x0, y0, w, h = box
    pts = [(x0 + u * w, y0 + v * h) for u, v in sign['stars']]
    for k, (i, j) in enumerate(sign['lines']):
        cv.path([pts[i], pts[j]], P.LINE, a * 0.75, 1.6, cl(frac * len(sign['lines']) - k), smooth=False)
    for k, p in enumerate(pts):
        tw = 0.75 + 0.25 * math.sin(t * 2 + k)
        cv.circle(p, 4.5 if k == 0 else 3.5, P.WARM, a * tw, fill=True); cv.glow(p, 14, P.GOLD, 0.5 * a * tw)
    return pts


def card(sign, t=12.0):
    """a 1920x1080 hero frame: full figure + emblem + prop, constellation, glyph medallion, names"""
    P = Palette(sign['element']); cam = Cam(1.0, 960, 540); cv = Canvas(cam); tx = Text(P)
    for (x, y, r, ph, sp, gold) in STARS:
        tw = 0.5 + 0.5 * math.sin(t * sp + ph); cv.circle((x, y), r * 0.8, P.LINE, 0.35 * tw, fill=True, layer=cv.F)
    cv.path([(-100, GY), (2020, GY)], P.LINE, 0.7, 1.6, smooth=False); cv.path([(-100, GY), (2020, GY)], P.LINE, 0.22, 6, smooth=False, layer=cv.F)
    for (x, y, h, ph, r) in FLAMES:
        hh = h * (1 + 0.12 * math.sin(t * 7 + ph)); flame(cv, x, y, hh, P.GOLD, 0.9); flame(cv, x, y, hh * 1.6, P.GOLD, 0.22, layer=cv.F)
    # halo
    cv.circle((960, 250), 150, P.GOLD, 0.35, 1.2); cv.glow((960, 300), 260, P.LINE, 0.10)
    # constellation (upper left) + glyph medallion (upper right)
    draw_constellation(cv, sign, (130, 110, 470, 300), P, t)
    mc = (1610, 300)
    cv.circle(mc, 140, P.GOLD, 0.7, 1.6); cv.circle(mc, 152, P.GOLD, 0.25, 1)
    for k in range(36):
        q = k / 36 * 2 * math.pi; r0 = 160 if k % 3 else 156
        cv.path([(mc[0] + r0 * math.cos(q), mc[1] + r0 * math.sin(q)), (mc[0] + 172 * math.cos(q), mc[1] + 172 * math.sin(q))], P.GOLD, 0.5, 1.2, smooth=False)
    # hero(es)
    if sign['emblem'] == 'twins':
        for x, look, flip in ((800, sign['look'], 1), (1120, sign['look2'], -1)):
            sc = hero(sign, look); sub = SubCam(cam, x, 0.92); cv.cam = sub
            aL = lerp_pose(ARM_L['rest'], ARM_L['offer'], 0.0); aR = ARM_R['rest']
            sc.draw_figure(cv, t, 1.0, 1.0, aL, aR, 0.0, 0.15)
            cv.cam = cam
        # the twins share one star between them
        cv.glow((960, 470), 40, P.WARM, 0.9); cv.circle((960, 470), 6, P.WARM, 1, fill=True)
        cv.path([(905, 482), (960, 470), (1015, 482)], P.GOLD, 0.8, 1.6, smooth=False)
    else:
        sc = hero(sign)
        custom = sign['prop'] in ('scales', 'bow', 'urn', 'wheat')
        aL = ARM_L['offer'] if custom else ARM_L['rest']; aR = ARM_R['rest']
        if sign['emblem'] == 'tail': draw_emblem(sc, cv, sign, t)
        sc.draw_figure(cv, t, 1.0, 1.0, aL, aR, 0.0, 0.15)
        if sign['emblem'] not in ('tail', 'none'): draw_emblem(sc, cv, sign, t)
        if custom: draw_sign_prop(sc, cv, sign, aL[-1], t)
        elif sign['prop'] != 'none':
            grip = (960, 578) if sign['prop'] == 'sword' else (960, 540)
            sc.draw_prop(cv, grip, math.pi / 2, 1.0, 0.4, t)
    # text
    tx.chars(sign['cn'], 360, 640, F(SERIF_BL, 120), P.WHITE, t, 0, 99, stagger=0)
    tx.chars(f"{sign['en']}   {sign['dates']}", 360, 712, F(SERIF_B, 40), (225, 235, 230), t, 0, 99, stagger=0)
    tx.chars(f"{ELEMENT_CN[sign['element']]} · {ELEMENT_EN[sign['element']]}", 360, 770, F(SANS_M, 30), P.TAG, t, 0, 99, stagger=0)
    img = cv.composite(P.BG) * P.VIG
    gm = glyph_mask(sign['glyph'], 170); h, w = gm.shape
    gl = gm[..., None] * np.array(P.GOLD, np.float32) * 1.1
    y0, x0 = mc[1] - h // 2 + 8, mc[0] - w // 2
    img[y0:y0 + h, x0:x0 + w] += gl + cv2.GaussianBlur(gl, (0, 0), 10) * 0.8
    img = tx.blend(img)
    return np.clip(img * 255, 0, 255).astype(np.uint8)
