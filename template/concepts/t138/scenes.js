/* T138 窗口叠影 Window Overlay (beauty / mood): floral light layered over the window — never a cut-out. */
(function () { const M = K.T.mo, X = M.X, INK = '#5a4636';
  const petals = (c, n, col) => Array.from({ length: n }, (_, i) => M.svg(c, 0, 0, 60, 60, `<path d="M30 4 C 50 20, 50 40, 30 56 C 10 40, 10 20, 30 4Z" fill="${col}" opacity=".8"/>`, { transformOrigin: '50% 50%' }));
  M.story({ bg: '#f4ebe1', sbg: ['linear-gradient(#f4ebe1,#e7d6c6)', 'linear-gradient(135deg,#ffd6e0,#e8d5ff)', '#f8f1ea'], tr: ['blur', 'iris'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(720, 120, 480), M.q(1300, 140, 460, 560, 230), M.c(200, 180, 440)],
    caps: [['今天的妆，像一场花事', 'Today’s look feels like spring'], ['柔光，叠一层粉', 'Soft light, a layer of pink'], ['此刻，刚刚好', 'This moment, just right']], port: { box: [100, 60, 1820, 820] },
    scenes: [
      [c => ({ glow: M.box(c, 620, 40, { width: '680px', height: '680px', borderRadius: '50%', background: 'radial-gradient(circle,rgba(255,179,138,.6),transparent 65%)', zIndex: 2 }), p: petals(c, 14, '#ffb3c6'), t: X(c, 140, 620, 64, INK, '像一场花事', 900, M.SERIF) }),
       (s, t, a) => { s.glow.style.opacity = M.env(t, a, 99, .8).a; s.p.forEach((e, i) => { const u = ((t - a) * .18 + i / 14) % 1; e.style.opacity = M.env(t, a + i * .05, 99).a; e.style.transform = `translate(${(100 + (i * 131) % 1700 + 40 * Math.sin(t + i)).toFixed(1)}px, ${(-60 + u * 900).toFixed(1)}px) rotate(${(t * 60 + i * 30).toFixed(0)}deg)`; }); M.hero(s.t, t, a + .5, 99); }],
      [c => ({ veil: M.box(c, 1300, 140, { width: '460px', height: '560px', borderRadius: '230px', background: 'linear-gradient(160deg,rgba(255,150,190,.35),rgba(190,150,255,.25))', zIndex: 60, mixBlendMode: 'screen' }), t: X(c, 160, 300, 110, '#6b3a5a', '柔光', 900, M.SERIF), t2: X(c, 160, 460, 64, '#8a5a7a', '叠一层粉', 900, M.SERIF) }),
       (s, t, a) => { s.veil.style.display = 'none'; M.hero(s.t, t, a - .1, 99); M.hero(s.t2, t, a + .3, 99); }],
      [c => ({ sil: M.svg(c, 0, 600, 1920, 480, '<path d="M0 480 L0 260 L240 120 L420 220 L640 60 L880 200 L1120 90 L1400 230 L1680 120 L1920 200 V480Z" fill="#c9b6a6" opacity=".6"/>'), t: X(c, 800, 300, 110, INK, '此刻 · Now', 900, M.SERIF), u: M.path(c, 800, 450, 620, 30, 'M0 15 C 200 0, 400 30, 610 10', '#d98fa0', 8) }),
       (s, t, a) => { M.rise(s.sil, t, a - .1, 99, { dy: 120 }); M.hero(s.t, t, a + .2, 99); M.draw(s.u, t, a + .6, .6, 99); }]
    ] });
})();
