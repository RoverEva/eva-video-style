/* T40 Route Map 路线地图 · 10 s concept sample (16:9). Silent; sample copy (illustrative); stylised map, no real geography. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", RD = '#e8453c', INK = '#1d2b36';
  const P = [[160, 640], [520, 330], [900, 590], [1080, 250]], ST = [['01', '构思', 'Idea'], ['02', '拍摄', 'Shoot'], ['03', '剪辑', 'Edit'], ['04', '发布', 'Publish']], AT = [.8, 3.0, 5.4, 7.6];
  const seg = (a, b) => `M${a[0]} ${a[1]} C ${a[0] + 160} ${a[1]}, ${b[0] - 160} ${b[1]}, ${b[0]} ${b[1]}`;
  M.setup({
    bg: '#e9efe4',
    win: { x: 1330, y: 120, w: 470, h: 560, r: 30, o: 1, s: 1.15 },
    ring: () => ({ color: '#ffffff', width: 10, shadow: .4 }),
    port: { box: [120, 80, 1100, 700] },
    captions: [{ t0: .5, t1: 3.4, cn: '一条视频的旅程', en: 'The journey of one video' },
               { t0: 3.5, t1: 6.6, cn: '从拍摄到剪辑，一站接一站', en: 'From shooting to editing, stop by stop' },
               { t0: 6.7, t1: 9.7, cn: '终点：发布上线', en: 'Final stop: publish' }],
    build(L) { const s = {};
      s.map = M.svg(L, -80, -40, 2080, 1160, `<path d="M0 820 C 300 760, 600 900, 1000 820 S 1700 700, 2080 780 L2080 1160 L0 1160Z" fill="#cfe3ef"/><path d="M-20 200 C 300 260, 520 120, 900 180 S 1500 90, 2100 160" stroke="#fff" stroke-width="22" fill="none"/><path d="M700 -20 C 760 300, 640 600, 760 1180" stroke="#fff" stroke-width="16" fill="none"/>` +
        Array.from({ length: 9 }, (_, i) => `<rect x="${120 + (i * 233) % 1700}" y="${300 + (i * 157) % 380}" width="${90 + (i % 3) * 30}" height="${70 + (i % 2) * 30}" rx="10" fill="#d6e2cc"/>`).join('')); M.bg(s.map);
      s.route = M.svg(L, 0, 0, 1920, 1080, P.slice(1).map((b, i) => `<path class="sg" d="${seg(P[i], b)}" fill="none" stroke="${RD}" stroke-width="8" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>`).join(''));
      s.sg = [...s.route.querySelectorAll('.sg')];
      s.pins = P.map(([x, y], i) => { const p = M.svg(L, x - 30, y - 76, 60, 80, `<path d="M30 78 C 30 78, 4 46, 4 30 A 26 26 0 1 1 56 30 C 56 46, 30 78, 30 78Z" fill="${i === 3 ? INK : RD}"/><circle cx="30" cy="30" r="10" fill="#fff"/>`, { transformOrigin: '50% 100%' });
        const lb = M.box(L, i === 3 ? x - 250 : x + 30, y - 70, { font: `900 38px ${CN}`, color: INK, background: '#fff', padding: '4px 14px', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,.12)', whiteSpace: 'nowrap' }, `${ST[i][0]} ${ST[i][1]}`); return { p, lb }; });
      s.car = M.box(L, 0, 0, { width: '34px', height: '34px', borderRadius: '50%', background: INK, border: '6px solid #fff', boxSizing: 'border-box', boxShadow: '0 4px 10px rgba(0,0,0,.3)' });
      s.title = M.box(L, 110, 860 - 760, { font: `900 64px ${CN}`, color: INK }, '一条视频的旅程');
      s.cards = ST.map(([n, cn, en], i) => M.box(L, 110, 186, { font: `700 30px Inter, sans-serif`, color: RD, letterSpacing: '.08em' }, `STOP ${n} · ${en.toUpperCase()}`));
      return s; },
    update(s, t) {
      s.map.style.transform = `translate(${(-t * 5).toFixed(1)}px, ${(-t * 2).toFixed(1)}px) scale(${(1 + t * .004).toFixed(4)})`;
      M.hero(s.title, t, .85, 9.2);
      s.pins.forEach(({ p, lb }, i) => { const v = M.env(t, AT[i], 9.2, .3), u = M.os((t - AT[i]) / .3);
        p.style.opacity = v.a; p.style.transform = `translateY(${(-60 * (1 - u)).toFixed(1)}px) scale(${(1 - .08 * v.x).toFixed(3)})`; M.rise(lb, t, AT[i] + .15, 9.2, { dy: 18 }); });
      s.sg.forEach((g, i) => M.draw(g, t, AT[i] + .35, AT[i + 1] - AT[i] - .45, 9.2));
      /* vehicle rides the route: on segment k between pin k and pin k+1 */
      let k = -1; for (let i = 0; i < 3; i++) if (t >= AT[i] + .35) k = i;
      if (k >= 0) { const d = (AT[k + 1] - AT[k] - .45), u = M.o3((t - AT[k] - .35) / d), pt = s.sg[k].getPointAtLength(s.sg[k].getTotalLength() * u);
        s.car.style.transform = `translate(${(pt.x - 17).toFixed(1)}px, ${(pt.y - 17).toFixed(1)}px)`; s.car.style.opacity = (1 - M.i2((t - 8.97) / .23)).toFixed(3); } else s.car.style.opacity = 0;
      s.cards.forEach((c, i) => { const a = AT[i], b = i < 3 ? AT[i + 1] : 9.2; const v = M.env(t, a + .1, b + .05, .25, .18); c.style.opacity = v.a.toFixed(3); c.style.transform = `translateY(${(12 * (1 - v.e) - 10 * v.x).toFixed(1)}px)`; });
    }
  });
})();
