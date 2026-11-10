/* T02 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const k = K;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T02 = {
    win: { x: 1260, y: 200, w: 560, h: 680, r: 30, s: 1.5 }, side: 'left', theme: 't02', cls: 'linegrid',
    themeOver: { surf: ['#ffffff', '#eef1ff'], ink: k.INK, mute: '#4a4f6e', acc: k.BLUE, kick: k.BLUE, head: "'Anton', 'Archivo Black', 'Noto Sans CJK SC', sans-serif", headW: 400,
      upper: true, cardHead: "'Anton', 'Archivo Black', 'Noto Sans CJK SC', sans-serif", type: '#fff', typeMode: 'glow', glow: '212,255,46', numMode: 'chip', chip: [k.BLUE, '#fff'],
      sh: [7, 11, 46], shA: 1.4, line: k.LIME, motion: 'fade-slide', dur: .45, bob: 0, heroRot: 0, r: 26 },
    ring: () => ({ color: k.LIME, width: 6, glow: 'rgba(212,255,46,.4)' }),
    bg: `radial-gradient(1400px 900px at 40% 30%, #12206b, ${k.NAVY})`,
    build: () => ({}), update: () => {}
  };
})(window);
