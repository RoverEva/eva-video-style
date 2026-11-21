/* T176 体能仪表 Fitness HUD: heart-rate ring, live stats, splits bar chart. Sample workout. */
(function () { const M = K.T.mo, X = M.X, LM = '#c6ff3a', BG = '#0b0d0a';
  const ring = (c, x, y) => M.svg(c, x, y, 440, 440, `<circle cx="220" cy="220" r="190" fill="none" stroke="#1e2a14" stroke-width="28"/><circle class="p" cx="220" cy="220" r="190" fill="none" stroke="${LM}" stroke-width="28" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 220 220)"/>`);
  M.story({ bg: BG, sbg: [BG, '#0d100b', BG], tr: ['zoom', 'push'], ring: () => ({ color: LM, width: 5, shadow: .5 }),
    wins: [M.q(1360, 200, 420, 480, 20), M.c(1440, 160, 360), M.q(110, 180, 420, 500, 20)],
    caps: [['今天，跑了 6.4 公里（示例）', 'Today: 6.4 km (sample)'], ['心率、配速、卡路里', 'Heart rate, pace, calories'], ['每一公里，都比上次快', 'Every km faster than last time']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ r: ring(c, 160, 220), n: X(c, 270, 330, 140, LM, '0', 400, M.INTER), u: X(c, 290, 500, 34, '#7a9a4a', 'BPM', 700, M.MONO), hb: M.path(c, 640, 380, 640, 160, 'M0 80 H180 L220 10 L260 150 L300 80 H640', LM, 6) }),
       (s, t, a) => { M.pop(s.r, t, a, 99, { from: .6 }); s.r.querySelector('.p').setAttribute('stroke-dashoffset', (1 - .78 * M.o3((t - a - .2) / 1.6)).toFixed(3)); M.rise(s.n, t, a + .2, 99); M.count(s.n, 142, t, a + .2, 1.6); M.rise(s.u, t, a + .4, 99); M.draw(s.hb, t, a + .5, 1, 99); s.hb.parentNode.style.transform = `scaleY(${(1 + .1 * Math.max(0, Math.sin(t * 8))).toFixed(2)})`; }],
      [c => ({ st: [['配速', "5'12\""], ['距离', '6.4 km'], ['卡路里', '412']].map(([k, v], i) => { const g = M.box(c, 160 + i * 400, 300, {}); X(g, 0, 0, 36, '#8aa060', k); X(g, 0, 60, 100, '#fff', v, 400, M.INTER); return g; }) }),
       (s, t, a) => s.st.forEach((g, i) => M.rise(g, t, a - .15 + i * .2, 99, { dy: 80 }))],
      [c => ({ bars: [5.6, 5.4, 5.3, 5.2, 5.0, 4.9].map((v, i) => { const b = M.box(c, 720 + i * 170, 0, { width: '110px', height: '0px', background: i === 5 ? LM : '#3a4a24', borderRadius: '12px 12px 0 0' }); b.v = (6 - v) * 500; X(c, 730 + i * 170, 860, 30, '#8aa060', 'KM' + (i + 1), 700, M.MONO); return b; }), t: X(c, 720, 140, 64, '#fff', '一次比一次快', 900) }),
       (s, t, a) => { s.bars.forEach((b, i) => { const h = b.v * M.o3((t - a - i * .12) / .6); b.style.height = h + 'px'; b.style.top = (840 - h) + 'px'; }); M.hero(s.t, t, a + .8, 99); }]
    ] });
})();
