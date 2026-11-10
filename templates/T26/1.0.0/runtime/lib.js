/* T26 Vintage Story (复古拼贴故事) · template-owned runtime library, version 1.0.0 (from t26-rebuild 04f6842, engine/t26.js).
 * Vertical-first (1080×1920); 16:9 is prepared for separate testing only (not a supported aspect yet).
 * Old-newspaper collage stage (seeded, stable), torn cream paper cards, condensed caps (Anton) + heavy newspaper serif
 * (Playfair Display) + italic hand notes, yellow highlighter BEHIND words, red hand-drawn lines / arrows / double circles that
 * draw on, photo prints with tape, and the presenter as a cream-outlined paper cut-out.
 * Presenter rule (the scaling fix): the cut-out always keeps the footage's own scale (s = 1); layouts only MOVE her (x / y),
 * so the whole head, shoulders and gestures stay visible. Her pixels are the HD frame masked by the AI cut-out.
 *   const o = T.vtLayout(n, L, words, m)  ·  per frame T.vtLayoutAt(o, t, t0, m, dur)
 *   m = { frame: t => HD frame jpg, cut: t => cut-out webp }; words come from the script (sample copy in the demo).
 * words: in a manual scene missing fields fall back to the sample copy; with words.auto = true (automatic edit) a missing
 * field is simply left out, so only transcript text ever reaches the screen. Layout 0 = collage + presenter only.
 * Layouts: 1 giant title behind · 2 ID card · 3 story card · 4 key collage · 5 statement · 6 big number · 7 before/after ·
 *          8 three steps · 9 ending chapter.  No sound is built in (add K.cue per video). */
