/* EVA Card System on T09 Wall / HUD: dark stage, HUD frame + bracket presenter window, t09 card theme (warm-white, gold numerals, 3D tilt-up). */
(function () {
  const C = EV, k = K, T = K.T, EC = K.EC, S = CS; S.setup(C, 6);
  const th = EC.theme('t09'), WIN = { x: 1290, y: 180, w: 520, h: 700, r: 0, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: WIN }]; C.ringFn = () => ({ width: 0, color: 'transparent', hud: 'rgba(255,255,255,.55)' });
  C.scene({ t0: 0, t1: C.end + .05, bg: T.hudBg, cls: 'linegrid', quiet: true, build(L) { return { f: T.hudFrame(L, 'EVA · CARD SYSTEM', 'T09') }; },
    update(lt, st, t) { T.hudFrameAt(st.f, t); } });
  C.scene({ t0: 0, t1: C.end + .05, z: 60, quiet: true, build(L) { return { h: EC.layout(L, 'hero', { hero: S.HERO, size: 120 }, { x: 110, y: 80, w: 1080 }, th),
      s: EC.layout(L, 'stack', { steps: S.STEPS, n: 4 }, { x: 110, y: 390, w: 1080, h: 600 }, th) }; },
    update(lt, st, t) { st.h.at(t, [.2, .4]); st.s.at(t, EC.times(.7, 4, .3)); } });
})();
