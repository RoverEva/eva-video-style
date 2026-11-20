/* T37 Magazine Cover 杂志封面 · 10 s concept sample (16:9). Silent; sample copy (illustrative); masthead "EVA" is the presenter's own name. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const PF = "'Playfair Display', serif", CN = "'Noto Sans CJK SC', sans-serif", RED = '#d4202a', INK = '#161616';
  M.setup({
    bg: '#efe3d3',
    win: { x: 700, y: 300, w: 520, h: 500, r: 28, o: 1, s: 1.12 },
    ring: () => ({ color: '#ffffff', width: 10, shadow: .4 }),
    captions: [{ t0: .5, t1: 3.4, cn: '这期封面，聊聊个人品牌', en: 'This issue: your personal brand' },
               { t0: 3.5, t1: 6.6, cn: '三个习惯，让人记住你', en: 'Three habits that make you memorable' },
               { t0: 6.7, t1: 9.7, cn: '完整访谈，下期见', en: 'Full interview next issue' }],
    build(L) { const s = {};
      s.mast = [...'EVA'].map((ch, i) => M.box(L, 610 + i * 250, 20, { font: `900 270px ${PF}`, color: RED, lineHeight: 1 }, ch));
      s.issue = M.box(L, 110, 70, { font: `700 24px 'Space Mono', monospace`, color: INK, letterSpacing: '.1em' }, 'ISSUE 07 · 2026');
      s.l1 = M.box(L, 110, 330, { font: `900 74px ${CN}`, color: INK, lineHeight: 1.12, width: '520px' }, '做自己的品牌');
      s.l2 = M.box(L, 112, 430, { font: `italic 700 46px ${PF}`, color: RED }, 'Be your own brand');
      s.rule = M.svg(L, 112, 510, 460, 10, `<path d="M0 5H440" stroke="${INK}" stroke-width="4" pathLength="1" stroke-dasharray="1 1"/>`).querySelector('path');
      s.r1 = M.box(L, 1290, 330, { font: `400 150px Anton, sans-serif`, color: RED, lineHeight: 1 }, '3');
      s.r2 = M.box(L, 1390, 350, { font: `900 50px ${CN}`, color: INK, lineHeight: 1.2 }, '个习惯');
      s.r3 = M.box(L, 1390, 420, { font: `700 34px ${CN}`, color: '#4a4a4a' }, '让人一眼记住你');
      s.flip = M.box(L, 0, 0, { width: C.W + 'px', height: C.H + 'px', background: RED, transformOrigin: '0 50%' });
      s.ex = M.box(L, 1290, 560, { font: `900 56px ${CN}`, color: '#fff', background: INK, padding: '8px 22px' }, '独家专访');
      s.ex2 = M.box(L, 1292, 650, { font: `italic 700 34px ${PF}`, color: INK }, 'Exclusive interview');
      s.bc = M.svg(L, 1660, 650, 150, 110, Array.from({ length: 26 }, (_, i) => `<line x1="${6 + i * 5.4}" x2="${6 + i * 5.4}" y1="6" y2="86" stroke="${INK}" stroke-width="${[1, 3, 2, 1, 4][i % 5]}" pathLength="1" stroke-dasharray="1 1"/>`).join('') + `<rect x="0" y="0" width="150" height="110" fill="none"/>`, { background: '#fff' });
      s.bars = [...s.bc.querySelectorAll('line')];
      return s; },
    update(s, t) {
      s.mast.forEach((e, i) => M.hero(e, t, .7 + i * .13, 9.2, { dx: 0, dy: -90, noclip: true }));
      M.rise(s.issue, t, .9, 9.2, { dy: 16 });
      M.hero(s.l1, t, 1.3, 9.2, { dx: -50 }); M.rise(s.l2, t, 1.6, 9.2); M.draw(s.rule, t, 1.8, .5, 9.2);
      M.pop(s.r1, t, 3.5, 9.2, { from: .4 }); M.hero(s.r2, t, 3.65, 9.2, { dx: 40 }); M.rise(s.r3, t, 3.85, 9.2);
      /* page-flip accent: a red sheet sweeps across behind the window (graphics layer) and folds away */
      const u = (t - 6.55) / .5; s.flip.style.display = u > 0 && u < 1 ? '' : 'none';
      s.flip.style.transform = `perspective(1800px) rotateY(${(-90 + 180 * M.io(u)).toFixed(2)}deg)`; s.flip.style.opacity = .92;
      M.panel(s.ex, t, 6.85, 9.2); M.rise(s.ex2, t, 7.05, 9.2);
      M.pop(s.bc, t, 7.3, 9.2, { from: .9 }); s.bars.forEach((b, i) => M.draw(b, t, 7.35 + i * .02, .18, 9.2));
    }
  });
})();
