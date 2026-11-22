/* T102 粉笔推导 Chalk Proof (teacher): blackboard, a formula chalk-writes itself step by step, circled answer. */
(function () { const M = K.T.mo, X = M.X, CK = '#f2f2ea', BD = '#1f3a2e', CH = "'Comic Sans MS', 'Noto Sans CJK SC', cursive";
  const board = c => M.box(c, -40, -40, { width: '2000px', height: '1160px', background: `radial-gradient(ellipse at 40% 40%, #2d5240, ${BD})`, boxShadow: 'inset 0 0 160px rgba(0,0,0,.5)' });
  const chalk = (c, x, y, px, txt, col) => X(c, x, y, px, col || CK, txt, 700, CH, { textShadow: '0 0 2px rgba(255,255,255,.4)', opacity: .92 });
  const write = (e, t, a, d) => { const u = Math.max(0, Math.min(1, (t - a) / d)); e.style.clipPath = `inset(-20px ${(100 - 100 * u).toFixed(1)}% -20px -20px)`; e.style.opacity = t > a ? .92 : 0; };
  M.story({ bg: BD, sbg: ['transparent', 'transparent', 'transparent'], tr: ['wipe', 'zoom'], ring: () => ({ color: '#c9a66b', width: 12, shadow: .45 }),
    wins: [M.q(1380, 180, 420, 500, 10), M.q(1380, 180, 420, 500, 10), M.c(1420, 200, 380)],
    caps: [['今天推一个公式', 'Let’s derive one formula'], ['一步一步写出来', 'Step by step on the board'], ['答案，圈出来', 'Circle the answer']], port: { box: [60, 60, 1800, 900] },
    scenes: [
      [c => ({ b: board(c), d: chalk(c, 140, 120, 40, '第 7 课 · Lesson 7', '#c9e4d4'), t: chalk(c, 140, 240, 150, '面积公式'), e: chalk(c, 146, 440, 54, 'Area of a circle', '#ffd6a5') }),
       (s, t, a) => { write(s.d, t, a + .2, .6); write(s.t, t, a + .6, 1); write(s.e, t, a + 1.5, .8); }],
      [c => ({ b: board(c), l: ['S = π × r × r', '= π r²', 'r = 3 → S = 9π'].map((tx, i) => chalk(c, 160, 200 + i * 170, 96, tx, i === 2 ? '#ffd6a5' : CK)), ci: M.svg(c, 140, 160, 200, 200, `<circle cx="100" cy="100" r="80" fill="none" stroke="${CK}" stroke-width="5" stroke-dasharray="8 8"/><path d="M100 100 H180" stroke="#ffd6a5" stroke-width="5"/>`) }),
       (s, t, a) => { s.l.forEach((e, i) => write(e, t, a - .1 + i * .8, .7)); s.ci.style.opacity = 0; }],
      [c => ({ b: board(c), ans: chalk(c, 300, 340, 160, 'S ≈ 28.3'), ring: M.path(c, 220, 260, 900, 340, 'M450 20 C 760 10, 880 120, 860 190 C 830 300, 400 320, 160 290 C 20 260, 10 120, 160 60 C 260 25, 400 18, 520 22', '#ff8fab', 8), st: chalk(c, 320, 660, 50, '✓ 记住它 · remember it', '#c9e4d4') }),
       (s, t, a) => { write(s.ans, t, a - .1, .9); M.draw(s.ring, t, a + .9, .7, 99); write(s.st, t, a + 1.6, .6); }]
    ] });
})();
