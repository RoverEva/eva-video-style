/* T01 Acid Lime Kinetic — demo on the shared 15 s intro */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, I = IN, T = I.T; I.setup(C);
  const CARD = { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .05, d: .4, L: CARD }];
  C.ringFn = () => ({ color: k.INK, width: 6, shadow: .22 });
  C.scene({ t0: 0, t1: C.end + .05, bg: k.LIME, cls: 'dotgrid', quiet: true, build(L) {
      const st = { rows: [] }; for (let r = 0; r < 7; r++) st.rows.push(k.disp(L, Array(8).fill(r % 2 ? 'EVA VIDEO STYLE' : 'OPEN SOURCE · AI EDITING').join(' · '), r % 2 ? 'rgba(11,11,13,.85)' : 'rgba(11,11,13,.13)', 104, -200, -30 + r * 150));
      st.hi = k.disp(L, "HI, I'M EVA", '#fff', 200, 110, 360, { textShadow: '8px 8px 0 #0b0b0d', zIndex: 5, background: '#0b0b0d', padding: '20px 40px', borderRadius: '30px' }); k.O(st.hi);
      st.t = k.card(L, 110, 120, 1040, 330, k.INK, { borderRadius: '34px', transformOrigin: '50% 50%' }); k.hud(st.t, 'MEET', k.LIME, 44, 40, 26, { opacity: 1 }); k.disp(st.t, 'EVA VIDEO STYLE', '#fff', 130, 40, 90);
      st.oss = k.O(k.chip(st.t, 'OPEN-SOURCE AI VIDEO-EDITING SKILL', k.LIME, k.INK, 38, 44, 236), '0 50%');
      st.c = I.STYLES.map((s, i) => { const c = k.card(L, 110, 510 + i * 100, 1040, 86, i % 2 ? '#fff' : k.INK, { borderRadius: '20px', transformOrigin: '0 50%' }); k.disp(c, '0' + (i + 1), k.BLUE, 70, 24, 8); k.disp(c, s, i % 2 ? k.INK : '#fff', 70, 130, 8); return c; });
      st.tp = k.card(L, 110, 120, 1040, 260, k.BLUE, { borderRadius: '34px', transformOrigin: '50% 50%' }); k.disp(st.tp, 'READY-TO-USE', '#fff', 110, 40, 30); k.disp(st.tp, 'TEMPLATES', k.LIME, 110, 40, 140);
      st.steps = [['1', 'PICK YOUR FAVORITE'], ['2', 'APPLY TO YOUR FOOTAGE'], ['3', 'LET AI EDIT']].map(([n, s], i) => { const c = k.card(L, 110, 420 + i * 150, 1040, 128, '#fff', { borderRadius: '24px', transformOrigin: '0 50%' }); k.disp(c, n, k.BLUE, 100, 30, 14); k.disp(c, s, k.INK, 76, 130, 26); return c; });
      st.sw = el(st.steps[2], 'div', 'abs', { left: '820px', top: '30px', width: '180px', height: '70px', borderRadius: '35px', background: '#ddd' }); st.kn = el(st.sw, 'div', 'abs', { left: '6px', top: '6px', width: '58px', height: '58px', borderRadius: '50%', background: '#fff', boxShadow: '0 2px 6px rgba(0,0,0,.3)' });
      st.l1 = k.card(L, 110, 120, 1040, 190, '#fff', { borderRadius: '30px', transformOrigin: '0 50%' }); k.disp(st.l1, 'LESS TIME EDITING', k.INK, 120, 40, 36); st.l2 = k.card(L, 110, 340, 1040, 190, k.BLUE, { borderRadius: '30px', transformOrigin: '100% 50%' }); k.disp(st.l2, 'MORE TIME CREATING', '#fff', 120, 40, 36);
      st.cta = k.card(L, 110, 560, 1040, 200, k.INK, { borderRadius: '34px', transformOrigin: '50% 50%' }); k.disp(st.cta, 'TRY IT TODAY →', k.LIME, 130, 46, 34);
      k.sfx('impact', .12, .16); k.sfx('whoosh', .9, .1); k.sfx('pop', 1.95, .12); [3.9, 4.75, 5.9, 6.7].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 140 })); k.sfx('whoosh', 7.75, .1);
      [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('click', 11.0, .14); k.sfx('impact', 12.1, .16); k.sfx('impact', 12.9, .16); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { st.rows.forEach((d, i) => tf(d, { x: (i % 2 ? -1 : 1) * (lt * 90) - 300, o: 1 }));
      const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      st.hi.style.display = t < .9 ? '' : 'none'; tf(st.hi, pop(t, .12, .35, 2));
      st.t.style.display = b[0] || b[1] ? '' : 'none'; tf(st.t, pop(t, .9, .45, 1.6)); tf(st.oss, pop(t, 1.95, .35));
      st.c.forEach((c, i) => { c.style.display = b[1] ? '' : 'none'; tf(c, slide(t, [3.87, 4.73, 5.87, 6.7][i], .4, -1100, 0)); });
      [st.tp, ...st.steps].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.tp, pop(t, 7.73, .45, 1.6)); st.steps.forEach((c, i) => tf(c, slide(t, [8.97, 9.87, 10.67][i], .4, -1100, 0)));
      const u = ease.io3(P(t, 11.0, .4)); st.kn.style.left = (6 + 110 * u) + 'px'; st.sw.style.background = u > .5 ? k.LIME : '#ddd';
      [st.l1, st.l2, st.cta].forEach(e => e.style.display = b[3] ? '' : 'none'); tf(st.l1, slide(t, 12.1, .4, -900, 0)); tf(st.l2, slide(t, 12.9, .4, 900, 0)); tf(st.cta, pop(t, 13.8, .45, 1.8)); } });
})();
