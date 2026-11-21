/* T148 霓虹雨夜 Neon Rain: rain streaks, wet reflections, cyan/gold outlined towers. */
(function () { const M = K.T.mo, X = M.X, CY = '#3ff0ff', GD = '#ffc94a';
  const towers = (c, n) => M.svg(c, 0, 0, 1920, 1080, Array.from({ length: n }, (_, i) => { const x = 40 + i * (1840 / n), h = 280 + (i * 53) % 360; return `<rect x="${x}" y="${820 - h}" width="${1840 / n - 30}" height="${h}" fill="#0a0f22" stroke="${CY}" stroke-width="2"/>` + Array.from({ length: 6 }, (_, k) => `<rect x="${x + 14 + (k % 2) * 40}" y="${840 - h + k * 40}" width="16" height="10" fill="${GD}" opacity="${(k * i) % 3 ? .9 : .2}"/>`).join(''); }).join('') + '<rect x="0" y="820" width="1920" height="260" fill="#05070f"/>');
  const rain = c => Array.from({ length: 80 }, (_, i) => M.box(c, (i * 137) % 1920, 0, { width: '2px', height: '46px', background: 'linear-gradient(transparent,rgba(180,220,255,.7))', transform: 'rotate(12deg)' }));
  const rainU = (L, t) => L.forEach((e, i) => { e.style.top = (((t * 900 + i * 97) % 1100) - 60) + 'px'; });
  M.story({ bg: '#05070f', sbg: ['#05070f', '#070a18', '#05070f'], tr: ['zoom', 'push'], ring: () => ({ color: CY, width: 4, glow: 'rgba(63,240,255,.5)', shadow: .5 }),
    wins: [M.c(1480, 100, 320), M.q(110, 140, 400, 480, 20), M.c(760, 80, 380)],
    caps: [['下雨的夜里，城市在发光', 'On rainy nights the city glows'], ['积水里，是另一座城', 'Another city in the puddles'], ['走吧，去雨里转转', 'Come on, let’s walk in the rain']], port: { box: [0, 40, 1920, 1000] },
    scenes: [
      [c => ({ tw: towers(c, 10), r: rain(c), t: X(c, 120, 120, 64, '#fff', 'NEON RAIN', 400, M.AN, { textShadow: `0 0 20px ${CY}` }) }), (s, t, a) => { M.rise(s.tw, t, a, 99, { dy: 80 }); rainU(s.r, t); M.hero(s.t, t, a + .3, 99); }],
      [c => ({ tw: towers(c, 9), ref: M.box(c, 0, 820, { width: '1920px', height: '260px', overflow: 'hidden', opacity: .5, filter: 'blur(3px)' }), r: rain(c), t: X(c, 900, 160, 80, '#fff', '积水里的城', 900, M.CN, { textShadow: `0 0 20px ${CY}` }) }),
       (s, t, a) => { if (!s.d) { const m = towers(s.ref, 9); m.style.transform = 'scaleY(-1)'; m.style.transformOrigin = '50% 0'; m.style.top = '-820px'; s.d = 1; } M.rise(s.tw, t, a - .1, 99); s.ref.style.transform = `translateX(${(6 * Math.sin(t * 3)).toFixed(1)}px)`; rainU(s.r, t); M.hero(s.t, t, a + .2, 99); }],
      [c => ({ tw: towers(c, 12), r: rain(c), st: Array.from({ length: 12 }, (_, i) => M.box(c, 0, 0, { width: '140px', height: '3px', background: i % 2 ? CY : '#ff2bd6', boxShadow: '0 0 10px currentColor' })), t: X(c, 120, 640, 90, GD, '走，去雨里转转', 900, M.CN, { textShadow: `0 0 20px ${GD}` }) }),
       (s, t, a) => { M.rise(s.tw, t, a - .1, 99); rainU(s.r, t); s.st.forEach((e, i) => { e.style.transform = `translate(${((t * 700 + i * 260) % 2200 - 200).toFixed(1)}px, ${(860 + (i % 4) * 40).toFixed(1)}px)`; }); M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
