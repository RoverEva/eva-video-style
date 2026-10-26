/* T15 Learning Style — demo on the shared 15 s intro. Flat storybook shapes are drawn in code; stars twinkle and clouds drift in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, Lr = T.LRN, I = IN; I.setup(C);
  const LOW = { x: 1560, y: 120, w: 260, h: 260, r: 130, s: 3 }, TOPR = { x: 1700, y: 40, w: 180, h: 180, r: 90, s: 3 }, SUN = { x: 820, y: 330, w: 280, h: 280, r: 140, s: 2.8 }, CARD = { x: 230, y: 230, w: 560, h: 620, r: 40, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, LOW, { o: 0 }) }, { t: .1, d: .4, L: LOW }, { t: 3.87, d: .45, L: TOPR }, { t: 7.73, d: .5, L: SUN }, { t: 12.07, d: .5, L: CARD }];
  C.ringFn = () => ({ color: '#fff', width: 10, shadow: .35 });

  // L1 · title + book staircase + paper plane to the sun
  C.scene({ t0: 0, t1: 3.9, bg: T.learnBg, quiet: true, build(L) {
      const st = {}; st.sky = T.sky(L, 14, 5); st.a = T.bubbly(L, "Hi, I'm Eva!", 110, 160, 150); st.b = T.bubbly(L, 'Eva Video Style', 110, 360, 130, { fill: Lr.STAR });
      st.c = T.bubbly(L, 'an open-source AI video-editing skill', 116, 580, 52);
      st.bs = T.stairs(L, 1000, 900); st.sun = T.sun(L, 1720, 220, 95);
      st.p = T.plane(L, [[1000, 760], [1100, 580], [1240, 380], [1420, 270]], 100);
      k.sfx('pop', .12, .1); k.sfx('pop', .9, .12, { f: 1100 }); [0, 1, 2, 3, 4].forEach(i => k.sfx('pop', 1.9 + i * .15, .08, { f: 700 + i * 120 })); k.sfx('whoosh', 2.4, .1); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.a, slide(t, .1, .5, 0, 60)); tf(st.b, slide(t, .9, .5, 0, 60)); tf(st.c, { o: P(t, 1.9, .4) });
      T.stairsAt(st.bs, t, 1.9, .15); T.sunAt(st.sun, t, P(lt, 1.0, .5)); T.planeAt(st.p, ease.io3(P(lt, 2.4, 1.4))); } });

  // L2 · four styles: icons on blobs
  C.scene({ t0: 3.87, t1: 7.76, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 12, 9, [[300, 30, .8], [1420, 30, .8], [-20, 300, .7]]);
      st.h = T.bubbly(L, 'Choose a style', 960, 70, 120, { anchor: 'middle' });
      st.it = [['openbook', 330, Lr.CLOUD, 'Cinematic'], ['bulb', 760, '#b0389a', 'Futuristic'], ['pencil', 1190, Lr.CLOUD, 'Social'], ['openbook', 1620, '#b0389a', 'Minimal']].map(([ic, x, bc, lab], i) => ({ b: T.blob(L, x, 560, 190, bc, 4 + i), i: T.lIcon(L, ic, x, 560, 170), l: T.bubbly(L, lab, x, 790, 64, { anchor: 'middle' }) }));
      [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 160 })); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.h, pop(lt, .05, .45, 1.6));
      st.it.forEach((o, i) => { const t0 = [3.9, 4.73, 5.87, 6.6][i]; tf(o.b, pop(t, t0, .4, 1.5)); const p = pop(t, t0 + .1, .45, 2); tf(o.i, { s: p.s, o: p.o, r: Math.sin(t * 2 + i) * 4 }); tf(o.l, { o: P(t, t0 + .3, .3) }); }); } });

  // L3 · open-book sunrise, planes fly out (presenter in the sunrise)
  C.scene({ t0: 7.73, t1: 12.1, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 16, 13, [[380, 60, .9], [1500, 120, .8], [-30, 620, .9], [1640, 600, .9]]);
      st.h = T.bubbly(L, 'Ready-to-use templates', 960, 60, 110, { anchor: 'middle' });
      st.s = ['Pick', 'Apply', 'AI edits'].map((s, i) => T.bubbly(L, s, [330, 1590, 960][i], [420, 420, 220][i], 84, { anchor: 'middle', fill: [Lr.STAR, Lr.GREEN, '#ff8fb8'][i] }));
      st.bk = T.bigBook(L, 960, 870, 1000); st.b1 = T.book(L, 160, 820, 300, 90, Lr.PURPLE); st.b2 = T.book(L, 180, 730, 280, 90, Lr.ORANGE); st.b3 = T.book(L, 1420, 830, 320, 90, Lr.GREEN);
      st.pl = [T.plane(L, [[820, 640], [600, 520], [430, 420], [230, 360]], 90), T.plane(L, [[1100, 640], [1300, 520], [1480, 420], [1690, 360]], 90)];
      k.sfx('riser', 7.8, .08, { d: .8 }); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('whoosh', 9.0, .1); k.sfx('whoosh', 9.9, .1); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); tf(st.h, pop(lt, .05, .45, 1.6)); st.s.forEach((e, i) => tf(e, pop(t, [8.97, 9.87, 10.67][i], .4, 1.8))); T.bigBookAt(st.bk, t, P(lt, 0, .8));
      [st.b1, st.b2, st.b3].forEach((b, i) => tf(b, { y: 80 * (1 - ease.outBack(P(lt, .3 + i * .15, .45), 1.5)), o: P(lt, .3 + i * .15, .1) })); st.pl.forEach((p, i) => T.planeAt(p, ease.io3(P(t, 9.0 + i * .9, 1.4)))); } });

  // L4 · content page with corner decorations (presenter card + goals)
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.learnBg, build(L) {
      const st = {}; st.sky = T.sky(L, 6, 21, [[20, 30, .7], [40, 900, .6]]);
      st.c1 = T.lIcon(L, 'pencil', 1740, 920, 140); st.c2 = T.book(L, 60, 930, 240, 70, Lr.RED); st.c3 = T.book(L, 80, 870, 220, 66, Lr.CLOUD); st.c4 = T.lIcon(L, 'bulb', 190, 790, 70);
      st.h = T.bubbly(L, "Today's goal", 900, 220, 84);
      st.g = [T.goal(L, '✓ Less time editing', 920, 400, Lr.STAR, -2), T.goal(L, '✓ More time creating', 920, 530, Lr.GREEN, 1.5), T.goal(L, 'Try Eva Video Style today →', 920, 660, '#ff8fb8', -1.5)];
      [12.1, 12.9, 13.8].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 120 })); return st; },
    update(lt, st, t) { T.skyAt(st.sky, t); [st.c1, st.c2, st.c3, st.c4].forEach((e, i) => tf(e, pop(lt, .1 + i * .1, .4, 1.6))); tf(st.h, { o: P(lt, .1, .4) });
      st.g.forEach((g, i) => { const p = pop(t, [12.1, 12.9, 13.8][i], .4, 1.8); tf(g, { s: p.s, o: p.o, r: [-2, 1.5, -1.5][i] }); }); } });
})();
