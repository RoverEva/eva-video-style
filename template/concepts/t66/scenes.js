/* T66 Podcast 播客 · 10 s sample (illustrative copy; silent — the waveform is decorative, labelled). Episode card, progress, subscribe. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, AM = '#ffb347', INK = '#f4ecdf';
  M.setup({ bg: 'radial-gradient(ellipse at 30% 30%, #2a2433, #14121a 70%)', win: { x: 1270, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: AM, width: 6, shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['新一期播客上线', 'New episode is out'], ['聊聊：怎么开始做播客', 'How to start a podcast'], ['订阅，不错过下一期', 'Subscribe for the next one']]),
    build(L) { const s = {};
      s.cov = M.box(L, 110, 90, { width: '300px', height: '300px', borderRadius: '24px', background: 'linear-gradient(140deg,#ffb347,#ff5e62)', boxShadow: '0 20px 40px rgba(0,0,0,.4)' });
      M.svg(s.cov, 90, 60, 120, 180, `<rect x="30" y="0" width="60" height="110" rx="30" fill="#fff"/><path d="M10 80 Q10 140 60 140 Q110 140 110 80" stroke="#fff" stroke-width="10" fill="none"/><path d="M60 140 V175" stroke="#fff" stroke-width="10"/>`);
      s.ep = M.txt(L, 450, 100, f(700, 30, M.MONO), AM, 'EP.12 · PODCAST'); s.t = M.txt(L, 450, 150, f(900, 64, M.CN), INK, '怎么开始做播客'); s.e = M.txt(L, 454, 240, f('italic 700', 34, M.PF), '#b9afc4', 'How to start a podcast');
      s.wv = Array.from({ length: 42 }, (_, i) => M.box(L, 110 + i * 23, 470, { width: '14px', height: '120px', borderRadius: '7px', background: AM, transformOrigin: '50% 50%' }));
      s.wl = M.txt(L, 110, 600, f(600, 22, M.INTER), '#7d7489', '示意波形 · visual only');
      s.pb = M.box(L, 110, 650, { width: '960px', height: '10px', borderRadius: '5px', background: '#3a3344' }); s.pf = el(s.pb, 'div', '', { height: '100%', width: '0%', background: AM, borderRadius: '5px' });
      s.tc = M.txt(L, 110, 672, f(700, 24, M.MONO), '#b9afc4', '00:00 / 32:10');
      s.sub = M.txt(L, 760, 690, f(900, 44, M.CN), '#14121a', '＋ 订阅 Subscribe', { background: AM, padding: '10px 26px', borderRadius: '999px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.pop(s.cov, t, .85, 9.2, { from: .7 }); M.rise(s.ep, t, 1.05, 9.2); M.hero(s.t, t, 1.2, 9.2); M.rise(s.e, t, 1.5, 9.2);
      s.wv.forEach((b, i) => { const a = M.env(t, 3.5 + i * .015, 9.2, .3).a, h = .15 + .85 * Math.abs(Math.sin(t * 5 + i * .7) * Math.sin(t * 1.7 + i * .23)); b.style.opacity = a; b.style.transform = `scaleY(${(h * Math.min(1, M.o3((t - 3.5 - i * .015) / .3))).toFixed(3)})`; });
      M.rise(s.wl, t, 3.8, 9.2, { dy: 8 }); M.rise(s.pb, t, 3.6, 9.2, { dy: 10 }); M.rise(s.tc, t, 3.7, 9.2, { dy: 10 });
      const p = Math.max(0, (t - 3.6) / 30); s.pf.style.width = (p * 100).toFixed(2) + '%'; const sec = Math.floor(p * 1930); s.tc.textContent = `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')} / 32:10`;
      M.pop(s.sub, t, 6.85, 9.2, { from: .5 }); if (t > 7.4) s.sub.style.transform += ` scale(${(1 + .04 * Math.sin((t - 7.4) * 6)).toFixed(3)})`; } });
})();
