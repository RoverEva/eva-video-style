/* T74 Spotlight Stage 聚光舞台 · 10 s sample (illustrative copy). Dark stage, sweeping cones converge, curtains frame the finale. */
(function () { const C = EV, M = K.T.mo, f = M.f, GOLD = '#f6c453', INK = '#fff6e0';
  const cone = (p, x) => M.box(p, x - 260, -80, { width: '520px', height: '1000px', background: 'linear-gradient(180deg, rgba(255,240,200,.55), rgba(255,240,200,0) 90%)', clipPath: 'polygon(46% 0, 54% 0, 100% 100%, 0 100%)', filter: 'blur(14px)', transformOrigin: '50% 0', mixBlendMode: 'screen' });
  M.setup({ bg: 'radial-gradient(ellipse at 50% 100%, #2a1a12, #060404 60%)', win: { x: 1280, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: GOLD, width: 8, glow: 'rgba(246,196,83,.5)', shadow: .6 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['灯光，请就位', 'Lights, please'], ['舞台准备好了', 'The stage is set'], ['今晚的主角，是你', "Tonight's star is you"]]),
    build(L) { const s = {};
      s.floor = M.bg(M.box(L, 160, 700, { width: '1600px', height: '300px', borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(255,220,160,.22), transparent 70%)' }));
      s.c1 = M.bg(cone(L, 300)); s.c2 = M.bg(cone(L, 1000));
      s.t = M.txt(L, 110, 200, f(900, 110, M.CN), INK, '今晚的主角', { textShadow: '0 0 30px rgba(246,196,83,.5)' }); s.e = M.txt(L, 116, 340, f('italic 700', 44, M.PF), GOLD, 'Tonight’s star');
      s.w = [['灯光', 'Light'], ['舞台', 'Stage'], ['你', 'You']].map(([c, e], i) => M.txt(L, 110 + i * 300, 470, f(900, 64, M.CN), i === 2 ? GOLD : INK, `${c}`, { textAlign: 'left' }));
      s.we = [['Light'], ['Stage'], ['You']].map(([e], i) => M.txt(L, 114 + i * 300, 555, f(700, 26, M.INTER), '#b9a88a', e.toUpperCase(), { letterSpacing: '.2em' }));
      s.cl = M.bg(M.box(L, -40, 0, { width: '260px', height: '1080px', background: 'repeating-linear-gradient(90deg,#7a0c12 0 40px,#a8141c 40px 70px,#7a0c12 70px 100px)', boxShadow: '10px 0 30px rgba(0,0,0,.6)' }));
      s.cr = M.bg(M.box(L, 1700, 0, { width: '260px', height: '1080px', background: 'repeating-linear-gradient(90deg,#7a0c12 0 40px,#a8141c 40px 70px,#7a0c12 70px 100px)', boxShadow: '-10px 0 30px rgba(0,0,0,.6)' }));
      return s; },
    update(s, t) { const sw = (k, ph) => { const conv = M.io((t - 6.7) / .8); return (1 - conv) * 22 * Math.sin(t * 1.3 + ph) + conv * k; };
      s.c1.style.opacity = s.c2.style.opacity = M.env(t, .5, 9.3, .6).a; s.c1.style.transform = `rotate(${sw(-28, 0).toFixed(2)}deg)`; s.c2.style.transform = `rotate(${sw(16, 2).toFixed(2)}deg)`;
      M.hero(s.t, t, 1.0, 9.2, { dx: 0, dy: 30 }); M.rise(s.e, t, 1.4, 9.2);
      s.w.forEach((e, i) => M.pop(e, t, 3.6 + i * .3, 9.2, { from: .5 })); s.we.forEach((e, i) => M.rise(e, t, 3.75 + i * .3, 9.2));
      const cu = M.os((t - 6.75) / .6), cx = 1 - M.i2((t - 9.0) / .3); s.cl.style.transform = `translateX(${(-260 * (1 - cu) - 260 * (1 - cx)).toFixed(1)}px)`; s.cr.style.transform = `translateX(${(260 * (1 - cu) + 260 * (1 - cx)).toFixed(1)}px)`;
      s.cl.style.opacity = s.cr.style.opacity = t > 6.75 ? 1 : 0; } });
})();
