/* T100 End Card 关注结尾卡 · 10 s logo-only sample. Mark, follow button with a cursor click, generic action icons (no platform logos). */
(function () { const C = EV, M = K.T.mo, f = M.f, P = '#ff3d71', INK = '#f5f3ff';
  const IC = [['<path d="M40 66 C 14 48, 8 30, 20 20 C 28 14, 36 18, 40 26 C 44 18, 52 14, 60 20 C 72 30, 66 48, 40 66Z"/>', '点赞', 'Like'], ['<path d="M52 16 L68 32 L52 48 M68 32 H34 C 22 32, 14 40, 14 54"/>', '分享', 'Share'], ['<path d="M24 54 V36 a16 16 0 0 1 32 0 V54 L62 60 H18Z M34 66 a6 6 0 0 0 12 0"/>', '开启通知', 'Notify']];
  M.setup({ noface: true, bg: 'radial-gradient(ellipse at 50% 30%, #2b1f4f, #100b20 70%)', port: { box: [300, 40, 1320, 780] },
    captions: M.caps([['谢谢观看', 'Thanks for watching'], ['点赞、分享、开启通知', 'Like, share, turn on notifications'], ['下期见！', 'See you next time!']]),
    build(L) { const s = {};
      s.logo = M.logo(L, 860, 70, 200, INK, '#2b1f4f'); s.name = M.txt(L, 0, 290, f(400, 52, M.AN), INK, 'EVA VIDEO STUDIO', { width: '1920px', textAlign: 'center', letterSpacing: '.14em' });
      s.btn = M.txt(L, 790, 380, f(900, 52, M.CN), '#fff', '＋ 关注 Follow', { background: P, padding: '14px 40px', borderRadius: '999px', transformOrigin: '50% 50%' });
      s.cur = M.svg(L, 0, 0, 60, 70, '<path d="M6 4 L6 56 L20 44 L30 66 L40 62 L30 40 L48 40Z" fill="#fff" stroke="#111" stroke-width="3"/>');
      s.ic = IC.map(([d, c, e], i) => { const g = M.box(L, 560 + i * 300, 520, { width: '200px', textAlign: 'center' }); g.s = M.svg(g, 60, 0, 80, 80, `<g fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">${d}</g>`, { transformOrigin: '50% 50%' });
        M.txt(g, 0, 92, f(900, 36, M.CN), INK, c, { width: '200px', textAlign: 'center' }); M.txt(g, 0, 140, f(600, 22, M.INTER), '#a99fd0', e, { width: '200px', textAlign: 'center' }); return g; });
      s.bye = M.txt(L, 0, 720, f(900, 60, M.CN), P, '下期见！See you next time', { width: '1920px', textAlign: 'center' });
      return s; },
    update(s, t) { M.pop(s.logo, t, .6, 10.3, { from: .4 }); M.rise(s.name, t, .95, 10.3);
      M.pop(s.btn, t, 1.4, 10.3, { from: .5 }); const cu = M.io((t - 1.9) / .7), cx = 1300 - 220 * cu, cy = 640 - 210 * cu, click = t > 2.65 && t < 2.95;
      s.cur.style.opacity = t > 1.9 && t < 3.6 ? 1 : 0; s.cur.style.transform = `translate(${cx.toFixed(1)}px, ${cy.toFixed(1)}px) scale(${click ? .85 : 1})`;
      if (t > 2.7) { s.btn.textContent = '✓ 已关注 Following'; s.btn.style.background = '#5b4bff'; s.btn.style.transform += ` scale(${(1 + .08 * Math.exp(-(t - 2.7) * 6)).toFixed(3)})`; }
      s.ic.forEach((g, i) => { M.rise(g, t, 3.6 + i * .2, 10.3, { dy: 30 }); const k = Math.max(0, 1 - Math.abs(t - (4.4 + i * .6)) / .3); g.s.style.transform = `scale(${(1 + .3 * k).toFixed(3)})`; g.s.querySelector('g').setAttribute('stroke', k > .2 ? P : INK); });
      M.hero(s.bye, t, 6.85, 10.3, { dx: 0, dy: 24, noclip: true }); } });
})();
