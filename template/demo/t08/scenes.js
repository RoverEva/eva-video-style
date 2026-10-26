/* T08 Neon Explainer — demo on the shared 15 s intro (pixel title → echo stack → neon-graded presenter → real screens → article → dot-grid diagram) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, I = IN; I.setup(C);
  const FULL = { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 }, TR = { x: 1590, y: 36, w: 290, h: 290, r: 145, s: 3 }, CARD = { x: 1240, y: 200, w: 560, h: 680, r: 30, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, FULL, { o: 0 }) }, { t: 1.9, d: 0, L: FULL }, { t: 7.73, d: .5, L: TR }, { t: 12.07, d: .5, L: CARD }];
  C.ringFn = () => ({ color: T.NEON.CREAM, width: 5, glow: 'rgba(255,214,90,.55)' });

  // N1 · pixel "HI!" → echo stack "EVA VIDEO STYLE" (black, presenter hidden)
  C.scene({ t0: 0, t1: 1.93, bg: '#030305', quiet: true, build(L) {
      const st = {}; st.px = T.pixel(L, "HI, I'M EVA", 470, 200); st.echo = T.echo(L, 'EVA VIDEO STYLE', 120, 3);
      k.sfx('impact', .15, .16); k.sfx('riser', .5, .1, { d: .4 }); k.sfx('pop', .9, .12); return st; },
    update(lt, st) { const a = lt < .9; st.px.style.display = a ? 'block' : 'none'; st.echo.style.display = a ? 'none' : 'block';
      tf(st.px, { s: 1 + .04 * lt, o: clamp(lt * 4) * (lt % .25 < .03 && lt < .5 ? .3 : 1) });
      st.echo.rows.forEach((r, i) => tf(r, { y: (1 - ease.outExpo(P(lt, .9 + Math.abs(i - 3) * .06, .5))) * (i - 3) * 60, o: P(lt, .9 + Math.abs(i - 3) * .06, .2) })); } });

  // N2 · full-bleed presenter in a neon grade, glowing side headline
  C.scene({ t0: 1.9, t1: 3.9, z: 60, build(L) {
      const st = {}; T.neonGrade(L);
      st.a = T.glow(L, 'Open-source', 110, 330, 96); st.b = T.glow(L, 'AI video-editing skill', 110, 450, 64, { color: '#fff' });
      k.sfx('pop', 1.95, .12); k.sfx('pop', 2.5, .12, { f: 1100 }); return st; },
    update(lt, st, t) { tf(st.a, slide(t, 1.95, .45, -80, 0)); tf(st.b, slide(t, 2.5, .45, -80, 0)); } });

  // N3 · four styles: real screens pop around the presenter
  C.scene({ t0: 3.87, t1: 7.76, z: 60, quiet: true, build(L) {
      const st = {}; T.neonGrade(L);
      st.c = T.collage(L, [I.SHOTS[0], I.SHOTS[6], I.SHOTS[8], I.SHOTS[3]], [[60, 70, 460, -4], [1400, 80, 440, 5], [70, 600, 420, 3], [1430, 620, 420, -5]]);
      st.l = I.STYLES.map((s, i) => T.glow(L, s, [80, 1420, 90, 1450][i], [370, 360, 870, 560][i], 40, { fontStyle: 'normal' }));
      [3.87, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .1, { f: 800 + i * 120 })); return st; },
    update(lt, st, t) { const at = [3.87, 4.73, 5.87, 6.6];
      st.c.forEach((e, i) => tf(e, Object.assign(pop(t, at[i], .4, 1.6), { r: [-4, 5, 3, -5][i] })));
      st.l.forEach((e, i) => tf(e, pop(t, at[i] + .1, .35, 1.6))); } });

  // N4 · article card with a highlighter sweep, then a speech bubble
  C.scene({ t0: 7.73, t1: 12.1, bg: '#d9d9d6', build(L) {
      const st = {}; st.a = T.article(L, 200, 300, 1150, 'Ready-to-use templates:', 'pick one, apply it', 'to your footage.', 'EVA VIDEO STYLE · README');
      st.b = T.bubble(L, 'Let AI do the editing!', 180, 300, 1150, '🤖');
      k.sfx('whoosh', 7.75, .08); k.sfx('click', 8.97, .08); k.sfx('whoosh', 9.87, .08); k.sfx('pop', 10.67, .14); return st; },
    update(lt, st, t) { const a = t < 10.67; st.a.style.display = a ? '' : 'none'; [st.b.box, st.b.e].forEach(e => e && (e.style.display = a ? 'none' : ''));
      tf(st.a, slide(lt, .05, .5, 0, 60)); T.articleAt(st.a, P(t, 8.97, 1.0)); T.bubbleAt(st.b, t, 10.67, 24); } });

  // N5 · dot-grid diagram: less editing, more creating
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.dotsBg, cls: 'dotgrid-w', build(L) {
      const st = {}; st.ch = T.glow(L, 'Less time editing, more time creating.', 120, 150, 64, { fontStyle: 'normal' });
      st.s = T.slots(L, 120, 320, ['EDITING', 'CREATING'], ['less', 'more'], 420);
      st.tg = T.tag(L, 'TRY IT TODAY', 120, 640, ['Eva Video Style', 'open source · MIT', 'github.com/RoverEva']);
      k.sfx('pop', 12.1, .12); k.sfx('pop', 12.9, .12, { f: 1100 }); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { tf(st.ch, slide(t, 12.1, .4, -60, 0)); T.slotsAt(st.s, t, 12.1, [12.1, 12.9]); T.tagAt(st.tg, t, 13.8, .25); } });
})();
