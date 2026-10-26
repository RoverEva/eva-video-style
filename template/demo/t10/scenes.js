/* T10 HUD Keynote — demo on the shared 15 s intro (glowing curve, BREAKING title, globe, file tree, metallic hero title) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, I = IN; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const CARD = { x: 1230, y: 70, w: 560, h: 640, r: 8, s: 1.5 }, SMALL = { x: 1440, y: 120, w: 380, h: 400, r: 8, s: 2 }, CIRC = { x: 1600, y: 70, w: 240, h: 240, r: 120, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .45, L: SMALL }, { t: 7.73, d: .45, L: CIRC }, { t: 12.07, d: .45, L: CARD }, { t: 13.7, d: .4, L: CIRC }];
  C.ringFn = t => (t < 7.8 || (t >= 12.07 && t < 13.75)) ? { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' } : { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 };
  const frame = L => T.hudFrame(L, 'EVA · KEYNOTE', '10');

  // K1 · HI → BREAKING → glowing S-curve with gold headline
  C.scene({ t0: 0, t1: 3.9, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, "HI, I'M ", 'EVA', 110, 110, 64, '#fff');
      st.b = T.breaking(L, 110, 250, 'NEW · OPEN SOURCE'); st.m = el(L, 'div', 'abs disp', { left: '110px', top: '300px', fontSize: '120px', color: '#fff' }, 'EVA VIDEO STYLE');
      st.c = T.curve(L, 110, 500, 1000, 260); st.g = el(L, 'div', 'abs disp', { left: '600px', top: '560px', fontSize: '70px', color: T.HUD.GOLD, textShadow: '0 0 30px rgba(245,184,61,.45)' }, 'AI VIDEO-EDITING SKILL');
      k.sfx('pop', .12, .1); k.sfx('impact', .9, .16); k.sfx('riser', 1.4, .08, { d: .6 }); k.sfx('ding', 1.95, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .1, .4, -40, 0)); st.b.style.opacity = (Math.floor(lt * 4) % 2 ? .45 : 1) * P(lt, .9, .1);
      const p = pop(t, .9, .45, 1.4); tf(st.m, { s: 1.2 - .2 * p.s, o: p.o }); st.m.style.transformOrigin = '0 50%'; st.m.style.filter = `blur(${8 * (1 - P(t, .9, .35))}px)`;
      T.curveAt(st.c, ease.io3(P(t, 1.5, 1.6))); tf(st.g, slide(t, 1.95, .45, 0, 30)); } });

  // K2 · four styles around a turning dotted globe
  C.scene({ t0: 3.87, t1: 7.76, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.g = T.globe(L, 980, 620, 260); st.h = T.title(L, 'CHOOSE A ', 'STYLE', 110, 110, 54, T.HUD.GOLD);
      st.s = I.STYLES.map((s, i) => T.kicker(L, '◆ ' + s, 110, 330 + i * 110, i % 2 ? T.HUD.BLUE : '#fff'));
      st.s.forEach(e => e.style.fontSize = '40px'); k.sfx('whoosh', 3.9, .1); [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x + .05, .1, { f: 900 + i * 100 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.globeAt(st.g, lt, ease.io3(P(lt, .3, 1.2))); st.g.cv.style.opacity = P(lt, .05, .4); tf(st.h, slide(lt, .1, .4, -40, 0));
      st.s.forEach((e, i) => tf(e, slide(t, [3.95, 4.73, 5.87, 6.6][i], .35, -40, 0))); } });

  // K3 · glowing orb → file icon → the real project files
  C.scene({ t0: 7.73, t1: 12.1, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, 'READY-TO-USE ', 'TEMPLATES', 110, 110, 54);
      st.orb = T.orb(L, 400, 560, 140); st.f = T.fileIcon(L, 310, 450, 180, 'T22');
      st.r = T.rows(Z(L, 1.5, 640, 300), 640, 300, [['👆', 'Pick your favorite', 'T01 – T22'], ['🎞️', 'Apply it to your footage', 'video + SRT'], ['🤖', 'Let AI do the editing', 'motion · captions · SFX']]);
      k.sfx('riser', 7.8, .08, { d: .6 }); k.sfx('pop', 8.5, .12); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 120 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, { o: P(lt, .1, .3) }); const o = P(lt, 0, .3) * (1 - P(lt, .75, .2)); tf(st.orb, { s: .9 + .06 * Math.sin(lt * 9), o });
      const f = P(lt, .8, .3); st.f.s.style.opacity = f; st.f.t.style.opacity = f; st.r.forEach((r, i) => tf(r, slide(t, [8.97, 9.87, 10.67][i], .35, -40, 0))); } });

  // K4 · less / more → metallic hero title
  C.scene({ t0: 12.07, t1: C.end + .05, bg: `radial-gradient(900px 500px at 50% 45%, #1b2240, ${T.HUD.BG} 70%)`, build(L) {
      const st = {}; st.fr = frame(L); st.a = T.title(L, 'LESS TIME ', 'EDITING', 110, 300, 110, '#fff'); st.b = T.title(L, 'MORE TIME ', 'CREATING', 110, 480, 110, T.HUD.GOLD);
      st.k = K.center(T.kicker(L, 'TRY IT TODAY · GITHUB.COM/ROVEREVA/EVA-VIDEO-STYLE', 0, 330, T.HUD.DIM)); st.m = T.metal(L, 'EVA STYLE', 380, 210);
      k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .12); k.sfx('riser', 13.5, .06, { d: .3 }); k.sfx('impact', 13.8, .2); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); const a = t < 13.77; [st.a, st.b].forEach(e => e.style.display = a ? '' : 'none'); [st.k, st.m.t].forEach(e => e.style.display = a ? 'none' : '');
      tf(st.a, slide(t, 12.1, .4, -40, 0)); tf(st.b, slide(t, 12.9, .4, -40, 0)); T.metalAt(st.m, t - 13.77, .15); tf(st.k, { o: P(t, 14.3, .4) }); } });
})();
