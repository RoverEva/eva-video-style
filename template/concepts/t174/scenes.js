/* T174 牌桌战术 Card Tactics: felt table, three cards deal and flip to reveal key points. */
(function () { const M = K.T.mo, X = M.X, FE = '#1f5f3a', R = '#d62828';
  const card = (c, rank, txt) => { const g = M.box(c, 0, 0, { width: '260px', height: '360px', transformOrigin: '50% 50%', transformStyle: 'preserve-3d' }); g.back = M.box(g, 0, 0, { width: '260px', height: '360px', borderRadius: '20px', background: `repeating-linear-gradient(45deg,#7a1020 0 12px,#9a1a2e 12px 24px)`, border: '10px solid #fff', boxSizing: 'border-box' }); g.front = M.box(g, 0, 0, { width: '260px', height: '360px', borderRadius: '20px', background: '#fff', boxShadow: '0 16px 30px rgba(0,0,0,.35)' }); X(g.front, 20, 14, 50, rank === 'A' ? '#111' : R, rank, 900, M.INTER); X(g.front, 40, 150, 56, '#111', txt, 900); return g; };
  const flip = (g, u) => { const ang = 180 * u; g.back.style.display = ang < 90 ? '' : 'none'; g.front.style.display = ang >= 90 ? '' : 'none'; g.style.transform += ` rotateY(${(ang < 90 ? ang : ang - 180).toFixed(1)}deg)`; };
  M.story({ bg: FE, sbg: ['radial-gradient(ellipse at 50% 40%,#2e7d4f,#14402a)', 'radial-gradient(ellipse at 50% 40%,#2e7d4f,#14402a)', 'radial-gradient(ellipse at 50% 40%,#2e7d4f,#14402a)'], tr: ['slide', 'zoom'], ring: () => ({ color: '#f4e3b2', width: 8, shadow: .4 }),
    wins: [M.c(1440, 120, 360), M.c(1440, 120, 360), M.q(110, 180, 440, 520, 20)],
    caps: [['这局，我只讲三个点', 'Three points, that’s all'], ['先看第一张牌', 'First card first'], ['三张牌，三个点', 'Three cards, three points']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ cs: ['A', 'K', 'Q'].map((r, i) => card(c, r, '要点 ' + (i + 1))) }),
       (s, t, a) => s.cs.forEach((g, i) => { const u = M.o3((t - a - .3 - i * .25) / .6); g.style.opacity = t > a + .3 + i * .25 ? 1 : 0; g.style.transform = `translate(${(1800 - (1800 - 300 - i * 300) * u).toFixed(0)}px, ${(800 - 560 * u).toFixed(0)}px) rotate(${((i - 1) * 8 + 200 * (1 - u)).toFixed(1)}deg)`; flip(g, 0); })],
      [c => ({ cs: ['A', 'K', 'Q'].map((r, i) => card(c, r, '要点 ' + (i + 1))) }),
       (s, t, a) => s.cs.forEach((g, i) => { g.style.opacity = 1; g.style.transform = `translate(${300 + i * 300}px, 240px) rotate(${(i - 1) * 8}deg) scale(${i === 0 ? 1 + .15 * M.o3((t - a) / .6) : 1})`; flip(g, i === 0 ? M.io((t - a - .3) / .6) : 0); })],
      [c => ({ cs: ['A', 'K', 'Q'].map((r, i) => card(c, r, '要点 ' + (i + 1))), t: X(c, 1300, 760, 70, '#f4e3b2', '三张牌，三个点', 900) }),
       (s, t, a) => { s.cs.forEach((g, i) => { g.style.opacity = 1; g.style.transform = `translate(${660 + i * 220}px, 260px) rotate(${(i - 1) * 10}deg)`; flip(g, i === 0 ? 1 : M.io((t - a - .1 - i * .4) / .5)); }); M.hero(s.t, t, a + 1.1, 99); }]
    ] });
})();
