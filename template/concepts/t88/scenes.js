/* T88 Logo Ink Drop 墨滴晕开 · 10 s logo-only sample. Ink blooms in water on rice paper; the mark appears in the ink; brush underline. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#141414', PAPER = '#f3eee2';
  M.setup({ noface: true, bg: PAPER, port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['一滴墨，慢慢晕开', 'A drop of ink, slowly spreading'], ['东方的留白，也是品牌', 'Space is part of the brand'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.blobs = [[960, 330, 520, 0], [880, 300, 380, .25], [1050, 380, 420, .45], [960, 420, 300, .7]].map(([x, y, r, dl]) => { const b = M.box(L, x - r / 2, y - r / 2, { width: r + 'px', height: r + 'px', borderRadius: '47% 53% 50% 50% / 52% 46% 54% 48%', background: `radial-gradient(circle, ${INK} 35%, rgba(20,20,20,.75) 55%, rgba(20,20,20,0) 72%)`, filter: 'blur(6px)', transformOrigin: '50% 50%' }); b.dl = dl; return b; });
      s.logo = M.logo(L, 810, 180, 300, PAPER);
      s.tag = M.txt(L, 0, 600, f(900, 60, M.SERIF), INK, '留白，也是品牌', { width: '1920px', textAlign: 'center' });
      s.br = M.path(L, 700, 690, 520, 40, 'M6 26 C 120 6, 300 34, 510 12', INK, 14, 'opacity=".85"');
      s.seal = M.txt(L, 1230, 600, f(900, 40, M.SERIF), PAPER, 'EVA', { background: '#b8292f', padding: '6px 10px', borderRadius: '4px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { s.blobs.forEach(b => { const u = M.o3((t - .6 - b.dl) / 2.2); b.style.opacity = (Math.min(1, (t - .6 - b.dl) * 4) * (1 - M.i2((t - 10.1) / .25))).toFixed(3); b.style.transform = `scale(${(.05 + .95 * u).toFixed(3)}) rotate(${(t * 6).toFixed(1)}deg)`; });
      M.pop(s.logo, t, 2.4, 10.3, { from: .85, din: .6 }); M.hero(s.tag, t, 3.6, 10.3, { dx: 0, dy: 20, noclip: true }); M.draw(s.br, t, 4.1, .6, 10.3);
      M.pop(s.seal, t, 6.85, 10.3, { from: 1.5, base: 'rotate(-6deg)' }); } });
})();
