/* T39 Split Before/After 对比分屏 · 10 s concept sample (16:9). Silent; sample copy (illustrative). */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C, P = C.portrait, at = (l, p) => P ? p : l, PW = at(960, 2000);
  const CN = "'Noto Sans CJK SC', sans-serif", YL = '#ffd23f', INK = '#151515';
  const list = (L, x, y, items, col, mk) => items.map((s, i) => { const r = M.box(L, x, y + i * 74, { font: `700 42px ${CN}`, color: col, whiteSpace: 'nowrap' }); r.innerHTML = `<span style="display:inline-block;width:56px">${mk}</span>${s}`; return r; });
  M.setup({
    bg: '#2b2d31',
    win: { x: 770, y: 300, w: 380, h: 380, r: 190, o: 1, s: 1.1 },
    ring: () => ({ color: '#ffffff', width: 10, shadow: .5 }),
    port: { box: [0, 60, 1100, 1120], maxH: 1000, win: { x: 720, y: 551, w: 300, h: 300, r: 150, o: 1, s: 1.1 } },
    captions: [{ t0: .5, t1: 3.4, cn: '以前：手动剪一整天', en: 'Before: a whole day of manual editing' },
               { t0: 3.5, t1: 6.6, cn: '现在：上传，几分钟搞定', en: 'Now: upload, done in minutes' },
               { t0: 6.7, t1: 9.7, cn: '差别，一眼就看得出', en: 'You can see the difference' }],
    build(L) { const s = {};
      s.after = M.box(L, at(960, -100), at(0, 620), { width: PW + 'px', height: at(C.H, 560) + 'px', background: YL });
      s.line = M.box(L, at(957, -103), at(0, 620), { width: '6px', height: at(C.H, 560) + 'px', background: '#fff' });
      s.bt = M.box(L, 110, 90, { font: `400 110px Anton, sans-serif`, color: '#8d9099', letterSpacing: '.04em' }, 'BEFORE');
      s.bh = M.box(L, 110, 220, { font: `900 60px ${CN}`, color: '#e8e8ea' }, '手动剪一整天');
      s.bl = list(L, 110, 330, ['逐帧对字幕', '反复导出', '加班到深夜'], '#a9acb4', '<span style="color:#ff5a5f">✕</span>');
      s.at = M.box(L, at(1230, 110), at(90, 650), { font: `400 110px Anton, sans-serif`, color: INK, letterSpacing: '.04em' }, 'AFTER');
      s.ah = M.box(L, at(1230, 110), at(220, 780), { font: `900 60px ${CN}`, color: INK }, '上传，几分钟');
      s.al = list(L, at(1230, 110), at(330, 890), ['自动双语字幕', '一键出片', '准点下班'], INK, '<span style="color:#1a9e55">✓</span>');
      s.vs = M.box(L, at(900, 520), at(700, 560), { width: '120px', height: '120px', borderRadius: '50%', background: INK, color: '#fff', font: `400 62px Anton, sans-serif`, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '6px solid #fff', boxSizing: 'border-box', transformOrigin: '50% 50%' }, 'VS');
      return s; },
    update(s, t) {
      /* divider sweep: the yellow AFTER panel wipes in from the right edge, then settles on the centre */
      const w = M.o5((t - 3.35) / .55), x = 960 + PW * (1 - w), out = M.i2((t - 8.97) / .23);
      s.after.style.clipPath = `inset(0 0 0 ${(PW * (1 - w)).toFixed(1)}px)`; s.after.style.opacity = (t > 3.35 ? 1 : 0) * (1 - out);
      s.line.style.transform = `translateX(${(PW * (1 - w)).toFixed(1)}px)`; s.line.style.opacity = (M.env(t, .7, 9.2).a).toFixed(3);
      M.hero(s.bt, t, .8, 9.2, { dx: -50 }); M.rise(s.bh, t, 1.05, 9.2); s.bl.forEach((r, i) => M.slide(r, t, 1.5 + i * .14, 9.2, { dx: -40 }));
      /* BEFORE dims once AFTER lands */
      const dim = 1 - .45 * M.o3((t - 3.9) / .4); [s.bt, s.bh, ...s.bl].forEach(e => { e.style.opacity = (parseFloat(e.style.opacity) * dim).toFixed(3); });
      M.hero(s.at, t, 3.75, 9.2, { dx: 50, xo: 24 }); M.rise(s.ah, t, 3.95, 9.2); s.al.forEach((r, i) => M.slide(r, t, 4.4 + i * .14, 9.2, { dx: 40 }));
      M.pop(s.vs, t, 6.8, 9.2, { from: .2 }); s.vs.style.transform += ` rotate(${(-12 * (1 - M.os((t - 6.8) / .3))).toFixed(2)}deg)`;
    }
  });
})();
