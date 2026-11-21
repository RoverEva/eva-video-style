/* T77 Clinic Clean 医疗健康 · 10 s sample (general wellness copy, not medical advice — disclaimer on screen). Soft teal cards, icons. */
(function () { const C = EV, M = K.T.mo, f = M.f, TL = '#1aa39a', INK = '#16343a';
  const ic = { drop: '<path d="M40 8 C 40 8, 14 40, 14 54 a26 26 0 0 0 52 0 C 66 40, 40 8, 40 8Z" fill="#1aa39a"/>', moon: '<path d="M52 10 a32 32 0 1 0 22 46 a26 26 0 1 1 -22 -46Z" fill="#5b7cfa"/>', walk: '<circle cx="44" cy="14" r="9" fill="#ff8a5b"/><path d="M42 26 L34 50 L22 70 M38 40 L54 50 M34 50 L48 72 M40 30 L24 38" stroke="#ff8a5b" stroke-width="7" stroke-linecap="round" fill="none"/>' };
  M.setup({ bg: 'linear-gradient(160deg,#f4fbfa,#e2f3f1)', win: { x: 1270, y: 160, w: 490, h: 490, r: 245, o: 1, s: 1.15 }, ring: () => ({ color: '#ffffff', width: 12, shadow: .25 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['每天三个健康小习惯', 'Three healthy daily habits'], ['喝水、早睡、动一动', 'Drink water, sleep early, move'], ['小习惯，慢慢来', 'Small habits, step by step']]),
    build(L) { const s = {};
      s.cross = M.svg(L, 110, 80, 90, 90, `<rect x="30" y="6" width="30" height="78" rx="8" fill="${TL}"/><rect x="6" y="30" width="78" height="30" rx="8" fill="${TL}"/>`, { transformOrigin: '50% 50%' });
      s.t = M.txt(L, 230, 84, f(900, 70, M.CN), INK, '每天 3 个健康小习惯'); s.e = M.txt(L, 234, 175, f(700, 28, M.INTER), '#5d8a86', 'THREE DAILY HABITS');
      s.cards = [['drop', '多喝水', 'Hydrate'], ['moon', '早点睡', 'Sleep early'], ['walk', '动一动', 'Move a little']].map(([k, c, e], i) => { const b = M.box(L, 110 + i * 330, 280, { width: '300px', height: '320px', borderRadius: '28px', background: '#fff', boxShadow: '0 14px 30px rgba(20,90,90,.12)' });
        b.i = M.svg(b, 110, 40, 80, 80, ic[k], { transformOrigin: '50% 50%' }); M.txt(b, 0, 150, f(900, 52, M.CN), INK, c, { width: '300px', textAlign: 'center' }); M.txt(b, 0, 225, f(600, 26, M.INTER), '#5d8a86', e, { width: '300px', textAlign: 'center' }); return b; });
      s.dis = M.txt(L, 110, 660, f(700, 30, M.CN), '#5d8a86', 'ⓘ 仅供参考，不构成医疗建议 · General info, not medical advice', { background: '#fff', padding: '10px 20px', borderRadius: '12px' });
      return s; },
    update(s, t) { M.pop(s.cross, t, .8, 9.2, { from: .3 }); s.cross.style.transform += ` rotate(${(90 * (1 - M.o3((t - .8) / .6))).toFixed(1)}deg)`; M.hero(s.t, t, 1.0, 9.2); M.rise(s.e, t, 1.3, 9.2);
      s.cards.forEach((b, i) => { M.rise(b, t, 3.6 + i * .15, 9.2, { dy: 50 }); M.pop(b.i, t, 3.8 + i * .15, 9.2, { from: .3 }); b.i.style.transform += ` translateY(${(-6 * Math.sin(t * 3 + i)).toFixed(1)}px)`; });
      M.rise(s.dis, t, 6.85, 9.2); } });
})();
