/* T69 Mind Map 思维导图 · 10 s sample (illustrative copy). Centre topic, branches grow, a sub-branch blooms, the path lights up. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#2b2440', CX = 560, CY = 400;
  const B = [['选题', 'Topic', -400, -230, '#ff7a59'], ['脚本', 'Script', -420, 40, '#ffb800'], ['拍摄', 'Shoot', -180, 260, '#2ec4b6'], ['剪辑', 'Edit', 360, 200, '#6b5bff'], ['发布', 'Post', 380, -220, '#ff4f9a']];
  M.setup({ bg: '#fdfaf3', win: { x: 1300, y: 160, w: 460, h: 460, r: 230, o: 1, s: 1.15 }, ring: () => ({ color: INK, width: 6, shadow: .2 }), port: { box: [60, 60, 1080, 720] },
    captions: M.caps([['做内容，脑子里要有一张图', 'Content needs a map in your head'], ['五个环节，一个都不能少', 'Five steps, none optional'], ['剪辑，是最后的魔法', 'Editing is the final magic']]),
    build(L) { const s = {};
      s.br = B.map(([c, e, dx, dy, col]) => { const ex = CX + dx, ey = CY + dy, p = M.path(L, 0, 0, 1200, 900, `M${CX} ${CY} C ${CX + dx * .5} ${CY}, ${CX + dx * .5} ${ey}, ${ex} ${ey}`, col, 8);
        const n = M.txt(L, ex - 90, ey - 40, f(900, 44, M.CN), '#fff', c, { background: col, padding: '8px 26px', borderRadius: '999px', transformOrigin: '50% 50%' }); M.txt(n, 0, 70, f(700, 22, M.INTER), col, e, { width: '100%', textAlign: 'center', left: 0 }); return { p, n }; });
      s.sub = [['字幕', 90, 300], ['节奏', 230, 370], ['封面', 380, 340]].map(([c, x, y]) => { const ex = CX + x + 300, ey = CY + y; return { p: M.path(L, 0, 0, 1200, 900, `M${CX + 360} ${CY + 200} Q ${ex - 40} ${CY + 220}, ${ex - 40} ${ey - 20}`, '#6b5bff', 4), n: M.txt(L, ex - 90, ey - 10, f(900, 34, M.CN), '#6b5bff', c, { border: '4px solid #6b5bff', padding: '2px 18px', borderRadius: '999px', background: '#fff', transformOrigin: '50% 50%' }) }; });
      s.c = M.txt(L, CX - 150, CY - 60, f(900, 60, M.CN), '#fff', '做内容', { background: INK, padding: '20px 40px', borderRadius: '30px', transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.pop(s.c, t, .85, 9.2, { from: .4 });
      s.br.forEach(({ p, n }, i) => { const a = 1.4 + i * .3 + (i > 2 ? 2.0 : 0); M.draw(p, t, a, .4, 9.2); M.pop(n, t, a + .3, 9.2, { from: .3 }); });
      s.sub.forEach(({ p, n }, i) => { M.draw(p, t, 6.8 + i * .2, .3, 9.2); M.pop(n, t, 7.05 + i * .2, 9.2, { from: .3 }); });
      const g = t > 6.7 ? Math.min(1, (t - 6.7) / .4) : 0; s.br[3].p.setAttribute('stroke-width', (8 + 6 * g).toFixed(1)); s.br[3].n.style.boxShadow = `0 0 ${(30 * g).toFixed(0)}px rgba(107,91,255,.7)`; } });
})();
