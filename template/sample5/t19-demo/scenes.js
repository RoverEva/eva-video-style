/* T19 Footage Intro · product demo layout (5 s sample). The product video plays full-bleed behind at normal speed; the presenter,
 * cut out, stands in front in a white-ringed circle that hops centre → up → right → down → left → centre. Label = text from the
 * screen. Silent: no built-in sound. Screen = media/demo (screen recording as 30 fps JPGs); presenter = media/eva + media/cut. */
(function () {
  const C = EV, T = K.T, S = S5, V = C.portrait; S.setup(C);
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const f5 = (d, t, n) => `../media/${d}/f_${String(Math.max(0, Math.min(n - 1, Math.round(t * 30)))).padStart(5, '0')}.jpg`;
  C.scene({ t0: 0, t1: C.end + .05, bg: '#000', quiet: true, build(L) { return { d: T.ftDemo(L, { D: V ? 420 : 360, label: 'TERM & DEFINITION MATCH' }) }; },
    update(lt, st, t) { T.ftDemoAt(st.d, t, f5('demo', t, 164), f5('eva', t, S.FRAMES), S.cut(t)); } });
})();
