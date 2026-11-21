"""Drawing core for the MBTI template: canvas with crisp + glow layers, splines, flames, text, palettes."""
import math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, GY = 1920, 1080, 920          # frame size and ground line


# ---------------------------------------------------------------- math
def cl(x, a=0., b=1.): return max(a, min(b, x))
def ramp(t, a, b): return cl((t - a) / (b - a)) if b > a else float(t >= a)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def pulse(t, t0, d=0.3):
    """instant hit at t0 that decays over ~d seconds"""
    return 0. if t < t0 else math.exp(-(t - t0) / d * 3)
def pop(t, t0, d=0.15):
    """0 before t0, then overshoots (1.6x) and settles to 1 — used for candles, people, flags"""
    if t < t0: return 0.
    k = cl((t - t0) / d)
    return 1 + 0.6 * math.sin(k * math.pi) * (1 - k) if k < 1 else 1.


def spline(pts, n=12, closed=False):
    P = np.array(pts, float)
    if len(P) < 3: return P
    P = np.vstack([P[-1], P, P[0], P[1]]) if closed else np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return np.array(out)


def mir(pts): return [(W - x, y) for x, y in pts]


def offset_line(pts, d0, d1):
    P = spline(pts, n=8); A, B = [], []
    for i in range(len(P)):
        t = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
        n = np.array([-t[1], t[0]]) / (np.linalg.norm(t) + 1e-6)
        d = lerp(d0, d1, i / (len(P) - 1)); A.append(P[i] + n * d); B.append(P[i] - n * d)
    return A, B


# ---------------------------------------------------------------- palettes (BGR floats)
PALETTES = {
    # Diplomats NF — emerald + gold (the reference look)
    'emerald': dict(line=(0.55, 1.00, 0.42), soft=(0.80, 1.00, 0.78), gold=(0.38, 0.84, 1.00), warm=(0.70, 0.95, 1.00),
                    dim=(0.35, 0.55, 0.30), bg=(0.035, 0.05, 0.025), bg_c=(0.05, 0.075, 0.035),
                    hi_rgb=(255, 214, 120), tag_rgb=(150, 235, 190)),
    # Analysts NT — violet + gold
    'violet': dict(line=(1.00, 0.55, 0.78), soft=(1.00, 0.82, 0.92), gold=(0.45, 0.80, 1.00), warm=(0.80, 0.92, 1.00),
                   dim=(0.55, 0.30, 0.42), bg=(0.05, 0.025, 0.04), bg_c=(0.08, 0.035, 0.055),
                   hi_rgb=(255, 205, 130), tag_rgb=(205, 170, 255)),
    # Sentinels SJ — azure + pale gold
    'azure': dict(line=(1.00, 0.78, 0.38), soft=(1.00, 0.92, 0.78), gold=(0.50, 0.86, 1.00), warm=(0.82, 0.96, 1.00),
                  dim=(0.55, 0.40, 0.22), bg=(0.055, 0.035, 0.015), bg_c=(0.085, 0.055, 0.025),
                  hi_rgb=(255, 220, 140), tag_rgb=(150, 205, 255)),
    # Explorers SP — amber + white gold
    'amber': dict(line=(0.35, 0.82, 1.00), soft=(0.70, 0.95, 1.00), gold=(0.55, 0.92, 1.00), warm=(0.85, 0.98, 1.00),
                  dim=(0.20, 0.40, 0.55), bg=(0.015, 0.035, 0.055), bg_c=(0.025, 0.055, 0.085),
                  hi_rgb=(255, 236, 170), tag_rgb=(255, 200, 120)),
}
GROUP_PALETTE = {'NF': 'emerald', 'NT': 'violet', 'SJ': 'azure', 'SP': 'amber'}


