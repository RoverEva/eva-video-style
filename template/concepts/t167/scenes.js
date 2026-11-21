/* T167 时基对齐 Timebase: two tracks with ticks drift, a delta readout, then lock into sync. */
(function () { const M = K.T.mo, X = M.X, R = '#e63946', INK = '#111';
  const track = (c, y, lab) => { const g = M.box(c, 140, y, {}); X(g, 0, -20, 32, INK, lab, 700, M.MONO); M.box(g, 60, 0, { width: '1100px', height: '4px', background: INK }); g.tk = M.svg(g, 60, -40, 1100, 40, Array.from({ length: 56 }, (_, i) => `<line x1="${i * 20}" y1="${i % 5 ? 24 : 4}" x2="${i * 20}" y2="40" stroke="${INK}" stroke-width="3"/>`).join('')); return g; };
  M.story({ bg: '#fbfbf8', sbg: ['#fbfbf8', '#f4f4ef', '#fbfbf8'], tr: ['slide', 'rise'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.q(1400, 160, 400, 480, 18), M.q(1400, 160, 400, 480, 18), M.c(1420, 160, 380)],
    caps: [['画面和声音，差了一点', 'Picture and sound are slightly off'], ['差 12 毫秒（示例）', 'Off by 12 ms (sample)'], ['对齐，就顺了', 'Aligned, it just flows']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ L: track(c, 300, 'L'), Rr: track(c, 520, 'R'), t: X(c, 140, 120, 64, INK, 'TIMEBASE', 400, M.AN) }),
       (s, t, a) => { M.slide(s.L, t, a, 99, { dx: -200 }); M.slide(s.Rr, t, a + .2, 99, { dx: 200 }); s.Rr.tk.style.transform = `translateX(${(8 + 6 * Math.sin(t * 2)).toFixed(1)}px)`; M.rise(s.t, t, a + .3, 99); }],
      [c => ({ L: track(c, 300, 'L'), Rr: track(c, 520, 'R'), m1: M.box(c, 680, 240, { width: '4px', height: '340px', background: R }), m2: M.box(c, 704, 240, { width: '4px', height: '340px', background: R }), n: X(c, 640, 680, 110, R, 'Δ 12 ms', 400, M.INTER) }),
       (s, t, a) => { s.L.style.opacity = s.Rr.style.opacity = 1; s.Rr.tk.style.transform = 'translateX(12px)'; M.rise(s.m1, t, a, 99); M.rise(s.m2, t, a + .2, 99); M.hero(s.n, t, a + .5, 99); M.count(s.n, 12, t, a + .5, .8, v => 'Δ ' + v + ' ms'); }],
      [c => ({ L: track(c, 300, 'L'), Rr: track(c, 520, 'R'), m: M.box(c, 680, 240, { width: '6px', height: '340px', background: '#2a9d8f' }), n: X(c, 640, 680, 110, '#2a9d8f', 'Δ 0 ms ✓', 400, M.INTER) }),
       (s, t, a) => { s.L.style.opacity = s.Rr.style.opacity = 1; s.Rr.tk.style.transform = `translateX(${(12 * (1 - M.io((t - a - .2) / .8))).toFixed(1)}px)`; M.rise(s.m, t, a + .9, 99); M.hero(s.n, t, a + 1, 99); }]
    ] });
})();
