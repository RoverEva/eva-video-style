/* T168 蓝图剖面 Section View: blueprint grid, a cup outline draws, section cut reveals the vacuum layer, heat path arrow. */
(function () { const M = K.T.mo, X = M.X, W = '#e6f1ff', BL = '#0f3d7a', OR = '#ff9f43';
  const grid = c => M.box(c, -400, -400, { width: '2720px', height: '1880px', backgroundImage: 'linear-gradient(rgba(255,255,255,.08) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.08) 2px,transparent 2px)', backgroundSize: '60px 60px' });
  M.story({ bg: BL, sbg: [BL, '#0d3570', BL], tr: ['wipe', 'zoom'], ring: () => ({ color: W, width: 4, shadow: .4 }),
    wins: [M.q(1400, 180, 400, 480, 14), M.q(1400, 180, 400, 480, 14), M.c(120, 180, 360)],
    caps: [['画一张蓝图', 'Draw a blueprint'], ['剖开看，中间是真空层', 'Cut it open: a vacuum layer'], ['热，走不出去', 'Heat can’t get out']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ g: grid(c), cup: M.path(c, 300, 180, 600, 700, 'M40 20 H560 L500 680 H100Z', W, 6), d1: M.path(c, 300, 900, 600, 40, 'M40 20 H560 M40 5 V35 M560 5 V35', W, 3), dt: X(c, 520, 920, 30, W, '84 mm', 700, M.MONO), t: X(c, 1000, 90, 60, W, 'BLUEPRINT 蓝图', 700, M.MONO) }),
       (s, t, a) => { M.drift(s.g, t, 10); M.draw(s.cup, t, a, 1.4, 99); M.draw(s.d1, t, a + 1, .6, 99); M.rise(s.dt, t, a + 1.3, 99); M.rise(s.t, t, a + .4, 99); }],
      [c => ({ g: grid(c), cup: M.path(c, 300, 180, 600, 700, 'M40 20 H560 L500 680 H100Z', W, 6), in: M.path(c, 300, 180, 600, 700, 'M80 40 H520 L466 650 H134Z', W, 4, 'stroke-dasharray="14 10"'), cut: M.box(c, 280, 160, { width: '6px', height: '740px', background: OR, boxShadow: `0 0 20px ${OR}` }), l: X(c, 980, 720, 44, W, 'VACUUM LAYER 真空层', 700, M.MONO) }),
       (s, t, a) => { s.cup.style.opacity = 1; s.cup.querySelector ? 0 : 0; M.draw(s.in, t, a + .4, 1, 99); s.cut.style.opacity = M.env(t, a, a + 1.4).a; s.cut.style.transform = `translateX(${(640 * M.io((t - a) / 1.2)).toFixed(1)}px)`; M.slide(s.l, t, a + .9, 99, { dx: 80 }); }],
      [c => ({ g: grid(c), cup: M.path(c, 700, 180, 600, 700, 'M40 20 H560 L500 680 H100Z', W, 6), hp: M.path(c, 700, 300, 900, 300, 'M300 200 C 420 160, 520 60, 760 40', OR, 8), hd: M.path(c, 1440, 310, 60, 60, 'M0 0 L40 30 L0 60', OR, 8), l: X(c, 1180, 230, 44, OR, 'HEAT PATH 热路 ✕', 700, M.MONO) }),
       (s, t, a) => { s.cup.style.opacity = 1; M.draw(s.hp, t, a + .2, 1, 99); M.draw(s.hd, t, a + 1.1, .2, 99); M.rise(s.l, t, a + 1.2, 99); }]
    ] });
})();
