/* T131 一日旅程 Day Story (vlog). Photos are frames of the presenter's own clip. */
(function () { const M = K.T.mo, X = M.X, OR = '#e76f51';
  const photo = (c, f) => { const p = M.box(c, 0, 0, { width: '340px', height: '250px', background: '#fff', padding: '12px', boxSizing: 'border-box', boxShadow: '0 14px 24px rgba(0,0,0,.2)', transformOrigin: '50% 20%' }); M.img(p, 12, 12, 316, 226, f); return p; };
  M.story({ bg: '#fff7ec', sbg: ['linear-gradient(#ffe8c7,#fff7ec)', 'linear-gradient(#bde0fe,#fff)', 'linear-gradient(#1b2a5f,#3a2f6e)'], tr: ['wipe', 'blur'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 30), M.c(1460, 160, 340)],
    caps: [['早上 8 点，出发', '8 a.m. — off we go'], ['中午，随手拍几张', 'Noon — a few quick shots'], ['晚上，把今天收好', 'Night — saving today']], port: { box: [100, 40, 1820, 840] },
    scenes: [
      [c => ({ arc: M.path(c, 160, 160, 1100, 600, 'M20 580 A560 520 0 0 1 1080 580', OR, 6, 'stroke-dasharray=".02 .015"'), sun: M.box(c, 0, 0, { width: '90px', height: '90px', borderRadius: '50%', background: '#ffb703', boxShadow: '0 0 40px #ffb703' }), tm: X(c, 160, 620, 110, OR, '08:00', 400, M.AN), p: photo(c, 30) }),
       (s, t, a) => { M.rise(s.arc, t, a, 99); const u = M.io((t - a) / 2.6), ang = Math.PI * (1 - u * .35); s.sun.style.transform = `translate(${(710 + Math.cos(ang) * 540).toFixed(1)}px, ${(740 - Math.sin(ang) * 500).toFixed(1)}px)`; s.sun.style.opacity = M.env(t, a, 99).a;
         M.hero(s.tm, t, a + .3, 99); M.slap(s.p, t, a + .8, 99, { x: 620, y: 360, r: -5 }); }],
      [c => ({ tm: X(c, 640, 120, 110, '#1d3557', '12:00', 400, M.AN), ps: [photo(c, 120), photo(c, 160), photo(c, 200)] }),
       (s, t, a) => { M.hero(s.tm, t, a - .1, 99); s.ps.forEach((p, i) => M.slap(p, t, a + .2 + i * .3, 99, { x: 640 + i * 360, y: 330 + (i % 2) * 60, r: [-6, 4, -2][i] })); }],
      [c => ({ moon: M.box(c, 300, 160, { width: '160px', height: '160px', borderRadius: '50%', boxShadow: 'inset -40px -10px 0 #fff1c1', transform: 'rotate(-20deg)' }), st: Array.from({ length: 30 }, (_, i) => M.box(c, (i * 197) % 1300 + 100, (i * 83) % 600 + 60, { width: '5px', height: '5px', borderRadius: '50%', background: '#fff' })), tm: X(c, 300, 420, 110, '#ffd27a', '21:00', 400, M.AN), t: X(c, 300, 560, 60, '#fff', '把今天收好') }),
       (s, t, a) => { M.pop(s.moon, t, a - .1, 99, { from: .3, base: 'rotate(-20deg)' }); s.st.forEach((e, i) => { e.style.opacity = (M.env(t, a + i * .02, 99).a * (.4 + .6 * Math.abs(Math.sin(t * 2 + i)))).toFixed(2); }); M.hero(s.tm, t, a + .3, 99); M.rise(s.t, t, a + .6, 99); }]
    ] });
})();
