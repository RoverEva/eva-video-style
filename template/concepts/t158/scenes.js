/* T158 模块拼贴 Bento: bento tiles snap into a grid around the window, then re-flow. */
(function () { const M = K.T.mo, X = M.X;
  const tile = (c, x, y, w, h, bg, html, fg) => { const g = M.box(c, x, y, { width: w + 'px', height: h + 'px', borderRadius: '36px', background: bg, color: fg || '#111', padding: '30px', boxSizing: 'border-box', font: M.f(900, 52, M.CN), transformOrigin: '50% 50%' }, html); return g; };
  M.story({ bg: '#f2efe9', sbg: ['#f2efe9', '#f7f4ee', '#111'], tr: ['zoom', 'flip'], ring: () => ({ color: '#ffffff', width: 0, shadow: .25 }),
    wins: [M.q(40, 40, 840, 560, 36, 1.05), M.q(1060, 40, 820, 520, 36, 1.05), M.q(60, 60, 600, 600, 36, 1.05)],
    caps: [['做视频，其实就几块', 'A video is just a few blocks'], ['速度、字幕、风格', 'Speed, captions, style'], ['EVA Video Style', 'EVA Video Style']], port: { box: [20, 20, 1880, 960] },
    scenes: [
      [c => ({ T: [tile(c, 920, 40, 440, 260, '#ff6b6b', '3×<div style="font-size:30px;font-weight:600">faster</div>'), tile(c, 1400, 40, 480, 560, '#4d8bff', '自动<br>双语字幕', '#fff'), tile(c, 920, 340, 440, 260, '#ffd23f', '✦'), tile(c, 40, 640, 860, 300, '#6bd16b', '几分钟出片'), tile(c, 940, 640, 940, 300, '#222', 'EVA VIDEO STYLE', '#fff')] }),
       (s, t, a) => s.T.forEach((g, i) => M.pop(g, t, a + .2 + i * .14, 99, { from: .4 }))],
      [c => ({ T: [tile(c, 40, 40, 980, 300, '#222', '速度 Speed', '#fff'), tile(c, 40, 380, 480, 560, '#ff6b6b', '字幕<br>CN / EN'), tile(c, 560, 380, 460, 260, '#ffd23f', '风格'), tile(c, 560, 680, 460, 260, '#4d8bff', '✦✦✦', '#fff'), tile(c, 1060, 600, 820, 340, '#6bd16b', '一键模版')] }),
       (s, t, a) => s.T.forEach((g, i) => M.slide(g, t, a - .15 + i * .1, 99, { dx: i % 2 ? 200 : -200 }))],
      [c => ({ T: [tile(c, 720, 60, 1140, 380, '#4d8bff', 'EVA<br>VIDEO STYLE', '#fff'), tile(c, 720, 480, 540, 460, '#ff6b6b', '200<div style="font-size:30px">templates</div>'), tile(c, 1300, 480, 560, 460, '#ffd23f', '开始 →')] }),
       (s, t, a) => { s.T.forEach((g, i) => M.pop(g, t, a - .1 + i * .18, 99, { from: .5 })); }]
    ] });
})();
