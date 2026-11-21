/* T152 爆炸图 Exploded View (logo/text only): a bottle assembles, explodes into labelled layers, reassembles. */
(function () { const M = K.T.mo, X = M.X, INK = '#2f3e46';
  const P = [['#2f3e46', 60, 380, '杯盖 Lid'], ['#84a98c', 24, 360, '密封圈 Seal'], ['#cad2c5', 300, 330, '内胆 Liner'], ['#52796f', 250, 380, '外壳 Shell']];
  const parts = c => P.map(([col, h, w, n], i) => { const g = M.box(c, 0, 0, {}); g.b = M.box(g, -w / 2, 0, { width: w + 'px', height: h + 'px', background: col, borderRadius: i === 0 ? '30px 30px 10px 10px' : i === 3 ? '20px 20px 60px 60px' : '14px' }); g.l = M.path(g, w / 2 + 20, h / 2 - 10, 240, 20, 'M0 10 H230', INK, 3); g.n = X(g, w / 2 + 270, h / 2 - 30, 40, INK, n, 700); g.h = h; return g; });
  const place = (L, t, a, ex) => { let y = 0; const Y = [0, 60, 84, 404]; L.forEach((g, i) => { const yy = 100 + Y[i] + ex * i * 50; g.style.opacity = M.env(t, a + i * .05, 99).a; g.style.transform = `translate(760px, ${yy.toFixed(1)}px)`; g.l.parentNode.style.opacity = ex; g.n.style.opacity = ex; }); };
  M.story({ noface: true, bg: '#eef1f4', sbg: ['#eef1f4', '#e6ebef', '#eef1f4'], tr: ['zoom', 'rise'],
    caps: [['一只保温杯', 'One insulated bottle'], ['拆开看，四层结构', 'Take it apart: four layers'], ['合上，就是一整天的温度', 'Put together: heat all day']], port: { box: [300, 80, 1400, 900] },
    scenes: [
      [c => ({ p: parts(c), t: X(c, 160, 160, 90, INK, '拆开看', 900) }), (s, t, a) => { place(s.p, t, a, 0); s.p.forEach((g, i) => g.style.transform += ` rotate(${(3 * Math.sin(t)).toFixed(1)}deg)`); M.hero(s.t, t, a + .3, 99); }],
      [c => ({ p: parts(c) }), (s, t, a) => place(s.p, t, a - .15, M.os((t - a) / .9))],
      [c => ({ p: parts(c), t: X(c, 160, 400, 80, INK, '一整天的温度', 900), n: X(c, 160, 520, 120, '#52796f', '12 h', 400, M.AN) }),
       (s, t, a) => { place(s.p, t, a - .1, 1 - M.io((t - a) / .8)); M.hero(s.t, t, a + .6, 99); M.hero(s.n, t, a + .8, 99); M.count(s.n, 12, t, a + .8, 1, v => v + ' h'); }]
    ] });
})();
