/* T165 破框而出 Frame Break: a yellow frame holds the window, then the window bursts out past it. */
(function () { const M = K.T.mo, X = M.X, Y = '#ffd23f';
  const shards = c => Array.from({ length: 10 }, (_, i) => M.svg(c, 0, 0, 40, 40, `<path d="M0 0 L40 14 L10 40Z" fill="${Y}"/>`, { transformOrigin: '50% 50%' }));
  M.story({ bg: '#121212', sbg: ['#121212', '#121212', '#ffd23f'], tr: ['push', 'zoom'], ring: () => ({ color: '#ffffff', width: 0, shadow: .5 }),
    wins: [M.q(380, 220, 440, 560, 18, 1.05), M.q(240, 80, 640, 860, 18, 1.05), M.c(1360, 160, 420)],
    caps: [['框，是给别人看的', 'Frames are for others to see'], ['打破画框，跳出来说', 'Break the frame, speak up'], ['这才是你的样子', 'This is the real you']], port: { box: [60, 40, 1800, 960] },
    scenes: [
      [c => ({ fr: M.box(c, 350, 190, { width: '500px', height: '620px', border: `10px solid ${Y}`, boxSizing: 'border-box' }), t: X(c, 1000, 380, 90, '#fff', '框', 900), t2: X(c, 1000, 520, 44, '#aaa', '给别人看的', 700) }),
       (s, t, a) => { M.pop(s.fr, t, a + .1, 99, { from: 1.2 }); M.hero(s.t, t, a + .4, 99); M.rise(s.t2, t, a + .7, 99); }],
      [c => ({ fr: M.box(c, 350, 190, { width: '500px', height: '620px', border: `10px solid ${Y}`, boxSizing: 'border-box' }), sh: shards(c), t: X(c, 960, 520, 150, Y, 'BREAK OUT', 400, M.AN), t2: X(c, 966, 720, 56, '#fff', '打破画框，跳出来说', 900) }),
       (s, t, a) => { s.fr.style.opacity = 1; s.sh.forEach((e, i) => { const u = M.o3((t - a - .1) / 1.2), ang = -1.2 + i * .25; e.style.opacity = t > a ? 1 - u * .6 : 0; e.style.transform = `translate(${(800 + Math.cos(ang) * 600 * u).toFixed(1)}px, ${(220 + Math.sin(ang) * 400 * u).toFixed(1)}px) rotate(${(u * 400 + i * 40).toFixed(0)}deg)`; }); M.hero(s.t, t, a + .2, 99, { dx: -120 }); M.rise(s.t2, t, a + .6, 99); }],
      [c => ({ t: X(c, 160, 360, 140, '#121212', '这才是', 900), t2: X(c, 160, 540, 140, '#121212', '你的样子', 900) }), (s, t, a) => { M.hero(s.t, t, a, 99); M.hero(s.t2, t, a + .3, 99); }]
    ] });
})();
