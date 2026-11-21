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
    const cy = C.portrait ? 1392 : C.H - 190;   /* 9:16: below the presenter, above the platform caption/buttons zone */
    el(box, 'div', 'abs', { left: 0, top: (cy - 70) + 'px', width: C.W + 'px', height: (C.portrait ? 300 : 260) + 'px', background: C.portrait ? 'linear-gradient(rgba(0,0,0,0), rgba(0,0,0,.45) 40%, rgba(0,0,0,0))' : 'linear-gradient(rgba(0,0,0,0), rgba(0,0,0,.5))' });
    const items = list.map(c => { const d = el(box, 'div', 'abs', { left: 0, width: C.W + 'px', top: cy + 'px', textAlign: 'center' });
      el(d, 'div', '', { font: "700 48px 'Noto Sans CJK SC', sans-serif", color: '#ffffff', textShadow: '0 2px 12px rgba(0,0,0,.65), 0 0 2px rgba(0,0,0,.9)' }, c.cn);
      el(d, 'div', '', { font: "600 30px Inter, sans-serif", color: '#f2f2f5', marginTop: '6px', textShadow: '0 2px 10px rgba(0,0,0,.65)' }, c.en); return { d, c }; });
    return t => items.forEach(({ d, c }) => { const v = M.env(t, c.t0, c.t1, .25, .18); d.style.opacity = v.a.toFixed(3); d.style.transform = `translateY(${(14 * (1 - M.o3((t - c.t0) / .25))).toFixed(1)}px)`; }); };
  /* shorthands for T42+ */
  M.CN = "'Noto Sans CJK SC', sans-serif"; M.SERIF = "'Noto Serif CJK SC', serif"; M.AN = 'Anton, sans-serif'; M.MONO = "'Space Mono', monospace"; M.INTER = 'Inter, sans-serif'; M.PF = "'Playfair Display', serif";
  M.f = (w, px, fam) => `${w} ${px}px ${fam}`;
  M.caps = a => a.map(([cn, en], i) => ({ t0: [.5, 3.5, 6.7][i], t1: [3.4, 6.6, 9.7][i], cn, en }));
  M.txt = (p, x, y, font, color, txt, sty) => M.box(p, x, y, Object.assign({ font, color, whiteSpace: 'nowrap' }, sty || {}), txt);
  M.path = (p, x, y, w, h, d, col, sw, ex) => M.svg(p, x, y, w, h, `<path d="${d}" fill="none" stroke="${col}" stroke-width="${sw || 6}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1" ${ex || ''}/>`).querySelector('path');
  M.img = (p, x, y, w, h, f, sty) => { const i = el(p, 'img', 'abs', Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', objectFit: 'cover', objectPosition: '52% 30%' }, sty || {})); i.src = `../../sample10/media/eva/f_${String(f).padStart(5, '0')}.jpg`; return i; };
  /* placeholder brand mark (the studio's own EVA monogram) for logo-only templates: .lr frame (drawable), .lt wordmark */
  M.logo = (p, x, y, sz, col, fill) => M.svg(p, x, y, sz, sz, `<rect class="lr" x="${sz * .04}" y="${sz * .04}" width="${sz * .92}" height="${sz * .92}" rx="${sz * .24}" fill="${fill || 'none'}" stroke="${col}" stroke-width="${sz * .045}" pathLength="1" stroke-dasharray="1 1"/><text class="lt" x="${sz / 2}" y="${sz * .62}" text-anchor="middle" font-family="Anton, sans-serif" font-size="${sz * .36}" fill="${col}" letter-spacing="${sz * .012}">EVA</text>`, { transformOrigin: '50% 50%' });

  /* ================= T101+ : three-scene stories with real transitions (not slides) =================
     Each template = 3 scenes (≈0.45–3.45, 3.45–6.65, 6.65–9.3). Scene changes are transitions (push / zoom / iris / wipe / flip /
     rise / shutter / blur), the whole stage drifts like a camera, and Eva's window re-shapes on every scene change. */
  M.TB = [[.45, 3.45], [3.45, 6.65], [6.65, 9.35]];
  const TRD = .6;   /* transition length (s) */
  const EX = () => C.portrait ? 1200 : 0, EY = () => C.portrait ? 1700 : 0, W = () => 1920 + 2 * EX(), H = () => 1080 + 2 * EY();
  M.TR = {
    push: (o, i, p) => { const e = M.io(p); o.style.transform = `translateX(${(-W() * e).toFixed(1)}px)`; i.style.transform = `translateX(${(W() * (1 - e)).toFixed(1)}px)`; },
    rise: (o, i, p) => { const e = M.io(p); o.style.transform = `translateY(${(-H() * e).toFixed(1)}px)`; i.style.transform = `translateY(${(H() * (1 - e)).toFixed(1)}px)`; },
    zoom: (o, i, p) => { o.style.transform = `scale(${(1 + .6 * M.i2(p)).toFixed(4)})`; o.style.opacity = (1 - M.i2(p)).toFixed(3); o.style.filter = `blur(${(10 * p).toFixed(1)}px)`;
      i.style.transform = `scale(${(.72 + .28 * M.o5(p)).toFixed(4)})`; i.style.opacity = M.o3(p * 1.4).toFixed(3); },
    iris: (o, i, p) => { o.style.transform = `scale(${(1 + .08 * p).toFixed(4)})`; i.style.clipPath = `circle(${((C.portrait ? 2400 : 1300) * M.o3(p)).toFixed(0)}px at 50% 50%)`; },
    wipe: (o, i, p) => { const e = M.io(p); o.style.transform = `translateX(${(-160 * e).toFixed(1)}px)`; o.style.filter = `brightness(${(1 - .4 * e).toFixed(3)})`; i.style.clipPath = `inset(0 ${(100 - 100 * e).toFixed(2)}% 0 0)`; },
    flip: (o, i, p) => { const e = M.io(p); o.style.transform = `perspective(2200px) rotateY(${(90 * Math.min(1, e * 2)).toFixed(2)}deg)`; o.style.opacity = e < .5 ? 1 : 0;
      i.style.transform = `perspective(2200px) rotateY(${(-90 * Math.max(0, 1 - (e - .5) * 2)).toFixed(2)}deg)`; i.style.opacity = e >= .5 ? 1 : 0; },
    shutter: (o, i, p) => { const e = M.io(p); i.style.clipPath = `inset(${(50 * (1 - e)).toFixed(2)}% 0 ${(50 * (1 - e)).toFixed(2)}% 0)`; o.style.transform = `scale(${(1 - .06 * e).toFixed(4)})`; },
    blur: (o, i, p) => { o.style.opacity = (1 - p).toFixed(3); o.style.filter = `blur(${(16 * p).toFixed(1)}px)`; i.style.opacity = p.toFixed(3); i.style.filter = `blur(${(16 * (1 - p)).toFixed(1)}px)`; },
    slide: (o, i, p) => { const e = M.io(p); o.style.transform = `translateX(${(W() * .35 * e).toFixed(1)}px) scale(${(1 - .15 * e).toFixed(4)})`; o.style.opacity = (1 - e).toFixed(3); i.style.transform = `translateX(${(-W() * (1 - e)).toFixed(1)}px)`; }
  };
  /* window shapes for the three scenes: c(x,y,d) circle · q(x,y,w,h,r) rounded */
  M.c = (x, y, d, s) => ({ x, y, w: d, h: d, r: d / 2, o: 1, s: s || 1.15 });
  M.q = (x, y, w, h, r, s) => ({ x, y, w, h, r: r ?? 28, o: 1, s: s || 1.15 });
  M.story = o => {
    const tr = o.tr || ['zoom', 'push'], keys = [];
    if (!o.noface && o.wins) o.wins.slice(1).forEach((L, k) => keys.push({ t: M.TB[k + 1][0] - .28, d: TRD, L }));
    M.setup({ over: o.over, overCover: o.overCover, bg: o.bg, noface: o.noface, win: o.wins ? o.wins[0] : undefined, keys, ring: o.ring, port: o.port, captions: M.caps(o.caps),
      build(L) { const s = {}; s.cam = M.box(L, 0, 0, { width: '1920px', height: '1080px', transformOrigin: '50% 50%' });
        if (o.back) s.back = o.back(s.cam);
        s.sc = o.scenes.map((sc, i) => { const ex = EX(), ey = EY(), c = M.box(s.cam, -ex, -ey, { width: (1920 + 2 * ex) + 'px', height: (1080 + 2 * ey) + 'px', transformOrigin: `${ex + 960}px ${ey + 540}px`, background: (o.sbg || [])[i] || '' });
          const inner = M.box(c, ex, ey, { width: '1920px', height: '1080px' }); c.s = sc[0](inner); c.u = sc[1]; return c; });
        if (o.front) s.front = o.front(s.cam); return s; },
      update(s, t) { const k = clamp(t / 10);
        s.cam.style.transform = `scale(${(1.0 + .045 * k).toFixed(4)}) translate(${(-14 * k).toFixed(1)}px, ${(-8 * k).toFixed(1)}px)`;   /* camera push */
        if (s.back && o.backU) o.backU(s.back, t);
        s.sc.forEach((c, i) => { const [a, b] = M.TB[i]; c.style.transform = ''; c.style.opacity = ''; c.style.filter = ''; c.style.clipPath = '';
          const start = i ? a - TRD / 2 : 0, end = i < 2 ? b + TRD / 2 : 99; c.style.display = t >= start && t <= end ? '' : 'none';
          if (c.style.display) return; c.u(c.s, t, a);
          if (i === 2 && !o.noface) c.style.opacity = (1 - M.i2((t - 9.05) / .3)).toFixed(3); });
        [0, 1].forEach(j => { const T = M.TB[j + 1][0], p = clamp((t - (T - TRD / 2)) / TRD); if (p > 0 && p < 1) M.TR[tr[j]](s.sc[j], s.sc[j + 1], p); });
        if (s.front && o.frontU) o.frontU(s.front, t); } });
  };
  /* scene decor helpers */
  M.grid = (p, col, sz, w) => M.box(p, -40, -40, { width: '2000px', height: '1160px', backgroundImage: `linear-gradient(${col} ${w || 1}px, transparent ${w || 1}px), linear-gradient(90deg, ${col} ${w || 1}px, transparent ${w || 1}px)`, backgroundSize: `${sz}px ${sz}px` });
  M.dots = (p, col, sz, r) => M.box(p, -40, -40, { width: '2000px', height: '1160px', backgroundImage: `radial-gradient(${col} ${r || 1.6}px, transparent ${(r || 1.6) + .5}px)`, backgroundSize: `${sz}px ${sz}px` });
  M.card = (p, x, y, w, h, bg, sty) => M.box(p, x, y, Object.assign({ width: w + 'px', height: h + 'px', background: bg, borderRadius: '20px', boxShadow: '0 16px 34px rgba(0,0,0,.18)' }, sty || {}));
  M.drift = (e, t, vx, vy) => { if (e) e.style.transform = `translate(${(-vx * t).toFixed(1)}px, ${(-(vy || 0) * t).toFixed(1)}px)`; };
  /* compact text: X(parent, x, y, size, color, text, weight=900, family=CN, extra) */
  M.X = (p, x, y, px, col, txt, w, fam, sty) => M.txt(p, x, y, M.f(w || 900, px, fam || M.CN), col, txt, sty);
  /* common setup for a 10 s concept sample on the Eva raw clip */
  /* 9:16: the graphics scene keeps its 16:9 drawing; the content box (o.port.box) is scaled into the top zone (y≈200–900),
     the presenter window sits below it (circle stays a circle, rounded square keeps its shape), captions below that.
     Opening/closing "full" = a full-width 1080 square (1080p footage, never upscaled). M.bg(e) = full-frame texture → cover;
     M.att(e) = decoration drawn around the 16:9 window → follows the portrait window. */
  M.FULLP = { x: 0, y: 250, w: 1080, h: 1080, r: 0, o: 1, s: 1 };
  M.pwin = L => { const y0 = C.remap.bottom + 40, y1 = 1360, d = Math.max(300, Math.min(520, y1 - y0)), yc = y0 + Math.max(0, (y1 - y0 - d) / 2);
    if (L.r >= Math.min(L.w, L.h) / 2 - 2) return { x: (1080 - d) / 2, y: yc, w: d, h: d, r: d / 2, o: 1, s: L.s };
    const w = Math.min(960, d * L.w / L.h); return { x: (1080 - w) / 2, y: yc, w, h: d, r: L.r * d / L.h, o: 1, s: L.s }; };
  M.bg = e => C.portCover ? C.portCover(e) : e;
  M.att = e => { if (!C.portrait || !C.remap) return e; const A = M._w16, B = M._wp, k = B.h / A.h; let r = e.parentNode;
    while (r && r.parentNode && !r.parentNode.classList.contains('layer')) r = r.parentNode;
    const w = el(null, 'div', '', { position: 'absolute', left: 0, top: 0, width: '1920px', height: '1080px', transformOrigin: '0 0', transform: `translate(${(B.x + B.w / 2 - (A.x + A.w / 2) * k).toFixed(2)}px,${(B.y - A.y * k).toFixed(2)}px) scale(${k.toFixed(5)})` });
    r.parentNode.appendChild(w); w.appendChild(e); return e; };
  M.setup = (o) => { C.src0 = 0; C.end = 10; C.evaDir = '../../sample10/media/eva'; C.src = { w: 1280, h: 720 }; C.face = { x: .52, y: .3, h: .34 };
    C.evaKeys = o.noface ? [{ t: 0, d: 0, L: { x: 0, y: 0, w: 4, h: 4, r: 0, o: 0, s: 1 } }] : M.win(o.win, o.keys, o.end);
    if (C.portrait && o.noface) { const bx = (o.port || {}).box || [90, 60, 1740, 760], sc = Math.min(984 / bx[2], 1000 / bx[3]);   /* centre the logo block between the top safe line and the captions */
      C.portLayout({ box: bx, top: 200 + Math.max(0, (1150 - bx[3] * sc) / 2), maxH: 1000, keep: [1], eva: false }); }
    else if (C.portrait) { const pp = o.port || {}; M._w16 = o.win;
      C.portLayout({ box: pp.box || [90, 60, 1100, 760], top: pp.top ?? 200, maxH: pp.maxH ?? 700, keep: [1], cover: o.over && o.overCover ? [2] : [], eva: L => L.w >= 1900 ? M.FULLP : (pp.win || M.pwin(L)) });
      M._wp = C.evaKeys[1].L; } C.ringFn = o.ring || (() => ({ color: '#fff', width: 0, shadow: .35 }));
    C.scene({ t0: 0, t1: 10.05, bg: o.bg, cls: o.cls || '', quiet: true, build: o.build, update: (lt, s, t) => o.update(s, t) });
    C.scene({ t0: 0, t1: 10.05, z: 70, quiet: true, build: L => M.captions(L, o.captions), update: (lt, f, t) => f(t) });
    if (o.over) C.scene({ t0: 0, t1: 10.05, z: 60, quiet: true, build: o.over[0], update: (lt, v, t) => o.over[1](v, t) });   /* layer above Eva's window (index 2: captions stay index 1) */ };
})();
