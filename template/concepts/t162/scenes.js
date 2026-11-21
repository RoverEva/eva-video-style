/* T162 机芯咬合 Gear Train (logo/text only): meshing gears turn at ratio, escapement tick, logo hub. */
(function () { const M = K.T.mo, X = M.X, GD = '#c9a45c', GR = '#8a8f98';
  const gear = (r, n, col) => { const pts = []; for (let i = 0; i < n * 2; i++) { const a = i / (n * 2) * 6.2832, rr = i % 2 ? r : r * 1.14; pts.push(`${(r * 1.2 + Math.cos(a) * rr).toFixed(1)},${(r * 1.2 + Math.sin(a) * rr).toFixed(1)}`); } return `<polygon points="${pts.join(' ')}" fill="${col}"/><circle cx="${r * 1.2}" cy="${r * 1.2}" r="${r * .32}" fill="#0d0d10"/>`; };
  const G = (c, x, y, r, n, col) => { const g = M.svg(c, x - r * 1.2, y - r * 1.2, r * 2.4, r * 2.4, gear(r, n, col), { transformOrigin: '50% 50%' }); g.r = r; return g; };
  M.story({ noface: true, bg: '#0d0d10', sbg: ['#0d0d10', '#101014', '#0d0d10'], tr: ['iris', 'zoom'],
    caps: [['每一个齿，都刚好咬合', 'Every tooth meets its match'], ['大齿轮慢，小齿轮快', 'Big gear slow, small gear fast'], ['精密，来自配合', 'Precision comes from teamwork']], port: { box: [300, 40, 1320, 900] },
    scenes: [
      [c => ({ a: G(c, 760, 520, 200, 20, GD), b: G(c, 1110, 340, 110, 11, GR), d: G(c, 1150, 680, 130, 13, GR), t: X(c, 120, 80, 72, GD, 'ESCAPEMENT', 400, M.INTER) }),
       (s, t, a) => { const w = (t - a) * 30; [[s.a, 1], [s.b, -200 / 110], [s.d, -200 / 130]].forEach(([g, k], i) => { M.pop(g, t, a + i * .15, 99, { from: .3 }); g.style.transform += ` rotate(${(w * k).toFixed(1)}deg)`; }); M.hero(s.t, t, a + .5, 99); }],
      [c => ({ a: G(c, 600, 540, 280, 28, GD), b: G(c, 1110, 540, 160, 16, GR), l1: X(c, 300, 140, 40, GD, '× 1', 400, M.AN), l2: X(c, 1060, 300, 40, GR, '× 1.75', 400, M.AN) }),
       (s, t, a) => { const w = (t - a) * 40; M.pop(s.a, t, a - .15, 99, { from: .6 }); M.pop(s.b, t, a, 99, { from: .6 }); s.a.style.transform += ` rotate(${w.toFixed(1)}deg)`; s.b.style.transform += ` rotate(${(-w * 1.75 + 6).toFixed(1)}deg)`; M.rise(s.l1, t, a + .5, 99); M.rise(s.l2, t, a + .7, 99); }],
      [c => ({ a: G(c, 960, 500, 260, 26, GD), hub: M.box(c, 880, 420, { width: '160px', height: '160px', borderRadius: '50%', background: '#0d0d10', border: `4px solid ${GD}`, color: GD, font: M.f(400, 54, M.AN), display: 'flex', alignItems: 'center', justifyContent: 'center' }, 'EVA'), t: X(c, 640, 90, 54, '#e8dcc0', '精密，来自配合', 900) }),
       (s, t, a) => { M.pop(s.a, t, a - .1, 99, { from: .5 }); const tick = Math.floor((t - a) * 2) * 6 + 6 * M.os(((t - a) * 2) % 1); s.a.style.transform += ` rotate(${tick.toFixed(1)}deg)`; M.pop(s.hub, t, a + .3, 99, { from: 1.5 }); M.hero(s.t, t, a + .6, 99); }]
    ] });
})();
