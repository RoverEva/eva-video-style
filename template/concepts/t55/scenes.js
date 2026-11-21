/* T55 Origami 折纸 · 10 s sample (illustrative copy). Paper panels unfold on hinges; a folded crane lands. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#1d2b33';
  const fold = (e, t, t0, t1, ax) => { const v = M.env(t, t0, t1, .5), u = M.os((t - t0) / .5); e.style.opacity = (clamp01((t - t0) / .12) * (1 - v.x)).toFixed(3);
    e.style.transform = `perspective(1400px) ${ax}(${(-90 * (1 - u) + 20 * v.x).toFixed(2)}deg)`; e.style.filter = `brightness(${(.75 + .25 * Math.min(1, u)).toFixed(3)})`; };
  const clamp01 = x => Math.max(0, Math.min(1, x));
  M.setup({ bg: '#e7eef0', win: { x: 1250, y: 150, w: 520, h: 600, r: 20, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }), port: { box: [90, 60, 1060, 740] },
    captions: M.caps([['把复杂的事，折简单', 'Fold the complex into simple'], ['问题、方法、结果', 'Problem, method, result'], ['三折，讲完一件事', 'One story, three folds']]),
    build(L) { const s = {};
      s.p1 = M.box(L, 110, 90, { width: '980px', height: '230px', background: 'linear-gradient(135deg,#2a9d8f 50%,#258b7f 50%)', transformOrigin: '0 0', padding: '40px 50px', boxSizing: 'border-box' });
      M.txt(s.p1, 50, 40, f(900, 88, M.CN), '#fff', '折一折，就清楚了'); M.txt(s.p1, 54, 158, f(700, 32, M.INTER), '#d8f3ef', 'Fold it, and it’s clear');
      s.ps = [['问题', 'Problem', '#e76f51'], ['方法', 'Method', '#f4a261'], ['结果', 'Result', '#264653']].map(([c, e, col], i) => { const p = M.box(L, 110 + i * 335, 380, { width: '310px', height: '260px', background: `linear-gradient(160deg, ${col} 55%, rgba(0,0,0,.12) 55%), ${col}`, transformOrigin: '0 50%', padding: '34px 30px', boxSizing: 'border-box' });
        M.txt(p, 30, 30, f(700, 30, M.MONO), 'rgba(255,255,255,.75)', '0' + (i + 1)); M.txt(p, 30, 80, f(900, 70, M.CN), '#fff', c); M.txt(p, 32, 170, f(700, 30, M.INTER), 'rgba(255,255,255,.85)', e); return p; });
      s.crane = M.svg(L, 820, 650, 220, 150, `<path d="M10 120 L110 60 L80 130Z" fill="#e76f51"/><path d="M110 60 L210 20 L150 110Z" fill="#f4a261"/><path d="M110 60 L80 130 L150 110Z" fill="#c4553d"/><path d="M110 60 L60 10 L95 70Z" fill="#2a9d8f"/>`, { transformOrigin: '50% 50%' });
      s.t3 = M.txt(L, 110, 690, f(900, 58, M.CN), INK, '三折，讲完一件事');
      return s; },
    update(s, t) { fold(s.p1, t, .85, 9.2, 'rotateX'); s.ps.forEach((p, i) => fold(p, t, 3.6 + i * .25, 9.2, 'rotateY'));
      M.pop(s.crane, t, 6.9, 9.2, { from: .3 }); s.crane.style.transform += ` translateY(${(-8 * Math.sin(t * 3)).toFixed(1)}px)`; M.hero(s.t3, t, 7.05, 9.2); } });
})();
