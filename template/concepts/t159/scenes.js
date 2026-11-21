/* T159 明暗快切 Flash Cut: black/white split, huge characters, the window flips B&W ↔ colour on beats. */
(function () { const M = K.T.mo, X = M.X, R = '#e63946';
  const split = (c, inv) => { M.box(c, 0, 0, { width: '960px', height: '1080px', background: inv ? '#fff' : '#000' }); M.box(c, 960, 0, { width: '960px', height: '1080px', background: inv ? '#000' : '#fff' }); };
  const beat = (s, t, a) => { const k = Math.floor((t - a) * 2.5); s.bg.style.opacity = k % 2; };
  M.story({ bg: '#000', sbg: ['#000', '#fff', '#000'], tr: ['shutter', 'shutter'], ring: () => ({ color: '#ffffff', width: 10, shadow: .4 }),
    wins: [M.c(760, 300, 400), M.q(110, 240, 520, 520, 0), M.c(1400, 120, 380)],
    caps: [['节奏感，靠快切', 'Rhythm comes from fast cuts'], ['一明一暗，一拍一切', 'Light, dark — one cut per beat'], ['剪得快，看得爽', 'Cut fast, feels great']], port: { box: [0, 40, 1920, 1000] },
    scenes: [
      [c => { split(c); return { bg: M.box(c, 0, 0, { width: '1920px', height: '1080px', background: 'linear-gradient(90deg,#fff 50%,#000 50%)' }), l: X(c, 200, 280, 460, '#fff', '快', 900, M.CN, { mixBlendMode: 'difference', zIndex: 5 }), r: X(c, 1260, 280, 460, '#fff', '切', 900, M.CN, { mixBlendMode: 'difference', zIndex: 5 }), bar: M.box(c, 0, 1040, { width: '1920px', height: '10px', background: R, transformOrigin: '0 50%' }) }; },
       (s, t, a) => { M.pop(s.l, t, a + .1, 99, { from: 1.6 }); M.pop(s.r, t, a + .3, 99, { from: 1.6 }); if (t > a + .8) beat(s, t, a); else s.bg.style.opacity = 0; s.bar.style.transform = `scaleX(${Math.min(1, Math.max(0, (t - a) / 3))})`; }],
      [c => ({ w: ['一明', '一暗', '一拍', '一切'].map((n, i) => X(c, 760 + (i % 2) * 520, 220 + Math.floor(i / 2) * 340, 200, i % 2 ? '#fff' : '#000', n, 900, M.CN, { background: i % 2 ? '#000' : 'transparent', padding: '0 20px' })) }),
       (s, t, a) => s.w.forEach((e, i) => { e.style.opacity = t > a - .1 + i * .4 ? 1 : 0; e.style.transform = `scale(${(1 + .3 * Math.max(0, 1 - (t - a + .1 - i * .4) * 6)).toFixed(3)})`; })],
      [c => { split(c, 1); return { bg: M.box(c, 0, 0, { width: '1920px', height: '1080px', background: R }), l: X(c, 160, 320, 260, '#000', '剪得快', 900), r: X(c, 160, 620, 140, '#fff', '看得爽 ✦', 900) }; },
       (s, t, a) => { s.bg.style.opacity = (Math.floor((t - a) * 3) % 2) * (t < a + 1.5); M.hero(s.l, t, a - .1, 99); M.hero(s.r, t, a + .3, 99); }]
    ] });
})();
