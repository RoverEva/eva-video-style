/* T68 Timeline 时间轴 · 10 s sample (illustrative milestones). A line draws, nodes pop, a dot travels, cards alternate above/below. */
(function () { const C = EV, M = K.T.mo, f = M.f, B = '#2a6df4', INK = '#1a2233';
  const N = [['第 1 年', '第一条视频', 'Year 1 · first video', 1.2], ['第 2 年', '找到风格', 'Year 2 · found a style', 3.6], ['第 3 年', '第 100 条', 'Year 3 · video 100', 5.0], ['现在', '下一站？', 'Now · what’s next?', 6.85]];
  M.setup({ bg: '#f7f7f2', win: { x: 1300, y: 110, w: 460, h: 460, r: 230, o: 1, s: 1.15 }, ring: () => ({ color: B, width: 6, shadow: .25 }), port: { box: [80, 60, 1180, 740] },
    captions: M.caps([['三年，一条时间线', 'Three years on one line'], ['从第一条，到第一百条', 'From video one to video one hundred'], ['下一站，你来定', 'You pick the next stop']]),
    build(L) { const s = {};
      s.t = M.txt(L, 110, 70, f(900, 72, M.CN), INK, '我的创作时间线'); s.e = M.txt(L, 114, 165, f(700, 30, M.INTER), '#7a8396', 'MY CREATOR TIMELINE · 示例 SAMPLE');
      s.ln = M.path(L, 110, 440, 1100, 20, 'M4 10H1090', '#c8cfdc', 6); s.lf = M.path(L, 110, 440, 1100, 20, 'M4 10H1090', B, 6);
      s.nodes = N.map(([y, c, e], i) => { const x = 160 + i * 300, up = i % 2 === 0; const d = M.box(L, x - 22, 428, { width: '44px', height: '44px', borderRadius: '50%', background: '#fff', border: `8px solid ${B}`, boxSizing: 'border-box', transformOrigin: '50% 50%' });
        const card = M.box(L, x - 130, up ? 250 : 500, { width: '260px', padding: '16px 18px', boxSizing: 'border-box', background: i === 3 ? B : '#fff', borderRadius: '16px', boxShadow: '0 10px 24px rgba(20,40,90,.12)' });
        M.txt(card, 0, 0, f(700, 24, M.MONO), i === 3 ? '#cfe0ff' : B, y, { position: 'static' }); M.txt(card, 0, 0, f(900, 42, M.CN), i === 3 ? '#fff' : INK, c, { position: 'static' }); M.txt(card, 0, 0, f(600, 20, M.INTER), i === 3 ? '#dbe6ff' : '#7a8396', e, { position: 'static' }); return { d, card, up }; });
      s.dot = M.box(L, 0, 0, { width: '26px', height: '26px', borderRadius: '50%', background: '#ff5a3c', boxShadow: '0 0 0 8px rgba(255,90,60,.2)' });
      return s; },
    update(s, t) { M.hero(s.t, t, .85, 9.2); M.rise(s.e, t, 1.1, 9.2); M.draw(s.ln, t, .9, .7, 9.2);
      const at = N.map(n => n[3]), x = t < at[0] ? 0 : t < at[1] ? 0 + 300 * M.io((t - at[0] - .5) / 1.6) * 0 : 0;
      let k = 0; for (let i = 0; i < 4; i++) if (t >= at[i]) k = i; const nx = i => 160 + i * 300; let px = nx(0);
      if (t >= at[0]) { px = nx(k); if (k < 3) px += 300 * M.io((t - at[k] - .4) / Math.max(.4, at[k + 1] - at[k] - .6)); }
      s.lf.setAttribute('stroke-dasharray', `${((px - 110) / 1090).toFixed(4)} 1`); s.lf.style.opacity = t >= at[0] ? (1 - M.i2((t - 8.97) / .23)) : 0;
      s.dot.style.opacity = s.lf.style.opacity; s.dot.style.transform = `translate(${(px - 13).toFixed(1)}px, 437px)`;
      s.nodes.forEach(({ d, card, up }, i) => { M.pop(d, t, at[i], 9.2, { from: .2 }); M.rise(card, t, at[i] + .12, 9.2, { dy: up ? 30 : -30 }); }); } });
})();
