/* T36 Pixel Game 像素游戏 · 10 s concept sample (16:9). Silent; sample copy (illustrative). Pixel text is canvas-thresholded (nearest-neighbour). */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", Y = '#ffd84a', G = '#5cf08a', PK = '#ff4fa3', DK = '#120e26';
  M.setup({
    bg: '#1b1638',
    win: { x: 1220, y: 170, w: 520, h: 520, r: 18, o: 1, s: 1.15 },
    ring: () => ({ color: '#ffffff', width: 8, shadow: .5 }),
    captions: [{ t0: .5, t1: 3.4, cn: '剪辑升级之路：第三关', en: 'Editing quest: level three' },
               { t0: 3.5, t1: 6.6, cn: '任务：给视频加上字幕', en: 'Mission: add captions to the video' },
               { t0: 6.7, t1: 9.7, cn: '完成！经验值满格', en: 'Cleared! XP bar full' }],
    build(L) { const s = {};
      el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', backgroundImage: 'linear-gradient(rgba(255,255,255,.05) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.05) 2px, transparent 2px)', backgroundSize: '40px 40px' });
      s.stars = Array.from({ length: 26 }, (_, i) => M.box(L, (i * 397) % 1880, (i * 211) % 760, { width: '8px', height: '8px', background: i % 3 ? '#8c86c9' : Y }));
      s.border = M.box(L, 1196, 146, { width: '568px', height: '568px', border: `8px solid ${PK}`, borderRadius: '6px', boxSizing: 'border-box', boxShadow: `8px 8px 0 ${DK}` });
      s.lv = M.pix(L, 'LV 3', 110, 90, 8, Y, DK);
      s.xpb = M.box(L, 110, 210, { width: '620px', height: '48px', border: '6px solid #fff', background: DK, boxSizing: 'border-box' });
      s.xpf = el(s.xpb, 'div', '', { height: '100%', width: '0%', background: G });
      s.xpt = M.pix(L, 'XP 40%', 760, 208, 4, '#fff');
      s.stage = M.box(L, 110, 300, { font: `900 92px ${CN}`, color: '#fff', textShadow: `6px 6px 0 ${PK}` }, '第三关：加字幕');
      s.dlg = M.box(L, 110, 470, { width: '1000px', height: '210px', background: DK, border: '6px solid #fff', boxShadow: `8px 8px 0 #000`, padding: '24px 30px', boxSizing: 'border-box' });
      s.dn = el(s.dlg, 'div', '', { font: `700 26px 'Space Mono', monospace`, color: Y }, '> EVA:');
      s.dt = el(s.dlg, 'div', '', { font: `700 48px ${CN}`, color: '#fff', marginTop: '10px', minHeight: '60px' });
      s.de = el(s.dlg, 'div', '', { font: `600 26px Inter, sans-serif`, color: '#bdb8e8', marginTop: '6px' });
      s.up = M.pix(L, 'LEVEL UP!', 250, 300, 12, Y, PK);
      s.coins = [0, 1, 2].map(i => M.box(L, 820 + i * 90, 720, { width: '56px', height: '56px', background: Y, border: `6px solid #b8860b`, borderRadius: '50%', boxSizing: 'border-box', font: `700 22px 'Space Mono', monospace`, color: '#6b4c00', display: 'flex', alignItems: 'center', justifyContent: 'center' }, '+10'));
      return s; },
    update(s, t) {
      s.stars.forEach((e, i) => { e.style.opacity = (.35 + .65 * (Math.sin(t * 3 + i) > .4 ? 1 : 0)) * M.env(t, .6, 9.3).a; });
      M.pop(s.border, t, .75, 9.15, { from: .9 });
      const step = u => Math.floor(u * 4) / 4;   /* pixel motion: 4-step entrances feel like sprites */
      const pv = M.env(t, .9, 9.2, .25); s.lv.style.opacity = pv.a; s.lv.style.transform = `translateY(${(-40 * (1 - step(M.o3((t - .9) / .25)))).toFixed(0)}px)`;
      M.slide(s.xpb, t, 1.1, 9.2, { dx: -60 }); M.slide(s.xpt, t, 1.2, 9.2, { dx: -30 });
      const xp = t < 6.8 ? 40 * M.o3((t - 1.3) / .8) : 40 + 60 * M.o3((t - 6.8) / .6);
      s.xpf.style.width = xp.toFixed(1) + '%'; s.xpf.style.background = xp > 99 ? Y : G;
      s.xpt.style.visibility = t < 6.8 ? '' : 'hidden';
      M.hero(s.stage, t, 1.6, 7.25, { dx: -50 });
      M.panel(s.dlg, t, 3.4, 9.2, { din: .3 });
      M.type(s.dt, '把字幕放进视频里……', t, 3.65, 1.3, true); M.type(s.de, 'Put captions into the video…', t, 3.9, 1.3);
      const on = t > 7.35 && t < 9.2; s.up.style.opacity = on ? ((Math.floor((t - 7.35) * 6) % 2 && t < 7.9) ? .25 : 1) * (1 - M.i2((t - 8.97) / .23)) : 0;
      s.up.style.transform = `scale(${(.6 + .4 * step(M.o3((t - 7.35) / .25))).toFixed(3)})`;
      s.coins.forEach((c, i) => { const a = 7.6 + i * .13; M.pop(c, t, a, 9.2, { from: .3 }); c.style.transform += ` translateY(${(-26 * Math.max(0, Math.sin(Math.min(Math.PI, (t - a) * 6)))).toFixed(1)}px)`; });
    }
  });
})();
