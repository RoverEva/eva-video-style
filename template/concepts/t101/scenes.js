/* T101 课堂纸雕 Papercut Lesson · 3 scenes: title → three inputs → result. Paper layers parallax; iris + push transitions. */
(function () { const M = K.T.mo, X = M.X, f = M.f, INK = '#0f3b46';
  const card = (p, x, y, c, cn, en) => { const b = M.box(p, 0, 0, { width: '300px', height: '220px', background: c, borderRadius: '18px', boxShadow: '0 14px 0 rgba(0,0,0,.12), 0 20px 30px rgba(0,40,50,.25)', padding: '30px', boxSizing: 'border-box' });
    X(b, 30, 40, 54, INK, cn); X(b, 32, 120, 26, '#2c6b75', en, 700, M.INTER); return { b, x, y }; };
  M.story({ bg: '#0f4c5c', sbg: ['#0f4c5c', '#f3ead8', '#0b3440'], tr: ['iris', 'push'], ring: () => ({ color: '#f4efe6', width: 10, shadow: .4 }),
    wins: [M.c(1270, 150, 460), M.q(110, 170, 500, 600, 44), M.c(760, 90, 400)],
    caps: [['植物是怎么“吃饭”的？', 'How do plants eat?'], ['阳光、水、二氧化碳', 'Sunlight, water and CO₂'], ['做出氧气和糖', 'They make oxygen and sugar']],
    port: { box: [80, 60, 1420, 900] },
    scenes: [
      [c => ({ wv: ['#1d6f7f', '#2a8f9c', '#55b2b5', '#9bd3cc'].map((col, i) => M.svg(c, -200, 560 + i * 110, 2400, 520, `<path d="M0 ${60 - i * 6} C 300 ${10 + i * 10}, 600 ${100 - i * 8}, 1000 ${50 + i * 6} S 1700 ${10 + i * 12}, 2400 60 V520 H0Z" fill="${col}" style="filter:drop-shadow(0 -8px 10px rgba(0,0,0,.3))"/>`)), k: X(c, 110, 150, 50, '#bfe8e2', 'SCIENCE · 第 3 课', 700, M.INTER), t: X(c, 104, 220, 150, '#f4efe6', '光合作用'), e: X(c, 112, 420, 44, '#bfe8e2', 'Photosynthesis', 700, M.PF),
          sun: M.svg(c, 880, 120, 220, 220, `<circle cx="110" cy="110" r="70" fill="#ffd166"/>${Array.from({ length: 10 }, (_, i) => `<path d="M110 6 L122 34 L98 34Z" fill="#ffd166" transform="rotate(${i * 36} 110 110)"/>`).join('')}`, { transformOrigin: '50% 50%' }) }),
       (s, t, a) => { s.wv.forEach((e, i) => M.drift(e, t, (i + 1) * 9)); M.rise(s.k, t, a + .4, 99); M.hero(s.t, t, a + .55, 99, { dy: 30, dx: 0 }); M.rise(s.e, t, a + .9, 99); M.pop(s.sun, t, a + 1.1, 99, { from: .2, base: `rotate(${(t * 20).toFixed(1)}deg)` }); }],
      [c => ({ cards: [card(c, 0, 0, '#ffe8a3', '阳光', 'Sunlight'), card(c, 0, 0, '#bde0fe', '水', 'Water'), card(c, 0, 0, '#d8f3dc', '二氧化碳', 'CO₂')] }),
       (s, t, a) => { s.cards.forEach(({ b }, i) => M.slap(b, t, a - .15 + i * .3, 99, { x: [720, 1120, 900][i], y: [140, 220, 470][i], r: [-4, 3, -2][i] })); }],
      [c => ({ eq: X(c, 300, 560, 120, '#f4efe6', '= 氧气 + 糖'), en: X(c, 310, 710, 40, '#bfe8e2', 'Oxygen + sugar', 700, M.INTER),
          lv: [0, 1].map(i => M.svg(c, i ? 1300 : 300, 200, 220, 300, `<path d="M110 290 V120" stroke="#2a9d8f" stroke-width="10"/><path d="M110 150 C 20 120, 10 40, 60 10 C 120 30, 130 100, 110 150Z" fill="#52b788"/><path d="M110 200 C 200 170, 210 90, 160 60 C 100 80, 90 150, 110 200Z" fill="#74c69d"/>`, { transformOrigin: '50% 100%' })) }),
       (s, t, a) => { M.hero(s.eq, t, a - .05, 99, { dx: 0, dy: 40 }); M.rise(s.en, t, a + .3, 99); s.lv.forEach((e, i) => M.pop(e, t, a + .1 + i * .2, 99, { from: 0 })); }]
    ] });
})();
