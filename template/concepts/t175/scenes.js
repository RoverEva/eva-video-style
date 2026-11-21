/* T175 粒子变形 Particle Morph (logo/text only): 600 points morph sphere → torus → helix → EVA wordmark. */
(function () { const M = K.T.mo, X = M.X, CY = '#8fd3ff', N = 600;
  const sph = i => { const y = 1 - 2 * (i + .5) / N, r = Math.sqrt(1 - y * y), th = i * 2.39996; return [Math.cos(th) * r, y, Math.sin(th) * r]; };
  const tor = i => { const u = i / N * 6.2832 * 1, v = i * .37; return [(1 + .4 * Math.cos(v)) * Math.cos(u) * .8, .4 * Math.sin(v) * .8, (1 + .4 * Math.cos(v)) * Math.sin(u) * .8]; };
  const hel = i => { const u = i / N; return [Math.cos(u * 25) * .5, 1.6 * u - .8, Math.sin(u * 25) * .5]; };
  const wm = (() => { const cv = document.createElement('canvas'); cv.width = 300; cv.height = 120; const g = cv.getContext('2d'); g.font = '900 110px Inter, sans-serif'; g.fillStyle = '#fff'; g.textAlign = 'center'; g.fillText('EVA', 150, 100); const d = g.getImageData(0, 0, 300, 120).data, P = []; for (let y = 0; y < 120; y += 3) for (let x = 0; x < 300; x += 3) if (d[(y * 300 + x) * 4 + 3] > 128) P.push([(x - 150) / 110, (y - 60) / 110, 0]); return i => P[Math.floor(i * P.length / N)]; })();
  const SH = [sph, tor, hel, wm];
  const cloud = c => Array.from({ length: N }, () => M.box(c, 0, 0, { width: '6px', height: '6px', borderRadius: '50%', background: CY }));
  const place = (L, A, B, u, t) => L.forEach((e, i) => { const p = A(i), q = B(i), k = M.io(u + (i % 37) / 400 - .05); let x = p[0] + (q[0] - p[0]) * k, y = p[1] + (q[1] - p[1]) * k, z = p[2] + (q[2] - p[2]) * k; const r = t * .6 * (B === wm && k > .95 ? 0 : 1), cx = x * Math.cos(r) + z * Math.sin(r), cz = -x * Math.sin(r) + z * Math.cos(r); e.style.transform = `translate(${(960 + cx * 330).toFixed(1)}px, ${(520 + y * 330).toFixed(1)}px) scale(${(1 + .6 * cz).toFixed(2)})`; e.style.opacity = (.45 + .55 * (cz + 1) / 2).toFixed(2); });
  M.story({ noface: true, bg: '#03040a', sbg: ['#03040a', '#04060e', '#03040a'], tr: ['blur', 'zoom'],
    caps: [['六百个点，先聚成球', '600 points form a sphere'], ['再拉成环，拧成螺旋', 'Then a ring, then a helix'], ['最后，变成名字', 'And finally, a name']], port: { box: [400, 80, 1120, 860] },
    scenes: [
      [c => ({ p: cloud(c), t: X(c, 100, 80, 40, CY, 'SPHERE', 700, M.MONO) }), (s, t, a) => { place(s.p, i => [Math.sin(i * 7.1) * 2.5, Math.cos(i * 3.3) * 1.6, Math.sin(i)], sph, (t - a) / 1.6, t); M.rise(s.t, t, a + .2, 99); }],
      [c => ({ p: cloud(c), t: X(c, 100, 80, 40, CY, 'SPHERE → TORUS → HELIX', 700, M.MONO) }), (s, t, a) => { const u = (t - a) / 1.3; if (u < 1.2) place(s.p, sph, tor, u, t); else place(s.p, tor, hel, u - 1.2, t); M.rise(s.t, t, a, 99); }],
      [c => ({ p: cloud(c), t: X(c, 100, 80, 40, CY, '→ EVA', 700, M.MONO) }), (s, t, a) => { place(s.p, hel, wm, (t - a) / 1.4, t); M.rise(s.t, t, a, 99); }]
    ] });
})();
