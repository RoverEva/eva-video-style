/* T46 Boarding Pass 登机牌 · 10 s sample (illustrative copy; fictional flight). Pass slides in, plane flies the arc, stub tears off. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, OR = '#ff6b4a', INK = '#1d2433';
  M.setup({ bg: 'linear-gradient(180deg,#2d6fb5,#8cc4ee)', win: { x: 1260, y: 150, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .35 }), port: { box: [90, 40, 1060, 760] },
    captions: M.caps([['登机！目的地：成片', 'Boarding — destination: final cut'], ['从灵感出发，一站直达', 'From idea, nonstop'], ['祝你旅途愉快', 'Enjoy the trip']]),
    build(L) { const s = {};
      s.clouds = [[200, 900, 380], [900, 860, 300], [1500, 920, 420], [600, 60, 260]].map(([x, y, w]) => M.bg(M.box(L, x, y, { width: w + 'px', height: w * .38 + 'px', borderRadius: '999px', background: 'rgba(255,255,255,.55)', filter: 'blur(14px)' })));
      s.card = M.box(L, 110, 200, { width: '760px', height: '440px', background: '#fff', borderRadius: '26px 0 0 26px', boxShadow: '0 20px 40px rgba(0,0,0,.25)', overflow: 'hidden' });
      el(s.card, 'div', 'abs', { left: 0, top: 0, width: '760px', height: '74px', background: OR });
      M.txt(s.card, 36, 14, f(900, 36, M.CN), '#fff', '登机牌 BOARDING PASS');
      const fld = (p, x, y, k, v, px) => { M.txt(p, x, y, f(700, 20, M.MONO), '#8a93a6', k); return M.txt(p, x, y + 28, f(900, px || 40, M.CN), INK, v); };
      s.from = fld(s.card, 40, 110, 'FROM', '灵感', 84); M.txt(s.card, 42, 236, f(700, 26, M.INTER), '#8a93a6', 'IDEA');
      s.to = fld(s.card, 470, 110, 'TO', '成片', 84); M.txt(s.card, 472, 236, f(700, 26, M.INTER), '#8a93a6', 'FINAL CUT');
      s.meta = [fld(s.card, 40, 300, 'FLIGHT', 'EV 001'), fld(s.card, 260, 300, 'GATE', '03'), fld(s.card, 440, 300, 'SEAT', '1A')];
      s.stub = M.box(L, 870, 200, { width: '230px', height: '440px', background: '#fff', borderRadius: '0 26px 26px 0', borderLeft: '4px dashed #c3c9d4', boxSizing: 'border-box', boxShadow: '0 20px 40px rgba(0,0,0,.25)', transformOrigin: '0 0' });
      el(s.stub, 'div', 'abs', { left: 0, top: 0, width: '230px', height: '74px', background: OR, borderRadius: '0 26px 0 0' });
      s.bars = M.svg(s.stub, 40, 120, 150, 260, Array.from({ length: 30 }, (_, i) => `<rect x="${[0, 4, 9, 12, 18][i % 5] + (i >> 2) * 18}" y="0" width="${[2, 4, 3, 2, 5][i % 5]}" height="260" fill="${INK}"/>`).join(''));
      s.arc = M.path(L, 170, 120, 620, 120, 'M10 110 C 160 -20, 460 -20, 610 110', '#ffffff', 4, 'stroke-dasharray=".02 .02"');
      s.plane = M.txt(L, 0, 0, f(400, 54, M.INTER), '#fff', '✈');
      s.bon = M.txt(L, 112, 680, f(900, 56, M.CN), '#fff', '旅途愉快 · Bon voyage', { textShadow: '0 4px 14px rgba(0,0,0,.25)' });
      return s; },
    update(s, t) { s.clouds.forEach((c, i) => { c.style.transform = `translateX(${(-t * (10 + i * 4)).toFixed(1)}px)`; });
      M.panel(s.card, t, .85, 9.2, { r: 26, din: .45 }); M.slide(s.stub, t, 1.15, 9.2, { dx: 60 });
      M.hero(s.from, t, 1.4, 9.2, { dx: -30 }); M.hero(s.to, t, 1.6, 9.2, { dx: -30 }); s.meta.forEach((e, i) => M.rise(e, t, 1.9 + i * .12, 9.2));
      const ap = s.arc; ap.setAttribute('stroke-dasharray', `${(M.o3((t - 3.6) / 1.6)).toFixed(4)} 1`); ap.style.opacity = t > 3.6 ? (1 - M.i2((t - 8.97) / .23)) : 0;
      const u = M.io((t - 3.6) / 1.6), pt = ap.getPointAtLength(ap.getTotalLength() * u), pt2 = ap.getPointAtLength(ap.getTotalLength() * Math.min(1, u + .01));
      s.plane.style.opacity = t > 3.6 ? ap.style.opacity : 0; s.plane.style.transform = `translate(${(170 + pt.x - 27).toFixed(1)}px, ${(120 + pt.y - 34).toFixed(1)}px) rotate(${(Math.atan2(pt2.y - pt.y, pt2.x - pt.x) * 57.3).toFixed(1)}deg)`;
      const tear = M.os((t - 6.85) / .5); if (t > 6.85) s.stub.style.transform = `translate(${(40 * tear).toFixed(1)}px, ${(26 * tear).toFixed(1)}px) rotate(${(7 * tear).toFixed(2)}deg)`;
      M.hero(s.bon, t, 7.2, 9.2); } });
})();
