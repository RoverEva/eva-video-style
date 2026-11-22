/* T204 前后对比 Before / After slider: a draggable divider sweeps across a scene, revealing the edited look, labels follow. */
(function () { const M = K.T.mo, X = M.X, Y = '#ffd23f';
  const pane = (c, after) => { const g = M.box(c, 140, 140, { width: '1120px', height: '700px', borderRadius: '18px', overflow: 'hidden', background: after ? 'linear-gradient(135deg,#ff7e5f,#feb47b 45%,#6a82fb)' : 'linear-gradient(135deg,#8a8a8a,#b5b5b5 45%,#6f6f6f)' }); M.svg(g, 0, 380, 1120, 320, `<path d="M0 320 V200 C 200 120, 380 220, 560 140 S 900 60, 1120 150 V320Z" fill="${after ? '#2b2d6e' : '#4a4a4a'}" opacity=".85"/>`); M.box(g, 760, 120, { width: '160px', height: '160px', borderRadius: '50%', background: after ? '#fff3b0' : '#d0d0d0', boxShadow: after ? '0 0 60px #fff3b0' : 'none' }); X(g, 40, after ? 620 : 40, 48, after ? '#fff' : '#eee', after ? 'AFTER · 调色后' : 'BEFORE · 原片', 900); return g; };
  const handle = c => { const g = M.box(c, 0, 140, { width: '8px', height: '700px', background: '#fff', boxShadow: '0 0 20px rgba(0,0,0,.4)' }); M.box(g, -36, 314, { width: '80px', height: '80px', borderRadius: '50%', background: '#fff', color: '#111', font: M.f(900, 40, M.INTER), display: 'flex', alignItems: 'center', justifyContent: 'center' }, '⇆'); return g; };
  const set = (s, u) => { const x = 140 + 1120 * u; s.af.style.clipPath = `inset(0 ${(100 - 100 * u).toFixed(1)}% 0 0 round 18px)`; s.h.style.transform = `translateX(${(x - 4).toFixed(0)}px)`; };
  M.story({ bg: '#101114', sbg: ['#101114', '#131418', '#101114'], tr: ['slide', 'zoom'], ring: () => ({ color: Y, width: 6, shadow: .4 }),
    wins: [M.q(1380, 200, 420, 500, 18), M.q(1380, 200, 420, 500, 18), M.c(1420, 220, 380)],
    caps: [['先看原片', 'First, the original'], ['拉一下，就是调色后', 'Drag — and it’s graded'], ['差别，一目了然', 'The difference is obvious']], port: { box: [60, 60, 1800, 880] },
    scenes: [
      [c => ({ bf: pane(c, 0), af: pane(c, 1), h: handle(c) }), (s, t, a) => { M.rise(s.bf, t, a, 99, { dy: 60 }); s.af.style.opacity = t > a + 1.2 ? 1 : 0; set(s, .08 * M.io((t - a - 1.2) / .6)); s.h.style.opacity = t > a + 1.2 ? 1 : 0; }],
      [c => ({ bf: pane(c, 0), af: pane(c, 1), h: handle(c) }), (s, t, a) => { s.bf.style.opacity = 1; s.af.style.opacity = 1; const u = .08 + .84 * M.io((t - a) / 1.6) - .3 * M.io((t - a - 1.8) / .8) * (t > a + 1.8); set(s, u); }],
      [c => ({ bf: pane(c, 0), af: pane(c, 1), h: handle(c), t: X(c, 160, 880, 1, '#fff', '', 900) }), (s, t, a) => { s.bf.style.opacity = 1; s.af.style.opacity = 1; set(s, .5 + .45 * Math.sin((t - a) * 1.6)); }]
    ] });
})();
