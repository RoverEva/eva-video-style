/* T202 文字立方体 Word Cube: a 3D cube rotates face to face, each face a keyword, beside the presenter. */
(function () { const M = K.T.mo, X = M.X, CL = ['#ff4f79', '#ffb84f', '#4fc3ff', '#7bdc6b'];
  const cube = (c, x, y, S, words) => { const w = M.box(c, x, y, { width: S + 'px', height: S + 'px', perspective: '1600px' }); const g = M.box(w, 0, 0, { width: S + 'px', height: S + 'px', transformStyle: 'preserve-3d' }); g.f = words.map((wd, i) => M.box(g, 0, 0, { width: S + 'px', height: S + 'px', background: CL[i % 4], color: '#111', font: M.f(900, S * .22, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `rotateY(${i * 90}deg) translateZ(${S / 2}px)`, backfaceVisibility: 'hidden', boxShadow: 'inset 0 0 0 8px rgba(0,0,0,.08)' }, wd)); g.S = S; return g; };
  const spin = (g, t, a, per) => { const k = Math.max(0, (t - a) / per), base = Math.floor(k), f = k - base, e = f < .7 ? 0 : M.io((f - .7) / .3); g.style.transform = `translateZ(-${g.S / 2}px) rotateX(-12deg) rotateY(${(-(base + e) * 90).toFixed(1)}deg)`; };
  M.story({ bg: '#121218', sbg: ['#121218', '#16161e', '#121218'], tr: ['zoom', 'flip'], ring: () => ({ color: '#ffffff', width: 8, shadow: .4 }),
    wins: [M.q(1300, 200, 460, 560, 20), M.q(160, 200, 460, 560, 20), M.c(1400, 200, 400)],
    caps: [['四个词，讲清楚', 'Four words make it clear'], ['快、稳、美、省', 'Fast, steady, beautiful, cheap'], ['转一圈，就记住了', 'One turn and you remember']], port: { box: [60, 60, 1800, 900] },
    scenes: [
      [c => ({ q: cube(c, 360, 260, 480, ['快', '稳', '美', '省']), t: X(c, 140, 110, 60, '#fff', 'WORD CUBE · 关键词', 700, M.INTER) }), (s, t, a) => { M.pop(s.q.parentNode, t, a + .1, 99, { from: .3 }); spin(s.q, t, a + .4, .7); M.rise(s.t, t, a + .2, 99); }],
      [c => ({ q: cube(c, 900, 240, 520, ['FAST', 'STEADY', 'BEAUTY', 'VALUE']) }), (s, t, a) => { M.pop(s.q.parentNode, t, a - .1, 99, { from: .6 }); spin(s.q, t, a, .75); }],
      [c => ({ q: cube(c, 420, 240, 520, ['EVA', 'EVA', 'EVA', 'EVA']), t: X(c, 140, 110, 44, '#aaa', '转一圈，记住了', 900) }), (s, t, a) => { M.pop(s.q.parentNode, t, a - .1, 99, { from: .6 }); s.q.style.transform = `translateZ(-260px) rotateX(-12deg) rotateY(${(-(t - a) * 120).toFixed(1)}deg)`; }]
    ] });
})();
