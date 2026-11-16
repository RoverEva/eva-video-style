/* T29 Depth Glow · 5 s vertical sample on the AI presenter clip: 01 headline → 03 globe → 07 particle stream → 08 checklist.
 * Copy is generic sample text (no transcript for this clip). Graphics render behind the presenter; no template sound. */
(function () {
  const C = EV, T = K.T, F = 151; C.src0 = 0; C.end = 151 / 30; C.evaDir = '../media26/eva'; C.face = { x: .5, y: .33, h: .2 }; C.src = { w: 1080, h: 1920 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const fr = (d, t, ext, n) => `../media26/${d}/f_${String(Math.max(0, Math.min(n - 1, Math.round(t * 30)))).padStart(5, '0')}.${ext}`;
  const m = { frame: t => fr('eva', t, 'jpg', F), cut: t => fr('cut', t, 'webp', 150) };
  const LAY = [[1, { a: '资料很少', k: 'NEW' }], [3, { items: ['AI tutorial', 'How-to guide', 'Your website'] }], [7, { a: '我的网站' }], [8, { a: 'FAQ', items: ['How do I make it?', 'How long does it take?', 'What do I need?'] }]],
    B = [0, 1.15, 2.3, 3.45, C.end + .05];
  C.scene({ t0: 0, t1: C.end + .05, bg: T.dgBg, quiet: true, build(L) { return { g: LAY.map(([n, w]) => T.dgLayout(n, L, w, m)) }; },
    update(lt, st, t) { const i = Math.max(0, B.findIndex((b, j) => t >= b && t < B[j + 1]));
      st.g.forEach((g, j) => { const on = j === i || (j === i - 1 && t < B[i] + .2); g.root.style.display = on ? '' : 'none'; if (!on) return;
        g.root.style.zIndex = j; g.fx.style.opacity = j < i ? 1 - (t - B[i]) / .2 : 1; if (j < i) { g.plate.style.opacity = g.cut.style.opacity = 0; }
        else g.plate.style.opacity = g.cut.style.opacity = 1;
        T.dgLayoutAt(g, t, B[j], m); }); } });
})();
