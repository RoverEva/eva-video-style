/* T52 Memphis 孟菲斯波普 · 10 s sample (illustrative copy). Squiggles, dots and triangles pop in; stickers on colour blobs. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#161616', PK = '#ff5fa2', Y = '#ffd23f', TL = '#2ec4b6', BL = '#3a5bff';
  M.setup({ bg: '#fff4e0', win: { x: 1250, y: 160, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: INK, width: 8, shadow: .2 }), port: { box: [90, 60, 1060, 740] },
    captions: M.caps([['周末去哪玩？', 'Where to this weekend?'], ['看展、野餐、逛市集', 'Gallery, picnic or market'], ['评论告诉我', 'Tell me in the comments']]),
    build(L) { const s = {};
      const deco = [['M0 20 Q 20 0 40 20 T 80 20 T 120 20 T 160 20', PK, 1180, 720, 170, 40], ['M0 20 Q 20 0 40 20 T 80 20 T 120 20', TL, 980, 90, 130, 40], ['M10 50 L40 0 L70 50Z', BL, 1820, 700, 80, 60], ['M10 50 L40 0 L70 50Z', Y, 60, 760, 80, 60], ['M0 20 Q 20 0 40 20 T 80 20 T 120 20', Y, 1760, 90, 130, 40]];
      s.deco = deco.map(([d, c, x, y, w, h]) => M.bg(M.path(L, x, y, w, h, d, c, 9).parentNode));
      s.dots = [[150, 690, PK], [1080, 640, TL], [1830, 420, Y], [960, 330, BL]].map(([x, y, c]) => M.bg(M.box(L, x, y, { width: '34px', height: '34px', borderRadius: '50%', background: c, transformOrigin: '50% 50%' })));
      s.t = M.txt(L, 110, 110, f(900, 110, M.CN), INK, '周末去哪玩？', { textShadow: `8px 8px 0 ${PK}` });
      s.st = [['看展', 'Gallery', Y, -6], ['野餐', 'Picnic', TL, 4], ['逛市集', 'Market', PK, -3]].map(([c, e, col, r], i) => { const g = M.box(L, 0, 0, { width: '290px', height: '200px', borderRadius: '46% 54% 40% 60% / 55% 45% 55% 45%', background: col, border: `6px solid ${INK}`, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' });
        M.txt(g, 0, 0, f(900, 60, M.CN), INK, c, { position: 'static' }); M.txt(g, 0, 0, f(700, 26, M.INTER), INK, e, { position: 'static' }); return { g, x: 110 + i * 330, y: 340, r }; });
      s.u = M.path(L, 110, 600, 560, 40, 'M4 20 Q 30 2 56 20 T 108 20 T 160 20 T 212 20 T 264 20 T 316 20 T 368 20 T 420 20 T 472 20 T 524 20', BL, 8);
      s.cta = M.txt(L, 110, 660, f(900, 64, M.CN), INK, '评论告诉我 ↓');
      return s; },
    update(s, t) { s.deco.forEach((e, i) => M.pop(e, t, .6 + i * .1, 9.25, { from: .2, base: `rotate(${(Math.sin(t + i) * 6).toFixed(1)}deg)` }));
      s.dots.forEach((e, i) => M.pop(e, t, .8 + i * .1, 9.25, { from: 0 }));
      M.pop(s.t, t, 1.0, 9.2, { from: .6 });
      s.st.forEach(({ g, x, y, r }, i) => M.slap(g, t, 3.6 + i * .18, 9.2, { x, y, r, rf: (i - 1) * 12 }));
      M.draw(s.u, t, 6.8, .5, 9.2); M.hero(s.cta, t, 7.0, 9.2); } });
})();
