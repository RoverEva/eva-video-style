/* Eva Video Style · T27 · 视频墙动感大字 · Video Wall Kinetic Typography. Load after kit.js and templates.js.
 *
 * Layer order (fixed):  video wall (z1–2) → kinetic typography (z5, BEHIND the presenter) → presenter cut-out with a
 * white chalk outline that floats 8–15 px outside the silhouette (z10) → minimal hand-drawn rays / accents (z15).
 *
 *   const o = T.vwStage(L, { wall: [...srcs], speed: 26 })        build once
 *   T.vwStageAt(o, t, cutSrc, { s, x, y }, fullFrameSrc)          every frame: wall scrolls; her pixels = original frame masked by the cut-out
 *   const w = T.vwWords(o, [{ t: '天天做自媒体', c: 'w' }, { t: '却没法变现', c: 'g' }], { layout: 'A' })
 *   T.vwWordsAt(w, t, t0, t1)                                     pop / scale / slide / impact / shake, exit at t1
 *   const r = T.vwRays(o, x, y, 'l')  →  T.vwRaysAt(r, t, t0, t1)  hand-drawn white strokes beside a keyword
 *   T.vwPlan(cues, { keys })                                      script (SRT cues or EV.asr segments) → shots with
 *                                                                 1–2 line splits and accent colours; nothing hard-coded
 * Presenter cut-outs come from scripts/matte.py (RVM, cached RGBA webp per frame). The outline is an SVG
 * filter on the cut-out's alpha (blur → threshold → dilate ring → fixed-noise wobble): it follows arms and palms
 * loosely, stays continuous and does not flicker; no per-frame refinement, so it costs nothing beyond the cached matte.
 * Works in 16:9 and 9:16 (EV.W / EV.H); colours: white, lime, indigo, all with a black stroke. */
