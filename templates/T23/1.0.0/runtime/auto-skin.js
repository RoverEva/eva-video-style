/* T23 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const C = EV, { P } = C, T = K.T;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T23 = {
    win: { x: 1180, y: 160, w: 620, h: 760, r: 40, s: 1.5 }, side: 'left', theme: 't23',
    themeOver: { surf: ['#ffffff', '#fff8ef'], ink: T.CP.INK, mute: '#5b587a', acc: T.CP.PINK, head: T.CP.KEY, headW: 400, upper: true, cardHead: T.CP.KEY,
      type: T.CP.INK, typeMode: 'pop', popC: T.CP.YEL, numMode: 'chip', chip: [T.CP.PINK, '#fff'], sh: [29, 27, 58], shA: 1, line: T.CP.INK, motion: 'pop', dur: .45, heroRot: -3, r: 28 },
    ring: () => ({ color: '#fff', width: 10, shadow: .35 }), bg: T.cpBg,
    build: (L, i) => ({ sb: T.cpSplashBg(L, (i || 0) + 2), sp: T.cpSparkles(L, 16, (i || 0) + 5) }),
    update: (st, t, lt) => { T.cpSplashBgAt(st.sb, t); T.cpSparklesAt(st.sp, t, P(lt, 0, .3)); }
  };
})(window);
