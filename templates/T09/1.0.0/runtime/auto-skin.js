/* T09 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const T = K.T;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T09 = {
    win: { x: 1290, y: 180, w: 520, h: 700, r: 0, s: 1.5 }, side: 'left', theme: 't09', cls: 'linegrid',
    ring: () => ({ width: 0, color: 'transparent', hud: 'rgba(255,255,255,.55)' }), bg: T.hudBg,
    build: L => ({ f: T.hudFrame(L, 'EVA · VIDEO STUDIO', 'T09') }),
    update: (st, t) => T.hudFrameAt(st.f, t)
  };
})(window);
