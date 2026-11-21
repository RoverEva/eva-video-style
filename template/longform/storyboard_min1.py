#!/usr/bin/env python3
"""白羊座 · 第一分钟分镜 —— 24 frames, one per beat of the copy, each with a meaningful action.

  python3 template/longform/storyboard_min1.py --out out/long/v4/storyboard
"""
import argparse, math, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))
from engine.core import W, H, Palette, flame, Text, F, SERIF_B, SERIF_BL, SANS_M
import zodiac_signs  # noqa
from vis import heart_pts
from aries_char import draw_aries, POSE
from story_frames import (Shot, starfield, milkyway, meteor, godrays, flare, dust, glint, skyline, lamp, rain, sp, solid,
                          figure, BLACK)

PF, PV = Palette('fire'), Palette('violet')
E8 = 60 / 112.9117 / 2


def pose(name, **kw): p = dict(POSE[name]); p.update(kw); return p


def caption(tx, lines, x, y, size=64, gold=(), col=None):
    for k, l in enumerate(lines):
        g = gold[k] if k < len(gold) else ()
        g = tuple(range(len(l))) if g == 'all' else g
        tx.chars(l, x, y + k * int(size * 1.4), F(SERIF_BL if size >= 90 else SERIF_B, size), col or PF.WHITE, 1, 0, 99, gold=g, stagger=0)


def heart(cv, c, s, P, a=1.0, glow=1.0):
    hp = [(c[0] + s * u, c[1] + s * v) for u, v in heart_pts(0, 0, 1.0, 60)]
    cv.poly(hp, BLACK, 1.0); cv.poly(hp, P.WARM * 0.45, a); cv.path(hp + [hp[0]], P.WARM, a, 3.0, smooth=False)
    cv.glow(c, s * 1.6, P.GOLD, 0.7 * a * glow)
    return hp


def flame_big(cv, c, h, P, a=1.0, seed=0):
    rr = np.random.default_rng(seed); base = c[1] + 0.42 * h
    for k, (scl, col, th) in enumerate(((1.0, P.GOLD, 2.6), (0.78, P.WARM, 2.0), (1.22, P.GOLD, 1.3), (0.52, P.WARM, 1.4))):
        w = h * scl * 0.36; hh = h * scl; wob = rr.uniform(-0.05, 0.05)
        pts = [(c[0] + (0.04 + wob) * hh, base - hh), (c[0] + w * 0.55, base - hh * 0.45), (c[0] + w * 0.5, base - hh * 0.15), (c[0], base),
               (c[0] - w * 0.5, base - hh * 0.15), (c[0] - w * 0.55, base - hh * 0.45)]
        cv.path(sp(pts, 10, True), col, a * (0.95 - 0.18 * k), th, smooth=False)
    flame(cv, c[0], base, h * 0.9, P.GOLD, 0.5 * a); flame(cv, c[0], base, h * 1.3, P.GOLD, 0.2 * a, layer=cv.F)


