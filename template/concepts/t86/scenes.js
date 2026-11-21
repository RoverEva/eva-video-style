/* T86 Logo Light Sweep 金属扫光 · 10 s logo-only sample. Brushed-metal wordmark; a specular band sweeps across; lens glint. */
(function () { const C = EV, M = K.T.mo, f = M.f;
  const metal = { backgroundImage: 'linear-gradient(180deg,#f5f7fa 0%,#b9c0ca 38%,#6b7480 50%,#d8dde3 62%,#8f98a3 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' };
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 40%, #232831, #07080b 70%)', port: { box: [300, 40, 1320, 780] },
    captions: M.caps([['质感，从第一眼开始', 'Quality from the first look'], ['专业，但不复杂', 'Professional, not complicated'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.w = M.txt(L, 0, 170, f(400, 300, M.AN), '', 'EVA', Object.assign({ width: '1920px', textAlign: 'center', letterSpacing: '.06em', lineHeight: 1, filter: 'drop-shadow(0 18px 30px rgba(0,0,0,.6))' }, metal));
      s.sh = M.txt(L, 0, 170, f(400, 300, M.AN), '', 'EVA', { width: '1920px', textAlign: 'center', letterSpacing: '.06em', lineHeight: 1, backgroundImage: 'linear-gradient(105deg, transparent 42%, rgba(255,255,255,.95) 50%, transparent 58%)', backgroundSize: '300% 100%', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' });
      s.line = M.box(L, 660, 510, { width: '600px', height: '2px', background: 'linear-gradient(90deg, transparent, #c9d0da, transparent)' });
      s.sub = M.txt(L, 0, 540, f(700, 40, M.INTER), '#c9d0da', 'VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.5em' });
      s.cn = M.txt(L, 0, 640, f(900, 50, M.CN), '#e8ecf1', '专业，但不复杂', { width: '1920px', textAlign: 'center' });
      s.glint = M.svg(L, 1180, 150, 120, 120, '<path d="M60 0 L66 54 L120 60 L66 66 L60 120 L54 66 L0 60 L54 54Z" fill="#fff"/>', { transformOrigin: '50% 50%', filter: 'drop-shadow(0 0 12px #fff)' });
      return s; },
    update(s, t) { M.hero(s.w, t, .7, 10.3, { dx: 0, dy: 30, noclip: true, din: .6 }); const sw = (t - 1.6) / 1.1, sw2 = (t - 6.7) / 1.1;
      s.sh.style.opacity = (sw > 0 && sw < 1) || (sw2 > 0 && sw2 < 1) ? 1 : 0; s.sh.style.backgroundPosition = `${(100 - 100 * M.io(sw > 0 && sw < 1 ? sw : sw2)).toFixed(1)}% 0`;
      const g = Math.max(0, 1 - Math.abs(t - 2.5) / .3); s.glint.style.opacity = g; s.glint.style.transform = `scale(${(.3 + g).toFixed(3)}) rotate(${(t * 90).toFixed(0)}deg)`;
      const lu = M.o5((t - 3.5) / .6); s.line.style.transform = `scaleX(${lu.toFixed(3)})`; s.line.style.opacity = t > 3.5 ? 1 - M.i2((t - 10.1) / .25) : 0;
      M.rise(s.sub, t, 3.7, 10.3, { dy: 14 }); M.rise(s.cn, t, 4.0, 10.3); } });
})();