(function () {
  const C = window.EV, K = window.K, T = K.T || (K.T = {}), { el, tf, P, ease, clamp } = C;
  const VW = T.VW = { W: '#ffffff', G: '#c6ff1a', I: '#3b2bff', INK: '#07060d', FONT: "'Noto Sans CJK SC','Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif" };
  const COL = c => ({ w: VW.W, g: VW.G, i: VW.W })[c] || c || VW.W;

  /* chalk outline ring, a GAP away from the body: blur + threshold the cut-out alpha (smooth, stable silhouette; small
   * fingers merge into the palm), dilate twice and subtract → a ring of width STROKE sitting GAP px outside her, warped by a
   * fixed low-frequency noise (hand-drawn wobble that does not flicker) and broken up by a fine chalk grain. */
  T.vwDefs = (gap, stroke) => { gap = gap == null ? 10 : gap; stroke = stroke || 18; const id = `vwRing${gap}_${stroke}`; if (document.getElementById(id)) return id;
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('width', 0); s.setAttribute('height', 0); s.style.position = 'absolute';
    s.innerHTML = `<filter id="${id}" x="-4%" y="-4%" width="108%" height="108%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="${Math.round(stroke * .55)}" result="b"/>
      <feComponentTransfer in="b" result="m"><feFuncA type="linear" slope="18" intercept="-6"/></feComponentTransfer>
      <feMorphology in="m" operator="dilate" radius="${gap}" result="o1"/>
      <feMorphology in="m" operator="dilate" radius="${gap + stroke}" result="o2"/>
      <feComposite in="o2" in2="o1" operator="out" result="ring"/>
      <feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="2" seed="11" result="wob"/>
      <feDisplacementMap in="ring" in2="wob" scale="${Math.round(stroke * .9)}" xChannelSelector="R" yChannelSelector="G" result="rw"/>
            <feGaussianBlur in="rw" stdDeviation=".8" result="rs"/><feComponentTransfer in="rs" result="rc"><feFuncA type="linear" slope="2.2" intercept="-.6"/></feComponentTransfer>
      <feFlood flood-color="#ffffff"/><feComposite in2="rc" operator="in"/></filter>`;
    document.body.appendChild(s); return id; };
  /* presenter-only grade: mild unsharp mask so face, eyes and hair stay crisp after the cut-out is scaled */
  T.vwSharp = () => { if (document.getElementById('vwSharp')) return 'vwSharp'; const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('width', 0); s.setAttribute('height', 0); s.style.position = 'absolute';
    s.innerHTML = '<filter id="vwSharp" color-interpolation-filters="sRGB"><feConvolveMatrix order="3" kernelMatrix="0 -.35 0 -.35 2.4 -.35 0 -.35 0" preserveAlpha="true"/></filter>'; document.body.appendChild(s); return 'vwSharp'; };

  /* stage: scrolling video wall + type layer + outlined presenter + fx layer */
  T.vwStage = (L, opt) => { opt = opt || {}; const W = C.W, H = C.H, o = { opt, speed: opt.speed || 26 };
    const box = (z, st) => el(L, 'div', 'abs', Object.assign({ left: 0, top: 0, width: W + 'px', height: H + 'px', zIndex: z, overflow: 'hidden' }, st || {}));
    o.wall = box(1, { background: '#0b0a1c' }); const srcs = opt.wall || [];
    const tw = opt.tile || 430, th = Math.round(tw * .5625), gap = 22, rows = Math.ceil(H / (th + gap)) + 3, per = Math.ceil((W * 1.6) / (tw + gap)) + 2;
    o.persp = el(o.wall, 'div', 'abs', { left: (-W * .3) + 'px', top: (-th) + 'px', width: (W * 1.6) + 'px', height: (H + th * 2) + 'px', transform: `perspective(1600px) rotateY(${opt.tilt == null ? -14 : opt.tilt}deg) rotateX(6deg)`, transformOrigin: '40% 50%', filter: `blur(${opt.blur == null ? 5 : opt.blur}px) saturate(1.45) brightness(1.25) contrast(1.05)` });
    o.rows = Array.from({ length: rows }, (_, r) => { const row = el(o.persp, 'div', 'abs', { left: 0, top: (r * (th + gap)) + 'px', height: th + 'px', width: (per * 2 * (tw + gap)) + 'px' }); row.v = (r % 2 ? 1.25 : .9) * (1 + (r % 3) * .08); row.w = per * (tw + gap);
      for (let i = 0; i < per * 2; i++) { const s = srcs.length && (r * 7 + i * 3) % 5 ? srcs[(r * 7 + i * 3) % srcs.length] : null; const tl = el(row, s ? 'img' : 'div', 'abs', { left: (i * (tw + gap) + (r % 2) * tw * .45) + 'px', top: 0, width: tw + 'px', height: th + 'px', objectFit: 'cover', borderRadius: '10px', background: s ? '#16163a' : ['#c6ff1a', '#3b2bff', '#c6ff1a', '#e8304a', '#7b5cff'][(r * 3 + i) % 5], boxShadow: '0 10px 26px rgba(0,0,0,.55)' }); if (s) C.setSrc(tl, s); tl.f = (r * 13 + i * 7) % 11; }
      return row; });
    o.tint = box(2, { background: `radial-gradient(${W * .62}px ${H * .7}px at 50% 50%, rgba(30,20,90,0), rgba(8,6,24,.42) 88%), linear-gradient(180deg, rgba(10,8,30,.18), rgba(10,8,30,0) 35%, rgba(6,5,16,.35))` });
    o.type = box(5, { overflow: 'visible' }); o.cw = box(10, { overflow: 'visible' }); const sc = Math.min(C.W, C.H) / 1080, fid = T.vwDefs(Math.round((opt.gap == null ? 10 : opt.gap) * sc), Math.round((opt.stroke || 18) * sc)), fit = { left: 0, top: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: C.portrait ? '50% 30%' : '50% 50%' };
    o.ring = el(o.cw, 'img', 'abs', Object.assign({ filter: `url(#${fid}) drop-shadow(0 4px 6px rgba(0,0,0,.45))` }, fit)); o.sh = el(o.cw, 'div', 'abs', Object.assign({ filter: `drop-shadow(0 22px 34px rgba(0,0,0,.45))` }, fit, { objectFit: '' }));
    /* sharpness: her pixels come from the ORIGINAL frame; the cut-out is used only as an alpha mask (no re-encoded colour, no blur) */
    o.cut = el(o.sh, 'img', 'abs', Object.assign({ filter: `url(#${T.vwSharp()}) brightness(${opt.lift || 1.12}) contrast(1.06) saturate(1.12)`, WebkitMaskSize: 'cover', maskSize: 'cover', WebkitMaskPosition: C.portrait ? '50% 30%' : '50% 50%', maskPosition: C.portrait ? '50% 30%' : '50% 50%', WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat' }, fit));
    o.fx = box(15, { overflow: 'visible' }); o.svg = K.svg(o.fx, W, H, 0, 0); return o; };
  T.vwStageAt = (o, t, cut, pose, full) => { o.rows.forEach(r => { const x = -((t * o.speed * r.v) % r.w); r.style.transform = `translateX(${x.toFixed(1)}px)`; });
    if (cut) { C.setSrc(o.ring, cut); if (full) { C.setSrc(o.cut, full); const m = `url(${cut})`; if (o.cut._m !== m) { o.cut.style.webkitMaskImage = m; o.cut.style.maskImage = m; o.cut._m = m; } } else C.setSrc(o.cut, cut); } const p = pose || {}; o.cw.style.transformOrigin = '50% 40%'; tf(o.cw, { s: p.s || 1, x: p.x || 0, y: p.y || 0 }); };

  /* layouts keep type in the band around the head (it sits behind her, so the head occludes part of it); 16:9 + 9:16 */
  const LAY = { // [x, y, size, rot, anchor] per line in a 1920×1080 frame (presenter sits low, head ≈ x 800–1120); 9:16 is remapped below
    A: [[110, 50, 1, -4, 'l'], [820, 215, 1, -4, 'l']], B: [[960, 100, 1.12, -3, 'c']], C: [[130, 60, .8, -3, 'l'], [1090, 205, 1.2, -4, 'l']],
    D: [[1060, 60, .8, -3, 'l'], [1120, 220, 1.05, -4, 'l']], E: [[110, 80, 1, -3, 'l'], [470, 245, 1.02, -3, 'l']], F: [[130, 50, .9, -4, 'l'], [880, 205, 1.1, -4, 'l']] };
  T.vwWords = (o, lines, opt) => { opt = opt || {}; const lay = LAY[opt.layout || (lines.length > 1 ? 'A' : 'B')], fs = opt.size || 165, port = C.portrait, out = [];
    lines.forEach((ln, i) => { const [x0, y0, sz, rot, an] = lay[Math.min(i, lay.length - 1)]; let s = Math.round((ln.size || fs) * sz * (port ? .72 : 1));
      let x = port ? (an === 'c' ? C.W / 2 : 60 + (x0 / 1920) * 300) : x0; const y = port ? 180 + y0 * .9 : y0;
      /* keep every line inside the frame: estimate its width (CJK ≈ 1 em, Latin ≈ .58 em, box padding), shift left, then shrink if needed */
      const em = [...ln.t].reduce((a2, ch) => a2 + (/[\u2e80-\uffff]/.test(ch) ? 1.02 : .58), 0) + (ln.c === 'i' || ln.box ? .45 : .1), M = 36;
      if (an !== 'c') { if (x + em * s > C.W - M) x = Math.max(M, C.W - M - em * s); if (x + em * s > C.W - M) s = Math.floor((C.W - M - x) / em); } else if (em * s > C.W - 2 * M) s = Math.floor((C.W - 2 * M) / em);
      const w = el(o.type, 'div', 'abs', { left: (an === 'c' ? x - 1500 : x) + 'px', width: an === 'c' ? '3000px' : 'auto', textAlign: an === 'c' ? 'center' : 'left', top: y + 'px', transformOrigin: an === 'c' ? '50% 60%' : '0 60%', whiteSpace: 'nowrap', display: 'none' });
      const span = el(w, 'span', '', { display: 'inline-block', fontFamily: VW.FONT, fontWeight: 900, fontSize: s + 'px', lineHeight: 1.08, letterSpacing: '.01em', color: COL(ln.c), WebkitTextStroke: `${Math.round(s * .085)}px ${VW.INK}`, paintOrder: 'stroke fill', textShadow: `0 ${Math.round(s * .06)}px 0 ${VW.INK}, 0 ${Math.round(s * .1)}px ${Math.round(s * .16)}px rgba(0,0,0,.45)`, transform: `rotate(${ln.r != null ? ln.r : rot}deg)` }, ln.t);
      if (ln.c === 'i' || ln.box) Object.assign(span.style, { background: VW.I, padding: `${s * .04}px ${s * .16}px ${s * .08}px`, border: `${Math.max(5, s * .05)}px solid ${VW.INK}`, borderRadius: '6px', boxShadow: `${s * .05}px ${s * .06}px 0 ${VW.INK}` });
      w.mode = ln.a || ['pop', 'impact', 'slide', 'scale'][(i + (opt.seed || 0)) % 4]; w.dt = ln.dt != null ? ln.dt : i * (opt.step || .35); out.push(w); });
    return out; };
  T.vwWordsAt = (ws, t, t0, t1) => ws.forEach(w => { const a = t0 + w.dt; if (t < a || t >= t1) { w.style.display = 'none'; return; } w.style.display = '';
    const l = t - a, u = clamp(l / .3), ex = clamp((t1 - t) / .16); let s = 1, x = 0, y = 0, o = 1, bl = 0;
    if (w.mode === 'pop') { s = .35 + .65 * ease.outBack(u, 2.2); o = clamp(u * 4); }
    if (w.mode === 'scale') { const v = clamp(l / .24); s = 1.7 - .7 * ease.out3(v); bl = (1 - v) * 10; o = clamp(v * 3); }
    if (w.mode === 'slide') { const v = clamp(l / .28); x = -260 * (1 - ease.outExpo(v)); o = clamp(v * 3); bl = (1 - v) * 6; }
    if (w.mode === 'impact') { const v = clamp(l / .14), sh = Math.max(0, 1 - l / .4); s = 2.1 - 1.1 * ease.out3(v); x = Math.sin(l * 95) * 12 * sh; y = Math.cos(l * 80) * 8 * sh; o = clamp(v * 3); }
    const br = 1 + .012 * Math.sin(l * 3.2); tf(w, { s: s * br * (.92 + .08 * ex), x, y, o: o * ex }); w.style.filter = bl > .3 ? `blur(${bl.toFixed(1)}px)` : 'none'; });

  /* hand-drawn white accent strokes in a small fan; they draw on, then "boil" a little like hand animation */
  T.vwRays = (o, x, y, side, opt) => { opt = opt || {}; const n = opt.n || 4, g = K.sv(o.svg, 'g', {}), dir = side === 'r' ? 0 : Math.PI, spread = opt.spread || 1.1, R0 = opt.r0 || 46, len = opt.len || 105, rs = [];
    for (let i = 0; i < n; i++) { const a = dir + (i / (n - 1) - .5) * spread + (side === 'r' ? -.25 : .25), p = K.sv(g, 'path', { fill: 'none', stroke: opt.col || '#fff', 'stroke-width': opt.w || 14, 'stroke-linecap': 'round' }); p.a = a; rs.push(p); }
    g.d = { x, y, R0, len, rs, col: opt.col }; g.style.filter = 'drop-shadow(0 3px 0 rgba(0,0,0,.55))'; return g; };
  T.vwRaysAt = (g, t, t0, t1) => { const D = g.d, on = t >= t0 && t < t1; g.style.display = on ? '' : 'none'; if (!on) return; const u = ease.out3(clamp((t - t0) / .22)), boil = Math.floor(t * 8);
    D.rs.forEach((p, i) => { const j = ((boil * 31 + i * 17) % 7 - 3) * .6, a = p.a + j * .01, r0 = D.R0 + j, r1 = r0 + D.len * u; const xa = D.x + Math.cos(a) * r0, ya = D.y + Math.sin(a) * r0, xb = D.x + Math.cos(a) * r1, yb = D.y + Math.sin(a) * r1;
      p.setAttribute('d', `M${xa.toFixed(1)} ${ya.toFixed(1)} L${xb.toFixed(1)} ${yb.toFixed(1)}`); p.setAttribute('opacity', clamp((t1 - t) / .15)); }); };

  /* script → shots. cues: [{start,end,text}] (SRT or EV.asr.segments). Splits each cue into 1–2 lines at punctuation or
   * mid-way, colours the second line lime / indigo (or a listed keyword), keeps pauses: shots shorter than `min` are merged. */
  T.vwPlan = (cues, opt) => { opt = opt || {}; const keys = opt.keys || [], min = opt.min || .9, out = []; let k = 0;
    cues.forEach(c => { const txt = String(c.text).replace(/\s+/g, ''); if (!txt) return; const last = out[out.length - 1];
      if (last && c.start - last.t0 < min) { last.t1 = c.end; return; }
      let a = txt, b = ''; const m = txt.match(/^(.{2,9}?)[，,、？?！!。](.+)$/); if (m) { a = m[1]; b = m[2]; } else if (txt.length > 7) { const h = Math.ceil(txt.length / 2); a = txt.slice(0, h); b = txt.slice(h); }
      const hit = keys.find(x => b.includes(x) || a.includes(x)); const acc = (k++ % 3 === 2) ? 'i' : 'g';
      const lines = b ? [{ t: a, c: 'w' }, { t: b.replace(/[。.]$/, ''), c: acc }] : [{ t: a, c: hit ? acc : 'w' }];
      out.push({ t0: c.start, t1: c.end, lines, layout: b ? 'ACDEF'[k % 5] : 'B' }); });
    for (let i = 0; i < out.length - 1; i++) out[i].t1 = Math.min(out[i].t1 + .25, out[i + 1].t0); return out; };
})();
