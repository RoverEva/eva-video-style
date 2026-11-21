/* T183 黏土小屋 Clay House: soft clay shapes squish in, wobble, home tips appear on clay tags. */
(function () { const M = K.T.mo, X = M.X, PK = '#f4a6a0', BG = '#ffe4d6';
  const clay = (c, x, y, w, h, col, r, txt) => M.box(c, x, y, { width: w + 'px', height: h + 'px', borderRadius: r, background: `radial-gradient(circle at 30% 25%, rgba(255,255,255,.7), ${col} 45%, ${col})`, boxShadow: `inset -14px -18px 30px rgba(0,0,0,.12), 0 20px 30px rgba(120,60,40,.18)`, color: '#5a2a22', font: M.f(900, 44, M.CN), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 100%' }, txt || '');
  const squish = (e, t, a) => { const u = (t - a), s = u < 0 ? 0 : u < .3 ? u / .3 : 1 + .25 * Math.exp(-(u - .3) * 5) * Math.sin((u - .3) * 18); e.style.opacity = u < 0 ? 0 : 1; e.style.transform = `scale(${(2 - s).toFixed(3)}, ${s.toFixed(3)})`; };
  M.story({ bg: BG, sbg: [BG, '#ffeede', '#e6f4ff'], tr: ['rise', 'zoom'], ring: () => ({ color: '#ffffff', width: 12, shadow: .2 }),
    wins: [M.c(1360, 160, 420), M.q(110, 180, 420, 500, 60), M.c(1360, 160, 420)],
    caps: [['把家，捏成一个小屋', 'Shape home like a little clay house'], ['软软的，暖暖的', 'Soft and warm'], ['三个小改造，马上做（示例）', 'Three small upgrades (sample)']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => ({ roof: M.svg(c, 220, 260, 460, 200, `<path d="M20 190 L230 20 L440 190Z" fill="#e48a8a"/>`, { transformOrigin: '50% 100%' }), body: clay(c, 260, 450, 380, 320, PK, '40px'), door: clay(c, 400, 600, 100, 170, '#b88b9a', '50px 50px 10px 10px'), b1: clay(c, 760, 680, 110, 110, '#a8e6f0', '50%'), b2: clay(c, 880, 700, 90, 90, '#c6f2b8', '50%') }),
       (s, t, a) => { squish(s.body, t, a + .2); squish(s.roof, t, a + .5); squish(s.door, t, a + .8); squish(s.b1, t, a + 1.1); squish(s.b2, t, a + 1.3); }],
      [c => ({ bl: [['#ffd6a5', '软'], ['#bde0fe', '暖'], ['#cdeac0', '慢']].map(([col, n], i) => clay(c, 760 + i * 320, 360, 260, 260, col, '50%', n)) }), (s, t, a) => s.bl.forEach((e, i) => squish(e, t, a - .1 + i * .25))],
      [c => ({ tg: ['换暖光灯', '加一块地毯', '摆一盆绿植'].map((n, i) => clay(c, 160, 200 + i * 200, 620, 150, ['#ffd6a5', '#f4a6a0', '#cdeac0'][i], '75px', n)) }), (s, t, a) => s.tg.forEach((e, i) => squish(e, t, a - .1 + i * .3))]
    ] });
})();
