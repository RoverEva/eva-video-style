/* EVA Card System · one shared, theme-aware card layer that any template can call. Load after templates.js (icons come from
 * K.T.cpIcon). Opt-in and additive: nothing changes in a section until it calls K.EC. See references/cards.md.
 *
 *   const th = K.EC.theme('t17');                       // premium | t17 | t20 | t01 | t09 (+ overrides)
 *   const o  = K.EC.layout(L, 'steps-v', data, box, th); // in build()   (9 layouts, see EC.LAYOUTS)
 *   o.at(t, times);                                     // in update()  (times = one landing time per item, e.g. from EV.asr)
 *   const cs = K.EC.fromSchema(L, cards, th); K.EC.schemaAt(cs, t);   // JSON card specs (references/cards.md) */
(function () {
  const C = window.EV, K = window.K, T = K.T, { el, tf, P, ease, clamp } = C;
  const EC = K.EC = {};

  /* ---------- themes: the card surface stays white / warm white everywhere; templates change accent, type, shadow tint and motion ---------- */
  const SANS = "'Inter', 'Noto Sans CJK SC', sans-serif", COND = "'Anton', 'Archivo Black', 'Noto Sans CJK SC', sans-serif";
  const BASE = { surf: ['#fffdf9', '#f1e9de'], ink: '#2e2823', mute: '#7a6d62', acc: '#2e2823', head: SANS, headW: 900, upper: false, cardHead: SANS,
    type: '#fff', typeMode: '3d', tint: [244, 236, 228], numMode: '3d', sh: [86, 60, 40], shA: 1, rim: 'rgba(255,255,255,.95)', hard: null, glow: null, border: 'none',
    r: 24, line: 'rgba(255,255,255,.85)', iconSw: 2.4, motion: 'float', dur: .75, bob: 4, heroRot: -6, script: "'Playfair Display', 'Noto Serif CJK SC', serif" };
  EC.THEMES = {
    premium: {},
    t17: { surf: ['#ffffff', '#e8f0f7'], ink: '#0b1630', mute: '#52617a', acc: '#0aa9c4', typeMode: 'glow', numMode: 'glow', glow: '24,224,242', sh: [0, 6, 20], shA: 1.7,
      line: 'rgba(24,224,242,.9)', motion: 'float', heroRot: 0, r: 20 },
    t20: { surf: ['#ffffff', '#f2eeff'], ink: '#111015', mute: '#5d5873', acc: '#7b5cff', hi: '#7b5cff', kick: '#7b5cff', type: '#111015', head: COND, headW: 400, upper: true, cardHead: COND,
      typeMode: 'pop', popC: '#d6ff3a', numMode: 'chip', chip: ['#7b5cff', '#fff'], sh: [60, 30, 140], shA: 1.2, line: '#111015', motion: 'pop', dur: .45, heroRot: -4, r: 28 },
    t01: { surf: ['#ffffff', '#f6f6f1'], ink: '#0b0b0d', mute: '#55554f', acc: '#2a2cf2', kick: '#0b0b0d', head: COND, headW: 400, upper: true, cardHead: COND,
      typeMode: 'block', numMode: 'chip', chip: ['#0b0b0d', '#d4ff2e'], sh: [11, 11, 13], shA: .9, hard: 'rgba(11,11,13,.92)', line: '#0b0b0d', motion: 'fade-slide', dur: .45, bob: 0, heroRot: 0, r: 22 },
    t09: { surf: ['#fbf8f2', '#e9e1d3'], ink: '#16140f', mute: '#6f6656', acc: '#a8842f', typeMode: 'metal', tint: [236, 220, 182], numMode: 'gold', sh: [0, 0, 0], shA: 2.2,
      border: '1px solid rgba(201,163,84,.6)', line: 'rgba(232,201,120,.85)', motion: 'tilt', dur: .7, bob: 2, heroRot: 0, r: 18 },
  };
  EC.theme = (name, over) => Object.assign({}, BASE, EC.THEMES[name] || {}, over || {}, { name: name || 'premium' });
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${Math.min(.92, a)})`;

  EC.cardShadow = th => { const a = th.shA, s = th.sh; return [`inset 0 2px 0 ${th.rim}`, `inset 0 -5px 0 ${rgba(s, .05)}`, th.hard && `0 9px 0 ${th.hard}`,
    `0 3px 8px ${rgba(s, .1 * a)}`, `0 14px 26px ${rgba(s, .15 * a)}`, `0 34px 64px ${rgba(s, .2 * a)}`, th.glow && `0 0 0 1px rgba(${th.glow},.4), 0 0 46px rgba(${th.glow},.28)`].filter(Boolean).join(', '); };
  /* headline type: '3d' stacked warm layers (reference look) · glow · pop · block · metal */
  EC.typeFx = (th, size) => { const s = th.sh, n = Math.max(3, Math.round(size / 26)), stack = tint => { const a = []; for (let i = 1; i <= n; i++) { const k = i * (34 / n); a.push(`${i * .9}px ${i * 1.1}px 0 rgb(${tint.map(v => Math.round(v - k)).join(',')})`); } return a; };
    switch (th.typeMode) {
      case 'glow': return [...stack([200, 220, 240]), `0 0 ${size * .25}px rgba(${th.glow},.55)`, `0 ${n * 3}px 30px rgba(0,0,0,.55)`].join(', ');
      case 'pop': return `0 ${size * .06}px 0 ${th.popC || th.acc}, 0 ${size * .06 + 14}px 30px ${rgba(s, .35)}`;
      case 'block': return `${size * .045}px ${size * .045}px 0 ${th.ink}`;
      case 'metal': return [...stack(th.tint), `0 ${n * 2 + 8}px 26px rgba(0,0,0,.6)`].join(', ');
      default: return [...stack(th.tint), `${n}px ${n * 2 + 6}px 18px ${rgba(s, .32)}`, `4px ${n * 4 + 18}px 46px ${rgba(s, .22)}`].join(', ');
    } };

  /* ---------- primitives ---------- */
  EC.group = (p, x, y, w, h, z, origin) => el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', zIndex: z || 14, transformOrigin: origin || '50% 50%' });
  EC.surface = (p, x, y, w, h, th, r) => el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', borderRadius: (r ?? th.r) + 'px',
    background: `linear-gradient(160deg, ${th.surf[0]} 30%, ${th.surf[1]})`, boxShadow: EC.cardShadow(th), border: th.border });
  EC.word = (p, txt, x, y, size, th, o) => { o = o || {}; const script = o.script, cond = !script && th.head === COND;
    return el(p, 'div', 'abs', Object.assign({ left: x + 'px', top: y + 'px', fontFamily: script ? th.script : th.head, fontWeight: script ? 400 : (o.w || th.headW), fontStyle: script || o.italic ? 'italic' : 'normal',
      fontSize: size + 'px', lineHeight: o.lh || (cond ? .9 : .95), letterSpacing: script || cond ? '0' : '-.02em', textTransform: th.upper && !script ? 'uppercase' : 'none', color: o.color || th.type,
      textShadow: EC.typeFx(th, size * (o.depth || 1)), whiteSpace: 'nowrap', transform: `rotate(${o.rot || 0}deg)`, transformOrigin: o.origin || '0 50%', zIndex: 20 }, o.css || {}), txt); };
  EC.icon = (p, name, size, x, y, th, col) => T.cpIcon(p, name, size, col || th.ink, x, y, th.iconSw);
  EC.num = (p, n, x, y, size, th) => { const s = String(n);
    if (th.numMode === 'chip') { const c = el(p, 'div', 'abs', { left: x + 'px', top: (y + size * .1) + 'px', width: size * .8 + 'px', height: size * .8 + 'px', borderRadius: size * .2 + 'px', background: th.chip[0],
        color: th.chip[1], fontFamily: th.head, fontWeight: th.headW, fontSize: size * .52 + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 ${th.hard ? 6 : 10}px ${th.hard ? 0 : 20}px ${th.hard || rgba(th.sh, .3)}` }, s); return c; }
    if (th.numMode === 'gold') return el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: th.head, fontWeight: 900, fontSize: size + 'px', lineHeight: 1,
      background: 'linear-gradient(180deg, #fff3cf, #d9b45a 55%, #a07a2a)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.55))' }, s);
    return EC.word(p, s, x, y, size, th, { lh: 1 }); };
  const txt = (p, s, x, y, size, col, font, w, extra) => el(p, 'div', 'abs', Object.assign({ left: x + 'px', top: y + 'px', fontFamily: font, fontWeight: w, fontSize: size + 'px', lineHeight: 1.1, color: col, whiteSpace: 'nowrap' }, extra || {}), s);
  const title = (p, s, x, y, size, th, extra) => txt(p, s, x, y, size, th.ink, th.cardHead, th.cardHead === COND ? 400 : 800, Object.assign({ textTransform: th.upper ? 'uppercase' : 'uppercase', letterSpacing: th.cardHead === COND ? '.01em' : '.02em' }, extra));

  /* ---------- motion presets (applied to a component's root group). bob = gentle float once landed ---------- */
  EC.MOTIONS = ['fade-slide', 'pop', 'float', 'stack', 'tilt', 'rearrange'];
  EC.move = (e, t, t0, th, o) => { o = o || {}; const pre = o.preset || th.motion, d = o.d || th.dur, u = P(t, t0, d), k = o.k || 0, land = u >= 1 ? 1 : 0, bob = (th.bob * Math.sin(t * 1.3 + k * 1.7)) * land, r = o.r || 0;
    let m; switch (pre) {
      case 'fade-slide': { const e3 = ease.outExpo(u); m = { x: (o.dx ?? 90) * (1 - e3), y: (o.dy || 0) * (1 - e3) + bob, o: clamp(u * 3), r }; break; }
      case 'pop': { m = { s: u <= 0 ? .4 : .4 + .6 * ease.outBack(u, 2.1), y: bob, o: clamp(u * 4), r }; break; }
      case 'stack': { const e3 = ease.out3(u); m = { y: 150 * (1 - e3) + bob, s: .9 + .1 * e3, r: r - 5 * (1 - e3), o: clamp(u * 2.5) }; break; }
      case 'tilt': { const e3 = ease.out3(u); m = { persp: 1400, rx: 78 * (1 - e3), y: 30 * (1 - e3) + bob, o: clamp(u * 2.2), r }; break; }
      case 'rearrange': { const e3 = ease.io3(u); m = { x: (o.dx || 0) * (1 - e3), y: (o.dy || 0) * (1 - e3) + bob, r: r + (o.dr || 0) * (1 - e3), s: .8 + .2 * e3, o: clamp(u * 3) }; break; }
      default: { const e3 = ease.out3(u); m = { s: 1.14 - .14 * e3, y: 22 * (1 - e3) + bob, o: clamp(u * 2.2), r }; e.style.filter = u < 1 ? `blur(${(1 - e3) * 9}px)` : 'none'; }
    }
    tf(e, m); };

  /* ---------- connectors: arrow drawing / curved path reveal ---------- */
  EC.connector = (L, d, th, w, head, z) => { const s = K.svg(L, 1920, 1080, 0, 0); s.style.zIndex = z || 12; s.style.overflow = 'visible';
    const p = K.sv(s, 'path', { d, fill: 'none', stroke: th.line, 'stroke-width': w || 5, 'stroke-linecap': 'round' }); const l = p.getTotalLength ? p.getTotalLength() : 1000;
    p.setAttribute('stroke-dasharray', l); p.setAttribute('stroke-dashoffset', l); const o = { s, p, l };
    if (head !== false && p.getPointAtLength) { const a = p.getPointAtLength(l), b = p.getPointAtLength(Math.max(0, l - 24)), ang = Math.atan2(a.y - b.y, a.x - b.x), q = 22 + (w || 5) * 2;
      const hp = (da) => `${a.x - q * Math.cos(ang + da)} ${a.y - q * Math.sin(ang + da)}`;
      o.h = K.sv(s, 'path', { d: `M${hp(.5)} L${a.x} ${a.y} L${hp(-.5)}`, fill: 'none', stroke: th.line, 'stroke-width': w || 5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: 0 }); }
    if (th.glow) s.style.filter = `drop-shadow(0 0 8px rgba(${th.glow},.7))`; else if (th.line !== th.ink) s.style.filter = `drop-shadow(0 6px 10px ${rgba(th.sh, .25)})`;
    o.at = u => { p.setAttribute('stroke-dashoffset', l * (1 - ease.io3(clamp(u)))); if (o.h) o.h.setAttribute('opacity', u > .96 ? 1 : 0); }; return o; };

  /* ---------- the five components. Each returns { g (root), at(t, t0) } ---------- */
  /* HeroCard: big 3D headline words + optional kicker / subtitle / script word */
  EC.HeroCard = (L, c, x, y, size, th, o) => { o = o || {}; const g = EC.group(L, x, y, 10, 10, 20, '0 50%'), rot = o.rot ?? th.heroRot, ws = []; let yy = 0;
    if (c.kicker) { ws.push(txt(g, c.kicker, 4, -size * .38, size * .16, th.kick || th.type, SANS, 700, { letterSpacing: '.3em', textTransform: 'uppercase', opacity: .85, textShadow: th.kick ? 'none' : `0 2px 10px ${rgba(th.sh, .4)}` })); }
    if (c.script) { ws.push(EC.word(g, c.script, 0, -size * .5, size * .5, th, { script: true, rot: rot - 2, depth: .6 })); }
    (c.words || []).forEach((w, i) => { ws.push(EC.word(g, w, i * size * .12, yy, size, th, { rot })); yy += size * .98; });
    if (c.sub) ws.push(EC.word(g, c.sub, size * .5, yy + size * .05, size * .32, th, { rot: rot - 2, italic: th.head !== COND, depth: .7, color: th.hi || th.type }));
    return { g, ws, at(t, t0, step) { ws.forEach((w, i) => EC.move(w, t, t0 + i * (step ?? .18), th, { preset: th.motion === 'tilt' || th.motion === 'stack' ? 'float' : th.motion, r: 0, k: i, d: th.dur + .05 })); } }; };

  /* StepCard: numbered step. dir 'h' = number + wide card (icon · title · description); 'v' = number above a square tile */
  EC.StepCard = (L, c, x, y, w, h, th, o) => { o = o || {}; const dir = o.dir || 'h';
    if (dir === 'v') { const g = EC.group(L, x, y - w * .62, w, w * 1.62, 14, '50% 100%'); EC.num(g, c.n, w * .3, 0, w * .5, th);
      const s = EC.surface(g, 0, w * .62, w, w, th); EC.icon(s, c.icon, w * .42, w * .29, w * .14, th); title(s, c.title, 0, w * .66, w * .13, th, { width: w + 'px', textAlign: 'center' });
      return { g, at: (t, t0, k) => EC.move(g, t, t0, th, { k, dx: 0, dy: 60, preset: o.preset }) }; }
    const nw = h * .66, g = EC.group(L, x, y, w, h, 14, '20% 50%'); EC.num(g, c.n, 0, h * .06, h * .88, th); const s = EC.surface(g, nw, 0, w - nw, h, th);
    if (o.hiLite) { s.style.boxShadow = EC.cardShadow(th) + `, 0 0 0 3px ${th.glow ? `rgba(${th.glow},.8)` : 'rgba(255,255,255,.9)'}, 0 0 60px ${th.glow ? `rgba(${th.glow},.45)` : 'rgba(255,255,255,.65)'}`; }
    EC.icon(s, c.icon, h * .48, h * .22, h * .26, th, o.iconCol); const tx = h * .95;
    if (o.rule !== false) el(s, 'div', 'abs', { left: (h * .86) + 'px', top: (h * .22) + 'px', width: '2px', height: (h * .56) + 'px', background: rgba(th.sh, .1) });
    title(s, c.title, tx, c.sub ? h * .2 : h * .34, h * .27, th); if (c.sub) txt(s, c.sub, tx, h * .58, h * .16, th.mute, th.body || SANS, 500);
    return { g, s, at: (t, t0, k) => EC.move(g, t, t0, th, { k, preset: o.preset, r: o.r }) }; };

  /* IconCard: compact floating card, icon + label. shape 'tile' | 'disc' */
  EC.IconCard = (L, c, cx, cy, size, th, o) => { o = o || {}; const disc = o.shape === 'disc', g = EC.group(L, cx - size / 2, cy - size / 2, size, size, o.z || 16), s = EC.surface(g, 0, 0, size, size, th, disc ? size / 2 : th.r * size / 220 + 6);
    if (disc) s.style.background = `radial-gradient(circle at 35% 28%, ${th.surf[0]}, ${th.surf[1]})`;
    const lab = c.title && o.label !== 'outside'; EC.icon(s, c.icon, size * (disc ? .4 : .42), size * (disc ? .3 : .29), size * (lab ? (disc ? .16 : .14) : .29), th);
    if (lab) title(s, c.title, 0, size * (disc ? .62 : .64), size * (disc ? .12 : .13), th, { width: size + 'px', textAlign: 'center' });
    return { g, at: (t, t0, k, mo) => EC.move(g, t, t0, th, Object.assign({ k, preset: o.preset }, mo || {})) }; };

  /* FeatureCard: large information card — number + title + body text, icon (or image) in a soft inset well */
  EC.FeatureCard = (L, c, x, y, w, h, th, o) => { o = o || {}; const g = EC.group(L, x, y, w, h, 14), s = EC.surface(g, 0, 0, w, h, th, th.r * 1.4); s.style.overflow = 'hidden';
    const pad = h * .12; if (c.n != null) { const n = th.numMode === 'chip' ? EC.num(s, c.n, pad, pad * .8, h * .3, th) : txt(s, String(c.n), pad, pad * .7, h * .32, th.ink, th.head, th.headW, { lineHeight: 1 }); n.style.zIndex = 2; }
    title(s, c.title, pad + (c.n != null ? h * .27 : 0), pad + h * .04, h * .17, th, { lineHeight: 1 });
    txt(s, c.body || '', pad, pad + h * .38, h * .075, th.mute, SANS, 500, { width: (w * .5) + 'px', whiteSpace: 'normal', lineHeight: 1.4 });
    const wx = w * .6, well = el(s, 'div', 'abs', { left: wx + 'px', top: 0, width: (w - wx) + 'px', height: h + 'px', background: `linear-gradient(200deg, ${th.surf[1]}, ${th.surf[0]})`, boxShadow: `inset 18px 0 30px ${rgba(th.sh, .08)}` });
    if (c.image) { const im = el(well, 'img', 'abs', { left: 0, top: 0, width: '100%', height: '100%', objectFit: 'cover' }); C.setSrc(im, c.image); }
    const ic = c.image ? null : EC.icon(well, c.icon, h * .48, (w - wx - h * .48) / 2, h * .26, th, th.acc);
    if (ic && th.glow) ic.style.filter = `drop-shadow(0 0 14px rgba(${th.glow},.6))`;
    return { g, at(t, t0) { EC.move(g, t, t0, th, { preset: o.preset, d: th.dur + .1 }); if (ic) tf(ic, { s: .7 + .3 * ease.outBack(P(t, t0 + .35, .6), 1.6), o: P(t, t0 + .35, .3) }); } }; };

  /* FlowCard: connected nodes (IconCards) along a polyline or curve, with an animated arrow. pts = [[x,y],...] */
  EC.FlowCard = (L, items, pts, th, o) => { o = o || {}; const size = o.size || 140, path = o.d || EC.smoothPath(pts, o.curve !== false);
    const ln = EC.connector(L, path, th, o.w || 4, o.head !== false, 12), nodes = items.map((it, k) => EC.IconCard(L, it, pts[k][0], pts[k][1], size, th, { shape: o.shape || 'disc', label: o.labels === 'above' ? 'outside' : 'in', preset: 'pop' }));
    const labs = o.labels === 'above' ? items.map((it, k) => el(L, 'div', 'abs', { left: (pts[k][0] - 140) + 'px', width: '280px', top: (pts[k][1] - size / 2 - 50) + 'px', textAlign: 'center', fontFamily: th.head,
      fontWeight: th.headW, fontSize: '28px', letterSpacing: th.head === COND ? '.02em' : '.05em', textTransform: 'uppercase', color: th.type, textShadow: EC.typeFx(th, 40), zIndex: 17 }, it.title)) : [];
    return { nodes, at(t, times) { ln.at(P(t, times[0] - .2, (times[times.length - 1] - times[0]) + .7)); nodes.forEach((n, k) => n.at(t, times[k], k));
      labs.forEach((l, k) => tf(l, { o: P(t, times[k] + .15, .4), y: 10 * (1 - ease.out3(P(t, times[k] + .15, .4))) })); } }; };
  EC.smoothPath = (pts, curve) => { if (!curve || pts.length < 3) return 'M' + pts.map(p => p.join(' ')).join(' L');
    let d = `M${pts[0][0]} ${pts[0][1]}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      d += ` C${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6} ${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]} ${p2[1]}`; } return d; };

  /* ---------- nine layout presets, all built from the five components. box = {x, y, w, h} card area; c = presenter centre [x, y] ---------- */
  EC.times = (t0, n, step) => Array.from({ length: n }, (_, i) => t0 + i * (step ?? .2));
  const pad4 = (a, n) => a.slice(0, n);
  EC.LAYOUTS = {
    /* 1 hero headline beside the presenter */
    'hero': (L, d, b, th) => { const sz = d.size || Math.min(b.w / 3.2, 230), h = EC.HeroCard(L, d.hero, b.x, b.y + sz * .4, sz, th); return { at: (t, ts) => h.at(t, ts[0], ts.length > 1 ? ts[1] - ts[0] : .2) }; },
    /* 2 vertical step cards */
    'steps-v': (L, d, b, th) => { const it = pad4(d.steps, d.n || 3), gap = 30, h = Math.min(220, (b.h - gap * (it.length - 1)) / it.length);
      const cs = it.map((s, k) => EC.StepCard(L, Object.assign({ n: k + 1 }, s), b.x, b.y + k * (h + gap), b.w, h, th)); return { at: (t, ts) => cs.forEach((c, k) => c.at(t, ts[k], k)) }; },
    /* 3 horizontal numbered process + sweeping arrow */
    'steps-h': (L, d, b, th) => { const it = pad4(d.steps, d.n || 4), gap = 26, sz = Math.min(220, (b.w - gap * (it.length - 1)) / it.length), y = b.y + sz * .62;
      const cs = it.map((s, k) => EC.StepCard(L, Object.assign({ n: k + 1 }, s), b.x + k * (sz + gap), y, sz, sz, th, { dir: 'v' })), W = it.length * (sz + gap);
      const ar = EC.connector(L, `M${b.x + 30} ${y + sz + 70} Q${b.x + W * .55} ${y + sz + 170} ${b.x + W - 20} ${y + sz + 40}`, th, 6);
      return { at: (t, ts) => { cs.forEach((c, k) => c.at(t, ts[k], k)); ar.at(P(t, ts[0], ts[ts.length - 1] - ts[0] + .8)); } }; },
    /* 4 circular cards around the presenter */
    'orbit': (L, d, b, th) => { const it = pad4(d.items, d.n || 6), [cx, cy] = d.c || [b.x + b.w / 2, b.y + b.h * .62], R = d.R || Math.min(b.w / 2.1, 520), a0 = Math.PI * .96, a1 = Math.PI * 2.04, sz = d.size || 170;
      const A = k => a0 + (a1 - a0) * k / Math.max(1, it.length - 1), pts = it.map((_, k) => [cx + R * Math.cos(A(k)), cy + R * Math.sin(A(k))]);
      const arc = EC.connector(L, `M${pts[0][0]} ${pts[0][1]} A${R * .8} ${R * .8} 0 0 1 ${pts[pts.length - 1][0]} ${pts[pts.length - 1][1]}`, th, 4, false, 11);
      const cs = it.map((s, k) => EC.IconCard(L, s, pts[k][0], pts[k][1], sz, th, { shape: 'disc', preset: 'pop' }));
      return { at: (t, ts) => { arc.at(P(t, ts[0] - .2, ts[ts.length - 1] - ts[0] + .6)); cs.forEach((c, k) => c.at(t, ts[k], k)); } }; },
    /* 5 large statement headline with directional arrows */
    'statement': (L, d, b, th) => { const sz = d.size || Math.min(b.w / 3.3, 230), x = b.x, y = b.y + sz * .7, h = EC.HeroCard(L, d.statement, x, y, sz, th, { rot: th.heroRot ? -8 : 0 });
      const u = EC.connector(L, `M${x + 80} ${y + sz * 1.9} Q${x + sz * 2.2} ${y + sz * 1.6} ${x + sz * 3.4} ${y + sz * 1.2}`, th, 9), top = EC.connector(L, `M${x + sz * 1.2} ${y - sz * .3} Q${x + sz * 2.5} ${y - sz * .6} ${x + sz * 3.3} ${y - sz * 1}`, th, 5);
      return { at: (t, ts) => { h.at(t, ts[0], .25); u.at(P(t, ts[0] + .8, .7)); top.at(P(t, ts[0] + .45, .6)); } }; },
    /* 6 stacked information cards (first one highlighted) */
    'stack': (L, d, b, th) => { const it = pad4(d.steps, d.n || 4), gap = 18, h = Math.min(160, (b.h - gap * (it.length - 1)) / it.length);
      const cs = it.map((s, k) => { const hi = k === 0 && d.highlight !== false, w = hi ? b.w : b.w * .94, c = EC.StepCard(L, Object.assign({ n: k + 1 }, s), b.x + (hi ? 0 : b.w * .05), b.y + k * (h + gap) + (hi ? 0 : 6), w, h, th, { hiLite: hi, preset: th.motion === 'fade-slide' ? 'fade-slide' : 'stack' }); if (hi) c.g.style.zIndex = 15; return c; });
      return { at: (t, ts) => cs.forEach((c, k) => c.at(t, ts[k], k)) }; },
    /* 7 large feature highlight card */
    'feature': (L, d, b, th) => { const f = EC.FeatureCard(L, d.feature, b.x, b.y, b.w, Math.min(b.h, b.w * .56), th); return { at: (t, ts) => f.at(t, ts[0]) }; },
    /* 8 curved workflow / journey across the frame */
    'journey': (L, d, b, th) => { const it = pad4(d.items, d.n || 7), n = it.length, amp = d.amp ?? b.h * .45, pts = it.map((_, k) => { const u = n > 1 ? k / (n - 1) : .5; return [b.x + b.w * u, b.y + b.h - amp * Math.sin(Math.PI * u)]; });
      const f = EC.FlowCard(L, it, pts, th, { size: d.size || 120, labels: 'above' }); return { at: (t, ts) => f.at(t, ts) }; },
    /* 9 floating card grid, tiles rearrange into a tilted 3D wall */
    'grid': (L, d, b, th) => { const it = pad4(d.items, d.n || 7), cols = d.cols || 3, gap = 26, sz = Math.min(220, (b.w - gap * (cols - 1)) / cols), R = C.rng(d.seed || 5);
      const wrap = EC.group(L, b.x, b.y, cols * (sz + gap), Math.ceil(it.length / cols) * (sz + gap), 14); wrap.style.transform = 'perspective(1600px) rotateY(-14deg) rotateX(8deg) rotateZ(-6deg)';
      const cs = it.map((s, k) => { const r = Math.floor(k / cols), rowN = Math.min(cols, it.length - r * cols), off = (cols - rowN) * (sz + gap) / 2;
        const c = EC.IconCard(wrap, s, off + (k % cols) * (sz + gap) + sz / 2, r * (sz + gap) + sz / 2, sz, th, { preset: 'rearrange' }); c.mo = { dx: (R() - .5) * 700, dy: (R() - .3) * 500, dr: (R() - .5) * 40 }; return c; });
      return { at: (t, ts) => cs.forEach((c, k) => c.at(t, ts[k], k, c.mo)) }; },
  };
  EC.layout = (L, name, data, box, th) => { const f = EC.LAYOUTS[name]; if (!f) throw new Error('EVA cards: unknown layout ' + name); return f(L, data, box, th); };

  /* ---------- presenter-safe regions: keep cards off the face. win = Eva window rect {x,y,w,h} ---------- */
  EC.region = (anchor, win, m) => { m = m ?? 70; const W = 1920, H = 1080, w = win || { x: 660, y: 0, w: 600, h: H };
    switch (anchor) { case 'left': return { x: m, y: m + 40, w: Math.max(300, w.x - 2 * m), h: H - 2 * m - 80 };
      case 'top': return { x: m, y: m, w: W - 2 * m, h: Math.max(200, w.y - 2 * m) };
      case 'bottom': return { x: m, y: w.y + w.h + m, w: W - 2 * m, h: Math.max(200, H - w.y - w.h - 2 * m) };
      case 'around': return { x: w.x - 80, y: w.y, w: w.w + 160, h: w.h };
      default: return { x: w.x + w.w + m, y: m + 40, w: Math.max(300, W - w.x - w.w - 2 * m), h: H - 2 * m - 80 }; } };
  EC.overlapsFace = (box, faceRect) => !(box.x + box.w < faceRect.x || faceRect.x + faceRect.w < box.x || box.y + box.h < faceRect.y || faceRect.y + faceRect.h < box.y);

  /* ---------- JSON card specs (see references/cards.md). type: hero | step | icon | flow | feature | layout ---------- */
  const TYPE2LAYOUT = { hero: 'hero', step: 'steps-v', icon: 'grid', flow: 'journey', feature: 'feature' };
  EC.validate = spec => { const e = [], types = ['hero', 'step', 'icon', 'flow', 'feature', 'layout'];
    if (!spec || typeof spec !== 'object') return ['spec must be an object'];
    if (!types.includes(spec.type)) e.push(`${spec.id || '?'}: type must be one of ${types.join(', ')}`);
    if (spec.layout && !EC.LAYOUTS[spec.layout]) e.push(`${spec.id}: unknown layout ${spec.layout}`);
    const a = spec.animation || {}; if (a.start == null && !a.word && !(a.times && a.times.length)) e.push(`${spec.id}: animation needs start, word or times`);
    if (a.preset && !EC.MOTIONS.concat(['sequential', 'arrow-draw', 'curve-reveal']).includes(a.preset)) e.push(`${spec.id}: unknown animation preset ${a.preset}`);
    if (spec.content && spec.content.icon && T.cpIconNames && !T.cpIconNames.includes(spec.content.icon)) e.push(`${spec.id}: unknown icon ${spec.content.icon}`);
    return e; };
  /* times: animation.times > animation.word (+EV.asr) > start + i*stagger. toLocal converts absolute (SRT/ASR) seconds to section time. */
  EC.specTimes = (spec, n, toLocal) => { const a = spec.animation || {}, f = toLocal || (s => s);
    if (a.times) return a.times.map(f); if (a.words && C.asr) return a.words.map(w => f(C.asr.at(w)));
    const s0 = a.word && C.asr ? C.asr.at(a.word) : a.start; return EC.times(f(s0), n, a.stagger ?? .2); };
  EC.fromSchema = (L, specs, th0, opt) => { opt = opt || {}; return specs.map(sp => { const bad = EC.validate(sp); if (bad.length) throw new Error('EVA cards: ' + bad.join('; '));
      const th = sp.style && sp.style !== th0.name && EC.THEMES[sp.style] ? EC.theme(sp.style) : Object.assign({}, th0), a = sp.animation || {};
      if (a.preset && EC.MOTIONS.includes(a.preset)) th.motion = a.preset; if (a.duration) th.dur = a.duration;
      const p = sp.position || {}, box = p.w ? { x: p.x * 1920, y: p.y * 1080, w: p.w * 1920, h: (p.h || .6) * 1080 } : Object.assign(EC.region(p.anchor || 'right', opt.win), p.x != null ? { x: p.x * 1920, y: p.y * 1080 } : {});
      const c = sp.content || {}, name = sp.layout || TYPE2LAYOUT[sp.type] || 'steps-v';
      const data = { hero: c.words ? c : { words: [c.title], sub: c.subtitle, kicker: c.kicker }, statement: c.words ? c : { script: c.kicker, words: [c.title], sub: c.subtitle },
        steps: c.items || [{ n: c.number, title: c.title, sub: c.subtitle, icon: c.icon }], items: c.items || [{ title: c.title, icon: c.icon }],
        feature: { n: c.number, title: c.title, body: c.body || c.subtitle, icon: c.icon, image: c.image }, n: (c.items || [1]).length, c: p.center, size: p.size };
      const o = EC.layout(L, name, data, box, th), n = name === 'hero' || name === 'statement' ? (data.hero.words || []).length + 2 : (name === 'feature' ? 1 : data.n);
      return { id: sp.id, o, times: EC.specTimes(sp, n, opt.toLocal), end: a.end != null ? (opt.toLocal || (s => s))(a.end) : null, L }; }); };
  EC.schemaAt = (list, t) => list.forEach(c => c.o.at(t, c.times));
})();
