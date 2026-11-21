/* T92 Quote Card 金句 · 10 s text-only sample (original line, no presenter). Giant quote mark draws, words resolve one by one. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#2a1d14', ACC = '#d1572e';
  const W1 = ['把', '一件事', '做到', '极致，'], W2 = ['就是', '品牌。'];
  M.setup({ noface: true, bg: 'linear-gradient(150deg,#fbeee0,#f2d9c2)', port: { box: [200, 60, 1520, 760] },
    captions: M.caps([['今天的一句话', "Today's line"], ['把一件事做到极致，就是品牌', "Do one thing really well — that's a brand"], ['收藏，慢慢想', 'Save it, think it over']]),
    build(L) { const s = {};
      s.q = M.txt(L, 196, -40, f(900, 340, M.PF), ACC, '“', { lineHeight: 1, transformOrigin: '30% 60%' });
      const row = (ws, y, px) => { let x = 220; return ws.map(w => { const e = M.txt(L, x, y, f(900, px, M.SERIF), INK, w); x += [...w].length * px * 1.0 + 6; return e; }); };
      s.w1 = row(W1, 260, 110); s.w2 = row(W2, 400, 110);
      s.en = M.txt(L, 226, 560, f('italic 700', 44, M.PF), '#7a5a44', 'Do one thing to the extreme — that is a brand.');
      s.rule = M.path(L, 226, 650, 200, 10, 'M2 5H190', ACC, 4); s.by = M.txt(L, 450, 632, f(700, 32, M.CN), '#7a5a44', '创作手记 · Creator notes');
      return s; },
    update(s, t) { M.pop(s.q, t, .6, 10.3, { from: .4, din: .45 });
      [...s.w1, ...s.w2].forEach((e, i) => M.hero(e, t, 1.1 + i * .28 + (i >= 4 ? 2.3 : 0), 10.3, { dx: 0, dy: 26, noclip: true, din: .45 }));
      M.rise(s.en, t, 5.3, 10.3); M.draw(s.rule, t, 6.8, .4, 10.3); M.rise(s.by, t, 7.0, 10.3); } });
})();
