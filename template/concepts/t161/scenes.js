/* T161 深境舞台 Deep Stage: perspective floor grid rushes forward, side panels, glow strip. */
(function () { const M = K.T.mo, X = M.X, GD = '#ffc94a';
  const floor = c => M.svg(c, 0, 540, 1920, 540, Array.from({ length: 25 }, (_, i) => `<line x1="960" y1="0" x2="${-1500 + i * 205}" y2="540" stroke="${GD}" stroke-opacity=".35" stroke-width="2"/>`).join('') + '<g class="h"></g>');
  const hl = (f, t) => { const g = f.querySelector('.h'); g.innerHTML = Array.from({ length: 8 }, (_, i) => { const u = ((i / 8 + t * .25) % 1), y = 540 * u * u; return `<line x1="0" y1="${y.toFixed(1)}" x2="1920" y2="${y.toFixed(1)}" stroke="${GD}" stroke-opacity="${(.15 + .5 * u).toFixed(2)}" stroke-width="2"/>`; }).join(''); };
  const panels = c => [[300, 200, 180, 160], [1440, 200, 180, 160], [520, 150, 220, 200], [1180, 150, 220, 200]].map(([x, y, w, h]) => M.box(c, x, y, { width: w + 'px', height: h + 'px', border: `3px solid ${GD}`, background: 'rgba(255,201,74,.05)', boxShadow: `0 0 20px rgba(255,201,74,.2)` }));
  M.story({ bg: '#050507', sbg: ['#050507', '#060609', '#050507'], tr: ['zoom', 'zoom'], ring: () => ({ color: GD, width: 5, glow: 'rgba(255,201,74,.5)', shadow: .5 }),
    wins: [M.q(760, 120, 400, 420, 10, 1.1), M.q(160, 180, 440, 480, 10), M.q(760, 100, 400, 420, 10, 1.1)],
    caps: [['走进一个更深的舞台', 'Step onto a deeper stage'], ['三个场景，一个故事', 'Three scenes, one story'], ['DEEP STAGE', 'Deep Stage']], port: { box: [100, 40, 1720, 960] },
    scenes: [
      [c => ({ f: floor(c), p: panels(c), glow: M.box(c, 260, 520, { width: '1400px', height: '40px', borderRadius: '50%', background: GD, filter: 'blur(26px)' }) }),
       (s, t, a) => { hl(s.f, t); s.f.style.opacity = M.env(t, a, 99, .6).a; s.p.forEach((e, i) => M.pop(e, t, a + .3 + i * .1, 99, { from: .5 })); s.glow.style.opacity = M.env(t, a + .5, 99).a * (.6 + .3 * Math.sin(t * 3)); }],
      [c => ({ f: floor(c), sc: ['01 起', '02 承', '03 合'].map((n, i) => { const b = M.box(c, 760 + i * 380, 220, { width: '320px', height: '380px', border: `3px solid ${GD}`, background: 'rgba(255,201,74,.06)', color: GD, font: M.f(900, 60), display: 'flex', alignItems: 'flex-end', padding: '24px', boxSizing: 'border-box' }, n); return b; }) }),
       (s, t, a) => { hl(s.f, t); s.f.style.opacity = 1; s.sc.forEach((b, i) => { M.pop(b, t, a - .1 + i * .2, 99, { from: .3 }); b.style.transform += ` perspective(800px) rotateY(${(-20 + i * 10)}deg)`; }); }],
      [c => ({ f: floor(c), p: panels(c), t: X(c, 560, 640, 120, GD, 'DEEP STAGE', 400, M.AN, { letterSpacing: '.08em', textShadow: `0 0 30px rgba(255,201,74,.6)` }) }),
       (s, t, a) => { hl(s.f, t); s.f.style.opacity = 1; s.p.forEach(e => { e.style.opacity = 1; }); M.hero(s.t, t, a + .3, 99); }]
    ] });
})();
