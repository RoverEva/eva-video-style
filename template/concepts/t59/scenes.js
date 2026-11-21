/* T59 Recipe Card 菜谱卡 · 10 s sample (illustrative copy; a common home recipe). Ingredients tick off; step timer; dinner stamp. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, R = '#e8553a', INK = '#3a2a20';
  M.setup({ bg: '#f6efe3', win: { x: 1260, y: 150, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: R, width: 10, shadow: .3 }), port: { box: [90, 40, 1060, 780] },
    captions: M.caps([['十分钟家常菜：番茄炒蛋', 'Ten-minute classic: tomato & egg'], ['先炒蛋，再炒番茄', 'Eggs first, then tomatoes'], ['开饭啦！', "Dinner's ready!"]]),
    build(L) { const s = {};
      M.bg(el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'linear-gradient(rgba(232,85,58,.12) 50%, transparent 50%), linear-gradient(90deg, rgba(232,85,58,.12) 50%, transparent 50%)', backgroundSize: '80px 80px' }));
      s.card = M.box(L, 100, 60, { width: '1000px', height: '720px', background: '#fffdf8', borderRadius: '24px', boxShadow: '0 20px 40px rgba(90,50,20,.18)' });
      s.t = M.txt(L, 150, 100, f(900, 78, M.CN), INK, '番茄炒蛋'); s.e = M.txt(L, 154, 200, f('italic 700', 34, M.PF), '#9a7a66', 'Tomato & egg · 10 min');
      s.ing = [['番茄', '2 个'], ['鸡蛋', '3 个'], ['葱', '1 根'], ['盐', '少许']].map(([a, b], i) => { const r = M.box(L, 150, 280 + i * 70, {}); r.box = M.box(r, 0, 4, { width: '38px', height: '38px', border: `4px solid ${INK}`, borderRadius: '8px', boxSizing: 'border-box' });
        r.ck = M.path(r, 2, 0, 44, 44, 'M8 22 L18 32 L38 8', R, 6); M.txt(r, 60, 0, f(700, 40, M.CN), INK, `${a}  ${b}`); return r; });
      s.steps = [['1', '先炒蛋，盛出'], ['2', '再炒番茄出汁'], ['3', '回锅，加盐']].map(([n, c], i) => M.txt(L, 560, 290 + i * 80, f(700, 38, M.CN), INK, `${n}  ${c}`));
      s.ring = M.svg(L, 860, 560, 160, 160, `<circle cx="80" cy="80" r="64" fill="none" stroke="#f1e3d5" stroke-width="14"/><circle class="p" cx="80" cy="80" r="64" fill="none" stroke="${R}" stroke-width="14" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 80 80)"/>`); s.rp = s.ring.querySelector('.p');
      s.rt = M.txt(L, 890, 618, f(700, 34, M.MONO), INK, '3:00');
      s.done = M.txt(L, 160, 610, f(900, 80, M.CN), '#fff', '开饭啦！', { background: R, padding: '6px 34px', borderRadius: '18px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.panel(s.card, t, .7, 9.2, { r: 24 }); M.hero(s.t, t, 1.0, 9.2); M.rise(s.e, t, 1.3, 9.2);
      s.ing.forEach((r, i) => { M.rise(r, t, 1.5 + i * .13, 9.2); M.draw(r.ck, t, 2.3 + i * .25, .25, 9.2); });
      s.steps.forEach((e, i) => M.slide(e, t, 3.6 + i * .3, 9.2, { dx: 40 }));
      M.pop(s.ring, t, 4.2, 9.2, { from: .6 }); M.rise(s.rt, t, 4.2, 9.2, { dy: 8 }); const u = M.io((t - 4.4) / 2); s.rp.setAttribute('stroke-dashoffset', (1 - u).toFixed(4));
      const sec = Math.round(180 * (1 - u)); s.rt.textContent = `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
      M.pop(s.done, t, 6.85, 9.2, { from: 1.4, base: 'rotate(-4deg)' }); } });
})();
