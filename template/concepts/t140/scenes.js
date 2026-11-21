/* T140 万花筒色盘 Kaleidoscope palette (beauty colours). */
(function () { const M = K.T.mo, X = M.X, P = ['#ff4fa3', '#ffd23f', '#3ff0ff', '#7b2fff', '#ff8a5b', '#7cff6b'];
  const kal = (c, x, y, sz, pal) => M.svg(c, x, y, sz, sz, Array.from({ length: 12 }, (_, i) => `<g transform="rotate(${i * 30} ${sz / 2} ${sz / 2})"><path d="M${sz / 2} ${sz / 2} L${sz / 2} 0 L${sz * .64} ${sz * .16}Z" fill="${pal[i % pal.length]}" opacity=".85"/><path d="M${sz / 2} ${sz / 2} L${sz * .6} ${sz * .28} L${sz * .7} ${sz * .4}Z" fill="${pal[(i + 2) % pal.length]}" opacity=".7"/></g>`).join(''), { transformOrigin: '50% 50%' });
  M.story({ bg: '#120a24', sbg: ['#120a24', '#1d0b33', '#fff4fa'], tr: ['zoom', 'iris'], ring: () => ({ color: '#ffffff', width: 8, shadow: .4 }),
    wins: [M.c(760, 340, 400), M.q(1340, 160, 420, 500, 210), M.c(1440, 150, 380)],
    caps: [['今天的颜色，转出来', 'Spin out today’s colours'], ['暖调、冷调，各一组', 'A warm set and a cool set'], ['选一个，属于你的色盘', 'Pick the palette that’s yours']], port: { box: [100, 40, 1820, 900] },
    scenes: [
      [c => ({ k: kal(c, 460, 40, 1000, P), t: X(c, 80, 80, 60, '#fff', '万花筒') }), (s, t, a) => { M.pop(s.k, t, a + .1, 99, { from: .3 }); s.k.style.transform += ` rotate(${(t * 30).toFixed(1)}deg)`; M.rise(s.t, t, a + .4, 99); }],
      [c => ({ w: kal(c, 140, 200, 520, ['#ff8a5b', '#ffd23f', '#ff4fa3']), cl: kal(c, 720, 200, 520, ['#3ff0ff', '#7b2fff', '#7cff6b']), l1: X(c, 300, 760, 56, '#fff', '暖调'), l2: X(c, 880, 760, 56, '#fff', '冷调') }),
       (s, t, a) => { M.pop(s.w, t, a - .15, 99, { from: .3 }); M.pop(s.cl, t, a + .1, 99, { from: .3 }); s.w.style.transform += ` rotate(${(t * 40).toFixed(1)}deg)`; s.cl.style.transform += ` rotate(${(-t * 40).toFixed(1)}deg)`; M.rise(s.l1, t, a + .4, 99); M.rise(s.l2, t, a + .6, 99); }],
      [c => ({ sw: P.map((col, i) => M.box(c, 160 + (i % 3) * 300, 200 + Math.floor(i / 3) * 280, { width: '240px', height: '240px', borderRadius: '50%', background: col, boxShadow: '0 16px 30px rgba(0,0,0,.15)', transformOrigin: '50% 50%' })), ring: M.box(c, 440, 180, { width: '280px', height: '280px', borderRadius: '50%', border: '10px solid #111' }) }),
       (s, t, a) => { s.sw.forEach((e, i) => M.pop(e, t, a - .1 + i * .1, 99, { from: .3 })); M.pop(s.ring, t, a + 1.0, 99, { from: 1.5 }); }]
    ] });
})();
