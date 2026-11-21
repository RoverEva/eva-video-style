/* T54 Watercolor 水彩晕染 · 10 s sample (illustrative copy). Washes bloom wet-in-wet; serif title; named colour swatches. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#3b3a46';
  const wash = (p, x, y, w, h, c, br) => M.box(p, x, y, { width: w + 'px', height: h + 'px', borderRadius: br || '48% 52% 44% 56% / 52% 46% 54% 48%', background: `radial-gradient(ellipse at 45% 40%, ${c}cc, ${c}55 55%, ${c}00 72%)`, filter: 'blur(6px)', transformOrigin: '50% 50%' });
  M.setup({ bg: '#fbf8f2', win: { x: 1250, y: 160, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 12, shadow: .18 }), port: { box: [90, 40, 1060, 760] },
    captions: M.caps([['慢慢画，慢慢生活', 'Paint slowly, live slowly'], ['今天的三种颜色', "Today's three colours"], ['你最喜欢哪一个？', 'Which is your favourite?']]),
    build(L) { const s = {};
      s.w = [[40, 20, 900, 460, '#7fc8c4'], [1100, 60, 820, 700, '#f4b59b'], [300, 560, 900, 520, '#b9a6e0']].map(a => M.bg(wash(L, ...a)));
      s.t = M.txt(L, 110, 120, f(900, 100, M.SERIF), INK, '慢慢画，慢慢生活'); s.e = M.txt(L, 116, 250, f('italic 700', 46, M.PF), '#6d6a7c', 'Paint slowly, live slowly');
      s.sw = [['晨雾', 'Mist', '#7fc8c4'], ['杏子', 'Apricot', '#f4b59b'], ['丁香', 'Lilac', '#b9a6e0']].map(([c, e, col], i) => { const g = M.box(L, 110 + i * 320, 380, { width: '280px', textAlign: 'center' });
        g.d = M.box(g, 40, 0, { width: '200px', height: '200px', position: 'relative', borderRadius: '50% 46% 52% 48%', background: `radial-gradient(circle at 40% 35%, ${col}, ${col}aa 60%, ${col}55)`, transformOrigin: '50% 50%' });
        M.txt(g, 0, 214, f(900, 44, M.SERIF), INK, c, { position: 'relative', left: 0, top: 0 }); M.txt(g, 0, 214, f('italic 700', 26, M.PF), '#6d6a7c', e, { position: 'relative', left: 0, top: 0 }); return g; });
      s.br = M.path(L, 100, 700, 700, 40, 'M6 24 C 160 6, 360 36, 690 14', '#b9a6e0', 18, 'opacity=".75"');
      return s; },
    update(s, t) { s.w.forEach((e, i) => { const a = [.5, .8, 3.5][i], u = M.o3((t - a) / 1.6); e.style.opacity = (u * (1 - M.i2((t - 9.0) / .4))).toFixed(3); e.style.transform = `scale(${(.4 + .6 * u).toFixed(3)}) rotate(${(t * 2).toFixed(1)}deg)`; });
      M.hero(s.t, t, .95, 9.2, { dx: 0, dy: 20, noclip: true }); M.rise(s.e, t, 1.35, 9.2);
      s.sw.forEach((g, i) => { M.rise(g, t, 3.6 + i * .16, 9.2, { dy: 30 }); const u = M.os((t - 3.6 - i * .16) / .5); g.d.style.transform = `scale(${(.3 + .7 * u).toFixed(3)})`; });
      M.draw(s.br, t, 6.8, .7, 9.2); if (t > 6.9) s.sw.forEach((g, i) => { g.d.style.transform = `scale(${(1 + .06 * Math.max(0, Math.sin((t - 6.9) * 3 - i))).toFixed(3)})`; }); } });
})();
