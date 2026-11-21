/* T186 养车四笔账 Car Costs: four monthly cost bars grow, a total, and a donut split. Sample figures. */
(function () { const M = K.T.mo, X = M.X, INK = '#264653', CL = ['#e76f51', '#2a9d8f', '#e9c46a', '#264653'], D = [['油费', 1200], ['保险', 500], ['保养', 300], ['停车', 600]];
  M.story({ bg: '#f3f5f7', sbg: ['#f3f5f7', '#eef1f4', '#f3f5f7'], tr: ['wipe', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1420, 160, 380, 480, 20), M.c(1440, 160, 360), M.q(110, 180, 400, 480, 20)],
    caps: [['养一台车，每月四笔账（示例）', 'Four monthly costs of a car (sample)'], ['加起来，2600 元', 'Total: ¥2,600'], ['油费，占了快一半', 'Fuel is almost half']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ h: X(c, 160, 110, 40, '#6b7c86', '每月养车账（示例）'), b: D.map(([k, v], i) => { const g = M.box(c, 160, 220 + i * 160, {}); g.bar = M.box(g, 0, 0, { width: '0px', height: '110px', borderRadius: '14px', background: CL[i], color: '#fff', font: M.f(900, 50, M.CN), display: 'flex', alignItems: 'center', paddingLeft: '30px', boxSizing: 'border-box', overflow: 'hidden', whiteSpace: 'nowrap' }, k); g.n = X(g, 0, 26, 54, CL[i], '¥' + v, 400, M.AN); g.v = v; return g; }) }),
       (s, t, a) => { M.rise(s.h, t, a + .1, 99); s.b.forEach((g, i) => { g.style.opacity = M.env(t, a + .2 + i * .15, 99).a; const w = g.v * .85 * M.o3((t - a - .3 - i * .15) / .8); g.bar.style.width = w + 'px'; g.n.style.transform = `translateX(${(w + 30).toFixed(0)}px)`; }); }],
      [c => ({ n: X(c, 160, 300, 260, INK, '¥0', 400, M.AN), u: X(c, 170, 600, 50, '#6b7c86', '每月合计 / month'), eq: X(c, 170, 200, 40, '#6b7c86', '1200 + 500 + 300 + 600', 700, M.MONO) }),
       (s, t, a) => { M.rise(s.eq, t, a - .1, 99); M.hero(s.n, t, a + .2, 99); M.count(s.n, 2600, t, a + .2, 1.4, v => '¥' + v.toLocaleString()); M.rise(s.u, t, a + .6, 99); }],
      [c => { let acc = 0; const arcs = D.map(([k, v], i) => { const s = `<circle class="a" cx="250" cy="250" r="180" fill="none" stroke="${CL[i]}" stroke-width="80" pathLength="2600" stroke-dasharray="0 2600" stroke-dashoffset="${-acc}" transform="rotate(-90 250 250)" data-v="${v}"/>`; acc += v; return s; }).join(''); return { d: M.svg(c, 700, 180, 500, 500, arcs), t: X(c, 1260, 300, 90, CL[0], '46%', 400, M.AN), l: X(c, 1266, 430, 44, INK, '油费 Fuel', 900) }; },
       (s, t, a) => { M.pop(s.d, t, a - .1, 99, { from: .7 }); [...s.d.querySelectorAll('.a')].forEach((p, i) => { const u = M.o3((t - a - i * .2) / .6); p.setAttribute('stroke-dasharray', `${(p.dataset.v * u).toFixed(0)} 2600`); }); M.hero(s.t, t, a + .9, 99); M.rise(s.l, t, a + 1.1, 99); }]
    ] });
})();
