/* T132 撕纸回忆 Torn Memories. Photos = frames of the presenter's own clip. */
(function () { const M = K.T.mo, X = M.X, INK = '#4a3a2a';
  const torn = 'polygon(0 4%,8% 0,20% 5%,35% 1%,50% 6%,66% 0,80% 4%,100% 1%,98% 30%,100% 60%,97% 96%,80% 100%,60% 95%,40% 100%,20% 96%,0 100%,3% 60%,0 30%)';
  const tp = (c, f, w, h) => { const p = M.box(c, 0, 0, { width: w + 'px', height: h + 'px', clipPath: torn, filter: 'sepia(.35) contrast(1.05)', transformOrigin: '50% 30%' }); M.img(p, 0, 0, w, h, f); return p; };
  M.story({ bg: '#ede6da', sbg: ['#ede6da', '#2a241e', '#efe7d8'], tr: ['slide', 'push'], ring: () => ({ color: '#fffdf6', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(1380, 150, 400, 480, 14), M.c(110, 160, 380)],
    caps: [['翻出几张旧照片', 'Digging out some old photos'], ['一格一格，像老胶片', 'Frame by frame, like old film'], ['十月，又来了', 'October, again']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ ps: [tp(c, 40, 420, 300), tp(c, 140, 380, 280), tp(c, 240, 400, 300)], tape: M.box(c, 380, 90, { width: '160px', height: '44px', background: 'rgba(255,230,150,.75)', transform: 'rotate(-6deg)' }) }),
       (s, t, a) => { s.ps.forEach((p, i) => M.slap(p, t, a + .2 + i * .35, 99, { x: [140, 560, 300][i], y: [120, 160, 460][i], r: [-4, 5, 2][i] })); M.pop(s.tape, t, a + 1.4, 99, { from: .4, base: 'rotate(-6deg)' }); }],
      [c => ({ strip: M.box(c, 0, 300, { width: '3000px', height: '360px', background: '#15120f', backgroundImage: 'repeating-linear-gradient(90deg,#efe7d8 0 24px,transparent 24px 56px),repeating-linear-gradient(90deg,#efe7d8 0 24px,transparent 24px 56px)', backgroundSize: '100% 26px,100% 26px', backgroundPosition: '0 14px,0 320px', backgroundRepeat: 'no-repeat' }) }),
       (s, t, a) => { if (!s.f) { s.f = 1; for (let i = 0; i < 6; i++) M.img(s.strip, 30 + i * 470, 60, 440, 240, 20 + i * 45, { filter: 'sepia(.4)' }); } s.strip.style.transform = `translateX(${(-200 - (t - a) * 160).toFixed(1)}px)`; }],
      [c => ({ t: X(c, 640, 320, 120, INK, 'October,', 700, M.PF, { fontStyle: 'italic' }), t2: X(c, 760, 470, 120, '#b5452b', 'again.', 700, M.PF, { fontStyle: 'italic' }), cn: X(c, 650, 650, 52, INK, '十月，又来了', 900, M.SERIF) }),
       (s, t, a) => { M.hero(s.t, t, a - .1, 99); M.hero(s.t2, t, a + .3, 99); M.rise(s.cn, t, a + .7, 99); }]
    ] });
})();
