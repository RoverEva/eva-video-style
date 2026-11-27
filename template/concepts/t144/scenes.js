/* T144 菜单黑板 Menu Board (food): a café chalk menu writes itself, prices tick in, today's special gets a star. Sample prices. */
(function () { const M = K.T.mo, X = M.X, CK = '#f4efe2', WD = '#6b4226', HW = "'Noto Sans CJK SC', cursive";
  const board = c => { const g = M.box(c, 140, 100, { width: '1160px', height: '780px', background: 'radial-gradient(ellipse at 40% 40%, #34373a, #1f2123)', border: `26px solid ${WD}`, borderRadius: '10px', boxSizing: 'border-box', boxShadow: '0 30px 60px rgba(0,0,0,.35)' }); return g; };
  const write = (e, t, a, d) => { const u = Math.max(0, Math.min(1, (t - a) / d)); e.style.clipPath = `inset(-20px ${(100 - 100 * u).toFixed(1)}% -20px -20px)`; e.style.opacity = t > a ? 1 : 0; };
  const items = [['手冲咖啡', 'Pour-over', 28], ['拿铁', 'Latte', 32], ['肉桂卷', 'Cinnamon roll', 22], ['今日特调', 'Today’s special', 36]];
  M.story({ bg: '#e8dccb', sbg: ['#e8dccb', '#e2d4c0', '#e8dccb'], tr: ['zoom', 'slide'], ring: () => ({ color: '#fffaf0', width: 12, shadow: .3 }),
    wins: [M.c(1440, 200, 380), M.c(1440, 200, 380), M.q(1380, 180, 420, 500, 20)],
    caps: [['今天的菜单，写在黑板上', 'Today’s menu, on the chalkboard'], ['四样，都是招牌（示例价格）', 'Four signatures (sample prices)'], ['推荐今日特调', 'Try today’s special']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ b: board(c), t: X(c, 260, 220, 120, CK, 'MENU', 700, M.PF, { fontStyle: 'italic' }), s: X(c, 266, 380, 50, '#ffd6a5', '今日菜单 · Café', 700, HW), cup: M.path(c, 900, 400, 280, 300, 'M40 80 H220 L200 260 H60Z M220 120 C 280 120, 280 200, 210 200 M90 60 C 80 30, 110 20, 100 0 M150 60 C 140 30, 170 20, 160 0', CK, 6) }),
       (s, t, a) => { s.b.style.opacity = M.env(t, a, 99).a; write(s.t, t, a + .3, .8); write(s.s, t, a + 1, .6); M.draw(s.cup, t, a + .6, 1.4, 99); }],
      [c => ({ b: board(c), rs: items.map(([cn, en, p], i) => { const g = M.box(c, 240, 190 + i * 150, { width: '960px' }); g.a = X(g, 0, 0, 60, CK, cn, 900, HW); g.e = X(g, 0, 74, 28, '#c9c2b4', en, 700, M.INTER); g.p = X(g, 820, 10, 60, '#ffd6a5', '¥0', 700, HW); g.d = M.path(g, 300, 40, 500, 10, 'M0 5 H500', '#8a8f94', 3, 'stroke-dasharray="6 10"'); g.v = p; return g; }) }),
       (s, t, a) => { s.b.style.opacity = 1; s.rs.forEach((g, i) => { const st = a - .1 + i * .4; write(g.a, t, st, .4); write(g.e, t, st + .2, .3); M.draw(g.d, t, st + .3, .3, 99); g.p.style.opacity = t > st + .5 ? 1 : 0; g.p.textContent = '¥' + Math.round(g.v * Math.min(1, Math.max(0, (t - st - .5) / .5))); }); }],
      [c => ({ b: board(c), sp: X(c, 260, 260, 110, CK, '今日特调', 900, HW), en: X(c, 266, 410, 44, '#c9c2b4', 'Today’s special · ¥36', 700, M.INTER), st: M.svg(c, 860, 160, 260, 260, '<path d="M130 10 L160 95 L250 95 L178 150 L205 240 L130 188 L55 240 L82 150 L10 95 L100 95Z" fill="none" stroke="#ffd166" stroke-width="8" stroke-linejoin="round"/>', { transformOrigin: '50% 50%' }) }),
       (s, t, a) => { s.b.style.opacity = 1; write(s.sp, t, a - .1, .8); write(s.en, t, a + .6, .5); M.pop(s.st, t, a + 1, 99, { from: 2 }); s.st.style.transform += ` rotate(${(10 * Math.sin(t * 2)).toFixed(1)}deg)`; }]
    ] });
})();
