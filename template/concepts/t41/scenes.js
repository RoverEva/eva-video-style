/* T41 Glass Product 玻璃拟态 · 10 s concept sample (16:9). Silent; sample copy (illustrative); stat values are sample data (labelled). */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif";
  const glass = { background: 'rgba(255,255,255,.10)', border: '1.5px solid rgba(255,255,255,.35)', backdropFilter: 'blur(18px)', boxShadow: '0 20px 50px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.4)', overflow: 'hidden' };
  M.setup({
    bg: '#0c0f1f',
    win: { x: 1180, y: 140, w: 560, h: 560, r: 280, o: 1, s: 1.15 },
    ring: () => ({ color: 'rgba(255,255,255,.75)', width: 4, glow: 'rgba(160,140,255,.55)', shadow: .5 }),
    captions: [{ t0: .5, t1: 3.4, cn: '一键生成你的品牌视频', en: 'Your brand video, in one click' },
               { t0: 3.5, t1: 6.6, cn: '更快、更稳、更好看', en: 'Faster, steadier, better-looking' },
               { t0: 6.7, t1: 9.7, cn: '现在就试试', en: 'Try it now' }],
    build(L) { const s = {};
      s.orbs = [['#6c5cff', 300, 260, 620], ['#ff4fa3', 1500, 820, 700], ['#2fd1ff', 900, 120, 460]].map(([c, x, y, r]) => M.box(L, x - r / 2, y - r / 2, { width: r + 'px', height: r + 'px', borderRadius: '50%', background: c, filter: 'blur(110px)', opacity: .55 }));
      s.card = M.box(L, 110, 120, Object.assign({ width: '960px', height: '300px', borderRadius: '36px', padding: '44px 54px', boxSizing: 'border-box' }, glass));
      el(s.card, 'div', '', { font: `700 26px Inter, sans-serif`, color: '#c9c3ff', letterSpacing: '.14em' }, 'EVA STUDIO');
      el(s.card, 'div', '', { font: `900 84px ${CN}`, color: '#fff', marginTop: '10px', whiteSpace: 'nowrap' }, '一键生成品牌视频');
      el(s.card, 'div', '', { font: `500 32px Inter, sans-serif`, color: 'rgba(255,255,255,.75)', marginTop: '6px' }, 'Brand videos in one click');
      s.sheen = el(s.card, 'div', 'abs', { left: 0, top: 0, width: '220px', height: '100%', background: 'linear-gradient(100deg, transparent, rgba(255,255,255,.28), transparent)' });
      s.stats = [['3×', '更快 Faster'], ['2', '语言 Languages'], ['1', '键导出 Click']].map(([n, l], i) => { const b = M.box(L, 110 + i * 330, 460, Object.assign({ width: '300px', height: '170px', borderRadius: '28px', padding: '22px 30px', boxSizing: 'border-box' }, glass));
        el(b, 'div', '', { font: `400 76px Anton, sans-serif`, color: '#fff', lineHeight: 1 }, n); el(b, 'div', '', { font: `700 28px ${CN}`, color: 'rgba(255,255,255,.8)', marginTop: '12px' }, l); return b; });
      s.note = M.box(L, 112, 640, { font: `600 20px Inter, sans-serif`, color: 'rgba(255,255,255,.5)' }, '示例数据 · sample figures');
      s.chips = ['自动字幕', '智能剪辑', '一键导出'].map((c, i) => M.box(L, 110 + i * 250, 690, Object.assign({ font: `700 34px ${CN}`, color: '#fff', padding: '12px 28px', borderRadius: '999px' }, glass, { overflow: '' }), '✦ ' + c));
      return s; },
    update(s, t) {
      s.orbs.forEach((o, i) => { o.style.transform = `translate(${(60 * Math.sin(t * .5 + i * 2)).toFixed(1)}px, ${(40 * Math.cos(t * .4 + i)).toFixed(1)}px)`; });
      M.panel(s.card, t, .85, 9.2, { r: 36, din: .45 });
      const sh = (t - 1.6) / .9; s.sheen.style.transform = `translateX(${(-260 + 1300 * M.io(sh)).toFixed(1)}px) skewX(-12deg)`; s.sheen.style.opacity = sh > 0 && sh < 1 ? 1 : 0;
      s.stats.forEach((b, i) => M.rise(b, t, 3.6 + i * .13, 9.2, { dy: 40 })); M.rise(s.note, t, 4.1, 9.2, { dy: 8 });
      s.chips.forEach((c, i) => M.pop(c, t, 6.8 + i * .13, 9.2, { from: .6 }));
    }
  });
})();
