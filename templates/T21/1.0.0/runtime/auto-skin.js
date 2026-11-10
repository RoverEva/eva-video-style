/* T21 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const C = EV, { el } = C, k = K;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T21 = {
    win: { x: 1240, y: 220, w: 520, h: 640, r: 0, s: 1.4 }, side: 'left', theme: 't21',
    themeOver: { surf: ['#f7f4ee', '#ece8e0'], ink: '#1c1b18', mute: '#6f6a61', acc: '#1c1b18', head: "'Playfair Display', 'Noto Serif CJK SC', serif", headW: 400, upper: false,
      cardHead: "'Playfair Display', 'Noto Serif CJK SC', serif", type: '#1c1b18', typeMode: 'pop', popC: 'rgba(0,0,0,0)', numMode: '3d', tint: [236, 232, 224],
      sh: [111, 106, 97], shA: .35, border: '1px solid #cbbfa9', line: '#cbbfa9', motion: 'fade-slide', dur: .9, bob: 0, heroRot: 0, r: 2 },
    ring: () => ({ color: '#cbbfa9', width: 2, shadow: 0 }), bg: '#ece8e0',
    build: L => { const sv = k.svg(L, 1920, 1080, 0, 0); return {
      v: el(L, 'div', 'abs', { left: '80px', top: '0px', width: '1px', height: '1080px', background: '#cbbfa9' }),
      c: k.sv(sv, 'circle', { cx: 1500, cy: 540, r: 420, fill: 'none', stroke: '#d8cfbf', 'stroke-width': 1.5, 'stroke-dasharray': '4 7' })
    }; },
    update: (st, t) => st.c.setAttribute('transform', `rotate(${(t * 3).toFixed(2)} 1500 540)`)
  };
})(window);
