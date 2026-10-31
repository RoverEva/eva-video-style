/* EVA Card System on T17 Science Network: same sample content, T17 background + presenter circle, t17 card theme. */
(function () {
  const C = EV, k = K, T = K.T, EC = K.EC, S = CS; S.setup(C, 6);
  const th = EC.theme('t17'), WIN = { x: 150, y: 300, w: 560, h: 560, r: 280, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: WIN }]; C.ringFn = () => ({ color: T.SCN.CYAN, width: 3, glow: 'rgba(24,224,242,.5)', shadow: .5 });
  C.scene({ t0: 0, t1: C.end + .05, bg: T.sciNetBg, quiet: true, build(L) { return { bk: T.bokeh(L, 45, 13), r: T.ribbon(L, { y: 1050, amp: 50, width: 70, rows: 4 }) }; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); } });
  C.scene({ t0: 0, t1: C.end + .05, z: 60, quiet: true, build(L) { return { h: EC.layout(L, 'hero', { hero: S.HERO, size: 120 }, { x: 830, y: 70, w: 960 }, th),
      s: EC.layout(L, 'stack', { steps: S.STEPS, n: 4 }, { x: 830, y: 390, w: 960, h: 600 }, th) }; },
    update(lt, st, t) { st.h.at(t, [.2, .4]); st.s.at(t, EC.times(.7, 4, .3)); } });
})();
