/* T11 HUD Dashboard — demo on the shared 15 s intro (terminal, checks, flow, quote, toggle/slider, gold stamp).  */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, I = IN; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const CARD = { x: 1230, y: 70, w: 560, h: 640, r: 8, s: 1.5 }, CIRC = { x: 1600, y: 70, w: 240, h: 240, r: 120, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .45, L: CIRC }, { t: 7.73, d: .45, L: CARD }, { t: 12.07, d: .45, L: CIRC }];
  C.ringFn = t => { const card = t < 4.0 || (t >= 7.73 && t < 12.2); return card ? { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' } : { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 }; };
  const frame = L => T.hudFrame(L, 'EVA · DASHBOARD', '11');

  // D1 · terminal boots the skill
  C.scene({ t0: 0, t1: 3.9, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, "HI, I'M ", 'EVA', 110, 110, 54);
      st.tm = T.terminal(Z(L, 1.5, 110, 230), 110, 230, 700, ['$ meet eva-video-style', '> open-source AI video-editing skill', '> license: MIT ✓']);
      st.st = T.goldStamp(L, 'OPEN SOURCE', 760, 700); k.sfx('pop', .12, .1); for (let i = 0; i < 10; i++) k.sfx('click', .9 + i * .1, .04); k.sfx('pop', 1.95, .14); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .1, .4, -40, 0)); T.terminalAt(st.tm, t, .9, 30); tf(st.st, pop(t, 2.3, .3, 2.4)); } });

  // D2 · four styles tick on, grid fills
  C.scene({ t0: 3.87, t1: 7.76, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, 'CHOOSE A ', 'STYLE', 110, 110, 54); st.c = T.checks(Z(L, 1.5, 110, 300), 110, 300, ['CINEMATIC', 'FUTURISTIC', 'SOCIAL', 'MINIMAL'], 220);
      st.s = el(L, 'div', 'abs disp', { left: '110px', top: '480px', fontSize: '80px', color: '#fff' }, `FOUR LOOKS · <span style="color:${T.HUD.GOLD}">22 TEMPLATES</span>`); st.g = T.grid(L, 110, 640, 22, 1, 52);
      [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 100 })); k.sfx('ding', 6.9, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); st.c.forEach((c, i) => T.checksAt([c], t, [3.9, 4.73, 5.87, 6.6][i], .35, 6.9));
      tf(st.s, slide(t, 6.9, .4, 0, 30)); T.gridAt(st.g, P(t, 4.0, 3.0)); } });

  // D3 · pick → apply → AI edits (flow + toggle + slider)
  C.scene({ t0: 7.73, t1: 12.1, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, 'READY-TO-USE ', 'TEMPLATES', 110, 110, 54);
      st.f = T.flow(Z(L, 1.6, 110, 300), 110, 300, [['👆', 'PICK'], ['🎞️', 'APPLY', T.HUD.BLUE], ['🤖', 'AI EDIT', T.HUD.GOLD]], 240);
      st.tg = T.toggle(L, 110, 640, 'AI editing'); st.sl = T.slider(L, 110, 750, 'Motion');
      [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 150 })); k.sfx('click', 10.9, .1); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); T.flowAt(st.f, t, 8.97, .85);
      [st.tg.p, st.sl.p].forEach(e => tf(e, { o: P(t, 10.5, .3) })); T.toggleAt(st.tg, P(t, 10.9, .25)); T.sliderAt(st.sl, ease.io3(P(t, 11.1, .8))); } });

  // D4 · quote card + gold CTA
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.q = T.quote(L, 'Less time editing, more time creating.', 110, 200, 'more time creating'); st.q.style.fontSize = '64px';
      st.big = el(L, 'div', 'abs disp', { left: '110px', top: '400px', fontSize: '150px', color: T.HUD.GOLD, textShadow: '0 0 40px rgba(245,184,61,.4)' }, 'TRY IT TODAY');
      st.url = T.kicker(L, 'GITHUB.COM/ROVEREVA/EVA-VIDEO-STYLE', 116, 560, '#fff');
      k.sfx('whoosh', 12.1, .1); k.sfx('ding', 12.9, .07); k.sfx('impact', 13.8, .16); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.q, slide(lt, .05, .4, -40, 0)); tf(st.big, pop(t, 13.8, .4, 1.8)); tf(st.url, { o: P(t, 14.1, .3) }); } });
})();
