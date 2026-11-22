/* T135 拍立得掉落 Polaroid Drop (vlog): instant photos drop and develop from white, pile up, a caption is handwritten. */
(function () { const M = K.T.mo, X = M.X, HW = "'Noto Sans CJK SC', cursive";
  const COL = ['#f4a261', '#2a9d8f', '#e76f51', '#8ab17d', '#6d597a', '#e9c46a'];
  const pol = (c, k, txt) => { const g = M.box(c, 0, 0, { width: '300px', height: '360px', background: '#fffdf8', padding: '18px 18px 70px', boxSizing: 'border-box', boxShadow: '0 18px 30px rgba(0,0,0,.25)', transformOrigin: '50% 50%' }); g.ph = M.box(g, 18, 18, { width: '264px', height: '264px', background: `linear-gradient(160deg, ${COL[k % 6]}, #1d3557)` }); g.wh = M.box(g, 18, 18, { width: '264px', height: '264px', background: '#f3f1ea' }); X(g, 24, 296, 30, '#333', txt, 700, HW); return g; };
  const drop = (g, t, a, x, y, r) => { const u = M.os((t - a) / .5); g.style.opacity = t > a ? 1 : 0; g.style.transform = `translate(${x}px, ${(y - 700 * (1 - Math.min(1, (t - a) / .5))).toFixed(0)}px) rotate(${(r * u).toFixed(1)}deg)`; g.wh.style.opacity = Math.max(0, 1 - (t - a - .4) / 1.2).toFixed(2); };
  M.story({ bg: '#e9e2d6', sbg: ['#e9e2d6', '#ded5c6', '#e9e2d6'], tr: ['rise', 'push'], ring: () => ({ color: '#fffdf8', width: 14, shadow: .3 }),
    wins: [M.q(1380, 160, 420, 520, 4), M.q(110, 180, 420, 500, 4), M.q(1380, 160, 420, 520, 4)],
    caps: [['周末，拍了一堆照片', 'A weekend full of photos'], ['慢慢显影', 'Slowly developing'], ['存下来的，都是好时光', 'What we keep are good times']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ p: ['海边', '早餐', '小巷'].map((n, i) => pol(c, i, n)) }), (s, t, a) => { const P = [[200, 200, -8], [560, 260, 5], [920, 180, -3]]; s.p.forEach((g, i) => drop(g, t, a + .2 + i * .45, ...P[i])); }],
      [c => ({ big: pol(c, 3, '日落 · sunset') }), (s, t, a) => { drop(s.big, t, a - .1, 900, 200, 4); s.big.style.transform += ' scale(1.5)'; }],
      [c => ({ p: ['海边', '早餐', '小巷', '日落', '朋友'].map((n, i) => pol(c, i, n)), t: X(c, 1080, 80, 60, '#3a3026', '都是好时光 ♡', 900, HW) }),
       (s, t, a) => { const P = [[140, 120, -10], [400, 300, 8], [660, 110, -4], [880, 330, 6], [240, 470, 3]]; s.p.forEach((g, i) => { drop(g, t, a - .1 + i * .18, ...P[i]); g.wh.style.opacity = 0; }); M.hero(s.t, t, a + 1.1, 99); }]
    ] });
})();
