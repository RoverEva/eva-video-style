/* T44 Chalkboard 黑板粉笔 · 10 s sample (illustrative copy). Chalk writing; a felt eraser wipes beat 1 away; chalk diagram. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, CH = '#f3f0e4', Y = '#ffe58a';
  const ch = (p, x, y, px, txt, col) => M.txt(p, x, y, f(900, px, M.CN), col || CH, txt, { textShadow: '0 0 3px rgba(255,255,255,.35)', opacity: .95 });
  M.setup({ bg: '#23362b', win: { x: 1240, y: 160, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: '#8a5a2b', width: 14, shadow: .5 }), port: { box: [90, 60, 1080, 740] },
    captions: M.caps([['今天只讲一件事', 'Just one lesson today'], ['说话，先说结论', 'Lead with the conclusion'], ['下课！', 'Class dismissed!']]),
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'radial-gradient(rgba(255,255,255,.05) 1px, transparent 1.5px), radial-gradient(ellipse at 30% 30%, rgba(255,255,255,.07), transparent 60%)', backgroundSize: '7px 7px, 100% 100%' }));
      s.g1 = M.box(L, 0, 0, { width: '1200px', height: '1080px' });
      s.t1 = ch(s.g1, 110, 120, 120, '今日一课'); s.e1 = M.txt(s.g1, 116, 270, f(700, 40, M.INTER), Y, "TODAY'S LESSON"); s.u1 = M.path(s.g1, 110, 330, 620, 30, 'M4 16 C 180 6, 400 26, 610 10', CH, 7);
      s.t2 = ch(L, 110, 90, 84, '说话，先说结论'); s.e2 = M.txt(L, 114, 200, f(700, 34, M.INTER), Y, 'Lead with the conclusion');
      s.bx = [['结论', 'Point'], ['理由', 'Why'], ['例子', 'Example']].map(([c, e], i) => { const g = M.box(L, 110 + i * 330, 330, {});
        g.p = M.path(g, 0, 0, 260, 150, 'M8 10 Q 130 2 252 8 Q 258 75 250 142 Q 130 148 6 142 Q 2 75 8 10Z', CH, 5); ch(g, 60, 34, 56, c, i ? CH : Y); M.txt(g, 64, 104, f(700, 26, M.INTER), '#cfd8cf', e); return g; });
      s.ar = [0, 1].map(i => M.path(L, 380 + i * 330, 385, 70, 40, 'M4 20 H60 M44 6 L62 20 L44 34', CH, 5));
      s.ring = M.path(L, 90, 300, 300, 210, 'M150 10 C 270 10, 300 110, 260 160 C 210 210, 60 205, 20 150 C -10 100, 30 14, 160 18', Y, 6);
      s.bye = ch(L, 110, 600, 96, '下课！', Y);
      s.er = M.box(L, 0, 0, { width: '190px', height: '96px', background: 'linear-gradient(#c9a777 0 60%, #3a3a3a 60%)', borderRadius: '10px', boxShadow: '0 10px 20px rgba(0,0,0,.4)' });
      return s; },
    update(s, t) { M.hero(s.t1, t, .9, 9.2, { dx: -30 }); M.rise(s.e1, t, 1.25, 9.2); M.draw(s.u1, t, 1.5, .5, 9.2);
      /* eraser pass 3.15–3.75 clears beat 1 left→right */
      const u = M.io((t - 3.15) / .6), ex = -200 + 1300 * u; s.er.style.opacity = t > 3.1 && t < 3.85 ? 1 : 0;
      s.er.style.transform = `translate(${ex.toFixed(1)}px, ${(150 + 40 * Math.sin(u * 18)).toFixed(1)}px) rotate(-8deg)`;
      s.g1.style.clipPath = t < 3.15 ? '' : `inset(0 0 0 ${Math.max(0, ex + 120).toFixed(1)}px)`;
      M.hero(s.t2, t, 3.6, 9.2, { dx: -30 }); M.rise(s.e2, t, 3.85, 9.2);
      s.bx.forEach((g, i) => { M.draw(g.p, t, 4.1 + i * .35, .4, 9.2); M.rise(g, t, 4.1 + i * .35, 9.2, { dy: 14 }); });
      s.ar.forEach((a, i) => M.draw(a, t, 4.45 + i * .35, .25, 9.2));
      M.draw(s.ring, t, 6.8, .5, 9.2); M.pop(s.bye, t, 7.4, 9.2, { from: .6 }); } });
})();
