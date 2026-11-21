/* T177 潮玩撞色 Sticker Pop (logo/text only): hot-pink field, a product blob, stickers slap on with bounce. */
(function () { const M = K.T.mo, X = M.X, PK = '#ff4fa3';
  const stk = (c, x, y, txt, bg, fg, r) => { const s = M.box(c, x, y, { padding: '18px 34px', borderRadius: '22px', background: bg, color: fg || '#111', font: M.f(900, 64, M.CN), border: '6px solid #111', boxShadow: '8px 8px 0 #111', whiteSpace: 'nowrap', transformOrigin: '50% 50%' }, txt); s.r = r; return s; };
  const slap = (s, t, a) => { M.pop(s, t, a, 99, { from: 2.2 }); s.style.transform += ` rotate(${s.r}deg)`; };
  const blob = c => M.box(c, 660, 320, { width: '600px', height: '440px', borderRadius: '45% 55% 50% 50% / 50% 45% 55% 50%', background: '#fff', boxShadow: '0 30px 0 rgba(0,0,0,.12)', color: '#999', font: M.f(700, 34, M.INTER), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 100%' }, 'PRODUCT · 示例');
  M.story({ noface: true, bg: PK, sbg: [PK, '#ffd23f', '#3ff0c8'], tr: ['flip', 'shutter'],
    caps: [['新品，到了！', 'New drop is here!'], ['轻，只有 0.2 kg', 'Light — just 0.2 kg'], ['限量，手慢无', 'Limited — be quick']], port: { box: [140, 80, 1640, 860] },
    scenes: [
      [c => ({ b: blob(c), s: [stk(c, 220, 200, 'NEW!', '#ffd23f', '#111', -8), stk(c, 1300, 260, 'HOT', '#7cff6b', '#111', 6)] }),
       (s, t, a) => { M.pop(s.b, t, a + .1, 99, { from: .3 }); s.b.style.transform += ` scaleY(${(1 + .03 * Math.sin(t * 5)).toFixed(3)})`; s.s.forEach((e, i) => slap(e, t, a + .7 + i * .35)); }],
      [c => ({ b: blob(c), s: [stk(c, 1180, 200, '轻 0.2kg', '#3ff0ff', '#111', 8), stk(c, 240, 640, 'SOFT', '#ff4fa3', '#fff', -6)] }),
       (s, t, a) => { M.pop(s.b, t, a - .1, 99, { from: .5 }); s.b.style.transform += ` translateY(${(-30 * Math.abs(Math.sin(t * 3))).toFixed(0)}px)`; s.s.forEach((e, i) => slap(e, t, a + .3 + i * .35)); }],
      [c => ({ b: blob(c), s: [stk(c, 260, 620, '限量', '#111', '#fff', -6), stk(c, 1260, 180, 'NEW!', '#ffd23f', '#111', 10), stk(c, 1240, 660, 'HOT', '#ff4fa3', '#fff', -4), stk(c, 200, 180, '0.2kg', '#fff', '#111', 5)] }),
       (s, t, a) => { M.pop(s.b, t, a - .1, 99, { from: .6 }); s.s.forEach((e, i) => slap(e, t, a + .2 + i * .25)); }]
    ] });
})();
