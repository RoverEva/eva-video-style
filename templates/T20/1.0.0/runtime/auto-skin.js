/* T20 automatic-edit skin, extracted unchanged from the Studio auto runtime. */
(function (root) {
  const C = EV, { el } = C;
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  root.EVA_TEMPLATE_SKINS.T20 = {
    win: { x: 130, y: 110, w: 600, h: 820, r: 52, s: 1.6 }, side: 'right', theme: 't20',
    ring: () => ({ color: '#fff', width: 10, shadow: .35 }), bg: '#ece6fb',
    build: L => ({ b: el(L, 'div', 'abs', { left: '440px', top: '640px', width: '520px', height: '380px', background: 'linear-gradient(135deg, #2fe0b4, #3aa0ff)',
      borderRadius: '48% 52% 44% 56% / 55% 45% 55% 45%', transform: 'rotate(-8deg)' }) }),
    update: () => {}
  };
})(window);
