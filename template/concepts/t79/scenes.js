/* T79 Glitch 故障风 · 10 s sample (illustrative copy). RGB split + slice displacement bursts (deterministic), scanlines, update progress. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, CY = '#00f0ff', MG = '#ff2bd6';
  const H = x => { const s = Math.sin(x * 127.1) * 43758.5453; return s - Math.floor(s); };
  const burst = t => [1.0, 3.5, 6.7].reduce((a, b) => Math.max(a, Math.max(0, 1 - Math.abs(t - b) / .22)), 0);
  const gl = (p, x, y, font, txt) => { const g = M.box(p, x, y, {}); g.r = M.txt(g, 0, 0, font, MG, txt, { mixBlendMode: 'screen' }); g.c = M.txt(g, 0, 0, font, CY, txt, { mixBlendMode: 'screen' }); g.w = M.txt(g, 0, 0, font, '#fff', txt, { mixBlendMode: 'screen' }); return g; };
  const jit = (g, t, k) => { const b = burst(t), n = Math.floor(t * 30); const dx = b * 22 * (H(n + k) - .5) * 2; g.r.style.transform = `translate(${(-4 - dx).toFixed(1)}px,0)`; g.c.style.transform = `translate(${(4 + dx).toFixed(1)}px,0)`;
    const y0 = (H(n * 3 + k) * 100).toFixed(1), h = (8 + 20 * H(n * 7 + k)).toFixed(1); g.w.style.clipPath = b > .05 ? `inset(${y0}% 0 ${Math.max(0, 100 - y0 - h).toFixed(1)}% 0)` : ''; g.w.style.transform = b > .05 ? `translateX(${(40 * b * (H(n + 9) - .5)).toFixed(1)}px)` : ''; };
  M.setup({ bg: '#05060a', win: { x: 1260, y: 150, w: 500, h: 560, r: 16, o: 1, s: 1.15 }, ring: t => ({ color: burst(t) > .3 ? MG : CY, width: 4, glow: 'rgba(0,240,255,.5)', shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['系统升级中……', 'System updating…'], ['新功能：自动双语字幕', 'New: automatic bilingual captions'], ['升级完成', 'Update complete']]),
    build(L) { const s = {};
      s.sl = M.bg(M.box(L, 0, 0, { width: '1920px', height: '1080px', backgroundImage: 'repeating-linear-gradient(0deg, rgba(255,255,255,.04) 0 2px, transparent 2px 5px)', pointerEvents: 'none' }));
      s.a = gl(L, 110, 90, f(400, 140, M.AN), 'SYSTEM UPDATE'); s.b = gl(L, 110, 260, f(900, 80, M.CN), '系统升级中……');
      s.c = gl(L, 110, 400, f(900, 64, M.CN), '新功能：自动双语字幕'); s.c2 = M.txt(L, 114, 490, f(700, 30, M.MONO), CY, '> feature: bilingual_captions = ON');
      s.pb = M.box(L, 110, 620, { width: '900px', height: '30px', border: `3px solid ${CY}`, boxSizing: 'border-box' }); s.pf = el(s.pb, 'div', '', { height: '100%', width: '0%', background: CY });
      s.pt = M.txt(L, 110, 670, f(700, 40, M.MONO), '#fff', '0%');
      return s; },
    update(s, t) { [[s.a, .9, 9.2], [s.b, 1.2, 9.2], [s.c, 3.55, 9.2]].forEach(([g, a, b], k) => { const v = M.env(t, a, b, .2); g.style.opacity = v.a; jit(g, t, k); });
      M.rise(s.c2, t, 3.9, 9.2, { dy: 8 }); if (t > 3.9) M.type(s.c2, '> feature: bilingual_captions = ON', t, 3.9, 1.0, true);
      M.rise(s.pb, t, 1.5, 9.2, { dy: 10 }); M.rise(s.pt, t, 1.6, 9.2, { dy: 10 });
      const p = t < 6.7 ? 68 * M.o3((t - 1.6) / 4.5) : 68 + 32 * M.o3((t - 6.7) / .7); s.pf.style.width = p.toFixed(1) + '%'; s.pt.textContent = t > 7.4 ? '100% · 升级完成 COMPLETE' : Math.round(p) + '%';
      s.sl.style.transform = `translateY(${((t * 60) % 5).toFixed(1)}px)`; } });
})();
