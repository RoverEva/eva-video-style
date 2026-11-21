/* T190 换不换车 Upgrade or Keep: old vs new car silhouettes, checklist duel, verdict stamp. Sample. */
(function () { const M = K.T.mo, X = M.X, OLD = '#8d99ae', NEW = '#2a9d8f', INK = '#2b2d42';
  const car = (c, x, y, col, s) => M.svg(c, x, y, 360 * s, 160 * s, `<g transform="scale(${s})"><path d="M20 110 L50 60 Q 90 20 160 20 H220 Q 280 20 320 70 L345 110 Q 350 130 330 130 H30 Q 10 130 20 110Z" fill="${col}"/><circle cx="90" cy="130" r="26" fill="${INK}"/><circle cx="270" cy="130" r="26" fill="${INK}"/></g>`, { transformOrigin: '50% 50%' });
  M.story({ bg: '#f1f3f6', sbg: ['#f1f3f6', '#eceff3', '#f1f3f6'], tr: ['push', 'flip'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1420, 180, 380, 460, 20), M.q(1420, 180, 380, 460, 20), M.c(110, 200, 360)],
    caps: [['车开了八年，要不要换？', 'Eight years in — upgrade or keep?'], ['油耗、保养、安全，逐项比', 'Fuel, upkeep, safety — side by side'], ['结论：再开两年（示例）', 'Verdict: keep it two more years (sample)']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ o: car(c, 200, 400, OLD, 1.4), n: car(c, 800, 400, NEW, 1.4), lo: X(c, 330, 280, 64, OLD, '旧车', 900), ln: X(c, 930, 280, 64, NEW, '新车', 900), vs: X(c, 700, 440, 80, INK, 'VS', 400, M.AN) }),
       (s, t, a) => { M.slide(s.o, t, a + .1, 99, { dx: -400 }); M.slide(s.n, t, a + .3, 99, { dx: 400 }); M.rise(s.lo, t, a + .5, 99); M.rise(s.ln, t, a + .6, 99); M.pop(s.vs, t, a + .9, 99, { from: 2 }); }],
      [c => ({ o: car(c, 200, 140, OLD, .8), n: car(c, 800, 140, NEW, .8), rows: ['油耗', '保养', '安全'].map((k, i) => { const g = M.box(c, 200, 360 + i * 120, {}); X(g, 0, 0, 52, '#c0392b', '✕ ' + k, 900); X(g, 600, 0, 52, NEW, '✓ ' + k, 900); return g; }), cost: X(c, 800, 740, 44, '#c0392b', '但：多花 ¥15 万（示例）', 900) }),
       (s, t, a) => { s.o.style.opacity = s.n.style.opacity = 1; s.rows.forEach((g, i) => M.slide(g, t, a - .1 + i * .3, 99, { dx: -80 })); M.hero(s.cost, t, a + 1.2, 99); }],
      [c => ({ o: car(c, 760, 360, OLD, 1.6), st: M.box(c, 820, 700, { padding: '16px 40px', border: '8px solid #e63946', borderRadius: '14px', color: '#e63946', font: M.f(900, 70, M.CN), transform: 'rotate(-6deg)' }, '再开两年'), t: X(c, 760, 200, 52, INK, '结论（示例）', 900) }),
       (s, t, a) => { M.pop(s.o, t, a - .1, 99, { from: .7 }); M.rise(s.t, t, a + .2, 99); M.pop(s.st, t, a + .7, 99, { from: 2.4, base: 'rotate(-6deg)' }); }]
    ] });
})();
