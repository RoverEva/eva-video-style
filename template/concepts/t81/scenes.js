/* T81 Galaxy 星空宇宙 · 10 s sample (illustrative copy). Twinkling star field, drifting nebula, constellation draws, shooting star. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#eef1ff';
  const P = [[180, 520], [330, 430], [470, 480], [600, 380], [760, 430], [900, 340]];
  M.setup({ bg: 'radial-gradient(ellipse at 30% 30%, #1b1f4b, #070816 70%)', win: { x: 1280, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: 'rgba(200,210,255,.85)', width: 4, glow: 'rgba(140,160,255,.6)', shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['每个想法，都是一颗星', 'Every idea is a star'], ['连起来，就是你的星座', 'Connect them into your constellation'], ['许个愿吧', 'Make a wish']]),
    build(L) { const s = {};
      s.neb = [['#6b4bff', 300, 300, 700], ['#ff4fa3', 1400, 800, 800], ['#2fd1ff', 900, 700, 500]].map(([c, x, y, r]) => M.bg(M.box(L, x - r / 2, y - r / 2, { width: r + 'px', height: r + 'px', borderRadius: '50%', background: c, filter: 'blur(120px)', opacity: .35 })));
      s.st = Array.from({ length: 70 }, (_, i) => M.bg(M.box(L, (i * 271) % 1920, (i * 157) % 1080, { width: (i % 5 ? 3 : 5) + 'px', height: (i % 5 ? 3 : 5) + 'px', borderRadius: '50%', background: '#fff' })));
      s.t = M.txt(L, 110, 110, f(900, 84, M.CN), INK, '每个想法，都是一颗星'); s.e = M.txt(L, 114, 215, f('italic 700', 36, M.PF), '#aab3e8', 'Every idea is a star');
      s.ln = M.path(L, 0, 0, 1200, 800, 'M' + P.map(p => p.join(' ')).join(' L'), 'rgba(200,210,255,.8)', 3);
      s.cs = P.map(([x, y]) => M.box(L, x - 10, y - 10, { width: '20px', height: '20px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 18px #9fb0ff', transformOrigin: '50% 50%' }));
      s.nm = M.txt(L, 560, 560, f(900, 48, M.CN), INK, '灵感座 · Inspiration', { textShadow: '0 0 20px rgba(160,180,255,.7)' });
      s.sh = M.box(L, 0, 0, { width: '260px', height: '4px', borderRadius: '2px', background: 'linear-gradient(90deg, rgba(255,255,255,0), #fff)', transformOrigin: '100% 50%' });
      s.wish = M.txt(L, 110, 660, f(900, 64, M.CN), INK, '许个愿吧 ✦');
      return s; },
    update(s, t) { s.neb.forEach((e, i) => { e.style.transform = `translate(${(40 * Math.sin(t * .3 + i * 2)).toFixed(1)}px, ${(30 * Math.cos(t * .25 + i)).toFixed(1)}px)`; });
      s.st.forEach((e, i) => { e.style.opacity = (.3 + .7 * Math.abs(Math.sin(t * (1 + i % 3) + i))).toFixed(2); });
      M.hero(s.t, t, .9, 9.2); M.rise(s.e, t, 1.25, 9.2);
      s.cs.forEach((e, i) => M.pop(e, t, 3.5 + i * .14, 9.2, { from: 0 })); M.draw(s.ln, t, 3.7, 1.3, 9.2); M.hero(s.nm, t, 5.1, 9.2);
      const d = (t - 6.75) / .7; s.sh.style.opacity = d > 0 && d < 1 ? (1 - d).toFixed(3) : 0; s.sh.style.transform = `translate(${(900 + 600 * d - 260).toFixed(1)}px, ${(60 + 260 * d).toFixed(1)}px) rotate(23deg)`;
      M.hero(s.wish, t, 7.1, 9.2); } });
})();
