/* T89 Logo 3D Flip 立体翻转 · 10 s logo-only sample. Extruded mark (stacked layers, preserve-3d) spins in and settles; floor reflection. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, B = '#5b4bff';
  M.setup({ noface: true, bg: 'linear-gradient(180deg,#eef0ff,#d6d9f5)', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['换个角度看品牌', 'See your brand from a new angle'], ['有厚度，才立得住', 'Depth makes it stand'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.sc = M.box(L, 760, 130, { width: '400px', height: '400px', perspective: '1400px' });
      s.rig = el(s.sc, 'div', 'abs', { left: 0, top: 0, width: '400px', height: '400px', transformStyle: 'preserve-3d' });
      for (let i = 14; i >= 0; i--) { const lay = el(s.rig, 'div', 'abs', { left: 0, top: 0, width: '400px', height: '400px', borderRadius: '96px', background: i ? `hsl(246, 70%, ${30 + i}%)` : `linear-gradient(140deg,#7a6bff,${B})`, transform: `translateZ(${-i * 3}px)` });
        if (!i) M.txt(lay, 0, 120, f(400, 150, M.AN), '#fff', 'EVA', { width: '400px', textAlign: 'center', lineHeight: 1 }); }
      s.shadow = M.box(L, 790, 560, { width: '340px', height: '50px', borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(40,30,120,.35), transparent 70%)', transformOrigin: '50% 50%' });
      s.tag = M.txt(L, 0, 630, f(900, 56, M.CN), '#1f1a4d', '有厚度，才立得住', { width: '1920px', textAlign: 'center' });
      s.en = M.txt(L, 0, 715, f(700, 32, M.INTER), B, 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.2em' });
      return s; },
    update(s, t) { const v = M.env(t, .6, 10.3, .4), spin = M.o3((t - .6) / 2.2), idle = t > 2.8 ? 18 * Math.sin((t - 2.8) * 1.2) : 0;
      s.sc.style.opacity = v.a; s.rig.style.transform = `rotateY(${(-540 * (1 - spin) + idle).toFixed(2)}deg) rotateX(${(10 * Math.sin(t * .8)).toFixed(2)}deg) translateY(${(-80 * (1 - M.os((t - .6) / .8))).toFixed(1)}px)`;
      s.shadow.style.opacity = v.a; s.shadow.style.transform = `scaleX(${(.7 + .3 * Math.abs(Math.cos((-540 * (1 - spin) + idle) / 57.3))).toFixed(3)})`;
      M.hero(s.tag, t, 3.6, 10.3, { dx: 0, dy: 24, noclip: true }); M.rise(s.en, t, 6.8, 10.3); } });
})();
