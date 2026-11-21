/* T115 信息卡堆叠 Card Stack (finance). Figures are SAMPLE. */
(function () { const M = K.T.mo, X = M.X, IN = '#cfd8ff';
  const stack = (c, cols) => cols.map((col, i) => M.card(c, 220 + i * 30, 180 + i * 36, 620, 560, col, { borderRadius: '34px', boxShadow: '0 30px 60px rgba(0,0,0,.45)' }));
  M.story({ bg: '#121826', sbg: ['#121826', '#18213b', '#121826'], tr: ['rise', 'flip'], ring: () => ({ color: '#5c6bc0', width: 6, shadow: .5 }),
    wins: [M.c(1440, 140, 380), M.q(1380, 160, 400, 480, 30), M.c(1420, 150, 380)],
    caps: [['这个月的市场，一张卡说清', "This month's market on one card"], ['三个方向：科技、消费、能源', 'Three themes: tech, consumer, energy'], ['关注，但别追高（示例观点）', 'Watch, but don’t chase (sample view)']], port: { box: [180, 120, 1680, 800] },
    scenes: [
      [c => ({ st: stack(c, ['#2b3a67', '#3f51b5', '#5c6bc0']), n: X(c, 330, 330, 190, '#fff', '+12%', 400, M.AN), l: X(c, 340, 560, 40, IN, '本月方向 · 示例数据') }),
       (s, t, a) => { s.st.forEach((e, i) => M.rise(e, t, a + .2 + i * .14, 99, { dy: 200 })); M.hero(s.n, t, a + .7, 99, { dx: 0, dy: 40 }); M.count(s.n, 12, t, a + .7, 1, v => '+' + v + '%'); M.rise(s.l, t, a + 1.0, 99); }],
      [c => ({ cs: [['科技', '#7c4dff'], ['消费', '#ff7043'], ['能源', '#26a69a']].map(([n, col], i) => { const g = M.card(c, 160 + i * 380, 220, 340, 460, col, { borderRadius: '30px' }); X(g, 40, 40, 30, 'rgba(255,255,255,.8)', '0' + (i + 1), 700, M.MONO); X(g, 40, 120, 80, '#fff', n); X(g, 40, 260, 30, 'rgba(255,255,255,.85)', ['算力需求', '假期出行', '储能'][i]); return g; }) }),
       (s, t, a) => s.cs.forEach((g, i) => { M.rise(g, t, a - .15 + i * .2, 99, { dy: 260 }); g.style.transform += ` rotate(${((i - 1) * 3).toFixed(1)}deg)`; })],
      [c => ({ card: M.card(c, 220, 220, 1000, 460, '#fff', { borderRadius: '34px' }), ar: M.path(c, 1240, 380, 260, 140, 'M10 120 C 80 120, 120 20, 240 20 M210 4 L242 20 L212 40', '#ff7043', 10) }),
       (s, t, a) => { if (!s.card.d) { X(s.card, 60, 70, 40, '#5c6bc0', '一句话 ONE LINE', 700, M.MONO); X(s.card, 60, 150, 92, '#121826', '关注，'); X(s.card, 60, 270, 92, '#121826', '但别追高'); X(s.card, 62, 400, 24, '#8a93ad', '示例观点，不构成投资建议'); s.card.d = 1; }
         M.panel(s.card, t, a - .1, 99, { r: 34 }); M.draw(s.ar, t, a + .7, .6, 99); }]
    ] });
})();
