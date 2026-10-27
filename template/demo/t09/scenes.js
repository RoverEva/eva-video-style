/* T09 Showcase Wall Opener — demo on the shared 15 s intro. Tiles are real frames from the HatchElite screen recordings and cartoon clips. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, I = IN; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const pad = n => String(n).padStart(5, '0'), SRC = [['web', 451], ['wb', 3327], ['fly', 286], ['whis', 403], ['sent', 2088], ['match', 387], ['egg', 151], ['jmw', 151]];
  const WALL = Array.from({ length: 55 }, (_, i) => { const [d, n] = SRC[i % SRC.length]; return `../media/${d}/f_${pad(Math.floor(((i * 37) % 97) / 97 * (n - 1)))}.jpg`; });
  const CARD = { x: 1240, y: 170, w: 560, h: 700, r: 8, s: 1.5 }, TR = { x: 1600, y: 60, w: 240, h: 240, r: 120, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: 2.5, d: .3, L: CARD }, { t: 7.73, d: .45, L: TR }, { t: 12.07, d: .45, L: CARD }];
  C.ringFn = t => t >= 7.9 && t < 12.1 ? { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 } : { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' };
  const frame = (L, n) => T.hudFrame(L, 'EVA · VIDEO STYLE', n);

  // W1 · 3D wall of real frames sweeping past; counter rolls to 20 templates
  C.scene({ t0: 0, t1: 1.93, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; const wrap = el(L, 'div', 'abs', { left: '-400px', top: '-120px', width: '2900px', height: '1400px', transformOrigin: '30% 50%' }); st.wrap = wrap;
      const R = C.rng(4); st.tiles = WALL.map((f, i) => { const c = i % 11, r = Math.floor(i / 11); const tl = el(wrap, 'img', 'abs', { left: (c * 262 + (r % 2) * 60) + 'px', top: (r * 170) + 'px', width: '240px', height: '135px', objectFit: 'cover', borderRadius: '6px', boxShadow: '0 10px 30px rgba(0,0,0,.6)' }); C.setSrc(tl, f); tl.d = R() * 1.2; return tl; });
      st.fr = frame(L, '01'); st.dim = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: 'rgba(5,6,10,.6)' });
      st.o = T.odometer(L, '20', 820, 380, 240, '#fff', false); st.k = T.kicker(L, 'TEMPLATES · EVA VIDEO STYLE', 760, 660, T.HUD.GOLD);
      k.sfx('whoosh', .1, .12); for (let i = 0; i < 8; i++) k.sfx('click', .9 + i * .08, .05); k.sfx('ding', 1.6, .08); return st; },
    update(lt, st, t) { st.wrap.style.transform = `perspective(1400px) rotateY(${-24 + 6 * lt / 2}deg) rotateX(14deg) translateX(${-300 * lt}px)`;
      st.tiles.forEach(tl => tl.style.opacity = clamp((lt - tl.d * .4) * 4)); T.hudFrameAt(st.fr, t);
      const d = P(t, .8, .3); st.dim.style.opacity = d; st.o.row.style.opacity = d; tf(st.k, slide(t, 1.2, .4, 0, 20)); T.odometerAt(st.o, t, .9, .8); } });

  // W2 · blue iris wipe with a spark burst
  C.scene({ t0: 1.9, t1: 2.63, bg: T.HUD.BG, z: 70, build(L) {
      const st = {}; st.c = el(L, 'div', 'abs', { left: '960px', top: '540px', width: '10px', height: '10px', marginLeft: '-5px', marginTop: '-5px', borderRadius: '50%', background: '#2f6bff', transformOrigin: '50% 50%', boxShadow: '0 0 80px #2f6bff' });
      st.m = T.metal(L, '', 400, 10); k.sfx('impact', 1.95, .16); return st; },
    update(lt, st) { const u = ease.outExpo(P(lt, .02, .45)); tf(st.c, { s: 1 + 260 * u }); st.c.style.opacity = 1 - P(lt, .5, .2); T.metalAt(st.m, lt, .05); } });

  // W3 · "OPEN-SOURCE / AI VIDEO EDITING." title beside the presenter card
  C.scene({ t0: 2.6, t1: 3.9, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '02'); st.k1 = T.kicker(L, '—  HI, I\'M EVA  —', 300, 360, T.HUD.GOLD);
      st.h = el(L, 'div', 'abs disp', { left: '160px', width: '900px', textAlign: 'center', top: '400px', fontSize: '150px', color: '#fff' }, 'OPEN-SOURCE'); K.O(st.h, '50% 50%');
      st.g = el(L, 'div', 'abs disp', { left: '160px', width: '900px', textAlign: 'center', top: '580px', fontSize: '70px', color: T.HUD.GOLD }, 'AI VIDEO-EDITING SKILL');
      k.sfx('pop', 2.7, .12); k.sfx('ding', 3.0, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); st.h.style.filter = `blur(${12 * (1 - ease.out3(P(lt, .05, .5)))}px)`; tf(st.h, { o: P(lt, .05, .3), s: 1.1 - .1 * ease.outExpo(P(lt, .05, .7)) }); tf(st.g, slide(lt, .4, .4, 0, 30)); tf(st.k1, { o: P(lt, .2, .3) }); } });

  // W4 · four styles as HUD rows
  C.scene({ t0: 3.87, t1: 7.76, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '03'); st.h = T.title(L, 'CHOOSE YOUR ', 'STYLE', 110, 110, 54, '#fff');
      st.r = T.rows(Z(L, 1.6, 110, 260), 110, 260, [['🎬', 'Cinematic', 'film light · big type'], ['🛰️', 'Futuristic tech', 'HUD · glow · data'], ['📱', 'Social media', 'fast cuts · stickers'], ['◻️', 'Minimalist', 'quiet type · one line']], 640);
      [3.87, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 100 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); st.r.forEach((r, i) => tf(r, slide(t, [3.9, 4.73, 5.87, 6.6][i], .35, -40, 0)));  } });

  // W5 · ready-to-use templates: pick → apply → AI edits
  C.scene({ t0: 7.73, t1: 12.1, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '04'); st.h = T.title(L, 'READY-TO-USE ', 'TEMPLATES', 110, 110, 64, '#fff');
      st.f = T.flow(Z(L, 1.7, 110, 360), 110, 360, [['👆', 'Pick'], ['🎞️', 'Apply', T.HUD.BLUE], ['🤖', 'AI edits', T.HUD.GOLD]], 260);
      st.k = T.kicker(L, 'YOUR FOOTAGE · YOUR SUBTITLES · ONE TEMPLATE', 116, 760, T.HUD.DIM);
      k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); T.flowAt(st.f, t, 8.97, .85); tf(st.k, { o: P(t, 10.9, .4) }); } });

  // W6 · less editing, more creating + CTA
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '05'); st.hi = el(L, 'div', 'abs disp', { left: '160px', top: '230px', fontSize: '150px', color: 'rgba(255,255,255,.55)' }, 'LESS EDITING.');
      st.nm = el(L, 'div', 'abs disp', { left: '160px', top: '390px', fontSize: '150px', color: '#fff' }, 'MORE');
      st.g = el(L, 'div', 'abs disp', { left: '160px', top: '530px', fontSize: '150px', color: T.HUD.GOLD }, 'CREATING.');
      st.sub = T.kicker(L, 'TRY EVA VIDEO STYLE TODAY  →  GITHUB.COM/ROVEREVA', 166, 730, T.HUD.BLUE);
      k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .12, { f: 1100 }); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.hi, slide(t, 12.1, .4, -60, 0)); tf(st.nm, slide(t, 12.9, .45, -60, 0)); tf(st.g, slide(t, 13.1, .45, -60, 0)); tf(st.sub, { o: P(t, 13.8, .4) }); } });
})();
