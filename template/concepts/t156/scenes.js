/* T156 拼贴开场 Collage Open: photo-print cards toss in, stack, and the window lands on top. */
(function () { const M = K.T.mo, X = M.X, INK = '#222';
  const COL = ['#e76f51', '#2a9d8f', '#264653', '#e9c46a', '#8ab17d', '#6d597a', '#f4a261'];
  const card = (c, k, txt) => { const g = M.box(c, 0, 0, { width: '360px', height: '240px', background: '#fff', padding: '14px', boxSizing: 'border-box', boxShadow: '0 16px 30px rgba(0,0,0,.18)', transformOrigin: '50% 50%' }); M.box(g, 14, 14, { width: '332px', height: '170px', background: COL[k % 7] }); X(g, 30, 40, 44, '#fff', txt, 900); X(g, 18, 194, 24, '#555', 'EP.0' + (k + 1), 700, M.MONO); return g; };
  const toss = (g, t, a, x, y, r) => { const u = M.os((t - a) / .6); g.style.opacity = t < a ? 0 : 1; g.style.transform = `translate(${(x + (1 - u) * (x > 900 ? 900 : -900)).toFixed(1)}px, ${(y - (1 - u) * 300).toFixed(1)}px) rotate(${(r + (1 - u) * 40).toFixed(1)}deg)`; };
  M.story({ bg: '#f1ede6', sbg: ['#f1ede6', '#e8e1d5', '#f1ede6'], tr: ['shutter', 'push'], ring: () => ({ color: '#ffffff', width: 12, shadow: .3 }),
    wins: [M.q(1360, 160, 420, 520, 18), M.q(700, 200, 520, 520, 18), M.q(1360, 160, 420, 520, 18)],
    caps: [['这一季的内容，先看一眼', 'A peek at this season'], ['选题、拍摄、剪辑', 'Topics, shooting, editing'], ['第一集，现在开始', 'Episode one starts now']], port: { box: [80, 40, 1820, 840] },
    scenes: [
      [c => ({ cs: ['旅行', '美食', '幕后', '日常', '开箱'].map((n, i) => card(c, i, n)) }), (s, t, a) => { const P = [[120, 120, -6], [520, 80, 4], [920, 140, -3], [180, 470, 5], [600, 450, -4]]; s.cs.forEach((g, i) => toss(g, t, a + .2 + i * .22, ...P[i])); }],
      [c => ({ cs: ['选题', '拍摄', '剪辑'].map((n, i) => card(c, i + 2, n)) }), (s, t, a) => { const P = [[140, 200, -8], [140, 480, 6], [1300, 340, -5]]; s.cs.forEach((g, i) => toss(g, t, a - .1 + i * .25, ...P[i])); }],
      [c => ({ cs: [0, 1, 2, 3].map(i => card(c, i + 3, ['', '', '', ''][i])), t: X(c, 140, 380, 180, INK, 'OPEN 01', 400, M.AN) }),
       (s, t, a) => { const P = [[200, 120, -10], [420, 600, 8], [860, 140, 4], [900, 640, -6]]; s.cs.forEach((g, i) => toss(g, t, a - .1 + i * .12, ...P[i])); M.hero(s.t, t, a + .7, 99); }]
    ] });
})();
