/* T57 Scoreboard 体育比分 · 10 s sample. Playful "us vs procrastination" match; all numbers are SAMPLE (marked). */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, OR = '#ff8a1a', LED = '#ffb42e';
  const flip = (e, t, t0, a, b) => { const u = (t - t0) / .3; e.textContent = u < .5 ? a : b; e.style.transform = `scaleY(${u > 0 && u < 1 ? Math.abs(Math.cos(u * Math.PI)).toFixed(3) : 1})`; };
  M.setup({ bg: 'radial-gradient(ellipse at 50% -10%, #3a5f4a, #0e1a14 60%)', win: { x: 1270, y: 150, w: 500, h: 560, r: 24, o: 1, s: 1.15 }, ring: () => ({ color: OR, width: 6, shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['本周对决：我们 vs 拖延', 'This week: us vs procrastination'], ['五条视频，全部按时发布（示例）', 'Five videos, all on time (sample)'], ['这一局，我们赢了', 'We won this round']]),
    build(L) { const s = {};
      s.tag = M.txt(L, 110, 70, f(400, 44, M.AN), OR, 'MATCH DAY · 本周对决', { letterSpacing: '.08em' });
      s.sb = M.box(L, 110, 140, { width: '960px', height: '250px', background: '#070a08', border: '6px solid #2b2b2b', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,.5)' });
      M.txt(s.sb, 40, 34, f(900, 44, M.CN), '#fff', '我们 US'); M.txt(s.sb, 620, 34, f(900, 44, M.CN), '#fff', '拖延 DELAY');
      s.a = M.txt(s.sb, 90, 96, f(700, 120, M.MONO), LED, '0', { textShadow: `0 0 16px ${LED}`, lineHeight: 1, transformOrigin: '50% 50%' }); s.b = M.txt(s.sb, 690, 96, f(700, 120, M.MONO), LED, '0', { textShadow: `0 0 16px ${LED}`, lineHeight: 1, transformOrigin: '50% 50%' });
      M.txt(s.sb, 440, 110, f(700, 80, M.MONO), '#555', ':');
      s.clk = M.txt(s.sb, 400, 30, f(700, 34, M.MONO), '#ff5a3c', "00'00\"");
      s.st = [['发布 Posts', 5, 5], ['准时 On time', 5, 5], ['拖延 Delays', 1, 5]].map(([k, v, m], i) => { const r = M.box(L, 110, 440 + i * 80, { width: '960px' }); M.txt(r, 0, 0, f(700, 32, M.CN), '#dfe8e2', k);
        const bar = M.box(r, 300, 10, { width: '560px', height: '26px', background: '#1d2a22', borderRadius: '13px', overflow: 'hidden' }); r.fill = el(bar, 'div', '', { height: '100%', width: '0%', background: i === 2 ? '#ff5a3c' : OR, borderRadius: '13px' }); r.v = v / m; r.n = M.txt(r, 880, 0, f(700, 32, M.MONO), '#fff', `${v}/${m}`); return r; });
      s.ft = M.txt(L, 110, 690, f(400, 80, M.AN), '#0e1a14', 'FULL TIME · 我们赢了 WIN', { background: OR, padding: '0 26px', letterSpacing: '.04em' });
      s.smp = M.txt(L, 900, 74, f(700, 22, M.INTER), '#0e1a14', 'SAMPLE 示例', { background: '#dfe8e2', padding: '4px 10px', borderRadius: '4px' });
      return s; },
    update(s, t) { M.slide(s.tag, t, .75, 9.2, { dx: -40 }); M.pop(s.smp, t, .9, 9.2, { from: .6 }); M.panel(s.sb, t, .9, 9.2, { r: 16 });
      const sa = t < 1.8 ? '0' : t < 2.6 ? '1' : t < 4.6 ? '2' : '3', pa = t < 2.6 ? '0' : t < 4.6 ? '1' : '2';
      [[1.8, '0', '1'], [2.6, '1', '2'], [4.6, '2', '3']].forEach(([t0, a, b]) => { if (t >= t0 && t < t0 + .3) flip(s.a, t, t0, a, b); }); if (![1.8, 2.6, 4.6].some(x => t >= x && t < x + .3)) { s.a.textContent = sa; s.a.style.transform = ''; }
      s.b.textContent = t < 3.2 ? '0' : '1'; if (t >= 3.2 && t < 3.5) flip(s.b, t, 3.2, '0', '1'); else s.b.style.transform = '';
      const m = Math.floor(Math.max(0, t - .9) * 9); s.clk.textContent = `${String(Math.min(90, m)).padStart(2, '0')}'00"`;
      s.st.forEach((r, i) => { M.slide(r, t, 3.6 + i * .15, 9.2, { dx: -40 }); r.fill.style.width = (r.v * 100 * M.o3((t - 3.8 - i * .15) / .8)).toFixed(1) + '%'; });
      M.panel(s.ft, t, 6.85, 9.2); } });
})();
