/* T85 Logo Liquid 液体溅落 · 10 s logo-only sample. A drop falls, splashes, the colour pool floods the frame and reveals the mark. */
(function () { const C = EV, M = K.T.mo, f = M.f, B = '#ff4f7b', INK = '#ffffff';
  M.setup({ noface: true, bg: '#fff4f6', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['一滴，就够了', 'One drop is enough'], ['让品牌自然散开', 'Let your brand spread'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.pool = M.box(L, 960 - 1200, 360 - 1200, { width: '2400px', height: '2400px', borderRadius: '50%', background: `radial-gradient(circle, #ff6b93, ${B} 60%, #e23a66)`, transformOrigin: '50% 50%' });
      s.drop = M.svg(L, 920, 0, 80, 110, `<path d="M40 0 C 40 0, 4 54, 4 72 a36 36 0 0 0 72 0 C 76 54, 40 0, 40 0Z" fill="${B}"/>`, { transformOrigin: '50% 100%' });
      s.rings = [0, 1, 2].map(i => M.box(L, 960 - 60, 360 - 20, { width: '120px', height: '40px', borderRadius: '50%', border: `5px solid ${B}`, boxSizing: 'border-box', transformOrigin: '50% 50%' }));
      s.dots = Array.from({ length: 10 }, (_, i) => M.box(L, 950, 350, { width: '18px', height: '18px', borderRadius: '50%', background: B }));
      s.logo = M.logo(L, 790, 190, 340, INK);
      s.tag = M.txt(L, 0, 600, f(900, 56, M.CN), INK, '让品牌，自然散开', { width: '1920px', textAlign: 'center' });
      s.en = M.txt(L, 0, 690, f(700, 34, M.INTER), 'rgba(255,255,255,.85)', 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.2em' });
      return s; },
    update(s, t) { const fall = M.i2((t - .6) / .55); s.drop.style.opacity = t > .6 && t < 1.2 ? 1 : 0; s.drop.style.transform = `translateY(${(-120 + 400 * fall).toFixed(1)}px) scaleY(${(1 + .3 * fall).toFixed(3)})`;
      s.rings.forEach((r, i) => { const d = (t - 1.15 - i * .12) / .9; r.style.opacity = d > 0 && d < 1 ? (1 - d).toFixed(3) : 0; r.style.transform = `scale(${(1 + 5 * M.o3(d)).toFixed(3)})`; });
      s.dots.forEach((e, i) => { const d = t - 1.15, a = i / 10 * Math.PI - Math.PI, v = 380 + (i % 3) * 120; e.style.opacity = d > 0 && d < .8 ? (1 - d / .8).toFixed(3) : 0; e.style.transform = `translate(${(Math.cos(a) * v * d).toFixed(1)}px, ${(Math.sin(a) * v * d + 900 * d * d).toFixed(1)}px)`; });
      const p = M.io((t - 1.5) / 1.4); s.pool.style.transform = `scale(${(p * (1 - .0 * p)).toFixed(4)})`; s.pool.style.opacity = t > 1.4 ? (1 - M.i2((t - 10.1) / .25)) : 0;
      M.pop(s.logo, t, 2.7, 10.3, { from: .5 }); s.logo.style.transform += ` translateY(${(-6 * Math.sin(t * 2)).toFixed(1)}px)`;
      M.hero(s.tag, t, 3.6, 10.3, { dx: 0, dy: 24, noclip: true }); M.rise(s.en, t, 6.8, 10.3); } });
})();
