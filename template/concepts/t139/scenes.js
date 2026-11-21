/* T139 笔触妆效 Brush Repaint: the window gets repainted stroke by stroke (filter mask), palette, swatches. */
(function () { const M = K.T.mo, X = M.X, INK = '#5a3d2b';
  M.story({ bg: '#efe6d6', sbg: ['#efe6d6', '#2a2420', '#f3ebdd'], tr: ['wipe', 'push'], ring: () => ({ color: '#fffaf0', width: 10, shadow: .35 }),
    wins: [M.q(160, 120, 900, 620, 12, 1.05), M.c(1420, 160, 360), M.q(120, 160, 420, 500, 20)],
    caps: [['一笔一笔，画出今天的妆', 'Stroke by stroke, today’s look'], ['三支笔刷，三种质感', 'Three brushes, three textures'], ['画完，就是你的风格', 'Finished — your own style']], port: { box: [100, 60, 1820, 800] },
    scenes: [
      [c => ({ paint: M.box(c, 160, 120, { width: '900px', height: '620px', borderRadius: '12px', backdropFilter: 'saturate(1.9) contrast(1.25) sepia(.2) blur(1px)', zIndex: 60, clipPath: 'inset(0 100% 0 0)' }), br: M.path(c, 160, 120, 900, 620, 'M0 120 C 200 60, 500 200, 900 100 M0 360 C 300 280, 600 440, 900 330 M0 560 C 260 500, 640 640, 900 540', '#c0392b', 40, 'opacity=".55"'), t: X(c, 1140, 300, 80, INK, '重绘', 900, M.SERIF), e: X(c, 1144, 420, 40, '#8a5a35', 'Repainted', 700, M.PF, { fontStyle: 'italic' }) }),
       (s, t, a) => { const u = M.io((t - a - .3) / 2); s.paint.style.clipPath = `inset(0 ${(100 - 100 * u).toFixed(1)}% 0 0 round 12px)`; M.draw(s.br, t, a + .3, 2, 99); M.hero(s.t, t, a + .5, 99); M.rise(s.e, t, a + .8, 99); }],
      [c => ({ bs: [['#e07a5f', '哑光'], ['#f2cc8f', '珠光'], ['#81b29a', '水润']].map(([col, n], i) => { const g = M.box(c, 160 + i * 400, 260, {}); M.box(g, 0, 0, { width: '320px', height: '90px', background: col, borderRadius: '45px 10px 45px 10px', transform: 'rotate(-6deg)' }); X(g, 20, 150, 64, '#f3ebdd', n, 900, M.SERIF); return g; }) }),
       (s, t, a) => s.bs.forEach((g, i) => { M.slide(g, t, a - .15 + i * .25, 99, { dx: -200 }); })],
      [c => ({ pal: M.svg(c, 700, 160, 600, 460, '<path d="M300 20 C 520 20, 580 180, 520 300 C 480 380, 380 360, 360 420 C 340 460, 120 440, 60 320 C 0 200, 100 20, 300 20Z" fill="#fff" stroke="#5a3d2b" stroke-width="6"/><circle cx="200" cy="130" r="40" fill="#e07a5f"/><circle cx="340" cy="110" r="40" fill="#f2cc8f"/><circle cx="440" cy="210" r="40" fill="#81b29a"/><circle cx="160" cy="270" r="40" fill="#3d405b"/>', { transformOrigin: '50% 50%' }), t: X(c, 1300, 640, 70, INK, '你的风格', 900, M.SERIF) }),
       (s, t, a) => { M.pop(s.pal, t, a - .1, 99, { from: .5 }); s.pal.style.transform += ` rotate(${(-6 + 4 * Math.sin(t)).toFixed(1)}deg)`; M.hero(s.t, t, a + .5, 99); }]
    ] });
})();
