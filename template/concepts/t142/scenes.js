/* T142 火候 Heat & Timing: ember glow, serif title, dial + temperature × time. */
(function () { const M = K.T.mo, X = M.X, OR = '#ff6a00', CR = '#f4e3cf';
  const ember = c => Array.from({ length: 26 }, (_, i) => M.box(c, 0, 0, { width: '8px', height: '8px', borderRadius: '50%', background: i % 2 ? '#ffb347' : OR, boxShadow: `0 0 10px ${OR}` }));
  const emberU = (L, t, a) => L.forEach((e, i) => { const u = ((t - a) * .35 + i / 26) % 1; e.style.opacity = (1 - u) * M.env(t, a, 99).a; e.style.transform = `translate(${(200 + (i * 151) % 1500 + 30 * Math.sin(t * 2 + i)).toFixed(1)}px, ${(1000 - u * 700).toFixed(1)}px)`; });
  M.story({ bg: '#1e120c', sbg: ['radial-gradient(ellipse at 50% 120%,#c2410c,#1e120c 60%)', '#160d08', 'radial-gradient(ellipse at 50% 120%,#ff6a00,#1e120c 55%)'], tr: ['blur', 'zoom'], ring: () => ({ color: '#ff8c3a', width: 4, shadow: .5 }),
    wins: [M.q(1340, 120, 420, 500, 14), M.c(110, 170, 380), M.c(1440, 140, 360)],
    caps: [['好菜，看的是火候', 'Great dishes are about heat'], ['温度乘以时间', 'Temperature times time'], ['火候到了，香味就出来了', 'Get it right and the aroma follows']], port: { box: [100, 40, 1820, 840] },
    scenes: [
      [c => ({ e: ember(c), t: X(c, 160, 200, 260, CR, '火候', 900, M.SERIF), en: X(c, 170, 520, 48, '#ff8c3a', 'HEAT & TIMING', 700, M.MONO) }), (s, t, a) => { emberU(s.e, t, a); M.hero(s.t, t, a + .3, 99, { dx: 0, dy: 50, noclip: true }); M.rise(s.en, t, a + .7, 99); }],
      [c => ({ d: M.svg(c, 640, 180, 460, 460, '<circle cx="230" cy="230" r="200" fill="none" stroke="#3a2418" stroke-width="30"/><circle class="p" cx="230" cy="230" r="200" fill="none" stroke="#ff6a00" stroke-width="30" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 230 230)"/>'), n: X(c, 720, 320, 110, CR, '180°C', 400, M.AN), x: X(c, 1180, 330, 110, '#ff8c3a', '× 3 min', 400, M.AN) }),
       (s, t, a) => { M.pop(s.d, t, a - .15, 99, { from: .6 }); M.draw(s.d.querySelector('.p'), t, a + .2, 1.6, 99); M.count(s.n, 180, t, a + .2, 1.4, v => v + '°C'); M.rise(s.n, t, a + .1, 99); M.hero(s.x, t, a + 1.0, 99); }],
      [c => ({ e: ember(c), steam: [0, 1, 2].map(i => M.path(c, 700 + i * 160, 200, 120, 360, 'M60 340 C 0 260, 120 200, 60 120 C 0 60, 80 20, 60 0', '#f4e3cf', 8, 'opacity=".6"')), t: X(c, 160, 640, 76, CR, '火候到了，香味就出来了', 900, M.SERIF) }),
       (s, t, a) => { emberU(s.e, t, a); s.steam.forEach((p, i) => { M.draw(p, t, a + i * .2, 1, 99); p.parentNode.style.transform = `translateY(${(-20 * Math.sin(t * 2 + i)).toFixed(1)}px)`; }); M.hero(s.t, t, a + .4, 99); }]
    ] });
})();
