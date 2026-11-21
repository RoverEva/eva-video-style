/* T118 门诊排队 Clinic Queue (illustrative). */
(function () { const M = K.T.mo, X = M.X, INK = '#111';
  M.story({ bg: '#ffffff', sbg: ['#ffffff', '#f2f5f8', '#ffffff'], tr: ['push', 'wipe'], ring: () => ({ color: INK, width: 5, shadow: .25 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 26), M.c(760, 90, 380)],
    caps: [['看病排队，最熬人', 'Waiting at the clinic is the worst'], ['为什么总卡在最后一格？', 'Why does it stall at the last step?'], ['提前在线挂号，少排一会儿（示意）', 'Book online ahead, wait less (illustrative)']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ q: Array.from({ length: 8 }, (_, i) => M.box(c, 300, 100 + i * 86, { width: '420px', height: '70px', border: '4px solid #111', borderRadius: '12px', boxSizing: 'border-box', background: '#fff' })), n: X(c, 800, 300, 130, INK, '第 7 位', 400, M.AN) }),
       (s, t, a) => { s.q.forEach((e, i) => { M.rise(e, t, a + .1 + i * .06, 99, { dy: 40 }); e.style.background = t > a + .8 + (7 - i) * .18 ? '#111' : '#fff'; }); M.hero(s.n, t, a + .6, 99); }],
      [c => ({ bar: M.box(c, 640, 420, { width: '1000px', height: '90px', border: '6px solid #111', borderRadius: '18px', boxSizing: 'border-box', overflow: 'hidden' }), p: X(c, 640, 560, 160, INK, '99%', 400, M.AN), sp: M.svg(c, 1480, 560, 140, 140, '<circle cx="70" cy="70" r="54" fill="none" stroke="#111" stroke-width="12" stroke-dasharray="80 260"/>', { transformOrigin: '50% 50%' }) }),
       (s, t, a) => { if (!s.f) s.f = M.box(s.bar, 0, 0, { height: '100%', background: 'repeating-linear-gradient(45deg,#ffd23f 0 18px,#111 18px 36px)' }); s.f.style.width = (99 * M.o3((t - a) / 1.2)) + '%'; M.panel(s.bar, t, a - .15, 99, { r: 18 }); M.rise(s.p, t, a + .3, 99); M.count(s.p, 99, t, a, 1.2, v => v + '%'); M.pop(s.sp, t, a + .4, 99, { from: .4, base: `rotate(${(t * 360).toFixed(0)}deg)` }); }],
      [c => ({ card: M.card(c, 300, 560, 1320, 200, '#111', { borderRadius: '26px', display: 'flex', alignItems: 'center', padding: '0 50px', boxSizing: 'border-box' }), cal: M.svg(c, 300, 200, 200, 200, '<rect x="10" y="30" width="180" height="160" rx="20" fill="#fff" stroke="#111" stroke-width="8"/><path d="M10 80 H190" stroke="#111" stroke-width="8"/><path d="M60 130 L90 160 L150 100" stroke="#2fbf71" stroke-width="12" fill="none"/>') }),
       (s, t, a) => { if (!s.card.d) { X(s.card, 0, 0, 54, '#fff', '提前在线挂号 · 少排一会儿', 900, M.CN, { position: 'static' }); s.card.d = 1; } M.panel(s.card, t, a - .1, 99, { r: 26 }); M.pop(s.cal, t, a + .3, 99, { from: .3 }); }]
    ] });
})();
