/* T08 NEON · 霓虹讲解 Neon Explainer — demo (16 s) */
(function () {
  const C = EV, { el, tf, pop, slide, wipe, P, ease, clamp } = C, k = K, T = K.T;
  C.src0 = 0; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  C.evaKeys = [
    { t: 0, d: 0, L: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1, o: 0 } },
    { t: 2.5, d: 0, L: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1, o: 1 } },
    { t: 8.0, d: .5, L: { x: 1590, y: 36, w: 290, h: 290, r: 145, s: 3, o: 1 } },
  ];
  C.ringFn = t => ({ color: T.NEON.CREAM, width: 5, glow: 'rgba(255,214,90,.55)' });

  // N1 · pixel title → echo stack (black, Eva hidden)
  C.scene({ t0: 0, t1: 2.53, bg: '#030305', quiet: true, build(L) {
      const st = {}; st.px = T.pixel(L, 'AI 时代', 470, 260); st.echo = T.echo(L, 'EVA STYLE', 120, 3);
      k.sfx('impact', .15, .16); k.sfx('riser', .9, .1, { d: .5 }); k.sfx('pop', 1.4, .12); return st; },
    update(lt, st) { const a = lt < 1.4; st.px.style.display = a ? 'block' : 'none'; st.echo.style.display = a ? 'none' : 'block';
      tf(st.px, { s: 1 + .04 * lt, o: clamp(lt * 4) * (lt % .25 < .03 && lt < .5 ? .3 : 1) });
      st.echo.rows.forEach((r, i) => tf(r, { y: (1 - ease.outExpo(P(lt, 1.4 + Math.abs(i - 3) * .06, .5))) * (i - 3) * 60, o: P(lt, 1.4 + Math.abs(i - 3) * .06, .2) })); } });

  // N2 · full-bleed Eva in a neon grade + glowing side headline
  C.scene({ t0: 2.5, t1: 5.53, z: 60, quiet: false, build(L) {
      const st = {}; T.neonGrade(L);
      st.a = T.glow(L, '最简单的方式', 110, 300, 92); st.b = T.glow(L, '上手 Eva Video Style', 110, 420, 64, { color: '#fff' });
      k.sfx('pop', 2.8, .12); k.sfx('pop', 3.7, .12, { f: 1100 }); return st; },
    update(lt, st, t) { tf(st.a, slide(t, 2.8, .45, -80, 0)); tf(st.b, slide(t, 3.7, .45, -80, 0)); } });

  // N3 · real screenshots pop around Eva
  C.scene({ t0: 5.5, t1: 8.03, z: 60, quiet: true, build(L) {
      const st = {}; T.neonGrade(L);
      st.c = T.collage(L, ['../../media/screen/f_00300.jpg', '../../media/screen/f_00600.jpg', '../../media/screen/f_01500.jpg', '../../media/screen/f_01800.jpg', '../../media/screen/f_03000.jpg'],
        [[60, 70, 460, -4], [1400, 80, 440, 5], [70, 600, 420, 3], [1430, 620, 420, -5], [1480, 360, 330, 2]]);
      st.t = T.glow(L, 'REAL SCREENS · 真实画面', 640, 960, 40, { fontStyle: 'normal' });
      for (let i = 0; i < 5; i++) k.sfx('pop', 5.7 + i * .18, .1, { f: 800 + i * 90 }); return st; },
    update(lt, st, t) { T.collageAt(st.c, t, 5.7, .18); tf(st.t, pop(t, 6.8, .35)); } });

  // N4 · article card with highlighter sweep (illustrative copy)
  C.scene({ t0: 8.0, t1: 10.53, bg: '#d9d9d6', build(L) {
      const st = {}; st.a = T.article(L, 240, 300, 1100, '用 AI 做视频剪辑：', 'Eva Video Style', '的模版库', 'EVA · NOTES'); k.note(L, '示意 · ILLUSTRATIVE', 160, 1000, '#333');
      k.sfx('click', 8.9, .08); k.sfx('whoosh', 9.0, .08); return st; },
    update(lt, st, t) { tf(st.a, slide(lt, .05, .5, 0, 60)); T.articleAt(st.a, P(t, 8.9, .6)); } });

  // N5 · speech bubble question on white
  C.scene({ t0: 10.5, t1: 13.03, bg: '#ffffff', build(L) {
      const st = {}; st.b = T.bubble(L, '什么是"视频模版"?', 180, 260, 1100, '🤔'); k.sfx('pop', 10.7, .14); return st; },
    update(lt, st, t) { T.bubbleAt(st.b, t, 10.7, 9); } });

  // N6 · dot-grid concept diagram: character + slots + tags
  C.scene({ t0: 13.0, t1: C.end + .05, bg: T.dotsBg, cls: 'dotgrid-w', build(L) {
      const st = {}; st.ch = k.emoji(L, '👩‍💻', 170, 860, 90);
      st.s = T.slots(L, 470, 400, ['模版 1', '模版 2', '模版 3'], ['开场', '讲解', '结尾']);
      st.tg = T.tag(L, '素材', 470, 660, ['你的口播视频', '双语字幕 SRT', '真实录屏']);
      k.sfx('pop', 13.2, .12); [13.8, 14.2, 14.6].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('click', 15.0, .08); return st; },
    update(lt, st, t) { tf(st.ch, pop(t, 13.1, .4, 2)); T.slotsAt(st.s, t, 13.4, [13.8, 14.2, 14.6]); T.tagAt(st.tg, t, 15.0, .25); } });
})();
