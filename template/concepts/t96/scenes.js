/* T96 Stats Highlights 数据亮点 · 10 s logo-only sample. Three big counters with icons; ALL numbers are SAMPLE (marked). */
(function () { const C = EV, M = K.T.mo, f = M.f, Y = '#ffcf4a', INK = '#f2f4f8';
  const S = [[120, '+', '条视频', 'videos made', '<path d="M10 16h46v40H10zM56 30l18-10v32L56 42"/>'], [2, '', '种语言', 'languages', '<circle cx="40" cy="40" r="28"/><path d="M12 40h56M40 12c-10 12-10 44 0 56M40 12c10 12 10 44 0 56"/>'], [10, 's', '秒出片', 'to first draft', '<circle cx="40" cy="42" r="28"/><path d="M40 26v18l10 6M32 8h16"/>']];
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 30%, #1d2740, #0a0e18 70%)', port: { box: [200, 40, 1520, 780] },
    captions: M.caps([['一组数字（示例）', 'A few numbers (sample)'], ['它们说明了一切', 'They say it all'], ['谢谢每一位观众', 'Thank you for watching']]),
    build(L) { const s = {};
      s.t = M.txt(L, 0, 80, f(900, 64, M.CN), INK, '这一年 · This year', { width: '1920px', textAlign: 'center' }); s.tag = M.txt(L, 890, 170, f(700, 22, M.INTER), '#0a0e18', 'SAMPLE 示例', { background: '#9aa6bd', padding: '4px 12px', borderRadius: '6px' });
      s.c = S.map(([n, suf, c, e, ic], i) => { const g = M.box(L, 260 + i * 480, 260, { width: '440px', textAlign: 'center' }); g.ic = M.svg(g, 180, 0, 80, 80, `<g fill="none" stroke="${Y}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">${ic}</g>`);
        g.n = M.txt(g, 0, 100, f(400, 150, M.AN), INK, '0', { width: '440px', textAlign: 'center', lineHeight: 1 }); M.txt(g, 0, 270, f(900, 44, M.CN), INK, c, { width: '440px', textAlign: 'center' }); M.txt(g, 0, 330, f(600, 24, M.INTER), '#8f9ab0', e, { width: '440px', textAlign: 'center' });
        g.u = M.path(g, 120, 380, 200, 10, 'M2 5H198', Y, 5); g.to = n; g.suf = suf; return g; });
      s.ty = M.txt(L, 0, 720, f(900, 48, M.CN), Y, '谢谢你 · Thank you', { width: '1920px', textAlign: 'center' });
      return s; },
    update(s, t) { M.hero(s.t, t, .7, 10.3, { dx: 0, dy: 20, noclip: true }); M.pop(s.tag, t, 1.0, 10.3, { from: .6 });
      s.c.forEach((g, i) => { const a = 1.3 + i * .9 + (i ? 1.3 : 0); M.rise(g, t, a, 10.3, { dy: 40 }); M.count(g.n, g.to, t, a, 1.0, v => v + g.suf); M.draw(g.u, t, a + .6, .4, 10.3); M.pop(g.ic, t, a + .1, 10.3, { from: .3 }); });
      M.rise(s.ty, t, 6.85, 10.3); } });
})();
