/* T153 储能面板 Power Panel (logo/text only): battery fills, live stats, charging flow. Sample numbers. */
(function () { const M = K.T.mo, X = M.X, G = '#3fe0b0', BG = '#0d1117';
  const batt = (c, x, y) => { const g = M.box(c, x, y, { width: '360px', height: '520px', border: `6px solid ${G}`, borderRadius: '36px', boxSizing: 'border-box', overflow: 'hidden' }); g.f = M.box(g, 14, 500, { width: '320px', height: '0px', borderRadius: '22px', background: `linear-gradient(${G},#1f8f6f)` }); g.n = X(g, 40, 40, 100, '#fff', '0%', 400, M.AN); return g; };
  const fill = (g, v) => { g.f.style.height = (490 * v / 100) + 'px'; g.f.style.top = (500 - 490 * v / 100) + 'px'; g.n.textContent = Math.round(v) + '%'; };
  M.story({ noface: true, bg: BG, sbg: [BG, '#0f1520', BG], tr: ['wipe', 'zoom'],
    caps: [['一块户外电源', 'A portable power station'], ['输出、续航、温度，一目了然', 'Output, runtime, temperature at a glance'], ['充满，出发（示例数据）', 'Full — let’s go (sample data)']], port: { box: [200, 60, 1520, 880] },
    scenes: [
      [c => ({ b: batt(c, 780, 220), bolt: M.svg(c, 900, 360, 120, 200, `<path d="M70 0 L10 110 H55 L40 200 L110 80 H62Z" fill="${G}"/>`), t: X(c, 200, 160, 64, '#fff', 'POWER', 400, M.AN) }),
       (s, t, a) => { M.pop(s.b, t, a, 99, { from: .6 }); fill(s.b, 68 * M.o3((t - a - .3) / 2)); s.bolt.style.opacity = .3 + .7 * Math.abs(Math.sin(t * 3)); M.rise(s.t, t, a + .3, 99); }],
      [c => ({ b: batt(c, 200, 200), st: [['输出', '1200 W'], ['剩余', '4.2 h'], ['温度', '32°C']].map(([k, v], i) => { const g = M.box(c, 680, 220 + i * 170, { width: '760px', height: '140px', borderRadius: '20px', background: '#161c27', border: '2px solid #243042', boxSizing: 'border-box' }); X(g, 30, 18, 32, '#8aa0b8', k); X(g, 30, 60, 60, G, v, 400, M.AN); return g; }) }),
       (s, t, a) => { M.slide(s.b, t, a - .15, 99, { dx: -200 }); fill(s.b, 68); s.st.forEach((g, i) => M.slide(g, t, a + i * .2, 99, { dx: 200 })); }],
      [c => ({ b: batt(c, 780, 200), flow: M.path(c, 0, 440, 1920, 60, 'M0 30 H760 M1160 30 H1920', G, 6, 'stroke-dasharray="30 30"'), t: X(c, 760, 760, 80, '#fff', '100% · 出发', 900), sm: X(c, 200, 900, 26, '#5a6b80', 'SAMPLE DATA 示例') }),
       (s, t, a) => { M.pop(s.b, t, a - .1, 99, { from: .8 }); fill(s.b, 68 + 32 * M.o3((t - a) / 1.6)); s.flow.setAttribute('stroke-dashoffset', (-t * 200).toFixed(0)); s.flow.style.opacity = M.env(t, a, 99).a; M.hero(s.t, t, a + 1.2, 99); M.rise(s.sm, t, a + .5, 99); }]
    ] });
})();
