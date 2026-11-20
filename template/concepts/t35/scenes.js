/* T35 Polaroid Scrapbook 拍立得手账 · 10 s concept sample (16:9). Silent; sample copy (illustrative). Photos are frames of Eva's own clip. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const HAND = "'Playfair Display', serif", CN = "'Noto Sans CJK SC', sans-serif", INK = '#2b2118';
  const pola = (L, f, cn) => { const p = M.box(L, 0, 0, { width: '330px', height: '380px', background: '#fffdf7', padding: '18px 18px 0', boxSizing: 'border-box', transformOrigin: '50% 20%' });
    const i = el(p, 'img', '', { width: '294px', height: '280px', objectFit: 'cover', objectPosition: '52% 30%', display: 'block' }); i.src = `../../sample10/media/eva/f_${String(f).padStart(5, '0')}.jpg`;
    el(p, 'div', '', { font: `italic 700 34px ${HAND}`, color: INK, textAlign: 'center', marginTop: '14px' }, cn); return p; };
  M.setup({
    bg: '#d9c3a0',
    win: { x: 150, y: 150, w: 520, h: 540, r: 6, o: 1, s: 1.15 },
    ring: () => ({ color: '#fffdf7', width: 0, shadow: .0 }),
    captions: [{ t0: .5, t1: 3.4, cn: '周末，给自己放个假', en: 'Weekend — time off for me' },
               { t0: 3.5, t1: 6.6, cn: '第一天看海，第二天爬山', en: 'Day one the sea, day two the hills' },
               { t0: 6.7, t1: 9.7, cn: '把好日子都记下来', en: 'Keep the good days on paper' }],
    build(L) { const s = {};
      s.paper = el(L, 'div', 'abs', { left: '-60px', top: '-40px', width: (C.W + 120) + 'px', height: (C.H + 80) + 'px', backgroundImage: 'radial-gradient(rgba(120,85,45,.18) 1.4px, transparent 1.8px), linear-gradient(rgba(255,255,255,.08), rgba(0,0,0,.06))', backgroundSize: '18px 18px, 100% 100%' });
      s.frame = M.box(L, 120, 120, { width: '580px', height: '700px', background: '#fffdf7', boxShadow: '0 18px 40px rgba(60,40,15,.35)', transformOrigin: '50% 50%' });
      el(s.frame, 'div', 'abs', { left: 0, top: '600px', width: '580px', textAlign: 'center', font: `700 46px ${CN}`, color: INK }, '今天的我');
      s.tape = M.box(L, 350, 100, { width: '130px', height: '40px', background: 'rgba(255,230,150,.75)', transform: 'rotate(-5deg)' });
      s.title = M.box(L, 820, 110, { font: `italic 900 96px ${HAND}`, color: INK, whiteSpace: 'nowrap' }, 'Weekend diary');
      s.cn = M.box(L, 826, 230, { font: `900 64px ${CN}`, color: '#b5452b' }, '周末旅行日记');
      s.ul = M.svg(L, 826, 312, 520, 30, `<path d="M4 16 C 120 4, 260 26, 510 10" stroke="#b5452b" stroke-width="6" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1 1"/>`).querySelector('path');
      s.p1 = pola(L, 60, 'day 1'); s.p2 = pola(L, 200, 'day 2');
      s.arr = M.svg(L, 1150, 680, 300, 120, `<path d="M10 60 C 90 120, 190 110, 280 40" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round" stroke-dasharray=".03 .025" pathLength="1"/>`).querySelector('path');
      s.star = M.svg(L, 1700, 330, 120, 120, `<path d="M60 6 L74 44 L114 46 L82 70 L94 110 L60 86 L26 110 L38 70 L6 46 L46 44Z" fill="#f2b632" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/>`, { transformOrigin: '50% 50%' });
      return s; },
    update(s, t) {
      s.paper.style.transform = `translate(${(-t * 4).toFixed(1)}px, ${(-t * 2).toFixed(1)}px)`;
      const fv = M.env(t, .3, 9.25, .62, .45); s.frame.style.opacity = fv.a.toFixed(3); s.frame.style.transform = `rotate(${(-2 * fv.e).toFixed(2)}deg) scale(${(1.08 - .08 * fv.e).toFixed(4)})`;
      M.pop(s.tape, t, .9, 9.2, { base: 'rotate(-5deg)', from: .4 });
      M.hero(s.title, t, .95, 9.2, { dx: -50 }); M.rise(s.cn, t, 1.3, 9.2); M.draw(s.ul, t, 1.7, .5, 9.2);
      M.slap(s.p1, t, 3.5, 9.2, { x: 830, y: 400, r: -6, rf: -10 }); M.slap(s.p2, t, 4.3, 9.2, { x: 1300, y: 380, r: 5, rf: 10 });
      const d = M.o3((t - 6.9) / .6); s.arr.style.clipPath = `inset(0 ${((1 - d) * 100).toFixed(1)}% 0 0)`; s.arr.style.opacity = (d > 0 ? 1 : 0) * (1 - M.i2((t - 8.97) / .23));
      M.pop(s.star, t, 7.4, 9.2, { from: .2, base: `rotate(${(12 * Math.sin(t * 2)).toFixed(2)}deg)` });
    }
  });
})();
