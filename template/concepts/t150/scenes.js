/* T150 空间画廊 Gallery Walk: a dark gallery corridor, framed works slide past in depth. */
(function () { const M = K.T.mo, X = M.X, GD = '#c9a45c';
  const PAL = [['#1d3557', '#f1faee'], ['#e63946', '#fff'], ['#2a9d8f', '#fff'], ['#f4a261', '#222'], ['#6d597a', '#fff'], ['#ffd166', '#222'], ['#118ab2', '#fff']];
  const frame = (c, k, w, h, txt) => { const [bg, fg] = PAL[k % PAL.length]; const f = M.box(c, 0, 0, { width: w + 'px', height: h + 'px', border: `10px solid ${GD}`, background: bg, boxShadow: '0 30px 50px rgba(0,0,0,.6)', boxSizing: 'border-box', transformOrigin: '50% 50%' }); X(f, 24, 24, h * .14, fg, txt, 900); M.box(f, 24, h * .55, { width: (w * .5) + 'px', height: '10px', background: fg, opacity: .5 }); return f; };
  M.story({ bg: '#1b1b1f', sbg: ['radial-gradient(ellipse at 50% 30%,#3a3a42,#141417)', 'linear-gradient(#202026,#111114)', 'radial-gradient(ellipse at 50% 20%,#4a4030,#141417)'], tr: ['push', 'zoom'], ring: () => ({ color: GD, width: 8, shadow: .5 }),
    wins: [M.q(760, 260, 400, 400, 6, 1.1), M.q(120, 200, 420, 520, 6), M.q(1380, 180, 400, 480, 6)],
    caps: [['欢迎来到我的作品展', 'Welcome to my gallery'], ['每一幅，都是一个项目', 'Every frame is a project'], ['慢慢走，慢慢看', 'Walk slowly, take it in']], port: { box: [80, 40, 1760, 900] },
    scenes: [
      [c => ({ f: ['海报', '品牌', '短片', '插画', '摄影', 'UI'].map((n, i) => frame(c, i, 240, 300, n)), floor: M.box(c, 0, 820, { width: '1920px', height: '260px', background: 'linear-gradient(#2a2a30,#0c0c0e)' }), t: X(c, 600, 780, 54, '#e8dcc0', 'Walk through the work', 700, M.PF, { fontStyle: 'italic' }) }),
       (s, t, a) => { s.f.forEach((e, i) => { const x = ((i * 330 - (t - a) * 160) % 1980 + 1980) % 1980 - 260, d = Math.abs(x + 120 - 960) / 960; e.style.opacity = M.env(t, a + i * .05, 99).a; e.style.transform = `translate(${x.toFixed(1)}px, ${(300 + 60 * d).toFixed(1)}px) scale(${(1 - .35 * d).toFixed(3)}) rotateY(${((x - 840) / 960 * -25).toFixed(1)}deg)`; }); M.hero(s.t, t, a + .5, 99); }],
      [c => ({ big: frame(c, 0, 820, 560, '项目 01'), tag: X(c, 660, 800, 40, GD, 'No.01 · 品牌海报 Poster', 700) }),
       (s, t, a) => { M.pop(s.big, t, a - .15, 99, { from: .7 }); s.big.style.transform = `translate(660px, 220px) ` + s.big.style.transform; M.rise(s.tag, t, a + .5, 99); }],
      [c => ({ g: [0, 1, 2, 3].map(i => frame(c, i + 2, 260, 320, ['短片', '插画', '摄影', 'UI'][i])), t: X(c, 200, 120, 70, '#e8dcc0', '慢慢走，慢慢看', 900, M.SERIF) }),
       (s, t, a) => { s.g.forEach((e, i) => { M.rise(e, t, a - .1 + i * .15, 99, { dy: 120 }); e.style.transform = `translate(${160 + i * 300}px, 260px) ` + e.style.transform; }); M.hero(s.t, t, a + .7, 99); }]
    ] });
})();