(function () {
  const C = EV, { el, tf, P, ease, clamp, pop } = C, T = K.T;
  const VT = T.VT = { PAPER: '#ece2cc', PAPER2: '#e2d5b9', INK: '#1d1a17', BASE: '#2b2620', SEP: '#8d8578', RED: '#c62029', YEL: '#f6e22b',
    CAPS: "'Anton','Noto Sans CJK SC',sans-serif", SERIF: "'Playfair Display','Noto Serif CJK SC',serif", HAND: "'Playfair Display',serif" };
  const ns = 'http://www.w3.org/2000/svg';
  const rnd = (s => () => (s = (s * 16807) % 2147483647) / 2147483647);
  const svg = (P2, x, y, w, h, inner, z) => { const s = document.createElementNS(ns, 'svg'); s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    Object.assign(s.style, { position: 'absolute', left: x + 'px', top: y + 'px', overflow: 'visible', zIndex: z || 6 }); s.innerHTML = inner; P2.appendChild(s); return s; };
  const torn = (r, w, h, j) => { const pts = [], n = Math.max(8, Math.round(w / 40)), m = Math.max(6, Math.round(h / 40)); j = j || 1;
    for (let i = 0; i <= n; i++) pts.push([i / n * 100, (r() * 1.6 * j)]); for (let i = 1; i <= m; i++) pts.push([100 - r() * 1.2 * j, i / m * 100]);
    for (let i = n - 1; i >= 0; i--) pts.push([i / n * 100, 100 - r() * 1.8 * j]); for (let i = m - 1; i > 0; i--) pts.push([r() * 1.2 * j, i / m * 100]);
    return 'polygon(' + pts.map(([a, b]) => `${a.toFixed(1)}% ${b.toFixed(1)}%`).join(',') + ')'; };
  const newsprint = (dark) => `repeating-linear-gradient(0deg, rgba(40,34,26,${dark ? .22 : .16}) 0 3px, transparent 3px 11px)`;

  /* ---------- stage: seeded old-newspaper collage ---------- */
  T.vtBg = VT.BASE;
  T.vtStage = (L, seed) => { const r = rnd(seed * 9973 + 7), o = { root: el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', overflow: 'hidden', zIndex: 0 }) };
    o.cam = el(o.root, 'div', 'abs', { left: '-4%', top: '-4%', width: '108%', height: '108%', background: VT.BASE, transformOrigin: '50% 45%' });
    const W = C.W * 1.08, H = C.H * 1.08;
    for (let i = 0; i < 46; i++) { const w = 160 + r() * 360, h = 120 + r() * 320, x = r() * W - 80, y = r() * H - 80, k = r(), photo = k < .32;
      const c = el(o.cam, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', transform: `rotate(${(r() - .5) * 8}deg)`,
        background: photo ? `radial-gradient(${w * .18}px ${w * .2}px at ${30 + r() * 40}% ${45 + r() * 15}%, rgba(40,36,30,.85) 98%, transparent), linear-gradient(180deg, #a49b8c, #6f675b)`
          : `${newsprint(k > .8)}, linear-gradient(180deg, ${k > .66 ? '#d9cdb1' : '#cfc3a6'}, #bfb295)`,
        clipPath: torn(r, w, h, .8), boxShadow: '0 6px 14px rgba(0,0,0,.45)', opacity: .9 });
      if (!photo && r() < .55) el(c, 'div', 'abs', { left: '8%', top: '8%', width: '84%', height: (14 + r() * 12) + '%', background: 'rgba(40,34,26,.55)' }); }
    o.grain = svg(o.root, 0, 0, C.W, C.H, `<filter id="vtg${seed}"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="${seed}"/><feColorMatrix values="0 0 0 0 .1  0 0 0 0 .08  0 0 0 0 .05  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#vtg${seed})"/>`, 1);
    o.grain.style.opacity = .5; o.grain.style.mixBlendMode = 'multiply';
    el(o.root, 'div', 'abs', { left: 0, top: 0, width: '100%', height: '100%', zIndex: 2, background: 'radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 45%, rgba(20,14,8,.55))' });
    return o; };
  T.vtStageAt = (o, t, lt, dur) => tf(o.cam, { s: 1.05 - .05 * ease.out3(P(lt, 0, dur || 2)) });

  /* ---------- paper, type, marks ---------- */
  T.vtCard = (P2, x, y, w, h, rot, seed, opt) => { opt = opt || {}; const r = rnd(seed * 31 + 3), d = el(P2, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', zIndex: opt.z || 6,
      transformOrigin: '50% 50%', filter: 'drop-shadow(0 14px 18px rgba(10,6,2,.55))' });
    d.p = el(d, 'div', 'abs', { left: 0, top: 0, width: '100%', height: '100%', background: `${opt.lines ? newsprint() + ',' : ''}linear-gradient(170deg, ${VT.PAPER}, ${VT.PAPER2})`, clipPath: torn(r, w, h, 1.2) });
    d.rot = rot || 0; return d; };
  T.vtText = (P2, s, x, y, fs, opt) => { opt = opt || {};
    if (opt.fitW && s) { const g = (opt.f && opt.f !== VT.CAPS) ? .56 : .46, n = Math.max(...String(s).split('\n').map(l => l.length), 1); fs = Math.min(fs, opt.fitW / (g * n)); }
    return el(P2, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: opt.f || VT.CAPS, fontWeight: opt.w || 400, fontStyle: opt.it ? 'italic' : 'normal',
    fontSize: fs + 'px', lineHeight: opt.lh || .92, color: opt.c || VT.INK, whiteSpace: 'pre', zIndex: opt.z || 7, textTransform: opt.up === false ? 'none' : (opt.f && opt.f !== VT.CAPS ? 'none' : 'uppercase'),
    letterSpacing: opt.ls || '0', textAlign: opt.al || 'left', transformOrigin: opt.o || '0 50%', textShadow: opt.sh || 'none' }, s); };
  T.vtHi = (P2, x, y, w, h, z) => { const d = el(P2, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: VT.YEL, zIndex: z || 6, transformOrigin: '0 50%',
      clipPath: 'polygon(1% 12%, 99% 0, 100% 88%, 0 100%)', opacity: .92 }); return d; };
  const stroke = (d, col, w) => `<path class="ln" d="${d}" fill="none" stroke="${col || VT.RED}" stroke-width="${w || 7}" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/>`;
  T.vtLine = (P2, x, y, w, h, d, z, col, sw) => svg(P2, x, y, w, h, stroke(d, col, sw), z || 8);
  T.vtUnder = (P2, x, y, w) => T.vtLine(P2, x, y, w, 40, `M4 22 C ${w * .3} 8, ${w * .65} 34, ${w - 4} 14`);
  T.vtArrow = (P2, x, y, w, h) => T.vtLine(P2, x, y, w, h, `M6 ${h * .2} C ${w * .4} ${h * .1}, ${w * .7} ${h * .5}, ${w - 10} ${h - 12} M${w - 46} ${h - 22} L${w - 10} ${h - 12} L${w - 22} ${h - 50}`);
  T.vtCircle = (P2, x, y, w, h) => T.vtLine(P2, x, y, w, h, `M${w * .55} 6 C ${w * 1.02} 4, ${w * 1.02} ${h - 4}, ${w * .48} ${h - 6} C ${w * .02} ${h - 8}, -2 ${h * .2}, ${w * .5} 10 C ${w * .9} 14, ${w * .98} ${h * .62}, ${w * .62} ${h - 16}`);
  T.vtChart = (P2, x, y, w, h) => { const pts = [[0, .8], [.22, .55], [.4, .7], [.62, .3], [.8, .45], [1, .1]].map(([a, b]) => [a * w, b * h]);
    return svg(P2, x, y, w, h, stroke('M' + pts.map(p => p.join(' ')).join(' L'), VT.RED, 6) + pts.map((p, i) => `<circle class="dot" cx="${p[0]}" cy="${p[1]}" r="11" fill="${VT.RED}" data-i="${i}"/>`).join(''), 8); };
  T.vtIcon = (P2, kind, x, y, s, z) => svg(P2, x, y, s, s, kind === 'bulb'
    ? `<path d="M${s * .5} ${s * .1}c-${s * .2} 0-${s * .32} ${s * .14}-${s * .32} ${s * .32} 0 ${s * .14} ${s * .08} ${s * .22} ${s * .14} ${s * .3} ${s * .04} ${s * .05} ${s * .05} ${s * .1} ${s * .05} ${s * .16}h${s * .26}c0-${s * .06} ${s * .01}-${s * .11} ${s * .05}-${s * .16} ${s * .06}-${s * .08} ${s * .14}-${s * .16} ${s * .14}-${s * .3} 0-${s * .18}-${s * .12}-${s * .32}-${s * .32}-${s * .32}z" fill="${VT.PAPER}" stroke="${VT.INK}" stroke-width="${s * .05}"/><path d="M${s * .38} ${s * .8}h${s * .24}M${s * .41} ${s * .9}h${s * .18}" stroke="${VT.PAPER}" stroke-width="${s * .05}" stroke-linecap="round"/>`
    : `<circle cx="${s * .42}" cy="${s * .42}" r="${s * .26}" fill="none" stroke="${VT.INK}" stroke-width="${s * .08}"/><path d="M${s * .62} ${s * .62}L${s * .9} ${s * .9}" stroke="${VT.INK}" stroke-width="${s * .12}" stroke-linecap="round"/>`, z || 7);
  T.vtTape = (P2, x, y, w, rot) => el(P2, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: '44px', background: 'rgba(236,226,204,.72)', transform: `rotate(${rot}deg)`, zIndex: 9, boxShadow: '0 2px 4px rgba(0,0,0,.25)' });
  /* photo print: the original frame (no cut-out) in a cream border, optional black-and-white */
  T.vtPrint = (P2, x, y, w, h, rot, opt) => { opt = opt || {}; const d = el(P2, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: VT.PAPER, padding: '18px 18px 60px', boxSizing: 'border-box',
      zIndex: opt.z || 6, transformOrigin: '50% 50%', boxShadow: '0 18px 30px rgba(10,6,2,.55)' }); d.rot = rot || 0;
    const win = el(d, 'div', '', { width: '100%', height: '100%', overflow: 'hidden', position: 'relative', background: '#555' });
    const iw = w - 36, ih = h - 78, k = Math.max(iw / C.src.w, ih / C.src.h) * (opt.zoom || 1.25);   // a print is a photo of the frame: cropped around the face
    d.img = el(win, 'img', 'abs', { width: C.src.w * k + 'px', height: C.src.h * k + 'px', left: (iw / 2 - C.face.x * C.src.w * k) + 'px', top: (ih * (opt.fy || .42) - C.face.y * C.src.h * k) + 'px',
      filter: opt.bw ? 'grayscale(1) contrast(1.1) brightness(1.02)' : 'sepia(.12) contrast(1.04)' });
    if (opt.cap) el(d, 'div', 'abs', { left: '20px', bottom: '8px', fontFamily: VT.HAND, fontStyle: 'italic', fontWeight: 700, fontSize: '34px', color: VT.INK }, opt.cap);
    return d; };
  /* presenter cut-out: HD frame masked by the AI cut-out, cream outline + shadow on the wrapper; scale is always 1 */
  T.vtCut = (P2, z) => { const w = el(P2, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', zIndex: z || 5,
      filter: `drop-shadow(5px 0 0 ${VT.PAPER}) drop-shadow(-5px 0 0 ${VT.PAPER}) drop-shadow(0 5px 0 ${VT.PAPER}) drop-shadow(0 -5px 0 ${VT.PAPER}) drop-shadow(0 18px 22px rgba(10,6,2,.55))` });
    w.im = el(w, 'img', 'abs', { left: 0, top: 0, width: '100%', height: '100%', objectFit: 'cover', WebkitMaskSize: '100% 100%', maskSize: '100% 100%', WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat' }); return w; };
  T.vtCutAt = (w, m, t, pose) => { C.setSrc(w.im, m.frame(t)); const mk = `url(${m.cut(t)})`; if (w.im._m !== mk) { w.im.style.webkitMaskImage = w.im.style.maskImage = mk; w.im._m = mk; } const p = pose || {}; tf(w, { x: p.x || 0, y: p.y || 0, s: 1 }); };

  /* ---------- layouts (1080×1920 coordinates) ---------- */
  T.vtLayout = (n, L, w, m) => { w = w || {}; const o = { n, it: [], w, prints: [] }, S = (k, d) => (w[k] != null && w[k] !== '' ? w[k] : (w.auto ? null : d));
    o.root = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', overflow: 'hidden' }); o.st = T.vtStage(o.root, n * 7 + 3);
    const R = o.root, add = (e, dt, mode, ex) => (o.it.push(Object.assign({ e, dt, mode }, ex || {})), e), cut = (pose, z) => { o.cut = T.vtCut(R, z); o.pose = pose; };
    if (n === 0) cut({ x: 0, y: 0 }, 5);
    if (n === 1) { add(T.vtText(R, S('a', 'VINTAGE'), 40, 230, 360, { fitW: w.auto ? 1000 : 0, c: VT.PAPER, sh: '0 10px 24px rgba(0,0,0,.6)', z: 4, ls: '-.01em', o: '50% 50%' }), 0, 'rise');
      cut({ x: 0, y: 70 }, 5);
      if (S('b', 1) !== null) { const n1 = add(T.vtCard(R, 40, 1430, 330, 190, -6, 11, { z: 8, lines: 1 }), .3, 'slideUp'); T.vtText(n1, S('b', 'STORY'), 36, 46, 92, { z: 2 });
      const n2 = add(T.vtCard(R, 690, 1480, 330, 170, 5, 12, { z: 8, lines: 1 }), .42, 'slideUp'); T.vtText(n2, S('c', 'NO. 01'), 34, 40, 80, { z: 2 });
      add(T.vtLine(R, 330, 1410, 420, 60, 'M6 40 C 120 6, 300 60, 414 14'), .55, 'draw'); } }
    if (n === 2) { const pr = add(T.vtPrint(R, 150, 240, 780, 980, -4, { cap: S('d', 'est. today'), zoom: 1.15 }), 0, 'drop'); o.prints.push(pr); T.vtTape(R, 430, 220, 220, -3);
      const c = add(T.vtCard(R, 120, 1270, 840, 330, 3, 21, { z: 8 }), .25, 'slideUp');
      T.vtText(c, S('a', "HI, I'M EVA"), 60, 50, 150, { z: 2 }); T.vtText(c, S('b', 'creator & storyteller'), 66, 220, 58, { f: VT.HAND, it: 1, w: 700, c: VT.RED, up: false, z: 2 });
      add(T.vtUnder(R, 190, 1530, 560), .55, 'draw'); }
    if (n === 3) { cut({ x: 0, y: 380 }, 5); const c = add(T.vtCard(R, 70, 170, 940, 560, -3, 31, { z: 7 }), 0, 'slideDown');
      add(T.vtHi(c, 50, 70, 560, 170, 1), .3, 'hi'); T.vtText(c, S('a', 'THE'), 60, 40, 220, { z: 2, fitW: w.auto ? 820 : 0 }); if (S('b', 1) !== null) T.vtText(c, S('b', 'STORY'), 60, 250, 250, { z: 2, fitW: w.auto ? 820 : 0 });
      add(T.vtLine(R, 700, 330, 260, 300, 'M20 280 C 60 120, 160 60, 240 20'), .55, 'draw'); }
    if (n === 4) { const c = add(T.vtCard(R, 90, 260, 620, 420, -5, 41, { z: 7 }), 0, 'slideDown'); add(T.vtHi(c, 40, 60, 470, 150, 1), .25, 'hi');
      T.vtText(c, S('a', 'MIX &'), 50, 40, 170, { z: 2 }); T.vtText(c, S('b', 'MATCH'), 50, 210, 170, { z: 2 });
      const pr = add(T.vtPrint(R, 520, 720, 470, 600, 6, { cap: S('d', 'take one'), zoom: 1.1 }), .15, 'drop'); o.prints.push(pr); T.vtTape(R, 640, 700, 200, 4);
      add(T.vtChart(R, 90, 820, 400, 260), .4, 'chart'); add(T.vtIcon(R, 'bulb', 110, 1150, 170), .5, 'pop'); add(T.vtIcon(R, 'mag', 330, 1250, 150), .6, 'pop');
      add(T.vtArrow(R, 640, 1340, 240, 200), .7, 'draw'); }
    if (n === 5) { cut({ x: 0, y: 500 }, 5); const c = add(T.vtCard(R, 50, 160, 980, 700, 2, 51, { z: 7, lines: 0 }), 0, 'slideDown');
      if (S('k', 1) !== null) { T.vtText(c, S('k', 'THE EVA TIMES'), 60, 40, 46, { f: VT.SERIF, w: 900, ls: '.12em', z: 2, up: false }); el(c, 'div', 'abs', { left: '60px', top: '110px', width: '860px', height: '6px', background: VT.INK, zIndex: 2 }); }
      T.vtText(c, S('a', 'Every story'), 60, 150, 132, { f: VT.SERIF, w: 900, z: 2, lh: 1, fitW: w.auto ? 860 : 0 }); if (S('b', 1) !== null) T.vtText(c, S('b', 'deserves a frame.'), 60, 300, 112, { f: VT.SERIF, w: 900, it: 1, z: 2, lh: 1 });
      if (S('c', 1) !== null) T.vtText(c, S('c', 'a vintage collage for talking-head videos'), 64, 470, 44, { f: VT.SERIF, w: 400, it: 1, z: 2, up: false, c: '#4a4238' });
      add(T.vtCircle(R, 90, 270, 560, 230), .4, 'draw'); }
    if (n === 6) { cut({ x: 230, y: 420 }, 5); const c = add(T.vtCard(R, 60, 200, 700, 760, -4, 61, { z: 7 }), 0, 'slideDown');
      T.vtText(c, S('a', '5'), 90, 60, 520, { z: 2, lh: 1 }); T.vtText(c, S('b', 'SECONDS'), 380, 420, 88, { z: 2 }); T.vtText(c, S('c', 'is all it takes'), 80, 600, 64, { f: VT.HAND, it: 1, w: 700, c: VT.RED, z: 2, up: false });
      add(T.vtCircle(R, 90, 190, 560, 640), .35, 'draw'); }
    if (n === 7) { const a = add(T.vtPrint(R, 70, 230, 600, 720, -6, { bw: 1, cap: S('a', 'before'), zoom: 1.15 }), 0, 'drop'); const b = add(T.vtPrint(R, 410, 930, 600, 720, 5, { cap: S('b', 'after'), zoom: 1.15 }), .25, 'drop');
      o.prints.push(a, b); T.vtTape(R, 240, 210, 200, -4); T.vtTape(R, 620, 910, 200, 3);
      const s1 = add(T.vtCard(R, 690, 330, 330, 170, 6, 71, { z: 8 }), .4, 'popr'); T.vtText(s1, S('c', 'PLAIN'), 40, 40, 96, { z: 2 });
      const s2 = add(T.vtCard(R, 60, 1300, 330, 170, -5, 72, { z: 8 }), .55, 'popr'); T.vtText(s2, S('d', 'STORY'), 36, 40, 96, { z: 2 }); add(T.vtArrow(R, 640, 560, 260, 330), .5, 'draw'); }
    if (n === 8) { const pr = add(T.vtPrint(R, 650, 300, 380, 460, 5, { cap: S('d', 'you'), zoom: 1.1 }), 0, 'drop'); o.prints.push(pr); T.vtTape(R, 750, 280, 160, 3);
      add(T.vtText(R, S('k', 'HOW IT\nWORKS'), 70, 260, 150, { c: VT.PAPER, sh: '0 8px 18px rgba(0,0,0,.6)', lh: 1, z: 8 }), .1, 'rise');
      (S('list', ['Record', 'Choose a style', 'Share'])).slice(0, 3).forEach((s, i) => { const c = add(T.vtCard(R, 70 + i * 30, 780 + i * 290, 900, 240, i % 2 ? 2 : -2, 81 + i, { z: 7 }), .25 + i * .2, 'slideLeft');
        T.vtText(c, String(i + 1).padStart(2, '0'), 50, 50, 150, { c: VT.RED, z: 2 }); T.vtText(c, s, 250, 70, 104, { f: VT.SERIF, w: 900, z: 2, up: false }); }); }
    if (n === 9) { cut({ x: 0, y: 120 }, 5); add(T.vtText(R, S('a', 'THE END'), 50, 200, 250, { fitW: w.auto ? 980 : 0, c: VT.PAPER, sh: '0 10px 24px rgba(0,0,0,.6)', z: 4 }), 0, 'rise');
      if (S('b', 1) !== null) { const c = add(T.vtCard(R, 120, 1400, 840, 260, -2, 91, { z: 8 }), .3, 'slideUp'); T.vtText(c, S('b', 'follow for the next chapter'), 50, 80, 64, { f: VT.HAND, it: 1, w: 700, c: VT.RED, z: 2, up: false });
      add(T.vtUnder(R, 220, 1600, 640), .55, 'draw'); } }
    return o; };

  T.vtLayoutAt = (o, t, t0, m, dur) => { const lt = t - t0; T.vtStageAt(o.st, t, lt, dur);
    if (o.cut) { const k = ease.outBack(P(lt, .05, .45), 1.3); T.vtCutAt(o.cut, m, t, { x: o.pose.x, y: o.pose.y + 60 * (1 - k) }); o.cut.style.opacity = P(lt, 0, .2); }
    o.prints.forEach(p => { C.setSrc(p.img, m.frame(t)); });
    o.it.forEach(it => { const e = it.e, u = P(lt, it.dt, .45), r = e.rot || it.r || 0;
      switch (it.mode) {
        case 'rise': tf(e, { y: 90 * (1 - ease.outExpo(u)), o: P(lt, it.dt, .25), s: 1.04 - .04 * ease.out3(P(lt, it.dt, dur || 2)) }); break;
        case 'slideUp': tf(e, { y: 260 * (1 - ease.outBack(u, 1.2)), r, o: P(lt, it.dt, .15) }); break;
        case 'slideDown': tf(e, { y: -260 * (1 - ease.outBack(u, 1.2)), r, o: P(lt, it.dt, .15) }); break;
        case 'slideLeft': tf(e, { x: 420 * (1 - ease.outBack(u, 1.2)), r, o: P(lt, it.dt, .15) }); break;
        case 'drop': tf(e, { s: 1.18 - .18 * ease.outBack(u, 1.6), r: r + 6 * (1 - u), o: P(lt, it.dt, .15) }); break;
        case 'popr': tf(e, { s: ease.outBack(u, 2), r, o: P(lt, it.dt, .1) }); break;
        case 'pop': tf(e, { s: ease.outBack(u, 2.2), o: P(lt, it.dt, .1), r: 4 * Math.sin(t * 2 + it.dt) }); break;
        case 'hi': e.style.transform = `scaleX(${ease.out3(P(lt, it.dt, .35)).toFixed(3)})`; break;
        case 'draw': e.querySelectorAll('.ln').forEach(p => { p.style.strokeDasharray = 1; p.style.strokeDashoffset = 1 - ease.out3(P(lt, it.dt, .5)); }); e.style.opacity = P(lt, it.dt, .05); break;
        case 'chart': { const q = ease.out3(P(lt, it.dt, .6)); e.querySelectorAll('.ln').forEach(p => { p.style.strokeDasharray = 1; p.style.strokeDashoffset = 1 - q; });
          e.querySelectorAll('.dot').forEach(d => { const k = clamp(q * 6 - +d.dataset.i); d.setAttribute('r', (11 * ease.outBack(k, 2)).toFixed(1)); }); e.style.opacity = P(lt, it.dt, .05); break; }
      } });
  };
})();
