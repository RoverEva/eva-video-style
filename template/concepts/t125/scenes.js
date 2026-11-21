/* T125 正反论证 Argument: can / can't / conclusion. */
(function () { const M = K.T.mo, X = M.X, OR = '#ff5a36', INK = '#1f2328';
  M.story({ bg: '#d9dde1', sbg: ['#d9dde1', '#1f2328', '#d9dde1'], tr: ['shutter', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.c(1560, 110, 300), M.q(120, 160, 420, 500, 24)],
    caps: [['AI 能代替人工吗？', 'Can AI replace people?'], ['能做的，和做不了的', 'What it can and can’t do'], ['结论：分工，而不是替代', 'Conclusion: divide the work, don’t replace']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ q: X(c, 140, 300, 130, INK, 'AI 能代替'), q2: X(c, 140, 470, 130, OR, '人工吗？'), bar: M.box(c, 140, 260, { width: '12px', height: '360px', background: OR }) }),
       (s, t, a) => { M.hero(s.q, t, a + .2, 99); M.hero(s.q2, t, a + .45, 99); const u = M.o3((t - a) / .5); s.bar.style.transform = `scaleY(${u})`; }],
      [c => ({ cols: [['能 CAN', OR, ['整理素材', '批量字幕', '找出重复']], ['不能 CAN’T', '#9aa3ad', ['判断品味', '讲你的故事', '承担责任']]].map(([h, col, L], i) => { const g = M.box(c, 140 + i * 640, 160, {}); X(g, 0, 0, 80, col, h, 400, M.AN); g.it = L.map((s2, k) => X(g, 0, 140 + k * 110, 56, '#fff', (i ? '✕ ' : '✓ ') + s2)); return g; }) }),
       (s, t, a) => s.cols.forEach((g, i) => { M.slide(g, t, a - .15 + i * .3, 99, { dx: i ? 80 : -80 }); g.it.forEach((e, k) => M.rise(e, t, a + .3 + i * .3 + k * .15, 99)); })],
      [c => ({ bar: M.box(c, 640, 360, { width: '1100px', height: '180px', background: OR, display: 'flex', alignItems: 'center', padding: '0 50px', boxSizing: 'border-box', font: M.f(900, 76, M.CN), color: '#fff' }, '分工，而不是替代'), k: X(c, 644, 260, 40, INK, 'CONCLUSION 结论', 700, M.MONO) }),
       (s, t, a) => { M.panel(s.bar, t, a - .1, 99); M.rise(s.k, t, a + .3, 99); }]
    ] });
})();
