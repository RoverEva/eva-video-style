/* T155 产品舞台 Product Stage (logo/text only): spotlight, product rises on a turntable, swap-ready label. */
(function () { const M = K.T.mo, X = M.X, P = '#7b6cff';
  const spot = c => M.box(c, 660, -40, { width: '600px', height: '900px', background: 'linear-gradient(rgba(255,255,255,.22),rgba(255,255,255,0))', clipPath: 'polygon(40% 0,60% 0,100% 100%,0 100%)' });
  const ped = c => M.box(c, 660, 760, { width: '600px', height: '110px', borderRadius: '50%', background: 'radial-gradient(ellipse,#3a3a48,#16161c)', boxShadow: '0 20px 40px rgba(0,0,0,.6)' });
  const prod = c => M.box(c, 840, 420, { width: '240px', height: '380px', borderRadius: '40px', background: `linear-gradient(160deg,#a99cff,${P})`, boxShadow: `0 0 60px rgba(123,108,255,.5)`, transformOrigin: '50% 100%' });
  M.story({ noface: true, bg: '#0b0b10', sbg: ['radial-gradient(ellipse at 50% 30%,#2b2b35,#0b0b10)', 'radial-gradient(ellipse at 50% 40%,#22223a,#0b0b10)', 'radial-gradient(ellipse at 50% 30%,#35305a,#0b0b10)'], tr: ['iris', 'zoom'],
    caps: [['灯亮了', 'Lights up'], ['它，慢慢转过来', 'It slowly turns to you'], ['你的产品，放这里', 'Your product goes here']], port: { box: [300, 0, 1320, 960] },
    scenes: [
      [c => ({ sp: spot(c), pd: ped(c), p: prod(c) }), (s, t, a) => { s.sp.style.opacity = t > a + .2 ? (t < a + .35 || t > a + .5 ? 1 : .2) : 0; M.rise(s.pd, t, a + .5, 99); M.rise(s.p, t, a + .9, 99, { dy: 300 }); }],
      [c => ({ sp: spot(c), pd: ped(c), p: prod(c), d: ['防水', '轻薄', '长续航'].map((n, i) => X(c, [260, 1320, 1320][i], [380, 300, 520][i], 54, '#d8d4ff', n, 900)) }),
       (s, t, a) => { s.p.style.transform = `rotateY(${((t - a) * 90).toFixed(0)}deg)`; s.d.forEach((e, i) => M.slide(e, t, a + .3 + i * .3, 99, { dx: i ? 100 : -100 })); }],
      [c => ({ sp: spot(c), pd: ped(c), p: prod(c), t: X(c, 650, 110, 52, '#fff', 'YOUR PRODUCT · 可替换', 700, M.INTER) }),
       (s, t, a) => { s.p.style.transform = `scale(${(1 + .05 * Math.sin(t * 2)).toFixed(3)})`; s.p.style.boxShadow = `0 0 ${(80 + 40 * Math.sin(t * 3)).toFixed(0)}px rgba(123,108,255,.7)`; M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
