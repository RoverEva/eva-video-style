/* EVA concept templates T30–T41 · shared motion grammar (K.T.mo). Load after templates.js.
 * Implements EVA_SIGNATURE_MOTION_STYLE.md timing at 30 fps: primary entrance 8–12 frames with a strong ease-out and a
 * ~2.5% overshoot; supporting entrance 6–10 frames; stagger 3–5 frames; exits 6–8 frames, ease-in, quieter than entrances;
 * hero type = directional travel + clip reveal + blur-to-sharp; lines draw by stroke progress; panels clip-reveal.
 * Presenter: the engine's Eva window (circle / rounded square), never a cut-out, never zoomed past the footage.
 * Templates carry no sound. All copy on screen comes from the sample script and is illustrative. */
(function () {
  const C = EV, T = K.T, { el, clamp } = C;
  const M = T.mo = {};
  M.IN = .33; M.OUT = .23; M.ST = .13;
  M.o3 = u => 1 - Math.pow(1 - clamp(u), 3);
  M.o5 = u => 1 - Math.pow(1 - clamp(u), 5);
  M.i2 = u => { u = clamp(u); return u * u; };
  M.os = u => { u = clamp(u); const s = .45; return 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2); };   /* ≈2.5% overshoot */
  M.io = u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
  /* envelope: e = entrance (with overshoot), x = exit 0..1 (ease-in), a = opacity */
  M.env = (t, t0, t1, din, dout) => { din = din || M.IN; dout = dout || M.OUT; t1 = t1 == null ? 1e9 : t1;
    return { e: M.os((t - t0) / din), x: M.i2((t - (t1 - dout)) / dout), a: clamp((t - t0) / (din * .55)) * (1 - M.i2((t - (t1 - dout)) / dout)) }; };
  const st = (e, o) => { e.style.opacity = o.a.toFixed(3); };
  /* hero type: travel from dx/dy, clip reveal (left→right), blur → sharp; exit = short drift + fade */
  M.hero = (e, t, t0, t1, o = {}) => { const din = o.din || .36, v = M.env(t, t0, t1, din, o.dout), c = M.o5((t - t0) / din);
    st(e, v); e.style.filter = `blur(${((1 - M.o3((t - t0) / (din * .9))) * 12).toFixed(2)}px)`;
    e.style.clipPath = o.noclip ? '' : `inset(-20% ${((1 - c) * 100).toFixed(2)}% -20% -5%)`;
    e.style.transform = `${o.base || ''} translate(${((o.dx ?? -60) * (1 - v.e) + (o.xo ?? -24) * v.x).toFixed(1)}px, ${((o.dy ?? 0) * (1 - v.e)).toFixed(1)}px)`; };
  /* supporting rise / pop / slide */
  M.rise = (e, t, t0, t1, o = {}) => { const v = M.env(t, t0, t1, o.din || .27, o.dout); st(e, v);
    e.style.transform = `${o.base || ''} translateY(${((o.dy ?? 34) * (1 - v.e) - 12 * v.x).toFixed(1)}px)`; };
  M.pop = (e, t, t0, t1, o = {}) => { const v = M.env(t, t0, t1, o.din || .3, o.dout); st(e, v);
    e.style.transform = `${o.base || ''} scale(${((o.from ?? .55) + (1 - (o.from ?? .55)) * v.e - .08 * v.x).toFixed(4)})`; };
  M.slide = (e, t, t0, t1, o = {}) => { const v = M.env(t, t0, t1, o.din || .33, o.dout); st(e, v);
    e.style.transform = `${o.base || ''} translate(${((o.dx ?? -80) * (1 - v.e)).toFixed(1)}px, ${((o.dy ?? 0) * (1 - v.e) + 10 * v.x).toFixed(1)}px)`; };
  /* panel: translation + left-to-right clip */
  M.panel = (e, t, t0, t1, o = {}) => { const din = o.din || .4, v = M.env(t, t0, t1, din, o.dout), c = M.o5((t - t0) / din);
    e.style.opacity = (clamp((t - t0) / .1) * (1 - v.x)).toFixed(3);
    e.style.clipPath = `inset(0 ${((1 - c) * 100).toFixed(2)}% 0 0 round ${o.r || 0}px)`;
    e.style.transform = `${o.base || ''} translate(${(-36 * (1 - v.e)).toFixed(1)}px, ${(8 * v.x).toFixed(1)}px)`; };
  /* slap: a sticky note / print lands — oversize, rotate settle, shadow lands */
  M.slap = (e, t, t0, t1, o = {}) => { const v = M.env(t, t0, t1, o.din || .3, o.dout), u = M.os((t - t0) / (o.din || .3));
    st(e, v); e.style.transform = `translate(${o.x || 0}px, ${o.y || 0}px) rotate(${((o.r || 0) + (o.rf ?? 7) * (1 - u)).toFixed(2)}deg) scale(${(1 + .16 * (1 - u)).toFixed(4)})`;
    e.style.boxShadow = `0 ${(8 + 18 * (1 - u)).toFixed(1)}px ${(16 + 26 * (1 - u)).toFixed(1)}px rgba(40,25,10,${(.32 - .12 * (1 - u)).toFixed(3)})`; };
  /* stroke draw: path/line/rect with pathLength="1" stroke-dasharray="1 1" */
  M.draw = (p, t, t0, d = .45, t1) => { p.setAttribute('stroke-dashoffset', (1 - M.o3((t - t0) / d)).toFixed(4));
    p.style.opacity = t1 != null ? (1 - M.i2((t - (t1 - M.OUT)) / M.OUT)).toFixed(3) : 1; };
  /* typewriter: [...text] revealed over d seconds */
  M.type = (e, txt, t, t0, d, caret) => { const ch = [...txt], k = Math.floor(clamp((t - t0) / d) * ch.length);
    e.textContent = ch.slice(0, k).join('') + (caret && k < ch.length && t >= t0 ? '▍' : ''); };
  /* count up a number string like "128.6" */
  M.count = (e, to, t, t0, d, fmt) => { const u = M.o3((t - t0) / d), dec = (String(to).split('.')[1] || '').length; e.textContent = fmt ? fmt((to * u).toFixed(dec)) : (to * u).toFixed(dec); };
  /* svg helper */
  const NS = 'http://www.w3.org/2000/svg';
  M.svg = (p, x, y, w, h, inner, sty) => { const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    Object.assign(s.style, { position: 'absolute', left: x + 'px', top: y + 'px', overflow: 'visible' }, sty || {}); s.innerHTML = inner; p.appendChild(s); return s; };
  M.box = (p, x, y, sty, txt) => el(p, 'div', 'abs', Object.assign({ left: x + 'px', top: y + 'px' }, sty || {}), txt);
  /* pixel text: drawn tiny on a canvas, hard-thresholded, scaled up with nearest-neighbour (authentic 8-bit edges) */
  M.pix = (p, txt, x, y, px, col, shadow) => { const cv = document.createElement('canvas'), g = cv.getContext('2d'), f = "bold 10px 'Space Mono', monospace";
    g.font = f; const w = Math.ceil(g.measureText(txt).width) + 2; cv.width = w; cv.height = 13; g.font = f; g.fillStyle = col; g.textBaseline = 'top'; g.fillText(txt, 1, 1);
    const d = g.getImageData(0, 0, cv.width, cv.height); for (let i = 3; i < d.data.length; i += 4) d.data[i] = d.data[i] > 100 ? 255 : 0; g.putImageData(d, 0, 0);
    Object.assign(cv.style, { position: 'absolute', left: x + 'px', top: y + 'px', width: (w * px) + 'px', height: (13 * px) + 'px', imageRendering: 'pixelated', transformOrigin: '0 50%',
      filter: shadow ? `drop-shadow(${px}px ${px}px 0 ${shadow})` : '' }); p.appendChild(cv); return cv; };
  /* Eva window path: full frame → template window (0.35 s, 0.6 s morph) → … → full frame at the end */
  M.FULL = { x: 0, y: 0, w: 1920, h: 1080, r: 0, o: 1, s: 1 };
  M.win = (W0, extra, end) => { const k = [{ t: 0, d: 0, L: M.FULL }, { t: .35, d: .62, L: W0 }].concat(extra || []); if (end !== false) k.push({ t: (end || 9.2), d: .6, L: M.FULL }); return k; };
  /* bilingual captions (CN on top), caption band from y≈840; crossfade + 14px rise */
  M.captions = (L, list) => { const box = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', pointerEvents: 'none' });
    el(box, 'div', 'abs', { left: 0, top: (C.H - 260) + 'px', width: C.W + 'px', height: '260px', background: 'linear-gradient(rgba(0,0,0,0), rgba(0,0,0,.5))' });
    const items = list.map(c => { const d = el(box, 'div', 'abs', { left: 0, width: C.W + 'px', top: (C.H - 190) + 'px', textAlign: 'center' });
      el(d, 'div', '', { font: "700 48px 'Noto Sans CJK SC', sans-serif", color: '#ffffff', textShadow: '0 2px 12px rgba(0,0,0,.65), 0 0 2px rgba(0,0,0,.9)' }, c.cn);
      el(d, 'div', '', { font: "600 30px Inter, sans-serif", color: '#f2f2f5', marginTop: '6px', textShadow: '0 2px 10px rgba(0,0,0,.65)' }, c.en); return { d, c }; });
    return t => items.forEach(({ d, c }) => { const v = M.env(t, c.t0, c.t1, .25, .18); d.style.opacity = v.a.toFixed(3); d.style.transform = `translateY(${(14 * (1 - M.o3((t - c.t0) / .25))).toFixed(1)}px)`; }); };
  /* common setup for a 10 s concept sample on the Eva raw clip */
  M.setup = (o) => { C.src0 = 0; C.end = 10; C.evaDir = '../../sample10/media/eva'; C.src = { w: 1280, h: 720 }; C.face = { x: .52, y: .3, h: .34 };
    C.evaKeys = M.win(o.win, o.keys, o.end); C.ringFn = o.ring || (() => ({ color: '#fff', width: 0, shadow: .35 }));
    C.scene({ t0: 0, t1: 10.05, bg: o.bg, cls: o.cls || '', quiet: true, build: o.build, update: (lt, s, t) => o.update(s, t) });
    C.scene({ t0: 0, t1: 10.05, z: 70, quiet: true, build: L => M.captions(L, o.captions), update: (lt, f, t) => f(t) }); };
})();
