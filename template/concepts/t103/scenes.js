/* T103 展墙历史课 Gallery Lesson */
(function () { const M = K.T.mo, X = M.X, f = M.f, GOLD = '#c9a45c';
  const paint = (p, x, y, w, h, inner) => { const fr = M.box(p, x, y, { width: w + 'px', height: h + 'px', border: '14px solid #2b2621', boxSizing: 'border-box', background: '#f3ead6', boxShadow: '0 18px 30px rgba(0,0,0,.3)', overflow: 'hidden' }); M.svg(fr, 0, 0, w - 28, h - 28, inner); return fr; };
  const cone = (p, x) => M.box(p, x - 180, -40, { width: '360px', height: '700px', background: 'linear-gradient(rgba(255,240,200,.5),rgba(255,240,200,0))', clipPath: 'polygon(42% 0,58% 0,100% 100%,0 100%)' });
  M.story({ bg: '#e9e4dc', sbg: ['#e9e4dc', '#211c18', '#efe9df'], tr: ['push', 'zoom'], ring: () => ({ color: '#2b2621', width: 12, shadow: .4 }),
    wins: [M.q(770, 230, 330, 390, 6), M.c(1440, 130, 360), M.q(120, 170, 420, 500, 20)],
    caps: [['今天的历史课，在展墙上', 'Today’s history lesson is on the wall'], ['唐、宋、元，一路走过', 'Tang, Song, Yuan — walking through'], ['宋朝：960 年到 1279 年', 'Song dynasty: 960 to 1279']], port: { box: [100, 40, 1700, 820] },
    scenes: [
      [c => ({ cn: [380, 935, 1490].map(x => cone(c, x)), p1: paint(c, 260, 230, 300, 390, '<path d="M0 300 L80 150 L150 230 L230 90 L272 160 V362 H0Z" fill="#6b8f71"/><circle cx="210" cy="70" r="30" fill="#e07a5f"/>'),
          p3: paint(c, 1320, 230, 300, 390, '<path d="M30 320 C 80 120, 200 120, 240 320Z" fill="#3d5a80"/><path d="M0 330 H272" stroke="#98c1d9" stroke-width="16"/>'), t: X(c, 600, 100, 64, '#2b2621', '展墙上的历史课', 900, M.SERIF),
          lb: [['山水 · 示意', 280], ['讲者', 830], ['江河 · 示意', 1340]].map(([s, x]) => M.box(c, x, 650, { padding: '8px 16px', background: '#fff', font: f(700, 22, M.CN), color: '#2b2621', boxShadow: '0 4px 8px rgba(0,0,0,.1)' }, s)) }),
       (s, t, a) => { s.cn.forEach((e, i) => { e.style.opacity = M.env(t, a + .2 + i * .2, 99, .5).a * (.8 + .2 * Math.sin(t * 2 + i)); }); M.rise(s.p1, t, a + .3, 99, { dy: 40 }); M.rise(s.p3, t, a + .5, 99, { dy: 40 }); M.hero(s.t, t, a + .7, 99, { dx: 0, dy: -20 }); s.lb.forEach((e, i) => M.rise(e, t, a + 1.0 + i * .12, 99)); }],
      [c => ({ sp: M.box(c, 0, 0, { width: '700px', height: '1080px', background: 'radial-gradient(ellipse at 50% 40%, rgba(255,230,170,.35), transparent 60%)' }),
          era: [['唐', '618'], ['宋', '960'], ['元', '1271']].map(([n, y], i) => { const g = M.box(c, 140 + i * 400, 300, { width: '320px', height: '300px', border: `3px solid ${GOLD}`, boxSizing: 'border-box', textAlign: 'center' }); X(g, 0, 40, 130, '#f3ead6', n, 900, M.SERIF, { width: '320px', textAlign: 'center' }); X(g, 0, 210, 40, GOLD, y + ' 年', 700, M.MONO, { width: '320px', textAlign: 'center' }); return g; }),
          ln: M.path(c, 140, 650, 1120, 20, 'M0 10 H1120', GOLD, 4) }),
       (s, t, a) => { s.sp.style.transform = `translateX(${(80 + 400 * M.io((t - a) / 2.6)).toFixed(1)}px)`; s.era.forEach((e, i) => M.slide(e, t, a - .1 + i * .35, 99, { dx: 80 })); M.draw(s.ln, t, a + .2, 1.4, 99); }],
      [c => ({ pl: M.card(c, 640, 200, 1000, 420, '#fffdf8', { borderRadius: '4px', padding: '50px', boxSizing: 'border-box' }) }),
       (s, t, a) => { if (!s.pl.done) { X(s.pl, 50, 40, 30, GOLD, '展签 · LABEL', 700, M.MONO); X(s.pl, 50, 100, 96, '#2b2621', '宋', 900, M.SERIF); X(s.pl, 180, 130, 54, '#2b2621', '960 — 1279', 700, M.MONO); X(s.pl, 52, 250, 34, '#5a4a3a', '一个特别重视读书人的朝代', 700, M.SERIF); s.pl.done = 1; }
         M.panel(s.pl, t, a - .1, 99, { r: 4, din: .55 }); }]
    ] });
})();
