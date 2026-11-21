/* T31 Sticky Notes Board 便利贴墙 · 10 s concept sample (16:9). Silent; sample copy (illustrative).
 * Cork board → rounded-square presenter window (white photo border) → sticky notes slap on → hand-drawn arrow / red strike. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", INK = '#1f1f1f';
  const note = (L, x, y, r, col, cn, en) => { const n = M.box(L, 0, 0, { width: '300px', height: '270px', background: col, padding: '30px 28px', boxSizing: 'border-box', transformOrigin: '50% 30%' });
    el(n, 'div', '', { font: `900 44px ${CN}`, color: INK, lineHeight: 1.15, whiteSpace: "nowrap" }, cn); el(n, 'div', '', { font: `italic 700 28px 'Playfair Display', serif`, color: '#3a3a3a', marginTop: '10px' }, en);
    el(n, 'div', 'abs', { left: '110px', top: '-14px', width: '80px', height: '26px', background: 'rgba(255,255,255,.45)' }); return { n, x, y, r }; };
  M.setup({
    bg: '#c9a072',
    win: { x: 100, y: 130, w: 560, h: 640, r: 36, o: 1, s: 1.2 },
    ring: () => ({ color: '#ffffff', width: 16, shadow: .42 }),
    port: { box: [740, 50, 1100, 720] },
    captions: [{ t0: .5, t1: 3.4, cn: '剪视频的三个小技巧', en: 'Three quick editing tips' },
               { t0: 3.5, t1: 6.6, cn: '一条一个点，别贪多', en: "One idea each — don't cram" },
               { t0: 6.7, t1: 9.7, cn: '记住了吗？收藏起来', en: 'Got it? Save this for later' }],
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', backgroundImage: 'radial-gradient(rgba(90,55,25,.35) 2px, transparent 2.4px), radial-gradient(rgba(255,240,215,.22) 1.4px, transparent 1.8px)', backgroundSize: '22px 22px, 15px 15px', backgroundPosition: '0 0, 8px 9px' }));
      s.title = M.box(L, 760, 70, { font: `900 74px ${CN}`, color: INK, background: '#fbf6ea', padding: '10px 26px', transformOrigin: '0 50%', boxShadow: '0 6px 14px rgba(60,35,10,.3)' }, '剪辑 3 个小技巧');
      s.notes = [note(L, 770, 250, -4, '#ffe45c', '先写开头', 'hook first'), note(L, 1130, 280, 3, '#ff9ec7', '一条一个点', 'one idea each'), note(L, 1480, 230, -2, '#8fd3ff', '越长越好？', 'longer = better?')];
      s.strike = M.svg(L, 1500, 300, 280, 200, `<path d="M14 30 L262 168" stroke="#e5262f" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/><path d="M262 26 L18 176" stroke="#e5262f" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>`);
      s.st = [...s.strike.querySelectorAll('path')];
      s.arrow = M.svg(L, 900, 540, 380, 200, `<path d="M20 30 C 120 190, 260 190, 340 60" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/><path d="M318 72 L342 56 L350 86" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1"/>`);
      s.ar = [...s.arrow.querySelectorAll('path')];
      s.circ = M.svg(L, 1100, 255, 360, 320, `<ellipse cx="180" cy="160" rx="170" ry="148" fill="none" stroke="#e5262f" stroke-width="7" pathLength="1" stroke-dasharray="1 1" transform="rotate(-6 180 160)"/>`).querySelector('ellipse');
      s.save = M.box(L, 820, 650, { font: `900 46px ${CN}`, color: '#fbf6ea', background: INK, padding: '10px 24px', borderRadius: '10px' }, '收藏 ✓');
      return s; },
    update(s, t) {
      M.hero(s.title, t, .9, 9.2, { dx: -40, din: .33 });
      const at = [1.9, 3.6, 4.9];
      s.notes.forEach(({ n, x, y, r }, i) => M.slap(n, t, at[i], 9.2, { x, y, r }));
      s.st.forEach((p, i) => M.draw(p, t, 5.7 + i * .2, .22, 9.2));
      s.ar.forEach((p, i) => M.draw(p, t, 6.85 + i * .45, i ? .18 : .45, 9.2));
      M.draw(s.circ, t, 7.5, .5, 9.2);
      M.pop(s.save, t, 8.2, 9.2, { from: .6 });
    }
  });
})();
