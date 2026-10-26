/* T12 Old Newspaper — demo on the shared 15 s intro. Photos and film frames are real frames from the HatchElite recordings and cartoon clips. */
(function () {
  const C = EV, { el, tf, pop, slide, wipe, P, ease, clamp } = C, k = K, T = K.T, N = T.NEWS, I = IN; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const S = I.SHOTS, CARD = { x: 1250, y: 210, w: 540, h: 640, r: 2, s: 1.5 }, SMALL = { x: 1560, y: 60, w: 300, h: 360, r: 2, s: 2 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .45, L: SMALL }, { t: 7.73, d: .45, L: Object.assign({}, SMALL, { o: 0 }) }, { t: 12.07, d: .4, L: CARD }];
  C.ringFn = () => ({ color: '#f3ecdc', width: 12, shadow: .5 });   // presenter stays in natural colour

  // P1 · front page: masthead, headline, columns; presenter as the front-page photo
  C.scene({ t0: 0, t1: 3.9, bg: T.newsBg(false), quiet: true, build(L) {
      const st = {}; st.m = T.masthead(L, 'THE EVA TIMES', "HI, I'M EVA · OPEN-SOURCE EDITION", 110, 50, 1060);
      st.h = T.headline(L, 'Meet Eva Video Style', 110, 290, 100); st.c = T.columns(L, 110, 460, 1060, 520, 3, 4);
      st.b = T.brush(L, 'OPEN SOURCE', 420, 620, 96, -6); st.tp = T.tape(L, 1450, 186, 150, -6); st.g = T.grain(L, .2);
      k.sfx('impact', .15, .14); k.sfx('click', .9, .08); k.sfx('impact', 1.95, .18); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.m, { o: P(lt, 0, .3), s: 1.05 - .05 * ease.outExpo(P(lt, 0, .6)) }); st.m.style.transformOrigin = '50% 0';
      tf(st.h, slide(lt, .9, .4, -60, 0)); wipe(st.c, ease.out3(P(lt, 1.2, 1.2)), 'd'); tf(st.b, { s: 1.6 - .6 * ease.outBack(P(t, 1.95, .3), 2), o: P(t, 1.95, .08), r: -6 }); } });

  // P2 · collage wall: film strip of real frames, the four styles as clippings
  C.scene({ t0: 3.87, t1: 7.76, bg: T.newsBg(true), build(L) {
      const st = {}; st.f = T.filmstrip(L, 60, 120, [S[0], S[6], S[8], S[9]], 260, -3);
      st.cl = I.STYLES.map((s, i) => { const d = el(L, 'div', 'abs', { left: (110 + (i % 2) * 640) + 'px', top: (520 + Math.floor(i / 2) * 200) + 'px', background: '#f3ecdc', padding: '16px 34px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '70px', color: N.INK, boxShadow: '0 12px 30px rgba(0,0,0,.35)', transformOrigin: '50% 50%' }, s); d.r = [-3, 2, 2.5, -2][i]; return d; });
      st.u = T.scribble(L, 'underline', 120, 650, 520, N.RED); st.g = T.grain(L, .25);
      k.sfx('whoosh', 3.9, .08); [3.9, 4.73, 5.87, 6.6].forEach(x => k.sfx('click', x + .05, .1)); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.f, slide(lt, .05, .6, -400, 0)); st.f.style.transform += ' rotate(-3deg)';
      st.cl.forEach((d, i) => { const q = pop(t, [3.95, 4.73, 5.87, 6.6][i], .35, 1.5); tf(d, { s: q.s, o: q.o, r: d.r }); }); T.scribbleAt(st.u, P(t, 4.3, .4)); } });

  // P3 · typewriter on paper: ready-to-use templates, pick / apply / AI
  C.scene({ t0: 7.73, t1: 12.1, bg: T.newsBg(false), build(L) {
      const st = {}; st.slip = el(L, 'div', 'abs', { left: '160px', top: '180px', width: '1300px', height: '330px', background: '#f6efde', boxShadow: '0 20px 50px rgba(0,0,0,.25)', transform: 'rotate(-1.5deg)' });
      st.k = el(st.slip, 'div', 'abs', { left: '50px', top: '40px', fontFamily: N.TYPE, fontSize: '28px', color: '#8a7f6a' }, 'Classifieds · No. 22');
      st.ty = T.typed(st.slip, 'Ready-to-use templates.', 50, 130, 84, N.INK);
      st.st = ['① Pick your favorite', '② Apply it to your footage', '③ Let AI do the editing'].map((s, i) => el(L, 'div', 'abs', { left: '220px', top: (600 + i * 110) + 'px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '64px', color: i === 2 ? N.RED : N.INK, transformOrigin: '0 50%' }, s));
      st.ar = T.scribble(L, 'arrow', 1150, 760, 260, N.RED, 160);
      st.g = T.grain(L, .2); for (let i = 0; i < 16; i++) k.sfx('click', 7.85 + i * .06, .05); [8.97, 9.87, 10.67].forEach(x => k.sfx('pop', x, .1)); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.slip, { y: 40 * (1 - ease.outExpo(P(lt, 0, .5))), o: P(lt, 0, .2), r: -1.5 }); T.typedAt(st.ty, t, 7.85, 18);
      st.st.forEach((e, i) => tf(e, slide(t, [8.97, 9.87, 10.67][i], .35, -50, 0))); T.scribbleAt(st.ar, P(t, 10.9, .4)); } });

  // P4 · red book-cover title card + CTA
  C.scene({ t0: 12.07, t1: C.end + .05, bg: '#14110e', build(L) {
      const st = {}; st.cv = T.cover(L, 'EVA', 110, 160, 260, 680);
      st.k = el(L, 'div', 'abs', { left: '440px', top: '220px', fontFamily: N.SERIF, fontSize: '30px', color: N.RED, borderLeft: `4px solid ${N.RED}`, paddingLeft: '14px' }, '2026 · OPEN SOURCE · MIT');
      st.a = T.headline(L, 'Less time editing,', 440, 300, 74, '#f1e6cf'); st.b = T.headline(L, 'more time creating.', 440, 410, 74, '#f1e6cf');
      st.n1 = el(L, 'div', 'abs', { left: '446px', top: '600px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '56px', color: N.RED }, 'Try Eva Video Style today →'); st.g = T.grain(L, .22);
      k.sfx('impact', 12.1, .14); k.sfx('click', 12.9, .1); k.sfx('pop', 13.8, .12); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.cv, { sx: ease.outExpo(P(lt, .05, .6)), o: 1 }); tf(st.k, { o: P(lt, .4, .3) }); tf(st.a, slide(t, 12.1, .45, -40, 0)); tf(st.b, slide(t, 12.9, .45, -40, 0)); tf(st.n1, pop(t, 13.8, .35, 1.5)); } });
})();
