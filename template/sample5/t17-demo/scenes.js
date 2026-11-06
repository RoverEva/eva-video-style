/* T17 Science Network · product demo layout (5 s sample). The product video plays big on a glass screen behind; the presenter,
 * cut out, stands in front in a glowing cyan circle that hops centre → up → right → down → left → centre. Silent: no built-in sound.
 * Screen = media/demo (the product screen recording as 30 fps JPGs); presenter = media/eva + media/cut. */
(function () {
  const C = EV, T = K.T, S = S5, V = C.portrait; S.setup(C);
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const f5 = (d, t, n) => `../media/${d}/f_${String(Math.max(0, Math.min(n - 1, Math.round(t * 30)))).padStart(5, '0')}.jpg`;
  C.scene({ t0: 0, t1: C.end + .05, bg: T.sciNetBg, quiet: true, build(L) {
      const st = { bk: T.bokeh(L, 40, 13), r: T.ribbon(L, V ? { y: 1500, amp: 90, width: 120, rows: 4, cols: 26, x1: C.W + 100 } : { y: 960, amp: 70, width: 90, rows: 4, cols: 40 }) };
      st.d = T.sciDemo(L, { D: V ? 420 : 360 }); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); T.sciDemoAt(st.d, t, f5('demo', t, 164), f5('eva', t, S.FRAMES), S.cut(t)); } });
})();
