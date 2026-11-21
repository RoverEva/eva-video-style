/* T129 芯片之旅 Chip Journey: sand → wafer → chip on a board. */
(function () { const M = K.T.mo, X = M.X, CY = '#3fe0ff';
  M.story({ bg: '#06121a', sbg: ['radial-gradient(ellipse,#3a2f20,#120e08)', '#06121a', '#071a10'], tr: ['zoom', 'iris'], ring: () => ({ color: CY, width: 4, shadow: .5 }),
    wins: [M.c(1460, 140, 360), M.q(1380, 160, 400, 480, 24), M.c(110, 160, 380)],
    caps: [['一粒砂，能变成什么？', 'What can one grain of sand become?'], ['提纯成硅，切成晶圆', 'Purified silicon, sliced into wafers'], ['最后，变成一颗芯片', 'And finally, a chip']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ g: Array.from({ length: 60 }, (_, i) => M.box(c, 200 + (i * 173) % 1100, 600 + (i * 37) % 240, { width: (6 + i % 5 * 3) + 'px', height: (6 + i % 5 * 3) + 'px', borderRadius: '40%', background: '#d9c49a' })), hero: M.box(c, 640, 360, { width: '90px', height: '80px', borderRadius: '40%', background: 'radial-gradient(circle at 35% 30%,#fff7e0,#d9c49a 50%,#8a7450)', transformOrigin: '50% 50%' }), t: X(c, 140, 160, 90, '#f3e6c8', '一粒砂') }),
       (s, t, a) => { s.g.forEach((e, i) => { e.style.opacity = M.env(t, a + i * .01, 99).a; }); M.pop(s.hero, t, a + .5, 99, { from: .2 }); s.hero.style.transform += ` scale(${(1 + 1.6 * M.io((t - a - 1.2) / 1.8)).toFixed(3)})`; M.hero(s.t, t, a + .3, 99); }],
      [c => ({ w: M.box(c, 300, 140, { width: '640px', height: '640px', borderRadius: '50%', background: 'repeating-linear-gradient(0deg,transparent 0 38px,rgba(63,224,255,.5) 38px 41px),repeating-linear-gradient(90deg,#1b2a3a 0 38px,rgba(63,224,255,.5) 38px 41px)', boxShadow: '0 0 60px rgba(63,224,255,.25)' }),
          lit: Array.from({ length: 16 }, (_, i) => M.box(c, 380 + (i % 4) * 120, 240 + Math.floor(i / 4) * 120, { width: '38px', height: '38px', background: CY, boxShadow: `0 0 18px ${CY}` })), t: X(c, 1000, 300, 90, '#e8fbff', '晶圆'), e: X(c, 1004, 420, 36, CY, 'WAFER', 700, M.MONO) }),
       (s, t, a) => { M.pop(s.w, t, a - .15, 99, { from: .6 }); s.w.style.transform += ` rotate(${(t * 8).toFixed(1)}deg)`; s.lit.forEach((e, i) => { e.style.opacity = t > a + .3 + i * .08 ? 1 : 0; }); M.hero(s.t, t, a + .3, 99); M.rise(s.e, t, a + .5, 99); }],
      [c => ({ tr: Array.from({ length: 10 }, (_, i) => M.path(c, 0, 0, 1920, 1080, `M${960 + (i - 5) * 30} 500 V${300 - i * 10} H${1700 - i * 20}`, '#2bd67b', 3)), chip: M.box(c, 820, 360, { width: '320px', height: '320px', background: '#101820', border: `4px solid ${CY}`, boxShadow: `0 0 40px rgba(63,224,255,.5)`, font: M.f(400, 70, M.AN), color: CY, display: 'flex', alignItems: 'center', justifyContent: 'center' }, 'CHIP'), t: X(c, 820, 740, 70, '#e8fbff', '一颗芯片') }),
       (s, t, a) => { M.pop(s.chip, t, a - .1, 99, { from: .5 }); s.tr.forEach((p, i) => M.draw(p, t, a + .4 + i * .05, .7, 99)); M.hero(s.t, t, a + .6, 99); }]
    ] });
})();
