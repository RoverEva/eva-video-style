/* T199 粒子 logo Particle Logo (logo/text only): dot rings converge into a glowing app-icon EVA mark, then pulse. */
(function () { const M = K.T.mo, X = M.X, TL = '#3fd1c4', N = 220;
  const dots = c => Array.from({ length: N }, (_, i) => M.box(c, 0, 0, { width: '7px', height: '7px', borderRadius: '50%', background: i % 3 ? TL : '#fff' }));
  const ring = (L, t, rr, sp, k) => L.forEach((e, i) => { const ring = i % 4, an = i / N * 6.2832 * 4 + t * sp * (ring % 2 ? 1 : -1), R = rr * (1 + ring * .18) * k; e.style.transform = `translate(${(960 + Math.cos(an) * R - 3).toFixed(1)}px, ${(520 + Math.sin(an) * R * .95 - 3).toFixed(1)}px)`; e.style.opacity = (.35 + .65 * k).toFixed(2); });
  const icon = c => { const g = M.box(c, 780, 340, { width: '360px', height: '360px', borderRadius: '84px', background: '#0b0f12', border: '10px solid #fff', boxSizing: 'border-box', boxShadow: `0 0 60px ${TL}`, color: '#fff', font: M.f(500, 120, M.INTER), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' }, 'EVA'); return g; };
  M.story({ noface: true, bg: '#05080a', sbg: ['#05080a', '#06090c', '#05080a'], tr: ['zoom', 'blur'],
    caps: [['点，从四面八方来', 'Points arrive from everywhere'], ['聚成一个标志', 'They gather into a mark'], ['EVA Video Studio', 'EVA Video Studio']], port: { box: [400, 80, 1120, 880] },
    scenes: [
      [c => ({ d: dots(c) }), (s, t, a) => ring(s.d, t, 360, .4, 1.8 - .8 * M.o3((t - a) / 2.6))],
      [c => ({ d: dots(c), ic: icon(c) }), (s, t, a) => { ring(s.d, t, 300, .7, 1 - .35 * M.io((t - a) / 1.2)); M.pop(s.ic, t, a + .6, 99, { from: 0 }); }],
      [c => ({ d: dots(c), ic: icon(c), t: X(c, 660, 760, 56, '#fff', 'EVA VIDEO STUDIO', 300, M.INTER, { letterSpacing: '.2em' }) }),
       (s, t, a) => { ring(s.d, t, 300, .3, .65 + .05 * Math.sin(t * 4)); s.ic.style.opacity = 1; s.ic.style.transform = `scale(${(1 + .03 * Math.sin(t * 4)).toFixed(3)})`; s.ic.style.boxShadow = `0 0 ${(60 + 30 * Math.sin(t * 4)).toFixed(0)}px ${TL}`; M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
