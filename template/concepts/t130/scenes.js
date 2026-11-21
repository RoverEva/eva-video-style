/* T130 数字光场 Light Field: grid floor, light pillars, shared context arcs. */
(function () { const M = K.T.mo, X = M.X, BL = '#4f8cff';
  const floor = c => M.svg(c, 0, 480, 1920, 600, Array.from({ length: 22 }, (_, i) => `<path d="M960 0 L${i * 92 - 50} 600" stroke="rgba(80,150,255,.35)"/>`).join('') + Array.from({ length: 8 }, (_, i) => `<path d="M0 ${20 + i * i * 9} H1920" stroke="rgba(80,150,255,.25)"/>`).join(''));
  const PIL = [[300, 260], [560, 180], [860, 300], [1160, 200], [1420, 280]];
  M.story({ bg: '#030a1f', sbg: ['#030a1f', '#020716', '#030a1f'], tr: ['blur', 'zoom'], ring: () => ({ color: BL, width: 4, glow: 'rgba(79,140,255,.6)', shadow: .5 }),
    wins: [M.c(1520, 90, 300), M.q(110, 120, 360, 420, 20), M.c(760, 80, 380)],
    caps: [['空间，也能被“看懂”', 'Space can be understood too'], ['每个点，都在共享信息', 'Every point shares context'], ['这就是空间智能', 'This is spatial intelligence']], port: { box: [100, 40, 1820, 900] },
    scenes: [
      [c => ({ f: floor(c), p: PIL.map(([x, h]) => M.box(c, x, 480 - h * 1.3, { width: '16px', height: h * 1.3 + 'px', background: 'linear-gradient(#e0f0ff,#2a6dff)', boxShadow: `0 0 26px ${BL}`, transformOrigin: '50% 100%' })), t: X(c, 100, 100, 70, '#dbe8ff', '空间智能') }),
       (s, t, a) => { M.drift(s.f, t, 0, -4); s.p.forEach((e, i) => { const u = M.os((t - a - .3 - i * .15) / .5); e.style.transform = `scaleY(${Math.max(0, u).toFixed(3)})`; e.style.opacity = u > 0 ? 1 : 0; }); M.hero(s.t, t, a + .2, 99); }],
      [c => ({ f: floor(c), arcs: PIL.slice(0, 4).map(([x], i) => M.path(c, 0, 0, 1920, 1080, `M${x + 8} 300 Q ${(x + PIL[i + 1][0]) / 2} 60, ${PIL[i + 1][0] + 8} 300`, '#9fd0ff', 4)), dots: PIL.map(([x]) => M.box(c, x - 6, 288, { width: '28px', height: '28px', borderRadius: '50%', background: '#fff', boxShadow: `0 0 20px ${BL}` })) }),
       (s, t, a) => { s.dots.forEach((e, i) => M.pop(e, t, a - .1 + i * .1, 99, { from: 0 })); s.arcs.forEach((p, i) => M.draw(p, t, a + .3 + i * .2, .5, 99)); }],
      [c => ({ ring: M.box(c, 560, 420, { width: '800px', height: '240px', borderRadius: '50%', border: `3px solid ${BL}`, boxShadow: `0 0 40px ${BL}` }), t: X(c, 520, 560, 120, '#fff', '空间智能', 900, M.CN, { textShadow: `0 0 30px ${BL}` }), e: X(c, 530, 720, 40, '#9fd0ff', 'SPATIAL INTELLIGENCE', 700, M.MONO) }),
       (s, t, a) => { M.pop(s.ring, t, a - .1, 99, { from: .3 }); s.ring.style.transform += ` rotate(${(t * 10).toFixed(1)}deg)`; M.hero(s.t, t, a + .3, 99, { dx: 0, dy: 30 }); M.rise(s.e, t, a + .6, 99); }]
    ] });
})();
