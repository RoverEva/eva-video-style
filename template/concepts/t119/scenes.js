/* T119 皮肤分层 Skin Layers (general skincare info). Moisturisers act on the epidermis; UV damages dermal collagen. */
(function () { const M = K.T.mo, X = M.X, INK = '#5a2e22';
  const L = [['表皮', 'Epidermis', '#f6c9b5'], ['真皮', 'Dermis', '#e89c8a'], ['皮下组织', 'Subcutis', '#f3dc9c']];
  M.story({ bg: '#fdf1ec', sbg: ['#fdf1ec', '#f7e1d7', '#fff6ef'], tr: ['zoom', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1500, 470, 330), M.q(1380, 160, 400, 480, 30), M.c(1420, 150, 380)],
    caps: [['皮肤其实有三层', 'Skin has three layers'], ['保湿，主要作用在表皮', 'Moisturiser works on the top layer'], ['防晒，保护真皮里的胶原', 'Sunscreen protects collagen in the dermis']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ sl: L.map(([cn, en, col], i) => { const g = M.box(c, 160, 220 + i * 150, { width: '900px', height: '130px', background: col, borderRadius: '20px', transform: 'skewX(-20deg)', boxShadow: '0 14px 20px rgba(90,46,34,.15)' }); g.lb = X(c, 1100, 250 + i * 150, 44, INK, `${cn} · ${en}`); return g; }) }),
       (s, t, a) => s.sl.forEach((g, i) => { M.rise(g, t, a + .2 + i * .25, 99, { dy: -120, base: 'skewX(-20deg)' }); M.hero(g.lb, t, a + .4 + i * .25, 99); })],
      [c => ({ top: M.card(c, 120, 400, 1100, 200, '#f6c9b5', { borderRadius: '30px' }), drops: Array.from({ length: 9 }, (_, i) => M.svg(c, 180 + i * 115, 200, 60, 80, '<path d="M30 4 C 30 4, 6 40, 6 54 a24 24 0 0 0 48 0 C 54 40, 30 4, 30 4Z" fill="#7cc6fe"/>')), t: X(c, 160, 640, 64, INK, '保湿 → 表皮') }),
       (s, t, a) => { M.panel(s.top, t, a - .15, 99, { r: 30 }); s.drops.forEach((e, i) => { const u = M.i2((t - a - i * .1) / .7); e.style.opacity = u > 0 && u < 1 ? 1 : 0; e.style.transform = `translateY(${(220 * u).toFixed(1)}px)`; }); M.hero(s.t, t, a + .6, 99); }],
      [c => ({ sun: M.svg(c, 220, 120, 220, 220, `<circle cx="110" cy="110" r="60" fill="#ffb703"/>${Array.from({ length: 10 }, (_, i) => `<path d="M110 10 V36" stroke="#ffb703" stroke-width="10" transform="rotate(${i * 36} 110 110)"/>`).join('')}`, { transformOrigin: '50% 50%' }),
          sh: M.svg(c, 560, 220, 300, 340, '<path d="M150 10 L280 60 V170 C 280 260, 150 320, 150 320 C 150 320, 20 260, 20 170 V60Z" fill="#ff8fab"/><path d="M95 160 L140 205 L215 120" stroke="#fff" stroke-width="18" fill="none"/>', { transformOrigin: '50% 50%' }), t: X(c, 160, 620, 64, INK, '防晒 → 守住真皮胶原') }),
       (s, t, a) => { M.pop(s.sun, t, a - .1, 99, { from: .3, base: `rotate(${(t * 20).toFixed(1)}deg)` }); M.pop(s.sh, t, a + .4, 99, { from: .3 }); M.hero(s.t, t, a + .6, 99); }]
    ] });
})();
