/* T192 桌面口播 Desktop Talk: a generic desktop (no real OS), window as a video-call app, sticky notes, toasts. */
(function () { const M = K.T.mo, X = M.X, INK = '#1d1d28';
  const desk = c => M.box(c, -400, -400, { width: '2720px', height: '1880px', background: 'linear-gradient(135deg,#a3b8ff,#c6a7ff 55%,#ffb3d9)' });
  const bar = c => { const b = M.box(c, 0, 0, { width: '1920px', height: '44px', background: 'rgba(255,255,255,.55)', backdropFilter: 'blur(10px)', font: M.f(700, 24, M.INTER), color: INK, paddingLeft: '30px', boxSizing: 'border-box', display: 'flex', alignItems: 'center' }, '◆  File   Edit   View'); return b; };
  const frame = (c, x, y, w, h, title) => { const f = M.box(c, x, y - 44, { width: w + 'px', height: (h + 44) + 'px', borderRadius: '18px', background: '#f6f6f8', boxShadow: '0 30px 60px rgba(40,20,80,.25)' }); X(f, 20, 8, 24, '#666', '● ● ●  ' + title, 700, M.INTER); return f; };
  const sticky = (c, x, y, txt, r) => M.box(c, x, y, { width: '300px', padding: '26px', background: '#fff59d', boxShadow: '0 12px 20px rgba(0,0,0,.15)', font: M.f(900, 40, M.CN), color: INK, lineHeight: 1.4, transform: `rotate(${r}deg)`, transformOrigin: '50% 0' }, txt);
  const toast = (c, y, txt) => M.box(c, 1380, y, { width: '460px', padding: '24px 30px', borderRadius: '18px', background: '#fff', boxShadow: '0 14px 30px rgba(0,0,0,.15)', font: M.f(700, 34, M.CN), color: INK }, txt);
  M.story({ bg: '#b7a8ff', sbg: ['transparent', 'transparent', 'transparent'], tr: ['slide', 'zoom'], ring: () => ({ color: '#ffffff', width: 0, shadow: .3 }),
    wins: [M.q(300, 200, 900, 600, 14, 1.02), M.q(200, 240, 720, 480, 14, 1.02), M.q(420, 200, 1080, 640, 14, 1.02)],
    caps: [['开个会，先讲两件事', 'Quick call — two things'], ['选题，和剪辑', 'Topics, and editing'], ['讲完，已保存', 'Done — saved']], port: { box: [100, 40, 1720, 900] },
    scenes: [
      [c => ({ d: desk(c), b: bar(c), f: frame(c, 300, 200, 900, 600, 'Video Call'), st: sticky(c, 1300, 220, '今天要讲：<br>① 选题<br>② 剪辑', 4) }),
       (s, t, a) => { M.rise(s.b, t, a, 99, { dy: -40 }); M.pop(s.f, t, a + .1, 99, { from: .9 }); M.pop(s.st, t, a + .8, 99, { from: 1.4, base: 'rotate(4deg)' }); s.st.style.transform += ` rotate(${(1.5 * Math.sin(t * 2)).toFixed(1)}deg)`; }],
      [c => ({ d: desk(c), b: bar(c), f: frame(c, 200, 240, 720, 480, 'Video Call'), n: [['① 选题', '#fff59d', 1040, 200, -3], ['② 剪辑', '#b9f6ca', 1360, 420, 5]].map(([tx, col, x, y, r]) => { const e = sticky(c, x, y, tx, r); e.style.background = col; e.r = r; return e; }) }),
       (s, t, a) => { s.b.style.opacity = 1; s.f.style.opacity = 1; s.n.forEach((e, i) => M.pop(e, t, a + .1 + i * .4, 99, { from: 1.4, base: `rotate(${e.r}deg)` })); }],
      [c => ({ d: desk(c), b: bar(c), f: frame(c, 420, 200, 1080, 640, 'Video Call'), t1: toast(c, 700, '✓ 已保存 Saved'), t2: toast(c, 840, '↗ 已分享给团队') }),
       (s, t, a) => { s.b.style.opacity = 1; s.f.style.opacity = 1; M.slide(s.t1, t, a + .6, 99, { dx: 500 }); M.slide(s.t2, t, a + 1.1, 99, { dx: 500 }); }]
    ] });
})();
