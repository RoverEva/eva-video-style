/* T15 LEARN · 学习风 Learning Style — demo (16 s). Flat storybook shapes are drawn in code; stars twinkle and clouds drift in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, Lr = T.LRN;
  C.src0 = 40; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const LOW = { x: 120, y: 740, w: 230, h: 230, r: 115, s: 3 }, TOPR = { x: 1700, y: 40, w: 180, h: 180, r: 90, s: 3 }, SUN = { x: 820, y: 330, w: 280, h: 280, r: 140, s: 2.8 }, CARD = { x: 230, y: 230, w: 560, h: 620, r: 40, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, LOW, { o: 0 }) }, { t: 1.0, d: .4, L: LOW }, { t: 4.0, d: .45, L: TOPR }, { t: 8.5, d: .5, L: SUN }, { t: 12.5, d: .5, L: CARD }];
  C.ringFn = () => ({ color: '#fff', width: 10, shadow: .35 });

  // L1 · title + book staircase + paper plane to the sun
  C.scene({ t0: 0, t1: 4.03, bg: T.learnBg, quiet: true, build(L) {
      const st = {}; st.sky = T.sky(L, 14, 5); st.a = T.bubbly(L, 'A World', 110, 220, 170); st.b = T.bubbly(L, 'of Words', 110, 410, 170);
      st.c = T.bubbly(L, '每一页，都有新发现', 116, 640, 52, { font: Lr.CN });
      st.bs = T.stairs(L, 980, 870); st.sun = T.sun(L, 1720, 220, 95);
      st.p = T.plane(L, [[1000, 740], [1100, 560], [1240, 360], [1420, 250]], 100);
      [0, 1, 2, 3, 4].forEach(i => k.sfx('pop', .6 + i * .22, .1, { f: 700 + i * 120 })); k.sfx('whoosh', 2.0, .1); k.sfx('ding', 3.0, .08); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.a, slide(lt, .1, .5, 0, 60)); tf(st.b, slide(lt, .3, .5, 0, 60)); tf(st.c, { o: P(lt, .9, .4) });
      T.stairsAt(st.bs, t, .6, .22); T.sunAt(st.sun, t, P(lt, 1.6, .5)); T.planeAt(st.p, ease.io3(P(lt, 2.0, 1.4))); } });

  // L2 · Small Steps, Big Ideas: Read → Think → Create
  C.scene({ t0: 4.0, t1: 8.53, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 12, 9, [[300, 30, .8], [1420, 30, .8], [-20, 300, .7]]);
      st.h = T.bubbly(L, 'Small Steps, Big Ideas', 960, 70, 120, { anchor: 'middle' });
      st.it = [['openbook', 420, Lr.CLOUD, 'Read · 读'], ['bulb', 960, '#b0389a', 'Think · 想'], ['pencil', 1500, Lr.CLOUD, 'Create · 做']].map(([ic, x, bc, lab], i) => ({ b: T.blob(L, x, 560, 230, bc, 4 + i), i: T.lIcon(L, ic, x, 560, 200), l: T.bubbly(L, lab, x, 820, 72, { anchor: 'middle', font: Lr.CN }) }));
      st.r = T.rays(L, 960, 540, 260, 7, -170, -10);
      st.d1 = T.dashArc(L, 640, 420, 770, 420, 90); st.d2 = T.dashArc(L, 1160, 420, 1290, 440, 90);
      [0, 1, 2].forEach(i => k.sfx('pop', 4.8 + i * .7, .12, { f: 800 + i * 160 })); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.h, pop(lt, .1, .45, 1.6));
      st.it.forEach((o, i) => { const t0 = 4.8 + i * .7; tf(o.b, pop(t, t0, .4, 1.5)); const p = pop(t, t0 + .1, .45, 2); tf(o.i, { s: p.s, o: p.o, r: Math.sin(t * 2 + i) * 4 }); tf(o.l, { o: P(t, t0 + .3, .3) }); });
      tf(st.r, { o: P(t, 5.7, .2) * (.6 + .4 * Math.sin(t * 6)) }); T.dashArcAt(st.d1, P(t, 5.2, .4)); T.dashArcAt(st.d2, P(t, 5.9, .4)); } });

  // L3 · Let Ideas Take Flight: open book sunrise, planes fly out (Eva in the sunrise)
  C.scene({ t0: 8.5, t1: 12.53, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 16, 13, [[380, 60, .9], [1500, 120, .8], [-30, 620, .9], [1640, 600, .9]]);
      st.h = T.bubbly(L, 'Let Ideas Take Flight', 960, 60, 116, { anchor: 'middle' }); st.s = T.bubbly(L, '读 · 想 · 做', 960, 230, 56, { anchor: 'middle', font: Lr.CN });
      st.bk = T.bigBook(L, 960, 870, 1000); st.b1 = T.book(L, 160, 820, 300, 90, Lr.PURPLE); st.b2 = T.book(L, 180, 730, 280, 90, Lr.ORANGE); st.b3 = T.book(L, 1420, 830, 320, 90, Lr.GREEN);
      st.pl = [T.plane(L, [[820, 640], [600, 520], [430, 420], [230, 360]], 90), T.plane(L, [[1100, 640], [1300, 520], [1480, 420], [1690, 360]], 90)];
      k.sfx('riser', 8.6, .08, { d: .8 }); k.sfx('whoosh', 9.6, .1); k.sfx('whoosh', 9.9, .1); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.h, pop(lt, .05, .45, 1.6)); tf(st.s, { o: P(lt, .5, .4) }); T.bigBookAt(st.bk, t, P(lt, 0, .8));
      [st.b1, st.b2, st.b3].forEach((b, i) => tf(b, { y: 80 * (1 - ease.outBack(P(lt, .3 + i * .15, .45), 1.5)), o: P(lt, .3 + i * .15, .1) })); st.pl.forEach((p, i) => T.planeAt(p, ease.io3(P(lt, 1.1 + i * .3, 1.6)))); } });

  // L4 · content page with corner decorations (Eva card + today's goals)
  C.scene({ t0: 12.5, t1: C.end + .05, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 6, 21, [[20, 30, .7], [40, 900, .6]]);
      st.c1 = T.lIcon(L, 'pencil', 1740, 920, 140); st.c2 = T.book(L, 60, 930, 240, 70, Lr.RED); st.c3 = T.book(L, 80, 870, 220, 66, Lr.CLOUD); st.c4 = T.lIcon(L, 'bulb', 190, 790, 70);
      st.h = T.bubbly(L, "Today's Goal · 今日小目标", 900, 220, 72, { font: Lr.CN });
      st.g = [T.goal(L, '① 读一页故事', 920, 400, Lr.STAR, -2), T.goal(L, '② 记住 5 个新词', 920, 530, Lr.GREEN, 1.5), T.goal(L, '③ 用新词写一句话', 920, 660, '#ff8fb8', -1.5)];
      st.g.forEach((_, i) => k.sfx('pop', 13.4 + i * .5, .1, { f: 900 + i * 120 })); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); [st.c1, st.c2, st.c3, st.c4].forEach((e, i) => tf(e, pop(lt, .1 + i * .1, .4, 1.6))); tf(st.h, { o: P(lt, .4, .4) });
      st.g.forEach((g, i) => { const p = pop(t, 13.4 + i * .5, .4, 1.8); tf(g, { s: p.s, o: p.o, r: [-2, 1.5, -1.5][i] }); }); } });
})();
