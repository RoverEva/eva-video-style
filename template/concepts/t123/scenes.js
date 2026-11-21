/* T123 案卷剪报 Case Clippings (illustrative evidence board). */
(function () { const M = K.T.mo, X = M.X, R = '#d62828';
  const clip = (c, x, y, r, s2) => { const g = M.box(c, 0, 0, { width: '300px', height: '240px', background: '#f4efe2', boxShadow: '0 10px 18px rgba(0,0,0,.3)', padding: '20px', boxSizing: 'border-box', font: M.f(900, 34, M.SERIF), color: '#2a2a2a', transformOrigin: '50% 10%' }, s2 + '<div style="margin-top:14px;height:12px;background:#ccc"></div><div style="margin-top:10px;height:12px;width:70%;background:#ccc"></div><div style="margin-top:10px;height:12px;width:85%;background:#ccc"></div>');
    M.box(g, 142, -10, { width: '20px', height: '20px', borderRadius: '50%', background: R }); return { g, x, y, r }; };
  M.story({ bg: '#b08a5f', sbg: ['#b08a5f', '#1b1712', '#a98256'], tr: ['push', 'zoom'], ring: () => ({ color: '#f4efe2', width: 8, shadow: .4 }),
    wins: [M.q(1400, 140, 400, 480, 14), M.c(1500, 140, 340), M.c(1440, 150, 380)],
    caps: [['一个案子，先把证据钉上墙', 'Pin the evidence up first'], ['证据 B：聊天记录（示例）', 'Exhibit B: chat records (sample)'], ['证据要能连成一条线', 'Evidence must connect into a line']], port: { box: [100, 40, 1820, 820] },
    scenes: [
      [c => ({ cork: M.dots(c, 'rgba(60,40,20,.3)', 22, 2), cl: [clip(c, 160, 120, -4, '证据 A'), clip(c, 560, 90, 3, '证据 B'), clip(c, 260, 450, 2, '证据 C'), clip(c, 760, 430, -3, '证据 D')], str: M.path(c, 0, 0, 1300, 900, 'M310 120 L710 90 L410 450 L910 430', R, 4) }),
       (s, t, a) => { s.cl.forEach(({ g, x, y, r }, i) => M.slap(g, t, a + .2 + i * .22, 99, { x, y, r })); M.draw(s.str, t, a + 1.2, .9, 99); }],
      [c => ({ big: M.card(c, 220, 160, 1000, 640, '#f4efe2', { borderRadius: '4px', padding: '60px', boxSizing: 'border-box' }), hl: M.box(c, 280, 420, { width: '0px', height: '60px', background: 'rgba(255,214,0,.55)' }) }),
       (s, t, a) => { if (!s.big.d) { X(s.big, 60, 50, 64, '#2a2a2a', '证据 B · 聊天记录', 900, M.SERIF); X(s.big, 60, 170, 38, '#555', '“工资下个月一起发。”（示例）', 700, M.SERIF); X(s.big, 60, 260, 38, '#555', '日期：3 月 5 日', 700, M.SERIF); s.big.d = 1; } M.pop(s.big, t, a - .15, 99, { from: .8 }); s.hl.style.width = (720 * M.io((t - a - .7) / .6)) + 'px'; }],
      [c => ({ ln: M.path(c, 160, 460, 1200, 20, 'M0 10 H1180', R, 6), pts: ['3 月 5 日', '4 月 1 日', '4 月 20 日'].map((d, i) => { const g = M.box(c, 160 + i * 500, 300, {}); M.box(g, 0, 140, { width: '40px', height: '40px', borderRadius: '50%', background: R }); X(g, 0, 0, 48, '#2a2a2a', d, 900, M.SERIF); X(g, 0, 210, 34, '#4a3a2a', ['证据 B', '证据 A', '证据 D'][i], 800, M.SERIF); return g; }) }),
       (s, t, a) => { M.draw(s.ln, t, a - .1, .9, 99); s.pts.forEach((g, i) => M.pop(g, t, a + .3 + i * .3, 99, { from: .5 })); }]
    ] });
})();
