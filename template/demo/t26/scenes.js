/* T26 Vintage Story (vertical) — all nine layouts in turn (1.6 s each): a design review sheet. Copy is generic sample text;
 * in a real edit every word comes from the script. Presenter = media26/eva (HD frames) + media26/cut (AI cut-out). */
(function () {
  const C = EV, T = K.T, D = 1.6, N = 9, F = 151; C.src0 = 0; C.end = D * N; C.evaDir = (window.EVA_TEMPLATE_MEDIA || '../../sample5/media26') + '/eva'; C.face = { x: .5, y: .33, h: .2 }; C.src = { w: 1080, h: 1920 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const fr = (d, t, ext) => `${window.EVA_TEMPLATE_MEDIA || '../../sample5/media26'}/${d}/f_${String(Math.round((t % (F / 30)) * 30) % F).padStart(5, '0')}.${ext}`;
  const m = { frame: t => fr('eva', t, 'jpg'), cut: t => fr('cut', t, 'webp').replace('f_00150', 'f_00149') };
  for (let n = 1; n <= N; n++) { const t0 = (n - 1) * D;
    C.scene({ t0, t1: t0 + D, bg: T.vtBg, quiet: true, build(L) { return { g: T.vtLayout(n, L, {}, m) }; }, update(lt, st, t) { T.vtLayoutAt(st.g, t, t0, m, D); } }); }
})();
