/* T23 Creative Pop — demo on the shared 15 s intro. Seven-colour card system: keyword stickers, stacked cards, a hub around
 * the presenter, a path journey, a split showcase with real footage and an icon burst, with sparkles, arrows and paint splashes. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, X = T.CP, I = IN; I.setup(C);
  const CARD = { x: 1180, y: 160, w: 620, h: 760, r: 40, s: 1.5 }, HUBC = { x: 780, y: 360, w: 360, h: 360, r: 180, s: 2.6 }, BL = { x: 80, y: 640, w: 330, h: 330, r: 165, s: 3 },
    TL = { x: 60, y: 60, w: 260, h: 260, r: 130, s: 3 }, MID = { x: 760, y: 290, w: 400, h: 400, r: 200, s: 2.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .05, d: .4, L: CARD }, { t: 7.73, d: .45, L: HUBC }, { t: 8.97, d: .45, L: BL }, { t: 12.07, d: .45, L: TL }, { t: 13.77, d: .45, L: MID }];
  C.ringFn = () => ({ color: '#fff', width: 10, shadow: .35 });
  const B = [0, 3.87, 7.73, 8.97, 12.07, 13.77, I.END + .05];
  const sc = (i, build, update) => C.scene({ t0: B[i], t1: B[i + 1] + .03, bg: T.cpBg, quiet: i > 0, build(L) { const st = { sb: T.cpSplashBg(L, i + 2), sp: T.cpSparkles(L, 16, i + 5) }; build(L, st); return st; },
    update(lt, st, t) { T.cpSplashBgAt(st.sb, t); T.cpSparklesAt(st.sp, t, P(lt, 0, .3)); update(st, t, lt); } });

  // 1 · Color Splash: keyword stickers pop on the words, idea bulb, arrow to the presenter
  sc(0, (L, s) => { s.o = T.cpSplash(L, [["HI, I'M EVA", X.YEL, X.INK, -4], ['EVA VIDEO STYLE', X.PINK, '#fff', 3], ['OPEN SOURCE', '#fff', X.INK, -3], ['AI EDITING', X.C[1], X.INK, 2]], 110, 130, 86, { bulb: [880, 560], arrow: [[900, 760], [1020, 820], [1150, 700]] });
      k.sfx('pop', .12, .14); k.sfx('pop', .92, .14, { f: 1100 }); k.sfx('pop', 1.92, .14, { f: 1250 }); k.sfx('pop', 2.45, .14, { f: 1400 }); k.sfx('whoosh', 2.6, .08); },
    (s, t) => T.cpSplashAt(s.o, t, [.1, .9, 1.9, 2.4]));
  // 2 · Vertical Cards: the four styles slide in as she names them
  sc(1, (L, s) => { s.h = T.cpSticker(L, 'CHOOSE A STYLE', 110, 90, X.YEL, X.INK, -2, 64);
      s.o = T.cpStack(L, [{ t: 'Cinematic', i: 'film' }, { t: 'Futuristic tech', i: 'rocket' }, { t: 'Social media', i: 'chat' }, { t: 'Minimalist', i: 'minimal' }], 110, 260, 920, 140, 26);
      s.ar = T.cpArrow(L, [[960, 860], [1060, 930], [1150, 800]], X.INK, 9); k.sfx('whoosh', 3.9, .08); [3.9, 4.75, 5.9, 6.62].forEach((x, i) => k.sfx('pop', x, .13, { f: 800 + i * 160 })); },
    (s, t) => { T.cpStickerAt(s.h, t, 3.9, -2); T.cpStackAt(s.o, t, [3.92, 4.75, 5.9, 6.62]); T.cpArrowAt(s.ar, P(t, 6.9, .5)); });
  // 3 · Circular Hub: the presenter in the middle, seven tool nodes pop around her
  sc(2, (L, s) => { s.h = T.cpSticker(L, 'READY-TO-USE TEMPLATES', 90, 70, X.PINK, '#fff', -3, 54);
      s.o = T.cpHub(L, [{ t: 'Script', i: 'script' }, { t: 'Footage', i: 'footage' }, { t: 'Cut', i: 'cut' }, { t: 'Effects', i: 'effects' }, { t: 'SFX', i: 'sound' }, { t: 'Caption', i: 'caption' }, { t: 'Export', i: 'export' }], 960, 560, 370, 150, -Math.PI / 2 + Math.PI / 7);
      k.sfx('whoosh', 7.75, .1); for (let i = 0; i < 7; i++) k.sfx('pop', 7.85 + i * .12, .08, { f: 800 + i * 90 }); },
    (s, t) => { T.cpStickerAt(s.h, t, 7.78, -3); T.cpHubAt(s.o, t, Array.from({ length: 7 }, (_, i) => 7.85 + i * .12)); });
  // 4 · Path Journey: pick → apply → AI edits
  sc(3, (L, s) => { s.o = T.cpPath(L, [{ t: 'PICK' }, { t: 'APPLY' }, { t: 'AI EDITS' }], [[620, 300], [1060, 600], [1520, 330]], 230);
      s.k = [['your favorite', 540, 470, X.YEL], ['to your footage', 980, 770, '#fff'], ['done ✓', 1460, 500, X.C[3]]].map(([a, x, y, c], i) => T.cpSticker(L, a, x, y, c, X.INK, [-3, 2, -2][i], 44));
      k.sfx('whoosh', 8.97, .08); [8.97, 9.87, 10.67].forEach((x, i) => { k.sfx('pop', x, .14, { f: 900 + i * 180 }); k.sfx('click', x + .35, .06); }); k.sfx('ding', 11.1, .08); },
    (s, t) => { T.cpPathAt(s.o, t, [8.97, 9.87, 10.67]); s.k.forEach((d, i) => T.cpStickerAt(d, t, [9.3, 10.2, 11.0][i], [-3, 2, -2][i])); });
  // 5 · Split Showcase: two panels with real footage
  sc(4, (L, s) => { s.o = T.cpSplit(L, [{ t: 'LESS EDITING', i: 'cut', c: X.C[5] }, { t: 'MORE CREATING', i: 'effects', c: X.C[0] }], 360, 170, 1460, 620, 2); C.setSrc(s.o.p[0].img, '../media/wb/f_01200.jpg'); C.setSrc(s.o.p[1].img, '../media/web/f_00300.jpg');
      k.sfx('whoosh', 12.1, .1); k.sfx('impact', 12.15, .12); k.sfx('whoosh', 12.9, .1); k.sfx('impact', 12.95, .12); },
    (s, t) => T.cpSplitAt(s.o, t, [12.1, 12.9]));
  // 6 · Icon Burst + banner
  sc(5, (L, s) => { s.o = T.cpBurst(L, [{ i: 'idea' }, { i: 'script' }, { i: 'build' }, { i: 'grow' }, { i: 'audience' }, { i: 'monetize' }, { i: 'success' }], 960, 460, 320, 130);
      s.b = T.cpBanner(L, 'TRY EVA VIDEO STYLE TODAY →', 470, 880, X.C[0], -4, 54); s.g = T.cpSticker(L, 'GITHUB.COM/ROVEREVA', 1240, 120, X.YEL, X.INK, 4, 36);
      k.sfx('impact', 13.8, .16); for (let i = 0; i < 7; i++) k.sfx('pop', 13.85 + i * .07, .06, { f: 900 + i * 120 }); k.sfx('whoosh', 14.3, .1); k.sfx('ding', 14.5, .07); },
    (s, t) => { T.cpBurstAt(s.o, t, Array.from({ length: 7 }, (_, i) => 13.85 + i * .07)); T.cpBannerAt(s.b, t, 14.3); T.cpStickerAt(s.g, t, 14.45, 4); });
})();
