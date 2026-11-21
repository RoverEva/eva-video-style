/* T124 证据图示 Evidence Icons: target → evidence stack → balance tips. */
(function () { const M = K.T.mo, X = M.X, G = '#2f855a', INK = '#333';
  M.story({ bg: '#efece6', sbg: ['#efece6', '#e2eee6', '#efece6'], tr: ['wipe', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(1380, 160, 400, 480, 26), M.c(1440, 150, 380)],
    caps: [['先想清楚：目标是什么', 'First: what is the goal?'], ['再摆证据，一条一条来', 'Then the evidence, one by one'], ['比较之后，再下结论', 'Compare, then conclude']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ tg: M.svg(c, 300, 160, 500, 500, `<circle cx="250" cy="250" r="230" fill="none" stroke="${G}" stroke-width="22"/><circle cx="250" cy="250" r="140" fill="none" stroke="${G}" stroke-width="22"/><circle cx="250" cy="250" r="50" fill="${G}"/>`, { transformOrigin: '50% 50%' }),
          ar: M.svg(c, 0, 0, 900, 600, '<path d="M0 0 L520 400" stroke="#333" stroke-width="12"/><path d="M490 360 L530 410 L470 400Z" fill="#333"/>'), t: X(c, 860, 360, 120, INK, '目标') }),
       (s, t, a) => { M.pop(s.tg, t, a + .2, 99, { from: .3 }); const u = M.os((t - a - .9) / .4); s.ar.style.opacity = u > 0 ? 1 : 0; s.ar.style.transform = `translate(${(-300 * (1 - Math.min(1, u))).toFixed(1)}px, ${(-230 * (1 - Math.min(1, u))).toFixed(1)}px)`; M.hero(s.t, t, a + 1.2, 99); }],
      [c => ({ cs: [0, 1, 2].map(i => { const g = M.card(c, 200 + i * 40, 200 + i * 60, 600, 360, '#fff', { border: `4px solid ${G}` }); X(g, 40, 40, 64, G, '证据 ' + (i + 1)); return g; }), t: X(c, 1000, 340, 110, INK, '证据') }),
       (s, t, a) => { s.cs.forEach((g, i) => M.slap(g, t, a - .1 + i * .3, 99, { x: 0, y: 0, r: (i - 1) * 3 })); M.hero(s.t, t, a + .8, 99); }],
      [c => ({ beam: M.svg(c, 360, 200, 800, 500, `<path d="M400 40 V460 M260 460 H540" stroke="#333" stroke-width="14"/>`), arm: M.svg(c, 360, 200, 800, 500, `<path d="M60 60 H740" stroke="#333" stroke-width="12"/><path d="M60 60 L0 220 H120Z M740 60 L680 220 H800Z" fill="${G}"/>`, { transformOrigin: '400px 60px' }), t: X(c, 1180, 640, 100, INK, '比较') }),
       (s, t, a) => { M.rise(s.beam, t, a - .1, 99); M.rise(s.arm, t, a, 99); s.arm.style.transform += ` rotate(${(-12 * M.os((t - a - .7) / .6)).toFixed(2)}deg)`; M.hero(s.t, t, a + .5, 99); }]
    ] });
})();
