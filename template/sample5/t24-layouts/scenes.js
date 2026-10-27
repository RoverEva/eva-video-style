/* T24 Luxury Nude — all eight layouts, 2 s each, on the 5 s sample (the presenter cut-out loops). Use it as a reference for each layout's call. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, X = T.LX, S = S5; S.setup(C); C.end = 16;
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const CUT = t => S.cut(t % 5);
  const ST = [{ t: 'Idea', d: 'Find the opportunity', i: 'idea' }, { t: 'Plan', d: 'Create a clear plan', i: 'plan' }, { t: 'Build', d: 'Turn it into reality', i: 'build' }, { t: 'Grow', d: 'Scale your impact', i: 'grow' }];
  const SEV = [{ t: 'Idea', i: 'idea' }, { t: 'Plan', i: 'plan' }, { t: 'Build', i: 'build' }, { t: 'Grow', i: 'grow' }, { t: 'Audience', i: 'audience' }, { t: 'Launch', i: 'rocket' }, { t: 'Success', i: 'success' }];
  const at = (t0, n, d) => Array.from({ length: n }, (_, i) => t0 + i * (d || .18));
  const POSE = [{ x: -470, s: 1.02 }, { x: -470, s: 1.02 }, { x: -470, s: 1.02 }, { x: 0, y: 120, s: .9 }, { x: -470, s: 1.02 }, { x: -470, s: 1.02 }, { x: 0, y: 170, s: .82 }, { x: -470, s: 1.02 }];
  C.scene({ t0: 0, t1: C.end + .05, bg: T.lxBg, quiet: true, build(L) {
      const st = { g: [] }; st.p = T.lxPresenter(L, 10); st.sw = T.lxSweep(L);
      const G = (i, f) => { const w = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 15 }); st.g[i] = { w, o: f(w) }; };
      G(0, w => T.lxHero(w, '', ['BIG', 'IDEAS'], 'SIMPLE STEPS', 1000, 200, 210));
      G(1, w => T.lxSteps(w, ST.slice(0, 3), 1020, 150, 760, 220, 34));
      G(2, w => T.lxTiles(w, ST, 980, 360, 200, 24));
      G(3, w => T.lxOrbit(w, SEV.slice(0, 6), 960, 620, 520, Math.PI * .96, Math.PI * 2.04, 170));
      G(4, w => T.lxStatement(w, 'Turn', 'IDEAS', 'INTO RESULTS', 980, 380, 230));
      G(5, w => T.lxFeature(w, { t: 'Idea', d: 'Find a real problem and a unique opportunity.', i: 'idea' }, 1, 900, 250, 900, 500));
      G(6, w => T.lxTimeline(w, SEV, 260, 1680, 380, 160, 130));
      G(7, w => T.lxGrid(w, SEV, 1000, 140, 3, 220, 26));
      return st; },
    update(lt, st, t) { const i = Math.min(7, Math.floor(t / 2)); st.g.forEach((g, k) => g.w.style.display = k === i ? '' : 'none'); T.lxPresenterAt(st.p, CUT(t), POSE[i]); T.lxSweepAt(st.sw, t, i * 2 - .3);
      const o = st.g[i].o, t0 = i * 2 + .1;
      [() => T.lxHeroAt(o, t, [t0, t0 + .2, t0 + .4, t0 + .7]), () => T.lxStepsAt(o, t, at(t0, 3, .3)), () => T.lxTilesAt(o, t, at(t0, 4, .2)), () => T.lxOrbitAt(o, t, at(t0, 6, .12)),
       () => T.lxStatementAt(o, t, [t0, t0 + .25, t0 + .5]), () => T.lxFeatureAt(o, t, t0), () => T.lxTimelineAt(o, t, at(t0, 7, .1)), () => T.lxGridAt(o, t, at(t0, 7, .1))][i](); } });
})();
