/* EVA Card System on T20 Social: lavender stage, rounded presenter card, t20 card theme (violet number chips, condensed type, pop motion). */
(function () {
  const C = EV, { el } = C, k = K, EC = K.EC, S = CS; S.setup(C, 6);
  const th = EC.theme('t20'), WIN = { x: 130, y: 110, w: 600, h: 820, r: 52, s: 1.6 };
  C.evaKeys = [{ t: 0, d: 0, L: WIN }]; C.ringFn = () => ({ color: '#fff', width: 10, shadow: .35 });
  C.scene({ t0: 0, t1: C.end + .05, bg: '#ece6fb', quiet: true, build(L) {
      return { b: el(L, 'div', 'abs', { left: '440px', top: '640px', width: '520px', height: '380px', background: 'linear-gradient(135deg, #2fe0b4, #3aa0ff)', borderRadius: '48% 52% 44% 56% / 55% 45% 55% 45%', transform: 'rotate(-8deg)' }) }; },
    update(lt, st, t) { } });
  C.scene({ t0: 0, t1: C.end + .05, z: 60, quiet: true, build(L) { return { h: EC.layout(L, 'hero', { hero: S.HERO, size: 130 }, { x: 840, y: 70, w: 960 }, th),
      s: EC.layout(L, 'stack', { steps: S.STEPS, n: 4 }, { x: 840, y: 400, w: 960, h: 600 }, th) }; },
    update(lt, st, t) { st.h.at(t, [.2, .4]); st.s.at(t, EC.times(.7, 4, .3)); } });
})();
