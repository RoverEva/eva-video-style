/* T107 深海压强 Depth: each scene is deeper (rise transitions = descending). ~1 atm per 10 m; light fades by ~200 m. */
(function () { const M = K.T.mo, X = M.X;
  const gauge = (c, m, atm, col) => ({ d: X(c, 200, 300, 210, col, m, 400, M.AN), p: X(c, 210, 560, 52, col, atm, 700, M.MONO), r: M.box(c, 110, 140, { width: '6px', height: '700px', background: `repeating-linear-gradient(${col} 0 3px, transparent 3px 40px)` }) });
  M.story({ bg: '#1d5f99', sbg: ['linear-gradient(#6fc0ee,#1d5f99)', 'linear-gradient(#0d3b66,#071a33)', 'linear-gradient(#04101f,#000)'], tr: ['rise', 'rise'], ring: () => ({ color: '#9fdcff', width: 6, shadow: .4 }),
    wins: [M.c(1400, 140, 400), M.c(1430, 180, 360), M.c(1460, 220, 320)],
    caps: [['从海面往下潜', 'Diving down from the surface'], ['每下潜 10 米，多一个大气压', 'Every 10 m adds one atmosphere'], ['到 200 米，阳光几乎消失', 'By 200 m, sunlight is almost gone']], port: { box: [100, 100, 1760, 760] },
    scenes: [
      [c => Object.assign(gauge(c, '0 m', '1 atm · 海面', '#fff'), { rays: [0, 1, 2, 3].map(i => M.box(c, 500 + i * 220, -100, { width: '80px', height: '900px', background: 'linear-gradient(rgba(255,255,255,.35),transparent)', transform: 'rotate(14deg)' })) }),
       (s, t, a) => { M.hero(s.d, t, a + .3, 99, { dx: 0, dy: 40 }); M.rise(s.p, t, a + .6, 99); M.rise(s.r, t, a + .2, 99); s.rays.forEach((e, i) => { e.style.opacity = (.5 + .4 * Math.sin(t * 2 + i)).toFixed(2); }); }],
      [c => Object.assign(gauge(c, '100 m', '11 atm', '#bfe3ff'), { fish: [0, 1, 2].map(i => M.svg(c, 700 + i * 160, 200 + i * 120, 120, 60, '<path d="M10 30 C 40 0, 80 0, 100 30 C 80 60, 40 60, 10 30Z M100 30 L120 10 V50Z" fill="#7fb8e6" opacity=".7"/>')) }),
       (s, t, a) => { M.hero(s.d, t, a - .1, 99, { dx: 0, dy: 60 }); M.count(s.d, 100, t, a - .1, 1.2, v => v + ' m'); M.rise(s.p, t, a + .4, 99); M.rise(s.r, t, a, 99); s.fish.forEach((e, i) => { M.rise(e, t, a + .2 + i * .2, 99); e.style.transform += ` translateX(${(-(t - a) * (50 + i * 30)).toFixed(1)}px)`; }); }],
      [c => Object.assign(gauge(c, '200 m', '21 atm · 光消失', '#7fd0ff'), { glow: Array.from({ length: 22 }, (_, i) => M.box(c, 600 + (i * 137) % 700, 120 + (i * 89) % 620, { width: '10px', height: '10px', borderRadius: '50%', background: i % 2 ? '#3ff0ff' : '#b5ff7d', boxShadow: '0 0 14px currentColor', color: i % 2 ? '#3ff0ff' : '#b5ff7d' })) }),
       (s, t, a) => { M.hero(s.d, t, a - .1, 99, { dx: 0, dy: 60 }); M.count(s.d, 200, t, a - .1, 1.2, v => v + ' m'); M.rise(s.p, t, a + .4, 99); M.rise(s.r, t, a, 99); s.glow.forEach((e, i) => { e.style.opacity = (M.env(t, a + .3 + i * .04, 99).a * (.3 + .7 * Math.abs(Math.sin(t * 2 + i)))).toFixed(2); }); }]
    ] });
})();
