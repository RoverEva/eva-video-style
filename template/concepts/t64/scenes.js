/* T64 Price Tag 电商促销 · 10 s sample. A swinging hang tag; old price struck, new price lands; SALE stamp. Prices are SAMPLE. */
(function () { const C = EV, M = K.T.mo, f = M.f, R = '#ff3b30', INK = '#1d1d1f';
  M.setup({ bg: 'linear-gradient(160deg,#fff1e8,#ffd9c7)', win: { x: 1260, y: 140, w: 500, h: 580, r: 28, o: 1, s: 1.15 }, ring: () => ({ color: R, width: 8, shadow: .3 }), port: { box: [90, 30, 1080, 790] },
    captions: M.caps([['今天有好价', "Today's deal"], ['限时三天（示例）', 'Three days only (sample)'], ['喜欢就别等', "Like it? Don't wait"]]),
    build(L) { const s = {};
      s.str = M.path(L, 380, 0, 20, 120, 'M10 0 V118', '#8a6d5a', 3);
      s.tag = M.box(L, 200, 110, { width: '380px', height: '440px', transformOrigin: '190px 10px' });
      M.svg(s.tag, 0, 0, 380, 440, `<path d="M190 0 L370 110 L370 430 Q370 440 360 440 L20 440 Q10 440 10 430 L10 110Z" fill="#fff" stroke="${INK}" stroke-width="6"/><circle cx="190" cy="70" r="20" fill="none" stroke="${INK}" stroke-width="6"/>`);
      s.old = M.txt(s.tag, 0, 140, f(400, 80, M.AN), '#9a9a9a', '¥99', { width: '380px', textAlign: 'center' }); s.strike = M.path(s.tag, 90, 170, 200, 40, 'M6 30 L194 8', R, 8);
      s.neu = M.txt(s.tag, 0, 240, f(400, 150, M.AN), R, '¥59', { width: '380px', textAlign: 'center', lineHeight: 1 }); M.txt(s.tag, 0, 400, f(700, 22, M.INTER), '#777', 'SAMPLE PRICE 示例价格', { width: '380px', textAlign: 'center' });
      s.t = M.txt(L, 640, 150, f(900, 84, M.CN), INK, '今日好价'); s.chips = ['限时 3 天', '包邮', '7 天退换'].map((c, i) => M.txt(L, 640, 290 + i * 90, f(900, 44, M.CN), '#fff', c, { background: i ? INK : R, padding: '6px 22px', borderRadius: '12px' }));
      s.sale = M.txt(L, 640, 610, f(400, 110, M.AN), R, 'SALE -40%', { border: `8px solid ${R}`, padding: '0 22px', borderRadius: '16px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.draw(s.str, t, .6, .3, 9.2); const v = M.env(t, .75, 9.2, .3), d = Math.max(0, t - .75); s.tag.style.opacity = v.a;
      s.tag.style.transform = `translateY(${(-80 * (1 - Math.min(1, M.o3(d / .4)))).toFixed(1)}px) rotate(${(14 * Math.exp(-d * 1.6) * Math.sin(d * 5.5) + (t > 3.9 && t < 5 ? 5 * Math.exp(-(t - 3.9) * 3) * Math.sin((t - 3.9) * 12) : 0)).toFixed(2)}deg)`;
      M.rise(s.old, t, 1.2, 9.2); M.draw(s.strike, t, 3.6, .3, 9.2); M.pop(s.neu, t, 3.9, 9.2, { from: 1.6 });
      M.hero(s.t, t, 1.0, 9.2); s.chips.forEach((c, i) => M.slide(c, t, 4.4 + i * .14, 9.2, { dx: 40 })); M.pop(s.sale, t, 6.85, 9.2, { from: 1.6, base: 'rotate(-5deg)' }); } });
})();
