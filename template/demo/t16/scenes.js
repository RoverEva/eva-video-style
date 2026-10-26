/* T16 Comic Pop — demo on the shared 15 s intro. Rays turn, clouds bob and stars pop in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, M = T.CMC, I = IN; I.setup(C);
  const BR = { x: 1560, y: 640, w: 270, h: 270, r: 135, s: 3 }, LEFT = { x: 150, y: 250, w: 460, h: 560, r: 30, s: 1.6 }, MID = { x: 810, y: 330, w: 300, h: 300, r: 150, s: 2.8 }, CARD = { x: 140, y: 260, w: 500, h: 600, r: 30, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, BR, { o: 0 }) }, { t: .1, d: .35, L: BR }, { t: 3.87, d: .45, L: LEFT }, { t: 7.73, d: .5, L: MID }, { t: 12.07, d: .5, L: CARD }];
  C.ringFn = () => ({ color: M.INK, width: 9, shadow: .3 });

  // C1 · green burst + speech-cloud title + action marks + stars
  C.scene({ t0: 0, t1: 3.9, quiet: true, build(L) {
      const st = {}; st.b = T.burst(L, 960, 520, M.GREEN);
      st.sc = T.speechCloud(L, 960, 500, 820, "Hi, I'm Eva!", 96);
      st.t2 = T.comicText(L, 'EVA VIDEO STYLE', 960, 840, 96, '#ffd21f', { anchor: 'middle', rot: -4 });
      st.st = T.sticker(L, 'open-source AI video editing ✓', 600, 975, '#fff', -2);
      st.a = T.action(L, 960, 480, 400); st.s = [[620, 230, 26], [1330, 260, 30], [1390, 340, 20], [560, 700, 22], [1300, 690, 24]].map(([x, y, r]) => T.cStar(L, x, y, r));
      k.sfx('impact', .15, .18); k.sfx('pop', .9, .14); k.sfx('pop', 1.95, .14, { f: 1100 }); st.s.forEach((_, i) => k.sfx('pop', .4 + i * .1, .06, { f: 900 + i * 90 })); return st; },
    update(lt, st, t) { T.burstAt(st.b, t); const p = pop(lt, .12, .5, 1.8); tf(st.sc.c, { s: p.s, o: p.o }); st.sc.c.style.transformOrigin = '50% 50%'; tf(st.sc.t, pop(lt, .3, .4, 1.6));
      const q = pop(t, .9, .4, 2); tf(st.t2, { s: q.s, o: q.o }); const r = pop(t, 1.95, .4, 1.8); tf(st.st, { s: r.s, o: r.o, r: -2 });
      tf(st.a, { s: .6 + .4 * ease.outBack(P(lt, .3, .3), 2.5) + .03 * Math.sin(t * 9), o: P(lt, .3, .1) }); st.s.forEach((s, i) => { const q2 = pop(lt, .4 + i * .1, .35, 2.2); tf(s, { s: q2.s * (1 + .08 * Math.sin(t * 5 + i)), o: q2.o, r: t * 20 }); }); } });

  // C2 · zigzag split green | yellow: four style stickers
  C.scene({ t0: 3.87, t1: 7.76, build(L) {
      const st = {}; const z = T.zigzag(L); st.l = T.burst(L, 300, 700, M.GREEN, z.left); st.r = T.burst(L, 1500, 420, M.YELLOW, z.right); st.z = z.s;
      st.cl = [T.comicCloud(L, 1460, -110, 420, 5), T.comicCloud(L, 1350, 860, 620, 8)];
      st.t1 = T.comicText(L, 'PICK A STYLE!', 1290, 200, 100, '#fff', { anchor: 'middle', rot: -4 });
      st.k = I.STYLES.map((s, i) => T.sticker(L, s, 780 + (i % 2) * 520, 380 + Math.floor(i / 2) * 170, ['#ffd21f', '#fff', '#4cc3f5', '#ff8fb8'][i], [-3, 2, 2, -2][i]));
      k.sfx('whoosh', 3.9, .1); [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x + .05, .12, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.burstAt(st.l, t, 4); T.burstAt(st.r, t, -4); st.z.style.clipPath = `inset(0 0 ${100 - 100 * ease.outExpo(P(lt, 0, .5))}% 0)`; st.cl.forEach(c => T.cloudAt(c, t));
      tf(st.t1, pop(lt, .1, .45, 2.2)); st.k.forEach((s, i) => { const q = pop(t, [3.95, 4.73, 5.87, 6.6][i], .4, 2); tf(s, { s: q.s, o: q.o, r: [-3, 2, 2, -2][i] }); }); } });

  // C3 · cyan burst + sparkles + cloud ground, presenter centre stage
  C.scene({ t0: 7.73, t1: 12.1, build(L) {
      const st = {}; st.b = T.burst(L, 960, 480, M.CYAN, null, { dots: false }); st.sp = T.sparkles(L, 40, 7); st.g = T.cloudGround(L, 860, 6, 4);
      st.t = T.comicText(L, 'READY-TO-USE TEMPLATES!', 960, 110, 100, '#ffd21f', { anchor: 'middle' });
      st.k = [['① PICK', 180, 380, '#fff', -3], ['② APPLY', 1300, 380, '#ffd21f', 3], ['③ AI EDITS!', 1260, 640, '#ff8fb8', -2]].map(([s, x, y, c, r]) => T.sticker(L, s, x, y, c, r));
      k.sfx('riser', 7.8, .08, { d: .6 }); k.sfx('impact', 8.2, .18); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.burstAt(st.b, t, 6); T.sparklesAt(st.sp, t); st.g.forEach(c => T.cloudAt(c, t, 6));
      tf(st.t, pop(lt, .3, .45, 2.2)); st.k.forEach((s, i) => { const q = pop(t, [8.97, 9.87, 10.67][i], .4, 2.2); tf(s, { s: q.s, o: q.o, r: [-3, 3, -2][i] }); }); } });

  // C4 · lime burst with a cloud border: less / more / try it
  C.scene({ t0: 12.07, t1: C.end + .05, build(L) {
      const st = {}; st.b = T.burst(L, 960, 380, M.LIME, null, { rays: 28 });
      st.cl = [T.comicCloud(L, -100, 780, 560, 51), T.comicCloud(L, 380, 850, 520, 52), T.comicCloud(L, 820, 820, 560, 53), T.comicCloud(L, 1300, 840, 520, 54), T.comicCloud(L, 1600, 720, 420, 55), T.comicCloud(L, 1620, -90, 380, 56)];
      st.h = T.comicText(L, 'LESS EDITING!', 760, 160, 96, '#fff');
      st.k = [T.sticker(L, 'MORE CREATING ★', 780, 360, '#ffd21f', -2), T.sticker(L, 'Try Eva Video Style today →', 780, 520, '#4cc3f5', 1.5)];
      k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .14); k.sfx('pop', 13.8, .14, { f: 1100 }); return st; },
    update(lt, st, t) { T.burstAt(st.b, t, 3); st.cl.forEach(c => T.cloudAt(c, t)); tf(st.h, slide(t, 12.1, .4, 0, -40));
      st.k.forEach((s, i) => { const q = pop(t, [12.9, 13.8][i], .4, 2); tf(s, { s: q.s, o: q.o, r: [-2, 1.5][i] }); }); } });
})();
