/* T197 涂鸦片头 Doodle Opener (logo/text only): a marker swoosh draws, colourful characters bounce on it, doodle sparkles. */
(function () { const M = K.T.mo, X = M.X, CL = ['#ff4f4f', '#3fbf5f', '#2f8fff', '#a259ff'];
  const spark = (c, x, y, col) => M.svg(c, x, y, 90, 90, `<path d="M45 0 C 50 35, 55 40, 90 45 C 55 50, 50 55, 45 90 C 40 55, 35 50, 0 45 C 35 40, 40 35, 45 0Z" fill="${col}"/>`, { transformOrigin: '50% 50%' });
  const word = (c, txt, y) => [...txt].map((ch, i) => X(c, 960 - txt.length * 130 + i * 260, y, 220, CL[i % 4], ch, 900, M.CN, { textShadow: '6px 6px 0 #222' }));
  const bounce = (L, t, a) => L.forEach((e, i) => { const u = t - a - i * .15; e.style.opacity = u > 0 ? 1 : 0; const y = u < 0 ? -300 : u < .4 ? -300 * (1 - u / .4) * (1 - u / .4) : -30 * Math.abs(Math.sin((u - .4) * 6)) * Math.exp(-(u - .4) * 2.5); e.style.transform = `translateY(${y.toFixed(0)}px) rotate(${((i % 2 ? 6 : -6) * Math.sin(t * 3)).toFixed(1)}deg)`; });
  M.story({ noface: true, bg: '#fffaf0', sbg: ['#fffaf0', '#fff3e0', '#fffaf0'], tr: ['wipe', 'zoom'],
    caps: [['准备好了吗？', 'Ready?'], ['快乐出发', 'Let’s go, happily'], ['今天的视频，开始！', 'Today’s video starts now!']], port: { box: [200, 120, 1520, 760] },
    scenes: [
      [c => ({ sw: M.path(c, 0, 0, 1920, 1080, 'M200 600 C 600 300, 1100 760, 1720 420', '#ffd23f', 90, 'stroke-linecap="round"'), sp: [spark(c, 300, 200, '#ff9f1c'), spark(c, 1520, 680, '#ff4f4f')], q: X(c, 700, 380, 140, '#222', '准备好了吗？', 900) }),
       (s, t, a) => { M.draw(s.sw, t, a + .1, 1, 99); s.sp.forEach((e, i) => { M.pop(e, t, a + .6 + i * .3, 99, { from: 0 }); e.style.transform += ` rotate(${(t * 90).toFixed(0)}deg)`; }); M.pop(s.q, t, a + 1, 99, { from: .3 }); }],
      [c => ({ sw: M.path(c, 0, 0, 1920, 1080, 'M300 640 C 700 420, 1100 760, 1600 520', '#ffd23f', 110, 'stroke-linecap="round"'), w: word(c, '快乐出发', 360), sp: [spark(c, 240, 180, '#ff9f1c'), spark(c, 1600, 160, '#3fbf5f'), spark(c, 1500, 760, '#a259ff')] }),
       (s, t, a) => { M.draw(s.sw, t, a - .2, .8, 99); bounce(s.w, t, a + .2); s.sp.forEach((e, i) => { M.pop(e, t, a + .9 + i * .2, 99, { from: 0 }); e.style.transform += ` rotate(${(t * 90).toFixed(0)}deg)`; }); }],
      [c => ({ w: word(c, '开始！', 340), lp: M.path(c, 0, 0, 1920, 1080, 'M380 700 C 700 760, 1200 760, 1300 700 C 1400 640, 1300 600, 1240 660 C 1180 720, 1400 800, 1560 740', '#2f8fff', 14) }),
       (s, t, a) => { bounce(s.w, t, a); M.draw(s.lp, t, a + .7, .9, 99); }]
    ] });
})();
