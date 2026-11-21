/* T122 条款放大镜 Clause Lens (illustrative contract; not legal advice). */
(function () { const M = K.T.mo, X = M.X, INK = '#2a2420', R = '#c2410c';
  M.story({ bg: '#f6f1e8', sbg: ['#f6f1e8', '#2a2622', '#f6f1e8'], tr: ['iris', 'flip'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 26), M.c(1420, 150, 380)],
    caps: [['合同里，最容易漏看的一条', 'The clause people miss most'], ['逾期付款，按日计息', 'Late payment: daily interest'], ['签字前，看金额、期限、违约', 'Before signing: amount, term, penalty']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ doc: M.card(c, 160, 120, 1040, 700, '#fff', { borderRadius: '6px', padding: '60px', boxSizing: 'border-box' }), lens: M.box(c, 0, 0, { width: '300px', height: '300px', borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%, rgba(255,255,255,.85), rgba(255,200,150,.2) 45%, rgba(255,140,60,.25))', boxShadow: 'inset -12px -16px 30px rgba(200,100,30,.35), 0 24px 40px rgba(0,0,0,.18)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: M.f(900, 58, M.SERIF), color: R }, '第 3 条') }),
       (s, t, a) => { if (!s.doc.d) { X(s.doc, 60, 50, 52, INK, '示例合同', 900, M.SERIF); for (let i = 0; i < 8; i++) M.box(s.doc, 60, 150 + i * 60, { width: (600 + (i * 97) % 300) + 'px', height: '18px', background: i === 3 ? '#ffd6a5' : '#e6e1d8', borderRadius: '9px' }); s.doc.d = 1; }
         M.panel(s.doc, t, a + .1, 99, { r: 6 }); const u = M.io((t - a - .6) / 1.6); s.lens.style.opacity = M.env(t, a + .5, 99).a; s.lens.style.transform = `translate(${(200 + 400 * u).toFixed(1)}px, ${(560 - 220 * u).toFixed(1)}px)`; }],
      [c => ({ t: X(c, 600, 300, 150, '#f6f1e8', '逾期付款', 900, M.SERIF), t2: X(c, 600, 480, 110, '#ffb37a', '按日计息', 900, M.SERIF), u: M.path(c, 600, 610, 700, 30, 'M0 15 C 200 0, 450 30, 690 10', R, 10) }),
       (s, t, a) => { M.hero(s.t, t, a - .15, 99, { dx: 0, dy: 40 }); M.hero(s.t2, t, a + .2, 99, { dx: 0, dy: 40 }); M.draw(s.u, t, a + .6, .6, 99); }],
      [c => ({ it: ['金额', '期限', '违约责任'].map((s2, i) => { const g = M.card(c, 160 + i * 400, 300, 360, 300, '#fff', { padding: '40px', boxSizing: 'border-box' }); X(g, 40, 40, 90, R, '0' + (i + 1), 400, M.AN); X(g, 40, 170, 56, INK, s2, 900, M.SERIF); return g; }), d: X(c, 160, 680, 28, '#7a6a5a', '法律常识分享 · 非法律意见') }),
       (s, t, a) => { s.it.forEach((g, i) => M.rise(g, t, a - .1 + i * .2, 99, { dy: 100 })); M.rise(s.d, t, a + .8, 99); }]
    ] });
})();
