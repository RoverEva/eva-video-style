/* T17 SCI · 科学风 Science Network — demo (16 s). Plexus networks keep rippling / rotating; bokeh drifts in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, S = T.SCN;
  C.src0 = 55; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const BR = { x: 1580, y: 690, w: 260, h: 260, r: 130, s: 3 }, BL = { x: 130, y: 640, w: 280, h: 280, r: 140, s: 3 }, TR = { x: 1600, y: 60, w: 240, h: 240, r: 120, s: 3 }, TUN = { x: 1220, y: 400, w: 260, h: 260, r: 130, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, BR, { o: 0 }) }, { t: 1.2, d: .4, L: BR }, { t: 4.0, d: .5, L: BL }, { t: 8.0, d: .5, L: TR }, { t: 12.0, d: .6, L: TUN }];
  C.ringFn = () => ({ color: S.CYAN, width: 3, glow: 'rgba(24,224,242,.5)', shadow: .5 });

  // S1 · headline + rippling plexus ribbon
  C.scene({ t0: 0, t1: 4.03, bg: T.sciNetBg, quiet: true, build(L) {
      const st = {}; st.bk = T.bokeh(L, 45, 13); st.r = T.ribbon(L, { y: 640, amp: 150, width: 230 });
      st.h = T.sciHead(L, ['[HOW WE]', 'LEARN NEW', 'WORDS'], '探索大脑和记忆背后的科学', 110, 80, 104);
      k.sfx('riser', .1, .08, { d: 1 }); k.sfx('impact', .7, .14); k.sfx('ding', 1.6, .07); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); st.r.cv.style.opacity = P(lt, 0, .8); T.sciHeadAt(st.h, t, .6); } });

  // S2 · plexus globe with real continents, slowly rotating
  C.scene({ t0: 4.0, t1: 8.03, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 35, 17); st.g = T.pSphere(L, 1300, 540, 380, { n: 320, land: true, speed: 8, lon0: 70 });
      st.h = T.sciHead(L, ['THE FUTURE', 'OF [AI]'], 'AI 正在改变我们学习的方式', 110, 180, 104);
      k.sfx('whoosh', 4.0, .1); k.sfx('impact', 4.5, .14); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.pSphereAt(st.g, t, P(lt, 0, .7)); T.sciHeadAt(st.h, t, 4.4); } });

  // S3 · chain of plexus spheres
  C.scene({ t0: 8.0, t1: 12.03, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 35, 21); st.r = T.ribbon(L, { y: 900, amp: 60, width: 60, rows: 3, cols: 40, seed: 8 });
      st.sp = [T.pSphere(L, 330, 800, 110, { n: 90, speed: 14 }), T.pSphere(L, 780, 640, 160, { n: 140, speed: -11 }), T.pSphere(L, 1320, 430, 230, { n: 200, speed: 9 })];
      st.h = T.sciHead(L, ['STEP BY STEP', '[BIG IDEAS]'], '一步一步，把知识连起来', 110, 120, 96);
      [0, 1, 2].forEach(i => k.sfx('pop', 8.6 + i * .4, .1, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); st.sp.forEach((s, i) => T.pSphereAt(s, t, P(lt, .5 + i * .4, .5))); T.sciHeadAt(st.h, t, 8.4); } });

  // S4 · plexus tunnel, Eva at its centre
  C.scene({ t0: 12.0, t1: C.end + .05, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 40, 25); st.tn = T.tunnel(L, 1350, 530, { rmax: 1100 });
      st.h = T.sciHead(L, ['OBSERVE.', 'THINK. [ACT.]'], '观察。思考。行动。', 110, 330, 100);
      k.sfx('riser', 12.0, .08, { d: .8 }); k.sfx('ding', 13.2, .08); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.tunnelAt(st.tn, t); st.tn.cv.style.opacity = P(lt, 0, .6); T.sciHeadAt(st.h, t, 12.6); } });
})();
