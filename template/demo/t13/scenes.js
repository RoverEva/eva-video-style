/* T13 Tech Blue — demo on the shared 15 s intro. Screens are real recordings; copy describes Eva Video Style itself. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, X = T.TECH, I = IN; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const CARD = { x: 1280, y: 230, w: 480, h: 600, r: 4, s: 1.5 }, CIRC = { x: 1620, y: 60, w: 230, h: 230, r: 115, s: 3 }, SIDE = { x: 1440, y: 120, w: 400, h: 500, r: 4, s: 1.7 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .1, d: .4, L: CARD }, { t: 3.87, d: .45, L: CIRC }, { t: 7.73, d: .45, L: SIDE }, { t: 12.07, d: .45, L: CIRC }];
  C.ringFn = () => ({ color: X.CYAN, width: 2, glow: 'rgba(98,240,255,.35)', shadow: .5, hud: X.CYAN });

  // B1 · title slide inside the HUD frame
  C.scene({ t0: 0, t1: 3.9, bg: T.techBg, quiet: true, build(L) {
      const st = {}; st.f = T.techFrame(L); st.hi = T.techTitle(L, "Hi, I'm Eva", '', 200, 260, 64); st.hi.b.remove();
      st.t = T.techTitle(L, 'Eva Video Style', 'An open-source AI video-editing skill', 200, 400, 120);
      k.sfx('riser', .1, .08, { d: .7 }); k.sfx('impact', .9, .14); k.sfx('pop', 1.95, .1); return st; },
    update(lt, st) { T.techFrameAt(st.f, P(lt, 0, 1.4)); tf(st.hi, slide(lt, .1, .4, -40, 0)); tf(st.t.a, slide(lt, .9, .5, -60, 0)); tf(st.t.b, { o: P(lt, 1.95, .4) }); } });

  // B2 · table of contents: the four styles
  C.scene({ t0: 3.87, t1: 7.76, bg: T.techBg, build(L) {
      const st = {}; st.c1 = T.corner(L, 1180, 90); st.c2 = T.corner(L, 120, 820, true);
      st.h = T.techTitle(L, 'Choose a Style', '', 0, 120, 76, 'center'); st.h.b.remove();
      st.toc = T.toc(Z(L, 1.6, 960, 600), [['Cinematic', 'film light · big type'], ['Futuristic Tech', 'HUD · glow · data'], ['Social Media', 'fast cuts · stickers'], ['Minimalist', 'quiet type · one line']], 640);
      [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .07, { f: 800 + i * 80 })); return st; },
    update(lt, st, t) { tf(st.h, { o: P(lt, .05, .3) }); st.c1.style.opacity = st.c2.style.opacity = P(lt, 0, .3);
      st.toc.r.forEach((r, i) => tf(r, slide(t, [3.9, 4.73, 5.87, 6.6][i], .45, i % 2 ? 60 : -60, 0))); } });

  // B3 · real screen band + info cards (presenter in a side card)
  C.scene({ t0: 7.73, t1: 12.1, bg: T.techBg, build(L) {
      const st = {}; st.p = T.panel(L, 120, 120, 1180, 220, 'Ready-to-use Templates', 'T01 – T21 · bilingual captions · no background music');
      st.b = T.band(L, '../media/web/f_00000.jpg', 0, 380, 1380, 300);
      st.a = T.infoCard(L, 'doc', 'Pick', 'your favorite template', 80, 720, 400); st.c = T.infoCard(L, 'window', 'Apply', 'it to your footage', 500, 720, 400); st.d = T.infoCard(L, 'cloud', 'AI edits', 'motion, captions, sound', 920, 720, 420);
      k.sfx('whoosh', 7.75, .08); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 120 })); return st; },
    update(lt, st, t) { T.panelAt(st.p, P(lt, .05, .9)); const u = ease.outExpo(P(t, 8.6, .6)); st.b.style.clipPath = `inset(0 ${100 - 100 * u}% 0 0)`;
      const im = st.b.querySelector && st.b.querySelector('img'); if (im) C.setSrc(im, C.seq('../media/web', Math.max(0, t - 8.6) * 1.4, 451));
      [st.a, st.c, st.d].forEach((e, i) => tf(e, slide(t, [8.97, 9.87, 10.67][i], .4, -40, 0))); } });

  // B4 · three outlined column cards
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.techBg, build(L) {
      const st = {}; st.c1 = T.corner(L, 1240, 70); st.h = T.techTitle(L, 'Less Editing · More Creating', '', 0, 80, 64, 'center'); st.h.b.remove();
      st.cards = [T.colCard(L, 250, 230, 440, 640, 'doc', 'Script', ['your video + SRT', 'EN or CN + EN', 'facts stay yours'], '01'),
                  T.colCard(L, 740, 230, 440, 640, 'window', 'Template', ['pick T01 – T21', 'mix per section', 'face always visible'], '02'),
                  T.colCard(L, 1230, 230, 440, 640, 'cloud', 'Try it', ['open source · MIT', 'github.com/RoverEva', 'eva-video-style'], '03')];
      k.sfx('whoosh', 12.1, .08); [12.4, 12.9, 13.8].forEach((x, i) => k.sfx('pop', x, .1, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { tf(st.h, { o: P(lt, .05, .3) }); st.c1.style.opacity = P(lt, 0, .3); st.cards.forEach((c, i) => { const u = ease.outExpo(P(t, [12.4, 12.9, 13.8][i], .5)); tf(c, { y: 60 * (1 - u), o: u }); }); } });
})();
