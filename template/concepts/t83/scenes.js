/* T83 Logo Particles 粒子汇聚 · 10 s logo-only sample (no presenter). Particles converge on points sampled from the mark, then the mark resolves. */
(function () { const C = EV, M = K.T.mo, f = M.f, CY = '#7cf3ff', INK = '#eef6ff';
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 45%, #10233f, #050913 70%)', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['你的品牌，在这里出现', 'Your brand appears here'], ['让每条视频都好看', 'Make every video look good'], ['敬请关注', 'Stay tuned']]),
    build(L) { const s = {};
      const cv = document.createElement('canvas'); cv.width = 400; cv.height = 400; const g = cv.getContext('2d'); g.strokeStyle = '#fff'; g.lineWidth = 18; g.beginPath(); g.roundRect(20, 20, 360, 360, 90); g.stroke(); g.fillStyle = '#fff'; g.font = '150px Anton'; g.textAlign = 'center'; g.fillText('EVA', 200, 255);
      const d = g.getImageData(0, 0, 400, 400).data, pts = []; for (let y = 0; y < 400; y += 9) for (let x = 0; x < 400; x += 9) if (d[(y * 400 + x) * 4 + 3] > 128) pts.push([x, y]);
      const H = k => { const v = Math.sin(k * 91.7) * 43758.5; return v - Math.floor(v); };
      s.p = pts.map(([x, y], i) => { const e = M.box(L, 0, 0, { width: '7px', height: '7px', borderRadius: '50%', background: i % 3 ? CY : '#fff', boxShadow: `0 0 8px ${CY}` }); e.tx = 760 + x; e.ty = 130 + y; e.sx = H(i) * 1920; e.sy = H(i + .5) * 1080; e.dl = H(i + .3) * .8; return e; });
      s.logo = M.logo(L, 760, 130, 400, INK);
      s.name = M.txt(L, 0, 570, f(400, 64, M.AN), INK, 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.12em' });
      s.tag = M.txt(L, 0, 660, f(900, 48, M.CN), CY, '让每条视频都好看', { width: '1920px', textAlign: 'center' });
      s.soon = M.txt(L, 0, 740, f(700, 30, M.MONO), '#7f93b8', 'COMING SOON · 敬请关注', { width: '1920px', textAlign: 'center', letterSpacing: '.2em' });
      return s; },
    update(s, t) { const fade = 1 - M.i2((t - 3.0) / .5);
      s.p.forEach(e => { const u = M.io((t - .6 - e.dl) / 1.6), x = e.sx + (e.tx - e.sx) * u, y = e.sy + (e.ty - e.sy) * u; e.style.opacity = (Math.min(1, (t - .3) * 3) * fade).toFixed(3); e.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`; });
      M.pop(s.logo, t, 2.7, 10.3, { from: .96, din: .5 }); s.logo.style.filter = `drop-shadow(0 0 ${(20 + 10 * Math.sin(t * 3)).toFixed(0)}px rgba(124,243,255,.6))`;
      M.hero(s.name, t, 3.6, 10.3, { dx: 0, dy: 20, noclip: true }); M.rise(s.tag, t, 3.9, 10.3); M.rise(s.soon, t, 6.8, 10.3); } });
})();
