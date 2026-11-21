/* T71 Spec Table 参数对比表 · 10 s sample. Manual vs template editing; rows fill; best column glows. Values are SAMPLE (marked). */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, CY = '#3fe0c5', INK = '#e8eef7';
  const R = [['上手难度', 'Learning curve', '高', '低'], ['出片时间', 'Time to video', '数小时', '几分钟'], ['双语字幕', 'Bilingual captions', '✕', '✓'], ['风格统一', 'Consistent look', '✕', '✓']];
  M.setup({ bg: 'radial-gradient(ellipse at 30% 20%, #1b2a44, #0f1724 70%)', win: { x: 1290, y: 160, w: 470, h: 470, r: 235, o: 1, s: 1.15 }, ring: () => ({ color: CY, width: 6, glow: 'rgba(63,224,197,.4)', shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['手动剪辑 vs 模板剪辑', 'Manual vs template editing'], ['四项对比，一目了然', 'Four rows, at a glance'], ['选哪个，你说了算', 'Your call']]),
    build(L) { const s = {};
      s.t = M.txt(L, 110, 60, f(900, 64, M.CN), INK, '参数对比'); s.tag = M.txt(L, 420, 80, f(700, 22, M.INTER), '#0f1724', '示例 SAMPLE', { background: '#9fb0c8', padding: '4px 12px', borderRadius: '6px' });
      s.hl = M.box(L, 790, 160, { width: '280px', height: '560px', borderRadius: '20px', background: 'rgba(63,224,197,.12)', border: `3px solid ${CY}`, boxSizing: 'border-box' });
      s.hd = [['', 110], ['手动', 520], ['模板', 840]].map(([h, x]) => M.txt(L, x, 180, f(900, 44, M.CN), h === '模板' ? CY : INK, h));
      s.rows = R.map(([k, e, a, b], i) => { const r = M.box(L, 110, 270 + i * 110, { width: '960px', height: '96px', borderTop: '2px solid rgba(255,255,255,.12)' });
        M.txt(r, 0, 16, f(700, 38, M.CN), INK, k); M.txt(r, 0, 64, f(600, 20, M.INTER), '#8c9ab3', e); r.a = M.txt(r, 410, 22, f(900, 40, M.CN), '#ff7a7a', a); r.b = M.txt(r, 730, 22, f(900, 40, M.CN), CY, b); return r; });
      return s; },
    update(s, t) { M.hero(s.t, t, .85, 9.2); M.pop(s.tag, t, 1.1, 9.2, { from: .6 }); s.hd.forEach((h, i) => M.rise(h, t, 1.2 + i * .12, 9.2));
      s.rows.forEach((r, i) => { M.slide(r, t, 1.7 + i * .12, 9.2, { dx: -40 }); M.pop(r.a, t, 3.6 + i * .3, 9.2, { from: .4 }); M.pop(r.b, t, 3.75 + i * .3, 9.2, { from: .4 }); r.a.style.opacity *= t < 3.6 + i * .3 ? 0 : 1; });
      M.panel(s.hl, t, 6.8, 9.2, { r: 20 }); s.hl.style.boxShadow = `0 0 ${(30 + 20 * Math.sin(t * 4)).toFixed(0)}px rgba(63,224,197,.35)`; } });
})();
