/* T05 Red Sunburst — demo on the shared 15 s intro (key point, pills, call to action) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, I = IN; I.setup(C);
  const BIGC = { x: 720, y: 150, w: 480, h: 480, r: 240, s: 2.4 }, RC = { x: 1260, y: 190, w: 500, h: 500, r: 250, s: 2.4 };
  C.evaKeys = [{ t: 0, d: 0, L: BIGC }, { t: .85, d: .55, L: RC }];
  C.ringFn = () => ({ color: '#fff', width: 12, glow: 'rgba(255,255,255,.5)' });
  C.scene({ t0: 0, t1: C.end + .05, bg: k.RED, quiet: true, build(L) {
      const st = {}; st.sun = k.sunburst(L);
      st.hi = k.disp(L, "HI, I'M EVA", '#fff', 130, 0, 680, { width: '1920px', textAlign: 'center', textShadow: '7px 7px 0 #0b0b0d', transformOrigin: '50% 50%' });
      st.kp = k.disp(L, 'MEET', k.LIME, 90, 110, 110, { textShadow: '5px 5px 0 #0b0b0d' }); st.nm = k.disp(L, 'EVA VIDEO', '#fff', 170, 110, 200, { textShadow: '8px 8px 0 #0b0b0d' }); st.nm2 = k.disp(L, 'STYLE', '#fff', 170, 110, 360, { textShadow: '8px 8px 0 #0b0b0d' });
      st.oss = k.O(k.chip(L, 'OPEN-SOURCE AI VIDEO-EDITING SKILL', k.LIME, k.INK, 46, 116, 560));
      st.bub = k.card(L, 110, 90, 820, 170, '#fff', { borderRadius: '30px' }); k.disp(st.bub, 'CHOOSE YOUR STYLE', k.INK, 90, 34, 40); k.O(st.bub, '0 100%'); el(st.bub, 'div', 'abs', { left: '60px', bottom: '-30px', width: 0, height: 0, borderLeft: '30px solid transparent', borderRight: '30px solid transparent', borderTop: '34px solid #fff' });
      st.p = [['🎬 CINEMATIC', '#fff', k.RED], ['🚀 FUTURISTIC TECH', k.BLUE, '#fff'], ['📱 SOCIAL MEDIA', k.LIME, k.INK], ['◻️ MINIMALIST', k.INK, '#fff']].map(([tx, bg, fg], i) => el(L, 'div', 'abs disp', { left: '110px', top: (330 + i * 130) + 'px', fontSize: '70px', background: bg, color: fg, padding: '8px 40px', borderRadius: '60px', boxShadow: '0 10px 0 rgba(0,0,0,.25)', transformOrigin: '0 50%' }, tx));
      st.kt = k.disp(L, 'READY-TO-USE', '#fff', 120, 110, 90, { textShadow: '6px 6px 0 #0b0b0d' }); st.kt2 = k.disp(L, 'TEMPLATES', k.LIME, 150, 110, 210, { textShadow: '6px 6px 0 #0b0b0d' });
      st.n = [['1', 'PICK YOUR FAVORITE'], ['2', 'APPLY TO YOUR FOOTAGE'], ['3', 'LET AI EDIT']].map(([a, s], i) => { const d = el(L, 'div', 'abs', { left: '110px', top: (420 + i * 140) + 'px', width: '1100px', height: '110px', transformOrigin: '0 50%' }); el(d, 'div', 'disp', { position: 'absolute', left: 0, top: 0, width: '110px', height: '110px', borderRadius: '50%', background: '#fff', color: k.RED, fontSize: '80px', lineHeight: '110px', textAlign: 'center' }, a); el(d, 'div', 'disp', { position: 'absolute', left: '140px', top: '18px', fontSize: '76px', color: '#fff', textShadow: '5px 5px 0 #0b0b0d' }, s); return d; });
      st.l1 = k.disp(L, 'LESS TIME EDITING', '#fff', 120, 110, 110, { textShadow: '6px 6px 0 #0b0b0d' }); st.l2 = k.disp(L, 'MORE TIME CREATING', k.LIME, 120, 110, 260, { textShadow: '6px 6px 0 #0b0b0d' });
      st.c = [['▶ TRY IT TODAY', '#fff', k.RED], ['★ STAR ON GITHUB', k.LIME, k.INK]].map(([tx, bg, fg], i) => el(L, 'div', 'abs disp', { left: '110px', top: (470 + i * 140) + 'px', fontSize: '66px', background: bg, color: fg, padding: '10px 40px', borderRadius: '60px', boxShadow: '0 10px 0 rgba(0,0,0,.25)', transformOrigin: '50% 50%' }, tx));
      k.sfx('impact', .12, .16); k.sfx('whoosh', .9, .1); k.sfx('pop', 1.95, .12); [3.9, 4.75, 5.9, 6.6].forEach((x, i) => k.sfx('pop', x, .14, { f: 900 + i * 150 })); k.sfx('impact', 7.75, .16); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .14); [13.8, 14.2].forEach((x, i) => k.sfx('pop', x, .14, { f: 1100 + i * 200 })); return st; },
    update(lt, st, t) { st.sun.style.transform = `rotate(${lt * 10}deg)`; const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      st.hi.style.display = t < .9 ? '' : 'none'; tf(st.hi, pop(t, .12, .35, 2));
      [st.kp, st.nm, st.nm2, st.oss].forEach(e => e.style.display = b[0] && t >= .85 ? '' : 'none'); tf(st.kp, pop(t, .9, .3)); tf(st.nm, slide(t, .95, .4, -200, 0)); tf(st.nm2, slide(t, 1.1, .4, -200, 0)); tf(st.oss, pop(t, 1.95, .35));
      [st.bub, ...st.p].forEach(e => e.style.display = b[1] ? '' : 'none'); const q = pop(t, 3.87, .4, 1.6); tf(st.bub, { s: q.s, o: q.o }); st.p.forEach((p, i) => { const r = pop(t, [3.95, 4.73, 5.87, 6.6][i], .35, 2.2); tf(p, { s: r.s, o: r.o, r: Math.sin(t * 4 + i) * 1.5 }); });
      [st.kt, st.kt2, ...st.n].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.kt, slide(t, 7.73, .4, -200, 0)); tf(st.kt2, pop(t, 8.0, .4, 1.8)); K.O(st.kt2); st.n.forEach((d, i) => tf(d, slide(t, [8.97, 9.87, 10.67][i], .4, -900, 0)));
      [st.l1, st.l2, ...st.c].forEach(e => e.style.display = b[3] ? '' : 'none'); tf(st.l1, slide(t, 12.1, .4, -200, 0)); tf(st.l2, slide(t, 12.9, .4, -200, 0)); st.c.forEach((c, i) => { const r = pop(t, 13.8 + i * .4, .35, 2.2); tf(c, { s: r.s * (1 + .03 * Math.sin(t * 6 + i)), o: r.o }); }); } });
})();
