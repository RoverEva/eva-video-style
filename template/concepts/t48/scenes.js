/* T48 Synthwave 80s 合成波 · 10 s sample (illustrative copy). Striped sun behind the window, scrolling perspective grid, chrome type. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, PK = '#ff4fd8', CY = '#4ff2ff';
  M.setup({ bg: 'linear-gradient(180deg,#0d0221 0%,#2a0845 55%,#5b0f5c 100%)', win: { x: 1260, y: 140, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: PK, width: 6, glow: 'rgba(255,79,216,.7)', shadow: .5 }), port: { box: [90, 60, 1060, 720] },
    captions: M.caps([['复古风又回来了', 'Retro is back'], ['八十年代的颜色，今天的内容', 'Eighties colours, today’s story'], ['按下播放键', 'Press play']]),
    build(L) { const s = {};
      s.floor = M.bg(M.box(L, -500, 600, { width: '2920px', height: '480px', perspective: '420px', overflow: 'hidden' }));
      s.g = el(s.floor, 'div', 'abs', { left: 0, top: '-200px', width: '2920px', height: '1200px', transformOrigin: '50% 0', transform: 'rotateX(62deg)', backgroundImage: `linear-gradient(${PK} 3px, transparent 3px), linear-gradient(90deg, ${PK} 3px, transparent 3px)`, backgroundSize: '120px 120px', opacity: .75 });
      s.sun = M.att(M.svg(L, 1190, 70, 640, 640, `<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe259"/><stop offset="1" stop-color="#ff3d9a"/></linearGradient></defs><circle cx="320" cy="320" r="320" fill="url(#sg)"/>` + [0, 1, 2, 3, 4].map(i => `<rect x="0" y="${400 + i * 46}" width="640" height="${8 + i * 4}" fill="#2a0845"/>`).join('')));
      s.t = M.txt(L, 104, 150, f(400, 190, M.AN), 'transparent', 'RETRO', { backgroundImage: 'linear-gradient(180deg,#ffffff 0%,#9fd8ff 45%,#2b1055 50%,#ff9de6 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextStroke: '2px #fff', letterSpacing: '.04em', lineHeight: 1 });
      s.cn = M.txt(L, 110, 360, f(900, 76, M.CN), '#fff', '复古回来了', { textShadow: `0 0 12px ${PK}, 0 0 30px ${PK}` });
      s.sw = ['#ff4fd8', '#4ff2ff', '#ffe259', '#7b2fff'].map((c, i) => M.box(L, 112 + i * 110, 480, { width: '80px', height: '80px', borderRadius: '50%', background: c, boxShadow: `0 0 24px ${c}`, transformOrigin: '50% 50%' }));
      s.sl = M.txt(L, 560, 496, f(700, 34, M.INTER), CY, '#1984 PALETTE', { textShadow: `0 0 10px ${CY}` });
      s.play = M.txt(L, 110, 600, f(400, 84, M.AN), '#fff', '▶ PRESS PLAY', { textShadow: `0 0 14px ${CY}, 0 0 34px ${CY}`, letterSpacing: '.06em' });
      return s; },
    update(s, t) { s.g.style.backgroundPosition = `0 ${(t * 160).toFixed(1)}px`; s.floor.style.opacity = M.env(t, .4, 9.3, .6).a;
      M.pop(s.sun, t, .5, 9.2, { from: .6, din: .6 }); s.sun.style.transform += ` translateY(${(40 * (1 - M.o3((t - .5) / 1.2))).toFixed(1)}px)`;
      M.hero(s.t, t, .95, 9.2, { dx: -60 }); M.rise(s.cn, t, 1.35, 9.2);
      s.sw.forEach((e, i) => M.pop(e, t, 3.6 + i * .13, 9.2, { from: .2 })); M.slide(s.sl, t, 4.2, 9.2, { dx: -40 });
      M.hero(s.play, t, 6.85, 9.2); if (t > 7.3) s.play.style.opacity *= (Math.floor((t - 7.3) * 2.5) % 2 ? .55 : 1); } });
})();
