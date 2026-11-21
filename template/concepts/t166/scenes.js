/* T166 工业管线 Pipeline: pipes draw, packets flow through a tank, conveyor delivers output. */
(function () { const M = K.T.mo, X = M.X, GY = '#8a939c', Y = '#f2c14e', CY = '#4cc9f0';
  const pipes = c => M.path(c, 0, 0, 1920, 1080, 'M120 300 H520 V640 H720 M960 640 H1160 V300 H1300', GY, 34, 'stroke-linejoin="round"');
  const tank = c => { const g = M.box(c, 720, 480, { width: '240px', height: '300px', borderRadius: '30px', background: '#4a525a', overflow: 'hidden' }); g.f = M.box(g, 0, 300, { width: '240px', height: '300px', background: CY }); return g; };
  const packets = (c, n) => Array.from({ length: n }, () => M.box(c, 0, 0, { width: '60px', height: '44px', background: Y, borderRadius: '6px' }));
  M.story({ bg: '#2b2f33', sbg: ['#2b2f33', '#262a2e', '#2b2f33'], tr: ['wipe', 'push'], ring: () => ({ color: Y, width: 6, shadow: .5 }),
    wins: [M.q(1400, 200, 400, 480, 18), M.q(1400, 200, 400, 480, 18), M.c(110, 160, 360)],
    caps: [['数据，从这里流进来', 'Data flows in here'], ['处理、过滤、合并', 'Process, filter, merge'], ['最后，送上传送带', 'Then onto the conveyor']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ p: pipes(c), tk: tank(c), pk: packets(c, 5), t: X(c, 120, 140, 60, '#e6e6e6', 'PIPELINE', 400, M.AN) }),
       (s, t, a) => { M.draw(s.p, t, a, 1.4, 99); M.pop(s.tk, t, a + .4, 99, { from: .6 }); s.tk.f.style.top = (300 - 160 * M.o3((t - a - .8) / 2)) + 'px'; s.pk.forEach((e, i) => { const u = ((t - a) * .4 + i / 5) % 1; e.style.opacity = t > a + .8 ? 1 : 0; e.style.transform = `translate(${(100 + u * 380).toFixed(1)}px, 236px)`; }); M.rise(s.t, t, a + .3, 99); }],
      [c => ({ st: [['处理', 'PROCESS'], ['过滤', 'FILTER'], ['合并', 'MERGE']].map(([n, e], i) => { const g = M.box(c, 160 + i * 400, 300, { width: '340px', height: '340px', borderRadius: '30px', background: '#3a4046', border: `4px solid ${i === 1 ? Y : GY}`, boxSizing: 'border-box' }); X(g, 30, 30, 70, '#fff', n, 900); X(g, 30, 130, 30, Y, e, 700, M.MONO); g.bar = M.box(g, 30, 260, { width: '0px', height: '16px', borderRadius: '8px', background: CY }); return g; }), ar: [0, 1].map(i => M.path(c, 500 + i * 400, 450, 60, 40, 'M0 20 H50 M35 5 L50 20 L35 35', Y, 6)) }),
       (s, t, a) => { s.st.forEach((g, i) => { M.pop(g, t, a - .15 + i * .3, 99, { from: .6 }); g.bar.style.width = (280 * M.o3((t - a - .3 - i * .5) / .8)) + 'px'; }); s.ar.forEach((p, i) => M.draw(p, t, a + .4 + i * .5, .3, 99)); }],
      [c => ({ belt: M.box(c, 480, 860, { width: '1400px', height: '40px', background: 'repeating-linear-gradient(90deg,#444 0 40px,#555 40px 80px)' }), pk: packets(c, 8), t: X(c, 520, 300, 100, '#fff', '送达 ✓', 900) }),
       (s, t, a) => { s.belt.style.backgroundPosition = `${(-t * 200).toFixed(0)}px 0`; M.rise(s.belt, t, a - .1, 99, { dy: 40 }); s.pk.forEach((e, i) => { const x = ((t - a) * 200 + i * 180) % 1440; e.style.opacity = t > a ? 1 : 0; e.style.transform = `translate(${(480 + x).toFixed(1)}px, 816px)`; }); M.hero(s.t, t, a + .4, 99); }]
    ] });
})();
