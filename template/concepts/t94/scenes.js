/* T94 Packshot 产品转台 · 10 s logo-only sample. Generic bottle (SAMPLE product) on a turntable: label band scrolls to fake rotation; callouts. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, INK = '#1b2430', AC = '#2a9d8f';
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 40%, #ffffff, #e5ebf0 70%)', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['新品亮相（示例）', 'New product (sample)'], ['三百六十度，看清每个细节', 'Every detail, all the way round'], ['敬请期待', 'Coming soon']]),
    build(L) { const s = {};
      s.tt = M.box(L, 760, 640, { width: '400px', height: '70px', borderRadius: '50%', background: 'linear-gradient(#d4dbe2,#b9c3cd)', boxShadow: '0 20px 30px rgba(40,60,80,.25)' });
      s.bot = M.box(L, 850, 170, { width: '220px', height: '480px', borderRadius: '60px 60px 40px 40px', background: 'linear-gradient(90deg,#1f6f66,#2a9d8f 40%,#7fd1c6 55%,#2a9d8f 70%,#1a5a53)', overflow: 'hidden', boxShadow: 'inset 0 -20px 40px rgba(0,0,0,.25)' });
      s.cap = M.box(L, 905, 110, { width: '110px', height: '80px', borderRadius: '14px 14px 4px 4px', background: 'linear-gradient(90deg,#222,#666 45%,#222)' });
      s.band = el(s.bot, 'div', 'abs', { left: 0, top: '170px', width: '880px', height: '150px', background: 'repeating-linear-gradient(90deg,#f7f3ea 0 220px,#f0eadc 220px 440px)', display: 'flex' });
      for (let i = 0; i < 4; i++) { const c = el(s.band, 'div', '', { width: '220px', textAlign: 'center', paddingTop: '26px', font: f(400, 54, M.AN), color: INK }, i % 2 ? '200ml' : 'EVA'); }
      s.gloss = el(s.bot, 'div', 'abs', { left: '40px', top: '20px', width: '30px', height: '440px', borderRadius: '15px', background: 'rgba(255,255,255,.35)' });
      s.co = [['玻璃瓶身', 'Glass body', 820, 300, -1], ['按压泵头', 'Pump top', 1010, 150, 1], ['200 ml', 'Volume', 1080, 420, 1]].map(([c, e, x, y, d]) => { const p = M.path(L, d > 0 ? x : x - 160, y, 160, 20, d > 0 ? 'M0 10H150' : 'M150 10H0', INK, 3);
        const g = M.box(L, d > 0 ? x + 170 : x - 420, y - 30, { width: '250px', textAlign: d > 0 ? 'left' : 'right' }); M.txt(g, 0, 0, f(900, 42, M.CN), INK, c, { position: 'static' }); M.txt(g, 0, 0, f(600, 22, M.INTER), '#6a7a88', e, { position: 'static' }); p.g = g; return p; });
      s.tag = M.txt(L, 110, 80, f(700, 24, M.INTER), '#fff', 'SAMPLE PRODUCT · 示例产品', { background: AC, padding: '6px 14px', borderRadius: '6px' });
      s.soon = M.txt(L, 0, 740, f(900, 50, M.CN), INK, '敬请期待 · Coming soon', { width: '1920px', textAlign: 'center' });
      return s; },
    update(s, t) { M.pop(s.tt, t, .6, 10.3, { from: .6 }); M.rise(s.bot, t, .8, 10.3, { dy: 60 }); M.rise(s.cap, t, .9, 10.3, { dy: 60 }); M.pop(s.tag, t, 1.0, 10.3, { from: .6 });
      s.band.style.transform = `translateX(${(-((t * 120) % 440)).toFixed(1)}px)`; s.gloss.style.transform = `translateX(${(14 * Math.sin(t * 1.6)).toFixed(1)}px)`;
      s.co.forEach((p, i) => { M.draw(p, t, 3.6 + i * .3, .35, 10.3); M.rise(p.g, t, 3.8 + i * .3, 10.3, { dy: 12 }); }); M.rise(s.soon, t, 6.85, 10.3); } });
})();
