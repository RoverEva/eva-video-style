/* T26 Vintage Story · 5 s vertical sample on the AI presenter clip: layouts 01 → 03 → 05 → 09, a new collage slides in on each
 * beat. Copy is generic sample text (no transcript for this clip). Sound: the clip's own voice + per-video cues (K.cue). */
(function () {
  const cue = K.cue || K.sfx;  /* K.cue (per-video cue) = K.sfx in EVA Core */
  const C = EV, T = K.T, F = 151; C.src0 = 0; C.end = 151 / 30; C.evaDir = (window.EVA_TEMPLATE_MEDIA || '../../sample5/media26') + '/eva'; C.face = { x: .5, y: .33, h: .2 }; C.src = { w: 1080, h: 1920 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const fr = (d, t, ext, n) => `${window.EVA_TEMPLATE_MEDIA || '../../sample5/media26'}/${d}/f_${String(Math.max(0, Math.min(n - 1, Math.round(t * 30)))).padStart(5, '0')}.${ext}`;
  const m = { frame: t => fr('eva', t, 'jpg', F), cut: t => fr('cut', t, 'webp', 150) };
  const LAY = [1, 3, 5, 9], B = [0, 1.25, 2.5, 3.75, C.end + .05];
  C.scene({ t0: 0, t1: C.end + .05, bg: T.vtBg, quiet: true, build(L) {
      const st = { g: LAY.map(n => T.vtLayout(n, L, {}, m)) };
      B.slice(1, -1).forEach(b => { cue('whoosh', b - .04, .06); cue('pop', b + .3, .05); }); cue('impact', .05, .07); cue('ding', 4.1, .05); return st; },
    update(lt, st, t) { const i = Math.max(0, B.findIndex((b, j) => t >= b && t < B[j + 1]));
      st.g.forEach((g, j) => { const on = j === i || (j === i - 1 && t < B[i] + .25); g.root.style.display = on ? '' : 'none'; if (!on) return;
        const u = Math.min(1, (t - B[j]) / .25), q = 1 - Math.pow(1 - u, 3); g.root.style.zIndex = j;
        g.root.style.transform = j ? `translateX(${C.W * (1 - q)}px) rotate(${3 * (1 - q)}deg)` : 'none';
        T.vtLayoutAt(g, t, B[j] + (j ? .1 : 0), m, B[j + 1] - B[j]); }); } });
})();
