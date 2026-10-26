/* T17 Science Network — demo on the shared 15 s intro. Plexus networks keep rippling / rotating; bokeh drifts in every shot. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, S = T.SCN, I = IN; I.setup(C);
  const BR = { x: 1580, y: 690, w: 260, h: 260, r: 130, s: 3 }, BL = { x: 1500, y: 600, w: 300, h: 300, r: 150, s: 2.8 }, TR = { x: 1600, y: 60, w: 240, h: 240, r: 120, s: 3 }, TUN = { x: 1220, y: 400, w: 260, h: 260, r: 130, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, BR, { o: 0 }) }, { t: .1, d: .4, L: BR }, { t: 3.87, d: .5, L: TR }, { t: 7.73, d: .5, L: BL }, { t: 12.07, d: .6, L: TUN }];
  C.ringFn = () => ({ color: S.CYAN, width: 3, glow: 'rgba(24,224,242,.5)', shadow: .5 });

  // S1 · headline + rippling plexus ribbon
  C.scene({ t0: 0, t1: 3.9, bg: T.sciNetBg, quiet: true, build(L) {
      const st = {}; st.bk = T.bokeh(L, 45, 13); st.r = T.ribbon(L, { y: 640, amp: 150, width: 230 });
      st.h = T.sciHead(L, ["[HI,] I'M EVA", 'MEET EVA', 'VIDEO STYLE'], 'An open-source AI video-editing skill', 110, 80, 104);
      k.sfx('riser', .1, .08, { d: .8 }); k.sfx('impact', .9, .14); k.sfx('ding', 1.95, .07); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); st.r.cv.style.opacity = P(lt, 0, .8); T.sciHeadAt(st.h, t, .1); } });

  // S2 · plexus globe with real continents, four styles
  C.scene({ t0: 3.87, t1: 7.76, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 35, 17); st.g = T.pSphere(L, 1250, 580, 360, { n: 320, land: true, speed: 8, lon0: 70 });
      st.h = T.sciHead(L, ['CHOOSE', 'A [STYLE]'], 'Cinematic · Futuristic tech · Social media · Minimalist', 110, 140, 104);
      st.s = I.STYLES.map((s, i) => el(L, 'div', 'abs disp', { left: '110px', top: (560 + i * 100) + 'px', fontSize: '64px', color: i % 2 ? S.CYAN : '#fff' }, s));
      k.sfx('whoosh', 3.9, .1); [3.9, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x + .05, .1, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.pSphereAt(st.g, t, P(lt, 0, .7)); T.sciHeadAt(st.h, t, 3.9); st.h.querySelector && 0;
      st.s.forEach((e, i) => tf(e, slide(t, [3.95, 4.73, 5.87, 6.6][i], .35, -60, 0))); } });

  // S3 · chain of plexus spheres: pick → apply → AI
  C.scene({ t0: 7.73, t1: 12.1, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 35, 21); st.r = T.ribbon(L, { y: 900, amp: 60, width: 60, rows: 3, cols: 40, seed: 8 });
      st.sp = [T.pSphere(L, 330, 720, 110, { n: 90, speed: 14 }), T.pSphere(L, 780, 600, 160, { n: 140, speed: -11 }), T.pSphere(L, 1260, 470, 200, { n: 200, speed: 9 })];
      st.l = [['PICK', 330, 860], ['APPLY', 780, 790], ['AI EDITS', 1260, 700]].map(([s, x, y]) => el(L, 'div', 'abs disp', { left: (x - 200) + 'px', width: '400px', textAlign: 'center', top: y + 'px', fontSize: '56px', color: '#fff', textShadow: `0 0 18px ${S.CYAN}` }, s));
      st.h = T.sciHead(L, ['READY-TO-USE', '[TEMPLATES]'], 'Pick one, apply it, let AI do the editing', 110, 100, 96);
      [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .1, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); const at = [8.97, 9.87, 10.67]; st.sp.forEach((s, i) => T.pSphereAt(s, t, P(t, at[i], .5))); st.l.forEach((e, i) => tf(e, pop(t, at[i] + .1, .35, 1.6))); T.sciHeadAt(st.h, t, 7.8); } });

  // S4 · plexus tunnel, presenter at its centre
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.sciNetBg, build(L) {
      const st = {}; st.bk = T.bokeh(L, 40, 25); st.tn = T.tunnel(L, 1350, 530, { rmax: 1100 });
      st.h = T.sciHead(L, ['LESS EDITING.', 'MORE [CREATING.]'], 'Try Eva Video Style today →', 110, 330, 100);
      k.sfx('riser', 12.1, .08, { d: .6 }); k.sfx('pop', 12.9, .1); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { T.bokehAt(st.bk, t); T.tunnelAt(st.tn, t); st.tn.cv.style.opacity = P(lt, 0, .6); T.sciHeadAt(st.h, t, 12.1); } });
})();
