/* T67 Documentary 纪录片 · 10 s sample (illustrative copy). Letterbox, film grain, serif chapter cards crossfading, slow push. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, GOLD = '#c9a96e', INK = '#efe9dc';
  const CH = [['Chapter One', '起点', 'The beginning', .8, 3.45], ['Chapter Two', '转折', 'The turn', 3.6, 6.65], ['Chapter Three', '现在', 'Now', 6.8, 9.2]];
  M.setup({ bg: '#0b0b0b', win: { x: 960, y: 150, w: 840, h: 560, r: 6, o: 1, s: 1.1 }, ring: () => ({ color: '#000', width: 0, shadow: .6 }), port: { box: [90, 60, 860, 700] },
    captions: M.caps([['每个人都有一个起点', 'Everyone starts somewhere'], ['转折，往往来得很安静', 'Turning points arrive quietly'], ['而现在，故事继续', 'And now, the story goes on']]),
    build(L) { const s = {};
      s.grain = M.bg(M.box(L, -40, -40, { width: '2000px', height: '1160px', backgroundImage: 'radial-gradient(rgba(255,255,255,.05) 1px, transparent 1.4px), radial-gradient(rgba(255,255,255,.035) 1px, transparent 1.4px)', backgroundSize: '6px 6px, 9px 9px', backgroundPosition: '0 0, 3px 4px' }));
      s.bars = [M.bg(M.box(L, 0, 0, { width: '1920px', height: '90px', background: '#000' }))];
      s.ch = CH.map(([k, cn, en]) => { const g = M.box(L, 110, 230, {}); M.txt(g, 0, 0, f('italic 700', 40, M.PF), GOLD, k, { letterSpacing: '.06em' }); g.cn = M.txt(g, 0, 70, f(900, 140, M.SERIF), INK, cn, { lineHeight: 1 }); M.txt(g, 4, 240, f(700, 28, M.INTER), '#8d877b', en.toUpperCase(), { letterSpacing: '.3em' }); return g; });
      s.rule = M.path(L, 110, 210, 300, 10, 'M2 5H290', GOLD, 2);
      s.tc = M.txt(L, 110, 120, f(700, 22, M.MONO), '#6f6a60', 'A SHORT DOCUMENTARY · 纪录短片');
      return s; },
    update(s, t) { s.grain.style.transform = `translate(${((t * 37) % 9).toFixed(0)}px, ${((t * 53) % 7).toFixed(0)}px)`; M.rise(s.tc, t, .7, 9.2, { dy: 8 }); M.draw(s.rule, t, .9, .8, 9.2);
      s.ch.forEach((g, i) => { const [, , , a, b] = CH[i], v = M.env(t, a, b, .7, .45); g.style.opacity = v.a.toFixed(3); g.style.transform = `translateY(${(14 * (1 - M.o3((t - a) / .7))).toFixed(1)}px)`; g.cn.style.filter = `blur(${((1 - M.o3((t - a) / .8)) * 8).toFixed(2)}px)`; }); } });
})();
