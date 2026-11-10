/* T17 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const T = K.T;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T17 = {
    win: { x: 150, y: 300, w: 560, h: 560, r: 280, s: 1.5 },
    side: 'right', theme: 't17',
    ring: () => ({ color: T.SCN.CYAN, width: 3, glow: 'rgba(24,224,242,.5)', shadow: .5 }),
    bg: T.sciNetBg,
    build: L => ({
      bk: T.bokeh(L, 45, 13),
      r: T.ribbon(L, { y: 1050, amp: 50, width: 70, rows: 4 })
    }),
    update: (st, t) => {
      T.bokehAt(st.bk, t);
      T.ribbonAt(st.r, t);
    }
  };
})(window);
