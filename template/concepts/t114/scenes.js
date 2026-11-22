/* T114 复利雪球 Compound Snowball (finance): a snowball rolls down a slope and grows, the balance compounds, sample math. */
(function () { const M = K.T.mo, X = M.X, NV = '#14213d', GD = '#fca311';
  const slope = c => M.svg(c, 0, 0, 1920, 1080, '<path d="M0 300 C 600 380, 1100 640, 1920 900 V1080 H0Z" fill="#e8f1fb"/><path d="M0 300 C 600 380, 1100 640, 1920 900" fill="none" stroke="#bcd3ee" stroke-width="6"/>');
  const ballP = u => { const x = 120 + 1600 * u, y = 300 + 600 * Math.pow(u, 1.6) * .98; return [x, y]; };
  M.story({ bg: '#cfe3f7', sbg: ['linear-gradient(#bcd9f5,#eef5fc)', NV, 'linear-gradient(#bcd9f5,#eef5fc)'], tr: ['push', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 90, 340), M.q(1380, 200, 400, 480, 20), M.c(140, 140, 360)],
    caps: [['钱，会像雪球一样滚大', 'Money grows like a snowball'], ['每年 8%，滚 20 年（示例）', '8% a year for 20 years (sample)'], ['越早开始，越大', 'Start early, end bigger']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ sl: slope(c), b: M.box(c, 0, 0, { width: '100px', height: '100px', borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%, #fff, #dbe8f5 60%, #a9c2dd)', boxShadow: '0 12px 20px rgba(20,33,61,.2)' }), t: X(c, 140, 120, 90, NV, '复利雪球', 900) }),
       (s, t, a) => { const u = Math.max(0, Math.min(1, (t - a) / 3)), [x, y] = ballP(u), r = 40 + 160 * u * u; s.b.style.width = s.b.style.height = 2 * r + 'px'; s.b.style.opacity = t > a ? 1 : 0; s.b.style.transform = `translate(${(x - r).toFixed(0)}px, ${(y - 2 * r + 10).toFixed(0)}px) rotate(${(u * 900).toFixed(0)}deg)`; M.slide(s.sl, t, a, 99, { dx: 0 }); M.hero(s.t, t, a + .2, 99); }],
      [c => ({ n: X(c, 160, 220, 160, GD, '¥10,000', 400, M.AN), yr: X(c, 170, 440, 50, '#e5e5e5', '第 0 年', 700), bars: Array.from({ length: 20 }, (_, i) => M.box(c, 170 + i * 52, 0, { width: '38px', height: '0px', background: i % 5 === 4 ? GD : '#3b4d74', borderRadius: '6px 6px 0 0' })), sm: X(c, 170, 860, 26, '#8a96b0', 'SAMPLE · 8% / year · 示例', 700, M.MONO) }),
       (s, t, a) => { const u = Math.max(0, Math.min(1, (t - a) / 2.4)), y = Math.round(20 * u), v = Math.round(10000 * Math.pow(1.08, y)); s.n.textContent = '¥' + v.toLocaleString(); s.yr.textContent = `第 ${y} 年 · Year ${y}`; M.rise(s.n, t, a - .1, 99); M.rise(s.yr, t, a, 99); s.bars.forEach((b, i) => { const h = i < y ? 30 * Math.pow(1.08, i) * 2.2 : 0; b.style.height = h + 'px'; b.style.top = (830 - h) + 'px'; }); M.rise(s.sm, t, a + .4, 99); }],
      [c => ({ a1: X(c, 760, 260, 60, NV, '早 10 年开始', 900), v1: X(c, 760, 360, 130, GD, '× 2.2', 400, M.AN), a2: X(c, 760, 560, 40, '#4a5a7a', '同样的钱，多滚 10 年（示例）', 700) }),
       (s, t, a) => { M.hero(s.a1, t, a - .1, 99); M.pop(s.v1, t, a + .4, 99, { from: 1.6 }); M.rise(s.a2, t, a + .8, 99); }]
    ] });
})();
