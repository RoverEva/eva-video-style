/* T206 翻牌信息板 Split Flap: airport-style split-flap board — characters flip into place, rows update, final message. */
(function () { const M = K.T.mo, X = M.X, Y = '#ffd23f', CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:';
  const cell = (p, x, y, s) => { const g = M.box(p, x, y, { width: 56 * s + 'px', height: 80 * s + 'px', background: '#1b1b1f', borderRadius: 6 * s + 'px', color: '#f4f4f4', font: M.f(700, 56 * s, M.MONO), display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'inset 0 -2px 0 #000' }); M.box(g, 0, 40 * s - 1, { width: '100%', height: '2px', background: '#000' }); g.tx = M.box(g, 0, 0, { width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }); return g; };
  const row = (p, x, y, txt, s) => [...txt].map((ch, i) => { const g = cell(p, x + i * 62 * s, y, s); g.ch = ch; return g; });
  const flip = (L, t, a, sp) => L.forEach((g, i) => { const st = a + i * (sp || .05), n = Math.floor((t - st) * 18); g.style.opacity = t > st - .2 ? 1 : 0; if (g.ch === ' ') { g.tx.textContent = ''; return; } const k = CH.indexOf(g.ch); g.tx.textContent = n >= 8 || k < 0 ? g.ch : CH[(Math.max(0, n) * 5 + i * 3) % CH.length]; g.tx.style.transform = n < 8 && n >= 0 ? `scaleY(${(.4 + .6 * Math.abs(Math.cos((t - st) * 28))).toFixed(2)})` : ''; });
  M.story({ bg: '#0c0c0e', sbg: ['#0c0c0e', '#111114', '#0c0c0e'], tr: ['shutter', 'push'], ring: () => ({ color: Y, width: 6, shadow: .5 }),
    wins: [M.q(1380, 200, 400, 480, 16), M.q(1380, 200, 400, 480, 16), M.c(1420, 200, 380)],
    caps: [['今天的安排，像机场的翻牌', 'Today’s plan, like a departure board'], ['一项一项，翻出来', 'Flipping in, one by one'], ['准时出发', 'Departing on time']], port: { box: [60, 60, 1800, 900] },
    scenes: [
      [c => ({ h: X(c, 140, 120, 40, Y, 'DEPARTURES · 出发', 700, M.MONO), r: row(c, 140, 260, 'GOOD MORNING', 1.4) }), (s, t, a) => { M.rise(s.h, t, a + .2, 99); flip(s.r, t, a + .4); }],
      [c => ({ hd: X(c, 140, 160, 30, '#888', 'TIME   TASK        GATE', 700, M.MONO), rs: ['0900 SCRIPT   A1', '1100 SHOOT    B2', '1500 EDIT     C3', '1800 POST     D4'].map((tx, k) => row(c, 140, 230 + k * 120, tx, 1)) }),
       (s, t, a) => { M.rise(s.hd, t, a - .1, 99); s.rs.forEach((r, k) => flip(r, t, a + k * .35, .03)); }],
      [c => ({ r: row(c, 140, 300, 'ON TIME', 1.8), st: M.box(c, 140, 520, { padding: '10px 26px', background: '#2ecc71', color: '#0c0c0e', font: M.f(700, 40, M.MONO) }, 'BOARDING ✓') }), (s, t, a) => { flip(s.r, t, a - .1, .08); M.pop(s.st, t, a + 1.2, 99, { from: .3 }); }]
    ] });
})();
