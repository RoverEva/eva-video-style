/* T27 Video Wall Kinetic Typography — 5 s sample. Scrolling, softly blurred wall of template frames; big CN words BEHIND the
 * presenter; presenter in front as the original HD frame masked by the AI cut-out, with a white outline that floats beside the
 * silhouette; a few hand-drawn rays. Copy is generic sample text. No sound is built in (see K.cue for per-video sound). */
(function () {
  const C = EV, T = K.T, S = S5, V = C.portrait; S.setup(C);
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const WALL = ['T20_a', 'T01_a', 'T02_a', 'T09_a', 'T11_a', 'T23_a', 'T13_a', 'T10_a', 'T08_a', 'T17_a', 'T14_a', 'T03_a', 'T24_a', 'T21_a'].map(n => `../../../references/samples/${n}.jpg`);
  const full = t => `../media/eva/f_${String(Math.max(0, Math.min(S.FRAMES - 1, Math.round(t * 30)))).padStart(5, '0')}.jpg`;
  const SH = [
    [0, 1.6, [{ t: '一个观点', c: 'w', a: 'impact' }], 'B', [['l', 700, 560], ['r', 1220, 560]]],
    [1.6, 3.3, [{ t: '大字放在', c: 'w' }, { t: '你的身后', c: 'g', a: 'impact' }], 'C', [['r', 1230, 560]]],
    [3.3, S.END + .05, [{ t: 'EVA', c: 'w', size: 200 }, { t: '视频墙', c: 'i' }], 'C', [['l', 700, 580, '#c6ff1a']]]];
  C.scene({ t0: 0, t1: C.end + .05, quiet: true, build(L) {
      const st = { o: T.vwStage(L, { wall: WALL, speed: 26 }) };
      st.sh = SH.map(([a, b, lines, layout, rays], i) => ({ a, b, w: T.vwWords(st.o, lines, { layout, seed: i, step: .5 }), r: rays.map(([sd, x, y, col]) => T.vwRays(st.o, x, y, sd, { col })) }));
      return st; },
    update(lt, st, t) { const u = C.ease.outExpo(C.P(t, 0, .7));
      T.vwStageAt(st.o, t, S.cut(t), V ? { s: 1.05 - .1 * u, y: 520 } : { s: (1.06 - .22 * u) + .025 * (t / C.end), y: 40 + 125 * u }, full(t));
      st.sh.forEach(s => { T.vwWordsAt(s.w, t, s.a, s.b); s.r.forEach(r => T.vwRaysAt(r, t, s.a + .3, s.b)); }); } });
})();
