/* T30 Blueprint 蓝图工程 · 10 s concept sample (16:9) on the Eva raw clip. Silent; sample copy (illustrative).
 * Blueprint grid → line drawing (stroke by stroke) → circular presenter window with a cyan ring and a dimension mark. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CY = '#7fd0ff', YEL = '#ffd36b', MONO = "'Space Mono', monospace", CN = "'Noto Sans CJK SC', sans-serif";
  M.setup({
    bg: '#0b3a6e',
    win: { x: 1240, y: 150, w: 520, h: 520, r: 260, o: 1, s: 1.15 },
    ring: () => ({ color: CY, width: 6, glow: 'rgba(127,208,255,.45)', shadow: .4 }),
    port: { box: [90, 80, 1080, 720] },
    captions: [{ t0: .5, t1: 3.4, cn: '三步，从原始素材到成片', en: 'Three steps from raw clip to final cut' },
               { t0: 3.5, t1: 6.6, cn: '上传、选风格、导出', en: 'Upload, pick a style, export' },
               { t0: 6.7, t1: 9.7, cn: '每一步都清清楚楚', en: 'Every step, crystal clear' }],
    build(L) { const s = {};
      s.grid = M.bg(el(L, 'div', 'abs', { left: '-96px', top: '-96px', width: (C.W + 192) + 'px', height: (C.H + 192) + 'px',
        backgroundImage: 'linear-gradient(rgba(140,200,255,.17) 2px, transparent 2px), linear-gradient(90deg, rgba(140,200,255,.17) 2px, transparent 2px), linear-gradient(rgba(140,200,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(140,200,255,.07) 1px, transparent 1px)',
        backgroundSize: '96px 96px, 96px 96px, 24px 24px, 24px 24px' }));
      s.ghost = M.box(L, 96, 380, { font: `900 230px Inter, sans-serif`, color: 'transparent', WebkitTextStroke: '2px rgba(127,208,255,.35)', letterSpacing: '-.02em', whiteSpace: 'nowrap' }, 'BLUEPRINT');
      s.cue = M.box(L, 110, 92, { font: `700 26px ${MONO}`, color: CY, letterSpacing: '.14em' }, 'SHEET 01 / HOW IT WORKS');
      s.hero = M.box(L, 106, 134, { font: `900 104px ${CN}`, color: '#f5faff', letterSpacing: '-.01em', whiteSpace: 'nowrap' }, '三步完成剪辑');
      s.rule = M.svg(L, 110, 262, 640, 12, `<path d="M0 6H620" stroke="url(#g30)" stroke-width="6" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/><defs><linearGradient id="g30"><stop offset="0" stop-color="${CY}"/><stop offset="1" stop-color="#b778ff"/></linearGradient></defs>`).querySelector('path');
      /* diagram: three boxes, arrows, labels */
      s.d = M.svg(L, 110, 340, 1040, 420, `
        <g fill="none" stroke="${CY}" stroke-width="3">
          <rect class="b" x="0" y="20" width="260" height="170" rx="12" pathLength="1" stroke-dasharray="1 1"/>
          <rect class="b" x="380" y="20" width="260" height="170" rx="12" pathLength="1" stroke-dasharray="1 1"/>
          <rect class="b" x="760" y="20" width="260" height="170" rx="12" pathLength="1" stroke-dasharray="1 1"/>
          <path class="a" d="M262 105H376" stroke-dasharray="1 1" pathLength="1"/><path class="a" d="M642 105H756" stroke-dasharray="1 1" pathLength="1"/>
          <path class="dim" d="M0 300H1020M0 286v28M1020 286v28" stroke="${YEL}" pathLength="1" stroke-dasharray="1 1"/>
          <path class="tk" d="M130 190v96M510 190v96M890 190v96" stroke-dasharray="1 1" pathLength="1" stroke-opacity=".6"/>
        </g>`);
      s.boxes = [...s.d.querySelectorAll('.b')]; s.arrows = [...s.d.querySelectorAll('.a')]; s.dim = s.d.querySelector('.dim'); s.ticks = s.d.querySelector('.tk');
      s.labels = [['01', '上传', 'UPLOAD'], ['02', '选风格', 'STYLE'], ['03', '导出', 'EXPORT']].map(([n, cn, en], i) => { const g = M.box(L, 110 + 380 * i + 26, 382, {});
        el(g, 'div', '', { font: `700 22px ${MONO}`, color: YEL }, n); el(g, 'div', '', { font: `900 54px ${CN}`, color: '#ffffff', lineHeight: 1.15 }, cn); el(g, 'div', '', { font: `700 20px ${MONO}`, color: CY, letterSpacing: '.12em' }, en); return g; });
      s.dl = M.box(L, 520, 610, { font: `700 26px ${CN}`, color: YEL, background: '#0b3a6e', padding: '0 14px' }, '每一步 · 都清楚');
      s.mark = M.att(M.svg(L, 1210, 120, 580, 580, `<g stroke="${YEL}" stroke-width="3"><path d="M290 0v30M290 550v30M0 290h30M550 290h30"/></g><text x="420" y="36" font-family="Space Mono, monospace" font-size="22" fill="${CY}">Ø 520</text>`));
      return s; },
    update(s, t) {
      s.grid.style.transform = `translate(${(-t * 6).toFixed(1)}px, ${(-t * 3).toFixed(1)}px)`;   /* slow drift: depth, not subject */
      M.slide(s.ghost, t, 1.1, 3.75, { dx: -120, din: .5 }); s.ghost.style.transform += ` translateX(${(-(t - 1.1) * 14).toFixed(1)}px)`;   /* outline motif: scale/depth, hands over to the diagram */
      M.rise(s.cue, t, .8, 9.2, { dy: 16 });
      M.hero(s.hero, t, .95, 9.2);
      M.draw(s.rule, t, 1.3, .5, 9.2);
      s.boxes.forEach((b, i) => M.draw(b, t, 3.55 + i * .42, .5, 9.2));
      s.arrows.forEach((a, i) => M.draw(a, t, 4.0 + i * .42, .3, 9.2));
      s.labels.forEach((g, i) => M.rise(g, t, 3.75 + i * .42, 9.2, { dy: 24 }));
      M.draw(s.ticks, t, 6.75, .4, 9.2); M.draw(s.dim, t, 6.95, .6, 9.2); M.pop(s.dl, t, 7.45, 9.2, { from: .7 });
      M.pop(s.mark, t, 1.05, 9.15, { from: .85 });
      s.boxes.forEach((b, i) => { const k = Math.max(0, 1 - Math.abs(t - (7.9 + i * .35)) / .3); b.setAttribute('stroke-width', (3 + 3 * k).toFixed(2)); });   /* step highlight sweep */
    }
  });
})();