def sparks(cv, c, n, r0, r1, P, a=1.0, seed=1, ang=(0, 2 * math.pi), streak=1.0):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        q = rr.uniform(*ang); d0 = rr.uniform(r0, r1); L = rr.uniform(10, 40) * streak
        p0 = (c[0] + d0 * math.cos(q), c[1] + d0 * math.sin(q)); p1 = (p0[0] + L * math.cos(q), p0[1] + L * math.sin(q))
        cv.path([p0, p1], P.WARM if rr.random() < 0.6 else P.GOLD, a * rr.uniform(0.5, 1), rr.uniform(1.2, 2.6), smooth=False)
    for _ in range(max(2, n // 12)): glint(cv, (c[0] + rr.uniform(-r1, r1), c[1] + rr.uniform(-r1, r1) * 0.7), rr.uniform(10, 22), P.WARM, a)


def ground(cv, y, P, a=0.6, x0=0, x1=W): cv.path([(x0, y), (x1, y)], P.LINE, a, 1.6, smooth=False)


def speedlines(cv, P, y0, y1, n=40, dirx=-1, a=0.5, seed=3):
    rr = np.random.default_rng(seed)
    for _ in range(n):
        y = rr.uniform(y0, y1); x = rr.uniform(-100, W); L = rr.uniform(120, 420)
        cv.path([(x, y), (x + dirx * L, y)], P.LINE, a * rr.uniform(0.3, 1), rr.uniform(0.8, 1.8), smooth=False)


def mini(cv, x, gy, h, P, a=0.6, pose_='stand', d=1):
    figure(cv, x, gy, h, pose_, P.LINE * 0.9, a, d=d, heart=None, P=P, th=1.6)


def qmark(tx, x, y, s=54, a=1.0): tx.chars('?', x, y, F(SERIF_B, s), (200, 200, 200), 1, 0, 99, stagger=0)


def cal_page(cv, tx, c, w, h, txt, P, a=1.0, rot=0.0, burn=0.0):
    cs, sn = math.cos(rot), math.sin(rot)
    R = lambda x, y: (c[0] + x * cs - y * sn, c[1] + x * sn + y * cs)
    box = [R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2 - h * 0.6 * burn), R(-w / 2, h / 2)]
    cv.poly(box, BLACK, 1.0); cv.poly(box, P.SOFT * 0.05, a); cv.path(box + [box[0]], P.SOFT, a, 2.4, smooth=False)
    cv.path([R(-w / 2, -h / 2 + h * 0.22), R(w / 2, -h / 2 + h * 0.22)], P.WARM, a, 2, smooth=False)
    for k in (-0.3, 0.3): cv.circle(R(w * k, -h / 2 - 6), 8, P.LINE, a, 2)
    tx.chars(txt, c[0], c[1] + h * 0.12, F(SERIF_BL, int(h * 0.3)), (235, 230, 220), 1, 0, 99, stagger=0)
    if burn > 0:
        e0, e1 = R(w / 2, h / 2 - h * 0.6 * burn), R(-w / 2, h / 2)
        for u in np.linspace(0, 1, 7): flame(cv, e0[0] + (e1[0] - e0[0]) * u, e0[1] + (e1[1] - e0[1]) * u, 40 + 30 * (u * 7 % 1), P.GOLD, 0.8)
        sparks(cv, ((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2), 40, 20, 200, P, 0.9, 5, (-math.pi, 0))


def wall(cv, x, y_top, y_bot, w, P, a=1.0, crack=0.0, seed=2):
    pts = [(x - w / 2, y_bot), (x - w / 2, y_top), (x + w / 2, y_top), (x + w / 2, y_bot)]
    cv.poly(pts, BLACK, 1.0); cv.poly(pts, P.LINE * 0.06, a); cv.path(pts, P.LINE, a, 2.4, smooth=False)
    for yy in np.arange(y_top + 50, y_bot, 50):
        cv.path([(x - w / 2, yy), (x + w / 2, yy)], P.LINE, 0.35 * a, 1.2, smooth=False)
        off = 0 if int((yy - y_top) / 50) % 2 else 45
        for xx in np.arange(x - w / 2 + off, x + w / 2, 90): cv.path([(xx, yy - 50), (xx, yy)], P.LINE, 0.3 * a, 1.1, smooth=False)
    if crack > 0:
        rr = np.random.default_rng(seed); c0 = (x - w / 2, (y_top + y_bot) * 0.48)
        for b in range(5):
            p = np.array(c0, float); seg = [tuple(p)]; ang = rr.uniform(-0.8, 0.8)
            for _ in range(int(6 * crack) + 1):
                ang += rr.uniform(-0.5, 0.5); p = p + np.array([math.cos(ang), math.sin(ang)]) * rr.uniform(40, 80); seg.append(tuple(p))
            cv.path(seg, P.WARM, a, 3, smooth=False); cv.path(seg, P.GOLD, 0.6 * a, 10, smooth=False, layer=cv.F)


def bolt(cv, p0, p1, P, a=1.0, seed=7, col=None):
    rr = np.random.default_rng(seed); col = P.HI if col is None else col
    pts = [p0]; n = 9
    for k in range(1, n):
        u = k / n; pts.append((p0[0] + (p1[0] - p0[0]) * u + rr.uniform(-40, 40), p0[1] + (p1[1] - p0[1]) * u + rr.uniform(-20, 20)))
    pts.append(p1)
    cv.path(pts, col, a, 4, smooth=False); cv.path(pts, col, 0.35 * a, 8, smooth=False, layer=cv.F)
    for k in (3, 6):
        q = pts[k]; cv.path([q, (q[0] + rr.uniform(-120, 120), q[1] + rr.uniform(40, 120))], col, 0.6 * a, 2, smooth=False)


def armor_burst(cv, c, P, a=1.0, n=10, r=260):
    for k in range(n):
        q = k / n * 2 * math.pi; p = (c[0] + r * math.cos(q), c[1] + r * 0.8 * math.sin(q))
        pl = [(p[0] + 26 * math.cos(q + s), p[1] + 18 * math.sin(q + s)) for s in (0, 1.8, 3.2, 4.6)]
        cv.path(pl + [pl[0]], P.GOLD, a, 2, smooth=False)
        cv.path([p, (c[0] + (r - 90) * math.cos(q), c[1] + (r - 90) * 0.8 * math.sin(q))], P.GOLD, 0.35 * a, 1.2, smooth=False)


# ================================================================ the 24 frames
# (time s, copy lines, gold, action, camera, sfx, draw)
FRAMES = []


def frame(t, copy, action, camera, sfx, gold=()):
    def deco(fn): FRAMES.append(dict(t=t, copy=copy, gold=gold, action=action, camera=camera, sfx=sfx, fn=fn)); return fn
    return deco


@frame(0.0, [], '黑场里一粒火星被线条画出来，一闪一闪', '极近景 · 画面正中 · 静止前推', '心跳一声（低频）')
def f01(sh, tx):
    cv = sh.cv; c = (960, 560)
    cv.glow(c, 60, PF.GOLD, 0.9); glint(cv, c, 40, PF.WARM, 1); cv.circle(c, 5, PF.HI, 1, fill=True)
    dust(cv, (700, 380, 1220, 740), 30, PF.WARM, 0.4)


@frame(1.1, ['他的心里'], '火星拉出第一缕火苗，线条从下往上长', '近景 · 缓慢推近', '火柴擦燃')
def f02(sh, tx):
    cv = sh.cv; flame_big(cv, (960, 600), 170, PF, 0.9, 1); sparks(cv, (960, 560), 14, 60, 180, PF, 0.6, 2, (-math.pi, 0))
    caption(tx, ['他的心里'], 960, 230, 72)


@frame(3.0, ['他的心里', '住着一团火'], '火苗卷起来，变成他火焰般竖起的头发；侧脸和羊角在火里被一笔一笔勾出', '特写 · 侧脸 · 火光从下往上打', '火焰呼一声 + 低音铺垫', gold=((), (3, 4)))
def f03(sh, tx):
    cv = sh.cv
    draw_aries(cv, 900, 1080 + 2000 * 0.6, 2000, pose('hero', mouth='flat', brow='calm', wind=(-0.6, 0.1)), P=PF, rim=(1, 0.3), heart=0)
    for k in range(5): flame(cv, 600 + k * 120, 360 - 40 * (k % 2), 160, PF.GOLD, 0.35, layer=cv.F)
    sparks(cv, (900, 260), 30, 120, 420, PF, 0.7, 4, (-math.pi, 0))
    caption(tx, ['他的心里', '住着一团火'], 1500, 760, 64, ((), (3, 4)))


@frame(4.3, ['一碰'], '一只别人的手指从画面左边伸进来，轻轻碰了一下火苗', '近景 · 手入画', '手指轻点（tick）')
def f04(sh, tx):
    cv = sh.cv; flame_big(cv, (1080, 600), 200, PF, 0.85, 3)
    hand = [(0, 520), (560, 540), (720, 552), (860, 566), (880, 586), (720, 590), (560, 610), (0, 640)]
    solid(cv, sp(hand, 4), PF.LINE, 1.0, 2.2, 0.04)
    cv.path(sp([(720, 552), (800, 548), (870, 566)], 4), PF.LINE, 0.6, 1.2)
    for k in range(3): cv.path([(560 - k * 40, 560 + k * 12), (600 - k * 40, 590 + k * 10)], PF.LINE, 0.35, 1.0, smooth=False)
    glint(cv, (880, 580), 30, PF.WARM, 1)
    caption(tx, ['一碰'], 960, 230, 76)


@frame(5.3, ['就燃'], '火焰「轰」地炸开成一圈火环，火星飞满屏，镜头被冲得一抖', '中景 · 冲击 · 镜头震动 + 轻微倾斜', '爆燃 + 低音冲击', gold=('all',))
def f05(sh, tx):
    cv = sh.cv; c = (960, 600); sh.roll = -3
    for k, r_ in enumerate((180, 300, 440)):
        cv.path([(c[0] + r_ * math.cos(q), c[1] + r_ * 0.75 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 90)], PF.GOLD, 1 - 0.25 * k, 3 - k * 0.6, smooth=False)
    flame_big(cv, c, 340, PF, 1.0, 5); sparks(cv, c, 160, 120, 760, PF, 1.0, 6, streak=2.0)
    godrays(cv, c, np.linspace(0, 2 * math.pi, 18), 1100, PF.GOLD, 0.1)
    caption(tx, ['就燃'], 960, 260, 130, ('all',))


@frame(6.4, ['可火的最中间'], '火焰向两边分开，像幕布拉开', '推镜 · 穿进火里', '风声 whoosh')
def f06(sh, tx):
    cv = sh.cv
    for sd in (-1, 1):
        for k in range(6): flame(cv, 960 + sd * (220 + k * 110), 1000, 520 - k * 50, PF.GOLD, 0.32 - k * 0.03)
    cv.glow((960, 600), 220, PF.WARM, 0.5); dust(cv, (700, 300, 1220, 900), 80, PF.WARM, 0.6)
    caption(tx, ['可火的最中间'], 960, 220, 72)


@frame(7.5, ['可火的最中间', '藏着一颗很软很软的心'], '中间是一颗软软的心，一跳一跳；线条是细的、暖的，跟外面的火不一样', '特写 · 心在正中 · 浅景深', '心跳两声 + 柔和钢琴音', gold=((), (4, 5, 6, 7)))
def f07(sh, tx):
    cv = sh.cv
    for sd in (-1, 1):
        for k in range(4): flame(cv, 960 + sd * (420 + k * 130), 1060, 560 - k * 60, PF.GOLD, 0.25)
    heart(cv, (960, 600), 150, PF, 1.0); cv.path([(960 + 190 * math.cos(q), 600 + 170 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 60)], PF.WARM, 0.3, 1.2, smooth=False)
    sh.bokeh_field(16, (0, 0, W, H), 20, 60, (PF.GOLD, PF.WARM), 0.4, 3)
    caption(tx, ['可火的最中间', '藏着一颗很软很软的心'], 960, 180, 64, ((), (4, 5, 6, 7)))


@frame(10.6, ['他从不让人看见'], '一只戴护腕的手从上面合拢，把心挡住；火光从指缝漏出来', '特写 · 光被挡住，画面变暗', '音乐抽空，只剩心跳')
def f08(sh, tx):
    cv = sh.cv; heart(cv, (960, 640), 120, PF, 0.5, 0.5)
    hand = [(560, 380), (1360, 380), (1380, 520), (1300, 600), (620, 600), (540, 520)]
    solid(cv, sp(hand, 4, True), PF.SOFT, 1.0, 2.4, 0.05)
    for k in range(4): cv.path([(700 + k * 170, 400), (700 + k * 170, 590)], PF.SOFT, 0.5, 1.2, smooth=False)
    cv.path([(560, 400), (1360, 400)], PF.GOLD, 1, 3, smooth=False)
    godrays(cv, (960, 600), [math.pi / 2 + q for q in (-0.5, -0.2, 0.2, 0.5)], 600, PF.GOLD, 0.12, 0.02)
    caption(tx, ['他从不让人看见'], 960, 240, 72)


@frame(13.8, ['白羊座的内心世界'], '【音乐炸】心变成他胸口的火焰心——镜头一下拉远：整个白羊少年站在星空下，羊角发光，披风扬起，背后是白羊座星座连线', '匹配剪辑 · 极近 → 全景（大拉）', '鼓点进 + 冲击 + 闪白', gold=('all',))
def f09(sh, tx):
    cv = sh.cv; starfield(cv, PF, 220, 760, 7, 0.8, 8); milkyway(cv, PF, (0, 120), (W, 420), 140, 6, 0.8)
    cons = [(1180, 260), (1330, 210), (1460, 250), (1520, 330)]
    cv.path(cons, PF.GOLD, 0.6, 1.4, smooth=False)
    for q in cons: glint(cv, q, 20, PF.WARM, 1)
    ground(cv, 960, PF, 0.5)
    draw_aries(cv, 620, 960, 640, pose('hero', mouth='smile', brow='calm', wind=(-0.9, -0.2)), P=PF, rim=(-1, -0.3))
    godrays(cv, (620, 560), np.linspace(-math.pi, 0, 12), 900, PF.GOLD, 0.06)
    caption(tx, ['白羊座的内心世界'], 1340, 560, 96, ('all',), PF.HI)


@frame(21.8, ['别人还在犹豫'], '起跑线上一排人，头顶冒问号、原地张望；只有他压低身体蓄力', '低机位全景 · 横向排开', '人群窃窃私语（很轻）')
def f10(sh, tx):
    cv = sh.cv; ground(cv, 900, PF, 0.6)
    cv.path([(150, 905), (1770, 905)], PF.WARM, 0.7, 2, smooth=False)
    for x in range(170, 1770, 60): cv.path([(x, 905), (x + 30, 905)], PF.SOFT, 0.5, 1.2, smooth=False)
    for k, x in enumerate((380, 560, 1060, 1240, 1420)):
        mini(cv, x, 900, 300, PF, 0.55, 'stand', 1 if k % 2 else -1); qmark(tx, x + 20, 560)
    draw_aries(cv, 800, 900, 380, pose('burst', mouth='grit'), P=PF, rim=(1, -0.2))
    caption(tx, ['别人还在犹豫'], 960, 200, 64)


@frame(22.9, ['别人还在犹豫', '他已经冲出去了'], '他像火箭一样蹿出去：脚下炸出尘土和火星，身后拖一道火焰尾迹，别人还在原地', '跟拍 · 低机位 · 速度线', '起跑爆发 whoosh(heavy)', gold=((), (3, 4, 5)))
def f11(sh, tx):
    cv = sh.cv; ground(cv, 920, PF, 0.6); speedlines(cv, PF, 300, 900, 50, -1, 0.5)
    for k, x in enumerate((140, 260, 380)): mini(cv, x, 920, 220, PF, 0.4)
    for k in range(8): flame(cv, 520 + k * 70, 860 - k * 6, 60 + k * 12, PF.GOLD, 0.25 + 0.05 * k, lean=-0.6)
    sparks(cv, (900, 920), 50, 20, 260, PF, 0.9, 8, (-math.pi, -math.pi * 0.6))
    draw_aries(cv, 1180, 920, 440, pose('run'), P=PF, rim=(1, -0.3))
    caption(tx, ['别人还在犹豫', '他已经冲出去了'], 1360, 200, 60, ((), (3, 4, 5)))


@frame(25.5, ['想做的事'], '一页写着「明天」的日历纸迎面飞来，挡在他面前', '正面 · 纸从景深处飞向镜头', '纸张翻飞')
def f12(sh, tx):
    cv = sh.cv; ground(cv, 940, PF, 0.5); speedlines(cv, PF, 280, 940, 30, -1, 0.3)
    draw_aries(cv, 560, 940, 400, pose('run'), P=PF, rim=(1, -0.3))
    cal_page(cv, tx, (1260, 560), 360, 420, '明天', PF, 1.0, 0.12)
    for k in range(3): cal_page(cv, tx, (1560 + k * 90, 300 + k * 140), 120, 140, '', PF, 0.4, -0.3 + k * 0.3)
    caption(tx, ['想做的事'], 960, 180, 64)


@frame(26.6, ['想做的事', '今天就要开始'], '他一跃穿过日历纸，纸从中间烧开，「明天」烧掉，背后露出金色的「今天」', '侧面跟拍 · 腾空定格一瞬', '纸燃 + 金属叮', gold=((), (0, 1, 4, 5)))
def f13(sh, tx):
    cv = sh.cv; ground(cv, 960, PF, 0.5)
    cal_page(cv, tx, (960, 520), 380, 440, '今天', PF, 1.0, 0.0, burn=0.55)
    draw_aries(cv, 980, 760, 400, pose('leap'), P=PF, rim=(1, -0.4))
    sparks(cv, (960, 520), 60, 120, 420, PF, 0.9, 9)
    caption(tx, ['想做的事', '今天就要开始'], 1460, 220, 58, ((), (0, 1, 4, 5)))


@frame(29.8, ['不服的事'], '地面「轰」地升起一堵墙拦住去路；他急刹车，靴子在地上犁出两道火花', '低机位 · 广角 · 墙压迫画面', '石墙升起 + 刹车摩擦')
def f14(sh, tx):
    cv = sh.cv; ground(cv, 940, PF, 0.6)
    wall(cv, 1420, 140, 940, 520, PF, 1.0)
    for k in range(10): cv.path([(1160 - k * 8, 950), (1160 + 30 - k * 8, 900 - k * 14)], PF.LINE, 0.4, 1.4, smooth=False)
    draw_aries(cv, 860, 940, 440, pose('skid'), P=PF, rim=(1, -0.3))
    sparks(cv, (940, 940), 80, 10, 200, PF, 1.0, 10, (-math.pi * 0.95, -math.pi * 0.55), 1.6)
    cv.path([(520, 946), (880, 946)], PF.WARM, 0.9, 3, smooth=False); cv.path([(540, 954), (900, 954)], PF.WARM, 0.6, 2, smooth=False)
    caption(tx, ['不服的事'], 600, 200, 64)


@frame(30.8, ['不服的事', '当场就要说清'], '他抬手一指——一道闪电劈在墙上，墙从中间裂开，金光从裂缝透出来', '仰拍 · 近景 · 闪白', '雷击 + 碎裂', gold=((), (0, 1, 4, 5)))
def f15(sh, tx):
    cv = sh.cv; ground(cv, 1000, PF, 0.6)
    wall(cv, 1480, 80, 1000, 560, PF, 1.0, crack=1.0)
    draw_aries(cv, 700, 1000, 560, pose('point'), P=PF, rim=(1, -0.2))
    bolt(cv, (1140, 0), (1220, 520), PF, 1.0, 3, PF.GOLD)
    sparks(cv, (1220, 520), 60, 20, 260, PF, 1.0, 11)
    caption(tx, ['不服的事', '当场就要说清'], 560, 170, 60, ((), (0, 1, 4, 5)))


@frame(34.5, ['可你知道吗'], '时间突然冻住：碎石和火星悬在半空，颜色退成冷蓝，所有声音都停了', '升镜 · 俯拍大全景', '一切静音，只留一声钟鸣')
def f16(sh, tx):
    cv = sh.cv; P = PV
    rr = np.random.default_rng(4)
    for _ in range(60):
        c = (rr.uniform(200, 1720), rr.uniform(200, 900)); s = rr.uniform(4, 14)
        cv.path([(c[0] - s, c[1]), (c[0], c[1] - s), (c[0] + s, c[1] + s * 0.4), (c[0] - s, c[1])], P.LINE, 0.6, 1.2, smooth=False)
    cv.path(sp([(0, 820), (960, 700), (W, 820)], 8), P.LINE, 0.4, 1.4)
    draw_aries(cv, 960, 760, 150, pose('hero', mouth='flat'), P=P, col=P.SOFT, heart=0.6)
    for k in range(3): cv.path([(960 + 70 * math.cos(q), 700 + 70 * (1 + k * 0.4) * math.sin(q) * 0.3 + k * 6) for q in np.linspace(0, 2 * math.pi, 50)], P.LINE, 0.25, 1, smooth=False)
    caption(tx, ['可你知道吗'], 960, 200, 64, col=P.WHITE)


@frame(35.6, ['可你知道吗', '跑得最快的人'], '冻住的画面里，他身后的残影一个个排开——这一路他跑得有多快', '横移 · 残影叠印', '倒放的风声')
def f17(sh, tx):
    cv = sh.cv; P = PV; ground(cv, 900, P, 0.5)
    for k in range(5):
        draw_aries(cv, 300 + k * 230, 900, 380, pose('run'), P=P, col=P.SOFT, a=0.2 + 0.18 * k, heart=0.3 + 0.15 * k, th=1.8 + 0.15 * k)
    caption(tx, ['可你知道吗', '跑得最快的人'], 1500, 200, 60, col=P.WHITE)


@frame(36.7, ['跑得最快的人', '最怕的是什么？'], '天上的星星一颗颗连起来，连成一个巨大的问号悬在他头顶', '仰拍 · 人小天大', '星星叮叮叮依次亮起')
def f18(sh, tx):
    cv = sh.cv; P = PV; starfield(cv, P, 200, 900, 2, 0.7, 4)
    q = [(840, 360), (850, 260), (930, 200), (1030, 220), (1070, 300), (1020, 380), (960, 430), (960, 520)]
    cv.path(q, P.SOFT, 0.8, 1.6, smooth=False)
    for p_ in q: glint(cv, p_, 22, P.WARM, 1)
    glint(cv, (960, 610), 30, P.WARM, 1)
    ground(cv, 1000, P, 0.5)
    draw_aries(cv, 960, 1000, 220, pose('lookback', d=1), P=P, col=P.SOFT, heart=0.6)
    caption(tx, ['跑得最快的人', '最怕的是什么？'], 1460, 760, 56, col=P.WHITE)


@frame(40.4, ['不是输'], '终点线的彩带在他面前断开，奖牌掉在地上——他看都不看，直接走过去', '侧面中景 · 奖牌在前景虚化', '彩带断裂 + 奖牌落地')
def f19(sh, tx):
    cv = sh.cv; ground(cv, 940, PF, 0.5)
    cv.path([(1000, 600), (1000, 940)], PF.LINE, 0.6, 2, smooth=False); cv.path([(1600, 600), (1600, 940)], PF.LINE, 0.6, 2, smooth=False)
    cv.path(sp([(1000, 640), (1120, 700), (1180, 760)], 6), PF.WARM, 0.9, 2.4); cv.path(sp([(1600, 640), (1480, 700), (1420, 780)], 6), PF.WARM, 0.9, 2.4)
    draw_aries(cv, 1260, 940, 420, pose('hero', mouth='flat', brow='calm', uaF=4, faF=10, uaB=-4, faB=4, hF='open', hB='open'), P=PF, rim=(-1, -0.3))
    sh.bokeh((420, 900), 110, PF.GOLD, 0.8); sh.bokeh((420, 900), 60, PF.WARM, 0.6)
    caption(tx, ['不是输'], 600, 260, 84)


@frame(41.5, ['不是输', '是在乎的人转身'], '路灯下，远处那个在乎的人转身走了；他回头，胸口的火焰心一下子暗下去，火星落成雨', '过肩镜头 · 他在前景，背影在远处', '音乐骤减 · 一个低音落下', gold=((), 'all'))
def f20(sh, tx):
    cv = sh.cv; P = PV; ground(cv, 960, P, 0.4)
    lamp(cv, 1320, 960, 420, P, 0.9, -1)
    mini(cv, 1300, 960, 220, P, 0.7, 'walk', 1)
    rain(cv, P, 0.35, 240, 0.12, 3)
    draw_aries(cv, 520, 1080 + 30, 900, pose('lookback', d=-1), d=-1, P=P, col=P.SOFT, heart=0.35, rim=(1, -0.2))
    caption(tx, ['不是输', '是在乎的人转身'], 1380, 230, 64, ((), 'all'), P.WHITE)


@frame(47.3, ['所以他把自己'], '他转回身，攥紧拳头，抬起下巴', '正面近景 · 缓慢推', '拳头攥紧的皮革声')
def f21(sh, tx):
    cv = sh.cv; starfield(cv, PF, 120, 600, 3, 0.4, 3)
    draw_aries(cv, 900, 1080 + 260, 1100, pose('stand_arm'), P=PF, rim=(1, -0.3), heart=0.6)
    caption(tx, ['所以他把自己'], 1500, 300, 64)


@frame(48.4, ['所以他把自己', '包装成刀枪不入'], '金色的铠甲一片一片飞来扣在身上：肩甲、胸甲、最后羊角头盔「咔」地合上', '环绕镜头 · 360° 半圈', '金属扣合 ×4 + 一声重响', gold=((), (3, 4, 5, 6)))
def f22(sh, tx):
    cv = sh.cv; ground(cv, 960, PF, 0.5)
    armor_burst(cv, (820, 620), PF, 0.9, 12, 320)
    draw_aries(cv, 820, 960, 560, pose('hero', mouth='flat', brow='fierce', hF='fist', hB='fist'), P=PF, armor=0.85, rim=(1, -0.3))
    godrays(cv, (820, 500), np.linspace(-math.pi, 0, 10), 900, PF.GOLD, 0.07)
    caption(tx, ['所以他把自己', '包装成刀枪不入'], 1440, 300, 62, ((), (3, 4, 5, 6)))


@frame(52.1, ['越怕受伤'], '箭和石子从四面飞来，全被铠甲弹开，火花四溅；他一动不动', '中景 · 慢动作', '叮叮叮连续弹开')
def f23(sh, tx):
    cv = sh.cv; ground(cv, 960, PF, 0.5)
    draw_aries(cv, 900, 960, 560, pose('stand_arm'), P=PF, armor=1.0, rim=(1, -0.3), heart=0.5)
    rr = np.random.default_rng(6)
    for k in range(9):
        q = rr.uniform(-math.pi, 0); p = (900 + 300 * math.cos(q), 650 + 240 * math.sin(q))
        cv.path([p, (p[0] + 200 * math.cos(q), p[1] + 200 * math.sin(q))], PF.LINE, 0.7, 1.6, smooth=False)
        sparks(cv, p, 10, 4, 50, PF, 0.9, k)
    caption(tx, ['越怕受伤'], 1500, 300, 70)


@frame(53.1, ['越怕受伤', '越要装作不怕'], '特写：他抬着下巴在笑——镜头推进胸甲，一道裂缝里，那颗软软的心在发抖', '特写 → 推进胸口（X光式）', '心跳加快，最后一拍收住', gold=((), (4, 5)))
def f24(sh, tx):
    cv = sh.cv
    J = draw_aries(cv, 780, 1080 + 1500 * 0.45, 1500, pose('hero', mouth='smile', brow='fierce', head=-8), P=PF, armor=1.0, rim=(1, -0.3), heart=0)
    c = (J['chest'][0] + 20, J['chest'][1] + 40)
    cr = [(c[0] - 20, c[1] - 110), (c[0] + 10, c[1] - 60), (c[0] - 15, c[1] - 10), (c[0] + 15, c[1] + 40), (c[0] - 5, c[1] + 100)]
    cv.path(cr, PF.WARM, 1, 3, smooth=False); cv.path(cr, PF.GOLD, 0.7, 14, smooth=False, layer=cv.F)
    heart(cv, (c[0] - 2, c[1] - 10), 34, PF, 1.0)
    for k in range(3): cv.path([(c[0] - 60 - k * 12, c[1] - 30 + k * 18), (c[0] - 46 - k * 12, c[1] - 24 + k * 18)], PF.WARM, 0.6, 1.4, smooth=False)
    caption(tx, ['越怕受伤', '越要装作不怕'], 1480, 300, 70, ((), (4, 5)))


# ================================================================ render + sheets
def render(f):
    sh = Shot(); tx = Text(PF)
    f['fn'](sh, tx)
    P = PV if f['fn'].__name__ in ('f16', 'f17', 'f18', 'f20') else PF
    img = sh.cv.composite(P.BG * 0.6, 0.0, glow=0.6) * P.VIG
    img = img + cv2.GaussianBlur(sh.fg, (0, 0), 9) * 0.9
    if sh.roll:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), sh.roll, 1.08); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    img = tx.blend(np.clip(img, 0, 1.5).astype(np.float32))
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def sheet(frames, imgs, k0, path, title):
    from PIL import Image, ImageDraw
    cols, tw, th_, gap, ann = 3, 620, 349, 20, 150
    rows = math.ceil(len(frames) / cols)
    S = Image.new('RGB', (cols * tw + (cols + 1) * gap, 110 + rows * (th_ + ann + gap)), (12, 10, 9)); d = ImageDraw.Draw(S)
    d.text((gap, 30), title, font=F(SERIF_BL, 46), fill=(255, 214, 140))
    for i, (f, im) in enumerate(zip(frames, imgs)):
        x = gap + (i % cols) * (tw + gap); y = 110 + (i // cols) * (th_ + ann + gap)
        S.paste(Image.fromarray(cv2.cvtColor(cv2.resize(im, (tw, th_), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)), (x, y))
        d.rectangle([x, y, x + tw - 1, y + th_ - 1], outline=(70, 55, 40))
        n = k0 + i; m, s = divmod(f['t'], 60)
        d.text((x, y + th_ + 8), f'{n:02d}   {int(m)}:{s:04.1f}', font=F(SANS_M, 24), fill=(255, 170, 90))
        line = ' / '.join(f['copy']) if f['copy'] else '（无字）'
        d.text((x + 150, y + th_ + 8), line, font=F(SERIF_B, 24), fill=(240, 235, 225))
        yy = y + th_ + 42
        for lab, txt, col in (('动作', f['action'], (215, 210, 200)), ('镜头', f['camera'], (170, 190, 210)), ('音效', f['sfx'], (170, 170, 160))):
            words = txt; lines = []; cur = ''
            for ch in words:
                if F(SANS_M, 19).getlength(lab + '：' + cur + ch) > tw - 6: lines.append(cur); cur = ch
                else: cur += ch
            lines.append(cur)
            for j, l in enumerate(lines[:3]):
                d.text((x, yy), (lab + '：' if j == 0 else '　　 ') + l, font=F(SANS_M, 19), fill=col); yy += 23
    S.save(path, quality=92)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--only')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    idx = range(len(FRAMES)) if not a.only else [int(x) - 1 for x in a.only.split(',')]
    imgs = {}
    for i in idx:
        im = render(FRAMES[i]); imgs[i] = im; cv2.imwrite(os.path.join(a.out, f'{i + 1:02d}.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 92]); print(i + 1, flush=True)
    if not a.only:
        sheet(FRAMES[:12], [imgs[i] for i in range(12)], 1, os.path.join(a.out, '分镜_01-12.jpg'), '白羊座的内心世界 · 第一分钟分镜（1/2）')
        sheet(FRAMES[12:], [imgs[i] for i in range(12, 24)], 13, os.path.join(a.out, '分镜_13-24.jpg'), '白羊座的内心世界 · 第一分钟分镜（2/2）')


if __name__ == '__main__':
    main()
