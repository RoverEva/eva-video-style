/* T181 等距户型 Iso Floor (home): isometric rooms drop in and label, then a furniture swap. */
(function () { const M = K.T.mo, X = M.X, INK = '#3a3a3a';
  const tile = (c, x, y, w, h, col, n) => { const g = M.box(c, x, y, { width: w + 'px', height: h + 'px', background: col, borderRadius: '10px', boxShadow: '0 14px 0 rgba(0,0,0,.12)', color: '#3a2a1a', font: M.f(900, 38, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' }, n); return g; };
  const plan = c => { const p = M.box(c, 420, 210, { width: '700px', height: '520px', transform: 'rotateX(55deg) rotateZ(-45deg)', transformOrigin: '50% 50%' }); p.r = [[0, 0, 340, 300, '#f2c14e', '客厅'], [360, 0, 340, 180, '#f4a261', '厨房'], [360, 200, 340, 320, '#c9b3ec', '书房'], [0, 320, 340, 200, '#8fd3d0', '卧室']].map(([x, y, w, h, col, n]) => tile(p, x, y, w, h, col, n)); return p; };
  M.story({ bg: '#f3efe6', sbg: ['#f3efe6', '#efe9dc', '#f3efe6'], tr: ['zoom', 'slide'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1400, 180, 400, 480, 20), M.q(1400, 180, 400, 480, 20), M.c(110, 180, 360)],
    caps: [['一套 80 平的小家（示例）', 'An 80 m² home (sample)'], ['四个区，各有用处', 'Four zones, each with a job'], ['书房换成儿童房，也行', 'The study can become a kids’ room']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ p: plan(c), n: X(c, 120, 120, 120, INK, '80 m²', 400, M.AN) }), (s, t, a) => { s.p.style.opacity = M.env(t, a, 99).a; s.p.r.forEach((e, i) => { const u = M.os((t - a - .2 - i * .2) / .5); e.style.opacity = t > a + .2 + i * .2 ? 1 : 0; e.style.transform = `translateY(${(-300 * (1 - u)).toFixed(0)}px)`; }); M.hero(s.n, t, a + .2, 99); M.count(s.n, 80, t, a + .2, 1, v => v + ' m²'); }],
      [c => ({ p: plan(c), ls: [['会客', 260], ['做饭', 360], ['安静', 460], ['睡觉', 560]].map(([n, y], i) => X(c, 1060, 200 + i * 130, 48, INK, '· ' + n, 900)) }),
       (s, t, a) => { s.p.style.opacity = 1; s.p.r.forEach((e, i) => { e.style.opacity = 1; e.style.transform = `translateY(${(-20 * Math.max(0, Math.sin((t - a) * 3 - i))).toFixed(0)}px)`; }); s.ls.forEach((e, i) => M.slide(e, t, a + i * .2, 99, { dx: 80 })); }],
      [c => ({ p: plan(c) }), (s, t, a) => { s.p.style.opacity = 1; s.p.style.transform = 'translateX(260px) rotateX(55deg) rotateZ(-45deg)'; s.p.r.forEach((e, i) => { e.style.opacity = 1; e.style.transform = ''; if (i === 2) { const u = M.io((t - a - .4) / .6); e.style.transform = `rotateY(${(180 * u).toFixed(0)}deg)`; e.textContent = u > .5 ? '儿童房' : '书房'; e.style.background = u > .5 ? '#ffb3c6' : '#c9b3ec'; e.style.direction = u > .5 ? 'rtl' : ''; if (u > .5) e.style.transform += ' scaleX(-1)'; } }); }]
    ] });
})();