class Palette:
    def __init__(self, name):
        p = PALETTES[name]; self.name = name
        self.LINE = np.array(p['line']); self.SOFT = np.array(p['soft']); self.GOLD = np.array(p['gold'])
        self.WARM = np.array(p['warm']); self.DIM = np.array(p['dim'])
        self.HI = p['hi_rgb']; self.TAG = p['tag_rgb']; self.WHITE = (238, 248, 238)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.rad = np.exp(-(((xx - 960) / 900) ** 2 + ((yy - 560) / 620) ** 2))
        bg, bc = np.array(p['bg'], np.float32), np.array(p['bg_c'], np.float32)
        self.BG = (bg[None, None, :] + bc[None, None, :] * self.rad[..., None]).astype(np.float32)
        self.BG += (np.clip((yy - 930) / 150, 0, 1) * -0.03)[..., None]
        self.VIG = (0.55 + 0.45 * self.rad ** 0.35)[..., None].astype(np.float32)


# ---------------------------------------------------------------- canvas
class Cam:
    def __init__(s, sc=1., cx=960, cy=540): s.s, s.cx, s.cy = sc, cx, cy
    def __call__(s, P): return (np.asarray(P, float) - [s.cx, s.cy]) * s.s + [960, 540]


class Canvas:
    """L = crisp anti-aliased lines; F = soft light that only shows through the glow passes."""
    def __init__(s, cam):
        s.cam = cam
        s.L = np.zeros((H, W, 3), np.float32); s.F = np.zeros((H, W, 3), np.float32)

    def _q(s, P): return np.round(s.cam(P) * 4).astype(np.int32)

    def path(s, pts, col, a=1., th=2., frac=1., smooth=True, closed=False, layer=None):
        if a <= 0.003 or frac <= 0: return
        P = spline(pts, closed=closed) if smooth and len(pts) > 2 else np.array(pts, float)
        if frac < 1:
            seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
            L = cum[-1] * frac; k = int(np.searchsorted(cum, L))
            if k <= 0: return
            k = min(k, len(P) - 1); r = (L - cum[k - 1]) / max(seg[k - 1], 1e-6)
            P = np.vstack([P[:k], P[k - 1] + (P[k] - P[k - 1]) * r])
        cv2.polylines(layer if layer is not None else s.L, [s._q(P)], False, tuple(float(c) * a for c in col),
                      max(1, int(round(th * s.cam.s))), cv2.LINE_AA, shift=2)

    def poly(s, pts, col, a=1., layer=None):
        if a <= 0.003: return
        cv2.fillPoly(layer if layer is not None else s.L, [s._q(np.array(pts, float))],
                     tuple(float(c) * a for c in col), cv2.LINE_AA, shift=2)

    def circle(s, c, r, col, a=1., th=2., fill=False, layer=None):
        if a <= 0.003: return
        q = s.cam([c])[0]
        cv2.circle(layer if layer is not None else s.L, (int(q[0] * 4), int(q[1] * 4)), max(1, int(r * s.cam.s * 4)),
                   tuple(float(x) * a for x in col), -1 if fill else max(1, int(th * s.cam.s)), cv2.LINE_AA, shift=2)

    def glow(s, c, r, col, a=1.):
        if a <= 0.003: return
        q = s.cam([c])[0]; R = r * s.cam.s
        x0, x1 = int(max(0, q[0] - 3 * R)), int(min(W, q[0] + 3 * R))
        y0, y1 = int(max(0, q[1] - 3 * R)), int(min(H, q[1] + 3 * R))
        if x1 <= x0 or y1 <= y0: return
        yy, xx = np.mgrid[y0:y1, x0:x1]
        s.F[y0:y1, x0:x1] += (np.exp(-((xx - q[0]) ** 2 + (yy - q[1]) ** 2) / (R * R))[..., None] * col * a).astype(np.float32)

    def composite(s, BG, flash=0.0, flash_col=(0.6, 0.9, 1.0)):
        L, Fl = s.L, s.F
        g1 = cv2.GaussianBlur(L, (0, 0), 3.5)
        small = cv2.resize(L + Fl, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        g2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H))
        g3 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 22), (W, H))
        img = BG + L * 0.95 + g1 * 1.3 + g2 * 1.6 + g3 * 1.1 + cv2.GaussianBlur(Fl, (0, 0), 2) * 0.6
        if flash > 0: img = img + flash * np.array(flash_col, np.float32)
        return 1 - np.exp(-img * 1.15)     # soft tonemap


