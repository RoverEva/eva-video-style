/* T72 Leaderboard 排行榜 · 10 s sample. Top 5 editing techniques; ranking is SAMPLE (marked). Rows enter 5→1, then #2 overtakes #1. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, GOLD = '#ffcc33', INK = '#f3eefe';
  const IT = [['跳剪', 'Jump cut', 92], ['字幕', 'Captions', 88], ['B-roll', 'B-roll', 75], ['变速', 'Speed ramp', 61], ['转场', 'Transitions', 54]];
  M.setup({ bg: 'linear-gradient(160deg,#2a1255,#120726)', win: { x: 1280, y: 150, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: GOLD, width: 8, shadow: .5 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['最常用的五个剪辑技巧', 'Top five editing techniques'], ['第五名到第二名……', 'Five down to two…'], ['第一名，是字幕（示例）', 'Number one: captions (sample)']]),
    build(L) { const s = {};
      s.t = M.txt(L, 110, 60, f(400, 90, M.AN), GOLD, 'TOP 5'); s.cn = M.txt(L, 330, 80, f(900, 56, M.CN), INK, '剪辑技巧排行榜'); s.tag = M.txt(L, 110, 175, f(700, 22, M.INTER), '#2a1255', '示例排名 SAMPLE RANKING', { background: '#cbbdf0', padding: '4px 12px', borderRadius: '6px' });
      s.rows = IT.map(([c, e, v], i) => { const r = M.box(L, 110, 0, { width: '980px', height: '92px', borderRadius: '18px', background: 'rgba(255,255,255,.08)', border: '2px solid rgba(255,255,255,.12)', boxSizing: 'border-box', overflow: 'hidden' });
        r.bar = el(r, 'div', 'abs', { left: 0, top: 0, height: '100%', width: '0%', background: 'linear-gradient(90deg, rgba(255,204,51,.35), rgba(255,204,51,.05))' });
        r.rk = M.txt(r, 24, 14, f(400, 56, M.AN), INK, '#'); M.txt(r, 120, 14, f(900, 48, M.CN), INK, c); M.txt(r, 120 + c.length * 50 + 20, 32, f(600, 24, M.INTER), '#b7a8e0', e); r.v = v; return r; });
      return s; },
    update(s, t) { M.hero(s.t, t, .8, 9.2, { dx: -40 }); M.hero(s.cn, t, 1.0, 9.2); M.pop(s.tag, t, 1.2, 9.2, { from: .6 });
      const swap = M.io((t - 6.8) / .6);
      s.rows.forEach((r, i) => { const rank = i === 0 ? 1 + swap : i === 1 ? 2 - swap : i + 1;
        /* sample order before the swap: #1 跳剪, #2 字幕 → 字幕 overtakes */
        const y = 240 + (rank - 1) * 108; const a = [5.4, 4.95, 4.5, 4.05, 3.6][i] - 1.9 + (i < 2 ? 1.9 : 0) * 0; const at = [2.9, 2.5, 2.1, 1.7, 1.3][i] + (i < 2 ? 1.5 : 0);
        const v = M.env(t, at, 9.2, .35); r.style.opacity = v.a; r.style.transform = `translate(${(-80 * (1 - v.e)).toFixed(1)}px, ${y.toFixed(1)}px)`;
        r.rk.textContent = '#' + Math.round(rank); r.rk.style.color = Math.round(rank) === 1 ? GOLD : INK; r.bar.style.width = (r.v * M.o3((t - at - .2) / .8)).toFixed(1) + '%';
        r.style.borderColor = Math.round(rank) === 1 && t > 7.2 ? GOLD : 'rgba(255,255,255,.12)'; }); } });
})();
