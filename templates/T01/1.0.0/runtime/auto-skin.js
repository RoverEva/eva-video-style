/* T01 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const C = EV, { el, tf } = C, k = K;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T01 = {
    win: { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 },
    side: 'left', theme: 't01', cls: 'dotgrid',
    ring: () => ({ color: k.INK, width: 6, shadow: .22 }),
    bg: k.LIME,
    build: L => ({
      rows: Array.from({ length: 7 }, (_, r) => k.disp(
        L,
        Array(8).fill(r % 2 ? 'EVA VIDEO STYLE' : 'AI EDITING').join(' · '),
        'rgba(11,11,13,.08)', 104, -200, -30 + r * 150
      ))
    }),
    update: (st, t, lt) => st.rows.forEach((d, i) => tf(d, {
      x: (i % 2 ? -1 : 1) * (lt * 90) - 300,
      o: 1
    }))
  };
})(window);
