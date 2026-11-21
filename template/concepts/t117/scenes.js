/* T117 热成像体温 Thermal (general health info; not medical advice). */
(function () { const M = K.T.mo, X = M.X;
  const heat = 'radial-gradient(circle at 30% 50%,#fff36b,#ff7b00 15%,#e5004f 32%,#5b00a8 58%,#120024 78%)';
  M.story({ bg: '#120024', sbg: [heat, '#120024', 'linear-gradient(135deg,#1c0638,#3b0a57)'], tr: ['blur', 'iris'], ring: () => ({ color: '#fff36b', width: 5, shadow: .5 }),
    wins: [M.c(1440, 140, 380), M.q(1380, 160, 400, 480, 26), M.c(760, 90, 380)],
    caps: [['发烧了？先看体温', 'Feverish? Check the number first'], ['超过 37.3°C，一般算发热', 'Above 37.3 °C usually counts as a fever'], ['多喝水、多休息，高烧不退要就医', 'Rest, drink water; see a doctor if it stays high']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ g: M.grid(c, 'rgba(255,255,255,.12)', 80), t: X(c, 120, 120, 54, '#fff', 'TEMP', 700, M.MONO), n: X(c, 120, 190, 220, '#fff', '36.5°', 400, M.AN), sc: M.box(c, 120, 680, { width: '700px', height: '22px', background: 'linear-gradient(90deg,#120024,#5b00a8,#e5004f,#ff7b00,#fff36b)', borderRadius: '11px' }) }),
       (s, t, a) => { M.drift(s.g, t, 6); M.rise(s.t, t, a + .2, 99); M.hero(s.n, t, a + .4, 99, { dx: 0, dy: 40 }); const v = (36.5 + 1.4 * M.o3((t - a - .6) / 2)).toFixed(1); s.n.textContent = v + '°'; M.panel(s.sc, t, a + .6, 99, { r: 11 }); }],
      [c => ({ ru: M.box(c, 300, 180, { width: '60px', height: '640px', background: 'linear-gradient(#fff36b,#e5004f,#5b00a8)', borderRadius: '30px' }), ticks: [36, 37, 38, 39, 40].map((v, i) => X(c, 390, 780 - i * 150, 40, '#e9d8ff', v + '°C', 700, M.MONO)),
          mk: M.box(c, 280, 780 - 1.3 * 150 + 10, { width: '100px', height: '8px', background: '#fff' }), lb: X(c, 640, 380, 72, '#fff', '37.3°C 以上'), lb2: X(c, 644, 480, 40, '#ffb3d1', '一般算发热 · 仅供参考') }),
       (s, t, a) => { M.rise(s.ru, t, a - .15, 99, { dy: 80 }); s.ticks.forEach((e, i) => M.rise(e, t, a + i * .08, 99)); M.slide(s.mk, t, a + .6, 99, { dx: -60 }); M.hero(s.lb, t, a + .7, 99); M.rise(s.lb2, t, a + 1.0, 99); }],
      [c => ({ tips: [['💧', '多喝水'], ['🛏', '多休息'], ['🏥', '高烧不退，及时就医']].map(([i2, s2], k) => { const g = M.card(c, 200 + k * 500, 560, 460, 140, 'rgba(255,255,255,.08)', { border: '2px solid rgba(255,255,255,.25)', display: 'flex', alignItems: 'center', gap: '20px', padding: '0 30px', boxSizing: 'border-box' });
          X(g, 0, 0, 52, '#fff', i2, 400, M.INTER, { position: 'static' }); X(g, 0, 0, 38, '#fff', s2, 900, M.CN, { position: 'static' }); return g; }), d: X(c, 200, 740, 26, '#b9a3d9', '仅供参考，不构成医疗建议') }),
       (s, t, a) => { s.tips.forEach((g, i) => M.pop(g, t, a - .1 + i * .22, 99, { from: .6 })); M.rise(s.d, t, a + .9, 99); }]
    ] });
})();
