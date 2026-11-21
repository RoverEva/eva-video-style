/* T56 Soft Clay 黏土软萌 · 10 s sample (illustrative copy). Soft 3D blobs squash-and-stretch in; clay pills; a bouncy +1. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#4a2f2a';
  const clay = (p, x, y, w, h, c, br) => M.box(p, x, y, { width: w + 'px', height: h + 'px', borderRadius: br || '50%', background: `radial-gradient(circle at 32% 28%, #ffffffaa 0 8%, ${c} 30%, ${c} 62%, rgba(0,0,0,.18) 100%)`, boxShadow: `0 18px 28px rgba(120,60,30,.22), inset -10px -14px 22px rgba(0,0,0,.12)`, transformOrigin: '50% 100%' });
  const squash = (e, t, t0, t1, base) => { const v = M.env(t, t0, t1, .35), d = t - t0, k = d > 0 ? Math.exp(-d * 5) * Math.sin(d * 18) : 0; e.style.opacity = v.a; e.style.transform = `${base || ''} translateY(${(-120 * (1 - Math.min(1, M.o3(d / .3)))).toFixed(1)}px) scale(${(1 + .22 * k).toFixed(3)}, ${(1 - .22 * k).toFixed(3)})`; };
  M.setup({ bg: '#ffe9d6', win: { x: 1250, y: 150, w: 520, h: 520, r: 260, o: 1, s: 1.15 }, ring: () => ({ color: '#fff7ef', width: 16, shadow: .25 }), port: { box: [90, 40, 1060, 780] },
    captions: M.caps([['每天进步一点点', 'A little better every day'], ['早起、运动、阅读', 'Rise early, move, read'], ['今天也 +1', 'Plus one today too']]),
    build(L) { const s = {};
      s.b = [[90, 40, 150, '#ff9aa2'], [980, 80, 110, '#a0e7e5'], [1080, 760, 90, '#ffd36e']].map(([x, y, d, c]) => M.bg(clay(L, x, y, d, d, c)));
      s.t = M.txt(L, 110, 210, f(900, 100, M.CN), INK, '每天进步一点点', { textShadow: '0 6px 0 #ffd2b5' });
      s.p = [['早起', 'Early', '#ffb4a2'], ['运动', 'Move', '#9bf6ff'], ['阅读', 'Read', '#cdb4db']].map(([c, e, col], i) => { const g = clay(L, 110 + i * 320, 400, 290, 150, col, '75px'); M.txt(g, 0, 26, f(900, 58, M.CN), INK, c, { width: '290px', textAlign: 'center' }); M.txt(g, 0, 98, f(700, 24, M.INTER), INK, e, { width: '290px', textAlign: 'center' }); return g; });
      s.one = clay(L, 420, 600, 300, 190, '#ff7aa2', '95px'); M.txt(s.one, 0, 30, f(400, 120, M.AN), '#fff', '+1', { width: '300px', textAlign: 'center' });
      return s; },
    update(s, t) { s.b.forEach((e, i) => squash(e, t, .6 + i * .15, 9.25)); squash(s.t, t, .95, 9.2);
      s.p.forEach((e, i) => squash(e, t, 3.6 + i * .18, 9.2)); squash(s.one, t, 6.85, 9.2); } });
})();
