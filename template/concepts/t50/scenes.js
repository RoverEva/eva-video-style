/* T50 Brutalist 粗野大字 · 10 s sample (illustrative copy). Huge type slams, thick borders, marquee band. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, INK = '#0a0a0a', Y = '#f9ff00';
  M.setup({ bg: '#efefef', win: { x: 1240, y: 130, w: 560, h: 620, r: 8, o: 1, s: 1.15 }, ring: () => ({ color: INK, width: 12, shadow: 0 }), port: { box: [70, 40, 1110, 790] },
    captions: M.caps([['别再拖了', 'Stop putting it off'], ['今天，就发第一条', 'Post your first one today'], ['完成比完美重要', 'Done beats perfect']]),
    build(L) { const s = {};
      s.stop = M.txt(L, 80, 20, f(400, 300, M.AN), INK, 'STOP.', { lineHeight: 1, transformOrigin: '0 100%' });
      s.bar = M.txt(L, 80, 340, f(900, 84, M.CN), '#fff', '别再拖了', { background: INK, padding: '6px 30px' });
      s.bx = ['今天', '第一条', '发出去'].map((w, i) => M.txt(L, 80 + i * 360, 500, f(900, 70, M.CN), INK, w, { border: `10px solid ${INK}`, padding: '10px 26px', background: i === 2 ? Y : '#fff' }));
      s.mq = M.box(L, 0, 690, { width: '1220px', height: '110px', background: INK, overflow: 'hidden' });
      s.mt = el(s.mq, 'div', 'abs', { left: 0, top: '14px', whiteSpace: 'nowrap', font: f(400, 72, M.AN), color: Y, letterSpacing: '.04em' }, Array(8).fill('DONE > PERFECT · 完成 > 完美 · ').join(''));
      return s; },
    update(s, t) { M.pop(s.stop, t, .8, 9.2, { from: 1.5, din: .25 }); M.panel(s.bar, t, 1.4, 9.2, { din: .3 });
      s.bx.forEach((e, i) => M.slide(e, t, 3.6 + i * .12, 9.2, { dx: 0, dy: -80, din: .25 }));
      M.panel(s.mq, t, 6.75, 9.2, { din: .35 }); s.mt.style.transform = `translateX(${(-(t - 6.75) * 260).toFixed(1)}px)`; } });
})();
