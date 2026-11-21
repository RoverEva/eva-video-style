/* T195 现代图文 Modern Editorial: magazine layout — big italic serif pull-quote, rule, column text, page number. */
(function () { const M = K.T.mo, X = M.X, INK = '#151515', R = '#d62828', PF = M.PF;
  M.story({ bg: '#f2f0eb', sbg: ['#f2f0eb', '#ebe7df', '#f2f0eb'], tr: ['slide', 'push'], ring: () => ({ color: '#ffffff', width: 0, shadow: .25 }),
    wins: [M.q(1080, 80, 640, 860, 4, 1.02), M.q(120, 120, 560, 760, 4, 1.02), M.q(1080, 80, 640, 860, 4, 1.02)],
    caps: [['少，但更好', 'Less, but better'], ['第一，删掉不必要的', 'One: cut what isn’t needed'], ['第二，留下最重要的', 'Two: keep what matters most']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ q: X(c, 140, 160, 150, INK, '“Less, but<br>better.”', 400, PF, { fontStyle: 'italic', lineHeight: 1.05 }), r: M.box(c, 140, 560, { width: '0px', height: '10px', background: R }), s: X(c, 140, 610, 46, INK, '少，但更好 · 观点拆解', 900), pg: X(c, 140, 900, 26, '#888', 'ISSUE 07 — P.12', 700, M.MONO) }),
       (s, t, a) => { M.hero(s.q, t, a + .2, 99); s.r.style.width = (220 * M.o3((t - a - .8) / .5)) + 'px'; M.rise(s.s, t, a + 1, 99); M.rise(s.pg, t, a + 1.2, 99); }],
      [c => ({ n: X(c, 820, 120, 260, R, '01', 400, PF, { fontStyle: 'italic' }), h: X(c, 820, 440, 80, INK, '删掉不必要的', 900), col: X(c, 824, 580, 34, '#444', '多一个镜头，不如少一个；<br>多一句话，不如留白。<br>剪掉的，都是为了留下的。', 400, M.CN, { lineHeight: 1.6 }) }),
       (s, t, a) => { M.hero(s.n, t, a - .1, 99); M.hero(s.h, t, a + .2, 99); M.rise(s.col, t, a + .5, 99); }],
      [c => ({ n: X(c, 140, 120, 260, R, '02', 400, PF, { fontStyle: 'italic' }), h: X(c, 140, 440, 80, INK, '留下最重要的', 900), st: M.path(c, 140, 560, 700, 40, 'M0 20 H680', INK, 3), pg: X(c, 140, 620, 34, '#444', '— EVA Editorial', 400, PF, { fontStyle: 'italic' }) }),
       (s, t, a) => { M.hero(s.n, t, a - .1, 99); M.hero(s.h, t, a + .2, 99); M.draw(s.st, t, a + .5, .6, 99); M.rise(s.pg, t, a + .9, 99); }]
    ] });
})();
