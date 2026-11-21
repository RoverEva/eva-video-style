/* T147 双景城市 Day & Night: the same skyline seen twice, split reveals. */
(function () { const M = K.T.mo, X = M.X;
  const SK = 'M0 400 V240 H80 V180 H140 V90 L180 50 L220 90 V180 H320 V220 H400 V140 H470 V220 H570 V170 L620 130 L670 170 V240 H800 V200 H880 V250 H960 V400Z';
  const sky = (c, col, lights, x) => M.svg(c, x || 480, 520, 960, 400, `<path d="${SK}" fill="${col}"/>` + (lights ? Array.from({ length: 26 }, (_, i) => `<rect x="${20 + i * 36}" y="${250 + (i * 37) % 110}" width="9" height="9" fill="#ffd27a"/>`).join('') : ''));
  M.story({ bg: '#000', sbg: ['linear-gradient(#8ecae6,#fefae0)', 'linear-gradient(#0b1026,#2b2d6e)', '#000'], tr: ['wipe', 'shutter'], ring: () => ({ color: '#ffffff', width: 6, shadow: .4 }),
    wins: [M.c(1480, 110, 320), M.c(110, 110, 320), M.c(800, 110, 320)],
    caps: [['同一座城，白天这样', 'One city — by day'], ['到了夜里，又是另一副样子', 'And at night, something else'], ['一座城，两种光', 'One city, two kinds of light']], port: { box: [0, 40, 1920, 940] },
    scenes: [
      [c => ({ s: sky(c, '#3d5a80'), sun: M.box(c, 1200, 180, { width: '140px', height: '140px', borderRadius: '50%', background: '#fff3b0', boxShadow: '0 0 60px #fff3b0' }), t: X(c, 120, 140, 110, '#1d3557', '白天') }), (s, t, a) => { M.rise(s.s, t, a + .1, 99, { dy: 120 }); M.pop(s.sun, t, a + .4, 99, { from: .3 }); M.hero(s.t, t, a + .3, 99); }],
      [c => ({ s: sky(c, '#0d0f24', 1), moon: M.box(c, 1300, 180, { width: '120px', height: '120px', borderRadius: '50%', boxShadow: 'inset -32px -8px 0 #fff1c1' }), t: X(c, 1400, 600, 110, '#ffd27a', '夜晚') }),
       (s, t, a) => { M.rise(s.s, t, a - .1, 99, { dy: 120 }); [...s.s.querySelectorAll('rect')].forEach((r, i) => { r.style.opacity = t > a + .2 + i * .05 ? 1 : 0; }); M.pop(s.moon, t, a + .2, 99, { from: .3 }); M.hero(s.t, t, a + .4, 99); }],
      [c => ({ L: M.box(c, 0, 0, { width: '960px', height: '1080px', background: 'linear-gradient(#8ecae6,#fefae0)', overflow: 'hidden' }), R: M.box(c, 960, 0, { width: '960px', height: '1080px', background: 'linear-gradient(#0b1026,#2b2d6e)', overflow: 'hidden' }), t: X(c, 560, 620, 110, '#fff', '一座城，两种光', 900, M.CN, { textShadow: '0 6px 20px rgba(0,0,0,.4)' }) }),
       (s, t, a) => { if (!s.d) { sky(s.L, '#3d5a80', 0, 0); sky(s.R, '#0d0f24', 1, -960); s.d = 1; } const u = M.io((t - a) / .8); s.L.style.transform = `translateX(${(-960 * (1 - u)).toFixed(1)}px)`; s.R.style.transform = `translateX(${(960 * (1 - u)).toFixed(1)}px)`; M.pop(s.t, t, a + .7, 99, { from: .6 }); }]
    ] });
})();
