/* T127 线框都市 Wireframe City */
(function () { const M = K.T.mo, X = M.X, CY = '#3ff0ff', MG = '#ff2bd6';
  const city = (c, n, sc) => Array.from({ length: n }, (_, i) => { const x = 80 + i * (1760 / n), h = 160 + (i * 61) % 340, w = 1760 / n - 30; return M.path(c, 0, 0, 1920, 1080, `M${x} 900 V${900 - h} L${x + w / 2} ${880 - h} L${x + w} ${900 - h} V900 M${x + w / 2} ${880 - h} V880`, i % 2 ? MG : CY, 3 * (sc || 1)); });
  M.story({ bg: '#070712', sbg: ['#070712', '#0b0b1e', '#05050f'], tr: ['zoom', 'push'], ring: () => ({ color: MG, width: 4, glow: 'rgba(255,43,214,.5)', shadow: .5 }),
    wins: [M.c(1500, 100, 320), M.q(110, 160, 380, 460, 20), M.c(1440, 140, 380)],
    caps: [['一座城，跑在数据上', 'A city that runs on data'], ['每条街，都是一条数据线', 'Every street is a data line'], ['这就是数字城市', 'This is the digital city']], port: { box: [60, 40, 1880, 920] },
    scenes: [
      [c => ({ b: city(c, 10), st: M.path(c, 0, 0, 1920, 1080, 'M0 900 H1920 M960 900 L0 1080 M960 900 L1920 1080', CY, 2), t: X(c, 100, 100, 44, CY, 'THE CITY RUNS ON DATA', 700, M.MONO) }),
       (s, t, a) => { s.b.forEach((p, i) => M.draw(p, t, a + .1 + i * .08, .7, 99)); M.draw(s.st, t, a, .6, 99); M.rise(s.t, t, a + .4, 99); }],
      [c => ({ g: M.box(c, 0, 0, { width: '1920px', height: '1080px', transformOrigin: '60% 70%' }), pulses: [] }),
       (s, t, a) => { if (!s.b) { s.b = city(s.g, 8, 1.5); s.pulses = Array.from({ length: 14 }, (_, i) => M.box(s.g, 0, 0, { width: '14px', height: '14px', borderRadius: '50%', background: i % 2 ? CY : MG, boxShadow: '0 0 14px currentColor', color: i % 2 ? CY : MG })); }
         s.b.forEach((p, i) => M.draw(p, t, a - .2 + i * .05, .5, 99)); s.g.style.transform = `scale(${(1 + .25 * M.io((t - a) / 3)).toFixed(4)})`;
         s.pulses.forEach((e, i) => { const u = ((t - a) * .5 + i / 14) % 1; e.style.transform = `translate(${(500 + u * 1400).toFixed(1)}px, ${(900 - 10 * Math.sin(i)).toFixed(1)}px)`; e.style.opacity = t > a ? 1 : 0; }); }],
      [c => ({ nodes: Array.from({ length: 9 }, (_, i) => M.box(c, 300 + (i % 3) * 360, 220 + Math.floor(i / 3) * 180, { width: '40px', height: '40px', borderRadius: '50%', border: `4px solid ${CY}`, boxShadow: `0 0 20px ${CY}` })),
          ln: M.path(c, 0, 0, 1920, 1080, 'M320 240 L680 420 L1040 240 L1040 600 L680 420 L320 600 Z M680 420 L680 240 M680 420 L680 600', MG, 3), t: X(c, 300, 720, 110, '#fff', '数字城市', 900, M.CN, { textShadow: `0 0 30px ${CY}` }) }),
       (s, t, a) => { s.nodes.forEach((e, i) => M.pop(e, t, a - .1 + i * .07, 99, { from: 0 })); M.draw(s.ln, t, a + .4, 1, 99); M.hero(s.t, t, a + .8, 99, { dx: 0, dy: 30 }); }]
    ] });
})();
