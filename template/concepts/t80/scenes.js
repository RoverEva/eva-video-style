/* T80 Isometric Town 等距小城 · 10 s sample (illustrative copy). Iso blocks rise from the ground, roads draw, flags pop. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#22324a';
  const iso = (p, cx, cy, w, h, col) => { const a = w * .866, b = w * .5; return M.svg(p, cx - a, cy - h - b, 2 * a, h + 2 * b, `<path d="M${a} 0 L${2 * a} ${b} L${a} ${2 * b} L0 ${b}Z" fill="${col[0]}"/><path d="M0 ${b} L${a} ${2 * b} L${a} ${2 * b + h} L0 ${b + h}Z" fill="${col[1]}"/><path d="M${2 * a} ${b} L${a} ${2 * b} L${a} ${2 * b + h} L${2 * a} ${b + h}Z" fill="${col[2]}"/>`, { transformOrigin: '50% 100%' }); };
  const B = [[300, 520, 90, 160, ['#ffd166', '#f4a62a', '#d98a14'], '工作室', 1.0], [560, 470, 80, 190, ['#7ad3ff', '#3aa7e0', '#2386bd'], '剪辑室', 1.3], [820, 540, 100, 120, ['#ff8fa3', '#e5677e', '#c84b62'], '发布中心', 1.6]];
  M.setup({ bg: 'linear-gradient(180deg,#e6f3ff,#cfe6f7)', win: { x: 1290, y: 150, w: 470, h: 470, r: 235, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['欢迎来到我的内容小镇', 'Welcome to my content town'], ['拍摄、剪辑、发布，一条路连起来', 'Shoot, edit, post — one road'], ['小镇每天都在长大', 'The town grows every day']]),
    build(L) { const s = {};
      s.ground = M.svg(L, 110, 360, 1000, 420, `<path d="M500 0 L1000 210 L500 420 L0 210Z" fill="#bfe3a8"/><path d="M500 0 L1000 210 L500 420 L0 210Z" fill="none" stroke="#a3cf8a" stroke-width="4"/>`, { transformOrigin: '50% 50%' });
      s.road = M.path(L, 110, 360, 1000, 420, 'M190 250 L450 140 L720 260', '#8a96a8', 16);
      s.bl = B.map(([x, y, w, h, col, nm]) => { const b = iso(L, x, y, w, h, col); b.lb = M.txt(L, x + w * .9 + 8, y - h - 10, f(900, 36, M.CN), INK, nm, { background: '#fff', padding: '4px 14px', borderRadius: '10px', boxShadow: '0 6px 14px rgba(0,0,0,.1)', zIndex: 5 }); return b; });
      s.t = M.txt(L, 110, 70, f(900, 72, M.CN), INK, '我的内容小镇'); s.e = M.txt(L, 114, 165, f(700, 28, M.INTER), '#5a6d86', 'MY CONTENT TOWN');
      s.flags = B.map(([x, y, w, h]) => M.svg(L, x - 6, y - h - w * .5 - 70, 70, 70, `<path d="M6 66 V6" stroke="${INK}" stroke-width="4"/><path d="M8 6 L60 18 L8 32Z" fill="#ff5a3c"/>`, { transformOrigin: '0 100%' }));
      return s; },
    update(s, t) { M.pop(s.ground, t, .7, 9.2, { from: .7 }); M.hero(s.t, t, .9, 9.2); M.rise(s.e, t, 1.2, 9.2);
      s.bl.forEach((b, i) => { const a = B[i][6], v = M.env(t, a, 9.2, .45), u = M.os((t - a) / .45); b.style.opacity = v.a; b.style.transform = `scaleY(${Math.max(0, u).toFixed(3)})`; M.rise(b.lb, t, a + 2.6 + i * .2, 9.2, { dy: 16 }); });
      M.draw(s.road, t, 3.6, 1.0, 9.2); s.flags.forEach((e, i) => { M.pop(e, t, 6.85 + i * .15, 9.2, { from: 0 }); e.style.transform += ` skewY(${(4 * Math.sin(t * 6 + i)).toFixed(1)}deg)`; }); } });
})();
