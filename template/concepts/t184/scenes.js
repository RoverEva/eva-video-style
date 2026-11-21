/* T184 点阵手账 Dot Journal: dotted paper, hand-drawn checklist ticks itself, a doodle sprout grows. */
(function () { const M = K.T.mo, X = M.X, INK = '#2a2a2a', TL = '#2a9d8f';
  const paper = c => M.box(c, 160, 70, { width: '980px', height: '900px', background: '#fffdf7', backgroundImage: 'radial-gradient(#c9c2b4 2px, transparent 2px)', backgroundSize: '36px 36px', boxShadow: '0 20px 40px rgba(0,0,0,.08)' });
  M.story({ bg: '#f6f2ea', sbg: ['#f6f2ea', '#f1ece2', '#f6f2ea'], tr: ['flip', 'slide'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1340, 180, 420, 500, 20), M.q(1340, 180, 420, 500, 20), M.c(1360, 180, 380)],
    caps: [['这周的家居清单', 'This week’s home to-do list'], ['做完一件，勾一件', 'Done one, tick one'], ['小家，慢慢长出来', 'A home grows slowly']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ p: paper(c), t: X(c, 220, 130, 64, INK, '本周家居清单', 900), u: M.path(c, 220, 220, 460, 30, 'M0 15 C 120 5, 300 25, 450 12', '#e9c46a', 10) }), (s, t, a) => { M.rise(s.p, t, a, 99, { dy: 80 }); M.hero(s.t, t, a + .4, 99); M.draw(s.u, t, a + .9, .6, 99); }],
      [c => ({ p: paper(c), it: ['换新窗帘', '整理书架', '买一盆绿萝', '修好台灯'].map((n, i) => { const g = M.box(c, 230, 200 + i * 130, {}); M.box(g, 0, 10, { width: '50px', height: '50px', border: `4px solid ${INK}`, borderRadius: '8px', boxSizing: 'border-box' }); g.ck = M.path(g, 4, 4, 60, 60, 'M8 30 L24 46 L56 6', TL, 8); X(g, 80, 0, 56, INK, n, 900); return g; }) }),
       (s, t, a) => { s.p.style.opacity = 1; s.it.forEach((g, i) => { M.rise(g, t, a - .1 + i * .15, 99); if (i < 3) M.draw(g.ck, t, a + .7 + i * .45, .3, 99); }); }],
      [c => ({ p: paper(c), st: M.path(c, 500, 260, 300, 600, 'M150 590 C 150 400, 140 300, 150 160', TL, 10), l1: M.path(c, 500, 260, 300, 600, 'M150 300 C 80 260, 40 200, 60 140 C 120 160, 150 220, 150 300', TL, 8), l2: M.path(c, 500, 260, 300, 600, 'M150 220 C 220 180, 260 120, 240 60 C 180 80, 150 140, 150 220', TL, 8), t: X(c, 230, 130, 56, INK, '慢慢长出来', 900) }),
       (s, t, a) => { s.p.style.opacity = 1; M.draw(s.st, t, a - .1, 1, 99); M.draw(s.l1, t, a + .7, .6, 99); M.draw(s.l2, t, a + 1.1, .6, 99); M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
