/* T163 一条线 One Line (logo/text only): a single line draws peaks, becomes a chart, ends as a signature. */
(function () { const M = K.T.mo, X = M.X, INK = '#111', R = '#e63946';
  const ln = (c, d, w) => M.path(c, 0, 0, 1920, 1080, d, INK, w || 6);
  M.story({ noface: true, bg: '#fff', sbg: ['#fff', '#fafafa', '#fff'], tr: ['slide', 'wipe'],
    caps: [['一条线', 'One line'], ['画出起伏', 'Drawing ups and downs'], ['也画出名字', 'And drawing a name']], port: { box: [100, 120, 1720, 800] },
    scenes: [
      [c => ({ l: ln(c, 'M80 640 H400 L520 280 L640 640 H760 C 820 640, 840 420, 900 420 S 980 640, 1040 640 H1200 V240 H1360 V640 H1500 C 1560 640, 1600 460, 1660 460 S 1760 640, 1840 640'), d: M.box(c, 0, 0, { width: '30px', height: '30px', borderRadius: '50%', background: R }), t: X(c, 80, 800, 44, INK, 'ONE LINE · NINE LIVES', 700, M.MONO) }),
       (s, t, a) => { const u = M.io((t - a) / 2.4); M.draw(s.l, t, a, 2.4, 99); const L = s.l.getTotalLength ? s.l.getTotalLength() : 0, p = L ? s.l.getPointAtLength(L * u) : { x: 0, y: 0 }; s.d.style.transform = `translate(${(p.x - 15).toFixed(1)}px, ${(p.y - 15).toFixed(1)}px)`; s.d.style.opacity = M.env(t, a, 99).a; M.rise(s.t, t, a + .6, 99); }],
      [c => ({ ax: ln(c, 'M200 820 H1720 M200 820 V200', 3), l: ln(c, 'M200 760 C 400 740, 520 600, 700 620 S 1000 380, 1200 420 S 1500 220, 1720 240', 8), n: X(c, 1500, 140, 90, R, '+68%', 400, M.AN) }),
       (s, t, a) => { M.draw(s.ax, t, a - .2, .6, 99); s.l.setAttribute('stroke', R); M.draw(s.l, t, a + .2, 1.6, 99); M.hero(s.n, t, a + 1.4, 99); M.count(s.n, 68, t, a + 1.4, .8, v => '+' + v + '%'); }],
      [c => ({ l: ln(c, 'M360 600 C 420 380, 520 380, 520 520 C 520 640, 420 660, 440 560 C 470 430, 620 420, 640 560 C 650 640, 700 640, 740 520 L 800 640 L 860 500 C 900 440, 980 460, 960 560 C 950 620, 1000 640, 1060 560 C 1120 460, 1220 460, 1220 560 C 1220 640, 1300 640, 1560 520', 7), u: ln(c, 'M360 700 H1560', 3), t: X(c, 360, 760, 40, INK, 'EVA · SIGNATURE', 700, M.MONO) }),
       (s, t, a) => { M.draw(s.l, t, a - .1, 1.8, 99); M.draw(s.u, t, a + 1.5, .5, 99); M.rise(s.t, t, a + 1.7, 99); }]
    ] });
})();
