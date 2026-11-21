/* T193 快讯台 News Desk: generic broadcast set (invented brand), lower-third, ticker, breaking stinger. */
(function () { const M = K.T.mo, X = M.X, R = '#e63946', NV = '#0d1b3d';
  const ticker = c => { const g = M.box(c, 0, 0, { width: '1920px', height: '80px', background: R, overflow: 'hidden' }); g.tx = X(g, 0, 14, 40, '#fff', '快讯 ▸ 新功能上线 · 双语字幕全面开放 · 示例内容 ▸ 快讯 ▸ 新功能上线 · 双语字幕全面开放 · 示例内容 ▸', 900, M.CN, { whiteSpace: 'nowrap' }); return g; };
  const set = c => M.svg(c, 0, 0, 1920, 1080, `<path d="M200 820 Q 200 160, 960 140 Q 1720 160, 1720 820" fill="none" stroke="#3d7bff" stroke-width="4" opacity=".7"/><rect x="560" y="820" width="800" height="100" rx="10" fill="#1a2d5c"/>`);
  M.story({ bg: NV, sbg: ['radial-gradient(ellipse at 50% 30%,#1d3a7a,#0d1b3d)', 'radial-gradient(ellipse at 50% 30%,#1d3a7a,#0d1b3d)', '#0d1b3d'], tr: ['wipe', 'push'], ring: () => ({ color: '#3d7bff', width: 4, shadow: .4 }),
    wins: [M.q(320, 260, 680, 460, 10), M.q(320, 260, 680, 460, 10), M.q(160, 180, 520, 560, 10)],
    caps: [['今日快讯', 'Today’s news'], ['新功能上线，双语字幕全面开放（示例）', 'New feature: bilingual captions for all (sample)'], ['明天见', 'See you tomorrow']], port: { box: [60, 40, 1800, 1000] },
    scenes: [
      [c => ({ s: set(c), h: X(c, 1080, 300, 110, '#fff', '今日快讯', 900), e: X(c, 1086, 450, 40, '#7fb0ff', 'NEWS DESK · LIVE', 700, M.INTER), u: M.box(c, 1086, 520, { width: '0px', height: '8px', background: R }), tk: ticker(c) }),
       (s, t, a) => { s.s.style.opacity = M.env(t, a, 99).a; M.hero(s.h, t, a + .3, 99); M.rise(s.e, t, a + .6, 99); s.u.style.width = (480 * M.o3((t - a - .8) / .5)) + 'px'; M.rise(s.tk, t, a + .2, 99, { dy: -80 }); s.tk.tx.style.transform = `translateX(${(-((t - a) * 220) % 1400).toFixed(0)}px)`; }],
      [c => ({ s: set(c), lt: M.box(c, 1080, 300, { width: '700px', padding: '28px 34px', background: '#fff', borderLeft: `14px solid ${R}`, boxSizing: 'border-box' }), tk: ticker(c) }),
       (s, t, a) => { s.s.style.opacity = 1; if (!s.d) { X(s.lt, 34, 24, 54, NV, '双语字幕', 900); X(s.lt, 34, 100, 36, '#555', '全面开放 · 示例', 700); s.lt.style.height = '180px'; s.d = 1; } const u = M.io((t - a) / .6); s.lt.style.clipPath = `inset(0 ${(100 - 100 * u).toFixed(1)}% 0 0)`; s.tk.style.opacity = 1; s.tk.tx.style.transform = `translateX(${(-((t - a) * 220) % 1400).toFixed(0)}px)`; }],
      [c => ({ br: M.box(c, 0, 380, { width: '1920px', height: '220px', background: R, transformOrigin: '0 50%' }), t: X(c, 760, 420, 120, '#fff', '明天见 ▸', 900), lg: X(c, 760, 680, 40, '#7fb0ff', 'NEWS DESK', 700, M.INTER) }),
       (s, t, a) => { s.br.style.transform = `scaleX(${M.io((t - a) / .5).toFixed(3)})`; M.hero(s.t, t, a + .4, 99); M.rise(s.lg, t, a + .7, 99); }]
    ] });
})();
