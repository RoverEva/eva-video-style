/* T38 Neon Night 霓虹夜店 · 10 s concept sample (16:9). Silent; sample copy (illustrative), no real venue. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el, clamp } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", PK = '#ff3fa4', CY = '#3ff0ff', YL = '#ffe14a';
  const glow = c => `0 0 6px #fff, 0 0 14px ${c}, 0 0 32px ${c}, 0 0 64px ${c}`;
  /* deterministic neon flicker: off-on-off-on then steady */
  const flick = (t, t0) => { const d = t - t0; if (d < 0) return 0; if (d > .42) return 1; return [1, 0, 1, .3, 1, 0, 1][Math.floor(d / .06)] ?? 1; };
  M.setup({
    bg: '#120c18',
    win: { x: 1200, y: 150, w: 520, h: 520, r: 260, o: 1, s: 1.15 },
    ring: t => ({ color: CY, width: 6, glow: 'rgba(63,240,255,.7)', shadow: .5 }),
    port: { box: [100, 80, 1000, 820] },
    captions: [{ t0: .5, t1: 3.4, cn: '下班了？来一碗热汤面', en: 'Off work? Grab a hot bowl of noodles' },
               { t0: 3.5, t1: 6.6, cn: '我们营业到凌晨两点', en: "We're open until 2 a.m." },
               { t0: 6.7, t1: 9.7, cn: '就在街角，等你来', en: 'Right around the corner' }],
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', backgroundImage: 'linear-gradient(rgba(0,0,0,.55) 3px, transparent 3px), linear-gradient(90deg, rgba(0,0,0,.45) 3px, transparent 3px)', backgroundSize: '120px 54px, 120px 108px', backgroundColor: '#2a1a24' }));
      s.vig = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', background: 'radial-gradient(ellipse at 35% 40%, rgba(255,63,164,.16), rgba(0,0,0,.75) 70%)' }); M.bg(s.vig);
      s.open = M.box(L, 110, 90, { font: `400 120px Anton, sans-serif`, color: '#ffe9f5', letterSpacing: '.08em', textShadow: glow(PK) }, 'OPEN LATE');
      s.name = M.box(L, 110, 250, { font: `900 120px ${CN}`, color: '#eaffff', textShadow: glow(CY) }, '深夜食堂');
      s.hrs = M.box(L, 110, 440, { font: `900 60px ${CN}`, color: '#fffbe0', padding: '14px 30px', border: `5px solid #fffbe0`, borderRadius: '16px', textShadow: glow(YL), boxShadow: `${glow(YL)}, inset 0 0 18px ${YL}` }, '营业到凌晨两点');
      s.clock = M.box(L, 110, 580, { font: `700 48px 'Space Mono', monospace`, color: YL, textShadow: glow(YL) }, '18:00 — 02:00');
      s.arr = M.box(L, 110, 690, { font: `900 64px ${CN}`, color: '#ffe9f5', textShadow: glow(PK) }, '→ 就在转角');
      s.refl = M.box(L, 110, 790, { font: `400 120px Anton, sans-serif`, color: 'rgba(255,63,164,.22)', letterSpacing: '.08em', transform: 'scaleY(-1)', filter: 'blur(4px)' }, 'OPEN LATE');
      return s; },
    update(s, t) {
      const fx = (e, t0, dy = 0) => { const f = flick(t, t0), out = 1 - M.i2((t - 8.97) / .23); e.style.opacity = (f * out).toFixed(3); e.style.transform = `translateY(${(dy * (1 - M.o3((t - t0) / .3))).toFixed(1)}px)`; };
      fx(s.open, .6); fx(s.name, 1.6, 10); s.name.style.opacity *= (.92 + .08 * Math.sin(t * 23));   /* gentle hum */
      M.panel(s.hrs, t, 3.6, 9.2, { r: 16 }); s.hrs.style.opacity *= flick(t, 3.6);
      M.rise(s.clock, t, 4.0, 9.2); fx(s.arr, 6.8, 0); s.arr.style.transform = `translateX(${(-40 * (1 - M.os((t - 6.8) / .33)) + 8 * Math.sin(t * 5) * (t > 7.2)).toFixed(1)}px)`;
      s.refl.style.opacity = (flick(t, .6) * (1 - M.i2((t - 8.97) / .23))).toFixed(3);
      s.vig.style.opacity = (.85 + .15 * Math.sin(t * 1.3)).toFixed(3);
    }
  });
})();
