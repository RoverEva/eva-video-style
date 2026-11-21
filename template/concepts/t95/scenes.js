/* T95 Phone Mockup 手机演示 · 10 s sample. Generic phone frame; the screen is a clearly-labelled PLACEHOLDER for the user's own screen recording (no invented app UI). */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, INK = '#16202c', B = '#3a7bff';
  M.setup({ noface: true, bg: 'linear-gradient(160deg,#eef3fb,#dde6f3)', port: { box: [300, 40, 1320, 780] },
    captions: M.caps([['三步上手', 'Get started in three steps'], ['打开、选模板、导出', 'Open, pick a template, export'], ['就这么简单', "That's it"]]),
    build(L) { const s = {};
      s.ph = M.box(L, 360, 60, { width: '380px', height: '760px', borderRadius: '56px', background: '#111', boxShadow: '0 30px 60px rgba(20,40,80,.3)', padding: '18px', boxSizing: 'border-box' });
      s.sc = el(s.ph, 'div', '', { width: '344px', height: '724px', borderRadius: '40px', overflow: 'hidden', position: 'relative', background: 'repeating-linear-gradient(135deg,#d9e1ec 0 18px,#cfd8e5 18px 36px)' });
      el(s.sc, 'div', 'abs', { left: '122px', top: '16px', width: '100px', height: '26px', borderRadius: '13px', background: '#111' });
      s.feed = el(s.sc, 'div', 'abs', { left: '24px', top: '80px', width: '296px' }); for (let i = 0; i < 9; i++) el(s.feed, 'div', '', { height: i % 3 ? '22px' : '150px', margin: '0 0 18px', borderRadius: '12px', background: i % 3 ? 'rgba(255,255,255,.7)' : 'rgba(255,255,255,.5)', width: i % 3 ? (60 + (i * 13) % 40) + '%' : '100%' });
      s.lbl = M.box(L, 400, 360, { width: '300px', textAlign: 'center', background: 'rgba(22,32,44,.85)', color: '#fff', borderRadius: '16px', padding: '16px 10px', font: f(700, 28, M.CN) }, '你的录屏放这里'); M.txt(s.lbl, 0, 0, f(600, 20, M.INTER), '#c9d4e5', 'YOUR SCREEN RECORDING', { position: 'static', marginTop: '6px', letterSpacing: '.1em' });
      s.tap = M.box(L, 0, 0, { width: '80px', height: '80px', borderRadius: '50%', border: `5px solid ${B}`, boxSizing: 'border-box' });
      s.steps = [['1', '打开', 'Open'], ['2', '选模板', 'Pick a template'], ['3', '导出', 'Export']].map(([n, c, e], i) => { const g = M.box(L, 860, 180 + i * 170, {}); M.txt(g, 0, 0, f(400, 90, M.AN), B, n); M.txt(g, 90, 10, f(900, 54, M.CN), INK, c); M.txt(g, 92, 82, f(600, 26, M.INTER), '#6a7a90', e); return g; });
      s.ok = M.txt(L, 860, 690, f(900, 50, M.CN), '#fff', '就这么简单 ✓', { background: B, padding: '8px 26px', borderRadius: '16px' });
      return s; },
    update(s, t) { M.rise(s.ph, t, .6, 10.3, { dy: 80 }); s.feed.style.transform = `translateY(${(-Math.max(0, t - 1.5) * 30).toFixed(1)}px)`; M.pop(s.lbl, t, 1.2, 10.3, { from: .7 });
      const TP = [[540, 300, 3.7], [520, 520, 4.7], [560, 700, 5.7]]; let on = null; TP.forEach(p => { if (t >= p[2] && t < p[2] + .6) on = p; });
      if (on) { const d = (t - on[2]) / .6; s.tap.style.opacity = (1 - d).toFixed(3); s.tap.style.transform = `translate(${on[0] - 40}px, ${on[1] - 40}px) scale(${(.4 + 1.2 * M.o3(d)).toFixed(3)})`; } else s.tap.style.opacity = 0;
      s.steps.forEach((g, i) => M.slide(g, t, 3.6 + i * 1.0, 10.3, { dx: 60 })); M.pop(s.ok, t, 6.85, 10.3, { from: .5 }); } });
})();
