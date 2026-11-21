/* T104 汉字小剧场 Glyph Theater: curtains of 幕 part; 人+木=休; 日 rises over 一 = 旦 */
(function () { const M = K.T.mo, X = M.X, SER = M.SERIF, RED = '#b3262b', GOLD = '#f1d08a';
  M.story({ bg: '#160d08', sbg: ['#160d08', '#f3ead6', '#1c120b'], tr: ['shutter', 'iris'], ring: () => ({ color: '#d9b25a', width: 8, shadow: .5 }),
    wins: [M.c(1500, 110, 320), M.q(120, 160, 400, 500, 30), M.c(1420, 160, 360)],
    caps: [['汉字也会演戏', 'Chinese characters can act'], ['人靠着树，就是“休”', 'A person by a tree: “rest”'], ['太阳升出地平线，就是“旦”', 'Sun over the horizon: “dawn”']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ L: X(c, 0, 0, 52, RED, '幕<br>'.repeat(16), 900, SER, { lineHeight: 1.3, width: '960px', whiteSpace: 'normal', letterSpacing: '20px', columnCount: 1 }), R: X(c, 960, 0, 52, RED, '幕<br>'.repeat(16), 900, SER, { lineHeight: 1.3 }),
          cols: Array.from({ length: 16 }, (_, i) => X(c, i * 60 + (i >= 8 ? 960 - 480 : 0), 0, 52, RED, '幕<br>'.repeat(14), 900, SER, { lineHeight: 1.36, opacity: .9 })), t: X(c, 520, 330, 150, GOLD, '汉字小剧场', 900, SER), fl: X(c, 300, 640, 34, '#6b4a2a', '台'.repeat(40), 700, SER) }),
       (s, t, a) => { s.L.style.display = s.R.style.display = 'none'; const o = M.io((t - a - .3) / 1.0); s.cols.forEach((e, i) => { e.style.transform = `translateX(${((i < 8 ? -1 : 1) * 700 * o).toFixed(1)}px)`; });
         M.hero(s.t, t, a + .9, 99, { dx: 0, dy: 30, noclip: true }); M.rise(s.fl, t, a + .5, 99); }],
      [c => ({ ren: X(c, 700, 260, 300, '#1b1b1b', '人', 900, SER), mu: X(c, 1150, 260, 300, '#1b1b1b', '木', 900, SER), xiu: X(c, 800, 240, 340, RED, '休', 900, SER), lb: X(c, 700, 640, 44, '#5a3a22', '人 + 木 ＝ 休：靠着树歇一歇', 900, M.CN) }),
       (s, t, a) => { const m = M.io((t - a - 1.0) / .6); M.slide(s.ren, t, a - .1, 99, { dx: -200 }); M.slide(s.mu, t, a + .1, 99, { dx: 200 });
         s.ren.style.transform += ` translateX(${(170 * m).toFixed(1)}px)`; s.mu.style.transform += ` translateX(${(-170 * m).toFixed(1)}px)`; s.ren.style.opacity *= 1 - M.i2((t - a - 1.5) / .3); s.mu.style.opacity *= 1 - M.i2((t - a - 1.5) / .3);
         M.pop(s.xiu, t, a + 1.55, 99, { from: .6 }); M.rise(s.lb, t, a + 1.8, 99); }],
      [c => ({ hz: M.path(c, 300, 560, 900, 20, 'M0 10 H900', GOLD, 10), sun: M.box(c, 660, 0, { width: '180px', height: '180px', borderRadius: '50%', background: 'radial-gradient(circle,#ffd166,#ff7b00)', boxShadow: '0 0 60px #ff9f1c' }),
          ri: X(c, 640, 300, 200, GOLD, '日', 900, SER), yi: X(c, 640, 470, 200, GOLD, '一', 900, SER), dan: X(c, 980, 300, 300, '#fff', '＝ 旦', 900, SER) }),
       (s, t, a) => { M.draw(s.hz, t, a - .1, .6, 99); const u = M.o3((t - a) / 1.4); s.sun.style.opacity = M.env(t, a, 99).a * (1 - M.i2((t - a - 1.3) / .3)); s.sun.style.transform = `translateY(${(620 - 340 * u).toFixed(1)}px)`;
         M.rise(s.ri, t, a + 1.3, 99, { dy: 120 }); M.rise(s.yi, t, a + 1.3, 99, { dy: 0 }); M.hero(s.dan, t, a + 1.7, 99, { dx: 60 }); }]
    ] });
})();
