/* T157 转化漏斗 Funnel (business): a funnel builds stage by stage, dots fall through and thin out, conversion rate. Sample data. */
(function () { const M = K.T.mo, X = M.X, INK = '#1f2a44', CL = ['#4361ee', '#4cc9f0', '#7209b7', '#f72585'], ST = [['曝光', 'Views', 10000], ['点击', 'Clicks', 2400], ['试用', 'Trials', 600], ['付费', 'Paid', 120]];
  const funnel = c => ST.map(([cn, en, v], i) => { const w = 900 - i * 190, g = M.box(c, 560 - w / 2 + 160, 180 + i * 150, { width: w + 'px', height: '120px', background: CL[i], clipPath: 'polygon(0 0,100% 0,92% 100%,8% 100%)', color: '#fff', font: M.f(900, 44, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 0' }, `${cn} ${en}`); g.v = v; return g; });
  M.story({ bg: '#f4f6fb', sbg: ['#f4f6fb', '#eef1f8', '#f4f6fb'], tr: ['rise', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1400, 180, 400, 480, 20), M.q(1400, 180, 400, 480, 20), M.c(110, 200, 360)],
    caps: [['用户，是一层层筛出来的', 'Customers come through a funnel'], ['一万次曝光，一百二十个付费（示例）', '10,000 views → 120 paid (sample)'], ['转化率 1.2%，先优化第一层', '1.2% conversion — fix the top first']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ f: funnel(c) }), (s, t, a) => s.f.forEach((g, i) => { g.style.opacity = t > a + .2 + i * .3 ? 1 : 0; g.style.transform = `scaleY(${M.os((t - a - .2 - i * .3) / .4).toFixed(3)})`; })],
      [c => ({ f: funnel(c), n: ST.map(([, , v], i) => X(c, 1180 - i * 95, 210 + i * 150, 44, CL[i], '0', 400, M.AN)), d: Array.from({ length: 40 }, () => M.box(c, 0, 0, { width: '14px', height: '14px', borderRadius: '50%', background: INK })) }),
       (s, t, a) => { s.f.forEach(g => { g.style.opacity = 1; }); s.n.forEach((e, i) => { M.rise(e, t, a + i * .3, 99); M.count(e, ST[i][2], t, a + i * .3, .6, v => v.toLocaleString()); }); s.d.forEach((e, i) => { const u = ((t - a) * .6 + i / 40) % 1, lvl = Math.floor(u * 4), keep = i % [1, 4, 16, 40][Math.min(3, lvl)] === 0; e.style.opacity = keep ? .7 : 0; e.style.transform = `translate(${(720 + ((i * 37) % 9 - 4) * (110 - lvl * 24)).toFixed(0)}px, ${(180 + u * 600).toFixed(0)}px)`; }); }],
      [c => ({ r: X(c, 760, 260, 220, '#f72585', '1.2%', 400, M.AN), l: X(c, 770, 520, 56, INK, '先优化第一层', 900), ar: M.path(c, 760, 620, 700, 120, 'M0 60 H620 M570 20 L630 60 L570 100', INK, 8) }),
       (s, t, a) => { M.pop(s.r, t, a - .1, 99, { from: 1.6 }); M.hero(s.l, t, a + .4, 99); M.draw(s.ar, t, a + .8, .6, 99); }]
    ] });
})();
