/* T133 拍摄手记 BTS Notes: clapperboard → REC → final cut. */
(function () { const M = K.T.mo, X = M.X, R = '#ff3b30';
  M.story({ bg: '#1c1c1e', sbg: ['#1c1c1e', '#0d0d0f', '#f2efe9'], tr: ['shutter', 'zoom'], ring: () => ({ color: '#ffffff', width: 6, shadow: .5 }),
    wins: [M.c(1440, 140, 380), M.q(260, 120, 1400, 700, 10, 1.05), M.q(560, 160, 800, 450, 18)],
    caps: [['第三场，第二条', 'Scene three, take two'], ['录着录着，就对了', 'Keep rolling until it clicks'], ['成片，出来了', 'And here’s the final cut']], port: { box: [100, 40, 1820, 840] },
    scenes: [
      [c => ({ body: M.card(c, 240, 340, 760, 400, '#2b2b2b', { borderRadius: '10px' }), top: M.svg(c, 240, 260, 780, 90, '<path d="M0 80 L760 0 V60 L0 140Z" fill="#fff"/><path d="M60 72 L130 2 M230 54 L300 -16 M400 36 L470 -34 M570 18 L640 -52" stroke="#111" stroke-width="40"/>', { transformOrigin: '0 80px' }),
          l: X(c, 290, 420, 64, '#fff', 'SCENE 03', 400, M.AN), l2: X(c, 290, 520, 64, '#fff', 'TAKE 02', 400, M.AN) }),
       (s, t, a) => { M.rise(s.body, t, a + .2, 99, { dy: 80 }); M.rise(s.top, t, a + .2, 99, { dy: 80 }); const cl = t > a + 1.3 ? M.os((t - a - 1.3) / .2) : 0; s.top.style.transform += ` rotate(${(-18 + 18 * Math.min(1, cl)).toFixed(1)}deg)`; M.hero(s.l, t, a + .6, 99); M.hero(s.l2, t, a + .8, 99); }],
      [c => ({ rec: M.box(c, 300, 150, { width: '26px', height: '26px', borderRadius: '50%', background: R }), rl: X(c, 340, 144, 34, '#fff', 'REC', 700, M.MONO), tc: X(c, 1500, 144, 34, '#fff', '00:00:00', 700, M.MONO), cor: M.svg(c, 260, 120, 1400, 700, '<path d="M0 60V0H60 M1340 0H1400V60 M0 640V700H60 M1340 700H1400V640" fill="none" stroke="#fff" stroke-width="6"/>') }),
       (s, t, a) => { s.rec.style.opacity = Math.floor(t * 2) % 2 ? 1 : .2; M.rise(s.rl, t, a, 99); M.rise(s.tc, t, a, 99); s.tc.textContent = '00:00:' + String(Math.floor(Math.max(0, t - a) * 10)).padStart(2, '0'); M.pop(s.cor, t, a - .1, 99, { from: 1.1 }); }],
      [c => ({ st: M.box(c, 1180, 560, { padding: '10px 26px', border: `6px solid ${R}`, color: R, font: M.f(400, 56, M.AN), transformOrigin: '50% 50%' }, 'FINAL CUT'), t: X(c, 560, 680, 60, '#1c1c1e', '成片，出来了'), pl: M.box(c, 910, 335, { width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(0,0,0,.45)', color: '#fff', font: M.f(900, 50, M.INTER), display: 'flex', alignItems: 'center', justifyContent: 'center' }, '▶') }),
       (s, t, a) => { M.pop(s.st, t, a + .6, 99, { from: 1.6, base: 'rotate(-8deg)' }); M.rise(s.t, t, a + .3, 99); M.pop(s.pl, t, a + .2, 99, { from: .4 }); }]
    ] });
})();
