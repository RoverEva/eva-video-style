/* T45 Receipt 购物小票 · 10 s sample. A receipt prints out of a slot line by line. All times are SAMPLE figures (marked). */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, INK = '#2a2a2a';
  M.setup({ bg: 'linear-gradient(160deg,#ece8e0,#d9d3c7)', win: { x: 1150, y: 150, w: 560, h: 620, r: 28, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 10, shadow: .35 }), port: { box: [180, 40, 900, 780] },
    captions: M.caps([['算一笔时间账', "Let's do the time math"], ['脚本、剪辑、字幕、导出', 'Script, edit, captions, export'], ['省下的时间，拿去拍下一条（示例）', 'Spend the saved time on the next one (sample)']]),
    build(L) { const s = {};
      s.slot = M.box(L, 240, 48, { width: '640px', height: '44px', borderRadius: '22px', background: '#3b3b3b', boxShadow: 'inset 0 6px 10px rgba(0,0,0,.6)' });
      s.win = M.box(L, 280, 70, { width: '560px', height: '720px', overflow: 'hidden' });
      s.pp = el(s.win, 'div', 'abs', { left: '20px', top: 0, width: '520px', height: '700px', background: '#fffefa', boxShadow: '0 10px 30px rgba(0,0,0,.2)', padding: '34px 40px', boxSizing: 'border-box', font: f(700, 30, M.MONO), color: INK });
      const row = (a, b, col) => { const r = el(s.pp, 'div', '', { display: 'flex', justifyContent: 'space-between', margin: '12px 0', color: col || INK }); el(r, 'span', '', { font: f(700, 34, M.CN) }, a); el(r, 'span', '', {}, b); return r; };
      el(s.pp, 'div', '', { textAlign: 'center', font: f(900, 40, M.CN) }, '时间收据'); el(s.pp, 'div', '', { textAlign: 'center', fontSize: '22px', marginBottom: '10px' }, 'TIME RECEIPT · SAMPLE');
      el(s.pp, 'div', '', { borderTop: '3px dashed #999', margin: '14px 0' });
      row('写脚本', '40 min'); row('剪辑', '15 min'); row('双语字幕', 'AUTO'); row('导出', '2 min');
      el(s.pp, 'div', '', { borderTop: '3px dashed #999', margin: '18px 0' });
      const tr = row('合计 TOTAL', ''); s.tot = tr.lastChild; s.tot.style.font = f(700, 44, M.MONO);
      el(s.pp, 'div', '', { textAlign: 'center', marginTop: '26px', fontSize: '22px', letterSpacing: '.2em' }, '|| ||| | || |||| | ||');
      s.stamp = M.txt(L, 560, 520, f(900, 56, M.CN), '#d23a2f', '示例 SAMPLE', { border: '6px solid #d23a2f', padding: '4px 18px', borderRadius: '10px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.rise(s.slot, t, .7, 9.2, { dy: -20 }); s.win.style.opacity = (1 - M.i2((t - 8.97) / .23)).toFixed(3);
      const vis = 300 * M.io((t - .9) / 2.3) + 400 * M.io((t - 3.6) / 2.2); s.pp.style.clipPath = `inset(0 0 ${(700 - vis).toFixed(1)}px 0)`;
      M.count(s.tot, 57, t, 5.4, .8, v => v + ' min');
      M.pop(s.stamp, t, 6.85, 9.2, { from: 1.6, base: 'rotate(-12deg)' }); } });
})();
