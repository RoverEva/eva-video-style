/* T51 Bauhaus 包豪斯几何 · 10 s sample (illustrative copy). Primary shapes assemble, regroup into a labelled row, then turn slowly. */
(function () { const C = EV, M = K.T.mo, f = M.f, R = '#d92b2b', B = '#1f4fb4', Y = '#f2b705', INK = '#151515';
  const A = [[170, 120, 0], [460, 60, 0], [700, 150, 0]], Bp = [[110, 130, 0], [450, 130, 0], [790, 130, 0]];
  M.setup({ bg: '#f3ead8', win: { x: 1240, y: 160, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: INK, width: 8, shadow: .25 }), port: { box: [90, 40, 1060, 760] },
    captions: M.caps([['一堂“少即是多”的设计课', 'A lesson in less'], ['形状、颜色、秩序', 'Shape, colour, order'], ['好看，也要好用', 'Beautiful and useful']]),
    build(L) { const s = {};
      s.sh = [M.svg(L, 0, 0, 280, 280, `<circle cx="140" cy="140" r="140" fill="${R}"/>`, { transformOrigin: '50% 50%' }), M.svg(L, 0, 0, 260, 260, `<rect width="260" height="260" fill="${B}"/>`, { transformOrigin: '50% 50%' }), M.svg(L, 0, 0, 300, 270, `<path d="M150 0 L300 270 L0 270Z" fill="${Y}"/>`, { transformOrigin: '50% 60%' })];
      s.lb = [['形', 'Shape'], ['色', 'Colour'], ['序', 'Order']].map(([c, e], i) => M.txt(L, Bp[i][0] + 70, 440, f(900, 54, M.CN), INK, `${c} ${e}`));
      s.t = M.txt(L, 110, 560, f(900, 80, M.CN), INK, '形式追随功能'); s.e = M.txt(L, 114, 660, f(700, 32, M.INTER), '#555', 'Form follows function', { letterSpacing: '.08em' });
      s.ok = M.txt(L, 640, 690, f(900, 52, M.CN), '#fff', '好看，也好用', { background: R, padding: '8px 22px' });
      return s; },
    update(s, t) { const k = M.io((t - 3.5) / .7);
      s.sh.forEach((e, i) => { const v = M.env(t, .8 + i * .14, 9.2, .4), x = A[i][0] + (Bp[i][0] - A[i][0]) * k, y = A[i][1] + (Bp[i][1] - A[i][1]) * k;
        e.style.opacity = v.a; e.style.transform = `translate(${x.toFixed(1)}px, ${(y + 80 * (1 - v.e)).toFixed(1)}px) rotate(${((1 - v.e) * (i - 1) * 90 + (t > 6.7 ? (t - 6.7) * (i - 1) * 8 : 0)).toFixed(1)}deg) scale(${(.85 + .15 * v.e).toFixed(3)})`; });
      s.lb.forEach((e, i) => M.rise(e, t, 4.1 + i * .14, 9.2)); M.hero(s.t, t, 1.4, 9.2); M.rise(s.e, t, 1.7, 9.2); M.pop(s.ok, t, 6.9, 9.2, { from: .5 }); } });
})();
