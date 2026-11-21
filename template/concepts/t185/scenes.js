/* T185 阳台菜园 Balcony Garden: planter grid, sprouts grow over days, a harvest count. Sample. */
(function () { const M = K.T.mo, X = M.X, SO = '#8d6e5a', GR = '#3fa34d';
  const pots = (c, cols, rows, x0, y0) => Array.from({ length: cols * rows }, (_, i) => { const g = M.box(c, x0 + (i % cols) * 170, y0 + Math.floor(i / cols) * 190, {}); M.box(g, 0, 60, { width: '140px', height: '110px', background: SO, borderRadius: '10px' }); g.sp = M.path(g, 20, -40, 100, 110, 'M50 105 V40 M50 60 C 30 50, 18 30, 22 10 C 40 18, 50 36, 50 60 M50 50 C 70 40, 82 20, 78 0 C 60 8, 50 26, 50 50', GR, 7); return g; });
  M.story({ bg: '#eaf5e4', sbg: ['#eaf5e4', '#e1f0d8', '#fff7df'], tr: ['rise', 'iris'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.c(1380, 180, 400), M.c(1380, 180, 400), M.q(110, 180, 420, 500, 24)],
    caps: [['阳台上，种了十二盆', 'Twelve pots on the balcony'], ['第 12 天，全发芽了（示例）', 'Day 12 — all sprouted (sample)'], ['第一次收获', 'The first harvest']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ p: pots(c, 4, 3, 220, 250), t: X(c, 220, 100, 64, '#2d5a27', '阳台菜园', 900) }), (s, t, a) => { s.p.forEach((g, i) => M.rise(g, t, a + .2 + i * .06, 99, { dy: 60 })); M.hero(s.t, t, a + .1, 99); }],
      [c => ({ p: pots(c, 4, 3, 220, 250), d: X(c, 220, 100, 64, '#2d5a27', '第 0 天', 900) }),
       (s, t, a) => { s.p.forEach((g, i) => { g.style.opacity = 1; M.draw(g.sp, t, a + .2 + (i * 5 % 12) * .12, .6, 99); g.sp.parentNode.style.transform = `rotate(${(4 * Math.sin(t * 2 + i)).toFixed(1)}deg)`; g.sp.parentNode.style.transformOrigin = '50% 100%'; }); const d = Math.min(12, Math.max(0, Math.round((t - a) * 6))); s.d.textContent = `第 ${d} 天 · 发芽了`; s.d.style.opacity = 1; }],
      [c => ({ bk: M.svg(c, 700, 360, 520, 360, '<path d="M20 120 H500 L440 340 H80Z" fill="#c98b4a"/><path d="M60 120 C 60 0, 460 0, 460 120" fill="none" stroke="#8a5a2a" stroke-width="16"/>'), v: [['#e63946', 820], ['#3fa34d', 920], ['#f4a261', 1020], ['#e63946', 1100]].map(([col, x]) => M.box(c, x, 0, { width: '90px', height: '90px', borderRadius: '50%', background: col })), n: X(c, 700, 160, 120, '#2d5a27', '× 12', 400, M.AN) }),
       (s, t, a) => { M.rise(s.bk, t, a - .1, 99, { dy: 100 }); s.v.forEach((e, i) => { const u = M.os((t - a - .3 - i * .15) / .5); e.style.opacity = t > a + .3 + i * .15 ? 1 : 0; e.style.transform = `translateY(${(-200 + 600 * u).toFixed(0)}px)`; }); M.hero(s.n, t, a + .9, 99); }]
    ] });
})();
