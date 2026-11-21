/* T58 Weather 天气预报 · 10 s sample. Generic forecast card; ALL temperatures are SAMPLE data (marked). */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#0f2d4a';
  const sun = (c) => `<g><circle cx="50" cy="50" r="22" fill="${c || '#ffc93c'}"/>${Array.from({ length: 8 }, (_, i) => `<path d="M50 ${12} V${22}" stroke="${c || '#ffc93c'}" stroke-width="6" stroke-linecap="round" transform="rotate(${i * 45} 50 50)"/>`).join('')}</g>`;
  const cloud = `<path d="M24 70 a16 16 0 0 1 4 -31 a22 22 0 0 1 42 -4 a16 16 0 0 1 8 35Z" fill="#ffffff"/>`;
  const rain = cloud + [30, 48, 66].map(x => `<path d="M${x} 78 l-5 12" stroke="#4aa3df" stroke-width="5" stroke-linecap="round"/>`).join('');
  M.setup({ bg: 'linear-gradient(180deg,#3d97d8,#bfe3ff)', win: { x: 1260, y: 150, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }), port: { box: [90, 40, 1060, 780] },
    captions: M.caps([['这周的拍摄天气（示例）', "This week's shooting weather (sample)"], ['周三有雨，备好室内景', 'Rain Wednesday — plan an indoor set'], ['晴天，出门拍！', 'Sunny — go shoot outside!']]),
    build(L) { const s = {};
      s.tag = M.txt(L, 110, 70, f(700, 28, M.INTER), INK, '天气预报 · FORECAST · 示例数据 SAMPLE', { background: 'rgba(255,255,255,.75)', padding: '8px 16px', borderRadius: '8px' });
      s.big = M.svg(L, 90, 130, 260, 260, `<g transform="scale(2.6)">${sun()}</g>`, { transformOrigin: '50% 50%' });
      s.tmp = M.txt(L, 380, 150, f(400, 190, M.AN), '#fff', '0°', { textShadow: '0 6px 18px rgba(0,40,80,.3)', lineHeight: 1 }); s.city = M.txt(L, 390, 350, f(900, 44, M.CN), '#fff', '晴 · 适合外拍');
      s.days = [['周一', sun(), '26°'], ['周二', cloud, '23°'], ['周三', rain, '19°'], ['周四', sun(), '25°']].map(([d, ic, tp], i) => { const c = M.box(L, 110 + i * 245, 440, { width: '220px', height: '230px', borderRadius: '24px', background: 'rgba(255,255,255,.28)', border: '2px solid rgba(255,255,255,.6)', textAlign: 'center' });
        M.txt(c, 0, 18, f(900, 36, M.CN), '#fff', d, { width: '220px' }); M.svg(c, 60, 66, 100, 100, ic); M.txt(c, 0, 168, f(400, 44, M.AN), '#fff', tp, { width: '220px' }); return c; });
      s.go = M.txt(L, 110, 700, f(900, 54, M.CN), INK, '☀ 晴天，出门拍！', { background: '#ffc93c', padding: '6px 24px', borderRadius: '14px' });
      return s; },
    update(s, t) { M.rise(s.tag, t, .75, 9.2); M.pop(s.big, t, .9, 9.2, { from: .3 }); s.big.style.transform += ` rotate(${(t * 12).toFixed(1)}deg)`;
      M.hero(s.tmp, t, 1.1, 9.2); M.count(s.tmp, 26, t, 1.1, 1.0, v => v + '°'); M.rise(s.city, t, 1.5, 9.2);
      s.days.forEach((c, i) => M.rise(c, t, 3.6 + i * .13, 9.2, { dy: 50 }));
      if (t > 4.4) { const c = s.days[2], k = Math.max(0, 1 - Math.abs(t - 5.0) / .5); c.style.background = `rgba(255,255,255,${(.28 + .4 * k).toFixed(3)})`; }
      M.pop(s.go, t, 6.85, 9.2, { from: .5 }); } });
})();
