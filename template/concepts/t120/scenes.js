/* T120 健康问答 Health Q&A (general wellness; not medical advice). Weekend catch-up sleep only partly repays sleep debt. */
(function () { const M = K.T.mo, X = M.X, TL = '#1aa39a', INK = '#16343a';
  const bub = (c, x, y, w, me, txt, sz) => { const b = M.box(c, x, y, { width: w + 'px', padding: '26px 32px', boxSizing: 'border-box', background: me ? TL : '#fff', color: me ? '#fff' : INK, borderRadius: me ? '30px 30px 8px 30px' : '30px 30px 30px 8px', boxShadow: '0 10px 20px rgba(0,0,0,.08)', font: M.f(800, sz || 44, M.CN), transformOrigin: me ? '100% 100%' : '0 100%' }, txt); return b; };
  M.story({ bg: '#eef7f5', sbg: ['#eef7f5', '#dff1ed', '#eef7f5'], tr: ['slide', 'iris'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 30), M.c(1440, 150, 380)],
    caps: [['熬夜之后，怎么补救？', 'Stayed up late — now what?'], ['先补觉，少靠咖啡，多喝水', 'Sleep first, less coffee, more water'], ['周末补觉，只能补回一部分', 'Weekend catch-up sleep only partly helps']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ dots: M.box(c, 160, 300, { display: 'flex', gap: '16px', padding: '30px 36px', background: '#fff', borderRadius: '30px' }), q: bub(c, 160, 300, 760, 0, '熬夜之后，要怎么补救？', 52) }),
       (s, t, a) => { if (!s.dots.d) { for (let i = 0; i < 3; i++) M.box(s.dots, 0, 0, { position: 'relative', width: '18px', height: '18px', borderRadius: '50%', background: '#9fb5b2' }); s.dots.d = 1; }
         s.dots.style.display = t < a + 1.0 ? '' : 'none'; M.pop(s.dots, t, a + .2, 99, { from: .6 }); M.pop(s.q, t, a + 1.0, 99, { from: .7 }); }],
      [c => ({ a: bub(c, 640, 160, 1000, 1, '先补觉，别靠咖啡硬撑', 52), tips: [['😴', '补觉'], ['☕', '少咖啡'], ['💧', '多喝水']].map(([e, s2], i) => { const g = M.card(c, 640 + i * 340, 420, 300, 260, '#fff', { textAlign: 'center' }); X(g, 0, 30, 90, INK, e, 400, M.INTER, { width: '300px', textAlign: 'center' }); X(g, 0, 160, 48, INK, s2, 900, M.CN, { width: '300px', textAlign: 'center' }); return g; }) }),
       (s, t, a) => { M.pop(s.a, t, a - .1, 99, { from: .7 }); s.tips.forEach((g, i) => M.rise(g, t, a + .4 + i * .18, 99, { dy: 80 })); }],
      [c => ({ q: bub(c, 160, 160, 760, 0, '那周末能补回来吗？', 46), a: bub(c, 500, 360, 1000, 1, '只能补回一部分，规律作息更重要', 44), d: X(c, 500, 600, 26, '#5d8a86', '仅供参考，不构成医疗建议') }),
       (s, t, a) => { M.pop(s.q, t, a - .1, 99, { from: .7 }); M.pop(s.a, t, a + .7, 99, { from: .7 }); M.rise(s.d, t, a + 1.1, 99); }]
    ] });
})();
