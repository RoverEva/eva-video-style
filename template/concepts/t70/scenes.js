/* T70 Checklist 清单打钩 · 10 s sample (illustrative copy). Clipboard list ticks off item by item; progress fills; all done. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, G = '#1fa463', INK = '#1d2a24';
  const IT = [['标题想好了', 'Title'], ['封面做好了', 'Cover'], ['字幕检查了', 'Captions'], ['时长 60 秒内', 'Under 60 s'], ['发布时间定了', 'Post time']], AT = [1.9, 3.6, 4.4, 5.2, 6.0];
  M.setup({ bg: '#eaf5ee', win: { x: 1260, y: 150, w: 500, h: 580, r: 28, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }), port: { box: [90, 30, 1080, 790] },
    captions: M.caps([['发视频前，过一遍清单', 'Run the checklist before posting'], ['一项一项，打钩', 'Tick them one by one'], ['全部完成，发！', 'All done — post it!']]),
    build(L) { const s = {};
      s.cb = M.box(L, 160, 70, { width: '860px', height: '720px', background: '#fff', borderRadius: '24px', boxShadow: '0 20px 40px rgba(20,60,40,.15)' });
      s.clip = M.box(L, 470, 40, { width: '240px', height: '70px', borderRadius: '16px', background: '#4b5a52' });
      s.t = M.txt(L, 220, 140, f(900, 62, M.CN), INK, '发布前清单'); s.e = M.txt(L, 224, 225, f(700, 26, M.INTER), '#6f8178', 'PRE-POST CHECKLIST');
      s.rows = IT.map(([c, e], i) => { const r = M.box(L, 220, 290 + i * 80, {}); r.b = M.box(r, 0, 4, { width: '48px', height: '48px', border: `5px solid ${INK}`, borderRadius: '12px', boxSizing: 'border-box' }); r.k = M.path(r, 4, -4, 56, 56, 'M8 28 L22 42 L50 10', G, 8);
        r.tx = M.txt(r, 76, 0, f(700, 42, M.CN), INK, c); r.ln = M.path(r, 72, 20, 300, 20, 'M2 10H290', '#9fb3a8', 4); M.txt(r, 400, 10, f(600, 24, M.INTER), '#8aa096', e); return r; });
      s.pb = M.box(L, 220, 710, { width: '740px', height: '18px', borderRadius: '9px', background: '#e1ece6' }); s.pf = el(s.pb, 'div', '', { height: '100%', width: '0%', borderRadius: '9px', background: G });
      s.done = M.txt(L, 640, 130, f(900, 46, M.CN), '#fff', '全部完成 ✓', { background: G, padding: '8px 22px', borderRadius: '14px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.panel(s.cb, t, .7, 9.2, { r: 24 }); M.pop(s.clip, t, .9, 9.2, { from: .6 }); M.hero(s.t, t, 1.05, 9.2); M.rise(s.e, t, 1.3, 9.2);
      s.rows.forEach((r, i) => { M.rise(r, t, 1.4 + i * .1, 9.2); M.draw(r.k, t, AT[i], .25, 9.2); M.draw(r.ln, t, AT[i] + .15, .3, 9.2); r.tx.style.color = t > AT[i] + .15 ? '#7c9187' : INK; });
      const n = AT.filter(a => t > a + .1).length, cur = n / 5; s.pf.style.width = (cur * 100).toFixed(1) + '%'; s.pf.style.transition = 'none'; M.rise(s.pb, t, 1.5, 9.2, { dy: 10 });
      M.pop(s.done, t, 6.85, 9.2, { from: .4 }); } });
})();
