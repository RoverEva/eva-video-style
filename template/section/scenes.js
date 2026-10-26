/* Example section · 6 s · hook on full-bleed → lime headline with Eva in a right card → red sunburst with Eva in a circle.
 * Copy this folder per section. Times are seconds local to the section; src0 is where the section starts in Eva's source video. */
(function () {
  const C = EV, { el, tf, pop, slide, wipe, ease } = C, k = K;
  C.src0 = 0;          // section start in the source video (seconds)
  C.end = 6;           // section length (seconds); sections must concatenate to the source frame count
  C.evaDir = '../../media/eva';            // Eva's footage as 30 fps JPGs: f_00000.jpg ...
  C.face = { x: .54, y: .35, h: .5 };      // calibrate on the new footage (see references/pipeline.md)

  // Eva window path: full-bleed → right card → circle top-right
  C.evaKeys = [
    { t: 0, d: 0, L: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 } },
    { t: 2.0, d: .5, L: { x: 1240, y: 170, w: 600, h: 700, r: 36, s: 1.5 } },
    { t: 4.0, d: .45, L: { x: 1590, y: 36, w: 290, h: 290, r: 145, s: 3 } },
  ];
  C.ringFn = t => t < 4 ? { color: k.INK, width: 6, shadow: .22 } : { color: '#fff', width: 8, glow: 'rgba(255,255,255,.5)' };

  // 1 · hook chip over full-bleed Eva (z above Eva so the chip shows on her video)
  C.scene({ t0: 0, t1: 2.03, z: 60, quiet: true, build(L) {
      const st = {}; st.c = k.O(k.chip(L, 'HOOK · THE FIRST 3 SECONDS', k.LIME, k.INK, 46, 110, 110));
      k.sfx('pop', .3, .14); return st; },
    update(lt, st) { tf(st.c, pop(lt, .3, .35)); } });

  // 2 · lime headline + bars (illustrative, no fake numbers)
  C.scene({ t0: 2.0, t1: 4.03, bg: k.LIME, cls: 'dotgrid', build(L) {
      const st = { bars: [] };
      st.h = k.disp(L, 'BIG IDEA', k.INK, 200, 110, 120); st.z = k.O(k.chip(L, 'ONE-LINE KEY IDEA', k.INK, '#fff', 50, 116, 330));
      [180, 260, 420].forEach((h, i) => { const b = k.card(L, 110 + i * 150, 900 - h, 110, h, i === 2 ? k.RED : k.INK, { borderRadius: '10px', transformOrigin: '50% 100%' }); st.bars.push(b); });
      k.note(L, 'ILLUSTRATIVE', 110, 930, k.INK);
      k.sfx('impact', 2.3, .16); return st; },
    update(lt, st) { wipe(st.h.parentNode, ease.outExpo(lt / .3), 'l'); tf(st.h, slide(lt, .05, .45, -150, 0)); tf(st.z, pop(lt, .4, .35));
      st.bars.forEach((b, i) => tf(b, { sy: ease.outBack(C.P(lt, .6 + i * .15, .5)), s: undefined })); } });

  // 3 · red sunburst finale with confetti
  C.scene({ t0: 4.0, t1: C.end + .05, bg: k.RED, build(L) {
      const st = {}; st.sun = k.sunburst(L);
      st.h = k.disp(L, 'YEAH!', '#fff', 260, 110, 300, { textShadow: '8px 8px 0 #0b0b0d' }); k.O(st.h, '50% 50%');
      st.c = k.O(k.chip(L, '♥ LIKE  + FOLLOW', '#fff', k.RED, 52, 116, 640));
      st.conf = k.confetti(L, 70, 3, 150, 1100);
      k.sfx('impact', 4.3, .2); k.sfx('applause', 4.4, .12, { d: 1.2 }); return st; },
    update(lt, st, t) { st.sun.style.transform = `rotate(${lt * 12}deg)`; wipe(st.sun.parentNode, ease.outExpo(lt / .35), 'u');
      tf(st.h, pop(lt, .3, .45, 2.4)); tf(st.c, pop(lt, .8, .35)); k.burst(st.conf, t, 4.4); } });
})();
