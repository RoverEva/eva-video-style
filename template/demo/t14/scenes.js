/* T14 Future Style — demo on the shared 15 s intro. The wave floor moves in every shot; the globe turns slowly. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, F = T.FUT, I = IN; I.setup(C);
  const LOW = { x: 1180, y: 320, w: 300, h: 300, r: 150, s: 2.8 }, CARD = { x: 1280, y: 190, w: 500, h: 620, r: 28, s: 1.5 }, RING = { x: 1100, y: 330, w: 360, h: 360, r: 180, s: 2.6 }, TR = { x: 1620, y: 60, w: 230, h: 230, r: 115, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .45, L: LOW }, { t: 7.73, d: .5, L: TR }, { t: 12.07, d: .6, L: RING }];
  C.ringFn = () => ({ color: F.CYAN, width: 3, glow: 'rgba(46,230,255,.55)', shadow: .5 });

  // F1 · title over the moving wave floor
  C.scene({ t0: 0, t1: 3.9, bg: T.futBg, quiet: true, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 600, amp: 60 }); st.hi = el(L, 'div', 'abs', { left: '134px', top: '110px', fontFamily: F.SANS, fontWeight: 900, fontSize: '48px', color: F.CYAN, textShadow: `0 0 20px ${F.CYAN}` }, "HI, I'M EVA");
      st.ti = T.futTitle(L, 'EVA VIDEO', 'STYLE', 'Open-source AI video editing', 130, 190, 130);
      k.sfx('riser', .1, .08, { d: .8 }); k.sfx('impact', .9, .18); k.sfx('ding', 1.95, .07); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.futTitleAt(st.ti, t, .9); tf(st.hi, slide(t, .1, .4, -60, 0)); } });

  // F2 · four styles as RULE 1–4 beside a turning globe
  C.scene({ t0: 3.87, t1: 7.76, bg: T.futBg, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 560, amp: 70 }); st.g = T.globeT(L, 1330, 470, 330);
      st.r = T.rules(L, ['CINEMATIC', 'FUTURISTIC', 'SOCIAL', 'MINIMAL'], 130, 90, 'STYLE', 96);
      k.sfx('whoosh', 3.9, .1); [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x + .05, .1, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.globeTAt(st.g, t, P(lt, 0, .8)); const at = [3.9, 4.73, 5.87, 6.6]; st.r.forEach((r, i) => { tf(r, slide(t, at[i], .45, -70, 0)); if (r.line) r.line.style.transform = `scaleX(${ease.outExpo(P(t, at[i] + .3, .6))})`; }); } });

  // F3 · circuit chip: ready-to-use templates, pick / apply / AI
  C.scene({ t0: 7.73, t1: 12.1, bg: T.futBg, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 520, amp: 55, speed: 1.2 }); st.c = T.chip(L, 1380, 700, 300);
      st.ti = T.futTitle(L, 'READY-TO-USE', 'TEMPLATES', 'Pick · Apply · Let AI edit', 130, 150, 120);
      st.s = ['01  PICK YOUR FAVORITE', '02  APPLY TO YOUR FOOTAGE', '03  LET AI DO THE EDITING'].map((s, i) => el(L, 'div', 'abs disp', { left: '130px', top: (560 + i * 110) + 'px', fontSize: '64px', color: i === 2 ? F.CYAN : '#fff', textShadow: `0 0 24px ${F.CYAN}` }, s));
      k.sfx('whoosh', 7.75, .1); k.sfx('impact', 8.1, .14); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.chipAt(st.c, t); st.c.cv.style.opacity = P(lt, .1, .5); T.futTitleAt(st.ti, t, 8.0); st.s.forEach((e, i) => tf(e, slide(t, [8.97, 9.87, 10.67][i], .35, -60, 0))); } });

  // F4 · wireframe ring with the presenter inside it
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.futBg, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 600, amp: 60, speed: .9 }); st.o = T.torus(L, 1280, 510, 300, 70);
      st.ti = T.futTitle(L, 'LESS EDITING', 'MORE CREATING', 'Try Eva Video Style today →', 130, 240, 110);
      k.sfx('riser', 12.1, .08, { d: .6 }); k.sfx('impact', 12.9, .14); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.torusAt(st.o, t); st.o.cv.style.opacity = P(lt, 0, .6); T.futTitleAt(st.ti, t, 12.2); } });
})();
