/* T182 马赛克揭幕 Mosaic Reveal: a tile grid covers the window, tiles flip away in a wave. */
(function () { const M = K.T.mo, X = M.X, CO = ['#2b2b30', '#3a3a42', '#d8d2c6', '#c9a45c', '#1f3b5c'];
  const mos = (c, x0, y0, cols, rows, sz) => Array.from({ length: cols * rows }, (_, i) => M.box(c, x0 + (i % cols) * sz, y0 + Math.floor(i / cols) * sz, { width: (sz - 4) + 'px', height: (sz - 4) + 'px', background: CO[(i * 7) % 5], transformOrigin: '50% 50%' }));
  const wave = (L, cols, t, a, cx, cy, dir) => L.forEach((e, i) => { const d = Math.hypot(i % cols - cx, Math.floor(i / cols) - cy), u = M.io((t - a - d * .08) / .4); const v = dir ? u : 1 - u; e.style.opacity = (1 - v).toFixed(2); e.style.transform = `rotateY(${(v * 90).toFixed(0)}deg) scale(${(1 - .4 * v).toFixed(2)})`; });
  M.story({ bg: '#121214', sbg: ['#121214', '#16161a', '#121214'], tr: ['iris', 'push'], ring: () => ({ color: '#ffffff', width: 0, shadow: .4 }),
    wins: [M.q(400, 160, 1120, 640, 8, 1.03), M.q(1200, 120, 560, 700, 8, 1.03), M.q(400, 180, 1120, 640, 8, 1.03)],
    caps: [['一块块拼起来', 'Piece by piece'], ['每一块，都是一次尝试', 'Each tile is one attempt'], ['拼完，就是完整的画面', 'Complete, it’s the whole picture']], port: { box: [100, 40, 1720, 900] },
    scenes: [
      [c => ({ m: mos(c, 0, 0, 24, 14, 80) }), (s, t, a) => wave(s.m, 24, t, a + .2, 12, 7, 0)],
      [c => ({ cards: Array.from({ length: 6 }, (_, i) => M.box(c, 140 + (i % 3) * 330, 200 + Math.floor(i / 3) * 330, { width: '300px', height: '300px', background: CO[i % 5], borderRadius: '6px', color: '#fff', font: M.f(900, 44, M.INTER), display: 'flex', alignItems: 'flex-end', padding: '20px', boxSizing: 'border-box' }, '#0' + (i + 1))) }),
       (s, t, a) => { s.cards.forEach((e, i) => { M.pop(e, t, a + .1 + i * .12, 99, { from: .3 }); e.style.transform += ` rotateY(${(90 * (1 - M.io((t - a - .1 - i * .12) / .4))).toFixed(0)}deg)`; }); }],
      [c => ({ m: mos(c, 0, 0, 24, 14, 80), t: X(c, 380, 70, 60, '#fff', '拼出完整画面', 900, M.CN, { zIndex: 5, textShadow: '0 4px 14px #000' }) }), (s, t, a) => { wave(s.m, 24, t, a - .2, 0, 0, 0); M.hero(s.t, t, a + .6, 99); }]
    ] });
})();
