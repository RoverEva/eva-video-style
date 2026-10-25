/* T16 COMIC · 漫画风 Comic Pop — demo (16 s). Rays turn, clouds bob and stars pop in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, M = T.CMC;
  C.src0 = 20; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const BR = { x: 1560, y: 640, w: 270, h: 270, r: 135, s: 3 }, LEFT = { x: 150, y: 250, w: 460, h: 560, r: 30, s: 1.6 }, MID = { x: 810, y: 300, w: 300, h: 300, r: 150, s: 2.8 }, CARD = { x: 140, y: 260, w: 500, h: 600, r: 30, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, BR, { o: 0 }) }, { t: 1.4, d: .35, L: BR }, { t: 4.0, d: .45, L: LEFT }, { t: 8.0, d: .5, L: MID }, { t: 12.0, d: .5, L: CARD }];
  C.ringFn = () => ({ color: M.INK, width: 9, shadow: .3 });

  // C1 · green burst + speech cloud title + action marks + stars
  C.scene({ t0: 0, t1: 4.03, quiet: true, build(L) {
      const st = {}; st.b = T.burst(L, 960, 520, M.GREEN);
      st.sc = T.speechCloud(L, 960, 520, 760, '漫画风 · Comic Pop', 66);
      st.a = T.action(L, 960, 500, 400); st.s = [[620, 230, 26], [1330, 260, 30], [1390, 340, 20], [560, 700, 22], [720, 790, 30], [1300, 690, 24]].map(([x, y, r]) => T.cStar(L, x, y, r));
      k.sfx('impact', .3, .18); st.s.forEach((_, i) => k.sfx('pop', .9 + i * .12, .08, { f: 900 + i * 90 })); return st; },
    update(lt, st, t) { T.burstAt(st.b, t); const p = pop(lt, .25, .5, 1.8); tf(st.sc.c, { s: p.s, o: p.o }); st.sc.c.style.transformOrigin = '50% 50%'; tf(st.sc.t, pop(lt, .55, .4, 1.6));
      tf(st.a, { s: .6 + .4 * ease.outBack(P(lt, .7, .3), 2.5) + .03 * Math.sin(t * 9), o: P(lt, .7, .1) }); st.s.forEach((s, i) => { const q = pop(lt, .9 + i * .12, .35, 2.2); tf(s, { s: q.s * (1 + .08 * Math.sin(t * 5 + i)), o: q.o, r: t * 20 }); }); } });

  // C2 · zigzag split green | yellow: before vs after
  C.scene({ t0: 4.0, t1: 8.03, build(L) {
      const st = {}; const z = T.zigzag(L); st.l = T.burst(L, 300, 700, M.GREEN, z.left); st.r = T.burst(L, 1500, 420, M.YELLOW, z.right); st.z = z.s;
      st.cl = [T.comicCloud(L, -60, -120, 520, 3), T.comicCloud(L, 1460, -110, 420, 5), T.comicCloud(L, 1350, 860, 620, 8), T.comicCloud(L, -80, 900, 420, 9)];
      st.vs = T.comicText(L, 'VS', 960, 300, 170, M.STAR[0] ? M.STAR : '#ffd21f', { anchor: 'middle', rot: -8 });
      st.t1 = T.comicText(L, 'AFTER · 现在', 1150, 560, 80, '#fff', { font: M.CN }); st.st = T.sticker(L, '一键套用模版 ✓', 1160, 720, '#fff', -3);
      st.s = [T.cStar(L, 860, 160, 22, '#fff'), T.cStar(L, 960, 210, 30, '#fff'), T.cStar(L, 1130, 970, 26, '#fff')];
      k.sfx('whoosh', 4.0, .1); k.sfx('impact', 4.6, .18); k.sfx('pop', 5.4, .12); k.sfx('pop', 6.2, .12, { f: 1100 }); return st; },
    update(lt, st, t) { T.burstAt(st.l, t, 4); T.burstAt(st.r, t, -4); st.z.style.clipPath = `inset(0 0 ${100 - 100 * ease.outExpo(P(lt, 0, .5))}% 0)`; st.cl.forEach(c => T.cloudAt(c, t));
      tf(st.vs, pop(lt, .6, .45, 2.4)); tf(st.t1, slide(lt, 1.4, .4, 120, 0)); const q = pop(lt, 2.2, .4, 1.8); tf(st.st, { s: q.s, o: q.o, r: -3 }); st.s.forEach((s, i) => tf(s, { s: pop(lt, .8 + i * .2, .3, 2).s * (1 + .1 * Math.sin(t * 6 + i)), o: P(lt, .8 + i * .2, .1), r: t * 25 })); } });

  // C3 · cyan burst + sparkles + cloud ground, Eva centre stage
  C.scene({ t0: 8.0, t1: 12.03, build(L) {
      const st = {}; st.b = T.burst(L, 960, 420, M.CYAN, null, { dots: false }); st.sp = T.sparkles(L, 40, 7); st.g = T.cloudGround(L, 860, 6, 4);
      st.t = T.comicText(L, '重点来了！BIG IDEA', 960, 110, 110, '#ffd21f', { anchor: 'middle', font: M.CN });
      st.p = [T.comicCloud(L, 330, 650, 230, 41), T.comicCloud(L, 1450, 620, 260, 42)]; k.sfx('riser', 8.0, .08, { d: .6 }); k.sfx('impact', 8.6, .18); return st; },
    update(lt, st, t) { T.burstAt(st.b, t, 6); T.sparklesAt(st.sp, t); st.g.forEach(c => T.cloudAt(c, t, 6)); st.p.forEach((c, i) => { T.cloudAt(c, t, 14); c.style.opacity = P(lt, .4 + i * .2, .3); });
      tf(st.t, pop(lt, .6, .45, 2.2)); } });

  // C4 · halftone green page with cloud border: content with stickers
  C.scene({ t0: 12.0, t1: C.end + .05, build(L) {
      const st = {}; st.b = T.burst(L, 960, 380, M.LIME, null, { rays: 28 });
      st.cl = [T.comicCloud(L, -100, 780, 560, 51), T.comicCloud(L, 380, 850, 520, 52), T.comicCloud(L, 820, 820, 560, 53), T.comicCloud(L, 1300, 840, 520, 54), T.comicCloud(L, 1600, 720, 420, 55), T.comicCloud(L, 1620, -90, 380, 56)];
      st.h = T.comicText(L, '三个小技巧 · 3 TIPS', 760, 150, 84, '#fff', { font: M.CN });
      st.k = [T.sticker(L, '① 开场 3 秒抓住人', 780, 340, '#ffd21f', -2), T.sticker(L, '② 一句话一个画面', 780, 480, '#fff', 1.5), T.sticker(L, '③ 结尾记得点赞关注', 780, 620, '#4cc3f5', -1.5)];
      st.k.forEach((_, i) => k.sfx('pop', 12.8 + i * .5, .12, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.burstAt(st.b, t, 3); st.cl.forEach(c => T.cloudAt(c, t)); tf(st.h, slide(lt, .2, .4, 0, -40));
      st.k.forEach((s, i) => { const q = pop(t, 12.8 + i * .5, .4, 2); tf(s, { s: q.s, o: q.o, r: [-2, 1.5, -1.5][i] }); }); } });
})();
