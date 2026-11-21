/* T61 Quiz Show 问答竞猜 · 10 s sample. Fact quiz: B-roll = supplementary footage (answer B). Options light, answer revealed. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, G = '#2fd17a', Y = '#ffd23f';
  M.setup({ bg: 'radial-gradient(ellipse at 40% 20%, #2b3fae, #0b1446 65%)', win: { x: 1270, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: Y, width: 8, glow: 'rgba(255,210,63,.5)', shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['来答题：B-roll 是什么？', 'Quiz: what is B-roll?'], ['四个选项，选一个', 'Four options — pick one'], ['答案是 B：辅助画面', 'Answer: B, supplementary footage']]),
    build(L) { const s = {};
      s.lights = M.bg(M.box(L, 0, 0, { width: '1920px', height: '1080px', background: 'repeating-conic-gradient(from 0deg at 50% 120%, rgba(255,255,255,.06) 0 6deg, transparent 6deg 18deg)' }));
      s.q = M.box(L, 110, 80, { width: '980px', padding: '30px 40px', boxSizing: 'border-box', background: '#ffffff', borderRadius: '24px', boxShadow: '0 12px 0 #c7cff8' });
      M.txt(s.q, 40, 26, f(700, 28, M.MONO), '#6a74b8', 'QUESTION 01', { position: 'static' }); M.txt(s.q, 40, 0, f(900, 62, M.CN), '#0b1446', '剪辑里的 B-roll 指的是？', { position: 'static', marginTop: '8px' });
      s.o = [['A', '主镜头'], ['B', '辅助画面'], ['C', '背景音乐'], ['D', '片尾字幕']].map(([k, v], i) => { const b = M.box(L, 110 + (i % 2) * 500, 330 + (i >> 1) * 150, { width: '470px', height: '120px', borderRadius: '60px', background: '#1d2a8a', border: '4px solid #6f7fe8', boxSizing: 'border-box', display: 'flex', alignItems: 'center', gap: '22px', padding: '0 24px' });
        b.k = el(b, 'div', '', { width: '74px', height: '74px', borderRadius: '50%', background: Y, color: '#0b1446', font: f(400, 46, M.AN), display: 'flex', alignItems: 'center', justifyContent: 'center' }, k); el(b, 'div', '', { font: f(900, 46, M.CN), color: '#fff' }, v); return b; });
      s.conf = Array.from({ length: 22 }, (_, i) => M.box(L, 0, 0, { width: '16px', height: '26px', background: [Y, G, '#ff5fa2', '#4ff2ff'][i % 4], borderRadius: '3px' }));
      return s; },
    update(s, t) { M.pop(s.q, t, .85, 9.2, { from: .7 });
      s.o.forEach((b, i) => { M.pop(b, t, 3.6 + i * .14, 9.2, { from: .6 }); const sel = t > 5.4 && t < 6.7 && Math.floor((t - 5.4) * 5) % 4 === i;
        const right = i === 1 && t > 6.75, dim = i !== 1 && t > 6.75;
        b.style.background = right ? G : sel ? '#3446c8' : '#1d2a8a'; b.style.borderColor = right ? '#fff' : '#6f7fe8'; if (dim) b.style.opacity = (parseFloat(b.style.opacity) * .4).toFixed(3);
        if (right) b.style.transform += ` scale(${(1 + .06 * M.os((t - 6.75) / .3) - .06 * Math.min(1, (t - 6.75) / .3)).toFixed(3)})`; });
      s.conf.forEach((c, i) => { const d = t - 6.8; if (d < 0 || t > 9.2) { c.style.opacity = 0; return; } const x = 360 + (i * 97) % 700, vy = -500 - (i * 53) % 300;
        c.style.opacity = (1 - M.i2((t - 8.9) / .3)).toFixed(3); c.style.transform = `translate(${(x + (i % 2 ? 1 : -1) * d * 120).toFixed(1)}px, ${(560 + vy * d + 700 * d * d).toFixed(1)}px) rotate(${(d * 400 + i * 30).toFixed(0)}deg)`; }); } });
})();
