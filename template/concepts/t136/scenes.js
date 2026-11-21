/* T136 成分表 Ingredient Label (general skincare info; sample label). */
(function () { const M = K.T.mo, X = M.X, OR = '#e76f51', INK = '#3a2a24';
  M.story({ bg: '#fdf1ec', sbg: ['#fdf1ec', '#fbe4da', '#fdf1ec'], tr: ['iris', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.q(110, 160, 400, 480, 30), M.c(1440, 150, 380)],
    caps: [['买护肤品，先看成分表', 'Read the ingredient list first'], ['烟酰胺：常用来提亮', 'Niacinamide: often for brightening'], ['三个常见成分，各管一件事', 'Three common ingredients, three jobs']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ bt: M.box(c, 300, 200, { width: '260px', height: '560px', borderRadius: '40px 40px 30px 30px', background: 'linear-gradient(90deg,#f5c6b8,#fde3da 45%,#f0b7a6)', boxShadow: '0 30px 50px rgba(120,50,30,.25)' }), cap: M.box(c, 360, 130, { width: '140px', height: '90px', borderRadius: '14px', background: '#3a2a24' }),
          lb: M.card(c, 640, 240, 640, 460, '#fff', { padding: '40px', boxSizing: 'border-box', font: M.f(600, 28, M.CN), color: '#666', lineHeight: 1.8 }) }),
       (s, t, a) => { if (!s.lb.d) { s.lb.innerHTML = `<b style="font-size:38px;color:${INK}">成分表 · 示例</b><br>水、甘油、丁二醇、<span style="background:#ffe066;color:${INK}">烟酰胺</span>、透明质酸钠、泛醇、尿囊素……`; s.lb.d = 1; } M.rise(s.bt, t, a + .2, 99, { dy: 100 }); M.rise(s.cap, t, a + .3, 99, { dy: 100 }); M.panel(s.lb, t, a + .7, 99, { r: 20 }); }],
      [c => ({ mg: M.box(c, 640, 200, { width: '460px', height: '460px', borderRadius: '50%', border: '18px solid #3a2a24', background: 'rgba(255,255,255,.92)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', boxShadow: '0 20px 40px rgba(0,0,0,.2)' }), h: M.box(c, 1020, 600, { width: '200px', height: '44px', background: '#3a2a24', borderRadius: '22px', transform: 'rotate(45deg)' }), tag: M.box(c, 1180, 240, { padding: '20px 30px', background: OR, color: '#fff', borderRadius: '18px', font: M.f(900, 48, M.CN) }, '提亮 Brighten') }),
       (s, t, a) => { if (!s.mg.d) { X(s.mg, 0, 0, 84, OR, '烟酰胺', 900, M.CN, { position: 'static' }); X(s.mg, 0, 0, 34, '#888', 'Niacinamide', 700, M.INTER, { position: 'static' }); s.mg.d = 1; } M.pop(s.mg, t, a - .15, 99, { from: .4 }); M.pop(s.h, t, a, 99, { from: .4, base: 'rotate(45deg)' }); M.slide(s.tag, t, a + .6, 99, { dx: 80 }); }],
      [c => ({ ch: [['烟酰胺', '提亮'], ['透明质酸', '补水'], ['泛醇', '舒缓']].map(([n, fx], i) => { const g = M.card(c, 160 + i * 400, 300, 360, 320, '#fff', { padding: '40px', boxSizing: 'border-box' }); X(g, 40, 40, 52, INK, n); X(g, 40, 140, 90, [OR, '#4cc9f0', '#80b918'][i], fx); return g; }), d: X(c, 160, 680, 26, '#9a7a6a', '一般护肤知识 · 因人而异') }),
       (s, t, a) => { s.ch.forEach((g, i) => M.rise(g, t, a - .1 + i * .2, 99, { dy: 100 })); M.rise(s.d, t, a + .9, 99); }]
    ] });
})();
