/* T06 Brand Purple — demo on the shared 15 s intro (product reveal: logo letter drop, feature cards, real screen, CTA) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, I = IN; I.setup(C);
  const TR = { x: 1590, y: 36, w: 290, h: 290, r: 145, s: 3 }, CARD = { x: 1260, y: 200, w: 560, h: 680, r: 36, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.87, d: .5, L: TR }];
  C.ringFn = () => ({ color: '#fff', width: 8, glow: 'rgba(212,255,46,.35)' });
  const BG = 'radial-gradient(1300px 800px at 35% 30%, #6d4fe8, #5b3fd6 45%, #1b0f4a 100%)';
  C.scene({ t0: 0, t1: C.end + .05, bg: BG, quiet: true, build(L) {
      const st = {}; st.hi = k.disp(L, "HI, I'M EVA", k.LIME, 80, 110, 110);
      st.lt = 'EVA VIDEO STYLE'.split('').map((ch, i) => k.disp(L, ch === ' ' ? ' ' : ch, '#fff', 150, 0, 230, { transformOrigin: '50% 100%' }));
      let x = 110; st.lt.forEach(e => { e.style.left = x + 'px'; x += ({ '\u00a0': 40, I: 38 })[e.textContent] || 66; });
      st.oss = k.O(k.chip(L, 'OPEN-SOURCE · AI VIDEO-EDITING SKILL', k.LIME, k.INK, 46, 116, 430));
      st.f = I.STYLES.map((s, i) => { const c = k.card(L, 110 + (i % 2) * 720, 120 + Math.floor(i / 2) * 330, 680, 290, 'rgba(255,255,255,.12)', { borderRadius: '28px', border: '2px solid rgba(255,255,255,.35)', backdropFilter: 'blur(8px)', transformOrigin: '50% 50%' }); k.hud(c, 'STYLE 0' + (i + 1), k.LIME, 34, 30, 22, { opacity: 1 }); k.disp(c, s, '#fff', 96, 34, 110); return c; });
      st.lap = el(L, 'div', 'abs', { left: '640px', top: '140px', width: '760px', height: '470px', borderRadius: '22px', background: '#111', padding: '18px', boxSizing: 'border-box', boxShadow: '0 30px 60px rgba(20,8,60,.6)', transformOrigin: '50% 50%' }); st.lim = el(st.lap, 'img', '', { width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 0', borderRadius: '8px', display: 'block' });
      st.ai = el(L, 'div', 'abs disp', { left: '1230px', top: '100px', width: '170px', height: '170px', borderRadius: '50%', background: k.LIME, color: k.INK, fontSize: '80px', lineHeight: '170px', textAlign: 'center', transformOrigin: '50% 50%', boxShadow: '0 0 40px rgba(212,255,46,.7)' }, 'AI');
      st.s = [['PICK', 'your favorite'], ['APPLY', 'to your footage'], ['AI EDITS', 'for you']].map(([a, b], i) => { const d = k.card(L, 110, 140 + i * 170, 480, 140, i === 2 ? k.LIME : '#fff', { borderRadius: '24px', transformOrigin: '0 50%' }); k.disp(d, a, i === 2 ? k.INK : '#5b3fd6', 76, 30, 14); el(d, 'div', 'abs sans', { left: '32px', top: '96px', fontSize: '28px', color: '#333' }, b); return d; });
      st.tp = k.hud(L, 'READY-TO-USE TEMPLATES', k.LIME, 116, 96, 22, { opacity: 1 });
      st.l = k.disp(L, 'LESS EDITING.', '#fff', 150, 110, 140); st.m = k.disp(L, 'MORE CREATING.', k.LIME, 150, 110, 300);
      st.cta = k.O(k.chip(L, 'TRY EVA VIDEO STYLE TODAY →', k.LIME, k.INK, 56, 116, 520)); st.url = k.hud(L, 'GITHUB.COM/ROVEREVA/EVA-VIDEO-STYLE', '#fff', 120, 640, 26, { opacity: .9 });
      'EVA VIDEO STYLE'.split('').forEach((_, i) => k.sfx('click', .9 + i * .04, .04)); k.sfx('pop', .12, .12); k.sfx('pop', 1.95, .12); [3.9, 4.75, 5.9, 6.6].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 140 })); k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('impact', 10.7, .14); k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .14); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      [st.hi, ...st.lt, st.oss].forEach(e => e.style.display = b[0] ? '' : 'none'); tf(st.hi, slide(t, .1, .35, -80, 0)); st.lt.forEach(e => { tf(e, { y: -200 * (1 - ease.outBack(P(t, .9, .4), 2)), o: P(t, .9, .1) }); }); tf(st.oss, pop(t, 1.95, .35));
      st.f.forEach((c, i) => { c.style.display = b[1] ? '' : 'none'; tf(c, pop(t, [3.87, 4.73, 5.87, 6.6][i], .45, 1.6)); });
      [st.lap, st.ai, ...st.s, st.tp].forEach(e => e.style.display = b[2] ? '' : 'none'); tf(st.tp, { o: P(t, 7.75, .3) }); st.s.forEach((d, i) => tf(d, slide(t, [8.97, 9.87, 10.67][i], .4, -600, 0))); tf(st.lap, pop(t, 9.87, .45, 1.5)); C.setSrc(st.lim, C.seq('../media/web', Math.max(0, t - 9.87) * 1.4, 451)); tf(st.ai, { s: pop(t, 10.7, .35, 2.6).s, o: P(t, 10.7, .1), r: t * 30 });
      [st.l, st.m, st.cta, st.url].forEach(e => e.style.display = b[3] ? '' : 'none'); tf(st.l, slide(t, 12.1, .4, -150, 0)); tf(st.m, slide(t, 12.9, .4, -150, 0)); tf(st.cta, pop(t, 13.8, .4, 1.7)); tf(st.url, { o: P(t, 14.1, .3) }); } });
})();
