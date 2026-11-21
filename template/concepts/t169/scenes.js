/* T169 轴测线稿 Axonometric: isometric line shelves draw in, a warm light sweep, dimension label. */
(function () { const M = K.T.mo, X = M.X, INK = '#222';
  const iso = (x, y, z) => [960 + (x - y) * .866, 800 + (x + y) * .5 - z];
  const boxP = (x, y, z, w, d, h) => { const P = [[x, y, z], [x + w, y, z], [x + w, y + d, z], [x, y + d, z]].map(([a, b, c]) => iso(a, b, c)), Q = [[x, y, z + h], [x + w, y, z + h], [x + w, y + d, z + h], [x, y + d, z + h]].map(([a, b, c]) => iso(a, b, c)); const m = p => p.map(v => v.toFixed(1)).join(' '); return `M${m(P[0])} L${m(P[1])} L${m(P[2])} L${m(P[3])}Z M${m(Q[0])} L${m(Q[1])} L${m(Q[2])} L${m(Q[3])}Z M${m(P[0])} L${m(Q[0])} M${m(P[1])} L${m(Q[1])} M${m(P[2])} L${m(Q[2])} M${m(P[3])} L${m(Q[3])}`; };
  const shelf = (c, n, dx) => Array.from({ length: n }, (_, i) => M.path(c, 0, 0, 1920, 1080, boxP(-500 + i * 130 + (dx || 0), -200, 0, 20, 260, 280), INK, 3));
  M.story({ bg: '#fbfaf6', sbg: ['#fbfaf6', '#f6f3ec', '#fbfaf6'], tr: ['slide', 'iris'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1420, 160, 380, 460, 18), M.c(110, 160, 360), M.q(1420, 160, 380, 460, 18)],
    caps: [['一层书架，先画线稿', 'One shelf level, drawn as lines'], ['光扫过，看清结构', 'Light sweeps the structure'], ['一层 · 26 米书架', 'One floor · 26 m of shelves']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ sh: shelf(c, 8, -100), fl: M.path(c, 0, 0, 1920, 1080, 'M120 860 H1200', INK, 2) }), (s, t, a) => { s.sh.forEach((p, i) => M.draw(p, t, a + i * .2, .8, 99)); M.draw(s.fl, t, a, 1, 99); }],
      [c => ({ sh: shelf(c, 8, 40), lt: M.box(c, -300, -100, { width: '200px', height: '1400px', background: 'linear-gradient(90deg,transparent,rgba(255,200,90,.45),transparent)', transform: 'rotate(18deg)' }) }),
       (s, t, a) => { s.sh.forEach(p => M.draw(p, t, a - .5, .3, 99)); s.lt.style.transform = `translateX(${(-200 + 2400 * M.io((t - a) / 2.6)).toFixed(0)}px) rotate(18deg)`; }],
      [c => ({ sh: shelf(c, 6, -200), t: X(c, 140, 760, 70, INK, '一层 · 26 米书架', 900), n: X(c, 140, 140, 140, '#c47a2c', '26 m', 400, M.AN) }),
       (s, t, a) => { s.sh.forEach((p, i) => M.draw(p, t, a - .1 + i * .1, .4, 99)); M.hero(s.t, t, a + .5, 99); M.hero(s.n, t, a + .2, 99); M.count(s.n, 26, t, a + .2, 1, v => v + ' m'); }]
    ] });
})();
