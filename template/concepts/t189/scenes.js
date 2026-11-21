/* T189 光带车名 Light Ribbon (logo/text only): neon ribbons sweep in, wrap a wordmark, then a model tag. */
(function () { const M = K.T.mo, X = M.X, CL = ['#3ff0ff', '#ff2bd6', '#ffd23f'];
  const rib = (c, k) => M.path(c, 0, 0, 1920, 1080, `M-100 ${560 + k * 40} C 400 ${300 + k * 80}, 800 ${800 - k * 60}, 1200 ${480 + k * 30} S 1800 ${360 + k * 70}, 2050 ${520 - k * 20}`, CL[k], 10, `style="filter:drop-shadow(0 0 14px ${CL[k]})"`);
  const ribU = (L, t, a) => L.forEach((p, k) => { M.draw(p, t, a + k * .15, 1.2, 99); p.parentNode.style.transform = `translateY(${(30 * Math.sin(t * 1.5 + k)).toFixed(1)}px)`; });
  M.story({ noface: true, bg: '#05060d', sbg: ['#05060d', '#070814', '#05060d'], tr: ['blur', 'zoom'],
    caps: [['一道光，划过夜色', 'A ribbon of light cuts the night'], ['光，写出它的名字', 'Light writes its name'], ['IDEA · 全新车型（示例）', 'IDEA · new model (sample)']], port: { box: [200, 160, 1520, 700] },
    scenes: [
      [c => ({ r: [0, 1, 2].map(k => rib(c, k)) }), (s, t, a) => ribU(s.r, t, a + .1)],
      [c => ({ r: [0, 1, 2].map(k => rib(c, k)), w: X(c, 460, 360, 300, '#fff', 'IDEA', 200, M.INTER, { letterSpacing: '.12em', textShadow: '0 0 30px #3ff0ff' }) }),
       (s, t, a) => { s.r.forEach(p => { p.parentNode.style.opacity = 1; p.style.strokeDashoffset = 0; }); ribU(s.r, t, a - 2); const u = M.io((t - a) / 1.4); s.w.style.clipPath = `inset(0 ${(100 - 100 * u).toFixed(1)}% 0 0)`; s.w.style.opacity = 1; }],
      [c => ({ r: [0, 1, 2].map(k => rib(c, k)), w: X(c, 460, 300, 300, '#fff', 'IDEA', 200, M.INTER, { letterSpacing: '.12em', textShadow: '0 0 30px #ff2bd6' }), tag: M.box(c, 780, 680, { padding: '12px 34px', border: '2px solid #fff', borderRadius: '40px', color: '#fff', font: M.f(700, 34, M.MONO), letterSpacing: '.2em' }, 'NEW MODEL · 2026') }),
       (s, t, a) => { ribU(s.r, t, a - 2); M.pop(s.w, t, a - .1, 99, { from: 1.2 }); M.rise(s.tag, t, a + .6, 99); }]
    ] });
})();
