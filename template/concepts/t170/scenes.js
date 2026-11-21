/* T170 能流传导 Current: four energy nodes, glowing packets travel the dotted grid, totals tick. */
(function () { const M = K.T.mo, X = M.X, G = '#3fe0a0';
  const N = [[300, 540, '风 WIND'], [700, 240, '网 GRID'], [1100, 540, '储 STORE'], [700, 840, '轮 WHEEL']];
  const net = c => { const s = M.svg(c, 0, 0, 1920, 1080, N.map(([x, y], i) => { const [x2, y2] = N[(i + 1) % 4]; return `<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${G}" stroke-width="3" stroke-dasharray="8 10" opacity=".6"/>`; }).join('') + N.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="40" fill="none" stroke="${G}" stroke-width="4"/>`).join('')); s.lb = N.map(([x, y, n]) => X(c, x - 80, y + 56, 30, G, n, 700, M.MONO, { width: '160px', textAlign: 'center' })); s.pk = Array.from({ length: 8 }, () => M.box(c, 0, 0, { width: '18px', height: '18px', borderRadius: '50%', background: G, boxShadow: `0 0 20px ${G}` })); return s; };
  const flow = (s, t, sp) => s.pk.forEach((e, i) => { const u = ((t * sp + i / 8) % 1) * 4, k = Math.floor(u), f = u - k, [x1, y1] = N[k], [x2, y2] = N[(k + 1) % 4]; e.style.transform = `translate(${(x1 + (x2 - x1) * f - 9).toFixed(1)}px, ${(y1 + (y2 - y1) * f - 9).toFixed(1)}px)`; });
  M.story({ bg: '#070a09', sbg: ['#070a09', '#08100d', '#070a09'], tr: ['zoom', 'blur'], ring: () => ({ color: G, width: 4, glow: 'rgba(63,224,160,.5)', shadow: .5 }),
    wins: [M.q(1420, 200, 380, 460, 18), M.q(1420, 200, 380, 460, 18), M.c(1440, 160, 360)],
    caps: [['电，从风里来', 'Power comes from the wind'], ['存起来，再送出去', 'Stored, then sent out'], ['一天，循环 24 小时（示例）', '24 hours, in a loop (sample)']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ n: net(c), t: X(c, 120, 80, 60, '#e8fff5', 'CURRENT 能流', 700, M.MONO) }), (s, t, a) => { s.n.style.opacity = M.env(t, a, 99, .8).a; s.n.lb.forEach((e, i) => M.rise(e, t, a + .3 + i * .15, 99)); s.n.pk.forEach(e => { e.style.opacity = t > a + .8 ? 1 : 0; }); flow(s.n, t, .2); M.rise(s.t, t, a + .2, 99); }],
      [c => ({ n: net(c), bars: [0, 1, 2, 3, 4].map(i => M.box(c, 1300 - 100 + i * 0, 0, {})), cap: M.box(c, 1240, 380, { width: '120px', height: '240px', border: `4px solid ${G}`, borderRadius: '16px', boxSizing: 'border-box', overflow: 'hidden' }) }),
       (s, t, a) => { s.n.style.opacity = 1; s.n.lb.forEach(e => { e.style.opacity = 1; }); flow(s.n, t, .35); if (!s.f) { s.f = M.box(s.cap, 6, 230, { width: '100px', height: '0px', background: G, borderRadius: '8px' }); } const u = M.o3((t - a) / 2.4); s.f.style.height = (220 * u) + 'px'; s.f.style.top = (230 - 220 * u) + 'px'; M.pop(s.cap, t, a, 99, { from: .6 }); }],
      [c => ({ n: net(c), num: X(c, 560, 470, 140, '#e8fff5', '24 h', 400, M.AN), sm: X(c, 566, 650, 26, '#5a8a74', 'SAMPLE 示例', 700, M.MONO) }),
       (s, t, a) => { s.n.style.opacity = 1; s.n.lb.forEach(e => { e.style.opacity = 1; }); flow(s.n, t, .5); M.hero(s.num, t, a + .2, 99); M.count(s.num, 24, t, a + .2, 1.2, v => v + ' h'); M.rise(s.sm, t, a + .6, 99); }]
    ] });
})();
