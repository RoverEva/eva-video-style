/* T198 擦除转场包 Wipe Pack: four wipe styles played OVER the window — vertical bars, horizontal bars, paper strips, ink strips. */
(function () { const M = K.T.mo, X = M.X, A = M.TB.map(b => b[0]), P = EV.portrait, LX = P ? 700 : 80, GX = P ? 700 : 1240, GY = P ? 130 : 200, GS = P ? 96 : 150, GF = P ? 40 : 52;
  const bars = (c, n, vert, col, alt) => Array.from({ length: n }, (_, i) => M.box(c, vert ? i * 1920 / n : 0, vert ? 0 : i * 1080 / n, { width: vert ? (1920 / n + 1) + 'px' : '1920px', height: vert ? '1080px' : (1080 / n + 1) + 'px', background: alt && i % 2 ? alt : col, transformOrigin: vert ? '50% 0' : '0 50%', transform: 'scale(0)' }));
  const run = (L, t, a, vert, inv) => L.forEach((e, i) => { const k = inv ? L.length - 1 - i : i, u = M.io((t - a - k * .04) / .4), v = u < 1 ? u : Math.max(0, 1 - M.io((t - a - .75 - k * .04) / .4)); e.style.transform = vert ? `scaleY(${v.toFixed(3)})` : `scaleX(${v.toFixed(3)})`; });
  const lab = (c, txt, bg, fg) => M.box(c, LX, P ? 200 : 80, { padding: '12px 30px', background: bg, color: fg, font: M.f(900, 52, M.CN), boxShadow: '0 8px 20px rgba(0,0,0,.3)' }, txt);
  const W = [['竖条合拢', '#ffffff', '#111', 8, 1, '#111'], ['横条下压', '#ffd23f', '#111', 8, 0, null], ['纸色竖条', '#e8dfcc', '#111', 10, 1, null], ['墨色竖条', '#1a1a1a', '#fff', 10, 1, null]];
  const T0 = [A[0] + .3, A[0] + 1.6, A[1] + .2, A[1] + 1.6];
  M.story({ bg: '#111', sbg: ['#f4f1ea', '#f4f1ea', '#f4f1ea'], tr: ['push', 'push'], ring: () => ({ color: '#ffffff', width: 0, shadow: .3 }),
    wins: [M.q(0, 0, 1920, 1080, 0, 1), M.q(0, 0, 1920, 1080, 0, 1), M.q(0, 0, 1920, 1080, 0, 1)],
    caps: [['四种擦除转场，一次看完', 'Four wipe transitions in one go'], ['纸色竖条，墨色竖条', 'Paper strips, ink strips'], ['选一个，放进你的视频', 'Pick one for your video']], port: { box: [0, 0, 1920, 1080] }, overCover: true,
    over: [L => ({ w: W.map(([n, bg, fg, k, vert, alt]) => ({ b: bars(L, k, vert, bg, alt), l: lab(L, n, bg, fg), vert })), g: W.map(([n, bg, fg], i) => M.box(L, GX, GY + i * GS, { padding: P ? '12px 26px' : '20px 36px', background: bg, color: fg, font: M.f(900, GF, M.CN), boxShadow: '0 10px 20px rgba(0,0,0,.3)' }, n)) }),
      (s, t) => { s.w.forEach((w, i) => { run(w.b, t, T0[i], w.vert, i % 2); w.l.style.opacity = t > T0[i] && t < (T0[i + 1] || A[2]) - .05 ? 1 : 0; }); s.g.forEach((e, i) => M.slide(e, t, A[2] + .1 + i * .18, 9.3, { dx: 300 })); }],
    scenes: [[c => ({}), () => {}], [c => ({}), () => {}], [c => ({}), () => {}]]
  });
})();
