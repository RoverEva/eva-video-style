/* T149 冰原档案 Polar Archive: aurora, ice archive cards with years, frosted strata. */
(function () { const M = K.T.mo, X = M.X, IC = '#cfe8f3', DK = '#0b2a3a';
  const aur = c => M.box(c, -200, -60, { width: '2320px', height: '420px', background: 'linear-gradient(90deg,transparent,rgba(80,255,180,.4),rgba(120,160,255,.35),transparent)', filter: 'blur(40px)', borderRadius: '50%' });
  M.story({ bg: DK, sbg: ['linear-gradient(#0b2a3a,#cfe8f3 75%)', 'linear-gradient(#0e3346,#9cc9dc)', 'linear-gradient(#cfe8f3,#f4fbff)'], tr: ['blur', 'rise'], ring: () => ({ color: '#ffffff', width: 8, shadow: .3 }),
    wins: [M.q(1360, 150, 420, 520, 24), M.c(110, 160, 380), M.q(1380, 170, 400, 480, 24)],
    caps: [['冰层里，藏着一百年的气候', 'A century of climate, kept in ice'], ['每一层，就是一年', 'Each layer is one year'], ['从 1912 到 2026（示例）', 'From 1912 to 2026 (sample)']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ a: aur(c), t: X(c, 160, 220, 140, '#fff', '冰原档案', 900, M.SERIF), e: X(c, 168, 420, 44, '#9ff0d0', 'POLAR ARCHIVE', 700, M.MONO) }),
       (s, t, a) => { s.a.style.opacity = M.env(t, a, 99, .8).a; s.a.style.transform = `translateX(${(120 * Math.sin(t * .8)).toFixed(1)}px) skewX(${(10 * Math.sin(t * .5)).toFixed(1)}deg)`; M.hero(s.t, t, a + .3, 99); M.rise(s.e, t, a + .7, 99); }],
      [c => ({ L: Array.from({ length: 9 }, (_, i) => M.box(c, 640, 160 + i * 72, { width: '640px', height: '60px', borderRadius: '8px', background: `rgba(235,248,255,${(.35 + i * .07).toFixed(2)})`, boxShadow: 'inset 0 -6px 0 rgba(0,40,70,.15)' })), y: Array.from({ length: 9 }, (_, i) => X(c, 1320, 172 + i * 72, 32, '#eaf7ff', String(2026 - i * 14), 700, M.MONO)) }),
       (s, t, a) => s.L.forEach((e, i) => { M.slide(e, t, a - .15 + i * .07, 99, { dx: i % 2 ? 300 : -300 }); M.rise(s.y[i], t, a + .2 + i * .07, 99); })],
      [c => ({ cards: [['No.01', '1912'], ['No.02', '1957'], ['No.03', '2026']].map(([n, y], i) => { const g = M.box(c, 160 + i * 360, 300, { width: '300px', height: '380px', background: '#fff', boxShadow: '0 20px 40px rgba(11,42,58,.18)', padding: '30px', boxSizing: 'border-box', transformOrigin: '50% 100%' }); X(g, 30, 30, 44, DK, n, 700, M.MONO); X(g, 30, 100, 80, DK, y, 700, M.MONO); return g; }), sm: X(c, 166, 720, 26, '#5a7a8a', 'SAMPLE ARCHIVE 示例') }),
       (s, t, a) => { s.cards.forEach((g, i) => { M.pop(g, t, a - .1 + i * .2, 99, { from: .6 }); g.style.transform += ` rotate(${((i - 1) * 3).toFixed(0)}deg)`; }); M.rise(s.sm, t, a + .9, 99); }]
    ] });
})();
