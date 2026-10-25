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
 */
(function () {
  'use strict';
  const FPS = 30;
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
  function norm(L) { return Object.assign({ x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1, o: 1 }, L); }
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
    scenes: [], end: 10, src0: 0, evaDir: '../media/eva',
    /* face calibration of the talking-head footage, as fractions of the 1920x1080 frame:
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
    const cover0 = Math.max(w / 1920, h / 1080);
    const roundness = clamp(rad / (Math.min(w, h) / 2));
    const fill = S.headFill - .08 * roundness;
    const cap = Math.max(1, fill * h / (S.face.h * 1080 * cover0));
    const z = Math.min(zoom, cap), cover = cover0 * z, iw = 1920 * cover, ih = 1080 * cover;
    const ty = lerp(.44, .52, roundness);
    const left = clamp(w / 2 - S.face.x * iw, w - iw, 0), top = clamp(h * ty - S.face.y * ih, h - ih, 0);
    Object.assign(S.evaImg.style, { width: iw.toFixed(2) + 'px', height: ih.toFixed(2) + 'px', left: left.toFixed(2) + 'px', top: top.toFixed(2) + 'px' });
    if (vis) setSrc(S.evaImg, seq(S.evaDir, S.src0 + t));
    const ring = S.ringFn ? S.ringFn(t) : { color: '#fff', width: 0, shadow: 0 };
    const hb = S.evaHud; hb.style.display = ring.hud && vis && w < 1900 ? 'block' : 'none';
    if (ring.hud) { const m = 12; Object.assign(hb.style, { left: (g.x - m) + 'px', top: (g.y - m) + 'px', width: (w + 2 * m) + 'px', height: (h + 2 * m) + 'px', color: ring.hud, opacity: clamp(g.o) }); }
    box.style.filter = ring.filter || '';
    box.style.boxShadow = w >= 1900 ? 'none' : `0 0 0 ${ring.width}px ${ring.color}, 0 28px 70px rgba(0,0,0,${ring.shadow ?? .45})` + (ring.glow ? `, 0 0 60px ${ring.glow}` : '');
  }

  S.start = function () {
    const stage = document.getElementById('stage');
    for (const sc of S.scenes) {
      sc.layer = el(stage, 'div', 'layer', { zIndex: sc.z || 1 });
      if (sc.bg) sc.layer.style.background = sc.bg;
      if (sc.cls) sc.layer.className += ' ' + sc.cls;
      sc.st = sc.build ? sc.build(sc.layer) || {} : {};
    }
    /* automatic whoosh on every scene change unless the scene is quiet */
    for (const sc of S.scenes) if (sc.t0 > .05 && !sc.quiet) S.sfx.push(['whoosh', +(sc.t0 - .05).toFixed(3), .14, {}]);
    evaInit(stage);
    window.END = S.end;
    window.renderAt = function (t) {
      for (const sc of S.scenes) {
        const on = t >= sc.t0 && t < sc.t1;
        sc.layer.style.display = on ? 'block' : 'none';
        if (on && sc.update) sc.update(t - sc.t0, sc.st, t);
      }
      evaRender(t);
    };
    window.imgWait = () => Promise.all([...pending]);
    window.READY = document.fonts.ready.then(() => { window.renderAt(0); return window.imgWait(); });
  };
  window.EV = S;
})();