def flame(cv, x, y, h, col, a, layer=None, lean=0.):
    w = h * 0.36
    pts = [(x + lean * h, y - h), (x + w * 0.55, y - h * 0.45), (x + w * 0.5, y - h * 0.15), (x, y),
           (x - w * 0.5, y - h * 0.15), (x - w * 0.55, y - h * 0.45)]
    cv.poly(spline(pts, n=6, closed=True), col, a, layer=layer)


# ---------------------------------------------------------------- fonts / text
def _font_file(pattern, fallback):
    try:
        f = subprocess.run(['fc-match', '-f', '%{file}', pattern], capture_output=True, text=True, timeout=5).stdout.strip()
        if f: return f
    except Exception: pass
    return fallback

SERIF_B = _font_file('Noto Serif CJK SC:style=Bold', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc')
SERIF_BL = _font_file('Noto Serif CJK SC:style=Black', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc')
SANS_M = _font_file('Noto Sans CJK SC:style=Medium', '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc')
_fc = {}
def F(path, size):
    if (path, size) in _fc: return _fc[(path, size)]
    f = None
    for i in range(10):
        try:
            g = ImageFont.truetype(path, size, index=i)
            if 'SC' in g.getname()[0]: f = g; break
        except Exception: break
    _fc[(path, size)] = f or ImageFont.truetype(path, size)
    return _fc[(path, size)]


class Text:
    def __init__(s, P):
        s.P = P; s.img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.img)

    def chars(s, txt, x, y, f, col, t, t0, t1=99, gold=(), anchor='c', spacing=0, stagger=0.035, hicol=None):
        """per-character reveal: fade + 14 px rise, staggered; exits with a 0.25 s fade"""
        if t < t0 or t > t1 + 0.25: return
        ws = [f.getlength(ch) + spacing for ch in txt]; tw = sum(ws) - spacing
        cx = x - tw / 2 if anchor == 'c' else (x if anchor == 'l' else x - tw)
        out = 1 - ramp(t, t1, t1 + 0.25)
        for i, ch in enumerate(txt):
            k = eo(ramp(t, t0 + i * stagger, t0 + i * stagger + 0.22))
            if k > 0:
                c = (hicol or s.P.HI) if i in gold else col
                s.d.text((cx, y + (1 - k) * 14), ch, font=f, fill=tuple(c) + (int(255 * k * out),), anchor='ls')
            cx += ws[i]

    def tag(s, letter, word, x, y, t, t0, t1):
        if t < t0 or t > t1 + 0.25: return
        k = eo(ramp(t, t0, t0 + 0.25)) * (1 - ramp(t, t1, t1 + 0.25)); al = int(255 * k)
        f = F(SANS_M, 18); w = f.getlength(word) + 34; x0 = x - w / 2
        hr, hg, hb = s.P.HI
        s.d.rounded_rectangle([x0, y - 20, x0 + 24, y + 4], 4, fill=(hr, int(hg * 0.85), int(hb * 0.6), al))
        s.d.text((x0 + 12, y - 1), letter, font=f, fill=(20, 30, 20, al), anchor='ms')
        s.d.text((x0 + 32, y - 1), word, font=f, fill=tuple(s.P.TAG) + (al,), anchor='ls')

    def blend(s, img):
        ta = np.asarray(s.img, np.float32) / 255.0
        if ta[..., 3].max() <= 0: return img
        rgb = ta[..., [2, 1, 0]]; al = ta[..., 3:4]
        return img * (1 - al) + rgb * al + cv2.GaussianBlur(rgb * al, (0, 0), 6) * 0.35


def gold_idx(line, word):
    """indices of `word` inside `line` (for gold highlighting)"""
    if not word: return ()
    i = line.find(word)
    return tuple(range(i, i + len(word))) if i >= 0 else ()
