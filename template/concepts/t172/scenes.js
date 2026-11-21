/* T172 赛博像素 Cyber Pixel (game): neon grid, item card scanline-reveals, stat bars, rarity glow. */
(function () { const M = K.T.mo, X = M.X, CY = '#3ff0ff', PK = '#ff2bd6';
  const grid = c => M.box(c, -400, -400, { width: '2720px', height: '1880px', backgroundImage: `linear-gradient(rgba(255,43,214,.18) 2px,transparent 2px),linear-gradient(90deg,rgba(255,43,214,.18) 2px,transparent 2px)`, backgroundSize: '64px 64px' });
  const card = (c, x, y, col, name, stat) => { const g = M.box(c, x, y, { width: '420px', height: '540px', border: `6px solid ${col}`, background: '#140226', boxShadow: `0 0 40px ${col}`, boxSizing: 'border-box', overflow: 'hidden' }); M.svg(g, 90, 60, 230, 230, `<polygon points="70,0 160,0 230,70 230,160 160,230 70,230 0,160 0,70" fill="${col}"/>` + Array.from({ length: 10 }, (_, i) => `<rect x="0" y="${i * 23 + 12}" width="230" height="8" fill="#140226"/>`).join('')); X(g, 40, 340, 48, col, name, 400, M.MONO); X(g, 40, 410, 30, PK, stat, 700, M.MONO); g.scan = M.box(g, 0, 0, { width: '420px', height: '540px', background: '#140226' }); return g; };
  M.story({ bg: '#0d0221', sbg: ['#0d0221', '#10032a', '#0d0221'], tr: ['shutter', 'zoom'], ring: () => ({ color: CY, width: 5, glow: 'rgba(63,240,255,.5)', shadow: .5 }),
    wins: [M.q(1300, 160, 460, 540, 6), M.q(110, 160, 420, 520, 6), M.q(1300, 160, 460, 540, 6)],
    caps: [['开箱，出了一件传说装备', 'Unboxed: a legendary item'], ['攻击、暴击、速度，全面提升', 'Attack, crit, speed — all up'], ['这把，必须留着', 'This one’s a keeper']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ g: grid(c), cd: card(c, 300, 220, CY, 'LEGENDARY', 'ATK +120 · RARE') }), (s, t, a) => { M.drift(s.g, t, 10); M.pop(s.cd, t, a + .1, 99, { from: .8 }); const u = M.io((t - a - .4) / 1.2); s.cd.scan.style.clipPath = `inset(${(100 * u).toFixed(1)}% 0 0 0)`; s.cd.style.boxShadow = `0 0 ${(40 + 30 * Math.sin(t * 4)).toFixed(0)}px ${CY}`; }],
      [c => ({ g: grid(c), b: [['ATK', .9], ['CRIT', .7], ['SPD', .55]].map(([k, v], i) => { const r = M.box(c, 680, 280 + i * 160, {}); X(r, 0, 0, 44, CY, k, 400, M.MONO); r.bar = M.box(r, 200, 10, { width: '0px', height: '40px', background: `linear-gradient(90deg,${PK},${CY})`, boxShadow: `0 0 20px ${PK}` }); r.v = v; return r; }) }),
       (s, t, a) => { M.drift(s.g, t, 10); s.b.forEach((r, i) => { M.slide(r, t, a - .15 + i * .2, 99, { dx: 100 }); const u = M.o3((t - a - .2 - i * .2) / .8); r.bar.style.width = (r.v * 800 * u) + 'px'; }); }],
      [c => ({ g: grid(c), cd: card(c, 300, 220, PK, 'KEEPER', 'SAVED · ★★★★★'), t: X(c, 780, 680, 60, '#fff', '必须留着', 900, M.CN, { textShadow: `0 0 20px ${PK}` }) }),
       (s, t, a) => { M.drift(s.g, t, 10); M.pop(s.cd, t, a - .1, 99, { from: .6 }); s.cd.scan.style.display = 'none'; s.cd.style.transform += ` rotate(${(-4 + 2 * Math.sin(t * 2)).toFixed(1)}deg)`; M.hero(s.t, t, a + .5, 99); }]
    ] });
})();
