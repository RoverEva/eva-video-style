#!/usr/bin/env python3
"""3:4 cover posters: 「X座 / 内心世界」 + glowing golden line-art of the sign + 「洞悉」.

  python3 template/longform/zodiac_cover.py --out out/covers [--only taurus]
"""
import argparse, math, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import splprep, splev

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cover_art import CREATURES

W, H = 1536, 2048
SERIF_BL = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'
SERIF_B = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
SYM = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GOLD = np.array([0.36, 0.72, 1.0], np.float32)        # BGR
CREAM = np.array([0.80, 0.94, 1.0], np.float32)
AMBER = np.array([0.10, 0.45, 0.95], np.float32)

SIGNS = [('aries', '白羊座', '♈'), ('taurus', '金牛座', '♉'), ('gemini', '双子座', '♊'), ('cancer', '巨蟹座', '♋'),
         ('leo', '狮子座', '♌'), ('virgo', '处女座', '♍'), ('libra', '天秤座', '♎'), ('scorpio', '天蝎座', '♏'),
         ('sagittarius', '射手座', '♐'), ('capricorn', '摩羯座', '♑'), ('aquarius', '水瓶座', '♒'), ('pisces', '双鱼座', '♓')]
CONST = {  # left-side constellation, unit box
    'aries': [(0, .5), (.45, .2), (.8, .3), (1, .55)], 'taurus': [(0, .2), (.3, .0), (.55, .1), (.75, .35), (1, .4)],
    'gemini': [(0, .1), (.3, .3), (.6, .5), (1, .6)], 'cancer': [(0, .2), (.45, .45), (1, .3)], 'leo': [(0, .4), (.25, .1), (.5, .0), (.7, .3), (1, .45)],
    'virgo': [(0, .2), (.3, .4), (.6, .35), (1, .6)], 'libra': [(0, .5), (.4, .1), (.8, .2), (1, .6)], 'scorpio': [(0, .1), (.3, .3), (.55, .55), (.8, .6), (1, .4)],
    'sagittarius': [(0, .5), (.3, .2), (.6, .3), (1, .1)], 'capricorn': [(0, .1), (.4, .6), (.8, .55), (1, .2)],
    'aquarius': [(0, .2), (.25, .4), (.5, .3), (.75, .55), (1, .45)], 'pisces': [(0, .6), (.35, .45), (.7, .3), (1, .05)],
}


def smooth(pts, closed=False, n=None):
    pts = np.asarray(pts, float)
    if len(pts) < 3: return pts
    k = 3 if len(pts) > 3 else 2
    try:
        if closed: pts = np.vstack([pts, pts[:1]])
        tck, _ = splprep([pts[:, 0], pts[:, 1]], s=0, k=k, per=1 if closed else 0)
        u = np.linspace(0, 1, n or max(40, len(pts) * 14))
        x, y = splev(u, tck); return np.stack([x, y], 1)
    except Exception:
        return pts


class Art:
    """two float layers: crisp lines L and translucent fill F, both single channel intensity"""
    def __init__(s):
        s.L = np.zeros((H, W), np.float32); s.F = np.zeros((H, W), np.float32); s.S = np.zeros((H, W), np.float32)

    def line(s, pts, w=3.0, a=1.0, closed=False, sm=True, layer=None):
        P = smooth(pts, closed) if sm else np.asarray(pts, float)
        tgt = s.L if layer is None else layer
        tmp = np.zeros_like(tgt)
        cv2.polylines(tmp, [np.round(P * 4).astype(np.int32)], closed, a, max(1, int(round(w * 2.2))), cv2.LINE_AA, shift=2)
        np.maximum(tgt, tmp, out=tgt)

    def fill(s, pts, a=0.25, sm=True):
        P = smooth(pts, True) if sm else np.asarray(pts, float)
        tmp = np.zeros_like(s.F); cv2.fillPoly(tmp, [np.round(P * 4).astype(np.int32)], a, cv2.LINE_AA, shift=2)
        np.maximum(s.F, tmp, out=s.F)

    def star(s, c, r, a=1.0):
        x, y = c
        for ang, L in ((0, 1), (math.pi / 2, 1), (math.pi / 4, 0.45), (-math.pi / 4, 0.45)):
            dx, dy = math.cos(ang) * r * L, math.sin(ang) * r * L
            s.line([(x - dx, y - dy), (x, y), (x + dx, y + dy)], 1.6, a, sm=False, layer=s.S)
        cv2.circle(s.S, (int(x), int(y)), max(2, int(r * 0.08)), a, -1, cv2.LINE_AA)

    def dot(s, c, r, a=1.0, layer=None):
        cv2.circle(s.L if layer is None else layer, (int(c[0]), int(c[1])), max(1, int(r)), a, -1, cv2.LINE_AA)


