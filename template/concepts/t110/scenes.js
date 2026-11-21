/* T110 声音拐弯 Sound Lines: by day sound rises away; at night a warm layer bends it back down (temperature inversion). */
(function () { const M = K.T.mo, X = M.X, CY = '#3ff0ff', OR = '#ffb37a';
  const waves = (c, bend) => [0, 1, 2, 3].map(i => M.path(c, 0, 0, 1900, 900, bend ? `M180 760 Q ${700 + i * 60} ${330 - i * 30}, ${1300 + i * 80} 760` : `M180 760 Q ${360 + i * 40} ${520 - i * 120}, ${500 + i * 60} ${-40 - i * 40}`, CY, 6 - i));
  const src = (c, x) => M.box(c, x - 18, 742, { width: '36px', height: '36px', borderRadius: '50%', background: CY, boxShadow: `0 0 20px ${CY}` });
  M.story({ bg: '#0d2a52', sbg: ['linear-gradient(#5aa3e0,#1b4f8a)', '#081a3a', '#050f24'], tr: ['wipe', 'zoom'], ring: () => ({ color: CY, width: 4, shadow: .4 }),
    wins: [M.c(1440, 140, 380), M.q(1360, 150, 400, 480, 30), M.c(760, 90, 380)],
    caps: [['为什么夜里声音传得更远？', 'Why does sound carry farther at night?'], ['上面暖、下面冷，声音被折回来', 'Warm air above bends sound back down'], ['所以远处也听得见', 'So it reaches far away']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ s: src(c, 180), w: waves(c, 0), t: X(c, 600, 120, 70, '#fff', '白天：声音往上跑') }), (s, t, a) => { M.pop(s.s, t, a + .2, 99, { from: .2 }); s.w.forEach((p, i) => M.draw(p, t, a + .4 + i * .2, .8, 99)); M.hero(s.t, t, a + .3, 99); }],
      [c => ({ band: M.box(c, 0, 220, { width: '1920px', height: '120px', background: `linear-gradient(90deg, transparent, rgba(255,140,60,.45), transparent)` }), bl: X(c, 120, 240, 34, OR, '暖空气层 WARM LAYER', 700, M.MONO), s: src(c, 180), w: waves(c, 1), ear: X(c, 1280, 700, 60, '#fff', '👂') }),
       (s, t, a) => { M.panel(s.band, t, a - .1, 99); M.rise(s.bl, t, a + .2, 99); M.pop(s.s, t, a, 99, { from: .2 }); s.w.forEach((p, i) => M.draw(p, t, a + .3 + i * .2, .9, 99)); M.pop(s.ear, t, a + 1.4, 99, { from: .3 }); }],
      [c => ({ s: src(c, 180), w: waves(c, 1), far: X(c, 1500, 640, 120, '#fff', '👂'), t: X(c, 200, 120, 80, '#fff', '远处，也听得见'), dist: M.path(c, 180, 860, 1500, 20, 'M0 10 H1450', OR, 4, 'stroke-dasharray=".02 .015"') }),
       (s, t, a) => { M.pop(s.s, t, a - .1, 99, { from: .2 }); s.w.forEach((p, i) => { M.draw(p, t, a + i * .15, .7, 99); p.style.opacity = (.5 + .5 * Math.sin(t * 4 - i)).toFixed(2); }); M.pop(s.far, t, a + .8, 99, { from: .3 }); M.hero(s.t, t, a + .2, 99); M.rise(s.dist, t, a + .5, 99); }]
    ] });
})();
