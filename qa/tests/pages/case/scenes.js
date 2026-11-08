/* QA Stage A test page (not a template). One 4 s section, the defect is chosen with ?case=:
 *   good       presenter in a right-hand card at her own scale, animated headline + chip on the left
 *   missing    good + a missing image and a font that is not installed
 *   face_text  T17 regression: full-bleed presenter with a big headline drawn ON TOP of her face
 *   zoom       T26 regression: presenter moved right AND enlarged 1.35x, half her head past the right edge
 *   static     good, but the second scene never animates (an intended static card when the plan says so)
 * Presenter frames, footage size and face calibration come from the URL (eva=, srcw=, srch=, face=) like the SaaS worker. */
(function () {
  const C = EV, { tf, pop, slide } = C, k = K, CASE = C.params.get('case') || 'good';
  C.src0 = 0; C.end = 4; C.evaDir = '../media/eva'; C.face = { x: .5, y: .36, h: .26 };
  const card = { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1 };
  C.evaKeys = CASE === 'face_text' ? [{ t: 0, d: 0, L: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 } }]
    : CASE === 'zoom' ? [{ t: 0, d: 0, L: card }, { t: 1.0, d: .4, L: { x: 500, y: -300, w: 2600, h: 1700, r: 0, s: 1 } }]
    : [{ t: 0, d: 0, L: card }];
  C.ringFn = () => ({ color: '#fff', width: 6 });
  C.scene({ t0: 0, t1: 2.03, bg: k.NAVY, z: CASE === 'face_text' ? 60 : 1, build(L) {
      const st = {};
      if (CASE === 'face_text') {   // headline placed exactly over the face the engine laid out
        const f = C.faceRect({ x: 0, y: 0, w: 1920, h: 1080, s: 1 });
        st.h = k.disp(L, 'FACE', '#d4ff2e', 260, f.x - 40, f.y + f.h * .25);
      } else st.h = k.disp(L, 'QA CHECK', '#fff', 170, 110, 160);
      st.c = k.O(k.chip(L, 'EVA VIDEO STYLE', k.LIME, k.INK, 46, 116, 420));
      if (CASE === 'missing') {
        C.el(L, 'img', '', { position: 'absolute', left: '110px', top: '560px', width: '200px' }).src = 'assets/no-such-logo.png';
        C.el(L, 'div', 'abs', { left: '110px', top: '800px', fontSize: '60px', color: '#fff', fontFamily: "'Eva Missing Font', serif" }, 'MISSING FONT');
      }
      return st; },
    update(lt, st) { tf(st.h, slide(lt, .05, .45, -150, 0)); tf(st.c, pop(lt, .4, .35)); } });
  C.scene({ t0: 2.0, t1: C.end + .05, bg: k.LIME, cls: 'dotgrid', build(L) {
      const st = {}; st.h = k.disp(L, 'SECOND BEAT', k.INK, 150, 110, 200); st.c = k.O(k.chip(L, 'ONE IDEA', k.INK, '#fff', 50, 116, 420)); return st; },
    update: CASE === 'static' ? null : (lt, st) => { tf(st.h, slide(lt, .05, .5, -150, 0)); tf(st.c, pop(lt, .5 + lt * .1, .35)); } });
})();
