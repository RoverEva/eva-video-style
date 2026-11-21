/* T105 三种解法 Three Solutions: rectangle with perimeter 20 — max area 25 (a square). */
(function () { const M = K.T.mo, X = M.X, G = '#2fbf71', INK = '#13213d';
  M.story({ bg: '#f4f6fb', sbg: ['#f4f6fb', '#0f1b33', '#f4f6fb'], tr: ['flip', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1420, 150, 380), M.c(1580, 110, 280), M.q(120, 170, 420, 500, 24)],
    caps: [['一道题，三种解法', 'One problem, three ways'], ['试算、画图、公式', 'Trial, drawing, formula'], ['答案：正方形，面积 25', 'Answer: a square, area 25']], port: { box: [100, 60, 1700, 800] },
    scenes: [
      [c => ({ q: M.card(c, 120, 200, 1160, 420, '#fff', { padding: '50px', boxSizing: 'border-box' }), rc: M.box(c, 820, 330, { width: '360px', height: '200px', border: '6px solid ' + INK, boxSizing: 'border-box' }) }),
       (s, t, a) => { if (!s.q.d) { X(s.q, 50, 40, 30, '#6a7aa0', 'QUESTION · 例题', 700, M.MONO); X(s.q, 50, 100, 58, INK, '长方形周长 20，', 900); X(s.q, 50, 190, 58, INK, '面积最大是多少？', 900); s.q.d = 1; }
         M.panel(s.q, t, a + .25, 99, { r: 20 }); const u = M.io((t - a - 1.2) / 1.4); s.rc.style.width = (360 - 160 * Math.sin(u * Math.PI * 2) * .5) + 'px'; M.pop(s.rc, t, a + 1.0, 99, { from: .6 }); }],
      [c => ({ col: [['解法一 · 试算', '1×9＝9<br>2×8＝16<br>4×6＝24<br>5×5＝25'], ['解法二 · 画图', '边越接近<br>越“方”<br>面积越大'], ['解法三 · 公式', 'a＋b＝10<br>ab ≤ 25']].map(([h, b], i) => { const g = M.card(c, 120 + i * 470, 220, 430, 500, '#17284d', { border: '2px solid #2a3f6e', padding: '36px', boxSizing: 'border-box' });
          X(g, 36, 30, 36, '#9fb4ff', h); X(g, 36, 110, 44, '#fff', b, 800, M.CN, { lineHeight: 1.5, whiteSpace: 'normal' }); return g; }) }),
       (s, t, a) => s.col.forEach((g, i) => M.rise(g, t, a - .15 + i * .22, 99, { dy: 120 }))],
      [c => ({ big: X(c, 640, 260, 150, INK, '5 × 5 ＝ 25'), ok: M.box(c, 640, 480, { padding: '14px 36px', background: G, borderRadius: '999px', font: M.f(900, 48, M.CN), color: '#fff' }, '最优：正方形 ✓'), sq: M.path(c, 1460, 260, 260, 260, 'M10 10 H250 V250 H10 Z', G, 10) }),
       (s, t, a) => { M.hero(s.big, t, a - .05, 99, { dx: 0, dy: 40 }); M.pop(s.ok, t, a + .5, 99, { from: .5 }); M.draw(s.sq, t, a + .3, .8, 99); }]
    ] });
})();
