/* T76 Lunar New Year 新春红金 · 10 s sample (illustrative copy). Swinging lanterns, gold serif title, 福 diamond spins in, gold sparkles. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, GOLD = '#ffd58a', R = '#b3121b';
  const gold = { backgroundImage: 'linear-gradient(180deg,#fff1c9,#f2c15a 50%,#c98b1b)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 6px rgba(80,0,0,.4))' };
  const lantern = (p, x, len) => { const g = M.box(p, x, 0, { width: '120px', height: (len + 170) + 'px', transformOrigin: '60px 0' });
    M.svg(g, 0, 0, 120, len + 170, `<path d="M60 0 V${len}" stroke="${GOLD}" stroke-width="3"/><rect x="40" y="${len}" width="40" height="14" fill="${GOLD}"/><ellipse cx="60" cy="${len + 70}" rx="56" ry="58" fill="#e0281f"/><path d="M60 ${len + 12} V${len + 128} M30 ${len + 22} Q 18 ${len + 70} 30 ${len + 118} M90 ${len + 22} Q 102 ${len + 70} 90 ${len + 118}" stroke="#ffb02e" stroke-width="3" fill="none" opacity=".7"/><rect x="40" y="${len + 124}" width="40" height="12" fill="${GOLD}"/><path d="M50 ${len + 136} V${len + 168} M60 ${len + 136} V${len + 170} M70 ${len + 136} V${len + 168}" stroke="${GOLD}" stroke-width="3"/>`); return g; };
  M.setup({ bg: `radial-gradient(ellipse at 40% 40%, #d11a24, ${R} 50%, #6e0a10)`, win: { x: 1270, y: 170, w: 490, h: 490, r: 245, o: 1, s: 1.15 }, ring: () => ({ color: GOLD, width: 10, glow: 'rgba(255,213,138,.5)', shadow: .5 }), port: { box: [90, 0, 1080, 790] },
    captions: M.caps([['新年快乐！', 'Happy New Year!'], ['福到了，好运来', 'Good fortune is here'], ['祝你万事如意', 'May all go your way']]),
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(255,213,138,.10) 2px, transparent 2.5px)', backgroundSize: '36px 36px' }));
      s.lan = [[120, 60], [900, 20], [1050, 110]].map(([x, l]) => lantern(L, x, l));
      s.t = M.txt(L, 110, 300, f(900, 150, M.SERIF), '', '新年快乐', gold); s.e = M.txt(L, 120, 470, f('italic 700', 44, M.PF), GOLD, 'Happy Lunar New Year');
      s.fu = M.box(L, 700, 520, { width: '200px', height: '200px', background: '#e0281f', border: `6px solid ${GOLD}`, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' });
      M.txt(s.fu, 0, 0, f(900, 120, M.SERIF), GOLD, '福', { position: 'static', transform: 'rotate(-45deg)' });
      s.wish = M.txt(L, 110, 600, f(900, 72, M.SERIF), '', '万事如意', gold);
      s.sp = Array.from({ length: 26 }, (_, i) => M.box(L, 80 + (i * 173) % 1100, 0, { width: '10px', height: '10px', borderRadius: '50%', background: GOLD, boxShadow: `0 0 10px ${GOLD}` }));
      return s; },
    update(s, t) { s.lan.forEach((g, i) => { const v = M.env(t, .6 + i * .15, 9.25, .5), d = Math.max(0, t - .6 - i * .15); g.style.opacity = v.a; g.style.transform = `translateY(${(-200 * (1 - v.e)).toFixed(1)}px) rotate(${(6 * Math.sin(d * 2.2 + i) * (0.4 + .6 * Math.exp(-d))).toFixed(2)}deg)`; });
      M.hero(s.t, t, 1.1, 9.2, { dx: 0, dy: 40, noclip: true }); M.rise(s.e, t, 1.5, 9.2);
      const u = M.os((t - 3.6) / .6); s.fu.style.opacity = M.env(t, 3.6, 9.2, .4).a; s.fu.style.transform = `rotate(${(45 + 360 * (1 - Math.min(1, u))).toFixed(1)}deg) scale(${(.4 + .6 * u).toFixed(3)})`;
      M.hero(s.wish, t, 6.85, 9.2, { dx: 0, dy: 30, noclip: true });
      s.sp.forEach((e, i) => { const d = t - 6.8 - (i % 7) * .08; if (d < 0 || t > 9.25) { e.style.opacity = 0; return; } e.style.opacity = (Math.min(1, d * 4) * (1 - M.i2((t - 8.95) / .3))).toFixed(3); e.style.transform = `translateY(${(800 - 260 * d - (i * 37) % 300).toFixed(1)}px) scale(${(.6 + .4 * Math.abs(Math.sin(t * 6 + i))).toFixed(2)})`; }); } });
})();
