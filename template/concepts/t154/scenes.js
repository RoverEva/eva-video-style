/* T154 键帽微距 Keycap Macro (logo/text only): keycaps press E·V·A, RGB sweep, then the wordmark. */
(function () { const M = K.T.mo, X = M.X, RGB = ['#ff2bd6', '#3ff0ff', '#7cff6b', '#ffd23f', '#7b2fff'];
  const key = (c, x, y, ch, s) => { const k = M.box(c, x, y, { width: 200 * s + 'px', height: 200 * s + 'px', borderRadius: 30 * s + 'px', background: 'linear-gradient(#3a3a40,#1c1c20)', boxShadow: '0 14px 0 #0c0c0e', color: '#eee', font: M.f(500, 100 * s, M.INTER), display: 'flex', alignItems: 'center', justifyContent: 'center' }, ch); return k; };
  M.story({ noface: true, bg: '#0b0b0d', sbg: ['#0b0b0d', '#0e0e12', '#0b0b0d'], tr: ['zoom', 'blur'],
    caps: [['按下第一个键', 'Press the first key'], ['灯光，扫过整块键盘', 'Light sweeps the board'], ['敲出你的名字', 'Type out your name']], port: { box: [200, 120, 1520, 820] },
    scenes: [
      [c => ({ k: key(c, 760, 300, 'E', 2), t: X(c, 160, 900, 36, '#888', 'CLICK', 700, M.MONO) }), (s, t, a) => { M.pop(s.k, t, a + .1, 99, { from: 1.4 }); const p = Math.max(0, Math.sin((t - a - .8) * 4)) * (t > a + .8 && t < a + 1.6); s.k.style.transform += ` translateY(${(p * 12).toFixed(1)}px)`; s.k.style.boxShadow = `0 ${14 - p * 12}px 0 #0c0c0e, 0 0 ${60 * p}px ${RGB[0]}`; M.rise(s.t, t, a + .5, 99); }],
      [c => ({ ks: Array.from({ length: 30 }, (_, i) => key(c, 220 + (i % 10) * 150, 280 + Math.floor(i / 10) * 150, 'QWERTYUIOPASDFGHJKL;ZXCVBNM,./'[i], .65)) }),
       (s, t, a) => s.ks.forEach((k, i) => { const col = i % 10, sw = (t - a) * 6 - col; M.rise(k, t, a - .15 + col * .03, 99, { dy: 40 }); const g = Math.max(0, 1 - Math.abs(sw - 2) / 2); k.style.boxShadow = `0 9px 0 #0c0c0e, 0 0 ${(40 * g).toFixed(0)}px ${RGB[(Math.floor((t - a) * 2) + col) % 5]}`; k.style.color = g > .3 ? RGB[col % 5] : '#eee'; })],
      [c => ({ ks: ['E', 'V', 'A'].map((ch, i) => key(c, 540 + i * 300, 320, ch, 1.2)), t: X(c, 760, 680, 36, '#888', 'EVA · RGB SWEEP', 700, M.MONO) }),
       (s, t, a) => { s.ks.forEach((k, i) => { M.pop(k, t, a - .1 + i * .25, 99, { from: 1.5 }); k.style.transform += ` translateY(${i === 1 ? 30 : 0}px)`; k.style.boxShadow = `0 14px 0 #0c0c0e, 0 30px 60px ${RGB[i]}`; }); M.rise(s.t, t, a + .9, 99); }]
    ] });
})();
