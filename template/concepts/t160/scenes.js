/* T160 发布会 Keynote: auditorium seats, a glowing screen, hero headline, spec reveal, "one more thing". */
(function () { const M = K.T.mo, X = M.X, V = '#8b7bff';
  const seats = c => M.svg(c, -40, 860, 2000, 240, Array.from({ length: 34 }, (_, i) => `<path d="M${i * 60} 240 V60 Q ${i * 60} 20 ${i * 60 + 26} 20 Q ${i * 60 + 52} 20 ${i * 60 + 52} 60 V240Z" fill="#1c1c24"/>`).join('') + Array.from({ length: 34 }, (_, i) => `<path d="M${i * 60 + 30} 240 V110 Q ${i * 60 + 30} 70 ${i * 60 + 56} 70 Q ${i * 60 + 82} 70 ${i * 60 + 82} 110 V240Z" fill="#14141a"/>`).join(''));
  const screen = c => M.box(c, 140, 60, { width: '1640px', height: '760px', borderRadius: '24px', background: 'linear-gradient(160deg,#1b1d2e,#0e0f18)', border: '2px solid #2a2d45', boxShadow: '0 0 120px rgba(139,123,255,.25)' });
  M.story({ bg: '#07070b', sbg: ['#07070b', '#07070b', '#07070b'], tr: ['zoom', 'blur'], ring: () => ({ color: '#ffffff', width: 0, shadow: .5 }),
    wins: [M.q(1160, 180, 500, 500, 20, 1.05), M.q(200, 200, 420, 480, 20), M.q(1220, 160, 460, 520, 20)],
    caps: [['今天，我们带来全新一代', 'Today we introduce the next generation'], ['更快，更轻，更聪明', 'Faster, lighter, smarter'], ['还有一件事……', 'One more thing…']], port: { box: [100, 40, 1720, 960] },
    scenes: [
      [c => ({ sc: screen(c), s: seats(c), t: X(c, 260, 260, 130, '#fff', '全新一代', 900), e: X(c, 266, 440, 46, V, 'Introducing what’s next', 700, M.INTER) }),
       (s, t, a) => { s.sc.style.opacity = M.env(t, a, 99, .8).a; M.rise(s.s, t, a, 99, { dy: 60 }); M.hero(s.t, t, a + .4, 99); M.rise(s.e, t, a + .8, 99); }],
      [c => ({ sc: screen(c), s: seats(c), sp: [['2×', '更快 faster'], ['−30%', '更轻 lighter'], ['AI', '更聪明 smarter']].map(([n, k], i) => { const g = M.box(c, 720 + i * 340, 300, {}); X(g, 0, 0, 120, i === 1 ? V : '#fff', n, 400, M.AN); X(g, 0, 160, 34, '#9a9ab8', k, 700); return g; }) }),
       (s, t, a) => { s.sc.style.opacity = 1; s.sp.forEach((g, i) => M.rise(g, t, a - .1 + i * .3, 99, { dy: 80 })); }],
      [c => ({ s: seats(c), t: X(c, 200, 320, 110, '#fff', 'One more thing…', 300, M.INTER), dot: M.box(c, 200, 520, { width: '20px', height: '20px', borderRadius: '50%', background: V, boxShadow: `0 0 30px ${V}` }) }),
       (s, t, a) => { M.hero(s.t, t, a + .2, 99); M.pop(s.dot, t, a + 1.2, 99, { from: 0 }); s.dot.style.transform += ` translateX(${(Math.max(0, t - a - 1.2) * 300).toFixed(0)}px)`; }]
    ] });
})();
