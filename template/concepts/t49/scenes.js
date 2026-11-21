/* T49 Y2K Chrome 千禧金属 · 10 s sample (illustrative copy). Chrome bubble type, twinkling four-point stars, glossy pills. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#2b1d5c';
  const star = (p, x, y, sz, c) => M.svg(p, x, y, sz, sz, `<path d="M${sz / 2} 0 C ${sz * .56} ${sz * .44}, ${sz * .56} ${sz * .44}, ${sz} ${sz / 2} C ${sz * .56} ${sz * .56}, ${sz * .56} ${sz * .56}, ${sz / 2} ${sz} C ${sz * .44} ${sz * .56}, ${sz * .44} ${sz * .56}, 0 ${sz / 2} C ${sz * .44} ${sz * .44}, ${sz * .44} ${sz * .44}, ${sz / 2} 0Z" fill="${c}"/>`, { transformOrigin: '50% 50%' });
  M.setup({ bg: 'linear-gradient(135deg,#cfe8ff 0%,#efd9ff 50%,#ffe0f0 100%)', win: { x: 1240, y: 150, w: 520, h: 520, r: 260, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, glow: 'rgba(185,140,255,.8)', shadow: .3 }), port: { box: [90, 60, 1040, 740] },
    captions: M.caps([['千禧风回来了', 'Y2K is back'], ['越亮晶晶越可爱', 'The shinier the better'], ['你喜欢吗？', 'Into it?']]),
    build(L) { const s = {};
      s.t = M.txt(L, 96, 40, f(400, 300, M.AN), 'transparent', 'Y2K', { backgroundImage: 'linear-gradient(180deg,#ffffff 0%,#c9d3e6 30%,#6e7b99 52%,#f4f7ff 60%,#9aa6c4 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextStroke: '3px #fff', filter: 'drop-shadow(0 10px 18px rgba(80,60,160,.35))', lineHeight: 1 });
      s.cn = M.txt(L, 110, 370, f(900, 80, M.CN), INK, '千禧风，闪亮登场');
      s.stars = [[620, 80, 90, '#fff'], [880, 260, 60, '#ffd6f5'], [560, 330, 46, '#fff'], [1120, 90, 70, '#e6dcff'], [980, 560, 54, '#fff']].map(a => star(L, ...a));
      s.pills = ['glossy 光泽', 'bubble 泡泡', 'sparkle 闪闪'].map((p, i) => M.txt(L, 110 + i * 300, 500, f(800, 34, M.CN), INK, p, { padding: '14px 30px', borderRadius: '999px', background: 'linear-gradient(180deg,#ffffff,#d9c8ff)', boxShadow: 'inset 0 -6px 12px rgba(120,80,220,.25), 0 8px 18px rgba(80,60,160,.2)', transformOrigin: '50% 50%' }));
      s.q = M.txt(L, 110, 640, f(900, 84, M.CN), '#ff4fa3', '你喜欢吗？ ♡', { textShadow: '0 4px 0 #fff' });
      return s; },
    update(s, t) { M.pop(s.t, t, .8, 9.2, { from: .5, din: .4 }); M.hero(s.cn, t, 1.3, 9.2);
      s.stars.forEach((e, i) => { const a = M.env(t, 1.0 + i * .2, 9.2).a, k = .6 + .4 * Math.abs(Math.sin(t * 2.4 + i * 1.3)); e.style.opacity = a; e.style.transform = `scale(${(k * M.os((t - 1 - i * .2) / .4)).toFixed(3)}) rotate(${(t * 30 + i * 20).toFixed(1)}deg)`; });
      s.pills.forEach((e, i) => M.pop(e, t, 3.6 + i * .14, 9.2, { from: .3 })); M.pop(s.q, t, 6.85, 9.2, { from: .5 }); } });
})();
