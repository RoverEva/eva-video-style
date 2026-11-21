/* T90 Logo Stamp 印章盖印 · 10 s logo-only sample. Rubber stamp slams onto paper (shadow + shake), ink texture, "officially live". */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, R = '#c8202b', INK = '#2a2420';
  M.setup({ noface: true, bg: '#efe8da', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['盖个章，正式上线', 'Stamped — officially live'], ['说到做到', 'We mean it'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.paper = M.box(L, 520, 70, { width: '880px', height: '660px', background: '#fbf7ee', boxShadow: '0 18px 40px rgba(80,60,30,.2)', backgroundImage: 'repeating-linear-gradient(0deg, transparent 0 46px, rgba(120,100,70,.12) 46px 48px)' });
      s.tx = M.txt(L, 600, 120, f(700, 30, M.MONO), '#8a7d66', 'NOTICE No. 001 · 公告');
      s.st = M.box(L, 760, 170, { width: '400px', height: '400px', transformOrigin: '50% 50%' });
      M.svg(s.st, 0, 0, 400, 400, `<defs><filter id="ink"><feTurbulence baseFrequency="1.4" numOctaves="2" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.6 1.25" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs><g filter="url(#ink)"><rect x="14" y="14" width="372" height="372" rx="70" fill="none" stroke="${R}" stroke-width="16"/><rect x="40" y="40" width="320" height="320" rx="52" fill="none" stroke="${R}" stroke-width="4"/><text x="200" y="230" text-anchor="middle" font-family="Anton" font-size="140" fill="${R}">EVA</text><text x="200" y="300" text-anchor="middle" font-family="Noto Sans CJK SC" font-weight="900" font-size="40" fill="${R}">正式上线</text></g>`);
      s.sh = M.box(L, 760, 170, { width: '400px', height: '400px', borderRadius: '70px', background: 'rgba(60,40,20,.25)', filter: 'blur(30px)' });
      s.tag = M.txt(L, 0, 760, f(900, 1, M.CN), INK, '', {});
      s.d = M.txt(L, 600, 620, f(900, 46, M.CN), INK, '说到做到 · We mean it');
      return s; },
    update(s, t) { M.panel(s.paper, t, .6, 10.3, { din: .45 }); M.rise(s.tx, t, .9, 10.3);
      const u = M.i2((t - 1.4) / .35), hit = t >= 1.75, sc = hit ? 1 : 2.2 - 1.2 * u; s.st.style.opacity = t > 1.4 ? (1 - M.i2((t - 10.1) / .25)) : 0;
      s.st.style.transform = `scale(${sc.toFixed(3)}) rotate(${(-8 + (hit ? 0 : 6 * (1 - u))).toFixed(2)}deg)`; s.sh.style.opacity = t > 1.4 && !hit ? (.2 + .8 * u) : 0; s.sh.style.transform = `translate(${(40 * (1 - u)).toFixed(0)}px, ${(60 * (1 - u)).toFixed(0)}px) scale(${(sc * .9).toFixed(3)})`;
      const k = hit ? Math.exp(-(t - 1.75) * 12) * Math.sin((t - 1.75) * 60) : 0; s.paper.style.transform += ` translate(${(6 * k).toFixed(2)}px, ${(4 * k).toFixed(2)}px)`;
      M.hero(s.d, t, 3.6, 10.3); } });
})();
