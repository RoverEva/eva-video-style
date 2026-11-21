/* T78 Notebook 作业本红笔 · 10 s sample (illustrative copy). Grid paper, red margin, blue-ink sum; red pen corrects it, ticks, 100 circled. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, BL = '#1f3f9e', R = '#e12d2d';
  M.setup({ bg: '#fdfdf8', win: { x: 1280, y: 160, w: 480, h: 540, r: 20, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['错题本，第三题', 'Mistake notebook, question three'], ['错了不怕，改过来', "Mistakes are fine — fix them"], ['满分！', 'Full marks!']]),
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'linear-gradient(rgba(70,120,220,.16) 2px, transparent 2px), linear-gradient(90deg, rgba(70,120,220,.16) 2px, transparent 2px)', backgroundSize: '48px 48px' }));
      s.mg = M.bg(M.box(L, 80, 0, { width: '4px', height: '1080px', background: 'rgba(225,45,45,.5)' }));
      s.t = M.txt(L, 130, 80, f(900, 64, M.CN), BL, '错题本 · 第 3 题'); s.e = M.txt(L, 134, 168, f(700, 28, M.INTER), '#6b7fb8', 'MISTAKE NOTEBOOK · Q3');
      s.eq = M.txt(L, 130, 280, f(700, 110, M.MONO), BL, '3 × 7 = 24');
      s.x = M.path(L, 700, 280, 130, 130, 'M14 14 L116 116 M116 14 L14 116', R, 10);
      s.fix = M.txt(L, 860, 290, f(700, 100, M.MONO), R, '21', { transform: 'rotate(-6deg)' });
      s.rows = ['3 × 6 = 18', '3 × 8 = 24'].map((q, i) => { const r = M.txt(L, 130, 430 + i * 100, f(700, 72, M.MONO), BL, q); r.k = M.path(L, 620, 430 + i * 100, 90, 90, 'M10 46 L36 72 L82 14', R, 9); return r; });
      s.score = M.txt(L, 820, 520, f(700, 110, M.MONO), R, '100', { transform: 'rotate(-8deg)' }); s.sc = M.path(L, 780, 500, 300, 190, 'M160 10 C 280 10, 300 100, 250 150 C 200 190, 60 185, 20 140 C -10 100, 40 14, 170 16', R, 7);
      s.u = M.path(L, 820, 650, 260, 40, 'M4 20 C 80 6, 170 30, 250 12 M30 34 C 100 24, 170 40, 230 28', R, 6);
      return s; },
    update(s, t) { M.hero(s.t, t, .85, 9.2); M.rise(s.e, t, 1.1, 9.2); M.hero(s.eq, t, 1.5, 9.2, { dx: -30 });
      M.draw(s.x, t, 3.6, .35, 9.2); M.hero(s.fix, t, 4.0, 9.2, { base: 'rotate(-6deg)', dx: 0, dy: -20 });
      s.rows.forEach((r, i) => { M.rise(r, t, 4.6 + i * .3, 9.2); M.draw(r.k, t, 5.2 + i * .3, .25, 9.2); });
      M.pop(s.score, t, 6.85, 9.2, { from: 1.5, base: 'rotate(-8deg)' }); M.draw(s.sc, t, 7.1, .5, 9.2); M.draw(s.u, t, 7.55, .4, 9.2); } });
})();
