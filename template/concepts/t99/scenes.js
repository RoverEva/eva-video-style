/* T99 Announcement 公告 · 10 s logo-only sample. Megaphone wobbles, banner unrolls, three update points (SAMPLE) tick in. */
(function () { const C = EV, M = K.T.mo, f = M.f, R = '#e63946', INK = '#1d1d24';
  M.setup({ noface: true, bg: 'linear-gradient(160deg,#fff7e6,#ffe8c2)', port: { box: [260, 40, 1400, 780] },
    captions: M.caps([['重要通知', 'Announcement'], ['三件事，一次说清（示例）', 'Three updates at once (sample)'], ['详情请看主页', 'Details on our page']]),
    build(L) { const s = {};
      s.mg = M.svg(L, 330, 90, 260, 220, `<path d="M40 80 L150 30 V190 L40 140Z" fill="${R}"/><rect x="10" y="80" width="40" height="60" rx="8" fill="${INK}"/><path d="M150 30 Q 200 110 150 190" fill="#ff6b6b"/><path d="M60 140 L80 200 H110 L94 148" fill="${INK}"/>` + [0, 1, 2].map(i => `<path class="w" d="M${200 + i * 22} ${70 - i * 10} Q ${230 + i * 22} 110 ${200 + i * 22} ${150 + i * 10}" stroke="${R}" stroke-width="7" fill="none" stroke-linecap="round"/>`).join(''), { transformOrigin: '40% 60%' });
      s.ws = [...s.mg.querySelectorAll('.w')];
      s.ban = M.box(L, 640, 130, { width: '760px', height: '140px', background: R, borderRadius: '12px', display: 'flex', alignItems: 'center', paddingLeft: '40px', boxSizing: 'border-box', transformOrigin: '0 50%', boxShadow: '0 12px 24px rgba(200,40,50,.25)' });
      M.txt(s.ban, 40, 26, f(900, 80, M.CN), '#fff', '重要通知'); M.txt(s.ban, 420, 52, f(400, 44, M.AN), '#ffd6d9', 'NOTICE');
      s.pts = [['新功能上线', 'New features'], ['界面全新升级', 'Fresh new look'], ['老用户专属福利', 'A thank-you for members']].map(([c, e], i) => { const g = M.box(L, 360, 380 + i * 110, {}); g.k = M.path(g, 0, 6, 60, 60, 'M8 30 L24 46 L52 12', R, 9); M.txt(g, 80, 0, f(900, 54, M.CN), INK, c); M.txt(g, 82, 66, f(600, 24, M.INTER), '#7a6a5a', e); return g; });
      s.tag = M.txt(L, 1150, 400, f(700, 22, M.INTER), '#fff', 'SAMPLE 示例', { background: '#8a7a6a', padding: '4px 12px', borderRadius: '6px' });
      s.more = M.txt(L, 360, 720, f(900, 44, M.CN), '#fff', '详情请看主页 →', { background: INK, padding: '8px 26px', borderRadius: '14px' });
      return s; },
    update(s, t) { M.pop(s.mg, t, .6, 10.3, { from: .4 }); s.mg.style.transform += ` rotate(${(6 * Math.sin(t * 7) * Math.exp(-Math.max(0, t - 1) * .6)).toFixed(2)}deg)`;
      s.ws.forEach((w, i) => { w.style.opacity = (.3 + .7 * Math.max(0, Math.sin(t * 6 - i))).toFixed(2); });
      const u = M.o5((t - 1.0) / .6); s.ban.style.opacity = t > 1 ? 1 : 0; s.ban.style.transform = `scaleX(${u.toFixed(3)})`;
      s.pts.forEach((g, i) => { M.slide(g, t, 3.6 + i * .45, 10.3, { dx: -40 }); M.draw(g.k, t, 3.75 + i * .45, .25, 10.3); }); M.pop(s.tag, t, 3.6, 10.3, { from: .6 }); M.rise(s.more, t, 6.85, 10.3); } });
})();
