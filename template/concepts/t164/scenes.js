/* T164 创业时间线 Founder Timeline (boss): a horizontal timeline draws, year pins drop with milestones, camera pans to today. Sample story. */
(function () { const M = K.T.mo, X = M.X, INK = '#1d1d1f', GD = '#c8a35a';
  const MS = [['2019', '一个人，一台电脑'], ['2021', '第一个客户'], ['2023', '团队 20 人'], ['2026', '今天']];
  const line = (c, off) => { const g = M.box(c, 0, 0, { width: '3200px', height: '1080px' }); g.ln = M.path(g, 0, 0, 3200, 1080, 'M100 600 H3100', INK, 6); g.pins = MS.map(([y, n], i) => { const p = M.box(g, 300 + i * 800, 0, {}); M.box(p, -18, 582, { width: '36px', height: '36px', borderRadius: '50%', background: i === 3 ? GD : INK, border: '6px solid #f6f3ee', boxSizing: 'border-box' }); p.y = X(p, -80, 430, 90, i === 3 ? GD : INK, y, 400, M.AN); p.n = X(p, -80, 650, 44, '#555', n, 900); return p; }); g.style.transform = `translateX(${-off}px)`; return g; };
  M.story({ bg: '#f6f3ee', sbg: ['#f6f3ee', '#efebe4', '#f6f3ee'], tr: ['slide', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1380, 120, 420, 300, 20, 1.1), M.q(1380, 120, 420, 300, 20, 1.1), M.c(1460, 100, 320)],
    caps: [['七年前，我一个人开始', 'Seven years ago I started alone'], ['一步一步，走到今天（示例）', 'Step by step to today (sample)'], ['下一站，和你一起', 'Next stop — with you']], port: { box: [60, 60, 1800, 920] },
    scenes: [
      [c => ({ g: line(c, 0), t: X(c, 140, 120, 80, INK, '创业时间线', 900) }), (s, t, a) => { M.draw(s.g.ln, t, a + .1, 2.4, 99); s.g.pins.forEach((p, i) => { M.rise(p, t, a + .5 + i * .6, 99, { dy: -60 }); }); s.g.style.transform = `translateX(${(-300 * M.io((t - a) / 3)).toFixed(0)}px)`; M.hero(s.t, t, a + .2, 99); }],
      [c => ({ g: line(c, 300) }), (s, t, a) => { s.g.ln.parentNode.style.opacity = 1; s.g.ln.style.strokeDashoffset = 0; s.g.ln.setAttribute('stroke-dashoffset', 0); s.g.pins.forEach(p => { p.style.opacity = 1; }); s.g.style.transform = `translateX(${(-300 - 1500 * M.io((t - a + .1) / 2.6)).toFixed(0)}px)`; }],
      [c => ({ nx: X(c, 160, 300, 140, GD, 'NEXT →', 400, M.AN), t: X(c, 170, 500, 64, INK, '下一站，和你一起', 900), sg: M.path(c, 160, 640, 700, 140, 'M10 100 C 60 20, 110 20, 120 80 C 130 130, 180 120, 220 60 C 260 10, 300 40, 320 90 C 340 130, 420 110, 520 60 L680 70', INK, 5) }),
       (s, t, a) => { M.hero(s.nx, t, a - .1, 99); M.rise(s.t, t, a + .4, 99); M.draw(s.sg, t, a + .9, 1, 99); }]
    ] });
})();
