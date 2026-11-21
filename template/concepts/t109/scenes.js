/* T109 火星蓝暮 Blue Dusk: orange Martian day → blue sunset; fine dust scatters blue light around the sun. */
(function () { const M = K.T.mo, X = M.X;
  const dunes = (c, a, b) => M.svg(c, -100, 640, 2200, 460, `<path d="M0 120 C 400 20, 700 200, 1100 90 S 1800 30, 2200 110 V460 H0Z" fill="${a}"/><path d="M0 220 C 500 150, 1000 300, 2200 190 V460 H0Z" fill="${b}"/>`);
  M.story({ bg: '#7a3416', sbg: ['linear-gradient(#e7a06a,#b4572a)', 'linear-gradient(#0d1636,#223a77 60%,#c4622d)', 'linear-gradient(#0b0f1e,#14204a)'], tr: ['blur', 'push'], ring: () => ({ color: '#ffd7b0', width: 6, shadow: .4 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 30), M.c(1440, 150, 360)],
    caps: [['火星的天空，白天偏橙', 'Mars skies are orange by day'], ['可是日落时，是蓝的', 'But sunsets there are blue'], ['细尘把蓝光散在太阳四周', 'Fine dust scatters blue light around the sun']], port: { box: [100, 40, 1820, 900] },
    scenes: [
      [c => ({ d: dunes(c, '#c4622d', '#8a3f1b'), sun: M.box(c, 900, 160, { width: '120px', height: '120px', borderRadius: '50%', background: '#fff3d6', boxShadow: '0 0 60px #ffd29a' }), t: X(c, 110, 120, 80, '#fff4e8', '火星的白天') }),
       (s, t, a) => { M.drift(s.d, t, 12); M.pop(s.sun, t, a + .3, 99, { from: .4 }); M.hero(s.t, t, a + .5, 99); }],
      [c => ({ d: dunes(c, '#4a2412', '#2a140a'), glow: M.box(c, 720, 340, { width: '480px', height: '480px', borderRadius: '50%', background: 'radial-gradient(circle,#e6f4ff 0 8%,#6fb4ff 22%,rgba(60,120,220,.4) 45%,transparent 70%)' }), t: X(c, 640, 120, 80, '#dff0ff', '日落：天空变蓝') }),
       (s, t, a) => { M.drift(s.d, t, 12); const u = M.o3((t - a) / 2); s.glow.style.opacity = M.env(t, a - .2, 99, .6).a; s.glow.style.transform = `translateY(${(120 - 140 * u).toFixed(1)}px) scale(${(.7 + .3 * u).toFixed(3)})`; M.hero(s.t, t, a + .4, 99); }],
      [c => ({ sun: M.box(c, 860, 400, { width: '70px', height: '70px', borderRadius: '50%', background: '#f4fbff' }), dots: Array.from({ length: 40 }, (_, i) => M.box(c, 0, 0, { width: '10px', height: '10px', borderRadius: '50%', background: '#c49a6c' })),
          ar: Array.from({ length: 8 }, (_, i) => M.path(c, 895 - 260, 435 - 260, 520, 520, `M260 260 L${260 + Math.cos(i * .785) * 230} ${260 + Math.sin(i * .785) * 230}`, '#6fb4ff', 6)), t: X(c, 110, 110, 62, '#dff0ff', '尘埃把蓝光“推”到太阳周围') }),
       (s, t, a) => { M.pop(s.sun, t, a - .1, 99, { from: .3 }); s.dots.forEach((e, i) => { const ang = i * 2.39, r = 160 + (i * 37) % 240; e.style.opacity = M.env(t, a + .1 + i * .01, 99).a; e.style.transform = `translate(${(895 + Math.cos(ang + t * .2) * r).toFixed(1)}px, ${(435 + Math.sin(ang + t * .2) * r).toFixed(1)}px)`; });
         s.ar.forEach((p, i) => M.draw(p, t, a + .5 + i * .06, .5, 99)); M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
