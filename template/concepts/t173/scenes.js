/* T173 信号故障 Glitch Highlight (game clips): RGB-split word, slice jitter, replay counter. */
(function () { const M = K.T.mo, X = M.X, CY = '#3ff0ff', PK = '#ff2bd6';
  const gw = (c, x, y, px, txt) => { const g = M.box(c, x, y, {}); g.r = X(g, 0, 0, px, PK, txt, 400, M.AN, { mixBlendMode: 'screen' }); g.b = X(g, 0, 0, px, CY, txt, 400, M.AN, { mixBlendMode: 'screen' }); g.w = X(g, 0, 0, px, '#fff', txt, 400, M.AN); return g; };
  const jit = (g, t, k) => { const j = (Math.sin(t * 37) > .6 ? 1 : 0) * k; g.r.style.transform = `translate(${(-6 - 14 * j).toFixed(0)}px, ${(2 * j).toFixed(0)}px)`; g.b.style.transform = `translate(${(6 + 14 * j).toFixed(0)}px, ${(-2 * j).toFixed(0)}px)`; g.w.style.clipPath = j ? `inset(${(40 + 20 * Math.sin(t * 11)).toFixed(0)}% 0 ${(30).toFixed(0)}% 0)` : 'none'; g.w.style.transform = j ? `translateX(${(20 * Math.sin(t * 50)).toFixed(0)}px)` : ''; };
  const scan = c => M.box(c, 0, 0, { width: '1920px', height: '1080px', backgroundImage: 'repeating-linear-gradient(transparent 0 3px,rgba(255,255,255,.04) 3px 4px)', zIndex: 3 });
  M.story({ bg: '#0a0a0c', sbg: ['#0a0a0c', '#0c0c10', '#0a0a0c'], tr: ['shutter', 'blur'], ring: () => ({ color: CY, width: 5, glow: 'rgba(63,240,255,.4)', shadow: .5 }),
    wins: [M.q(1180, 420, 560, 420, 8), M.q(120, 160, 520, 420, 8), M.c(1380, 140, 400)],
    caps: [['这一波操作，看好了', 'Watch this play'], ['慢放，再看一遍', 'Slow it down, once more'], ['三杀，漂亮', 'Triple kill — beautiful']], port: { box: [40, 40, 1840, 960] },
    scenes: [
      [c => ({ sc: scan(c), w: gw(c, 120, 160, 220, 'HIGHLIGHT'), t: X(c, 130, 480, 70, '#fff', '这一波操作', 900) }), (s, t, a) => { M.pop(s.w, t, a + .1, 99, { from: 1.4 }); jit(s.w, t, 1); M.hero(s.t, t, a + .6, 99); }],
      [c => ({ sc: scan(c), w: gw(c, 760, 220, 160, 'REPLAY'), sp: X(c, 770, 460, 80, '#ffd23f', '0.25×', 400, M.AN), bar: M.box(c, 770, 620, { width: '960px', height: '10px', background: '#333' }), pg: M.box(c, 770, 620, { width: '0px', height: '10px', background: PK }) }),
       (s, t, a) => { M.slide(s.w, t, a - .15, 99, { dx: 200 }); jit(s.w, t, .6); M.rise(s.sp, t, a + .3, 99); M.rise(s.bar, t, a + .2, 99); s.pg.style.width = (960 * Math.min(1, Math.max(0, (t - a) / 3))) + 'px'; }],
      [c => ({ sc: scan(c), w: gw(c, 120, 300, 260, 'TRIPLE'), k: [0, 1, 2].map(i => M.box(c, 140 + i * 200, 640, { width: '160px', height: '160px', borderRadius: '50%', border: `8px solid ${PK}`, boxSizing: 'border-box', color: '#fff', font: M.f(400, 70, M.AN), display: 'flex', alignItems: 'center', justifyContent: 'center' }, '✕')) }),
       (s, t, a) => { M.pop(s.w, t, a - .1, 99, { from: 1.6 }); jit(s.w, t, 1); s.k.forEach((e, i) => M.pop(e, t, a + .5 + i * .3, 99, { from: 2 })); }]
    ] });
})();
