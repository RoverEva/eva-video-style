/* Eva Video Style · deterministic motion engine
 *
 * A section page is a pure function of time: the renderer calls window.renderAt(t) for every frame,
 * waits for window.imgWait(), then takes a screenshot. Nothing depends on wall-clock time, so every
 * render of the same section is identical.
 *
 * Page contract (used by scripts/render.mjs):
 *   window.READY    Promise that resolves when fonts + first frame are loaded
 *   window.END      section length in seconds
 *   window.renderAt(t)
 *   window.imgWait()  Promise that resolves when all image-sequence frames for this t are decoded
 *   window.EV.sfx   list of sound cues [kind, t, gain, args] (read by scripts/render.mjs --cues)
 *   window.EV.W/H   stage size in pixels (1920x1080 landscape, 1080x1920 portrait; scripts/render.mjs sizes the viewport from it)
 *
 * Aspect ratio: the stage is 16:9 unless the page URL has ?ar=9:16 (or window.EV_AR = '9:16' is set before this script).
 * Templates read EV.portrait / EV.pick(landscapeValue, portraitValue) and the zones in EV.SAFE / EV.zone(); landscape output is unchanged.
 */
(function () {
  'use strict';
  const FPS = 30;
  /* ---------- Responsive Video Layout: aspect, stage size, source footage ---------- */
  const Q = new URLSearchParams((typeof location !== 'undefined' && location.search) || '');
  const AR = String(Q.get('ar') || window.EV_AR || '16:9').replace('x', ':');
  const PORTRAIT = AR === '9:16';
  const W = PORTRAIT ? 1080 : 1920, H = PORTRAIT ? 1920 : 1080;
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const ease = {
    lin: u => u,
    out3: u => 1 - Math.pow(1 - clamp(u), 3),
    in3: u => Math.pow(clamp(u), 3),
    io3: u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; },
    smooth5: u => { u = clamp(u); return u * u * u * (u * (u * 6 - 15) + 10); },
    outExpo: u => (u = clamp(u)) >= 1 ? 1 : 1 - Math.pow(2, -10 * u),
    outBack: (u, k = 1.9) => { u = clamp(u); return 1 + (k + 1) * Math.pow(u - 1, 3) + k * Math.pow(u - 1, 2); },
    outElastic: u => { u = clamp(u); if (u === 0 || u === 1) return u; return Math.pow(2, -10 * u) * Math.sin((u * 10 - .75) * (2 * Math.PI / 3)) + 1; },
  };
  const P = (t, a, d) => clamp((t - a) / d);
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  function el(parent, tag, cls, style, html) {
    const e = document.createElement(tag || 'div');
    if (cls) e.className = cls;
    if (style) Object.assign(e.style, style);
    if (html !== undefined) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }
  /* transform helper: x,y translate px · s scale · sx/sy · r rotate deg · rx/ry 3D · persp · o opacity */
  function tf(e, o) {
    const parts = [];
    if (o.persp) parts.push(`perspective(${o.persp}px)`);
    if (o.x || o.y) parts.push(`translate(${(o.x || 0).toFixed(2)}px,${(o.y || 0).toFixed(2)}px)`);
    if (o.ry) parts.push(`rotateY(${o.ry}deg)`);
    if (o.rx) parts.push(`rotateX(${o.rx}deg)`);
    if (o.r) parts.push(`rotate(${o.r}deg)`);
    if (o.s !== undefined) parts.push(`scale(${Math.max(0.0001, o.s).toFixed(4)})`);
    if (o.sx !== undefined || o.sy !== undefined) parts.push(`scale(${(o.sx ?? 1).toFixed(4)},${(o.sy ?? 1).toFixed(4)})`);
    e.style.transform = parts.join(' ');
    if (o.o !== undefined) { e.style.opacity = clamp(o.o).toFixed(3); e.style.visibility = o.o <= 0.001 ? 'hidden' : 'visible'; }
  }
  /* pop-in with overshoot -> {s,o} */
  function pop(t, t0, d = .38, k = 1.9) { const u = P(t, t0, d); return { s: u <= 0 ? 0 : ease.outBack(u, k), o: u <= 0 ? 0 : clamp(u * 4) }; }
  /* slide in from an offset -> {x,y,o} */
  function slide(t, t0, d, dx, dy) { const u = ease.outExpo(P(t, t0, d)); return { x: dx * (1 - u), y: dy * (1 - u), o: u <= 0 ? 0 : clamp(u * 3) }; }
  /* clip-path wipe, u 0..1, dir l|r|u|d */
  function wipe(e, u, dir = 'l') {
    u = clamp(u); const r = (1 - u) * 100;
    e.style.clipPath = dir === 'l' ? `inset(0 ${r}% 0 0)` : dir === 'r' ? `inset(0 0 0 ${r}%)` : dir === 'u' ? `inset(${r}% 0 0 0)` : `inset(0 0 ${r}% 0)`;
  }

  /* image sequences (extracted at 30 fps as dir/f_00000.jpg) */
  const pending = new Set();
  function setSrc(img, src) {
    if (img.getAttribute('src') === src) return;
    const pr = new Promise(res => { img.onload = img.onerror = () => res(); });
    pending.add(pr); pr.then(() => pending.delete(pr));
    img.setAttribute('src', src);
  }
  const pad = (n, w = 5) => String(Math.max(0, n)).padStart(w, '0');
  function seq(dir, seconds, count) {
    let i = Math.round(seconds * FPS);
    if (count) i = Math.min(count - 1, Math.max(0, i));
    return `${dir}/f_${pad(i)}.jpg`;
  }

  /* Eva window path: keys [{t, d, L:{x,y,w,h,r,s,o}}]. Each key starts at t and eases (quintic) to L over d seconds,
   * starting from wherever the window is at that moment, so overlapping moves blend without jumps. */
  const GEO = ['x', 'y', 'w', 'h', 'r', 's', 'o'];
  function norm(L) { return Object.assign({ x: 0, y: 0, w: W, h: H, r: 0, s: 1, o: 1 }, L); }
  function compilePath(keys) {
    const ks = keys.map(k => ({ t: k.t, d: k.d || 0, L: norm(k.L), e: k.ease || 'smooth5' })).sort((a, b) => a.t - b.t);
    const at = (t, upto) => {
      let i = -1; for (let j = 0; j < upto; j++) if (ks[j].t <= t) i = j;
      if (i < 0) return ks[0].L;
      const k = ks[i]; if (!k.from) k.from = i === 0 ? k.L : at(k.t, i);
      const u = k.d > 0 ? ease[k.e]((t - k.t) / k.d) : 1;
      const g = {}; for (const n of GEO) g[n] = lerp(k.from[n], k.L[n], u); return g;
    };
    return { at: t => at(t, ks.length) };
  }

  const S = {
    FPS, clamp, lerp, ease, P, rng, el, tf, pop, slide, wipe, setSrc, seq,
    W, H, AR, portrait: PORTRAIT, params: Q,
    scenes: [], end: 10, src0: 0, evaDir: '../media/eva',
    /* size of the presenter footage frames (any orientation: a 9:16 phone clip is { w: 1080, h: 1920 }) */
    src: { w: 1920, h: 1080 },
    /* face calibration of the talking-head footage, as fractions of the source frame:
       x = face centre, y = head centre, h = head height (hair to chin). Re-measure for every new shoot. */
    face: { x: .54, y: .35, h: .5 }, headFill: .6,
    evaKeys: [{ t: 0, L: {} }], ringFn: null, sfx: [],
    scene(def) { this.scenes.push(def); return def; },
  };

  function evaInit(stage) {
    S.evaBox = el(stage, 'div'); S.evaBox.id = 'eva';
    S.evaImg = el(S.evaBox, 'img'); S.evaImg.alt = '';
    S.evaPath = compilePath(S.evaKeys);
    /* HUD corner brackets (used when ringFn returns {hud: color}) */
    S.evaHud = el(stage, 'div', '', { position: 'absolute', zIndex: 51, pointerEvents: 'none' });
    ['tl', 'tr', 'bl', 'br'].forEach(c => el(S.evaHud, 'div', 'hudc ' + c));
  }
  function evaRender(t) {
    const g = S.evaPath.at(t);
    const w = g.w, h = g.h, zoom = Math.max(1, g.s || 1), box = S.evaBox;
    const rad = Math.min(g.r, Math.min(w, h) / 2), vis = g.o > 0.01;
    box.style.visibility = vis ? 'visible' : 'hidden';
    Object.assign(box.style, { left: g.x.toFixed(2) + 'px', top: g.y.toFixed(2) + 'px', width: w.toFixed(2) + 'px', height: h.toFixed(2) + 'px', borderRadius: rad.toFixed(2) + 'px', opacity: clamp(g.o).toFixed(3) });
    /* Never crop Eva's head: cap the zoom so the whole head fills at most headFill of the window
       (a little less for circles), and centre the window on her face. */
    const SW = S.src.w, SH = S.src.h, FULL = w >= W - 20 && h >= H - 20;
    const cover0 = Math.max(w / SW, h / SH);
    const roundness = clamp(rad / (Math.min(w, h) / 2));
    const fill = S.headFill - .08 * roundness;
    const cap = Math.max(1, fill * h / (S.face.h * SH * cover0));
    const z = Math.min(zoom, cap), cover = cover0 * z, iw = SW * cover, ih = SH * cover;
    const ty = lerp(.44, .52, roundness);
    const left = clamp(w / 2 - S.face.x * iw, w - iw, 0), top = clamp(h * ty - S.face.y * ih, h - ih, 0);
    Object.assign(S.evaImg.style, { width: iw.toFixed(2) + 'px', height: ih.toFixed(2) + 'px', left: left.toFixed(2) + 'px', top: top.toFixed(2) + 'px' });
    if (vis) setSrc(S.evaImg, seq(S.evaDir, S.src0 + t));
    const ring = S.ringFn ? S.ringFn(t) : { color: '#fff', width: 0, shadow: 0 };
    const hb = S.evaHud; hb.style.display = ring.hud && vis && !FULL ? 'block' : 'none';
    if (ring.hud) { const m = 12; Object.assign(hb.style, { left: (g.x - m) + 'px', top: (g.y - m) + 'px', width: (w + 2 * m) + 'px', height: (h + 2 * m) + 'px', color: ring.hud, opacity: clamp(g.o) }); }
    box.style.filter = ring.filter || '';
    box.style.boxShadow = FULL ? 'none' : `0 0 0 ${ring.width}px ${ring.color}, 0 28px 70px rgba(0,0,0,${ring.shadow ?? .45})` + (ring.glow ? `, 0 0 60px ${ring.glow}` : '');
  }

  const LW = 1920, LH = 1080;
  const asLand = f => { S.W = LW; S.H = LH; try { return f(); } finally { S.W = W; S.H = H; } };
  /* Zone remap for 9:16, for templates whose 16:9 scenes are a content block beside the presenter.
   *   EV.portLayout({ box: [x, y, w, h], top, maxH, cover: [sceneIndex...], keep: [sceneIndex...], eva, coverX })
   * box     the 16:9 rectangle that holds the scene content (titles, cards, lists), in 1920x1080 pixels
   * top     where the box starts in 9:16 (default SAFE.top + 20); it is scaled to the safe width (max maxH tall)
   * cover   scenes that are full-frame footage / backgrounds: scaled to fill the 9:16 frame instead (coverX = focus 0..1)
   * keep    scenes already written for 9:16 (pick/zone): left untouched
   * eva     true (default): the presenter window path is re-laid below the content block: full stays full, circles become a
   *         circle and cards a card in the presenter zone. Pass a function (L, i, key) => L to place keys yourself.
   * In 16:9 this does nothing. Elements still keep their 16:9 design; nothing is cropped. */
  const fitOf = (box, top, maxH, pad) => { const [x, y, w, h] = box, s = Math.min((W - 2 * pad) / w, maxH / h); return { s, dx: (W - w * s) / 2 - x * s, dy: top - y * s }; };
  S.portLayout = cfg => { if (!PORTRAIT) return; const [x, y, w, h] = cfg.box, top = cfg.top ?? S.SAFE.top + 20, maxH = cfg.maxH ?? 820;
    const s = Math.min((W - 2 * (cfg.pad ?? 48)) / w, maxH / h), cs = Math.max(W / LW, H / LH), cx = cfg.coverX ?? .5;
    /* per-scene boxes: at: { sceneIndex: { box, top, maxH } } (e.g. text over a full-bleed presenter goes in the lower zone) */
    const per = {}; for (const i in cfg.at || {}) { const a = cfg.at[i]; per[i] = fitOf(a.box || cfg.box, a.top ?? top, a.maxH ?? maxH, a.pad ?? cfg.pad ?? 48); }
    S.remap = { per, cover: cfg.cover || [], keep: cfg.keep || [], fitXf: { s, dx: (W - w * s) / 2 - x * s, dy: top - y * s },
      coverXf: { s: cs, dx: Math.min(0, Math.max(W - LW * cs, W / 2 - cx * LW * cs)), dy: (H - LH * cs) / 2 }, bottom: top + h * s };
    if (cfg.eva === false) return;
    const y0 = S.remap.bottom + 36, y1 = H - S.SAFE.bottom + 20, zh = Math.max(240, y1 - y0);
    const place = typeof cfg.eva === 'function' ? cfg.eva : (L0, i, k) => { const L = Object.assign({ x: 0, y: 0, w: LW, h: LH, r: 0, s: 1, o: 1 }, L0);
      if (L.w >= LW - 20 && L.h >= LH - 20) return Object.assign({}, S.POSES.full, { o: L.o });
      if (L.r >= Math.min(L.w, L.h) / 2 - 2) { const d = Math.min(cfg.circle ?? 480, Math.max(240, zh)); return { x: (W - d) / 2, y: y0 + Math.max(0, (zh - d) / 2), w: d, h: d, r: d / 2, s: L.s, o: L.o }; }
      const ch = Math.max(300, zh), cw = Math.min(W - 2 * 110, ch * .82); return { x: (W - cw) / 2, y: y0, w: cw, h: ch, r: Math.min(L.r, 40), s: L.s, o: L.o }; };
    const fx = S.remap.fitXf, inbox = L0 => { const L = Object.assign({ x: 0, y: 0, w: LW, h: LH, r: 0, s: 1, o: 1 }, L0); return Object.assign({}, L, { x: L.x * fx.s + fx.dx, y: L.y * fx.s + fx.dy, w: L.w * fx.s, h: L.h * fx.s, r: L.r * fx.s }); };
    S.evaKeys = S.evaKeys.map((k, i) => Object.assign({}, k, { L: (cfg.inbox || []).includes(i) ? inbox(k.L) : place(k.L, i, k) })); };
  /* portFull(el): in a remapped 9:16 scene, move a full-frame element (footage, sky, grade) out of the content box so it fills
     the whole 9:16 frame; heights scale with the frame. No-op in 16:9. */
  /* portCover(el): like portFull, but keeps the element's 16:9 drawing (canvas, rays, floor) and scales it to cover the 9:16
     frame instead of stretching it. Use for full-frame backgrounds built inside a remapped scene. No-op in 16:9. */
  S.portCover = (e, fx) => { if (!PORTRAIT || !S.remap) return e; let r = e.parentNode; while (r && r.parentNode && !r.parentNode.classList.contains('layer')) r = r.parentNode;
    if (!r || !r.parentNode) return e; const c = S.remap.coverXf, dx = fx == null ? c.dx : Math.min(0, Math.max(W - LW * c.s, W / 2 - fx * LW * c.s));
    const w = el(null, 'div', '', { position: 'absolute', left: 0, top: 0, width: LW + 'px', height: LH + 'px', transformOrigin: '0 0', transform: `translate(${dx.toFixed(2)}px,${c.dy.toFixed(2)}px) scale(${c.s.toFixed(5)})`, zIndex: getComputedStyle(e).zIndex === 'auto' ? '' : e.style.zIndex });
    r.parentNode.insertBefore(w, r); w.appendChild(e); return e; };
  S.portFull = e => { if (!PORTRAIT || !S.remap) return e; let r = e.parentNode; while (r && r.parentNode && !r.parentNode.classList.contains('layer')) r = r.parentNode;
    if (!r || !r.parentNode) return e; r.parentNode.insertBefore(e, r); const h = parseFloat(e.style.height) || LH, tp = parseFloat(e.style.top) || 0;
    Object.assign(e.style, { left: '0px', width: W + 'px', top: (tp / LH * H) + 'px', height: (h / LH * H) + 'px' }); return e; };
  S.start = function () {
    const stage = document.getElementById('stage');
    /* per-render overrides (renderer / SaaS worker pass them in the URL): eva=frames dir, srcw/srch=footage size, face=x,y,h */
    if (Q.get('eva')) S.evaDir = Q.get('eva');
    if (Q.get('srcw')) S.src = { w: +Q.get('srcw'), h: +(Q.get('srch') || S.src.h) };
    if (Q.get('face')) { const [x, y, h] = Q.get('face').split(',').map(Number); S.face = { x, y, h }; }
    if (PORTRAIT) { document.documentElement.classList.add('ar-portrait');
      for (const e of [document.documentElement, document.body, stage]) Object.assign(e.style, { width: W + 'px', height: H + 'px' }); }
    S.scenes.forEach((sc, i) => {
      sc.layer = el(stage, 'div', 'layer', { zIndex: sc.z || 1 });
      if (sc.bg) sc.layer.style.background = sc.bg;
      if (sc.cls) sc.layer.className += ' ' + sc.cls;
      /* 9:16 zone remap (see S.portLayout): the scene is built in its original 1920x1080 coordinates inside a box that is
         scaled into the portrait content zone ('fit') or scaled to fill the frame ('cover', for full-frame footage layers) */
      const R = PORTRAIT && S.remap ? (S.remap.cover.includes(i) ? S.remap.coverXf : S.remap.keep.includes(i) ? null : S.remap.per[i] || S.remap.fitXf) : null;
      let root = sc.layer;
      if (R) { sc.land = true; root = el(sc.layer, 'div', '', { position: 'absolute', left: 0, top: 0, width: LW + 'px', height: LH + 'px', transformOrigin: '0 0', transform: `translate(${R.dx.toFixed(2)}px,${R.dy.toFixed(2)}px) scale(${R.s.toFixed(5)})` }); }
      sc.root = root;
      sc.st = sc.build ? (sc.land ? asLand(() => sc.build(root)) : sc.build(root)) || {} : {};
    });
    /* old automatic whoosh on every scene change: templates carry no sound now, so only with C.templateSfx (see kit.js K.cue) */
    if (S.templateSfx) for (const sc of S.scenes) if (sc.t0 > .05 && !sc.quiet) S.sfx.push(['whoosh', +(sc.t0 - .05).toFixed(3), .14, {}]);
    evaInit(stage);
    if (Q.get('guides')) S.guides(stage);
    window.END = S.end;
    window.renderAt = function (t) {
      for (const sc of S.scenes) {
        const on = t >= sc.t0 && t < sc.t1;
        sc.layer.style.display = on ? 'block' : 'none';
        if (on && sc.update) { if (sc.land) asLand(() => sc.update(t - sc.t0, sc.st, t)); else sc.update(t - sc.t0, sc.st, t); }
      }
      evaRender(t);
    };
    window.imgWait = () => Promise.all([...pending]);
    window.READY = document.fonts.ready.then(() => { S.fits.forEach(f => f()); window.renderAt(0); return window.imgWait(); });
  };
  /* ---------- Responsive layout helpers ----------
   * pick(land, port)       landscape value or portrait value (land is returned unchanged in 16:9, so 16:9 output never moves)
   * SAFE                   margins that stay clear of phone UI: 9:16 = TikTok / Reels / Shorts overlays (top bar, caption + buttons
   *                        at the bottom, action rail on the right); 16:9 = broadcast title-safe
   * zone(name)             named rectangles {x,y,w,h} inside the safe area (see ZONES below)
   * pose(name, extra)      named Eva-window rectangles for evaKeys, per aspect
   * fit(el, maxW, minPx)   shrink an element's font so its text fits maxW (measured once after fonts load: deterministic)
   * faceRect(g)            where the presenter's face is on stage for an Eva window rectangle g (to keep text off it) */
  S.pick = (land, port) => PORTRAIT ? (port === undefined ? land : port) : land;
  S.SAFE = PORTRAIT ? { top: 210, bottom: 430, left: 64, right: 150 } : { top: 60, bottom: 110, left: 96, right: 96 };
  const SF = S.SAFE, IW = W - SF.left - SF.right;
  S.ZONES = PORTRAIT ? {
    safe: { x: SF.left, y: SF.top, w: IW, h: H - SF.top - SF.bottom },
    head: { x: SF.left, y: SF.top, w: IW, h: 470 },               // headline block, above the presenter
    body: { x: SF.left, y: SF.top + 500, w: IW, h: 560 },         // cards / lists between the headline and the presenter
    lower: { x: SF.left, y: 1060, w: IW, h: H - SF.bottom - 1060 },// lower third (over full-bleed presenter, below the face)
    caption: { x: 90, y: H - SF.bottom - 190, w: W - 240, h: 190 },// burned subtitles: above the platform caption + buttons
  } : {
    safe: { x: SF.left, y: SF.top, w: W - SF.left - SF.right, h: H - SF.top - SF.bottom },
    head: { x: SF.left, y: SF.top, w: 1040, h: 330 },
    body: { x: SF.left, y: 420, w: 1040, h: 520 },
    lower: { x: SF.left, y: 780, w: 1200, h: 190 },
    caption: { x: 380, y: 900, w: 1160, h: 150 },
  };
  S.zone = name => Object.assign({}, S.ZONES[name] || S.ZONES.safe);
  /* presenter poses. 9:16: 'card' = framed card in the lower half, 'split' = bottom 45% edge to edge, 'pip' = small circle bottom-left
     above the UI zone, 'pipTop' = small circle top-right, 'full' = full-bleed. 16:9 keeps the classic right-hand card. */
  S.POSES = PORTRAIT ? {
    full: { x: 0, y: 0, w: W, h: H, r: 0, s: 1 },
    card: { x: 150, y: 960, w: 780, h: 900, r: 44, s: 1.4 },
    split: { x: 0, y: 1040, w: W, h: H - 1040, r: 0, s: 1.25 },
    pip: { x: 70, y: 1180, w: 300, h: 300, r: 150, s: 3 },
    pipTop: { x: 760, y: 70, w: 240, h: 240, r: 120, s: 3 },
  } : {
    full: { x: 0, y: 0, w: W, h: H, r: 0, s: 1 },
    card: { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 },
    split: { x: 960, y: 0, w: 960, h: H, r: 0, s: 1.2 },
    pip: { x: 1580, y: 690, w: 260, h: 260, r: 130, s: 3 },
    pipTop: { x: 1600, y: 60, w: 240, h: 240, r: 120, s: 3 },
  };
  S.pose = (name, extra) => Object.assign({}, S.POSES[name] || S.POSES.card, extra || {});
  S.fits = [];
  S.fit = (e, maxW, minPx) => { S.fits.push(() => { let fs = parseFloat(getComputedStyle(e).fontSize); const lo = minPx || fs * .4;
      for (let i = 0; i < 40 && e.scrollWidth > maxW && fs > lo; i++) { fs = Math.max(lo, fs * Math.min(.97, maxW / e.scrollWidth)); e.style.fontSize = fs.toFixed(1) + 'px'; } }); return e; };
  S.faceRect = g => { const SW = S.src.w, SH = S.src.h, c = Math.max(g.w / SW, g.h / SH) * Math.max(1, g.s || 1), fh = S.face.h * SH * c;
    return { x: g.x + g.w / 2 - fh * .45, y: g.y + g.h * .48 - fh / 2, w: fh * .9, h: fh }; };
  /* ?guides=1 draws the safe area and the phone-UI zones on top (layout checks only, never in a final render) */
  S.guides = stage => { const g = el(stage, 'div', '', { position: 'absolute', inset: 0, zIndex: 999, pointerEvents: 'none' }), sf = S.SAFE;
    el(g, 'div', '', { position: 'absolute', left: sf.left + 'px', top: sf.top + 'px', width: (W - sf.left - sf.right) + 'px', height: (H - sf.top - sf.bottom) + 'px', outline: '3px dashed rgba(0,255,140,.85)' });
    const ui = PORTRAIT ? [[0, 0, W, sf.top, 'TOP BAR'], [0, H - sf.bottom, W, sf.bottom, 'CAPTION + UI'], [W - sf.right, 860, sf.right, H - sf.bottom - 860, 'ACTIONS']] : [];
    ui.forEach(([x, y, w, h, n]) => el(g, 'div', '', { position: 'absolute', left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: 'rgba(255,40,80,.18)', color: 'rgba(255,255,255,.8)', font: '700 22px Inter, sans-serif', padding: '8px', boxSizing: 'border-box' }, n));
    const c = S.ZONES.caption; el(g, 'div', '', { position: 'absolute', left: c.x + 'px', top: c.y + 'px', width: c.w + 'px', height: c.h + 'px', outline: '2px dashed rgba(255,210,0,.9)' }); };
  window.EV = S;
})();
