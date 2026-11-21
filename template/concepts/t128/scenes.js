/* T128 激光扫描 Laser Scan (logo/text only): sweep → point cloud → mesh → shaded model. */
(function () { const M = K.T.mo, X = M.X, CY = '#7fd0ff', R = '#ff2d2d';
  const P = []; for (let i = 0; i < 420; i++) { const y = -1 + 2 * (i / 420), a = i * 2.4, r = Math.sqrt(1 - y * y) * (1 - .3 * y); P.push([960 + Math.cos(a) * r * 230, 520 + y * 300, Math.cos(a)]); }
  M.story({ noface: true, bg: '#030405', sbg: ['#030405', '#05080c', '#0a0d12'], tr: ['wipe', 'zoom'],
    caps: [['一道激光，扫过物体', 'A laser sweeps the object'], ['点连成线，线织成网', 'Points become lines, lines a mesh'], ['扫描、建网、成模型', 'Scan, mesh, model']], port: { box: [400, 100, 1120, 840] },
    scenes: [
      [c => ({ pts: P.map(([x, y, z]) => M.box(c, x, y, { width: '5px', height: '5px', borderRadius: '50%', background: z > 0 ? CY : '#2a5a7a' })), las: M.box(c, 0, 0, { width: '1920px', height: '5px', background: R, boxShadow: `0 0 24px ${R}` }), t: X(c, 100, 100, 40, CY, 'SCAN', 700, M.MONO) }),
       (s, t, a) => { const ly = 200 + 660 * ((t - a) / 2.8 % 1); s.las.style.transform = `translateY(${ly.toFixed(1)}px)`; s.pts.forEach((e, i) => { e.style.opacity = P[i][1] < ly ? 1 : 0; }); M.rise(s.t, t, a + .2, 99); }],
      [c => ({ mesh: M.svg(c, 0, 0, 1920, 1080, Array.from({ length: 12 }, (_, i) => `<ellipse cx="960" cy="520" rx="${230 * Math.sin((i + .5) / 12 * Math.PI)}" ry="${24}" transform="translate(0 ${-300 + (i + .5) * 50})" fill="none" stroke="${CY}" stroke-width="2" pathLength="1" stroke-dasharray="1 1"/>`).join('') + Array.from({ length: 10 }, (_, i) => `<ellipse cx="960" cy="520" rx="${230 * Math.abs(Math.cos(i * .314))}" ry="300" fill="none" stroke="${CY}" stroke-width="2" opacity=".6" pathLength="1" stroke-dasharray="1 1"/>`).join('')), t: X(c, 100, 100, 40, CY, 'MESH', 700, M.MONO) }),
       (s, t, a) => { [...s.mesh.querySelectorAll('ellipse')].forEach((p, i) => M.draw(p, t, a - .1 + i * .06, .6, 99)); M.rise(s.t, t, a + .2, 99); }],
      [c => ({ obj: M.box(c, 730, 220, { width: '460px', height: '600px', borderRadius: '50% 50% 46% 46% / 40% 40% 60% 60%', background: 'radial-gradient(circle at 35% 30%, #cfe8ff, #4a7ea6 45%, #12263a 80%)', boxShadow: '0 40px 80px rgba(0,0,0,.6)' }), t: X(c, 100, 100, 40, CY, 'MODEL', 700, M.MONO), tt: X(c, 100, 880, 52, '#fff', 'SCAN → MESH → MODEL', 400, M.AN) }),
       (s, t, a) => { M.pop(s.obj, t, a - .1, 99, { from: .8 }); s.obj.style.transform += ` rotateY(${(20 * Math.sin(t)).toFixed(1)}deg)`; M.rise(s.t, t, a + .2, 99); M.hero(s.tt, t, a + .5, 99); }]
    ] });
})();
