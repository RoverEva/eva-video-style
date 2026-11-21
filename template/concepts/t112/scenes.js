/* T112 决策剧场 Decision Theater: spotlight on the table → bars grow → one big number. SAMPLE data. */
(function () { const M = K.T.mo, X = M.X, Y = '#ffd23f';
  const spot = (c, x) => M.box(c, x - 500, -100, { width: '1000px', height: '1300px', background: 'radial-gradient(ellipse at 50% 55%, rgba(255,255,255,.16), transparent 55%)' });
  M.story({ bg: '#000', sbg: ['#000', '#070707', '#000'], tr: ['iris', 'shutter'], ring: () => ({ color: Y, width: 4, shadow: .5 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 380, 460, 22), M.c(1440, 140, 380)],
    caps: [['A 还是 B？先看数据', 'A or B? Look at the data first'], ['一根根柱子，说清楚差距', 'Bar by bar, the gap is clear'], ['选 B，多出 72%（示例）', 'Pick B: 72% more (sample)']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ sp: spot(c, 700), rows: [['方案 A', '成本 低', '周期 长'], ['方案 B', '成本 中', '周期 短']].map((r, i) => { const g = M.box(c, 260, 300 + i * 160, { display: 'flex', gap: '60px' }); r.forEach((v, k) => X(g, 0, 0, 52, k ? '#bbb' : '#fff', v, 800, M.CN, { position: 'static' })); return g; }) }),
       (s, t, a) => { s.sp.style.opacity = M.env(t, a, 99, .6).a; s.sp.style.transform = `translateX(${(80 * Math.sin(t)).toFixed(1)}px)`; s.rows.forEach((g, i) => M.slide(g, t, a + .3 + i * .3, 99, { dx: -60 })); }],
      [c => ({ sp: spot(c, 1100), b: [140, 220, 180, 330, 270, 420].map((h, i) => M.box(c, 640 + i * 150, 820 - h, { width: '100px', height: h + 'px', background: i === 5 ? Y : '#3a3a3a', transformOrigin: '50% 100%' })) }),
       (s, t, a) => { s.sp.style.opacity = M.env(t, a - .2, 99, .5).a; s.b.forEach((e, i) => { const u = M.os((t - a + .1 - i * .12) / .5); e.style.transform = `scaleY(${Math.max(0, u).toFixed(3)})`; e.style.opacity = u > 0 ? 1 : 0; }); }],
      [c => ({ sp: spot(c, 700), n: X(c, 300, 260, 300, '#fff', '72%', 400, M.AN), lb: X(c, 320, 600, 52, Y, '选 B（示例）'), ring: M.box(c, 200, 140, { width: '1000px', height: '700px', borderRadius: '50%', boxShadow: '0 0 0 2000px #000' }) }),
       (s, t, a) => { s.sp.style.opacity = 1; M.hero(s.n, t, a - .1, 99, { dx: 0, dy: 40 }); M.count(s.n, 72, t, a - .1, 1.0, v => v + '%'); M.rise(s.lb, t, a + .5, 99); const u = M.i2((t - a - 1.9) / .8); s.ring.style.transform = `scale(${(1.6 - .9 * u).toFixed(3)})`; s.ring.style.opacity = u > 0 ? 1 : 0; }]
    ] });
})();
