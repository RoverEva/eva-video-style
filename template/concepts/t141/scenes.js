/* T141 排队值不值 Queue Meter (food review). Scores are SAMPLE. */
(function () { const M = K.T.mo, X = M.X, OR = '#ff6b35', INK = '#222';
  M.story({ bg: '#fff6e6', sbg: ['#fff6e6', '#2a1a10', '#fff6e6'], tr: ['push', 'flip'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.c(1560, 110, 300), M.q(120, 160, 420, 500, 24)],
    caps: [['网红店，排 45 分钟（示例）', 'A hyped spot: 45 minutes (sample)'], ['口味、价格、环境，逐项打分', 'Taste, price, setting — scored'], ['结论：值得排一次', 'Verdict: worth one wait']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ q: Array.from({ length: 9 }, (_, i) => M.box(c, 160 + i * 110, 520, { width: '70px', height: '150px', borderRadius: '35px 35px 10px 10px', background: '#e9d7bd' })), n: X(c, 160, 180, 200, OR, '45 min', 400, M.AN), t: X(c, 170, 420, 50, INK, '排队时间（示例）') }),
       (s, t, a) => { s.q.forEach((e, i) => { M.rise(e, t, a + .1 + i * .06, 99, { dy: 60 }); e.style.transform += ` translateY(${(-6 * Math.abs(Math.sin(t * 3 + i))).toFixed(1)}px)`; }); M.hero(s.n, t, a + .3, 99); M.count(s.n, 45, t, a + .3, 1.2, v => v + ' min'); M.rise(s.t, t, a + .6, 99); }],
      [c => ({ rows: [['口味', 9], ['价格', 6], ['环境', 8], ['服务', 7]].map(([k, v], i) => { const g = M.box(c, 160, 200 + i * 140, {}); X(g, 0, 0, 52, '#f6e7d0', k); g.b = M.box(g, 180, 18, { width: '0px', height: '40px', borderRadius: '20px', background: OR }); g.v = v; g.n = X(g, 0, 0, 52, OR, v + '/10', 400, M.AN); return g; }) }),
       (s, t, a) => s.rows.forEach((g, i) => { M.slide(g, t, a - .15 + i * .15, 99, { dx: -60 }); const u = M.o3((t - a - .2 - i * .15) / .8); g.b.style.width = (g.v * 80 * u) + 'px'; g.n.style.transform = `translateX(${(200 + g.v * 80 * u).toFixed(1)}px)`; })],
      [c => ({ st: X(c, 640, 220, 110, '#ffb703', '★★★★☆'), v: X(c, 640, 380, 120, INK, '值得排一次'), sm: X(c, 646, 560, 30, '#a08060', '示例测评 · 个人口味') }),
       (s, t, a) => { M.hero(s.st, t, a - .1, 99); M.hero(s.v, t, a + .3, 99); M.rise(s.sm, t, a + .7, 99); }]
    ] });
})();
