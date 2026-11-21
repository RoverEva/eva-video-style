/* T106 光谱实验 Spectrum: a prism splits white light; the seven colours breathe; flares drift. */
(function () { const M = K.T.mo, X = M.X, COL = ['#ff4b4b', '#ff9f40', '#ffe14a', '#5be37d', '#3fa9ff', '#4b4bff', '#b05bff'], NM = ['红', '橙', '黄', '绿', '蓝', '靛', '紫'];
  M.story({ bg: '#f3f5f8', sbg: ['#f3f5f8', '#06070d', '#eef1f6'], tr: ['wipe', 'zoom'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(110, 170, 400, 500, 30), M.c(760, 90, 400)],
    caps: [['白光里藏着七种颜色', 'White light hides seven colours'], ['红、橙、黄、绿、蓝、靛、紫', 'Red through violet'], ['彩虹就是这样来的', 'That’s how rainbows form']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ beam: M.path(c, 100, 420, 420, 20, 'M0 10 H400', '#999', 10), pr: M.svg(c, 500, 260, 300, 300, '<path d="M150 10 L290 280 L10 280Z" fill="rgba(200,220,255,.5)" stroke="#9db4d9" stroke-width="4"/>'),
          fan: COL.map((c2, i) => M.path(c, 680, 330, 700, 400, `M0 100 L680 ${-40 + i * 60}`, c2, 14)), t: X(c, 110, 120, 80, '#1d2433', '白光 ＝ 七种颜色') }),
       (s, t, a) => { M.draw(s.beam, t, a + .2, .5, 99); M.pop(s.pr, t, a + .4, 99, { from: .6 }); s.fan.forEach((p, i) => M.draw(p, t, a + .8 + i * .07, .6, 99)); M.hero(s.t, t, a + .3, 99); }],
      [c => ({ b: COL.map((c2, i) => M.box(c, 640 + i * 170, 140, { width: '110px', height: '620px', background: c2, filter: 'blur(14px)', opacity: .9, transformOrigin: '50% 100%' })), n: NM.map((s2, i) => X(c, 670 + i * 170, 790, 44, '#fff', s2)) }),
       (s, t, a) => { s.b.forEach((e, i) => { const v = M.env(t, a - .2 + i * .08, 99, .4); e.style.opacity = (v.a * .9).toFixed(3); e.style.transform = `scaleY(${(v.e * (.8 + .2 * Math.sin(t * 3 + i))).toFixed(3)})`; }); s.n.forEach((e, i) => M.rise(e, t, a + .3 + i * .08, 99)); }],
      [c => ({ fl: [[300, 300, 120], [600, 520, 60], [1400, 260, 90], [1600, 600, 40]].map(([x, y, r]) => M.box(c, x, y, { width: r * 2 + 'px', height: r * 2 + 'px', borderRadius: '50%', border: '3px solid rgba(255,255,255,.9)', background: 'radial-gradient(circle, rgba(255,255,255,.6), rgba(160,200,255,.15) 60%, transparent 70%)' })),
          arc: M.svg(c, 200, 420, 1520, 500, COL.map((c2, i) => `<path d="M${40 + i * 18} 480 A ${720 - i * 18} ${420 - i * 18} 0 0 1 ${1480 - i * 18} 480" stroke="${c2}" stroke-width="18" fill="none" opacity=".85" pathLength="1" stroke-dasharray="1 1"/>`).join('')), t: X(c, 600, 560, 90, '#1d2433', '彩虹就是这样来的') }),
       (s, t, a) => { s.fl.forEach((e, i) => { M.pop(e, t, a + i * .15, 99, { from: .3 }); e.style.transform += ` translateX(${(-(t - a) * (40 + i * 10)).toFixed(1)}px)`; }); [...s.arc.querySelectorAll('path')].forEach((p, i) => M.draw(p, t, a + .1 + i * .06, .9, 99)); M.hero(s.t, t, a + .9, 99, { dx: 0, dy: 30 }); }]
    ] });
})();
