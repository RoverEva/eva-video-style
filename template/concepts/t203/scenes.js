/* T203 天气播报 Weather Desk: a forecast board — animated icons (sun, cloud, rain), temperatures count, week strip. Sample forecast. */
(function () { const M = K.T.mo, X = M.X, NV = '#0b3d91', SKY = '#e8f3ff';
  const sun = (c, x, y, s) => M.svg(c, x, y, 200 * s, 200 * s, `<g transform="scale(${s})"><circle cx="100" cy="100" r="48" fill="#ffc93c"/>${Array.from({ length: 8 }, (_, i) => `<rect x="96" y="14" width="8" height="30" rx="4" fill="#ffc93c" transform="rotate(${i * 45} 100 100)"/>`).join('')}</g>`, { transformOrigin: '50% 50%' });
  const cloud = (c, x, y, s, col) => M.svg(c, x, y, 260 * s, 160 * s, `<g transform="scale(${s})"><path d="M60 140 C 10 140, 10 80, 60 80 C 60 30, 140 20, 160 70 C 200 40, 250 80, 220 140Z" fill="${col || '#fff'}" stroke="#c9d8ea" stroke-width="4"/></g>`);
  const rain = (c, x, y) => Array.from({ length: 10 }, (_, i) => M.box(c, x + (i % 5) * 40, y, { width: '6px', height: '30px', borderRadius: '3px', background: '#4f9dff' }));
  M.story({ bg: SKY, sbg: ['linear-gradient(#cfe6ff,#f3f9ff)', 'linear-gradient(#a9c3e0,#dce8f5)', 'linear-gradient(#cfe6ff,#f3f9ff)'], tr: ['wipe', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.q(1380, 200, 420, 500, 24), M.c(110, 220, 360), M.q(1380, 200, 420, 500, 24)],
    caps: [['明天，晴（示例）', 'Tomorrow: sunny (sample)'], ['后天下雨，记得带伞', 'Rain the day after — bring an umbrella'], ['一周天气，一眼看完', 'The week at a glance']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ s: sun(c, 260, 220, 1.6), cl: cloud(c, 470, 380, .9), t: X(c, 760, 240, 200, NV, '26°', 400, M.AN), l: X(c, 770, 500, 50, NV, '明天 · 晴', 900) }),
       (s, t, a) => { M.pop(s.s, t, a + .1, 99, { from: .3 }); s.s.style.transform += ` rotate(${(t * 30).toFixed(0)}deg)`; M.slide(s.cl, t, a + .4, 99, { dx: 300 }); s.cl.style.transform += ` translateX(${(20 * Math.sin(t)).toFixed(0)}px)`; M.rise(s.t, t, a + .3, 99); M.count(s.t, 26, t, a + .3, 1, v => v + '°'); M.rise(s.l, t, a + .6, 99); }],
      [c => ({ cl: cloud(c, 700, 200, 1.6, '#e3eaf3'), r: rain(c, 820, 470), u: M.svg(c, 1100, 520, 220, 220, `<path d="M10 110 A 100 100 0 0 1 210 110 Z" fill="#ff5c7a"/><path d="M110 110 V190 C 110 215, 80 215, 80 195" fill="none" stroke="#333" stroke-width="8"/>`, { transformOrigin: '50% 100%' }), l: X(c, 700, 780, 54, NV, '后天 · 小雨 18°', 900) }),
       (s, t, a) => { M.rise(s.cl, t, a - .1, 99, { dy: -60 }); s.r.forEach((e, i) => { e.style.opacity = t > a + .3 ? .8 : 0; e.style.transform = `translateY(${(((t * 400) + i * 37) % 260).toFixed(0)}px) rotate(12deg)`; }); M.pop(s.u, t, a + .8, 99, { from: 0 }); s.u.style.transform += ` rotate(${(8 * Math.sin(t * 3)).toFixed(1)}deg)`; M.rise(s.l, t, a + .5, 99); }],
      [c => ({ d: [['一', '☀', 26], ['二', '☁', 22], ['三', '☂', 18], ['四', '☂', 17], ['五', '⛅', 21], ['六', '☀', 25], ['日', '☀', 27]].map(([n, ic, v], i) => { const g = M.card(c, 120 + i * 175, 300, 150, 300, '#fff'); X(g, 50, 24, 40, '#556', n, 900); X(g, 34, 90, 80, NV, ic, 400, M.CN); X(g, 30, 210, 50, NV, v + '°', 400, M.AN); return g; }) }),
       (s, t, a) => s.d.forEach((g, i) => M.rise(g, t, a - .1 + i * .1, 99, { dy: 80 }))]
    ] });
})();
