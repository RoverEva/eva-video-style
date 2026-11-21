/* T111 三栏账本 Ledger Trio. All amounts are SAMPLE figures. */
(function () { const M = K.T.mo, X = M.X, INK = '#3a2e1e', G = '#1a7f4b', R = '#9b2c1e';
  const col = (c, i, title, nums, plus) => { const g = M.box(c, 140 + i * 430, 220, { width: '380px', height: '560px', background: '#fffdf6', backgroundImage: 'repeating-linear-gradient(transparent 0 58px, #d9cfb8 58px 60px)', boxShadow: '0 12px 24px rgba(0,0,0,.3)', padding: '30px', boxSizing: 'border-box' });
    X(g, 30, 20, 48, INK, title, 900, M.SERIF); g.n = nums.map((v, k) => X(g, 40, 110 + k * 60, 40, plus ? G : R, (plus ? '+' : '−') + v, 700, M.MONO)); return g; };
  M.story({ bg: '#efe6d2', sbg: ['#efe6d2', '#2d2418', '#efe6d2'], tr: ['flip', 'push'], ring: () => ({ color: '#fffdf6', width: 10, shadow: .35 }),
    wins: [M.c(1420, 150, 380), M.c(1560, 110, 300), M.q(120, 160, 420, 500, 24)],
    caps: [['这个月的三笔账', "This month's three accounts"], ['房租、吃饭、存钱（示例）', 'Rent, food, savings (sample)'], ['结余：每月 1,800（示例）', 'Left over: 1,800 a month (sample)']], port: { box: [100, 60, 1820, 800] },
    scenes: [
      [c => ({ book: M.card(c, 160, 220, 640, 460, '#5a3d22', { borderRadius: '10px 20px 20px 10px', boxShadow: 'inset 30px 0 0 #3e2914, 0 20px 40px rgba(0,0,0,.3)' }), t: X(c, 260, 360, 96, '#f3e3c3', '账本', 900, M.SERIF), pen: M.path(c, 260, 520, 460, 40, 'M0 20 C 120 0, 300 40, 450 14', '#f3e3c3', 6) }),
       (s, t, a) => { M.pop(s.book, t, a + .2, 99, { from: .8 }); M.hero(s.t, t, a + .5, 99); M.draw(s.pen, t, a + .9, .7, 99); }],
      [c => ({ c: [col(c, 0, '房租', ['3,000'], 0), col(c, 1, '吃饭', ['1,200', '400'], 0), col(c, 2, '存钱', ['1,800'], 1)] }),
       (s, t, a) => s.c.forEach((g, i) => { M.rise(g, t, a - .15 + i * .2, 99, { dy: 140 }); g.n.forEach((e, k) => M.hero(e, t, a + .5 + i * .2 + k * .2, 99, { dx: -30 })); })],
      [c => ({ ln: M.path(c, 640, 420, 1100, 20, 'M0 10 H1100', INK, 6), tot: X(c, 640, 460, 110, G, '+1,800', 400, M.AN), lb: X(c, 650, 600, 48, INK, '每月结余（示例）', 900, M.SERIF), st: M.box(c, 1460, 230, { width: '180px', height: '180px', border: `8px solid ${G}`, borderRadius: '50%', color: G, font: M.f(900, 44, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' }, '达标') }),
       (s, t, a) => { M.draw(s.ln, t, a - .1, .6, 99); M.hero(s.tot, t, a + .3, 99); M.count(s.tot, 1800, t, a + .3, .9, v => '+' + Number(v).toLocaleString('en')); M.rise(s.lb, t, a + .6, 99); M.pop(s.st, t, a + 1.1, 99, { from: 1.6, base: 'rotate(-12deg)' }); }]
    ] });
})();
