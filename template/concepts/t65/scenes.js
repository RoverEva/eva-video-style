/* T65 Live Shopping 直播带货 · 10 s sample. Generic live badge (no real platform UI), viewer counter, comments, product card, 3-2-1. Numbers/comments are SAMPLE. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, PK = '#ff2d6f', INK = '#22122a';
  M.setup({ bg: 'linear-gradient(160deg,#ffe3ee,#ffc2d8)', win: { x: 1240, y: 110, w: 480, h: 660, r: 30, o: 1, s: 1.15 }, ring: () => ({ color: PK, width: 8, shadow: .3 }), port: { box: [90, 30, 1080, 790] },
    captions: M.caps([['直播开始啦', "We're live"], ['今天的好物，看这里', "Today's pick — right here"], ['三、二、一，上链接（示例）', '3, 2, 1 — link’s up (sample)']]),
    build(L) { const s = {};
      s.live = M.box(L, 110, 70, { display: 'flex', alignItems: 'center', gap: '14px', background: PK, padding: '8px 22px', borderRadius: '10px' }); s.dot = el(s.live, 'div', '', { width: '18px', height: '18px', borderRadius: '50%', background: '#fff' }); el(s.live, 'div', '', { font: f(400, 40, M.AN), color: '#fff', letterSpacing: '.06em' }, 'LIVE');
      s.view = M.txt(L, 320, 82, f(700, 32, M.INTER), INK, '👀 0 · 示例 SAMPLE');
      s.t = M.txt(L, 110, 160, f(900, 84, M.CN), INK, '今日好物 · 直播间');
      s.cm = [['小鹿', '主播今天好美！'], ['阿杰', '求链接 🙏'], ['Momo', '多少钱呀'], ['小林', '已下单 ✓']].map(([n, c]) => M.txt(L, 110, 0, f(700, 32, M.CN), '#fff', `${n}：${c}`, { background: 'rgba(34,18,42,.55)', padding: '8px 18px', borderRadius: '20px' }));
      s.card = M.box(L, 560, 300, { width: '520px', height: '260px', borderRadius: '24px', background: '#fff', boxShadow: '0 16px 34px rgba(160,20,70,.2)', padding: '24px', boxSizing: 'border-box' });
      M.box(s.card, 24, 24, { width: '180px', height: '180px', borderRadius: '18px', background: 'linear-gradient(140deg,#ffd166,#ff6b9a)' }); M.txt(s.card, 230, 30, f(900, 40, M.CN), INK, '示例好物'); M.txt(s.card, 230, 90, f(600, 26, M.CN), '#7a5a6a', '限量 · 今日专享'); M.txt(s.card, 230, 140, f(400, 64, M.AN), PK, '¥ 129');
      s.n = M.txt(L, 680, 600, f(400, 170, M.AN), PK, '3', { width: '200px', textAlign: 'center', lineHeight: 1, transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.pop(s.live, t, .75, 9.2, { from: .6 }); s.dot.style.opacity = .4 + .6 * Math.abs(Math.sin(t * 4)); M.rise(s.view, t, .95, 9.2);
      s.view.textContent = `👀 ${Math.round(12800 * M.o3((t - .95) / 6)).toLocaleString('en')} · 示例 SAMPLE`; M.hero(s.t, t, 1.1, 9.2);
      s.cm.forEach((c, i) => { const a = 1.6 + i * 1.1, d = t - a; c.style.opacity = d > 0 ? (Math.min(1, d / .25) * (1 - Math.min(1, Math.max(0, (d - 2.6) / .4)))).toFixed(3) : 0; c.style.transform = `translateY(${(700 - 90 * Math.min(4, d / .9) - 20 * M.o3(d / .3)).toFixed(1)}px)`; });
      M.slide(s.card, t, 3.6, 9.2, { dx: 120 });
      const k = t < 6.75 ? -1 : Math.min(2, Math.floor((t - 6.75) / .55)); s.n.textContent = ['3', '2', '1'][Math.max(0, k)]; const lt = (t - 6.75) % .55;
      s.n.style.opacity = t < 6.75 || t > 9.2 ? 0 : (k === 2 ? 1 : 1 - M.i2((lt - .35) / .2)); s.n.style.transform = `scale(${(1.5 - .5 * M.os(lt / .25)).toFixed(3)})`; } });
})();
