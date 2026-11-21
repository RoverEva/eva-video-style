/* T62 Live Poll 投票条 · 10 s sample. Poll bars grow; percentages are SAMPLE results (marked). */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, P = '#6b5bff', INK = '#1c1a3a';
  M.setup({ bg: 'linear-gradient(160deg,#f2f4ff,#e4e2ff)', win: { x: 1270, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: P, width: 8, shadow: .3 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['问你一个问题', 'A quick question'], ['你更喜欢哪种开头？', 'Which opening do you prefer?'], ['评论区投出你的一票', 'Vote in the comments']]),
    build(L) { const s = {};
      s.tag = M.txt(L, 110, 80, f(700, 28, M.INTER), '#fff', 'POLL · 示例投票 SAMPLE', { background: P, padding: '8px 18px', borderRadius: '999px' });
      s.q = M.txt(L, 110, 150, f(900, 78, M.CN), INK, '你更喜欢哪种开头？');
      s.o = [['直接给结论', 'Lead with the point', 62], ['先讲一个故事', 'Start with a story', 38]].map(([c, e, v], i) => { const r = M.box(L, 110, 330 + i * 170, { width: '980px', height: '130px', borderRadius: '24px', background: '#fff', boxShadow: '0 10px 24px rgba(60,50,160,.12)', overflow: 'hidden' });
        r.bar = el(r, 'div', 'abs', { left: 0, top: 0, height: '100%', width: '0%', background: i ? '#cfc9ff' : 'linear-gradient(90deg,#8f83ff,#6b5bff)' });
        M.txt(r, 34, 22, f(900, 50, M.CN), INK, c); M.txt(r, 36, 86, f(600, 24, M.INTER), '#5d5a85', e); r.p = M.txt(r, 820, 30, f(400, 70, M.AN), INK, '0%'); r.v = v; return r; });
      s.win = M.txt(L, 110, 690, f(900, 52, M.CN), '#fff', '👑 结论派领先', { background: INK, padding: '6px 24px', borderRadius: '14px' });
      return s; },
    update(s, t) { M.pop(s.tag, t, .8, 9.2, { from: .6 }); M.hero(s.q, t, 1.0, 9.2);
      s.o.forEach((r, i) => { M.slide(r, t, 1.6 + i * .15, 9.2, { dx: -50 }); const u = M.o3((t - 3.6 - i * .1) / 1.4); r.bar.style.width = (r.v * u).toFixed(1) + '%'; r.p.textContent = Math.round(r.v * u) + '%'; });
      M.pop(s.win, t, 6.85, 9.2, { from: .5 }); } });
})();
