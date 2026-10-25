/* T09 WALL · 作品墙开场 Showcase Wall Opener — demo (14 s). Tiles are real frames from Eva's own videos. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, T = K.T;
  C.src0 = 10; C.end = 14; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const CARD = { x: 1200, y: 150, w: 560, h: 700, r: 8, s: 1.5 };
  C.evaKeys = [
    { t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) },
    { t: 6.3, d: .3, L: Object.assign({}, CARD, { o: 1 }) },
  ];
  C.ringFn = () => ({ color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' });

  // W1+W2 · 3D wall of works sweeping past, counter rolls to the real tile count
  C.scene({ t0: 0, t1: 5.53, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; const wrap = el(L, 'div', 'abs', { left: '-400px', top: '-120px', width: '2900px', height: '1400px', transform: 'perspective(1400px) rotateY(-24deg) rotateX(14deg)', transformOrigin: '30% 50%' }); st.wrap = wrap;
      const R = C.rng(4); st.tiles = [];
      WALL.forEach((f, i) => { const c = i % 11, r = Math.floor(i / 11); const tl = el(wrap, 'img', 'abs', { left: (c * 262 + (r % 2) * 60) + 'px', top: (r * 170) + 'px', width: '240px', height: '135px', objectFit: 'cover', borderRadius: '6px', boxShadow: '0 10px 30px rgba(0,0,0,.6)' }); C.setSrc(tl, '../../media/wall/' + f); tl.d = R() * 1.2; st.tiles.push(tl); });
      st.fr = T.hudFrame(L, 'EVA · WORKS WALL', '01');
      st.dim = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: 'rgba(5,6,10,.55)' });
      st.o = T.odometer(L, String(WALL.length), 800, 410, 220, '#fff', false); st.k = T.kicker(L, 'FRAMES · FROM EVA\'S VIDEOS', 790, 660, T.HUD.GOLD);
      k.sfx('whoosh', .1, .12); for (let i = 0; i < 10; i++) k.sfx('click', 2.6 + i * .09, .05); k.sfx('ding', 3.6, .08); return st; },
    update(lt, st, t) { st.wrap.style.transform = `perspective(1400px) rotateY(${-24 + 6 * lt / 5.5}deg) rotateX(14deg) translateX(${-260 * lt}px)`;
      st.tiles.forEach(tl => tl.style.opacity = clamp((lt - tl.d * .5) * 3)); T.hudFrameAt(st.fr, t);
      const d = P(t, 2.4, .4); st.dim.style.opacity = d; st.o.row.style.opacity = d; tf(st.k, slide(t, 3.0, .4, 0, 20)); T.odometerAt(st.o, t, 2.5, 1.1); } });

  // W3 · blue iris wipe with a spark burst
  C.scene({ t0: 5.5, t1: 6.53, bg: T.HUD.BG, z: 70, build(L) {
      const st = {}; st.c = el(L, 'div', 'abs', { left: '960px', top: '540px', width: '10px', height: '10px', marginLeft: '-5px', marginTop: '-5px', borderRadius: '50%', background: '#2f6bff', transformOrigin: '50% 50%', boxShadow: '0 0 80px #2f6bff' });
      st.m = T.metal(L, '', 400, 10); k.sfx('impact', 5.6, .16); return st; },
    update(lt, st) { const u = ease.outExpo(P(lt, .05, .55)); tf(st.c, { s: 1 + 260 * u }); st.c.style.opacity = 1 - P(lt, .7, .3); T.metalAt(st.m, lt, .1); } });

  // W4 · title + gold "IS HERE."  ·  W5 · hello card
  C.scene({ t0: 6.5, t1: C.end + .05, bg: T.hudBg, build(L) {
      const st = {}; st.fr = T.hudFrame(L, 'EVA · VIDEO STYLE', '02');
      st.k1 = T.kicker(L, '—  REAL · OPEN · TEMPLATES  —', 300, 380, T.HUD.GOLD);
      st.h = el(L, 'div', 'abs cn', { left: '200px', width: '800px', textAlign: 'center', top: '400px', fontSize: '130px', color: '#fff' }, '模版时代'); st.h.style.transformOrigin = '50% 50%';
      st.g = el(L, 'div', 'abs disp', { left: '200px', width: '800px', textAlign: 'center', top: '570px', fontSize: '84px', color: T.HUD.GOLD }, 'IS HERE.');
      st.ln = el(L, 'div', 'abs', { left: '300px', top: '690px', width: '600px', height: '1px', background: 'rgba(255,255,255,.3)' });
      st.hi = T.kicker(L, '// HELLO, I\'M', 160, 380); st.nm = el(L, 'div', 'abs cn', { left: '160px', top: '410px', fontSize: '170px', color: '#fff' }, 'Eva');
      st.sub = T.kicker(L, 'CREATOR · AI VIDEO EDITING', 166, 630, T.HUD.BLUE);
      k.sfx('pop', 6.8, .12); k.sfx('ding', 7.6, .08); k.sfx('whoosh', 10.4, .1); k.sfx('pop', 10.6, .12, { f: 1100 }); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); const a = t < 10.4;
      [st.k1, st.h, st.g, st.ln].forEach(e => e.style.display = a ? 'block' : 'none'); [st.hi, st.nm, st.sub].forEach(e => e.style.display = a ? 'none' : 'block');
      st.h.style.filter = `blur(${12 * (1 - ease.out3(P(t, 6.7, .6)))}px)`; tf(st.h, { o: P(t, 6.7, .3), s: 1.1 - .1 * ease.outExpo(P(t, 6.7, .8)) });
      tf(st.g, slide(t, 7.6, .45, 0, 30)); tf(st.k1, { o: P(t, 7.2, .4) }); st.ln.style.transform = `scaleX(${ease.outExpo(P(t, 7.0, .8))})`;
      tf(st.hi, slide(t, 10.5, .4, -40, 0)); tf(st.nm, slide(t, 10.6, .45, -60, 0)); tf(st.sub, { o: P(t, 11.0, .4) }); } });
})();
