/* T108 影子几何 Shadow Geometry: point light = sharp shadow; large light = umbra + penumbra. */
(function () { const M = K.T.mo, X = M.X, INK = '#3a2a1a';
  M.story({ bg: '#f4ecdc', sbg: ['#f4ecdc', '#efe2c4', '#f6efe0'], tr: ['slide', 'iris'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(120, 160, 400, 480, 26), M.c(1420, 160, 380)],
    caps: [['影子为什么有时候是虚的？', 'Why are some shadows blurry?'], ['光源越大，边缘越虚', 'The bigger the light, the softer the edge'], ['中间是本影，边上是半影', 'Umbra in the middle, penumbra at the edge']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ sun: M.box(c, 220, 160, { width: '60px', height: '60px', borderRadius: '50%', background: '#ffcc4d', boxShadow: '0 0 40px #ffcc4d' }), pole: M.box(c, 700, 380, { width: '16px', height: '320px', background: INK }),
          rays: M.svg(c, 0, 0, 1400, 900, '<path d="M250 190 L708 380 L1200 700" stroke="#b9a27e" stroke-width="3" stroke-dasharray="10 8" fill="none"/>'), sh: M.box(c, 716, 690, { width: '480px', height: '16px', background: INK, transformOrigin: '0 50%' }), t: X(c, 120, 60, 64, INK, '点光源：影子边缘很清楚', 900, M.SERIF) }),
       (s, t, a) => { M.pop(s.sun, t, a + .2, 99, { from: .2 }); M.rise(s.pole, t, a + .4, 99, { dy: 80 }); M.rise(s.rays, t, a + .7, 99, { dy: 0 }); const u = M.o3((t - a - .9) / .6); s.sh.style.transform = `scaleX(${u.toFixed(3)})`; s.sh.style.opacity = u > 0 ? 1 : 0; M.hero(s.t, t, a + .3, 99); }],
      [c => ({ lamp: M.box(c, 700, 120, { width: '380px', height: '60px', borderRadius: '30px', background: '#ffcc4d', boxShadow: '0 0 60px #ffcc4d' }), pole: M.box(c, 900, 380, { width: '16px', height: '320px', background: INK }),
          um: M.box(c, 916, 690, { width: '300px', height: '16px', background: INK }), pen: M.box(c, 916, 690, { width: '620px', height: '16px', background: 'linear-gradient(90deg, rgba(58,42,26,.9) 45%, rgba(58,42,26,0))' }), t: X(c, 640, 760, 56, INK, '大光源：边缘变虚', 900, M.SERIF) }),
       (s, t, a) => { M.slide(s.lamp, t, a - .1, 99, { dx: 200 }); M.rise(s.pole, t, a, 99); const u = M.o3((t - a - .5) / .8); s.um.style.transform = s.pen.style.transform = `scaleX(${u.toFixed(3)})`; s.um.style.transformOrigin = s.pen.style.transformOrigin = '0 50%'; M.hero(s.t, t, a + .8, 99); }],
      [c => ({ g: M.svg(c, 120, 140, 1200, 640, '<path d="M600 80 V560" stroke="#3a2a1a" stroke-width="14"/><path d="M600 560 L900 560 L600 80Z" fill="rgba(58,42,26,.7)"/><path d="M900 560 L1150 560 L600 80Z" fill="rgba(58,42,26,.25)"/><path d="M0 560 H1200" stroke="#3a2a1a" stroke-width="3"/>'),
          a1: X(c, 820, 720, 48, INK, '本影', 900, M.SERIF), a2: X(c, 1050, 720, 48, '#8a6a4a', '半影', 900, M.SERIF), t: X(c, 120, 70, 60, INK, '越远，边缘越虚', 900, M.SERIF) }),
       (s, t, a) => { M.rise(s.g, t, a - .1, 99, { dy: 40 }); M.pop(s.a1, t, a + .5, 99, { from: .5 }); M.pop(s.a2, t, a + .7, 99, { from: .5 }); M.hero(s.t, t, a + .2, 99); }]
    ] });
})();
