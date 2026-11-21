/* T113 黑金早报 Black Gold (logo/text only). */
(function () { const M = K.T.mo, X = M.X, GD = '#d4a64a';
  const gold = { backgroundImage: 'linear-gradient(#fff4c9,#d4a64a 50%,#8a6418)', WebkitBackgroundClip: 'text', backgroundClip: 'text' };
  M.story({ noface: true, bg: '#050505', sbg: ['#050505', '#0b0905', '#050505'], tr: ['blur', 'zoom'],
    caps: [['早上好，这是今天的早报', 'Good morning — today’s brief'], ['三件事，一分钟看完', 'Three things in one minute'], ['一句话：先做最重要的那件', 'In one line: do the most important thing first']], port: { box: [200, 80, 1520, 760] },
    scenes: [
      [c => ({ t: X(c, 300, 260, 220, 'transparent', '早报', 900, M.SERIF, gold), e: X(c, 320, 540, 44, GD, 'MORNING BRIEF · 07:30', 700, M.MONO), l: [0, 1].map(i => M.path(c, 300, 520 + i * 100, 1300, 10, 'M0 5 H1300', GD, 2)) }),
       (s, t, a) => { M.hero(s.t, t, a + .3, 99, { dx: 0, dy: 40, din: .6 }); M.rise(s.e, t, a + .8, 99); s.l.forEach((p, i) => M.draw(p, t, a + .5 + i * .3, .9, 99)); }],
      [c => ({ k: [['01', '天气转凉'], ['02', '新功能上线'], ['03', '周五截止']].map(([n, w], i) => { const g = M.box(c, 260 + i * 480, 340, { width: '420px', height: '300px', border: `2px solid ${GD}`, boxSizing: 'border-box', padding: '36px' }); X(g, 36, 30, 90, 'transparent', n, 400, M.AN, gold); X(g, 36, 160, 52, '#f3e3c3', w, 900, M.SERIF); return g; }) }),
       (s, t, a) => s.k.forEach((g, i) => M.pop(g, t, a - .15 + i * .25, 99, { from: .7 }))],
      [c => ({ ls: [200, 480, 760].map(y => M.path(c, 200, 0, 1200, 1000, `M0 ${y} C 500 ${y}, 600 480, 1100 480`, GD, 3)), dot: M.box(c, 1280, 462, { width: '36px', height: '36px', borderRadius: '50%', background: GD, boxShadow: `0 0 30px ${GD}` }), t: X(c, 380, 640, 90, 'transparent', '先做最重要的那件', 900, M.SERIF, gold) }),
       (s, t, a) => { s.ls.forEach((p, i) => M.draw(p, t, a - .1 + i * .15, .9, 99)); M.pop(s.dot, t, a + .9, 99, { from: 0 }); M.hero(s.t, t, a + 1.1, 99, { dx: 0, dy: 30, noclip: true }); }]
    ] });
})();
