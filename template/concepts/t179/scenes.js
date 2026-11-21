/* T179 城市夜跑 Night Run: orange dusk skyline with lit windows, a heart-rate line runs across, km counter. */
(function () { const M = K.T.mo, X = M.X, OR = '#ff8a3d';
  const city = c => M.svg(c, 0, 520, 1920, 560, Array.from({ length: 14 }, (_, i) => { const x = i * 140, h = 220 + (i * 71) % 300; return `<rect x="${x}" y="${560 - h}" width="110" height="${h}" fill="#2a120a"/>` + Array.from({ length: Math.floor(h / 40) * 3 }, (_, k) => `<rect x="${x + 12 + (k % 3) * 32}" y="${580 - h + Math.floor(k / 3) * 40}" width="18" height="22" fill="#ffb470" opacity="${(k * 7 + i) % 5 ? .15 : .9}"/>`).join(''); }).join(''));
  const hr = c => M.path(c, 0, 220, 1920, 200, 'M0 120 H300 L340 30 L380 180 L420 120 H900 L940 20 L980 190 L1020 120 H1500 L1540 40 L1580 170 L1620 120 H1920', '#fff', 6);
  M.story({ bg: '#3a1a0e', sbg: ['linear-gradient(#ff8a3d,#7a2e12 70%,#2a120a)', 'linear-gradient(#c2451c,#3a1a0e)', 'linear-gradient(#5a2414,#120806)'], tr: ['push', 'blur'], ring: () => ({ color: '#ffffff', width: 8, shadow: .4 }),
    wins: [M.c(1440, 100, 360), M.c(1440, 100, 360), M.q(110, 120, 400, 480, 20)],
    caps: [['下班后，城市夜跑', 'After work: a city night run'], ['心率稳在 150 左右（示例）', 'Heart rate steady around 150 (sample)'], ['5 公里，收工', '5 km — done']], port: { box: [0, 40, 1920, 1000] },
    scenes: [
      [c => ({ ci: city(c), h: hr(c), t: X(c, 100, 100, 80, '#fff', '城市夜跑 · 心率', 900) }), (s, t, a) => { M.rise(s.ci, t, a, 99, { dy: 120 }); s.ci.style.transform += ` translateX(${(-t * 20).toFixed(0)}px)`; M.draw(s.h, t, a + .4, 2.2, 99); M.hero(s.t, t, a + .2, 99); }],
      [c => ({ ci: city(c), n: X(c, 160, 220, 260, '#fff', '150', 400, M.AN), u: X(c, 170, 520, 50, '#ffd0a8', 'BPM · 稳', 700) }),
       (s, t, a) => { s.ci.style.opacity = 1; s.ci.style.transform = `translateX(${(-t * 20).toFixed(0)}px)`; M.hero(s.n, t, a, 99); M.count(s.n, 150, t, a, 1); s.n.style.transform += ` scale(${(1 + .04 * Math.max(0, Math.sin(t * 8))).toFixed(3)})`; M.rise(s.u, t, a + .4, 99); }],
      [c => ({ ci: city(c), tr: M.path(c, 0, 0, 1920, 1080, 'M700 900 C 900 700, 1200 820, 1400 600 S 1700 400, 1800 300', OR, 10), n: X(c, 700, 160, 180, '#fff', '5.0 km', 400, M.AN), d: M.box(c, 0, 0, { width: '36px', height: '36px', borderRadius: '50%', background: '#fff', boxShadow: `0 0 20px ${OR}` }) }),
       (s, t, a) => { s.ci.style.opacity = 1; M.draw(s.tr, t, a - .1, 1.8, 99); const L = s.tr.getTotalLength(), p = s.tr.getPointAtLength(L * M.io((t - a + .1) / 1.8)); s.d.style.transform = `translate(${(p.x - 18).toFixed(0)}px, ${(p.y - 18).toFixed(0)}px)`; M.hero(s.n, t, a + .3, 99); }]
    ] });
})();
