/* T18 History — demo on the shared 15 s intro. Dust floats in every shot; the globe turns, the compass needle swings. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, H = T.HIS, I = IN; I.setup(C);
  const FRAME = { x: 1450, y: 270, w: 380, h: 500, r: 6, s: 1.6 }, TR = { x: 1640, y: 50, w: 220, h: 220, r: 110, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, FRAME, { o: 0 }) }, { t: .1, d: .5, L: FRAME }, { t: 7.73, d: .5, L: TR }];
  C.ringFn = () => ({ color: H.WOOD, width: 12, shadow: .45 });

  // H1 · scroll unrolls with the title
  C.scene({ t0: 0, t1: 3.9, bg: T.histBg('paper'), quiet: true, build(L) {
      const st = {}; st.sq = [T.squiggles(L, 10)]; st.sc = T.scroll(L, 700, 540, 1060, 470);
      st.t = T.histTitle(L, 'Meet Eva Video Style', 170, 420, 72, '#fff8ea', { align: 'center', w: 1060, sub: "Hi, I'm Eva.\nAn open-source AI video-editing skill." }); st.t.style.textShadow = '0 2px 10px rgba(70,35,10,.55)'; st.t.s.style.color = '#fff8ea'; st.t.s.style.fontSize = '40px'; st.t.s.style.lineHeight = '1.4';
      st.d = T.dust(L, 40, 3); k.sfx('whoosh', .2, .1); k.sfx('ding', .95, .07); k.sfx('click', 1.95, .06); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.scrollAt(st.sc, P(lt, .1, .8)); tf(st.t, { o: P(lt, .9, .4), y: 20 * (1 - ease.out3(P(lt, .9, .5))) }); } });

  // H2 · quill writes the four styles on burnt parchment
  C.scene({ t0: 3.87, t1: 7.76, bg: T.histBg('wood'), build(L) {
      const st = {}; st.p = T.parchment(L, 90, 90, 1240, 880, { burnt: true, crumple: true, ghost: true, seed: 7 });
      st.q = T.quill(L, 190); st.h = T.hand(L, ['Choose a style:', 'cinematic, futuristic tech,', 'social media', 'or minimalist.'], 220, 230, 72, H.INK, st.q);
      st.ink = T.inkPot(L, 1150, 740, 220); st.d = T.dust(L, 30, 5); for (let i = 0; i < 16; i++) k.sfx('click', 3.95 + i * .2, .04); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); tf(st.p, { o: P(lt, 0, .4), s: 1.03 - .03 * ease.out3(P(lt, 0, .8)) }); st.p.style.transformOrigin = '50% 50%'; T.handAt(st.h, t, 3.9, 30); } });

  // H3 · antique globe + torn parchment card
  C.scene({ t0: 7.73, t1: 12.1, bg: T.histBg('map'), build(L) {
      const st = {}; st.mb = T.oldMapBg(L, .4); st.g = T.oldGlobe(L, 470, 470, 290);
      st.p = T.parchment(L, 860, 300, 960, 640, { seed: 21, crumple: true });
      st.t = T.histTitle(L, 'Ready-to-use templates', 960, 400, 66, H.RUST, { w: 780 });
      st.s = ['I.  Pick your favorite', 'II.  Apply it to your footage', 'III.  Let AI do the editing'].map((s, i) => el(L, 'div', 'abs', { left: '970px', top: (530 + i * 100) + 'px', fontFamily: "'Playfair Display', Georgia, serif", fontStyle: 'italic', fontSize: '54px', color: H.INK, zIndex: 8 }, s));
      st.d = T.dust(L, 30, 8); k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach(x => k.sfx('click', x, .08)); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.oldGlobeAt(st.g, t, P(lt, 0, .5)); tf(st.p, slide(lt, .2, .6, 120, 0)); tf(st.t, { o: P(lt, .7, .5) }); st.s.forEach((e, i) => tf(e, slide(t, [8.97, 9.87, 10.67][i], .4, 40, 0))); } });

  // H4 · journey timeline with medallions + compass
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.histBg('paper'), build(L) {
      const st = {}; st.c = T.compass(L, 1700, 860, 150); st.t = T.histTitle(L, 'Less time editing, more time creating', 140, 300, 64, H.RUST, { w: 1400 });
      st.tl = T.timelineH(L, [['01', 'Footage'], ['02', 'Template'], ['03', 'AI edit'], ['04', 'Create']], 760);
      st.cta = T.histTitle(L, 'Try Eva Video Style today →', 140, 450, 48, H.INK, { w: 1400 });
      st.d = T.dust(L, 30, 11); [0, 1, 2, 3].forEach(i => k.sfx('pop', 12.4 + i * .4, .09, { f: 700 + i * 120 })); k.sfx('ding', 13.8, .07); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.compassAt(st.c, t); st.c.style.opacity = P(lt, .1, .4); tf(st.t, slide(lt, .05, .4, -40, 0)); T.timelineAt(st.tl, t, 12.3); tf(st.cta, { o: P(t, 13.8, .4) }); } });
})();
