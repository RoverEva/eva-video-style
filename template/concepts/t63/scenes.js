/* T63 Unboxing 开箱 · 10 s sample. A kraft box opens, a generic product card rises, callout lines draw to features (illustrative). */
(function () { const C = EV, M = K.T.mo, f = M.f, KR = '#c99a63', INK = '#2c2219';
  M.setup({ bg: 'radial-gradient(ellipse at 40% 60%, #fbf3e6, #e9dcc8)', win: { x: 1270, y: 150, w: 500, h: 560, r: 26, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['开箱时间到', 'Unboxing time'], ['轻、小、好用', 'Light, compact, easy'], ['开箱完成，你想要吗？', 'Unboxed — want one?']]),
    build(L) { const s = {};
      s.t = M.txt(L, 110, 70, f(900, 80, M.CN), INK, '开箱时间 📦'); s.e = M.txt(L, 114, 170, f(700, 32, M.INTER), '#7b6550', 'UNBOXING · 示例产品 SAMPLE');
      s.prod = M.box(L, 330, 470, { width: '300px', height: '220px', borderRadius: '36px', background: 'linear-gradient(140deg,#6fd3c1,#3b7dd8)', boxShadow: '0 20px 40px rgba(40,60,90,.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: f(400, 64, M.AN), color: '#fff' }, 'NEW');
      s.box = M.svg(L, 260, 520, 440, 280, `<path d="M0 40 L440 40 L410 280 L30 280Z" fill="${KR}"/><path d="M0 40 L440 40 L440 70 L0 70Z" fill="#b5864f"/><path d="M200 70 H240 V280 H200Z" fill="rgba(255,255,255,.35)"/>`);
      s.fl = M.svg(L, 260, 520, 220, 60, `<path d="M0 40 L220 40 L200 0 L20 0Z" fill="#d8ab74"/>`, { transformOrigin: '0 40px' }); s.fr = M.svg(L, 480, 520, 220, 60, `<path d="M0 40 L220 40 L200 0 L20 0Z" fill="#d8ab74"/>`, { transformOrigin: '220px 40px' });
      s.co = [['轻 Light', 300], ['小 Compact', 380], ['好用 Easy', 460]].map(([w, y], i) => { const p = M.path(L, 640, y - 10, 120, 40, `M0 ${20 + (i - 1) * 14} L50 20 L110 20`, INK, 4); M.box(L, 626, y + (i - 1) * 14 - 4, { width: '16px', height: '16px', borderRadius: '50%', background: INK }); p.dot = p.parentNode.previousSibling; p.lb = M.txt(L, 770, y - 30, f(900, 44, M.CN), INK, w); return p; });
      s.co.forEach(p => { p.dot = p.parentNode.nextSibling; });
      s.ok = M.txt(L, 770, 560, f(900, 54, M.CN), '#fff', '开箱完成 ✓', { background: '#2fbf71', padding: '6px 24px', borderRadius: '14px' });
      return s; },
    update(s, t) { M.hero(s.t, t, .85, 9.2); M.rise(s.e, t, 1.15, 9.2); M.rise(s.box, t, 1.0, 9.2, { dy: 60 });
      const op = M.os((t - 1.8) / .5); [s.fl, s.fr].forEach((e, i) => { M.rise(e, t, 1.0, 9.2, { dy: 60 }); e.style.transform += ` rotate(${((i ? 1 : -1) * 150 * Math.max(0, op)).toFixed(1)}deg)`; });
      const up = M.os((t - 2.4) / .6); s.prod.style.opacity = (Math.min(1, Math.max(0, (t - 2.4) / .2)) * (1 - M.i2((t - 8.97) / .23))).toFixed(3); s.prod.style.transform = `translateY(${(-200 * Math.max(0, up)).toFixed(1)}px) rotate(${(-6 * (1 - Math.min(1, up))).toFixed(1)}deg)`;
      s.co.forEach((p, i) => { M.draw(p, t, 3.6 + i * .35, .45, 9.2); M.rise(p.lb, t, 3.95 + i * .35, 9.2, { dy: 14 }); M.pop(p.dot, t, 3.6 + i * .35, 9.2, { from: 0 }); });
      M.pop(s.ok, t, 6.85, 9.2, { from: .5 }); } });
})();
