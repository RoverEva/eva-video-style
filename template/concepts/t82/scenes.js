/* T82 Vinyl 黑胶唱片 · 10 s sample (illustrative copy). Record slides from its sleeve, spins; tonearm drops; side-A tracklist. */
(function () { const C = EV, M = K.T.mo, f = M.f, R = '#d8432f', CR = '#f1e4cc';
  M.setup({ bg: 'radial-gradient(ellipse at 30% 40%, #3a2a20, #15100c 70%)', win: { x: 1290, y: 160, w: 470, h: 470, r: 235, o: 1, s: 1.15 }, ring: () => ({ color: CR, width: 6, shadow: .5 }), port: { box: [90, 40, 1180, 780] },
    captions: M.caps([['今天放一张老唱片', 'Spinning an old record today'], ['A 面：开场、故事、结尾', 'Side A: intro, story, outro'], ['好的视频，像一首歌', 'A good video is like a song']]),
    build(L) { const s = {};
      s.rec = M.svg(L, 150, 150, 460, 460, `<circle cx="230" cy="230" r="228" fill="#0d0d0d"/>${Array.from({ length: 14 }, (_, i) => `<circle cx="230" cy="230" r="${215 - i * 9}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="2"/>`).join('')}<path d="M230 10 A220 220 0 0 1 420 120" stroke="rgba(255,255,255,.18)" stroke-width="10" fill="none"/><circle cx="230" cy="230" r="78" fill="${R}"/><text x="230" y="222" text-anchor="middle" font-family="Anton" font-size="34" fill="${CR}">EVA</text><text x="230" y="258" text-anchor="middle" font-family="Space Mono" font-size="16" fill="${CR}">SIDE A</text><circle cx="230" cy="230" r="8" fill="#15100c"/>`, { transformOrigin: '50% 50%' });
      s.sleeve = M.box(L, 110, 140, { width: '480px', height: '480px', background: `linear-gradient(140deg, ${R}, #f0a33a)`, boxShadow: '0 20px 40px rgba(0,0,0,.5)' });
      M.txt(s.sleeve, 34, 30, f(400, 90, M.AN), CR, 'SIDE A'); M.txt(s.sleeve, 38, 380, f(900, 48, M.CN), CR, '慢慢听');
      s.arm = M.svg(L, 780, 110, 120, 380, `<circle cx="80" cy="30" r="26" fill="#9a9a9a"/><path d="M80 30 L80 260 L40 330" stroke="#c9c9c9" stroke-width="12" fill="none" stroke-linecap="round"/><rect x="22" y="320" width="40" height="44" rx="6" fill="#d9d9d9" transform="rotate(25 42 342)"/>`, { transformOrigin: '80px 30px' });
      s.tr = [['A1', '开场', 'Intro'], ['A2', '故事', 'Story'], ['A3', '结尾', 'Outro']].map(([n, c, e], i) => M.txt(L, 990, 220 + i * 110, f(900, 52, M.CN), CR, `${n}  ${c}`, { letterSpacing: '.02em' }));
      s.tre = ['Intro', 'Story', 'Outro'].map((e, i) => M.txt(L, 1080, 290 + i * 110, f(700, 22, M.INTER), '#a38f78', e.toUpperCase(), { letterSpacing: '.2em' }));
      s.song = M.txt(L, 990, 600, f('italic 700', 44, M.PF), '#f0a33a', 'Like a song ♪');
      return s; },
    update(s, t) { M.slide(s.sleeve, t, .75, 9.2, { dx: -80 });
      const out = M.os((t - 1.2) / .7); M.rise(s.rec, t, 1.2, 9.2, { dy: 0 }); s.rec.style.transform = `translateX(${(220 * Math.max(0, out)).toFixed(1)}px) rotate(${(Math.max(0, t - 1.2) * (t > 3.6 ? 200 : 60)).toFixed(1)}deg)`;
      M.rise(s.arm, t, 1.6, 9.2, { dy: 0 }); s.arm.style.transform = `rotate(${(-35 + 28 * M.io((t - 3.5) / .6)).toFixed(2)}deg)`;
      s.tr.forEach((e, i) => { M.slide(e, t, 3.8 + i * .14, 9.2, { dx: 40 }); e.style.color = t > 4.5 + i * .7 && t < 5.2 + i * .7 ? '#f0a33a' : CR; }); s.tre.forEach((e, i) => M.rise(e, t, 3.95 + i * .14, 9.2));
      M.hero(s.song, t, 6.85, 9.2); } });
})();
