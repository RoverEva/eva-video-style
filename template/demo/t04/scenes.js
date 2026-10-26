/* T04 Paper — demo on the shared 15 s intro (dot-grid paper, colour tiles, stamps) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, I = IN; I.setup(C);
  const TR = { x: 1620, y: 40, w: 240, h: 240, r: 120, s: 3 }, CARD = { x: 1260, y: 200, w: 560, h: 680, r: 30, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .5, L: TR }, { t: 12.07, d: .5, L: CARD }];
  C.ringFn = () => ({ color: k.INK, width: 6, shadow: .22 });
  C.scene({ t0: 0, t1: C.end + .05, bg: k.PAPER, cls: 'dotgrid', quiet: true, build(L) {
      const st = {}; st.hi = k.disp(L, "HI, I'M EVA", k.INK, 140, 110, 110);
      st.st = k.disp(L, 'EVA VIDEO STYLE', k.RED, 120, 110, 290, { border: `8px solid ${k.RED}`, padding: '0 26px', borderRadius: '14px', transformOrigin: '50% 50%' });
      st.oss = k.card(L, 110, 480, 1100, 150, k.BLUE, { borderRadius: '24px', transformOrigin: '0 50%' }); k.disp(st.oss, 'OPEN-SOURCE', '#fff', 80, 30, 34); k.disp(st.oss, 'AI VIDEO-EDITING SKILL', k.LIME, 46, 500, 56);
      st.tiles = [['🎬', 'CINEMATIC', k.INK, '#fff', -3], ['🚀', 'FUTURISTIC TECH', k.BLUE, '#fff', 2], ['📱', 'SOCIAL MEDIA', k.RED, '#fff', -2], ['◻️', 'MINIMALIST', k.LIME, k.INK, 3]].map(([e, s, bg, fg, r], i) => { const c = k.card(L, 110 + (i % 2) * 560, 120 + Math.floor(i / 2) * 330, 520, 280, bg, { borderRadius: '26px', boxShadow: '0 14px 0 rgba(11,11,13,.18)', transformOrigin: '50% 50%' }); k.emoji(c, e, 90, 34, 30); k.disp(c, s, fg, 70, 34, 170); c.r = r; return c; });
      st.mess = k.disp(L, 'TEMPLATES', k.INK, 160, 110, 100); st.ready = k.disp(L, 'READY TO USE ✓', k.RED, 70, 120, 270, { border: `6px solid ${k.RED}`, padding: '4px 22px', transformOrigin: '50% 50%' });
      st.list = [['PICK YOUR FAVORITE', k.BLUE], ['APPLY IT TO YOUR FOOTAGE', k.RED], ['LET AI DO THE EDITING', k.INK]].map(([s, c], i) => { const d = k.card(L, 110, 420 + i * 140, 1000, 112, '#fff', { borderRadius: '20px', border: `4px solid ${k.INK}`, transformOrigin: '0 50%' }); k.disp(d, String(i + 1), c, 80, 26, 12); k.disp(d, s, k.INK, 64, 110, 22); d.ck = k.disp(d, '✓', c, 80, 920, 10, { transformOrigin: '50% 50%' }); return d; });
      st.l1 = k.disp(L, 'LESS TIME EDITING', k.INK, 110, 110, 150); st.x = el(L, 'div', 'abs', { left: '100px', top: '210px', width: '0px', height: '14px', background: k.RED, transform: 'rotate(-2deg)' });
      st.l2 = k.card(L, 110, 330, 1040, 190, k.LIME, { borderRadius: '30px', transformOrigin: '50% 50%', boxShadow: '0 14px 0 rgba(11,11,13,.18)' }); k.disp(st.l2, 'MORE TIME CREATING ✎', k.INK, 110, 40, 40);
      st.cta = k.disp(L, 'TRY IT TODAY!', k.RED, 120, 110, 600, { border: `8px solid ${k.RED}`, padding: '0 26px', borderRadius: '14px', transformOrigin: '50% 50%' });
      k.sfx('pop', .12, .12); k.sfx('impact', .95, .18); k.sfx('pop', 1.95, .12); [3.9, 4.75, 5.9, 6.6].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 140 })); k.sfx('impact', 7.75, .16); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('click', x + .3, .12)); k.sfx('click', 12.5, .14); k.sfx('pop', 12.9, .14); k.sfx('impact', 13.8, .18); return st; },
    update(lt, st, t) { const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      [st.hi, st.st, st.oss].forEach(e => e.style.display = b[0] ? '' : 'none'); tf(st.hi, slide(t, .1, .4, -120, 0)); const s = pop(t, .95, .35, 2.6); tf(st.st, { s: s.s, o: s.o, r: -4 }); tf(st.oss, slide(t, 1.95, .4, -1000, 0));
      st.tiles.forEach((c, i) => { c.style.display = b[1] ? '' : 'none'; const q = pop(t, [3.87, 4.73, 5.87, 6.6][i], .4, 1.8); tf(c, { s: q.s, o: q.o, r: c.r + Math.sin(t * 1.5 + i) * .8 }); });
      [st.mess, st.ready, ...st.list].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.mess, slide(t, 7.73, .4, -150, 0)); const r = pop(t, 8.3, .3, 2.6); tf(st.ready, { s: r.s, o: r.o, r: -5 });
      st.list.forEach((d, i) => { const a = [8.97, 9.87, 10.67][i]; tf(d, slide(t, a, .4, -1000, 0)); tf(d.ck, pop(t, a + .3, .3, 2.6)); });
      [st.l1, st.x, st.l2, st.cta].forEach(e => e.style.display = b[3] ? '' : 'none'); tf(st.l1, slide(t, 12.1, .4, -100, 0)); st.x.style.width = (1000 * ease.out3(P(t, 12.5, .35))) + 'px';
      const q = pop(t, 12.9, .45, 1.8); tf(st.l2, { s: q.s, o: q.o, r: -1.5 * q.s }); const c = pop(t, 13.8, .35, 2.6); tf(st.cta, { s: c.s, o: c.o, r: -5 }); } });
})();
