/* T93 Photo Slideshow 照片轮播 · 10 s sample (no presenter window). Photos = frames from the sample clip (1080p, downscaled); Ken Burns + crossfades + bilingual title cards. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, INK = '#fff';
  const PH = [[40, '01', '出发', 'Setting off', .4, 3.65], [150, '02', '路上', 'On the way', 3.45, 6.85], [270, '03', '到达', 'Arrived', 6.65, 10.3]];
  M.setup({ noface: true, bg: '#111', port: { box: [380, 0, 1160, 1080] },
    captions: M.caps([['这一周的高光时刻', 'Highlights of the week'], ['每一张，都有故事', 'Every photo has a story'], ['下周见', 'See you next week']]),
    build(L) { const s = {};
      s.ph = PH.map(([fr, n, c, e]) => { const w = M.box(L, 0, 0, { width: '1920px', height: '1080px', overflow: 'hidden' }); const i = el(w, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', transformOrigin: '50% 35%' }); i.src = `../../sample10/media/eva1080/f_${String(fr).padStart(5, '0')}.jpg`;
        el(w, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: 'linear-gradient(90deg, rgba(0,0,0,.55), transparent 50%)' });
        w.t = M.box(w, C.portrait ? 420 : 110, C.portrait ? 560 : 360, {}); M.txt(w.t, 0, 0, f(700, 34, M.MONO), '#ffd166', n); M.txt(w.t, 0, 50, f(900, 120, M.CN), INK, c); M.txt(w.t, 4, 200, f('italic 700', 44, M.PF), '#e9e2d6', e); w.i = i; return w; });
      return s; },
    update(s, t) { s.ph.forEach((w, k) => { const [, , , , a, b] = PH[k], v = M.env(t, a, b, .5, .4), u = Math.max(0, Math.min(1, (t - a) / (b - a)));
      w.style.opacity = k === 0 && t < .4 ? 1 : v.a.toFixed(3); w.i.style.transform = `scale(${(1.0 + .1 * u).toFixed(4)}) translate(${((k % 2 ? 1 : -1) * 30 * u).toFixed(1)}px, 0)`; M.hero(w.t, t, a + .35, b, { dx: -40, noclip: true }); }); } });
})();
