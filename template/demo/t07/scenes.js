/* T07 Cartoon — demo on the shared 15 s intro (cartoon clips full-bleed or framed, muted; text sits in open sky) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, TT = K.T, I = IN; I.setup(C);
  const TL = { x: 50, y: 40, w: 260, h: 260, r: 130, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, TL, { o: 0 }) }, { t: .1, d: .4, L: TL }];
  C.ringFn = () => ({ color: '#fff', width: 10, shadow: .35 });
  C.scene({ t0: 0, t1: C.end + .05, bg: 'linear-gradient(180deg, #6fb7ff, #bfe3ff)', quiet: true, build(L) {
      const st = {}; st.full = el(L, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', objectPosition: '50% 70%' });
      st.sky = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '500px', background: 'linear-gradient(180deg, rgba(30,70,160,.85), rgba(30,70,160,.5) 70%, rgba(30,70,160,0))' });
      st.h1 = TT.bubbly(L, "Hi, I'm Eva!", 360, 70, 120); st.h2 = TT.bubbly(L, 'Eva Video Style', 360, 220, 120, { fill: '#d4ff2e' }); st.h3 = TT.goal(L, 'open-source AI video editing ✨', 370, 400, '#fff', -2);
      st.fr = el(L, 'div', 'abs', { left: '900px', top: '300px', width: '880px', height: '495px', borderRadius: '30px', border: '14px solid #fff', overflow: 'hidden', boxShadow: '0 20px 0 rgba(20,60,140,.25)', transformOrigin: '50% 50%' }); st.fi = el(st.fr, 'img', '', { width: '100%', height: '100%', objectFit: 'cover', display: 'block' });
      st.cl = I.STYLES.map((s, i) => { const c = el(L, 'div', 'abs disp', { left: (100 + (i % 2) * 380) + 'px', top: (360 + Math.floor(i / 2) * 170) + 'px', padding: '22px 34px', background: '#fff', color: '#2a6fd6', fontSize: '52px', borderRadius: '60px', boxShadow: '0 10px 0 rgba(20,60,140,.2)', transformOrigin: '50% 50%' }, s); return c; });
      st.ch = TT.bubbly(L, 'Choose a style', 360, 150, 96);
      st.tp = TT.bubbly(L, 'Ready-to-use templates', 100, 340, 84);
      st.st = ['① Pick your favorite', '② Apply it to your footage', '③ Let AI do the editing'].map((s, i) => TT.goal(L, s, 110, 480 + i * 120, ['#fff', '#d4ff2e', '#ffd21f'][i], [-2, 1.5, -1.5][i]));
      st.l1 = TT.bubbly(L, 'Less time editing,', 360, 80, 110); st.l2 = TT.bubbly(L, 'more time creating!', 360, 230, 120, { fill: '#d4ff2e' }); st.cta = TT.goal(L, 'Try Eva Video Style today →', 370, 420, '#ffd21f', -2);
      k.sfx('pop', .15, .12); k.sfx('ding', .95, .08); k.sfx('pop', 1.95, .12); [3.9, 4.75, 5.9, 6.6].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 140 })); k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .14); k.sfx('ding', 13.8, .08); [st.h1, st.h2, st.ch, st.tp, st.l1, st.l2].forEach(e => e && (e.style.filter = 'drop-shadow(0 0 4px #17306e) drop-shadow(0 7px 0 #17306e)')); return st; },
    update(lt, st, t) { const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      const fullOn = b[0] || b[3]; st.full.style.display = st.sky.style.display = fullOn ? '' : 'none'; C.setSrc(st.full, b[0] ? C.seq('../media/egg', t * 1.4, 151) : C.seq('../media/jmw', (t - 12.07), 151)); tf(st.full, { s: 1.04 + .03 * Math.sin(t * .5) });
      [st.h1, st.h2, st.h3].forEach(e => e.style.display = b[0] ? '' : 'none'); tf(st.h1, pop(t, .12, .4, 1.8)); tf(st.h2, pop(t, .95, .45, 1.8)); const g = pop(t, 1.95, .4, 1.8); tf(st.h3, { s: g.s, o: g.o, r: -2 });
      st.fr.style.display = b[1] || b[2] ? '' : 'none'; tf(st.fr, pop(t, 3.87, .5, 1.5)); C.setSrc(st.fi, C.seq(b[1] ? '../media/jmw' : '../media/egg', (t - 3.87) % 5, 151));
      [st.ch, ...st.cl].forEach(e => e.style.display = b[1] ? '' : 'none'); tf(st.ch, pop(t, 3.9, .4, 1.6)); st.cl.forEach((c, i) => { const q = pop(t, [3.95, 4.73, 5.87, 6.6][i], .4, 2); tf(c, { s: q.s, o: q.o, y: 6 * Math.sin(t * 2 + i) }); });
      [st.tp, ...st.st].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.tp, pop(t, 7.75, .4, 1.6)); st.st.forEach((s, i) => { const q = pop(t, [8.97, 9.87, 10.67][i], .4, 1.8); tf(s, { s: q.s, o: q.o, r: [-2, 1.5, -1.5][i] }); });
      [st.l1, st.l2, st.cta].forEach(e => e.style.display = b[3] ? '' : 'none'); tf(st.l1, pop(t, 12.1, .4, 1.8)); tf(st.l2, pop(t, 12.9, .45, 1.8)); const c = pop(t, 13.8, .4, 1.8); tf(st.cta, { s: c.s, o: c.o, r: -2 }); } });
})();
