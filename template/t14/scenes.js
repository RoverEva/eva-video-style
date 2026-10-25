/* T14 FUT · 未来科技 Future Style — demo (18 s). The wave floor moves in every shot; the globe turns slowly. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, F = T.FUT;
  C.src0 = 10; C.end = 18; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const LOW = { x: 150, y: 700, w: 240, h: 240, r: 120, s: 3 }, CARD = { x: 120, y: 190, w: 500, h: 620, r: 28, s: 1.5 }, RING = { x: 1100, y: 330, w: 360, h: 360, r: 180, s: 2.6 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, LOW, { o: 0 }) }, { t: 1.2, d: .4, L: LOW }, { t: 9.0, d: .5, L: CARD }, { t: 13.5, d: .6, L: RING }];
  C.ringFn = () => ({ color: F.CYAN, width: 3, glow: 'rgba(46,230,255,.55)', shadow: .5 });
  const wave = L => T.wave(L, { horizon: 560, amp: 70 });

  // F1 + F2 · BREAKING NEWS → RULE 1/2/3, one continuous globe that keeps turning
  C.scene({ t0: 0, t1: 9.03, bg: T.futBg, quiet: true, build(L) {
      const st = {}; st.w = wave(L); st.g = T.globeT(L, 1330, 470, 330);
      st.ti = T.futTitle(L, 'BREAKING', 'NEWS', '重磅消息', 130, 190, 150);
      st.r = T.rules(L, ['规则一', '规则二', '规则三'], 130, 110, 'RULE', 110);
      k.sfx('riser', .1, .08, { d: 1.2 }); k.sfx('impact', 1.0, .18); k.sfx('ding', 1.7, .07);
      k.sfx('whoosh', 4.5, .1); [4.8, 5.4, 6.0].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 140 })); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.globeTAt(st.g, t, P(lt, 0, .8));
      const a = t < 4.5; st.ti.style.display = a ? 'block' : 'none'; st.r.forEach(r => { r.style.display = a ? 'none' : 'block'; if (r.line) r.line.style.display = r.style.display; });
      T.futTitleAt(st.ti, t, 1.0); T.rulesAt(st.r, t, 4.8, .6); } });

  // F3 · circuit chip (Eva in a big rounded card)
  C.scene({ t0: 9.0, t1: 13.53, bg: T.futBg, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 520, amp: 55, speed: 1.2 }); st.c = T.chip(L, 1440, 720, 300);
      st.ti = T.futTitle(L, 'FUTURE', 'STYLE', '未来科技模版', 720, 150, 120);
      k.sfx('whoosh', 9.1, .1); k.sfx('impact', 9.5, .14); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.chipAt(st.c, t); st.c.cv.style.opacity = P(lt, .1, .5); T.futTitleAt(st.ti, t, 9.4); } });

  // F4 · wireframe ring with Eva inside it
  C.scene({ t0: 13.5, t1: C.end + .05, bg: T.futBg, build(L) {
      const st = {}; st.w = T.wave(L, { horizon: 600, amp: 60, speed: .9 }); st.o = T.torus(L, 1280, 510, 300, 70);
      st.ti = T.futTitle(L, 'SEE YOU', 'NEXT TIME', '下期见', 130, 220, 120);
      k.sfx('riser', 13.5, .08, { d: .8 }); k.sfx('ding', 14.6, .08); return st; },
    update(lt, st, t) { T.waveAt(st.w, t); T.torusAt(st.o, t); st.o.cv.style.opacity = P(lt, 0, .6); T.futTitleAt(st.ti, t, 14.2); } });
})();
