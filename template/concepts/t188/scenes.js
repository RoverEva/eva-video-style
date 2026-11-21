/* T188 自驾线路 Road Trip Lines: metro-style route draws stop by stop, km counter, altitude badge. Sample route. */
(function () { const M = K.T.mo, X = M.X, R = '#e63946', TL = '#2a9d8f', INK = '#222';
  const S = [[260, 760, '成都'], [620, 760, '康定'], [620, 440, '新都桥'], [1000, 440, '理塘'], [1000, 220, '巴塘'], [1300, 220, '拉萨']];
  const route = (c, n) => { const d = 'M' + S.slice(0, n).map(([x, y]) => `${x} ${y}`).join(' L'); const p = M.path(c, 0, 0, 1920, 1080, d, R, 20, 'stroke-linejoin="round"'); p.st = S.slice(0, n).map(([x, y, nm]) => { const g = M.box(c, x - 26, y - 26, { width: '52px', height: '52px', borderRadius: '50%', background: '#fff', border: `8px solid ${INK}`, boxSizing: 'border-box' }); g.l = X(c, x - 60, y + 40, 38, INK, nm, 900, M.CN, { width: '120px', textAlign: 'center' }); return g; }); return p; };
  M.story({ bg: '#f6f4ee', sbg: ['#f6f4ee', '#f2efe6', '#f6f4ee'], tr: ['slide', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1440, 380, 380, 460, 20), M.q(1440, 380, 380, 460, 20), M.c(1440, 400, 380)],
    caps: [['从成都出发', 'Starting from Chengdu'], ['一路向西，一站一站', 'Heading west, stop by stop'], ['2100 公里，到拉萨（示例）', '2,100 km to Lhasa (sample)']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ g: M.path(c, 0, 0, 1920, 1080, 'M120 900 H700 V600 H1300 V100', TL, 14, 'opacity=".35"'), r: route(c, 2) }), (s, t, a) => { M.draw(s.g, t, a, 1.4, 99); M.draw(s.r, t, a + .5, 1, 99); s.r.st.forEach((e, i) => { M.pop(e, t, a + .5 + i * 1, 99, { from: 0 }); M.rise(e.l, t, a + .6 + i * 1, 99); }); }],
      [c => ({ g: M.path(c, 0, 0, 1920, 1080, 'M120 900 H700 V600 H1300 V100', TL, 14, 'opacity=".35"'), r: route(c, 5) }), (s, t, a) => { s.g.parentNode.style.opacity = 1; M.draw(s.r, t, a - .4, 2.6, 99); s.r.st.forEach((e, i) => { M.pop(e, t, a - .4 + i * .55, 99, { from: 0 }); M.rise(e.l, t, a - .3 + i * .55, 99); }); }],
      [c => ({ r: route(c, 6), n: X(c, 160, 140, 110, R, '0 km', 400, M.AN), alt: M.box(c, 170, 290, { padding: '10px 24px', borderRadius: '30px', background: INK, color: '#fff', font: M.f(700, 34, M.MONO) }, '▲ 3650 m') }),
       (s, t, a) => { M.draw(s.r, t, a - 1, 1.2, 99); s.r.st.forEach((e, i) => { e.style.opacity = 1; e.l.style.opacity = 1; }); M.hero(s.n, t, a + .2, 99); M.count(s.n, 2100, t, a + .2, 1.4, v => v + ' km'); M.pop(s.alt, t, a + 1.2, 99, { from: .3 }); }]
    ] });
})();
