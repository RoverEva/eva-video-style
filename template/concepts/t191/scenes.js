/* T191 三行汇报 Three Lines: a clean weekly report in three numbered lines, each one gets its own scene. */
(function () { const M = K.T.mo, X = M.X, INK = '#111', BL = '#2f6fe8', OR = '#e8642f';
  const line = (c, n, k, v, col) => { const g = M.box(c, 160, 0, {}); X(g, 0, 0, 34, '#8a8f98', `0${n}  ${k}`, 700, M.MONO); g.v = X(g, 0, 56, 96, col, v, 900); g.u = M.box(g, 0, 190, { width: '0px', height: '8px', background: col }); return g; };
  M.story({ bg: '#fff', sbg: ['#fff', '#f7f9fc', '#fff'], tr: ['rise', 'rise'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1360, 160, 420, 500, 20), M.q(1360, 160, 420, 500, 20), M.q(1360, 160, 420, 500, 20)],
    caps: [['这周汇报，就三行', 'This week’s report: three lines'], ['数据：留存涨了 6%（示例）', 'Data: retention +6% (sample)'], ['下一步：周五前修完反馈', 'Next: fix feedback by Friday']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ l: line(c, 1, '结论', '本周上线 2 个功能', INK), d: [0, 1].map(i => M.box(c, 160 + i * 120, 620, { width: '90px', height: '90px', borderRadius: '50%', background: BL, color: '#fff', font: M.f(900, 44, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center' }, '✓')) }),
       (s, t, a) => { s.l.style.top = '300px'; M.rise(s.l, t, a + .2, 99); s.l.u.style.width = (900 * M.o3((t - a - .7) / .6)) + 'px'; s.d.forEach((e, i) => M.pop(e, t, a + 1.1 + i * .2, 99, { from: 0 })); }],
      [c => ({ l: line(c, 2, '数据', '留存 +6%（示例）', BL), sp: M.path(c, 160, 560, 900, 220, 'M0 200 C 200 180, 300 120, 450 130 S 700 40, 890 20', BL, 8) }),
       (s, t, a) => { s.l.style.top = '240px'; M.rise(s.l, t, a - .1, 99); s.l.u.style.width = (900 * M.o3((t - a - .4) / .6)) + 'px'; M.draw(s.sp, t, a + .5, 1.2, 99); }],
      [c => ({ l: line(c, 3, '下一步', '周五前修完反馈', OR), cal: M.box(c, 160, 600, { display: 'flex', gap: '14px' }) }),
       (s, t, a) => { s.l.style.top = '240px'; M.rise(s.l, t, a - .1, 99); s.l.u.style.width = (900 * M.o3((t - a - .4) / .6)) + 'px'; if (!s.d) { s.d = ['一', '二', '三', '四', '五'].map(n => M.box(s.cal, 0, 0, { position: 'relative', width: '120px', height: '120px', borderRadius: '16px', background: '#f1f3f6', color: INK, font: M.f(900, 44, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center' }, n)); } s.d.forEach((e, i) => { M.pop(e, t, a + .5 + i * .1, 99, { from: .3 }); e.style.background = i === 4 && t > a + 1.3 ? OR : '#f1f3f6'; e.style.color = i === 4 && t > a + 1.3 ? '#fff' : INK; }); }]
    ] });
})();
