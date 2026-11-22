/* T205 倒计时开场 Countdown (logo/text only): 3-2-1 with sweeping rings and flash, then the title lands. */
(function () { const M = K.T.mo, X = M.X, CL = ['#ff3d7f', '#ffd23f', '#3ff0c8'];
  const ring = (c, col) => M.svg(c, 660, 240, 600, 600, `<circle cx="300" cy="300" r="260" fill="none" stroke="#222" stroke-width="22"/><circle class="p" cx="300" cy="300" r="260" fill="none" stroke="${col}" stroke-width="22" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 300 300)"/>`);
  const num = (c, n, col) => X(c, 0, 330, 360, col, String(n), 400, M.AN, { width: '1920px', textAlign: 'center', lineHeight: 1 });
  const beat = (s, t, a, d) => { const u = Math.max(0, Math.min(1, (t - a) / d)); s.r.querySelector('.p').setAttribute('stroke-dashoffset', (1 - u).toFixed(3)); s.r.style.opacity = t > a - .1 ? 1 : 0; s.n.style.opacity = t > a ? 1 : 0; s.n.style.transform = `scale(${(1.4 - .4 * M.o3((t - a) / .3)).toFixed(3)})`; s.n.style.transformOrigin = '50% 50%'; };
  M.story({ noface: true, bg: '#0a0a0c', sbg: ['#0a0a0c', '#0a0a0c', '#0a0a0c'], tr: ['zoom', 'iris'],
    caps: [['准备', 'Ready'], ['倒数', 'Counting down'], ['开始！', 'Go!']], port: { box: [400, 160, 1120, 760] },
    scenes: [
      [c => ({ r: ring(c, CL[0]), n: num(c, 3, CL[0]) }), (s, t, a) => beat(s, t, a + .4, 2.4)],
      [c => ({ r: ring(c, CL[1]), n: num(c, 2, CL[1]), r2: ring(c, CL[2]), n2: num(c, 1, CL[2]) }), (s, t, a) => { if (t < a + 1.5) { beat(s, t, a - .1, 1.5); s.r2.style.opacity = s.n2.style.opacity = 0; } else { s.r.style.opacity = s.n.style.opacity = 0; beat({ r: s.r2, n: s.n2 }, t, a + 1.5, 1.4); } }],
      [c => ({ fl: M.box(c, 0, 0, { width: '1920px', height: '1080px', background: '#fff' }), t: X(c, 0, 360, 200, '#fff', 'GO!', 400, M.AN, { width: '1920px', textAlign: 'center' }), s: X(c, 0, 620, 44, CL[2], 'EVA · 开始', 700, M.INTER, { width: '1920px', textAlign: 'center', letterSpacing: '.3em' }), bs: Array.from({ length: 16 }, (_, i) => M.box(c, 954, 520, { width: '12px', height: '60px', borderRadius: '6px', background: CL[i % 3], transformOrigin: '6px -160px' })) }),
       (s, t, a) => { s.fl.style.opacity = Math.max(0, 1 - (t - a) / .4) * (t > a ? 1 : 0); M.pop(s.t, t, a + .1, 99, { from: 2 }); M.rise(s.s, t, a + .5, 99); s.bs.forEach((e, i) => { const u = M.o3((t - a) / .8); e.style.opacity = t > a ? (1 - Math.max(0, (t - a - .8) / .6)).toFixed(2) : 0; e.style.transform = `rotate(${i * 22.5}deg) translateY(${(-200 * u).toFixed(0)}px)`; }); }]
    ] });
})();
