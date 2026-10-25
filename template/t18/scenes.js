/* T18 HIST · 历史风 History — demo (18 s). Dust floats in every shot; the globe turns, the compass needle swings. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, H = T.HIS;
  C.src0 = 5; C.end = 18; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const FRAME = { x: 1450, y: 270, w: 380, h: 500, r: 6, s: 1.6 }, TR = { x: 1640, y: 50, w: 220, h: 220, r: 110, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, FRAME, { o: 0 }) }, { t: 1.6, d: .5, L: FRAME }, { t: 9.0, d: .5, L: TR }];
  C.ringFn = () => ({ color: H.WOOD, width: 12, shadow: .45 });

  // H1 · scroll unrolls with the title
  C.scene({ t0: 0, t1: 4.53, bg: T.histBg('paper'), quiet: true, build(L) {
      const st = {}; st.sq = [T.squiggles(L, 10), T.squiggles(L, 1850)]; st.sc = T.scroll(L, 760, 540, 1060, 470);
      st.t = T.histTitle(L, '历史小课堂 · History Lesson', 230, 420, 66, '#fff8ea', { align: 'center', w: 1060, sub: '每一个单词，背后都有一段历史。\n我们从词根开始，读懂它的来历。' }); st.t.style.textShadow = '0 2px 10px rgba(70,35,10,.55)'; st.t.s.style.color = '#fff8ea';
      st.d = T.dust(L, 40, 3); k.sfx('whoosh', .2, .1); k.sfx('ding', 1.6, .07); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.scrollAt(st.sc, P(lt, .1, 1.4)); tf(st.t, { o: P(lt, 1.3, .5), y: 20 * (1 - ease.out3(P(lt, 1.3, .6))) }); } });

  // H2 · quill writes on burnt parchment over dark wood
  C.scene({ t0: 4.5, t1: 9.03, bg: T.histBg('wood'), build(L) {
      const st = {}; st.p = T.parchment(L, 90, 90, 1240, 880, { burnt: true, crumple: true, ghost: true, seed: 7 });
      st.q = T.quill(L, 190); st.h = T.hand(L, ['Every word has a story,', 'and every story', 'begins with one page.', '每个单词，都有它的故事。'], 220, 230, 64, H.INK, st.q);
      st.ink = T.inkPot(L, 1150, 740, 220);
      st.d = T.dust(L, 30, 5); for (let i = 0; i < 16; i++) k.sfx('click', 4.9 + i * .2, .04); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); tf(st.p, { o: P(lt, 0, .4), s: 1.03 - .03 * ease.out3(P(lt, 0, .8)) }); st.p.style.transformOrigin = '50% 50%'; T.handAt(st.h, t, 4.9, 24); } });

  // H3 · antique globe + torn parchment card
  C.scene({ t0: 9.0, t1: 13.53, bg: T.histBg('map'), build(L) {
      const st = {}; st.mb = T.oldMapBg(L, .4); st.g = T.oldGlobe(L, 470, 450, 290);
      st.p = T.parchment(L, 860, 180, 960, 680, { seed: 21, crumple: true });
      st.t = T.histTitle(L, 'The World of Words', 960, 280, 72, H.RUST, { w: 780, sub: '英语里很多单词来自拉丁语和希腊语，\n学词根，就像在读一段历史。' });
      st.d = T.dust(L, 30, 8); k.sfx('whoosh', 9.1, .1); k.sfx('ding', 9.9, .07); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.oldGlobeAt(st.g, t, P(lt, 0, .5)); tf(st.p, slide(lt, .2, .6, 120, 0)); tf(st.t, { o: P(lt, .7, .5) }); } });

  // H4 · learning-journey timeline with medallions + compass
  C.scene({ t0: 13.5, t1: C.end + .05, bg: T.histBg('paper'), build(L) {
      const st = {}; st.c = T.compass(L, 1700, 860, 150); st.t = T.histTitle(L, '学习的旅程 · Learning Journey', 140, 90, 64, H.RUST, { w: 1400 });
      st.tl = T.timelineH(L, [['01', '开始'], ['02', '坚持'], ['03', '进步'], ['04', '突破'], ['05', '收获']], 760);
      st.d = T.dust(L, 30, 11); [0, 1, 2, 3, 4].forEach(i => k.sfx('pop', 13.9 + i * .44, .09, { f: 700 + i * 120 })); return st; },
    update(lt, st, t) { T.dustAt(st.d, t); T.compassAt(st.c, t); st.c.style.opacity = P(lt, .1, .4); tf(st.t, slide(lt, .1, .4, -40, 0)); T.timelineAt(st.tl, t, 13.7); } });
})();
