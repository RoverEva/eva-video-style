/* T02 Electric Blue Console — demo on the shared 15 s intro */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, TT = K.T, I = IN; I.setup(C);
  const TR = { x: 1590, y: 40, w: 290, h: 290, r: 145, s: 3 }, CARD = { x: 1260, y: 200, w: 560, h: 680, r: 30, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .5, L: TR }, { t: 12.07, d: .5, L: CARD }];
  C.ringFn = () => ({ color: k.LIME, width: 6, glow: 'rgba(212,255,46,.4)' });
  const BG = `radial-gradient(1400px 900px at 40% 30%, #12206b, ${k.NAVY})`;
  C.scene({ t0: 0, t1: C.end + .05, bg: BG, cls: 'linegrid', quiet: true, build(L) {
      const st = {}; st.hi = k.disp(L, "HI, I'M EVA", '#fff', 150, 110, 140);
      st.name = k.disp(L, 'EVA VIDEO STYLE', k.LIME, 150, 110, 320, { textShadow: '0 0 30px rgba(212,255,46,.45)' }); st.oss = k.O(k.chip(L, 'OPEN-SOURCE · AI VIDEO-EDITING SKILL', '#fff', k.INK, 46, 116, 500));
      st.p = I.STYLES.map((s, i) => { const c = k.card(L, 110 + (i % 2) * 720, 120 + Math.floor(i / 2) * 330, 680, 290, '#fff', { borderRadius: '26px', transformOrigin: '50% 50%' }); k.hud(c, 'STYLE 0' + (i + 1), k.BLUE, 32, 28, 22, { opacity: 1 }); k.disp(c, s, k.INK, 92, 32, 80);
        c.bar = el(c, 'div', 'abs', { left: '32px', top: '210px', width: '0px', height: '22px', borderRadius: '11px', background: `repeating-linear-gradient(110deg, ${k.BLUE} 0 22px, #4f6bff 22px 44px)` }); return c; });
      st.tp = k.disp(L, 'READY-TO-USE TEMPLATES', '#fff', 100, 110, 70);
      st.f = [['PICK', 'YOUR FAVORITE'], ['APPLY', 'TO YOUR FOOTAGE'], ['AI', 'DOES THE EDIT']].map(([a, b], i) => { const c = k.card(L, 110 + i * 470, 260, 420, 300, i === 2 ? k.LIME : '#fff', { borderRadius: '26px', transformOrigin: '50% 50%' }); k.disp(c, a, i === 2 ? k.INK : k.BLUE, 120, 34, 40); k.disp(c, b, k.INK, 44, 38, 190); return c; });
      st.ar = [0, 1].map(i => k.disp(L, '→', '#fff', 100, 540 + i * 470, 330));
      st.prog = el(L, 'div', 'abs', { left: '110px', top: '640px', width: '1360px', height: '30px', borderRadius: '15px', background: 'rgba(255,255,255,.15)' }); st.pf = el(st.prog, 'div', 'abs', { left: 0, top: 0, height: '30px', width: '0px', borderRadius: '15px', background: k.LIME });
      st.pl = k.hud(L, 'AI EDITING', k.LIME, 116, 690, 20, { opacity: 1 });
      st.cv = TT.curve(L, 110, 360, 1080, 380, k.LIME); st.l1 = k.disp(L, 'LESS TIME EDITING', '#fff', 90, 110, 120); st.l2 = k.disp(L, 'MORE TIME CREATING', k.LIME, 100, 110, 220);
      st.cta = k.O(k.chip(L, 'TRY EVA VIDEO STYLE TODAY →', k.LIME, k.INK, 56, 116, 800));
      k.sfx('impact', .12, .14); k.sfx('pop', .95, .12); k.sfx('pop', 1.95, .12, { f: 1100 }); [3.9, 4.75, 5.9, 6.7].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 140 }));
      k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('riser', 12.1, .07, { d: 1 }); k.sfx('impact', 12.9, .16); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      [st.hi, st.name, st.oss].forEach(e => e.style.display = b[0] ? '' : 'none'); tf(st.hi, slide(t, .1, .4, -150, 0)); tf(st.name, slide(t, .9, .45, -150, 0)); tf(st.oss, pop(t, 1.95, .35));
      st.p.forEach((c, i) => { c.style.display = b[1] ? '' : 'none'; const a = [3.87, 4.73, 5.87, 6.6][i]; tf(c, pop(t, a, .4, 1.6)); c.bar.style.width = (616 * ease.out3(P(t, a + .2, .8))) + 'px'; c.bar.style.backgroundPosition = `${t * 60}px 0`; });
      [st.tp, ...st.f, ...st.ar, st.prog, st.pl].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.tp, slide(t, 7.73, .4, -150, 0)); st.f.forEach((c, i) => tf(c, pop(t, [8.97, 9.87, 10.67][i], .4, 1.6))); st.ar.forEach((a, i) => tf(a, { o: P(t, [9.7, 10.5][i], .2) })); st.pf.style.width = (1360 * ease.io3(P(t, 10.7, 1.3))) + 'px'; st.pf.style.backgroundImage = `repeating-linear-gradient(110deg, rgba(0,0,0,.12) 0 18px, transparent 18px 36px)`; st.pf.style.backgroundPosition = `${t * 80}px 0`;
      [st.cv.s || st.cv, st.l1, st.l2, st.cta].forEach(e => { if (e && e.style) e.style.display = b[3] ? '' : 'none'; }); TT.curveAt(st.cv, P(t, 12.1, 1.4)); tf(st.l1, slide(t, 12.1, .4, -100, 0)); tf(st.l2, pop(t, 12.9, .4, 1.8)); tf(st.cta, pop(t, 13.8, .4, 1.7)); } });
})();
