/* EVA Card System on T01 Acid Lime: lime dot grid + scrolling type, presenter card on the right, t01 card theme (ink chips, hard edge, fast slide). */
(function () {
  const C = EV, { tf } = C, k = K, EC = K.EC, S = CS; S.setup(C, 6);
  const th = EC.theme('t01'), WIN = { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: WIN }]; C.ringFn = () => ({ color: k.INK, width: 6, shadow: .22 });
  C.scene({ t0: 0, t1: C.end + .05, bg: k.LIME, cls: 'dotgrid', quiet: true, build(L) {
      return { rows: Array.from({ length: 7 }, (_, r) => k.disp(L, Array(8).fill(r % 2 ? 'EVA VIDEO STYLE' : 'OPEN SOURCE · AI EDITING').join(' · '), 'rgba(11,11,13,.08)', 104, -200, -30 + r * 150)) }; },
    update(lt, st, t) { st.rows.forEach((d, i) => tf(d, { x: (i % 2 ? -1 : 1) * (lt * 90) - 300, o: 1 })); } });
  C.scene({ t0: 0, t1: C.end + .05, z: 60, quiet: true, build(L) { return { h: EC.layout(L, 'hero', { hero: S.HERO, size: 130 }, { x: 110, y: 70, w: 1040 }, th),
      s: EC.layout(L, 'stack', { steps: S.STEPS, n: 4 }, { x: 110, y: 400, w: 1040, h: 600 }, th) }; },
    update(lt, st, t) { st.h.at(t, [.2, .4]); st.s.at(t, EC.times(.7, 4, .3)); } });
})();
