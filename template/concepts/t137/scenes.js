/* T137 网点人像 Halftone Portrait */
(function () { const M = K.T.mo, X = M.X, Y = '#ffd23f', INK = '#111';
  const ht = (c, txt, x, y, px) => X(c, x, y, px, 'transparent', txt, 400, M.AN, { backgroundImage: `radial-gradient(${INK} 45%, transparent 48%)`, backgroundSize: '14px 14px', WebkitBackgroundClip: 'text', backgroundClip: 'text', lineHeight: 1 });
  M.story({ bg: Y, sbg: [Y, '#111', '#ff5fa2'], tr: ['wipe', 'iris'], ring: () => ({ color: INK, width: 8, shadow: .3 }),
    wins: [M.c(1380, 300, 440), M.q(1300, 140, 480, 580, 0), M.c(760, 120, 400)],
    caps: [['一点一点，显出画面', 'Dot by dot, the picture appears'], ['像老报纸一样印出来', 'Printed like an old newspaper'], ['网点风，复古又醒目', 'Halftone: retro and bold']], port: { box: [80, 40, 1840, 900] },
    scenes: [
      [c => ({ t: ht(c, 'HALF', 100, 100, 320), t2: ht(c, 'TONE', 100, 420, 320), dots: M.box(c, 1380, 300, { width: '440px', height: '440px', borderRadius: '50%', backgroundImage: 'radial-gradient(rgba(255,210,63,.6) 35%, transparent 40%)', backgroundSize: '12px 12px', mixBlendMode: 'multiply' }) }),
       (s, t, a) => { M.hero(s.t, t, a + .2, 99); M.hero(s.t2, t, a + .5, 99); const u = M.o3((t - a) / 2.5); s.t.style.backgroundSize = s.t2.style.backgroundSize = `${(30 - 16 * u).toFixed(1)}px ${(30 - 16 * u).toFixed(1)}px`; s.dots.style.opacity = M.env(t, a, 3.3).a; }],
      [c => ({ ov: M.box(c, 1300, 140, { width: '480px', height: '580px', backgroundImage: 'radial-gradient(rgba(0,0,0,.55) 30%, transparent 34%)', backgroundSize: '10px 10px', mixBlendMode: 'multiply', zIndex: 60 }), t: X(c, 140, 300, 140, '#fff', '老报纸', 900, M.SERIF), e: X(c, 150, 480, 44, Y, 'PRINTED · 1 COLOUR', 700, M.MONO) }),
       (s, t, a) => { s.ov.style.display = 'none'; M.hero(s.t, t, a - .1, 99); M.rise(s.e, t, a + .3, 99); }],
      [c => ({ t: ht(c, 'POP', 140, 380, 360), cn: X(c, 1260, 520, 110, INK, '网点风'), r: Array.from({ length: 6 }, (_, i) => M.box(c, 1250 + i * 60, 680, { width: '40px', height: '40px', borderRadius: '50%', background: INK, transformOrigin: '50% 50%' })) }),
       (s, t, a) => { M.pop(s.t, t, a - .1, 99, { from: 1.4 }); M.hero(s.cn, t, a + .3, 99); s.r.forEach((e, i) => { M.pop(e, t, a + .4 + i * .06, 99, { from: 0 }); e.style.transform += ` scale(${(.4 + .6 * Math.abs(Math.sin(t * 3 + i))).toFixed(2)})`; }); }]
    ] });
})();
