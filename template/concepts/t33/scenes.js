/* T33 Ink Wash 水墨国风 · 10 s concept sample (16:9). Silent; sample copy (illustrative).
 * Rice paper → ink blooms + drifting mountain silhouettes → vertical calligraphic title + red seal → circular window with an ink ring. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el, clamp } = C;
  const SERIF = "'Noto Serif CJK SC', 'Noto Serif CJK JP', serif", INK = '#1b1b1b';
  M.setup({
    bg: '#f2ecdf',
    win: { x: 1150, y: 150, w: 540, h: 540, r: 270, o: 1, s: 1.15 },
    ring: () => ({ color: 'rgba(27,27,27,.82)', width: 5, shadow: .18 }),
    port: { box: [120, 70, 940, 740] },
    captions: [{ t0: .5, t1: 3.4, cn: '山水之间，一杯好茶', en: 'Between mountains and water, a good tea' },
               { t0: 3.5, t1: 6.6, cn: '从采摘到冲泡，慢慢来', en: 'From picking to brewing, take it slow' },
               { t0: 6.7, t1: 9.7, cn: '慢下来，才尝得出味道', en: 'Slow down to taste it' }],
    build(L) { const s = {};
      s.blooms = [[260, 300, 520], [520, 200, 340], [1400, 760, 700]].map(([x, y, r]) => M.box(L, x - r / 2, y - r / 2, { width: r + 'px', height: r + 'px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(25,25,25,.30), rgba(25,25,25,.12) 45%, rgba(25,25,25,0) 70%)', filter: 'blur(8px)' })); s.blooms.forEach(M.bg);
      s.far = M.bg(M.svg(L, -100, 470, 2200, 420, `<path d="M0 260 C 160 150, 260 190, 380 110 C 480 40, 600 150, 720 100 C 840 50, 940 170, 1080 130 C 1240 90, 1360 200, 1520 140 C 1680 80, 1820 170, 2200 120 L2200 420 L0 420Z" fill="rgba(40,40,40,.13)"/>`));
      s.near = M.bg(M.svg(L, -100, 560, 2200, 360, `<path d="M0 230 C 150 160, 280 220, 420 170 C 540 130, 640 220, 800 190 C 980 160, 1120 240, 1300 200 C 1480 160, 1640 230, 2200 190 L2200 360 L0 360Z" fill="rgba(35,35,35,.22)"/>`));
      s.ghost = M.box(L, 520, 40, { font: `900 560px ${SERIF}`, color: 'transparent', WebkitTextStroke: '3px rgba(27,27,27,.10)', lineHeight: 1 }, '茶');
      s.chars = [...'山水之间'].map((ch, i) => M.box(L, 150, 90 + i * 150, { font: `900 136px ${SERIF}`, color: INK, lineHeight: 1 }, ch));
      s.sub = [...'一杯好茶的来历'].map((ch, i) => M.box(L, 335, 110 + i * 56, { font: `600 40px ${SERIF}`, color: '#3f3f3f', lineHeight: 1 }, ch));
      s.seal = M.box(L, 168, 700, { width: '96px', height: '96px', background: '#c0272d', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `900 52px ${SERIF}`, color: '#f6e9d6', transformOrigin: '50% 50%' }, '茶');
      s.line = M.svg(L, 450, 610, 560, 40, `<path d="M6 22 C 120 10, 300 34, 550 16" stroke="${INK}" stroke-width="9" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1 1" opacity=".85"/>`).querySelector('path');
      s.slow = M.box(L, 470, 520, { font: `900 72px ${SERIF}`, color: INK, letterSpacing: '.12em' }, '慢 · 品');
      return s; },
    update(s, t) {
      s.blooms.forEach((b, i) => { const a = [.5, .8, 3.5][i], u = M.o3((t - a) / 1.4); b.style.opacity = (u * (1 - M.i2((t - 9.0) / .4))).toFixed(3); b.style.transform = `scale(${(.3 + .7 * u).toFixed(3)})`; });
      s.far.style.transform = `translateX(${(-t * 8).toFixed(1)}px)`; s.near.style.transform = `translateX(${(-t * 16).toFixed(1)}px)`;   /* slow parallax */
      M.rise(s.ghost, t, 6.7, 9.2, { dy: 30, din: .6 }); s.ghost.style.transform += ` scale(${(1 + (t - 6.7) * .015).toFixed(4)})`;
      s.chars.forEach((c, i) => M.hero(c, t, .95 + i * .16, 9.2, { dx: 0, dy: -30, noclip: true }));   /* each stroke settles from above, blur → sharp */
      s.sub.forEach((c, i) => M.hero(c, t, 3.6 + i * .1, 9.2, { dx: 0, dy: -16, noclip: true, din: .3 }));
      const u = M.os((t - 2.3) / .28); s.seal.style.opacity = clamp((t - 2.3) / .12) * (1 - M.i2((t - 9.0) / .23)); s.seal.style.transform = `rotate(-4deg) scale(${(1.45 - .45 * u).toFixed(4)})`;   /* stamp press */
      M.hero(s.slow, t, 6.85, 9.2, { dx: -50 }); M.draw(s.line, t, 7.2, .6, 9.2);
    }
  });
})();