def text_layer(txt, font, size, cx, cy, spacing=0):
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img); f = ImageFont.truetype(font, size)
    widths = [f.getlength(ch) for ch in txt]; tw = sum(widths) + spacing * (len(txt) - 1); x = cx - tw / 2
    for ch, w_ in zip(txt, widths):
        d.text((x, cy), ch, font=f, fill=255, anchor='lm'); x += w_ + spacing
    return np.asarray(img, np.float32) / 255


def background(seed):
    rr = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = np.array([0.02, 0.035, 0.07], np.float32)
    glow = np.exp(-(((xx - W / 2) / (W * 0.55)) ** 2 + ((yy - H * 0.6) / (H * 0.45)) ** 2))
    base += glow[..., None] * np.array([0.03, 0.07, 0.14], np.float32)
    dust = np.zeros((H, W), np.float32)
    n = 2600
    xs, ys = rr.integers(0, W, n), rr.integers(0, H, n); v = rr.uniform(0.1, 0.7, n) ** 2
    dust[ys, xs] = v
    dust = cv2.GaussianBlur(dust, (0, 0), 0.8) * 3
    base += dust[..., None] * np.array([0.5, 0.75, 1.0], np.float32)
    return base


def compose(art, title, glyph, key):
    img = background(hash(key) % 1000)
    # creature/ornament glow
    L, F, S = art.L, art.F, art.S
    glow = cv2.GaussianBlur(L, (0, 0), 3) * 0.8 + cv2.GaussianBlur(L, (0, 0), 12) * 0.55 + cv2.GaussianBlur(L, (0, 0), 44) * 0.45
    fglow = cv2.GaussianBlur(F, (0, 0), 3)
    img += fglow[..., None] * AMBER * 0.55
    img += glow[..., None] * GOLD
    img += L[..., None] * CREAM * 1.1
    sg = cv2.GaussianBlur(S, (0, 0), 3) * 1.2 + cv2.GaussianBlur(S, (0, 0), 16) * 0.8
    img += sg[..., None] * GOLD + S[..., None] * CREAM
    # text: cream→gold vertical gradient with a warm glow
    def put(mask, top, bot, glow_a=0.9):
        ys = np.where(mask.max(1) > 0)[0]
        if len(ys) == 0: return
        y0, y1 = ys.min(), ys.max(); g = np.clip((np.arange(H) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
        col = CREAM * (1 - g) + GOLD * g
        nonlocal_img = img
        nonlocal_img += (cv2.GaussianBlur(mask, (0, 0), 10) * 0.55 + cv2.GaussianBlur(mask, (0, 0), 36) * 0.35)[..., None] * GOLD * glow_a
        nonlocal_img *= (1 - mask[..., None] * 0.95)
        nonlocal_img += mask[..., None] * col * 1.05
    put(text_layer(title, SERIF_BL, 215, W / 2, 330, 18), 0, 0)
    put(text_layer('内心世界', SERIF_BL, 215, W / 2, 575, 18), 0, 0)
    put(text_layer('洞悉', SERIF_BL, 150, W / 2, 1880, 30), 0, 0, 0.8)
    put(text_layer(glyph, SYM, 120, W / 2, 790), 0, 0, 1.2)
    out = np.clip(img, 0, 1)
    out = out ** 0.95
    return (out * 255).astype(np.uint8)


def ornaments(art, key):
    # top crescent + dots
    c = (W / 2, 70)
    q = np.linspace(math.pi * 0.15, math.pi * 1.85, 40)
    outer = [(c[0] + 34 * math.cos(t + math.pi / 2), c[1] + 34 * math.sin(t + math.pi / 2)) for t in q]
    art.line(outer, 4, 1.0, sm=False)
    for k, (dx, r) in enumerate(((-150, 5), (-95, 8), (95, 8), (150, 5))): art.dot((c[0] + dx, c[1]), r, 0.9)
    for dx in (-210, 210): art.dot((c[0] + dx, c[1]), 3, 0.7)
    # big faint arc around the title
    arc = [(W / 2 + 760 * math.cos(t), 760 + 700 * math.sin(t)) for t in np.linspace(math.pi * 1.06, math.pi * 1.94, 120)]
    art.line(arc, 1.6, 0.45, sm=False)
    # constellation left
    pts = CONST[key]; ox, oy, sw, shh = 70, 830, 330, 150
    P = [(ox + x * sw, oy + y * shh) for x, y in pts]
    art.line(P, 1.8, 0.55, sm=False)
    for p in P: art.star(p, 26, 1.0)
    # right orbit + bright star
    orb = [(1360 + 120 * math.cos(t), 980 + 260 * math.sin(t)) for t in np.linspace(-math.pi * 0.55, math.pi * 0.35, 60)]
    art.line(orb, 1.6, 0.55, sm=False); art.star((1370, 990), 46, 1.0)
    for p in ((1440, 640), (1300, 1500), (180, 1350), (1460, 1250)): art.star(p, 18, 0.8)
    # mandorla with beads
    cx, cy, rx, ry = W / 2, 1240, 470, 500
    ell = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in np.linspace(math.pi * 1.0, math.pi * 3.0, 220)]
    art.line(ell, 2.2, 0.75, sm=False)
    for t in np.linspace(math.pi, 3 * math.pi, 23)[:-1]:
        art.dot((cx + rx * math.cos(t), cy + ry * math.sin(t)), 6, 0.9)
    # orbit rings crossing the creature
    for a_, b_, rot, alpha in ((560, 120, -0.18, 0.5), (620, 90, 0.12, 0.35)):
        ring = [(cx + a_ * math.cos(t) * math.cos(rot) - b_ * math.sin(t) * math.sin(rot), cy + 40 + a_ * math.cos(t) * math.sin(rot) + b_ * math.sin(t) * math.cos(rot)) for t in np.linspace(0, 2 * math.pi, 200)]
        art.line(ring, 1.6, alpha, sm=False)
    # platform: concentric ellipses, horizon, falling droplets
    py = 1700
    for k, (a_, b_, al) in enumerate(((380, 40, 0.9), (300, 30, 0.6), (200, 20, 0.5), (110, 11, 0.6))):
        art.line([(cx + a_ * math.cos(t), py + b_ * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 160)], 2.2 if k == 0 else 1.4, al, sm=False)
    art.line([(0, py), (W, py)], 2.0, 0.8, sm=False)
    rr = np.random.default_rng(7)
    for i in range(70):
        x = 20 + i * (W - 40) / 69 + rr.uniform(-6, 6); d = abs(x - cx) / (W / 2)
        L_ = (1 - d) * 70 + 10; y0 = py + 14 + rr.uniform(0, 1) * 40 * (1 - d)
        if rr.random() < 0.7:
            y = y0 + rr.uniform(0, L_)
            drop = [(x, y - 9), (x + 4.5, y + 2), (x, y + 6), (x - 4.5, y + 2)]
            tmp = np.round(smooth(drop, True) * 4).astype(np.int32); cv2.fillPoly(art.L, [tmp], 0.5 + 0.5 * (1 - d), cv2.LINE_AA, shift=2)
        art.line([(x, py + 4), (x, y0)], 1.0, 0.25 * (1 - d), sm=False)
    # bottom flourish around 洞悉
    for sd in (-1, 1):
        x0 = cx + sd * 200; x1 = cx + sd * 640
        art.line([(x0, 1880), (x1, 1880)], 1.6, 0.6, sm=False)
        art.star((cx + sd * 260, 1880), 34, 1.0)
        art.dot((x1, 1880), 4, 0.8)


def render(key, title, glyph):
    art = Art(); ornaments(art, key)
    CREATURES[key](art, W / 2, 1300)
    return compose(art, title, glyph, key)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--only')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    for i, (key, title, glyph) in enumerate(SIGNS):
        if a.only and key not in a.only.split(','): continue
        img = render(key, title, glyph)
        p = os.path.join(a.out, f'{i + 1:02d}_{title}_内心世界_洞悉.png'); cv2.imwrite(p, img); print(p, flush=True)
