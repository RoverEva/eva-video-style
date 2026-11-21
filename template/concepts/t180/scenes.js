/* T180 习惯档案 Habit Grid: archive cards for each day fill in, a streak highlights, day counter. Sample. */
(function () { const M = K.T.mo, X = M.X, INK = '#2b2d42', COLS = ['#8ac06a', '#f2c14e', '#ef6f3c', '#4a6f8a'];
  const grid = (c, x0, y0, n, cols, start) => Array.from({ length: n }, (_, i) => { const g = M.box(c, x0 + (i % cols) * 140, y0 + Math.floor(i / cols) * 150, { width: '120px', height: '130px', background: '#fff', border: '2px solid #dde', borderRadius: '8px', boxSizing: 'border-box' }); g.d = M.box(g, 44, 30, { width: '32px', height: '32px', borderRadius: '50%', background: COLS[i % 4] }); X(g, 10, 92, 18, '#889', 'No.' + (start + i), 700, M.MONO); return g; });
  M.story({ bg: '#eef0f4', sbg: ['#eef0f4', '#f4f5f8', '#eef0f4'], tr: ['rise', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1400, 180, 400, 500, 20), M.q(1400, 180, 400, 500, 20), M.c(1420, 180, 380)],
    caps: [['每天打一张卡', 'One card per day'], ['连续 7 天，没断', 'Seven days straight'], ['第 27 天，还在坚持（示例）', 'Day 27 and going (sample)']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ g: grid(c, 160, 180, 24, 8, 400) }), (s, t, a) => s.g.forEach((e, i) => { M.pop(e, t, a + .2 + i * .06, 99, { from: .3 }); M.pop(e.d, t, a + .5 + i * .06, 99, { from: 0 }); })],
      [c => ({ g: grid(c, 160, 180, 24, 8, 400), hl: M.box(c, 150, 320, { width: '0px', height: '150px', border: '6px solid #3a86ff', borderRadius: '14px', boxSizing: 'border-box' }), t: X(c, 160, 720, 80, '#3a86ff', '连续 7 天', 900) }),
       (s, t, a) => { s.g.forEach(e => { e.style.opacity = 1; e.d.style.opacity = 1; }); s.hl.style.width = (20 + 960 * M.io((t - a) / 1.4)) + 'px'; M.hero(s.t, t, a + 1, 99); }],
      [c => ({ n: X(c, 160, 200, 300, INK, '27', 400, M.AN), t: X(c, 170, 540, 70, INK, '第 27 天 · 习惯打卡', 900), sm: X(c, 176, 660, 30, '#889', 'SAMPLE 示例', 700, M.MONO), dots: Array.from({ length: 27 }, (_, i) => M.box(c, 700 + (i % 9) * 70, 200 + Math.floor(i / 9) * 70, { width: '44px', height: '44px', borderRadius: '50%', background: COLS[i % 4] })) }),
       (s, t, a) => { M.hero(s.n, t, a, 99); M.count(s.n, 27, t, a, 1.2); M.rise(s.t, t, a + .4, 99); M.rise(s.sm, t, a + .6, 99); s.dots.forEach((d, i) => M.pop(d, t, a + .1 + i * .04, 99, { from: 0 })); }]
    ] });
})();
