/* T12 NEWS · 旧报纸 Old Newspaper — demo (16 s). Photos and film frames are real frames from Eva's videos. */
(function () {
  const C = EV, { el, tf, pop, slide, wipe, P, ease, clamp } = C, k = K, T = K.T, N = T.NEWS;
  C.src0 = 50; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const W = f => '../../media/wall/' + f;
  const CARD = { x: 1250, y: 210, w: 540, h: 640, r: 2, s: 1.5 }, SMALL = { x: 1560, y: 60, w: 300, h: 360, r: 2, s: 2 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 6.5, d: .45, L: SMALL }, { t: 9.5, d: .45, L: Object.assign({}, SMALL, { o: 0 }) }, { t: 13.0, d: .4, L: CARD }];
  C.ringFn = () => ({ color: '#f3ecdc', width: 12, shadow: .5 });   // Eva stays in natural colour

  // P1 · front page: masthead, headline, columns; Eva as the b/w front-page photo
  C.scene({ t0: 0, t1: 3.03, bg: T.newsBg(false), quiet: true, build(L) {
      const st = {}; st.m = T.masthead(L, 'THE EVA TIMES', 'VOL. 1 · 视频日报 · 2026', 110, 50, 1060);
      st.h = T.headline(L, 'AI 剪辑，真的能用吗？', 110, 290, 92); st.c = T.columns(L, 110, 460, 1060, 520, 3, 4);
      st.tp = T.tape(L, 1450, 186, 150, -6); st.g = T.grain(L, .2); k.sfx('impact', .15, .14); k.sfx('click', 1.0, .08); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.m, { o: P(lt, 0, .3), s: 1.05 - .05 * ease.outExpo(P(lt, 0, .6)) }); st.m.style.transformOrigin = '50% 0';
      tf(st.h, slide(lt, .9, .4, -60, 0)); wipe(st.c, ease.out3(P(lt, 1.3, 1.2)), 'd'); } });

  // P2 · collage wall: film strip of real frames, red X + "?", red brush stamp
  C.scene({ t0: 3.0, t1: 6.53, bg: T.newsBg(true), build(L) {
      const st = {}; st.f = T.filmstrip(L, 60, 140, ['w_117.jpg', 'w_15.jpg', 'w_209.jpg', 'w_300.jpg'].map(W), 260, -3);
      st.p = T.photo(L, W('w_310.jpg'), 120, 520, 520, 320, 4); st.t1 = T.tape(L, 300, 500, 140, 3);
      st.x = T.scribble(L, 'x', 200, 560, 330, N.RED); st.q = el(L, 'div', 'abs', { left: '760px', top: '330px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '260px', color: '#f3ecdc', opacity: .9 }, '?');
      st.b = T.brush(L, '重跑一遍', 360, 760, 110, -9); st.bolt = T.scribble(L, 'bolt', 960, 470, 150, N.RED, 10);
      st.g = T.grain(L, .25); k.sfx('whoosh', 3.2, .08); k.sfx('click', 4.0, .1); k.sfx('impact', 5.0, .2); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.f, slide(lt, .05, .6, -400, 0)); st.f.style.transform += ' rotate(-3deg)'; tf(st.p, { s: pop(t, 3.4, .4, 1.4).s, o: P(t, 3.4, .2), r: 4 }); tf(st.t1, { o: P(t, 3.6, .2), r: 3 });
      T.scribbleAt(st.x, P(t, 4.0, .5)); tf(st.q, pop(t, 4.4, .35, 1.6)); st.q.style.opacity = .9 * P(t, 4.4, .1); tf(st.b, { s: 1.6 - .6 * ease.outBack(P(t, 5.0, .3), 2), o: P(t, 5.0, .08), r: -9 }); T.scribbleAt(st.bolt, P(t, 5.3, .3)); } });

  // P3 · typewriter on paper + red arrow
  C.scene({ t0: 6.5, t1: 9.53, bg: T.newsBg(false), build(L) {
      const st = {}; st.slip = el(L, 'div', 'abs', { left: '160px', top: '300px', width: '1100px', height: '300px', background: '#f6efde', boxShadow: '0 20px 50px rgba(0,0,0,.25)', transform: 'rotate(-1.5deg)' });
      st.k = el(st.slip, 'div', 'abs', { left: '50px', top: '40px', fontFamily: N.TYPE, fontSize: '28px', color: '#8a7f6a' }, 'Write something ...');
      st.ty = T.typed(st.slip, 'Eva Video Style · No. 12', 50, 120, 72, N.INK); st.ar = T.scribble(L, 'arrow', 1000, 560, 260, N.RED, 160);
      st.u = T.scribble(L, 'underline', 200, 470, 760, N.RED); st.n = el(L, 'div', 'abs', { left: '1020px', top: '820px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '48px', color: N.RED, transform: 'rotate(-4deg)' }, '一键套用 ✓');
      st.g = T.grain(L, .2); for (let i = 0; i < 18; i++) k.sfx('click', 7.0 + i * .07, .05); k.sfx('ding', 8.4, .06); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.slip, { y: 40 * (1 - ease.outExpo(P(lt, 0, .5))), o: P(lt, 0, .2), r: -1.5 }); T.typedAt(st.ty, t, 7.0, 14);
      T.scribbleAt(st.u, P(t, 8.4, .4)); T.scribbleAt(st.ar, P(t, 8.6, .4)); tf(st.n, { o: P(t, 8.9, .2), r: -4 }); } });

  // P4 · editorial triptych: three b/w frames with role labels
  C.scene({ t0: 9.5, t1: 13.03, bg: '#14110e', build(L) {
      const st = { c: [] }; const R = [['w_117.jpg', 'OPENING', '开场'], ['w_209.jpg', 'EXPLAIN', '讲解'], ['w_310.jpg', 'FINALE', '结尾']];
      R.forEach(([f, role, zh], i) => { const x = 110 + i * 580; const im = el(L, 'img', 'abs', { left: x + 'px', top: '300px', width: '540px', height: '304px', objectFit: 'cover', filter: N.BW }); C.setSrc(im, W(f));
        const cap = T.caption(L, `0${i + 1} · ${role}`, zh + ' · 一个模版', x, 630); st.c.push([im, cap]); });
      st.h = K.center(el(L, 'div', 'abs mono', { top: '200px', fontSize: '20px', color: '#d9cdb2' }, '— ONE STYLE · THREE PARTS —')); st.g = T.grain(L, .22);
      [0, 1, 2].forEach(i => k.sfx('click', 9.9 + i * .45, .08)); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); st.h.style.opacity = P(lt, .1, .3); st.c.forEach(([im, cap], i) => { const u = P(t, 9.9 + i * .45, .5); im.style.opacity = u; im.style.filter = N.BW + ` blur(${(1 - u) * 8}px)`; cap.style.opacity = P(t, 10.2 + i * .45, .3); }); } });

  // P5 · red book-cover title card
  C.scene({ t0: 13.0, t1: C.end + .05, bg: '#14110e', build(L) {
      const st = {}; st.cv = T.cover(L, '视频风格', 110, 160, 260, 680);
      st.k = el(L, 'div', 'abs', { left: '440px', top: '220px', fontFamily: N.SERIF, fontSize: '30px', color: N.RED, borderLeft: `4px solid ${N.RED}`, paddingLeft: '14px' }, '2026 · 第 12 号模版');
      st.a = T.headline(L, 'Eva · 旧报纸', 440, 300, 120, '#f1e6cf'); st.b = el(L, 'div', 'abs', { left: '446px', top: '470px', fontFamily: 'Georgia,serif', fontSize: '64px', color: '#f1e6cf', letterSpacing: '.06em' }, 'OLD NEWSPAPER');
      st.n1 = el(L, 'div', 'abs', { left: '446px', top: '600px', fontFamily: N.SERIF, fontWeight: 900, fontSize: '50px', color: N.RED }, '黑白 · 颗粒 · 红章'); st.g = T.grain(L, .22);
      k.sfx('impact', 13.2, .14); k.sfx('pop', 14.2, .1); return st; },
    update(lt, st, t) { T.grainAt(st.g, t); tf(st.cv, { sx: ease.outExpo(P(lt, .05, .6)), o: 1 }); tf(st.k, { o: P(lt, .5, .3) }); tf(st.a, slide(lt, .6, .45, -40, 0)); tf(st.b, { o: P(lt, .9, .4) }); tf(st.n1, pop(t, 14.2, .35, 1.5)); } });
})();
