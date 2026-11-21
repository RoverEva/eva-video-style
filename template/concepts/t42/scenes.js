/* T42 Swiss Grid 瑞士网格 · 10 s sample (illustrative copy). International-style grid; red block; numbered cells. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, RED = '#e30613', INK = '#111';
  M.setup({ bg: '#f4f1ea', win: { x: 1180, y: 140, w: 580, h: 640, r: 24, o: 1, s: 1.15 }, ring: () => ({ color: INK, width: 6, shadow: .25 }), port: { box: [90, 60, 1040, 740] },
    captions: M.caps([['好设计，从网格开始', 'Good design starts with a grid'], ['对齐、留白、对比', 'Align, space, contrast'], ['简单，但不随便', 'Simple, never careless']]),
    build(L) { const s = {};
      s.grid = M.bg(M.svg(L, 0, 0, 1920, 1080, Array.from({ length: 13 }, (_, i) => `<path d="M${96 + i * 144} 0V1080" stroke="rgba(0,0,0,.09)" stroke-width="2" pathLength="1" stroke-dasharray="1 1"/>`).join('')));
      s.gl = [...s.grid.querySelectorAll('path')];
      s.red = M.box(L, 96, 70, { width: '528px', height: '300px', background: RED });
      s.num = M.txt(L, 124, 84, f(400, 230, M.AN), '#fff', '01', { lineHeight: 1 });
      s.t = M.txt(L, 96, 400, f(900, 96, M.CN), INK, '先有秩序');
      s.e = M.txt(L, 100, 520, f(700, 30, M.INTER), INK, 'ORDER FIRST — INTERNATIONAL STYLE', { letterSpacing: '.06em' });
      s.cells = [['02', '对齐', 'Align'], ['03', '留白', 'Space'], ['04', '对比', 'Contrast']].map(([n, c, e], i) => { const b = M.box(L, 96 + i * 336, 600, { width: '312px', height: '180px', borderTop: `8px solid ${i === 1 ? RED : INK}`, padding: '14px 12px 0', boxSizing: 'border-box' });
        el(b, 'div', '', { font: f(700, 26, M.MONO), color: RED }, n); el(b, 'div', '', { font: f(900, 58, M.CN), color: INK }, c); el(b, 'div', '', { font: f(600, 24, M.INTER), color: '#555' }, e); return b; });
      return s; },
    update(s, t) { s.gl.forEach((p, i) => M.draw(p, t, .5 + i * .04, .6, 9.3));
      M.panel(s.red, t, .85, 9.2, { din: .45 }); M.hero(s.num, t, 1.05, 9.2, { dx: 0, dy: 70 });
      M.hero(s.t, t, 1.35, 9.2); M.rise(s.e, t, 1.6, 9.2);
      s.cells.forEach((b, i) => M.slide(b, t, 3.6 + i * .15, 9.2, { dx: 0, dy: 50 }));
      s.cells.forEach((b, i) => { const k = Math.max(0, 1 - Math.abs(t - (7.0 + i * .5)) / .35); b.style.background = `rgba(227,6,19,${(.12 * k).toFixed(3)})`; }); } });
})();
