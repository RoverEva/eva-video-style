/* T53 Risograph 孔版印刷 · 10 s sample (illustrative copy). Two-colour misregistration settles into register; halftone; issue stamp. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, PK = '#ff48b0', BL = '#0078bf';
  const riso = (p, x, y, font, txt) => { const g = M.box(p, x, y, {}); g.a = M.txt(g, 0, 0, font, BL, txt, { mixBlendMode: 'multiply' }); g.b = M.txt(g, 0, 0, font, PK, txt, { mixBlendMode: 'multiply' }); return g; };
  M.setup({ bg: '#f5efe2', win: { x: 1240, y: 150, w: 520, h: 600, r: 18, o: 1, s: 1.15 }, ring: () => ({ color: BL, width: 8, shadow: .15 }), port: { box: [90, 60, 1060, 740] },
    captions: M.caps([['做一本自己的小志', 'Make your own zine'], ['两种颜色，也够好看', 'Two colours are plenty'], ['第三期，印好了', 'Issue three is printed']]),
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'radial-gradient(rgba(0,0,0,.06) 1px, transparent 1.3px)', backgroundSize: '5px 5px' }));
      s.t = riso(L, 100, 70, f(400, 200, M.AN), 'ZINE CLUB'); s.cn = riso(L, 110, 300, f(900, 96, M.CN), '独立小志');
      s.ht = M.box(L, 640, 330, { width: '420px', height: '420px', borderRadius: '50%', backgroundImage: `radial-gradient(${PK} 38%, transparent 40%)`, backgroundSize: '18px 18px', mixBlendMode: 'multiply', transformOrigin: '50% 50%' });
      s.ph = M.img(L, 110, 440, 460, 300, 120, { filter: 'grayscale(1) contrast(1.4)', mixBlendMode: 'multiply', opacity: .9 }); s.ph2 = M.box(L, 110, 440, { width: '460px', height: '300px', background: BL, mixBlendMode: 'screen', opacity: .6 });
      s.iss = M.txt(L, 640, 640, f(400, 70, M.AN), PK, 'ISSUE 03 · 第三期', { border: `6px solid ${PK}`, padding: '0 20px', mixBlendMode: 'multiply', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { const reg = (g, t0) => { const u = M.o3((t - t0) / .9), d = 16 * (1 - u) + 4; M.rise(g, t, t0, 9.2, { dy: 30 }); g.a.style.transform = `translate(${-d}px, ${d * .6}px)`; g.b.style.transform = `translate(${d}px, ${-d * .4}px)`; };
      reg(s.t, .85); reg(s.cn, 1.3);
      M.pop(s.ht, t, 3.5, 9.2, { from: .4 }); s.ht.style.transform += ` rotate(${(t * 6).toFixed(1)}deg)`;
      M.panel(s.ph, t, 3.8, 9.2); M.panel(s.ph2, t, 3.8, 9.2); s.ph2.style.opacity = (parseFloat(s.ph2.style.opacity) * .6).toFixed(3);
      M.pop(s.iss, t, 6.85, 9.2, { from: 1.5, base: 'rotate(-6deg)' }); } });
})();
