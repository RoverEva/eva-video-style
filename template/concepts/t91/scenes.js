/* T91 Icon Grid 图标矩阵 · 10 s logo-only sample. Six feature tiles (generic line icons) light up in sequence; the mark lands centre. */
(function () { const C = EV, M = K.T.mo, f = M.f, B = '#00c2a8', INK = '#e9f4f2';
  const IC = { cc: '<rect x="8" y="16" width="64" height="48" rx="8"/><path d="M22 40h14M44 40h14M22 50h22"/>', cut: '<circle cx="22" cy="58" r="10"/><circle cx="58" cy="58" r="10"/><path d="M28 50 L62 10M52 50 L18 10"/>', pal: '<path d="M40 8a32 32 0 1 0 0 64c6 0 8-6 4-10s-2-10 6-10h8a14 14 0 0 0 14-14C72 20 58 8 40 8Z"/><circle cx="26" cy="32" r="4"/><circle cx="40" cy="22" r="4"/><circle cx="54" cy="30" r="4"/>', globe: '<circle cx="40" cy="40" r="30"/><path d="M10 40h60M40 10c-12 14-12 46 0 60M40 10c12 14 12 46 0 60"/>', clock: '<circle cx="40" cy="40" r="30"/><path d="M40 22v20l12 8"/>', exp: '<path d="M40 50V10M26 24 L40 10 L54 24M14 46v20h52V46"/>' };
  const T = [['cc', '自动字幕', 'Auto captions'], ['cut', '智能剪辑', 'Smart cuts'], ['pal', '品牌风格', 'Brand style'], ['globe', '中英双语', 'Bilingual'], ['clock', '几分钟出片', 'Minutes'], ['exp', '一键导出', 'One-click export']];
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 30%, #12322e, #071413 70%)', port: { box: [300, 40, 1320, 780] },
    captions: M.caps([['一个工具，六件事', 'One tool, six jobs'], ['字幕、剪辑、风格、双语……', 'Captions, cuts, style, bilingual…'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.tiles = T.map(([k, c, e], i) => { const x = 360 + (i % 3) * 420, y = 90 + (i / 3 | 0) * 330, b = M.box(L, x, y, { width: '380px', height: '290px', borderRadius: '28px', background: 'rgba(255,255,255,.05)', border: '2px solid rgba(255,255,255,.12)', boxSizing: 'border-box', transformOrigin: '50% 50%' });
        b.ic = M.svg(b, 150, 40, 80, 80, `<g fill="none" stroke="${B}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">${IC[k]}</g>`); M.txt(b, 0, 150, f(900, 46, M.CN), INK, c, { width: '380px', textAlign: 'center' }); M.txt(b, 0, 215, f(600, 24, M.INTER), '#8fb5ae', e, { width: '380px', textAlign: 'center' }); return b; });
      s.cov = M.box(L, 0, 0, { width: '1920px', height: '1080px', background: 'rgba(7,20,19,.75)' });
      s.logo = M.logo(L, 810, 210, 300, '#071413', B);
      s.name = M.txt(L, 0, 540, f(400, 56, M.AN), INK, 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.14em' });
      return s; },
    update(s, t) { s.tiles.forEach((b, i) => { M.pop(b, t, .7 + i * .12, 10.3, { from: .7 }); const on = Math.max(0, 1 - Math.abs(t - (3.6 + i * .45)) / .45);
        b.style.background = `rgba(0,194,168,${(.05 + .25 * on).toFixed(3)})`; b.style.borderColor = on > .3 ? B : 'rgba(255,255,255,.12)'; b.ic.style.transform = `scale(${(1 + .25 * on).toFixed(3)})`; });
      const c = M.env(t, 6.7, 10.3, .4); s.cov.style.opacity = c.a; M.pop(s.logo, t, 6.85, 10.3, { from: .4 }); M.rise(s.name, t, 7.1, 10.3); } });
})();
