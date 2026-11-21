/* T146 一镜横移 One-Take Pan: a skyline pans while the sky goes dawn → dusk → night (scenes = time of day). */
(function () { const M = K.T.mo, X = M.X;
  const SKY = 'M0 300 V160 H70 V120 H110 V60 L135 35 L160 60 V120 H240 V150 H300 V90 H350 V150 H430 V110 L470 80 L510 110 V160 H600 V130 H660 V170 H740 V100 H790 V170 H860 V140 H940 V180 H1000 V300Z';
  const city = (c, col, lights) => { const g = M.box(c, 0, 0, { width: '4000px', height: '1080px' }); for (let k = 0; k < 4; k++) M.svg(g, k * 1000, 640, 1000, 300, `<path d="${SKY}" fill="${col}"/>` + (lights ? Array.from({ length: 30 }, (_, i) => `<rect x="${20 + i * 32}" y="${180 + (i * 37) % 90}" width="8" height="8" fill="#ffd27a"/>`).join('') : '')); M.box(g, 0, 940, { width: '4000px', height: '140px', background: col }); return g; };
  M.story({ bg: '#1a2b5f', sbg: ['linear-gradient(#ffd9a8,#f7b267 60%,#f4845f)', 'linear-gradient(#4f9be0,#bfe3ff)', 'linear-gradient(#0b1026,#1d2a5f)'], tr: ['blur', 'blur'], ring: () => ({ color: '#ffffff', width: 6, shadow: .4 }),
    wins: [M.c(1480, 100, 320), M.c(1480, 100, 320), M.c(1480, 100, 320)],
    caps: [['清晨，城市醒来', 'Dawn — the city wakes up'], ['正午，人来人往', 'Noon — people everywhere'], ['入夜，灯一盏盏亮起', 'Night — lights come on one by one']], port: { box: [0, 40, 1920, 1000] },
    scenes: [
      [c => ({ sun: M.box(c, 700, 560, { width: '200px', height: '200px', borderRadius: '50%', background: '#fff0c2', boxShadow: '0 0 80px #ffd27a' }), g: city(c, '#5a3a4a'), t: X(c, 120, 120, 80, '#5a2a2a', '清晨 06:00') }),
       (s, t, a) => { s.g.style.transform = `translateX(${(-t * 60).toFixed(1)}px)`; s.sun.style.transform = `translateY(${(-160 * M.o3((t - a) / 3)).toFixed(1)}px)`; M.hero(s.t, t, a + .2, 99); }],
      [c => ({ sun: M.box(c, 900, 120, { width: '160px', height: '160px', borderRadius: '50%', background: '#fffbe6', boxShadow: '0 0 80px #fff3b0' }), g: city(c, '#3d5a80'), t: X(c, 120, 120, 80, '#1d3557', '正午 12:00') }),
       (s, t, a) => { s.g.style.transform = `translateX(${(-t * 60).toFixed(1)}px)`; M.hero(s.t, t, a, 99); }],
      [c => ({ moon: M.box(c, 300, 140, { width: '130px', height: '130px', borderRadius: '50%', boxShadow: 'inset -34px -8px 0 #fff1c1', transform: 'rotate(-20deg)' }), g: city(c, '#0e1330', 1), t: X(c, 600, 120, 80, '#ffd27a', '入夜 20:00') }),
       (s, t, a) => { s.g.style.transform = `translateX(${(-t * 60).toFixed(1)}px)`; [...s.g.querySelectorAll('rect')].forEach((r, i) => { r.style.opacity = t > a + (i % 30) * .05 ? 1 : 0; }); M.pop(s.moon, t, a, 99, { from: .4, base: 'rotate(-20deg)' }); M.hero(s.t, t, a + .2, 99); }]
    ] });
})();
