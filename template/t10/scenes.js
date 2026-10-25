/* T10 KEY · HUD 发布会 HUD Keynote — demo (16 s) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T;
  C.src0 = 24; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const CARD = { x: 1230, y: 70, w: 560, h: 640, r: 8, s: 1.5, o: 1 }, SMALL = { x: 1440, y: 120, w: 380, h: 400, r: 8, s: 2 }, CIRC = { x: 1600, y: 70, w: 240, h: 240, r: 120, s: 3 };
  C.evaKeys = [
    { t: 0, d: 0, L: CARD }, { t: 3.2, d: .45, L: SMALL }, { t: 6.4, d: .45, L: CARD }, { t: 7.5, d: .45, L: CIRC }, { t: 13.6, d: .4, L: Object.assign({}, CIRC, { o: 0 }) },
  ];
  C.ringFn = t => t < 7.5 ? { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' } : { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 };
  let FR; const frame = L => { const f = T.hudFrame(L, 'EVA · KEYNOTE', '03'); return f; };

  // K1 · glowing S-curve with comet + gold headline
  C.scene({ t0: 0, t1: 3.23, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '持续', '打磨', 110, 110, 54, '#fff');
      st.c = T.curve(L, 110, 330, 1000, 300); st.g = el(L, 'div', 'abs cn', { left: '720px', top: '380px', fontSize: '84px', color: T.HUD.GOLD, textShadow: '0 0 30px rgba(245,184,61,.45)' }, '越做越好');
      st.k = T.kicker(L, 'MOTION STANDARD · 动效标准', 724, 490, T.HUD.DIM); k.sfx('riser', .6, .1, { d: 1.2 }); k.sfx('ding', 1.9, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); T.curveAt(st.c, ease.io3(P(lt, .5, 1.6))); tf(st.g, slide(lt, 1.8, .45, 0, 30)); tf(st.k, { o: P(lt, 2.2, .3) }); } });

  // K2 · rolling counter (in real edits: only a number Eva actually says)
  C.scene({ t0: 3.2, t1: 6.43, bg: T.hudBg, cls: 'dotgrid-w', build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '', 'SAMPLE NUMBER · 示例数字', 420, 250, 40, T.HUD.BLUE); st.o = T.odometer(L, '1000+', 430, 360, 220, '#fff');
      st.k = T.kicker(L, 'REPLACE WITH EVA\'S NUMBER', 434, 650); for (let i = 0; i < 12; i++) k.sfx('click', 3.6 + i * .08, .05); k.sfx('ding', 4.9, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, { o: P(lt, .1, .3) }); T.odometerAt(st.o, t, 3.6, 1.2); tf(st.k, { o: P(lt, 1.4, .3) }); } });

  // K3 · BREAKING + big title
  C.scene({ t0: 6.4, t1: 8.63, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.b = T.breaking(L, 700, 380, 'BREAKING · 01'); st.h = el(L, 'div', 'abs cn', { left: '560px', top: '430px', fontSize: '130px', color: '#fff' }, '重磅消息'); K.O(st.h, '50% 50%');
      k.sfx('impact', 7.6, .18); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); st.b.style.opacity = (Math.floor(lt * 4) % 2 ? .4 : 1) * P(lt, .1, .2); const p = pop(t, 7.6, .45, 1.4); tf(st.h, { s: 1.3 - .3 * p.s, o: p.o }); st.h.style.filter = `blur(${10 * (1 - P(t, 7.6, .4))}px)`; } });

  // K4 · dotted globe + gold orbit
  C.scene({ t0: 8.6, t1: 11.43, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.g = T.globe(L, 860, 560, 260); st.h = T.title(L, '分享给 · ', '更多家庭', 110, 110, 54, T.HUD.GOLD);
      st.k = T.kicker(L, 'SHARING · WORLDWIDE', 116, 190, T.HUD.GOLD); k.sfx('whoosh', 9.6, .1); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.globeAt(st.g, lt, ease.io3(P(lt, 1.0, 1.2))); st.g.cv.style.opacity = P(lt, .05, .4); tf(st.h, slide(lt, .4, .4, -40, 0)); tf(st.k, { o: P(lt, .8, .3) }); } });

  // K5 · glowing orb → dashed file "?" → file tree (real project files)
  C.scene({ t0: 11.4, t1: 13.63, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '可编辑的', '视频模版', 110, 110, 54);
      st.orb = T.orb(L, 400, 560, 140); st.f = T.fileIcon(L, 310, 450, 180, '?');
      st.r = T.rows(L, 620, 300, [['📄', 'scenes.js', '分镜 · 动效'], ['📁', 'media/', '口播 · 录屏'], ['💬', 'captions.srt', '双语字幕'], ['🔊', 'sfx.wav', '音效 · 无 BGM']]);
      k.sfx('riser', 11.5, .08, { d: .6 }); k.sfx('pop', 12.2, .12); st.r.forEach((_, i) => k.sfx('pop', 12.5 + i * .18, .08, { f: 900 + i * 100 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, { o: P(lt, .1, .3) }); const o = P(lt, .0, .3) * (1 - P(lt, .75, .2)); tf(st.orb, { s: .7 + .3 * Math.sin(lt * 9) * .2 + .3, o });
      const f = P(lt, .8, .3); st.f.s.style.opacity = f; st.f.t.style.opacity = f; st.r.forEach((r, i) => tf(r, slide(t, 12.5 + i * .18, .35, -40, 0))); } });

  // K6 · metallic hero title with spark burst
  C.scene({ t0: 13.6, t1: C.end + .05, bg: `radial-gradient(900px 500px at 50% 45%, #1b2240, ${T.HUD.BG} 70%)`, build(L) {
      const st = {}; st.fr = frame(L); st.k = K.center(T.kicker(L, 'A NEW VIDEO STYLE FOR THE AI ERA', 0, 330, T.HUD.DIM)); st.m = T.metal(L, 'EVA STYLE', 380, 210);
      k.sfx('impact', 13.75, .2); k.sfx('riser', 13.6, .06, { d: .3 }); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.metalAt(st.m, lt, .15); tf(st.k, { o: P(lt, .8, .4) }); } });
})();
