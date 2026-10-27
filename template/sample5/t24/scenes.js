/* T24 Luxury Nude Motion — 5 s sample. Solid nude stage, presenter integrated as an AI cut-out with a soft shadow,
 * 3D white type, floating ivory cards, light-sweep transitions. Copy is generic sample text. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, X = T.LX, S = S5; S.setup(C);
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const B = [0, 1.4, 3.2, S.END + .05];
  C.scene({ t0: 0, t1: C.end + .05, bg: T.lxBg, quiet: true, build(L) {
      const st = { g: [] }; st.p = T.lxPresenter(L, 10); st.sw = T.lxSweep(L);
      const G = f => { const w = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 15 }); st.g.push({ w, o: f(w) }); };
      G(w => T.lxHero(w, 'EVA VIDEO STYLE', ['BIG', 'IDEAS'], 'SIMPLE STEPS', 1000, 230, 220));
      G(w => T.lxSteps(w, [{ t: 'Idea', d: 'Find the opportunity', i: 'idea' }, { t: 'Plan', d: 'Create a clear plan', i: 'plan' }, { t: 'Build', d: 'Turn it into reality', i: 'build' }], 1010, 160, 780, 220, 34));
      G(w => T.lxStatement(w, 'Turn', 'IDEAS', 'INTO RESULTS', 1080, 400, 220));
      k.sfx('riser', .02, .05, { d: .5 }); k.sfx('ding', .45, .05); k.sfx('whoosh', B[1] - .05, .06); [1.5, 1.9, 2.3].forEach((x, i) => k.sfx('pop', x, .07, { f: 700 + i * 120 })); k.sfx('whoosh', B[2] - .05, .06); k.sfx('ding', 3.6, .05); return st; },
    update(lt, st, t) { const i = t < B[1] ? 0 : t < B[2] ? 1 : 2; st.g.forEach((g, k2) => { g.w.style.display = k2 === i ? '' : 'none'; g.w.style.opacity = k2 < 2 ? 1 - P(t, B[k2 + 1] - .25, .25) : 1; });
      T.lxPresenterAt(st.p, S.cut(t), { x: -470, y: 0, s: 1.02 + .03 * P(t, 0, S.END) }); T.lxSweepAt(st.sw, t, B[i] - .35);
      const o = st.g[i].o; [() => T.lxHeroAt(o, t, [.05, .2, .45, .75]), () => T.lxStepsAt(o, t, [1.5, 1.9, 2.3]), () => T.lxStatementAt(o, t, [3.3, 3.55, 3.85])][i](); } });
})();
