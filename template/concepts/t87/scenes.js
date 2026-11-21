/* T87 Logo Shatter 碎片重组 · 10 s logo-only sample. Shards fly in and lock into the mark; a crack-line flash; tagline. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, Y = '#ffd23f', INK = '#111';
  const GX = 6, GY = 6, SZ = 420, X0 = 750, Y0 = 120;
  M.setup({ noface: true, bg: '#1b1b1f', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['打碎，再重组', 'Break it, rebuild it'], ['每一块，都在对的位置', 'Every piece in its place'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {}; const H = k => { const v = Math.sin(k * 78.233) * 43758.5; return v - Math.floor(v); }; const pw = SZ / GX, ph = SZ / GY;
      s.pc = []; for (let j = 0; j < GY; j++) for (let i = 0; i < GX; i++) { const k = j * GX + i, p = M.box(L, X0 + i * pw, Y0 + j * ph, { width: pw + 'px', height: ph + 'px', overflow: 'hidden', transformOrigin: '50% 50%' });
        const inner = M.box(p, -i * pw, -j * ph, { width: SZ + 'px', height: SZ + 'px', borderRadius: '100px', background: Y }); M.txt(inner, 0, 120, f(400, 150, M.AN), INK, 'EVA', { width: SZ + 'px', textAlign: 'center', lineHeight: 1 });
        p.dx = (H(k) - .5) * 1600; p.dy = (H(k + 7) - .5) * 1000; p.r = (H(k + 3) - .5) * 540; p.dl = H(k + 11) * .7; s.pc.push(p); }
      s.flash = M.box(L, X0 - 40, Y0 - 40, { width: (SZ + 80) + 'px', height: (SZ + 80) + 'px', borderRadius: '120px', boxShadow: `0 0 0 4px ${Y}, 0 0 60px ${Y}` });
      s.tag = M.txt(L, 0, 600, f(900, 56, M.CN), '#fff', '每一块，都在对的位置', { width: '1920px', textAlign: 'center' });
      s.en = M.txt(L, 0, 690, f(700, 34, M.INTER), Y, 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.2em' });
      return s; },
    update(s, t) { s.pc.forEach(p => { const u = M.os((t - .7 - p.dl) / .9), v = 1 - Math.min(1, Math.max(0, u)); p.style.opacity = (Math.min(1, Math.max(0, (t - .7 - p.dl) / .15)) * (1 - M.i2((t - 10.1) / .25))).toFixed(3);
        p.style.transform = `translate(${(p.dx * v).toFixed(1)}px, ${(p.dy * v).toFixed(1)}px) rotate(${(p.r * v).toFixed(1)}deg) scale(${(1 + .3 * v).toFixed(3)})`; });
      const fl = Math.max(0, 1 - Math.abs(t - 2.55) / .35); s.flash.style.opacity = fl.toFixed(3); s.flash.style.transform = `scale(${(1 + .1 * (1 - fl)).toFixed(3)})`;
      M.hero(s.tag, t, 3.6, 10.3, { dx: 0, dy: 24, noclip: true }); M.rise(s.en, t, 6.8, 10.3); } });
})();
