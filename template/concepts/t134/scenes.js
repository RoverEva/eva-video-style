/* T134 无限画布 Infinite Canvas: notes + cursors → pan & connect → zoom-out overview. */
(function () { const M = K.T.mo, X = M.X;
  const note = (c, x, y, col, s2) => M.box(c, x, y, { width: '240px', height: '180px', background: col, padding: '24px', boxSizing: 'border-box', font: M.f(900, 44, M.CN), boxShadow: '0 8px 16px rgba(0,0,0,.1)' }, s2);
  const cur = (c, col, n) => { const g = M.box(c, 0, 0, {}); M.svg(g, 0, 0, 40, 46, `<path d="M2 2 L2 36 L11 27 L19 42 L25 39 L17 24 L31 24Z" fill="${col}"/>`); X(g, 30, 34, 20, '#fff', n, 700, M.INTER, { background: col, padding: '3px 10px', borderRadius: '8px' }); return g; };
  M.story({ bg: '#f7f7f4', sbg: ['#f7f7f4', '#f7f7f4', '#eeeee8'], tr: ['slide', 'zoom'], ring: () => ({ color: '#ffffff', width: 8, shadow: .25 }),
    wins: [M.q(1340, 140, 440, 330, 20), M.q(110, 520, 420, 300, 20), M.c(1520, 130, 300)],
    caps: [['大家一起，往画布上贴想法', 'Everyone pins ideas on the canvas'], ['连起来，就是一条流程', 'Connect them into a flow'], ['退远一点，全局一目了然', 'Zoom out — the whole picture']], port: { box: [100, 40, 1820, 840] },
    scenes: [
      [c => ({ d: M.dots(c, '#cfcfc8', 26, 2), n: [note(c, 200, 160, '#ffd166', '选题'), note(c, 560, 300, '#a0e7e5', '脚本'), note(c, 300, 520, '#ffadad', '剪辑')], c1: cur(c, '#ff5a5f', 'Eva'), c2: cur(c, '#3a86ff', 'Leo') }),
       (s, t, a) => { s.n.forEach((e, i) => M.pop(e, t, a + .3 + i * .35, 99, { from: .6 })); const u = M.io((t - a) / 2.4); s.c1.style.transform = `translate(${(900 - 420 * u).toFixed(1)}px, ${(700 - 300 * u).toFixed(1)}px)`; s.c2.style.transform = `translate(${(1100 - 300 * u).toFixed(1)}px, ${(200 + 300 * u).toFixed(1)}px)`; s.c1.style.opacity = s.c2.style.opacity = M.env(t, a + .2, 99).a; }],
      [c => ({ g: M.box(c, 0, 0, { width: '3000px', height: '1080px' }) }),
       (s, t, a) => { if (!s.n) { M.dots(s.g, '#cfcfc8', 26, 2); s.n = [['选题', '#ffd166'], ['脚本', '#a0e7e5'], ['拍摄', '#cdb4db'], ['剪辑', '#ffadad'], ['发布', '#b9fbc0']].map(([w, col], i) => note(s.g, 600 + i * 420, 300 + (i % 2) * 160, col, w)); s.ln = [0, 1, 2, 3].map(i => M.path(s.g, 0, 0, 3000, 1080, `M${840 + i * 420} ${390 + (i % 2) * 160} C ${900 + i * 420} ${390 + (i % 2) * 160}, ${960 + i * 420} ${390 + ((i + 1) % 2) * 160}, ${1020 + i * 420} ${390 + ((i + 1) % 2) * 160}`, '#555', 4)); }
         s.g.style.transform = `translateX(${(-60 - 460 * M.io((t - a) / 3)).toFixed(1)}px)`; s.n.forEach((e, i) => M.pop(e, t, a - .1 + i * .12, 99, { from: .7 })); s.ln.forEach((p, i) => M.draw(p, t, a + .5 + i * .3, .4, 99)); }],
      [c => ({ fr: M.box(c, 200, 160, { width: '1180px', height: '640px', border: '4px dashed #888', borderRadius: '24px' }), mini: Array.from({ length: 12 }, (_, i) => M.box(c, 260 + (i % 4) * 280, 230 + Math.floor(i / 4) * 180, { width: '220px', height: '130px', background: ['#ffd166', '#a0e7e5', '#cdb4db', '#ffadad', '#b9fbc0'][i % 5], borderRadius: '6px' })), t: X(c, 230, 100, 40, '#333', 'PROJECT BOARD · 全局', 700, M.MONO) }),
       (s, t, a) => { M.pop(s.fr, t, a - .1, 99, { from: 1.3 }); s.mini.forEach((e, i) => M.pop(e, t, a + i * .04, 99, { from: 1.4 })); M.rise(s.t, t, a + .4, 99); }]
    ] });
})();
