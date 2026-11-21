/* T98 Store Locator 门店地址 · 10 s logo-only sample. Stylised street map, route from "you" to the pin, pulse; address is a SAMPLE placeholder. */
(function () { const C = EV, M = K.T.mo, f = M.f, R = '#ff4d3d', INK = '#1d2633';
  M.setup({ noface: true, bg: '#eef0ea', port: { box: [200, 40, 1520, 780] },
    captions: M.caps([['我们的门店在这里（示例）', 'Our store is here (sample)'], ['沿着路线，很快就到', 'Follow the route — it’s close'], ['欢迎来坐坐', 'Come by anytime']]),
    build(L) { const s = {};
      s.map = M.bg(M.svg(L, -100, -60, 2120, 1200, Array.from({ length: 12 }, (_, i) => `<path d="M${i * 190} 0 V1200" stroke="#fff" stroke-width="${i % 3 ? 14 : 26}"/>`).join('') + Array.from({ length: 8 }, (_, i) => `<path d="M0 ${i * 170} H2120" stroke="#fff" stroke-width="${i % 3 ? 14 : 26}"/>`).join('') + Array.from({ length: 16 }, (_, i) => `<rect x="${30 + (i * 381) % 2000}" y="${30 + (i * 233) % 1100}" width="130" height="110" rx="10" fill="${i % 4 ? '#dfe4d6' : '#cfe6c4'}"/>`).join('') + '<path d="M0 980 C 600 900, 1200 1060, 2120 940" stroke="#bcd9ee" stroke-width="60" fill="none"/>'));
      s.route = M.path(L, 0, 0, 1920, 1080, 'M480 700 L480 520 L860 520 L860 360 L1240 360', R, 10, 'stroke-dasharray=".015 .012"');
      s.you = M.box(L, 456, 676, { width: '48px', height: '48px', borderRadius: '50%', background: '#3a7bff', border: '8px solid #fff', boxSizing: 'border-box', boxShadow: '0 4px 12px rgba(0,0,0,.2)' }); s.yl = M.txt(L, 380, 740, f(900, 34, M.CN), INK, '你 · You');
      s.pulse = [0, 1].map(() => M.box(L, 1190, 330, { width: '100px', height: '60px', borderRadius: '50%', border: `4px solid ${R}`, boxSizing: 'border-box', transformOrigin: '50% 50%' }));
      s.pin = M.svg(L, 1200, 230, 80, 130, `<path d="M40 128 C 40 128, 4 70, 4 40 A36 36 0 1 1 76 40 C 76 70, 40 128, 40 128Z" fill="${R}"/><circle cx="40" cy="40" r="14" fill="#fff"/>`, { transformOrigin: '50% 100%' });
      s.card = M.box(L, 1300, 380, { width: '460px', padding: '24px 28px', boxSizing: 'border-box', background: '#fff', borderRadius: '20px', boxShadow: '0 16px 34px rgba(20,40,60,.18)' });
      M.txt(s.card, 0, 0, f(900, 42, M.CN), INK, '示例门店', { position: 'static' }); M.txt(s.card, 0, 0, f(700, 28, M.CN), '#5a6676', '示例路 88 号', { position: 'static', marginTop: '8px' }); M.txt(s.card, 0, 0, f(600, 22, M.INTER), '#8a96a6', 'SAMPLE ADDRESS · 10:00–22:00', { position: 'static', marginTop: '10px' });
      s.t = M.txt(L, 110, 80, f(900, 70, M.CN), INK, '来店里找我们', { background: 'rgba(238,240,234,.85)', padding: '0 10px' });
      return s; },
    update(s, t) { s.map.style.transform = `scale(${(1.08 - .008 * t).toFixed(4)})`; M.hero(s.t, t, .7, 10.3);
      const pv = M.env(t, 1.1, 10.3, .3), pu = M.os((t - 1.1) / .35); s.pin.style.opacity = pv.a; s.pin.style.transform = `translateY(${(-160 * (1 - Math.min(1, pu))).toFixed(1)}px) scaleY(${(1 - .12 * Math.exp(-(t - 1.45) * 10) * (t > 1.45)).toFixed(3)})`;
      s.pulse.forEach((p, i) => { const d = ((t - 1.5 - i * .7) % 1.4) / 1.4; p.style.opacity = t > 1.5 ? (1 - d).toFixed(3) : 0; p.style.transform = `scale(${(.4 + 1.6 * d).toFixed(3)})`; });
      M.panel(s.card, t, 1.8, 10.3, { r: 20 }); M.pop(s.you, t, 3.5, 10.3, { from: .3 }); M.rise(s.yl, t, 3.6, 10.3); s.route.setAttribute('stroke-dashoffset', 0); const u = M.io((t - 3.8) / 2.2);
      s.route.style.clipPath = `inset(0 ${(100 - 100 * Math.min(1, u * 1.0)).toFixed(1)}% 0 0)`; s.route.style.opacity = t > 3.8 ? 1 : 0; } });
})();
