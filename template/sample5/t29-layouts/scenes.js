/* T29 Depth Glow · all 9 layouts, 2 s each, on the AI presenter sample clip (looped). Graphics render behind the presenter. */
(function () {
  const C = EV, T = K.T, N = 151, D = 2; C.src0 = 0; C.end = 9 * D; C.evaDir = '../media26/eva'; C.face = { x: .5, y: .33, h: .2 }; C.src = { w: 1080, h: 1920 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const f = t => { const i = Math.round(t * 30) % (2 * N - 2); return i < N ? i : 2 * N - 2 - i; };   /* ping-pong loop of the 5 s clip */
  const fr = (d, t, ext, n) => `../media26/${d}/f_${String(Math.min(n - 1, f(t))).padStart(5, '0')}.${ext}`;
  const m = { frame: t => fr('eva', t, 'jpg', N), cut: t => fr('cut', t, 'webp', 150) };
  const W = { 1: { a: '资料很少', k: 'NEW' }, 2: { a: 'AI VIDEO', k: 'TRENDING' }, 3: { items: ['AI tutorial', 'How-to guide', 'Your website'] }, 4: { a: 'AI ASSISTANT' },
    5: { a: 'best way to make an AI video?' }, 6: { a: 'INDEXED' }, 7: { a: '我的网站' }, 8: { a: 'FAQ' }, 9: { a: 'NEW', b: '一键直达' } };
  for (let n = 1; n <= 9; n++) { const t0 = (n - 1) * D;
    C.scene({ t0, t1: t0 + D, bg: T.dgBg, quiet: true, build(L) { const o = T.dgLayout(n, L, W[n], m);
        K.hud(L, `T29 · ${String(n).padStart(2, '0')}`, '#fff', 40, C.H - 60, 26, { opacity: .5, zIndex: 90 }); return o; },
      update(lt, o, t) { T.dgLayoutAt(o, t, t0, m); } }); }
})();
