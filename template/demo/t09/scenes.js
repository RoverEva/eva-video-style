/* T09 Showcase Wall Opener — demo on the shared 15 s intro. Tiles are real frames from the HatchElite screen recordings and cartoon clips.
 * Responsive: 16:9 = original layout; 9:16 = taller tile wall, titles in the top zone, presenter card / circle below them. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, I = IN, V = C.portrait, pk = C.pick; I.setup(C);
  const Z = (L, s, ox, oy) => el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', transform: `scale(${s})`, transformOrigin: `${ox || 0}px ${oy || 0}px` });
  const pad = n => String(n).padStart(5, '0'), SRC = [['web', 451], ['wb', 3327], ['fly', 286], ['whis', 403], ['sent', 2088], ['match', 387], ['egg', 151], ['jmw', 151]];
  const NT = pk(55, 96), COLS = pk(11, 8);
  const WALL = Array.from({ length: NT }, (_, i) => { const [d, n] = SRC[i % SRC.length]; return `../media/${d}/f_${pad(Math.floor(((i * 37) % 97) / 97 * (n - 1)))}.jpg`; });
  /* optional: ?wall=DIR&wallN=FRAMES builds the wall from slices of one video (30 fps JPGs); each tile plays its own slice */
  const WD = C.params.get('wall'), WN = +(C.params.get('wallN') || 0), WOFF = Array.from({ length: NT }, (_, i) => Math.floor(((i * 37) % NT) / NT * Math.max(0, WN - 60)));
  const CARD = pk({ x: 1240, y: 170, w: 560, h: 700, r: 8, s: 1.5 }, { x: 190, y: 880, w: 700, h: 660, r: 8, s: 1.5 }),
    TR = pk({ x: 1600, y: 60, w: 240, h: 240, r: 120, s: 3 }, { x: 390, y: 980, w: 300, h: 300, r: 150, s: 3 });
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: 2.5, d: .3, L: CARD }, { t: 7.73, d: .45, L: TR }, { t: 12.07, d: .45, L: CARD }];
  C.ringFn = t => t >= 7.9 && t < 12.1 ? { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 } : { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' };
  const frame = (L, n) => T.hudFrame(L, 'EVA · VIDEO STYLE', n);
  const X = pk(110, 64), CW = 952, kick = (L, txt, x, y, col) => { const e = T.kicker(L, txt, x, y, col); if (V) { e.style.fontSize = '24px'; C.fit(e, CW); } return e; };
  const big = e => V ? C.fit(e, CW) : e;

  // W1 · 3D wall of real frames sweeping past; counter rolls to 20 templates
  C.scene({ t0: 0, t1: 1.93, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; const wrap = el(L, 'div', 'abs', { left: pk(-400, -360) + 'px', top: '-120px', width: pk(2900, 2400) + 'px', height: pk(1400, 2300) + 'px', transformOrigin: '30% 50%' }); st.wrap = wrap;
      const R = C.rng(4); st.tiles = WALL.map((f, i) => { const c = i % COLS, r = Math.floor(i / COLS); const tl = el(wrap, 'img', 'abs', { left: (c * 262 + (r % 2) * 60) + 'px', top: (r * 170) + 'px', width: '240px', height: '135px', objectFit: 'cover', borderRadius: '6px', boxShadow: '0 10px 30px rgba(0,0,0,.6)' }); C.setSrc(tl, WD ? `${WD}/f_${pad(WOFF[i])}.jpg` : f); tl.d = R() * 1.2; return tl; });
      st.fr = frame(L, '01'); st.dim = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', background: 'rgba(5,6,10,.6)' });
      st.o = T.odometer(L, '20', pk(820, 360), pk(380, 640), 240, '#fff', false); st.k = kick(L, 'TEMPLATES · EVA VIDEO STYLE', pk(760, 200), pk(660, 920), T.HUD.GOLD);
      k.sfx('whoosh', .1, .12); for (let i = 0; i < 8; i++) k.sfx('click', .9 + i * .08, .05); k.sfx('ding', 1.6, .08); return st; },
    update(lt, st, t) { st.wrap.style.transform = `perspective(1400px) rotateY(${-24 + 6 * lt / 2}deg) rotateX(14deg) translateX(${-pk(300, 160) * lt}px)`;
      st.tiles.forEach((tl, i) => { tl.style.opacity = clamp((lt - tl.d * .4) * 4); if (WD) C.setSrc(tl, C.seq(WD, WOFF[i] / 30 + lt, WN)); }); T.hudFrameAt(st.fr, t);
      const d = P(t, .8, .3); st.dim.style.opacity = d; st.o.row.style.opacity = d; tf(st.k, slide(t, 1.2, .4, 0, 20)); T.odometerAt(st.o, t, .9, .8); } });

  // W2 · blue iris wipe with a spark burst
  C.scene({ t0: 1.9, t1: 2.63, bg: T.HUD.BG, z: 70, build(L) {
      const st = {}; st.c = el(L, 'div', 'abs', { left: (C.W / 2) + 'px', top: (C.H / 2) + 'px', width: '10px', height: '10px', marginLeft: '-5px', marginTop: '-5px', borderRadius: '50%', background: '#2f6bff', transformOrigin: '50% 50%', boxShadow: '0 0 80px #2f6bff' });
      st.m = T.metal(L, '', pk(400, 860), 10); k.sfx('impact', 1.95, .16); return st; },
    update(lt, st) { const u = ease.outExpo(P(lt, .02, .45)); tf(st.c, { s: 1 + pk(260, 420) * u }); st.c.style.opacity = 1 - P(lt, .5, .2); T.metalAt(st.m, lt, .05); } });

  // W3 · "OPEN-SOURCE / AI VIDEO EDITING." title beside (16:9) or above (9:16) the presenter card
  C.scene({ t0: 2.6, t1: 3.9, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '02'); st.k1 = kick(L, '—  HI, I\'M EVA  —', pk(300, 380), pk(360, 300), T.HUD.GOLD);
      st.h = big(el(L, 'div', 'abs disp', { left: pk(160, X) + 'px', width: pk(900, CW) + 'px', textAlign: 'center', top: pk(400, 360) + 'px', fontSize: '150px', color: '#fff' }, 'OPEN-SOURCE')); K.O(st.h, '50% 50%');
      st.g = big(el(L, 'div', 'abs disp', { left: pk(160, X) + 'px', width: pk(900, CW) + 'px', textAlign: 'center', top: pk(580, 540) + 'px', fontSize: pk(70, 76) + 'px', color: T.HUD.GOLD }, 'AI VIDEO-EDITING SKILL'));
      k.sfx('pop', 2.7, .12); k.sfx('ding', 3.0, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); st.h.style.filter = `blur(${12 * (1 - ease.out3(P(lt, .05, .5)))}px)`; tf(st.h, { o: P(lt, .05, .3), s: 1.1 - .1 * ease.outExpo(P(lt, .05, .7)) }); tf(st.g, slide(lt, .4, .4, 0, 30)); tf(st.k1, { o: P(lt, .2, .3) }); } });

  // W4 · four styles as HUD rows
  C.scene({ t0: 3.87, t1: 7.76, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '03'); st.h = T.title(L, 'CHOOSE YOUR ', 'STYLE', X, pk(110, 230), pk(54, 66), '#fff');
      st.r = T.rows(Z(L, pk(1.6, 1.4), X, pk(260, 360)), X, pk(260, 360), [['🎬', 'Cinematic', 'film light · big type'], ['🛰️', 'Futuristic tech', 'HUD · glow · data'], ['📱', 'Social media', 'fast cuts · stickers'], ['◻️', 'Minimalist', 'quiet type · one line']], pk(640, 610));
      [3.87, 4.73, 5.87, 6.6].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 100 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); st.r.forEach((r, i) => tf(r, slide(t, [3.9, 4.73, 5.87, 6.6][i], .35, -40, 0)));  } });

  // W5 · ready-to-use templates: pick → apply → AI edits
  C.scene({ t0: 7.73, t1: 12.1, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '04'); st.h = T.title(L, 'READY-TO-USE ', 'TEMPLATES', X, pk(110, 230), pk(64, 70), '#fff'); if (V) C.fit(st.h, CW);
      st.f = T.flow(Z(L, pk(1.7, 1.32), X, pk(360, 420)), X, pk(360, 420), [['👆', 'Pick'], ['🎞️', 'Apply', T.HUD.BLUE], ['🤖', 'AI edits', T.HUD.GOLD]], pk(260, 250));
      st.k = kick(L, 'YOUR FOOTAGE · YOUR SUBTITLES · ONE TEMPLATE', pk(116, X), pk(760, 720), T.HUD.DIM);
      k.sfx('whoosh', 7.75, .1); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); T.flowAt(st.f, t, 8.97, .85); tf(st.k, { o: P(t, 10.9, .4) }); } });

  // W6 · less editing, more creating + CTA
  C.scene({ t0: 12.07, t1: C.end + .05, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L, '05'); st.hi = el(L, 'div', 'abs disp', { left: pk(160, X) + 'px', top: pk(230, 250) + 'px', fontSize: pk(150, 140) + 'px', color: 'rgba(255,255,255,.55)' }, 'LESS EDITING.');
      st.nm = el(L, 'div', 'abs disp', { left: pk(160, X) + 'px', top: pk(390, 395) + 'px', fontSize: pk(150, 140) + 'px', color: '#fff' }, 'MORE');
      st.g = el(L, 'div', 'abs disp', { left: pk(160, X) + 'px', top: pk(530, 540) + 'px', fontSize: pk(150, 140) + 'px', color: T.HUD.GOLD }, 'CREATING.');
      st.sub = kick(L, 'TRY EVA VIDEO STYLE TODAY  →  GITHUB.COM/ROVEREVA', pk(166, X), pk(730, 720), T.HUD.BLUE);
      k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .12, { f: 1100 }); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.hi, slide(t, 12.1, .4, -60, 0)); tf(st.nm, slide(t, 12.9, .45, -60, 0)); tf(st.g, slide(t, 13.1, .45, -60, 0)); tf(st.sub, { o: P(t, 13.8, .4) }); } });
})();
