/* Eva Video Style · template library for T08–T17. Load after kit.js (and land.js for the T14 globe).
 *   T08 NEON  · 霓虹讲解 Neon Explainer
 *   T09 WALL  · 作品墙开场 Showcase Wall Opener
 *   T10 KEY   · HUD 发布会 HUD Keynote
 *   T11 DASH  · HUD 仪表盘 HUD Dashboard
 *   T12 NEWS  · 旧报纸 Old Newspaper
 *   T13 TECH  · 科技蓝 Tech Blue
 *   T14 FUT   · 未来科技 Future Style
 *   T15 LEARN · 学习风 Learning Style
 *   T16 COMIC · 漫画风 Comic Pop
 *   T17 SCI   · 科学风 Science Network
 * Every builder takes (parent, ...) and returns an object; the matching *At(obj, ...) call animates it inside update().
 * Colours, sizes and copy are parameters: never hard-code facts — pass what Eva actually says. */
(function () {
  const C = window.EV, K = window.K, { el, tf, pop, slide, P, ease, clamp, lerp } = C;
  const NS = 'http://www.w3.org/2000/svg';
  const T = K.T = {};

  /* ---------- shared HUD look (T09–T11) ---------- */
  T.HUD = { BG: '#0a0b0f', LINE: 'rgba(255,255,255,.14)', DIM: 'rgba(255,255,255,.42)', BLUE: '#4d7cff', GOLD: '#f5b83d', GREEN: '#34d27b', RED: '#ff4d4d', PANEL: '#14161d' };
  T.hudBg = `radial-gradient(1200px 700px at 50% 40%, #151822, ${T.HUD.BG} 70%)`;
  /* frame: corner brackets, mono labels, running timecode, bottom tick ruler. Call T.hudFrameAt(f, t) in update. */
  T.hudFrame = (L, label, code) => {
    const f = { L }; const m = 26, H = T.HUD;
    const box = el(L, 'div', 'abs', { left: m + 'px', top: m + 'px', width: (1920 - 2 * m) + 'px', height: (1080 - 2 * m) + 'px', color: 'rgba(255,255,255,.28)', zIndex: 2 });
    ['tl', 'tr', 'bl', 'br'].forEach(c => el(box, 'div', 'hudc ' + c));
    f.lab = el(L, 'div', 'abs mono', { left: '62px', top: '44px', fontSize: '13px', color: H.DIM }, (label || 'EVA · VIDEO STYLE') + '  —  ' + (code || '01'));
    f.tc = el(L, 'div', 'abs mono', { right: '62px', top: '44px', fontSize: '13px', color: H.DIM }, '00:00:00:00');
    const r = el(L, 'div', 'abs', { left: '62px', right: '62px', bottom: '40px', height: '8px', backgroundImage: `repeating-linear-gradient(90deg, ${H.LINE} 0 1px, transparent 1px 24px)` });
    f.dot = el(L, 'div', 'abs', { bottom: '38px', left: '62px', width: '12px', height: '12px', borderRadius: '50%', background: H.BLUE, boxShadow: `0 0 12px ${H.BLUE}` });
    return f; };
  T.hudFrameAt = (f, t, total) => { const fr = Math.floor(t * 30); const s = Math.floor(t);
    f.tc.textContent = `00:${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}:${String(fr % 30).padStart(2, '0')}`;
    f.dot.style.left = (62 + (1920 - 136) * clamp(t / (total || C.end))) + 'px'; };
  /* small title with one highlighted word: T.title(L, 'KEEP ', 'IMPROVING', x, y, size, hiColor) */
  T.title = (L, a, hi, x, y, size, col, after) => el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: (size || 46) + 'px', color: '#fff', fontWeight: 900 }, `${a || ''}<span style="color:${col || T.HUD.BLUE}">${hi || ''}</span>${after || ''}`);
  T.kicker = (L, txt, x, y, col) => el(L, 'div', 'abs mono', { left: x + 'px', top: y + 'px', fontSize: '16px', color: col || T.HUD.DIM }, txt);

  /* ---------- T10 HUD Keynote ---------- */
  /* glowing S-curve with a comet that travels it; u 0..1 */
  T.curve = (L, x, y, w, h, col) => { const s = K.svg(L, w, h, x, y); const d = `M0 ${h} L${w * .32} ${h} C${w * .55} ${h} ${w * .5} 0 ${w * .78} 0 L${w} 0`;
    const glow = K.sv(s, 'path', { d, fill: 'none', stroke: col || '#fff', 'stroke-width': 10, opacity: .25, filter: 'blur(6px)' });
    const p = K.sv(s, 'path', { d, fill: 'none', stroke: col || '#fff', 'stroke-width': 4, 'stroke-linecap': 'round' });
    const len = p.getTotalLength(); [p, glow].forEach(q => { q.setAttribute('stroke-dasharray', len); q.setAttribute('stroke-dashoffset', len); });
    const cm = el(L, 'div', 'abs', { width: '26px', height: '26px', marginLeft: '-13px', marginTop: '-13px', borderRadius: '50%', background: 'radial-gradient(circle, #fff, ' + T.HUD.GOLD + ' 40%, rgba(245,184,61,0) 70%)', boxShadow: `0 0 40px 12px rgba(245,184,61,.5)` });
    return { s, p, glow, len, cm, x, y }; };
  T.curveAt = (c, u) => { u = clamp(u); const off = c.len * (1 - u); c.p.setAttribute('stroke-dashoffset', off); c.glow.setAttribute('stroke-dashoffset', off);
    const pt = c.p.getPointAtLength(c.len * u); c.cm.style.left = (c.x + pt.x) + 'px'; c.cm.style.top = (c.y + pt.y) + 'px'; c.cm.style.opacity = u > 0 ? 1 : 0; };
  /* rolling counter: digits roll to their value, other characters stay; with an underline bar */
  T.odometer = (L, text, x, y, size, col, bar) => { const o = { reels: [] }; const row = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', display: 'flex', alignItems: 'flex-end' }); o.row = row; const h = size * 1.05;
    for (const ch of String(text)) { if (/\d/.test(ch)) { const win = el(row, 'div', '', { position: 'relative', height: h + 'px', width: (size * .56) + 'px', overflow: 'hidden' }); const strip = el(win, 'div', 'abs', { left: 0, top: 0, width: '100%' });
        for (let n = 0; n <= 19; n++) el(strip, 'div', 'sans', { height: h + 'px', lineHeight: h + 'px', fontSize: size + 'px', fontWeight: 900, color: col || '#fff', textAlign: 'center' }, String(n % 10)); o.reels.push({ strip, d: +ch, h }); }
      else el(row, 'div', 'sans', { height: h + 'px', lineHeight: h + 'px', fontSize: (ch === '+' ? size * .5 : size) + 'px', fontWeight: 900, color: col || '#fff', padding: '0 4px' }, ch); }
    if (bar !== false) { o.bar = el(L, 'div', 'abs', { left: x + 'px', top: (y + h + 16) + 'px', height: '4px', width: '0px', background: T.HUD.BLUE, boxShadow: `0 0 14px ${T.HUD.BLUE}` }); o.barW = row.getBoundingClientRect ? 0 : 0; o.bw = String(text).length * size * .58; }
    return o; };
  T.odometerAt = (o, t, t0, d) => { o.reels.forEach((r, i) => { const u = ease.outExpo(P(t, t0 + i * .12, d || 1.2)); r.strip.style.transform = `translateY(${(-(u * (10 + r.d))) * r.h}px)`; });
    if (o.bar) o.bar.style.width = (o.bw * ease.out3(P(t, t0, d || 1.2))) + 'px'; };
  /* BREAKING tag */
  T.breaking = (L, x, y, txt) => { const b = el(L, 'div', 'abs mono', { left: x + 'px', top: y + 'px', fontSize: '15px', color: T.HUD.RED }, '●  ' + (txt || 'BREAKING · 01')); return b; };
  /* dotted globe (canvas) + gold orbit; T.globeAt(g, t) rotates it */
  T.globe = (L, cx, cy, r) => { const cv = el(L, 'canvas', 'abs', { left: (cx - r - 10) + 'px', top: (cy - r - 10) + 'px' }); cv.width = cv.height = 2 * r + 20;
    const pts = []; const N = 1400; for (let i = 0; i < N; i++) { const yy = 1 - (i / (N - 1)) * 2, rad = Math.sqrt(1 - yy * yy), th = i * 2.39996; pts.push([Math.cos(th) * rad, yy, Math.sin(th) * rad]); }
    const s = K.svg(L, 2 * r + 300, 2 * r, cx - r - 150, cy - r); const orb = K.sv(s, 'ellipse', { cx: r + 150, cy: r * .78, rx: r * 1.15, ry: r * .32, fill: 'none', stroke: T.HUD.GOLD, 'stroke-width': 3, opacity: .9, transform: `rotate(-12 ${r + 150} ${r * .78})` });
    const len = 2 * Math.PI * Math.sqrt((Math.pow(r * 1.15, 2) + Math.pow(r * .32, 2)) / 2); orb.setAttribute('stroke-dasharray', len); orb.setAttribute('stroke-dashoffset', len);
    return { cv, g: cv.getContext('2d'), pts, r, orb, len }; };
  T.globeAt = (G, t, orbitU) => { const { g, pts, r } = G, c = r + 10; g.clearRect(0, 0, G.cv.width, G.cv.height);
    const grd = g.createRadialGradient(c - r * .3, c - r * .3, r * .1, c, c, r); grd.addColorStop(0, 'rgba(60,80,140,.55)'); grd.addColorStop(1, 'rgba(10,12,24,.9)'); g.fillStyle = grd; g.beginPath(); g.arc(c, c, r, 0, 7); g.fill();
    const a = t * .35, ca = Math.cos(a), sa = Math.sin(a);
    for (const [x, y, z] of pts) { const X = x * ca + z * sa, Z = -x * sa + z * ca; if (Z < 0) continue; const land = Math.sin(x * 5.1 + 1) * Math.cos(y * 4.3) + Math.sin(z * 6.2) > .35;
      g.fillStyle = land ? `rgba(130,160,255,${.35 + .6 * Z})` : `rgba(90,110,180,${.08 + .12 * Z})`; g.fillRect(c + X * r - 1.5, c - y * r - 1.5, 3, 3); }
    G.orb.setAttribute('stroke-dashoffset', G.len * (1 - clamp(orbitU ?? 1))); };
  /* glowing orb (breathes) */
  T.orb = (L, cx, cy, r, col) => el(L, 'div', 'abs', { left: (cx - r) + 'px', top: (cy - r) + 'px', width: 2 * r + 'px', height: 2 * r + 'px', borderRadius: '50%', background: `radial-gradient(circle, #fff 0 18%, ${col || 'rgba(140,170,255,.9)'} 30%, rgba(80,110,255,0) 70%)`, transformOrigin: '50% 50%' });
  /* dashed file icon (text inside, e.g. "?" or ".eva") */
  T.fileIcon = (L, x, y, w, txt, solid) => { const h = w * 1.25; const s = K.svg(L, w, h, x, y);
    K.sv(s, 'path', { d: `M2 2 H${w * .68} L${w - 2} ${w * .32} V${h - 2} H2 Z`, fill: solid ? '#1c1f29' : 'none', stroke: solid ? 'rgba(255,255,255,.35)' : T.HUD.BLUE, 'stroke-width': 2, 'stroke-dasharray': solid ? '' : '7 6' });
    const t = el(L, 'div', 'abs sans', { left: x + 'px', top: (y + h * .38) + 'px', width: w + 'px', textAlign: 'center', fontSize: (w * .3) + 'px', fontWeight: 800, color: solid ? '#fff' : T.HUD.BLUE }, txt || '?'); return { s, t }; };
  /* big metallic title with a spark burst (canvas). T.metalAt(m, lt) */
  T.metal = (L, txt, y, size) => { const m = {}; m.t = K.center(el(L, 'div', 'abs sans', { top: y + 'px', fontSize: (size || 200) + 'px', fontWeight: 900, letterSpacing: '-.02em', background: 'linear-gradient(180deg,#ffffff 0%,#c9cfdc 45%,#6f7690 60%,#e7eaf2 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 0 30px rgba(140,160,255,.35))' }, txt));
    m.cv = el(L, 'canvas', 'abs', { left: 0, top: 0 }); m.cv.width = 1920; m.cv.height = 1080; m.g = m.cv.getContext('2d'); const R = C.rng(5); m.sp = [];
    for (let i = 0; i < 160; i++) { const a = R() * 6.283, v = 300 + R() * 900; m.sp.push([Math.cos(a) * v, Math.sin(a) * v * .6, .4 + R() * .8]); } m.cy = y + (size || 200) * .6; return m; };
  T.metalAt = (m, lt, t0) => { const u = lt - (t0 || 0); m.g.clearRect(0, 0, 1920, 1080); m.t.style.opacity = clamp(u * 3); m.t.style.transform = `scale(${1.25 - .25 * ease.outExpo(clamp(u / .8))})`; m.t.style.transformOrigin = '50% 50%';
    if (u < 0 || u > 1.6) return; for (const [vx, vy, l] of m.sp) { const k = clamp(u / l); if (k >= 1) continue; const x = 960 + vx * k, y = m.cy + vy * k; m.g.strokeStyle = `rgba(200,215,255,${1 - k})`; m.g.lineWidth = 2; m.g.beginPath(); m.g.moveTo(x, y); m.g.lineTo(x - vx * .05, y - vy * .05); m.g.stroke(); } };
  /* file tree / list panel rows: T.rows(L, x, y, [['icon','scenes.js','small note'], ...]) */
  T.rows = (L, x, y, items, w) => items.map((it, i) => { const r = el(L, 'div', 'abs', { left: (x + (i ? 24 : 0)) + 'px', top: (y + i * 90) + 'px', width: (w || 560) + 'px', height: '72px', borderRadius: '10px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.12)' });
    el(r, 'div', 'abs', { left: '18px', top: '18px', fontSize: '30px', fontFamily: "'Noto Color Emoji'" }, it[0]); el(r, 'div', 'abs sans', { left: '70px', top: '10px', fontSize: '28px', fontWeight: 700, color: '#fff' }, it[1]); el(r, 'div', 'abs cn', { left: '70px', top: '44px', fontSize: '16px', fontWeight: 400, color: T.HUD.DIM }, it[2] || '');
    el(r, 'div', 'abs', { right: '20px', top: '28px', width: '14px', height: '14px', borderRight: '2px solid ' + T.HUD.DIM, borderBottom: '2px solid ' + T.HUD.DIM, transform: 'rotate(-45deg)' }); K.O(r); return r; });
  /* VS block: left (locked, faded) vs right content */
  T.vs = (L, x, y, leftTxt) => { const v = {}; v.l = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: '220px', height: '260px', borderRadius: '16px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.12)' });
    el(v.l, 'div', 'abs sans', { left: '20px', top: '18px', fontSize: '30px', fontWeight: 900, color: '#fff' }, leftTxt || 'MP4'); el(v.l, 'div', 'abs', { left: '80px', top: '120px', fontSize: '60px', fontFamily: "'Noto Color Emoji'" }, '🔒');
    v.vs = el(L, 'div', 'abs sans', { left: (x + 270) + 'px', top: (y + 100) + 'px', fontSize: '48px', fontWeight: 900, color: T.HUD.DIM }, 'VS'); return v; };

  /* ---------- T11 HUD Dashboard ---------- */
  /* process flow: icon tiles joined by arrows. T.flowAt(f, t, t0, step) */
  T.flow = (L, x, y, nodes, gap) => { const f = { n: [], a: [] }; gap = gap || 260;
    nodes.forEach(([ic, lab, col], i) => { const n = el(L, 'div', 'abs', { left: (x + i * gap) + 'px', top: y + 'px', width: '170px', height: '156px', borderRadius: '20px', background: T.HUD.PANEL, border: `1px solid ${col || 'rgba(255,255,255,.18)'}`, transformOrigin: '50% 50%' });
      el(n, 'div', 'abs', { left: 0, width: '170px', top: '16px', textAlign: 'center', fontSize: '58px', fontFamily: "'Noto Color Emoji'" }, ic); el(n, 'div', 'abs cn', { left: 0, width: '170px', top: '98px', textAlign: 'center', fontSize: '30px', color: col || '#fff' }, lab); f.n.push(n);
      if (i < nodes.length - 1) f.a.push(el(L, 'div', 'abs sans', { left: (x + i * gap + 186) + 'px', top: (y + 50) + 'px', fontSize: '44px', color: T.HUD.DIM }, '→')); }); return f; };
  T.flowAt = (f, t, t0, step) => { f.n.forEach((n, i) => tf(n, pop(t, t0 + i * (step || .5), .35, 1.7))); f.a.forEach((a, i) => tf(a, slide(t, t0 + i * (step || .5) + .25, .3, -20, 0))); };
  /* gauge with needle and % number */
  T.gauge = (L, cx, cy, r, label) => { const g = {}; const s = K.svg(L, 2 * r + 40, r + 40, cx - r - 20, cy - r - 20); g.r = r;
    const arc = (a0, a1) => { const p = a => [r + 20 + r * Math.cos(a), r + 20 + r * Math.sin(a)]; const [x0, y0] = p(a0), [x1, y1] = p(a1); return `M${x0} ${y0} A${r} ${r} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${x1} ${y1}`; };
    K.sv(s, 'path', { d: arc(Math.PI, 2 * Math.PI - .001), fill: 'none', stroke: 'rgba(255,255,255,.12)', 'stroke-width': 18, 'stroke-linecap': 'round' });
    g.p = K.sv(s, 'path', { d: arc(Math.PI, 2 * Math.PI - .001), fill: 'none', stroke: T.HUD.BLUE, 'stroke-width': 18, 'stroke-linecap': 'round' }); g.len = Math.PI * r; g.p.setAttribute('stroke-dasharray', g.len); g.p.setAttribute('stroke-dashoffset', g.len);
    g.nd = el(L, 'div', 'abs', { left: cx + 'px', top: (cy - 3) + 'px', width: (r * .9) + 'px', height: '6px', borderRadius: '3px', background: '#fff', transformOrigin: '0 50%' }); el(L, 'div', 'abs', { left: (cx - 9) + 'px', top: (cy - 9) + 'px', width: '18px', height: '18px', borderRadius: '50%', background: '#fff' });
    g.n = el(L, 'div', 'abs disp', { left: (cx - 200) + 'px', width: '400px', textAlign: 'center', top: (cy - r * .55) + 'px', fontSize: (r * .55) + 'px', color: T.HUD.GOLD }, ''); g.l = T.kicker(L, label || '', cx - r, cy - r - 60); return g; };
  T.gaugeAt = (g, u, val, suffix) => { u = clamp(u); g.p.setAttribute('stroke-dashoffset', g.len * (1 - u)); g.nd.style.transform = `rotate(${180 + 180 * u}deg)`; g.n.textContent = u > .02 ? Math.round(val * u) + (suffix ?? '%') : ''; };
  /* timer box mm:ss counting to target seconds */
  T.timer = (L, x, y) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: '220px', height: '96px', borderRadius: '14px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.16)' }); b.n = el(b, 'div', 'abs sans', { left: 0, width: '220px', top: '20px', textAlign: 'center', fontSize: '48px', fontWeight: 800, color: '#fff' }, '00:00'); return b; };
  T.timerAt = (b, sec) => { sec = Math.max(0, Math.round(sec)); b.n.textContent = String(Math.floor(sec / 60)).padStart(2, '0') + ':' + String(sec % 60).padStart(2, '0'); };
  /* quote card */
  T.quote = (L, txt, x, y, hi) => el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: '34px', color: '#fff', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.16)', borderRadius: '14px', padding: '18px 28px' }, `“${txt.replace(hi || '\u0000', `<span style="color:${T.HUD.GOLD}">${hi}</span>`)}”`);
  /* chips that tick on with a green check: T.checksAt(c, t, t0, step) */
  T.checks = (L, x, y, names, w) => names.map((nm, i) => { const c = el(L, 'div', 'abs sans', { left: (x + i * ((w || 200) + 24)) + 'px', top: y + 'px', width: (w || 200) + 'px', height: '72px', lineHeight: '72px', textAlign: 'center', borderRadius: '12px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.16)', fontSize: '28px', fontWeight: 800, color: '#fff', transformOrigin: '50% 50%' }, nm);
    c.ck = el(c, 'div', 'abs', { right: '-10px', top: '-10px', width: '24px', height: '24px', borderRadius: '50%', background: T.HUD.GREEN, color: '#fff', fontSize: '15px', lineHeight: '24px', textAlign: 'center', transformOrigin: '50% 50%' }, '✓'); return c; });
  T.checksAt = (cs, t, t0, step, gold) => cs.forEach((c, i) => { tf(c, pop(t, t0 + i * (step || .35), .3, 1.6)); tf(c.ck, pop(t, t0 + i * (step || .35) + .25, .25, 2.4)); if (gold !== undefined) c.style.borderColor = t > gold ? T.HUD.GOLD : 'rgba(255,255,255,.16)'; });
  /* timeline block rows (an editing timeline) */
  T.timeline = (L, x, y, w, rows) => { const p = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: (60 + rows * 36) + 'px', borderRadius: '14px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.12)', overflow: 'hidden' });
    ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => el(p, 'div', 'abs', { left: (16 + i * 20) + 'px', top: '14px', width: '11px', height: '11px', borderRadius: '50%', background: c })); const R = C.rng(9);
    for (let r = 0; r < rows; r++) { let xx = 16; while (xx < w - 40) { const bw = 18 + R() * 30; el(p, 'div', 'abs', { left: xx + 'px', top: (50 + r * 36) + 'px', width: bw + 'px', height: '26px', borderRadius: '4px', background: r % 2 ? '#c99a2e' : '#5b4bd6' }); xx += bw + 5; } } return p; };
  /* big red X stamp */
  T.xStamp = (L, cx, cy, s) => el(L, 'div', 'abs sans', { left: (cx - s / 2) + 'px', top: (cy - s * .62) + 'px', width: s + 'px', textAlign: 'center', fontSize: s + 'px', fontWeight: 900, color: T.HUD.RED, lineHeight: 1, transformOrigin: '50% 50%', textShadow: '0 0 30px rgba(255,77,77,.5)' }, '✕');
  /* grid that fills cell by cell */
  T.grid = (L, x, y, cols, rows, cell) => { const g = []; for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) g.push(el(L, 'div', 'abs', { left: (x + c * (cell + 4)) + 'px', top: (y + r * (cell + 4)) + 'px', width: cell + 'px', height: cell + 'px', borderRadius: '3px', background: 'rgba(255,255,255,.06)' })); return g; };
  T.gridAt = (g, u, col) => { const R = C.rng(3), ord = g.map((_, i) => [R(), i]).sort((a, b) => a[0] - b[0]); const n = Math.floor(clamp(u) * g.length); ord.forEach(([, i], k) => g[i].style.background = k < n ? (col || T.HUD.BLUE) : 'rgba(255,255,255,.06)'); };
  /* comparison bars: [[label, value 0..1, colour], ...] */
  T.bars = (L, x, y, w, items) => items.map(([lab, v, col], i) => { el(L, 'div', 'abs cn', { left: x + 'px', top: (y + i * 44) + 'px', fontSize: '20px', color: T.HUD.DIM }, lab); el(L, 'div', 'abs', { left: (x + 260) + 'px', top: (y + 6 + i * 44) + 'px', width: w + 'px', height: '14px', borderRadius: '7px', background: 'rgba(255,255,255,.08)' });
    const b = el(L, 'div', 'abs', { left: (x + 260) + 'px', top: (y + 6 + i * 44) + 'px', width: '0px', height: '14px', borderRadius: '7px', background: col || T.HUD.BLUE }); b.v = v * w; return b; });
  T.barsAt = (bs, t, t0) => bs.forEach((b, i) => b.style.width = (b.v * ease.out3(P(t, t0 + i * .2, .8))) + 'px');
  /* toggle switch + slider (LOW / MID / HIGH) */
  T.toggle = (L, x, y, label) => { const o = {}; o.p = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: '460px', height: '80px', borderRadius: '14px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.14)' });
    el(o.p, 'div', 'abs cn', { left: '24px', top: '20px', fontSize: '30px', color: '#fff' }, label); o.tr = el(o.p, 'div', 'abs', { right: '24px', top: '22px', width: '72px', height: '36px', borderRadius: '18px', background: 'rgba(255,255,255,.15)' }); o.k = el(o.tr, 'div', 'abs', { left: '4px', top: '4px', width: '28px', height: '28px', borderRadius: '50%', background: '#fff' }); return o; };
  T.toggleAt = (o, u) => { u = ease.io3(clamp(u)); o.k.style.left = (4 + 36 * u) + 'px'; o.tr.style.background = u > .5 ? T.HUD.BLUE : 'rgba(255,255,255,.15)'; };
  T.slider = (L, x, y, label, steps) => { const o = { steps: steps || ['LOW', 'MID', 'HIGH'] }; o.p = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: '460px', height: '96px', borderRadius: '14px', background: T.HUD.PANEL, border: '1px solid rgba(255,255,255,.14)' });
    el(o.p, 'div', 'abs cn', { left: '24px', top: '14px', fontSize: '26px', color: '#fff' }, label); o.v = el(o.p, 'div', 'abs sans', { right: '24px', top: '14px', fontSize: '24px', fontWeight: 800, color: '#fff' }, o.steps[0]);
    el(o.p, 'div', 'abs', { left: '24px', top: '66px', width: '412px', height: '4px', background: 'rgba(255,255,255,.15)' }); o.f = el(o.p, 'div', 'abs', { left: '24px', top: '66px', width: '0px', height: '4px', background: `linear-gradient(90deg, ${T.HUD.BLUE}, ${T.HUD.GOLD})` }); o.k = el(o.p, 'div', 'abs', { left: '16px', top: '60px', width: '16px', height: '16px', borderRadius: '50%', background: '#fff' }); return o; };
  T.sliderAt = (o, u) => { u = clamp(u); o.f.style.width = 412 * u + 'px'; o.k.style.left = (16 + 412 * u) + 'px'; o.v.textContent = o.steps[Math.min(o.steps.length - 1, Math.round(u * (o.steps.length - 1)))]; o.v.style.color = u > .9 ? T.HUD.GOLD : '#fff'; };
  /* two rising lines that track each other */
  T.lines = (L, x, y, w, h, labels) => { const s = K.svg(L, w, h, x, y); K.sv(s, 'line', { x1: 0, y1: h, x2: w, y2: h, stroke: 'rgba(255,255,255,.2)' }); K.sv(s, 'line', { x1: 0, y1: 0, x2: 0, y2: h, stroke: 'rgba(255,255,255,.2)' });
    const mk = (dy, col) => { const p = K.sv(s, 'path', { d: `M0 ${h - 10 + dy} C${w * .45} ${h - 10 + dy} ${w * .55} ${10 + dy} ${w} ${10 + dy}`, fill: 'none', stroke: col, 'stroke-width': 4 }); const l = p.getTotalLength(); p.setAttribute('stroke-dasharray', l); p.setAttribute('stroke-dashoffset', l); p.l = l; return p; };
    const o = { a: mk(0, T.HUD.BLUE), b: mk(10, T.HUD.GOLD) }; (labels || []).forEach((t, i) => el(L, 'div', 'abs cn', { left: (x + w + 14) + 'px', top: (y + i * 30) + 'px', fontSize: '18px', color: i ? T.HUD.GOLD : T.HUD.BLUE }, t)); return o; };
  T.linesAt = (o, u) => { [o.a, o.b].forEach(p => p.setAttribute('stroke-dashoffset', p.l * (1 - clamp(u)))); };
  /* terminal with typed lines: T.terminalAt(term, t, t0) */
  T.terminal = (L, x, y, w, lines) => { const p = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: (100 + lines.length * 48) + 'px', borderRadius: '14px', background: '#0d0f14', border: '1px solid rgba(255,255,255,.14)' });
    ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => el(p, 'div', 'abs', { left: (18 + i * 20) + 'px', top: '16px', width: '11px', height: '11px', borderRadius: '50%', background: c }));
    p.ls = lines.map((t, i) => { const d = el(p, 'div', 'abs mono', { left: '24px', top: (54 + i * 48) + 'px', fontSize: '30px', letterSpacing: '0', textTransform: 'none', color: i ? '#9fe6b4' : '#fff' }, ''); d.full = t; return d; }); return p; };
  T.terminalAt = (p, t, t0, cps) => { let tt = t - t0; p.ls.forEach(d => { const n = Math.max(0, Math.min(d.full.length, Math.floor(tt * (cps || 22)))); d.textContent = d.full.slice(0, n) + (n > 0 && n < d.full.length ? '▌' : ''); tt -= d.full.length / (cps || 22) + .25; }); };
  /* gold stamp (BETA / NEW) */
  T.goldStamp = (L, txt, x, y) => el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: '44px', color: T.HUD.GOLD, border: `3px solid ${T.HUD.GOLD}`, borderRadius: '8px', padding: '4px 18px', transform: 'rotate(-6deg)', boxShadow: '0 0 24px rgba(245,184,61,.35)', transformOrigin: '50% 50%' }, txt);
  /* version counter V1 → Vn over a tick ruler */
  T.version = (L, x, y) => { const v = el(L, 'div', 'abs disp', { left: x + 'px', top: y + 'px', fontSize: '150px', color: '#fff' }, 'V1'); el(L, 'div', 'abs', { left: x + 'px', top: (y + 170) + 'px', width: '1200px', height: '30px', backgroundImage: 'repeating-linear-gradient(90deg, rgba(255,255,255,.25) 0 2px, transparent 2px 16px)' }); return v; };
  T.versionAt = (v, u, from, to) => { v.textContent = 'V' + Math.round(lerp(from || 1, to || 8, ease.io3(clamp(u)))); };

  /* ---------- T08 Neon Explainer ---------- */
  T.NEON = { CREAM: '#fff3c4', GLOW: '0 0 8px rgba(255,236,150,.9), 0 0 24px rgba(255,214,90,.7), 0 0 60px rgba(255,190,60,.45)', PINK: '#ff4fd8', VIO: '#7b3cff' };
  /* colour grade over full-bleed Eva: violet/magenta "neon room" wash (z above Eva) */
  T.neonGrade = L => { el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: 'radial-gradient(900px 700px at 18% 20%, rgba(255,60,200,.55), rgba(0,0,0,0) 60%), radial-gradient(1100px 800px at 85% 15%, rgba(110,60,255,.55), rgba(0,0,0,0) 65%), linear-gradient(rgba(40,10,90,.35), rgba(10,0,30,.55))', mixBlendMode: 'soft-light' });
    return el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: 'radial-gradient(1300px 900px at 50% 45%, rgba(0,0,0,0) 55%, rgba(10,0,25,.55))' }); };
  /* glowing cream text */
  T.glow = (L, txt, x, y, size, extra) => el(L, 'div', 'abs cn', Object.assign({ left: x + 'px', top: y + 'px', fontSize: size + 'px', color: T.NEON.CREAM, textShadow: T.NEON.GLOW, fontStyle: 'italic' }, extra || {}), txt);
  /* pixel text: drawn tiny on a canvas, scaled up with hard pixels (works for Chinese) */
  T.pixel = (L, txt, cy, size, col) => { const sm = Math.round(size / 10), cv = document.createElement('canvas'), g = cv.getContext('2d'); g.font = `900 ${sm}px 'Noto Sans CJK SC'`; const w = Math.ceil(g.measureText(txt).width) + 4; cv.width = w; cv.height = sm + 6;
    g.font = `900 ${sm}px 'Noto Sans CJK SC'`; g.fillStyle = col || T.NEON.CREAM; g.textBaseline = 'top'; g.fillText(txt, 2, 2); const img = el(L, 'img', 'abs', { imageRendering: 'pixelated', width: (w * 10) + 'px', height: ((sm + 6) * 10) + 'px', left: (960 - w * 5) + 'px', top: (cy - (sm + 6) * 5) + 'px', filter: `drop-shadow(0 0 18px rgba(255,214,90,.7))`, transformOrigin: '50% 50%' }); img.src = cv.toDataURL(); return img; };
  /* echo stack: the same word repeated, centre line bright, others fading */
  T.echo = (L, txt, size, n) => { const box = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' }); const rows = [];
    for (let i = -n; i <= n; i++) rows.push(K.center(el(box, 'div', 'abs', { top: (540 - size * .6 + i * size * 1.1) + 'px', fontSize: size + 'px', fontStyle: 'italic', fontWeight: 900, fontFamily: "'Inter','Noto Sans CJK SC'", color: i ? 'rgba(255,243,196,0)' : T.NEON.CREAM, WebkitTextStroke: i ? '1.5px rgba(255,243,196,' + (.65 - Math.abs(i) * .12) + ')' : '0', textShadow: i ? 'none' : T.NEON.GLOW }, txt))); box.rows = rows; return box; };
  /* article card with a highlighter sweep over the key phrase */
  T.article = (L, x, y, w, pre, hi, post, src) => { const a = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', background: '#f7f7f5', borderRadius: '10px', padding: '40px 46px', boxShadow: '0 40px 90px rgba(0,0,0,.5)', fontFamily: "Georgia,'Noto Serif CJK SC',serif", fontSize: '84px', lineHeight: 1.25, color: '#1a1a1a' });
    if (src) el(a, 'div', 'mono', { fontSize: '16px', color: '#888', marginBottom: '18px', letterSpacing: '.12em' }, src);
    const body = el(a, 'div', '', {}); body.innerHTML = `${pre} <span class="hl" style="background:linear-gradient(#ffe74a,#ffe74a) no-repeat 0 60%/0% 70%;padding:0 6px;border-radius:6px">${hi}</span> ${post}`; a.hl = body.querySelector('.hl'); return a; };
  T.articleAt = (a, u) => { a.hl.style.backgroundSize = (100 * ease.out3(clamp(u))) + '% 85%'; };
  /* floating screenshot collage around Eva: real images only */
  T.collage = (L, srcs, spots) => srcs.map((src, i) => { const [x, y, w, r] = spots[i % spots.length]; const c = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', borderRadius: '10px', overflow: 'hidden', boxShadow: '0 24px 60px rgba(0,0,0,.55)', border: '3px solid #fff', transform: `rotate(${r}deg)`, transformOrigin: '50% 50%' }); const im = el(c, 'img', '', { display: 'block', width: '100%' }); C.setSrc(im, src); c.r = r; return c; });
  T.collageAt = (cs, t, t0, step) => cs.forEach((c, i) => { const p = pop(t, t0 + i * (step || .18), .35, 1.8); tf(c, { s: p.s, o: p.o, r: c.r }); });
  /* white speech bubble with typed question + emoji */
  T.bubble = (L, txt, x, y, w, emoji) => { const b = {}; b.box = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', minHeight: '190px', background: '#fff', border: '4px solid #222', borderRadius: '34px', padding: '42px 50px', transformOrigin: '20% 100%' });
    b.t = el(b.box, 'div', 'cn', { fontSize: '80px', color: '#111', whiteSpace: 'nowrap', fontStyle: 'italic' }, ''); b.full = txt;
    const s = K.svg(L, 140, 120, x + w - 180, y + 186); K.sv(s, 'path', { d: 'M0 0 L120 100 L60 0', fill: '#fff', stroke: '#222', 'stroke-width': 4 }); el(L, 'div', 'abs', { left: (x + w - 220) + 'px', top: (y + 172) + 'px', width: '200px', height: '12px', background: '#fff' });
    b.e = K.emoji(L, emoji || '🤔', 190, x + w - 10, y + 190); return b; };
  T.bubbleAt = (b, t, t0, cps) => { tf(b.box, pop(t, t0, .4, 1.6)); const n = Math.max(0, Math.min(b.full.length, Math.floor((t - t0 - .3) * (cps || 10)))); b.t.textContent = b.full.slice(0, n); tf(b.e, pop(t, t0 + .5, .4, 2.2)); };
  /* dashed slot boxes that get filled ("SKILL 1 / 2 / 3") */
  T.slots = (L, x, y, labels, words, w) => labels.map((lab, i) => { const s = el(L, 'div', 'abs', { left: (x + i * ((w || 260) + 40)) + 'px', top: y + 'px', width: (w || 260) + 'px', height: '150px', border: '3px dashed rgba(255,255,255,.75)', borderRadius: '10px', transformOrigin: '50% 50%' });
    el(s, 'div', 'abs cn', { left: '50%', top: '-22px', transform: 'translateX(-50%)', background: '#000', padding: '0 10px', fontSize: '26px', color: '#d4ff2e' }, lab); s.w = el(s, 'div', 'abs cn', { left: 0, width: '100%', top: '32px', textAlign: 'center', fontSize: '76px', color: '#fff' }, words[i] || ''); s.w.style.transformOrigin = '50% 50%'; return s; });
  T.slotsAt = (ss, t, t0, fillT) => ss.forEach((s, i) => { tf(s, pop(t, t0, .35, 1.5)); tf(s.w, pop(t, fillT[i] ?? 99, .3, 2)); });
  /* orange-bordered tag with white bullet chips under it */
  T.tag = (L, title, x, y, bullets) => { const g = { b: [] }; g.h = el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: '44px', color: '#fff', border: '2px solid #ff7a4a', borderRadius: '8px', padding: '2px 14px', transformOrigin: '0 50%' }, title);
    bullets.forEach((t, i) => g.b.push(el(L, 'div', 'abs cn', { left: x + 'px', top: (y + 86 + i * 58) + 'px', fontSize: '34px', color: '#111', background: '#fff', padding: '2px 12px', borderRadius: '4px', transformOrigin: '0 50%' }, '· ' + t))); return g; };
  T.tagAt = (g, t, t0, step) => { tf(g.h, pop(t, t0, .3, 1.8)); g.b.forEach((b, i) => tf(b, slide(t, t0 + .4 + i * (step || .5), .3, -30, 0))); };
  T.dotsBg = '#050507';

  /* ---------- T12 Old Newspaper ---------- */
  T.NEWS = { PAPER: '#e8dcc0', AGED: '#d6c6a0', INK: '#1c1814', RED: '#c4232b', DARK: '#211b15', SERIF: "'Noto Serif CJK SC','Noto Serif CJK JP',Georgia,serif", TYPE: "'Courier 10 Pitch',Courier,monospace",
    BW: 'grayscale(1) contrast(1.35) brightness(.95) sepia(.25)' };
  /* aged-paper background: newsprint with stains and vignette; dark=true gives the cork/desk wall */
  T.newsBg = dark => dark ? 'radial-gradient(1100px 700px at 50% 45%, #4a3c2c, #1a140f 75%)' : 'radial-gradient(1200px 800px at 45% 40%, #efe5cc, #d9c9a3 70%, #b9a47a 100%)';
  /* film-grain overlay (canvas noise); T.grainAt(g, t) jitters it every frame */
  T.grain = (L, op) => { const cv = el(L, 'canvas', 'abs', { left: '-40px', top: '-40px', opacity: op ?? .18, mixBlendMode: 'multiply', zIndex: 80, pointerEvents: 'none' }); cv.width = 1000; cv.height = 580; cv.style.width = '2000px'; cv.style.height = '1160px';
    const g = cv.getContext('2d'), im = g.createImageData(1000, 580), R = C.rng(11); for (let i = 0; i < im.data.length; i += 4) { const v = 120 + R() * 135; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } g.putImageData(im, 0, 0); return cv; };
  T.grainAt = (cv, t) => { const f = Math.floor(t * 30); cv.style.transform = `translate(${(f * 37) % 40 - 20}px,${(f * 53) % 40 - 20}px)`; };
  /* masthead: paper name, double rules, issue line */
  T.masthead = (L, name, issue, x, y, w) => { const m = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', textAlign: 'center', color: T.NEWS.INK });
    el(m, 'div', '', { borderTop: `6px solid ${T.NEWS.INK}`, borderBottom: `2px solid ${T.NEWS.INK}`, height: '12px' });
    el(m, 'div', '', { fontFamily: T.NEWS.SERIF, fontWeight: 900, fontSize: '96px', lineHeight: 1.1, letterSpacing: '.04em', padding: '6px 0' }, name);
    el(m, 'div', '', { borderTop: `2px solid ${T.NEWS.INK}`, borderBottom: `2px solid ${T.NEWS.INK}`, fontFamily: T.NEWS.TYPE, fontSize: '20px', padding: '6px 0', letterSpacing: '.12em' }, issue); return m; };
  /* columns of greyed text lines (layout texture only, never readable fake text) */
  T.columns = (L, x, y, w, h, cols, seed) => { const box = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', display: 'flex', gap: '26px' }); const R = C.rng(seed || 2);
    for (let c = 0; c < cols; c++) { const col = el(box, 'div', '', { flex: 1, borderLeft: c ? `1px solid rgba(28,24,20,.35)` : 'none', paddingLeft: c ? '20px' : 0 });
      for (let y2 = 0; y2 < h - 20; y2 += 22) el(col, 'div', '', { height: '9px', marginBottom: '13px', width: (y2 % 154 === 132 ? 40 + R() * 30 : 88 + R() * 12) + '%', background: 'rgba(28,24,20,.28)', borderRadius: '2px' }); } return box; };
  /* headline in heavy serif */
  T.headline = (L, txt, x, y, size, col) => el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: T.NEWS.SERIF, fontWeight: 900, fontSize: size + 'px', lineHeight: 1.15, color: col || T.NEWS.INK, whiteSpace: 'nowrap' }, txt);
  /* torn-edge photo card (real image), b/w halftone, with tape strips */
  T.photo = (L, src, x, y, w, h, rot) => { const c = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: '#f3ecdc', padding: '12px', transform: `rotate(${rot || 0}deg)`, transformOrigin: '50% 50%', boxShadow: '0 18px 40px rgba(0,0,0,.45)',
      clipPath: 'polygon(0 2%,6% 0,14% 2%,25% 0,38% 1.5%,52% 0,66% 2%,79% 0,91% 1.5%,100% 0,99% 20%,100% 42%,98.5% 63%,100% 84%,99% 100%,86% 98%,71% 100%,57% 98.5%,43% 100%,28% 98%,15% 100%,3% 98.5%,0 100%,1.5% 78%,0 55%,1% 31%)' });
    const im = el(c, 'img', '', { width: '100%', height: '100%', objectFit: 'cover', display: 'block', filter: T.NEWS.BW }); C.setSrc(im, src);
    el(c, 'div', 'abs', { left: '12px', top: '12px', right: '12px', bottom: '12px', backgroundImage: 'radial-gradient(rgba(0,0,0,.35) 1px, transparent 1.6px)', backgroundSize: '5px 5px', mixBlendMode: 'multiply' }); c.r = rot || 0; c.im = im; return c; };
  T.tape = (L, x, y, w, rot) => el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: (w || 120) + 'px', height: '34px', background: 'rgba(235,225,195,.75)', transform: `rotate(${rot || -8}deg)`, boxShadow: '0 2px 6px rgba(0,0,0,.2)' });
  /* film strip with sprocket holes, frames are real images */
  T.filmstrip = (L, x, y, srcs, fw, rot) => { const fh = fw * .5625, s = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', height: (fh + 56) + 'px', background: '#111', padding: '28px 14px', display: 'flex', gap: '12px', transform: `rotate(${rot || 0}deg)`, transformOrigin: '0 50%', boxShadow: '0 20px 50px rgba(0,0,0,.5)',
      backgroundImage: 'radial-gradient(circle at 50% 50%, #e8dcc0 0 5px, transparent 6px), radial-gradient(circle at 50% 50%, #e8dcc0 0 5px, transparent 6px)', backgroundSize: '26px 20px, 26px 20px', backgroundPosition: '0 2px, 0 calc(100% - 2px)', backgroundRepeat: 'repeat-x' });
    s.fr = srcs.map(src => { const im = el(s, 'img', '', { width: fw + 'px', height: fh + 'px', objectFit: 'cover', filter: T.NEWS.BW, flex: 'none' }); C.setSrc(im, src); return im; }); return s; };
  /* red brush banner stamp */
  T.brush = (L, txt, x, y, size, rot) => el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: T.NEWS.SERIF, fontWeight: 900, fontSize: size + 'px', color: '#fff', background: T.NEWS.RED, padding: '.1em .5em', transform: `rotate(${rot ?? -8}deg)`, transformOrigin: '50% 50%', boxShadow: '0 12px 30px rgba(0,0,0,.4)', whiteSpace: 'nowrap',
      clipPath: 'polygon(1% 8%,8% 0,30% 5%,55% 0,80% 6%,99% 0,97% 30%,100% 62%,98% 100%,70% 94%,45% 100%,20% 93%,0 100%,3% 60%,0 35%)', textShadow: '2px 2px 0 rgba(0,0,0,.25)' }, txt);
  /* hand-drawn red scribbles: kind arrow | bolt | circle | x | underline. T.scribbleAt(s, u) draws it */
  T.scribble = (L, kind, x, y, size, col, rot) => { const s = K.svg(L, size, size, x, y); s.style.transform = `rotate(${rot || 0}deg)`; s.style.overflow = 'visible';
    const D = { arrow: `M5 ${size * .8} C${size * .3} ${size * .7} ${size * .55} ${size * .45} ${size * .9} ${size * .12} M${size * .62} ${size * .1} L${size * .92} ${size * .1} L${size * .88} ${size * .42}`,
      bolt: `M${size * .55} 4 L${size * .25} ${size * .52} L${size * .55} ${size * .5} L${size * .35} ${size - 4}`, circle: `M${size * .9} ${size * .45} C${size * .95} ${size * .1} ${size * .1} ${size * .02} ${size * .06} ${size * .45} C${size * .02} ${size * .9} ${size * .92} ${size * .98} ${size * .95} ${size * .4} L${size * .85} ${size * .2}`,
      x: `M${size * .1} ${size * .1} L${size * .9} ${size * .9} M${size * .88} ${size * .12} L${size * .12} ${size * .88}`, underline: `M4 ${size * .5} C${size * .3} ${size * .44} ${size * .6} ${size * .56} ${size - 4} ${size * .46}` };
    const p = K.sv(s, 'path', { d: D[kind] || D.arrow, fill: 'none', stroke: col || T.NEWS.RED, 'stroke-width': Math.max(5, size / 22), 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); p.l = p.getTotalLength(); p.setAttribute('stroke-dasharray', p.l); p.setAttribute('stroke-dashoffset', p.l); s.p = p; return s; };
  T.scribbleAt = (s, u) => s.p.setAttribute('stroke-dashoffset', s.p.l * (1 - clamp(u)));
  /* typewriter text on a paper slip */
  T.typed = (L, txt, x, y, size, col) => { const d = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: T.NEWS.TYPE, fontSize: size + 'px', color: col || T.NEWS.INK, whiteSpace: 'nowrap' }, ''); d.full = txt; return d; };
  T.typedAt = (d, t, t0, cps) => { const n = Math.max(0, Math.min(d.full.length, Math.floor((t - t0) * (cps || 14)))); d.textContent = d.full.slice(0, n) + (t > t0 && n < d.full.length && Math.floor(t * 4) % 2 ? '_' : ''); };
  /* red book-cover block with vertical serif title */
  T.cover = (L, txt, x, y, w, h) => { const c = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: T.NEWS.RED, boxShadow: '0 30px 60px rgba(0,0,0,.45)', transformOrigin: '0 50%' });
    el(c, 'div', 'abs', { left: '50%', top: '40px', transform: 'translateX(-50%)', writingMode: 'vertical-rl', fontFamily: T.NEWS.SERIF, fontWeight: 900, fontSize: (w * .3) + 'px', color: '#f3e6cf', letterSpacing: '.15em', border: '2px solid rgba(243,230,207,.6)', padding: '14px 8px' }, txt); return c; };
  /* small caption label under a photo: mono role + serif note */
  T.caption = (L, role, note, x, y, col) => { const d = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', color: col || '#d9cdb2' }); el(d, 'div', 'mono', { fontSize: '15px', letterSpacing: '.2em' }, role); el(d, 'div', '', { fontFamily: T.NEWS.SERIF, fontSize: '20px', opacity: .8 }, note); return d; };

  /* ---------- T13 Tech Blue (Information-Technology deck look) ---------- */
  T.TECH = { BG0: '#0d4fd0', BG1: '#06297a', BG2: '#021335', CYAN: '#62f0ff', LINE: '#2f8dff', BAR: '#1f6bff', WHITE: '#ffffff', DIM: 'rgba(220,235,255,.72)',
    SERIF: "'Noto Serif CJK SC','Noto Serif CJK JP',Georgia,serif", SANS: "'Inter','Noto Sans CJK SC',sans-serif" };
  T.techBg = `radial-gradient(1100px 700px at 50% 50%, ${'#0d4fd0'}, ${'#06297a'} 55%, ${'#021335'} 100%)`;
  /* full-frame HUD outline: chamfered inner frame, detached corner strokes, blue tabs top-left, dash ladder left, cyan bars right, barcode bottom.
     T.techFrameAt(f, u) draws it in (0..1). opts {inset, tabs, ladder, barcode} */
  T.techFrame = (L, opts) => { const o = Object.assign({ x: 90, y: 110, w: 1720, h: 880, tabs: true, ladder: true, barcode: true, right: true }, opts || {}); const f = { parts: [] };
    const s = K.svg(L, 1920, 1080, 0, 0); const { x, y, w, h } = o, c = 34;
    const line = (d, wdt, col) => { const p = K.sv(s, 'path', { d, fill: 'none', stroke: col || T.TECH.LINE, 'stroke-width': wdt || 3, 'stroke-linejoin': 'round' }); p.l = p.getTotalLength(); p.setAttribute('stroke-dasharray', p.l); p.setAttribute('stroke-dashoffset', p.l); f.parts.push(p); return p; };
    line(`M${x + 420} ${y} L${x + w - c - 160} ${y} L${x + w - c - 130} ${y + 22} L${x + w - c} ${y + 22} L${x + w} ${y + 22 + c} L${x + w} ${y + h - c} L${x + w - c} ${y + h} L${x + 180} ${y + h} L${x + 150} ${y + h - 22} L${x} ${y + h - 22} L${x} ${y + 60} L${x + 30} ${y + 30}`, 3);
    line(`M${x + w - 220} ${y - 38} L${x + w + 40} ${y - 38} L${x + w + 70} ${y - 8}`, 3, T.TECH.LINE);
    line(`M${x - 40} ${y + h + 40} L${x + 240} ${y + h + 40} L${x + 270} ${y + h + 70}`, 3, T.TECH.LINE);
    f.extra = [];
    if (o.tabs) { [[x + 20, 34], [x + 70, 34], [x + 120, 320]].forEach(([tx, tw], i) => f.extra.push(el(L, 'div', 'abs', { left: tx + 'px', top: (y - 40) + 'px', width: tw + 'px', height: '30px', background: T.TECH.BAR, clipPath: i === 2 ? 'polygon(0 0, 92% 0, 100% 100%, 0 100%)' : 'none', transformOrigin: '0 50%' }))); }
    if (o.ladder) { const lad = el(L, 'div', 'abs', { left: (x - 50) + 'px', top: (y + 30) + 'px', width: '24px', height: '320px', backgroundImage: `repeating-linear-gradient(180deg, ${T.TECH.CYAN} 0 8px, transparent 8px 26px)`, transformOrigin: '50% 0' }); f.extra.push(lad); }
    if (o.right) { f.extra.push(el(L, 'div', 'abs', { left: (x + w + 26) + 'px', top: (y + 70) + 'px', width: '14px', height: '120px', background: T.TECH.CYAN, transformOrigin: '50% 0' }));
      f.extra.push(el(L, 'div', 'abs', { left: (x + w + 26) + 'px', top: (y + 210) + 'px', width: '14px', height: '60px', backgroundImage: `repeating-linear-gradient(180deg, ${T.TECH.CYAN} 0 8px, transparent 8px 18px)`, transformOrigin: '50% 0' })); }
    if (o.barcode) f.extra.push(el(L, 'div', 'abs', { left: (x + w / 2 - 110) + 'px', top: (y + h - 70) + 'px', width: '220px', height: '26px', backgroundImage: `repeating-linear-gradient(90deg, ${T.TECH.LINE} 0 3px, transparent 3px 7px)`, transformOrigin: '0 50%' }));
    return f; };
  T.techFrameAt = (f, u) => { f.parts.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.l * (1 - ease.out3(clamp(u * 1.3 - i * .12))))); f.extra.forEach((e, i) => { const k = ease.outExpo(clamp(u * 1.6 - .3 - i * .08)); e.style.opacity = k > 0 ? 1 : 0; e.style.transform = e.style.transformOrigin === '50% 0' ? `scaleY(${k})` : `scaleX(${k})`; }); };
  /* cyan serif title + white spaced uppercase subtitle */
  T.techTitle = (L, title, sub, x, y, size, align) => { const d = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', textAlign: align || 'left' }); if (align === 'center') { d.style.left = '0'; d.style.width = '1920px'; }
    d.a = el(d, 'div', '', { fontFamily: T.TECH.SERIF, fontWeight: 700, fontSize: (size || 120) + 'px', lineHeight: 1.1, color: T.TECH.CYAN, textShadow: '0 0 30px rgba(98,240,255,.35)', whiteSpace: 'nowrap' }, title);
    d.b = el(d, 'div', '', { fontFamily: T.TECH.SANS, fontWeight: 700, fontSize: Math.round((size || 120) * .33) + 'px', letterSpacing: '.08em', color: '#fff', marginTop: '18px', whiteSpace: 'nowrap', textTransform: 'uppercase' }, sub || ''); return d; };
  /* table of contents: items [[title, sub], ...] in two columns with numbered circles. T.tocAt(t, time, t0, step) */
  T.toc = (L, items, cy) => { const rows = Math.ceil(items.length / 2), o = { r: [] }; const y0 = (cy || 600) - rows * 75;
    items.forEach(([ti, su], i) => { const col = i % 2, row = Math.floor(i / 2), y = y0 + row * 150, left = col === 0;
      const r = el(L, 'div', 'abs', { top: y + 'px', [left ? 'right' : 'left']: (left ? 1920 - 940 : 980) + 'px', display: 'flex', alignItems: 'center', gap: '22px', flexDirection: left ? 'row' : 'row-reverse', transformOrigin: left ? '100% 50%' : '0 50%' });
      const tx = el(r, 'div', '', { textAlign: left ? 'right' : 'left' }); el(tx, 'div', '', { fontFamily: T.TECH.SERIF, fontWeight: 700, fontSize: '38px', color: '#fff', whiteSpace: 'nowrap' }, ti); el(tx, 'div', 'cn', { fontSize: '22px', fontWeight: 400, color: T.TECH.DIM }, su);
      el(r, 'div', '', { width: '88px', height: '88px', borderRadius: '50%', border: `2px solid ${T.TECH.LINE}`, color: T.TECH.CYAN, fontFamily: T.TECH.SERIF, fontSize: '32px', lineHeight: '84px', textAlign: 'center', flex: 'none' }, String(i + 1).padStart(2, '0')); o.r.push(r); }); return o; };
  T.tocAt = (o, t, t0, step) => o.r.forEach((r, i) => tf(r, slide(t, t0 + i * (step || .25), .45, (i % 2 ? 60 : -60), 0)));
  /* chamfered outline panel with tabs + barcode, for section titles. T.panelAt(p, u) */
  T.panel = (L, x, y, w, h, title, sub) => { const p = {}; const s = K.svg(L, w + 40, h + 80, x - 20, y - 50); const c = 60;
    p.o = K.sv(s, 'path', { d: `M${20 + c} 50 L${20 + w * .55} 50 L${20 + w * .55 + 30} 70 L${20 + w} 70 L${20 + w} ${50 + h - c} L${20 + w - c} ${50 + h} L20 ${50 + h} L20 ${50 + c} Z`, fill: 'rgba(5,30,90,.35)', stroke: T.TECH.CYAN, 'stroke-width': 3 }); p.l = p.o.getTotalLength(); p.o.setAttribute('stroke-dasharray', p.l); p.o.setAttribute('stroke-dashoffset', p.l);
    p.tab1 = el(L, 'div', 'abs', { left: (x + 80) + 'px', top: (y - 34) + 'px', width: '180px', height: '18px', background: T.TECH.BAR, transformOrigin: '0 50%' }); p.tab2 = el(L, 'div', 'abs', { left: (x + w * .62) + 'px', top: (y - 52) + 'px', width: '260px', height: '28px', background: T.TECH.BAR, transformOrigin: '0 50%' });
    p.bc = el(L, 'div', 'abs', { left: (x + w - 380) + 'px', top: (y + h + 30) + 'px', width: '380px', height: '24px', backgroundImage: `repeating-linear-gradient(90deg, ${T.TECH.LINE} 0 3px, transparent 3px 7px)`, transformOrigin: '100% 50%' });
    p.t = T.techTitle(L, title, '', x, y + h / 2 - 90, 96); p.t.style.width = w + 'px'; p.t.style.textAlign = 'center'; p.t.b.remove();
    p.s = el(L, 'div', 'cn', { position: 'absolute', left: x + 'px', width: w + 'px', top: (y + h / 2 + 30) + 'px', textAlign: 'center', fontSize: '30px', fontWeight: 400, color: '#fff' }, sub || ''); return p; };
  T.panelAt = (p, u) => { p.o.setAttribute('stroke-dashoffset', p.l * (1 - ease.out3(clamp(u * 1.4)))); [p.tab1, p.tab2, p.bc].forEach((e, i) => { const k = ease.outExpo(clamp(u * 1.6 - .3 - i * .1)); e.style.transform = `scaleX(${k})`; });
    p.t.style.opacity = clamp(u * 2 - .6); p.s.style.opacity = clamp(u * 2 - .9); };
  /* simple line icons drawn in SVG: window | cloud | chart | code | play | doc */
  T.icon = (L, kind, x, y, size, col) => { const s = K.svg(L, size, size, x, y); const a = { fill: 'none', stroke: col || '#fff', 'stroke-width': Math.max(2, size / 28), 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }; const z = size;
    const P2 = d => K.sv(s, 'path', Object.assign({ d }, a));
    if (kind === 'window' || kind === 'code' || kind === 'play' || kind === 'chart') { P2(`M${z * .06} ${z * .14} H${z * .94} V${z * .86} H${z * .06} Z M${z * .06} ${z * .3} H${z * .94}`); K.sv(s, 'circle', Object.assign({ cx: z * .14, cy: z * .22, r: z * .02 }, a)); K.sv(s, 'circle', Object.assign({ cx: z * .22, cy: z * .22, r: z * .02 }, a)); }
    if (kind === 'code') P2(`M${z * .36} ${z * .46} L${z * .24} ${z * .58} L${z * .36} ${z * .7} M${z * .64} ${z * .46} L${z * .76} ${z * .58} L${z * .64} ${z * .7} M${z * .54} ${z * .42} L${z * .46} ${z * .74}`);
    if (kind === 'play') P2(`M${z * .42} ${z * .44} L${z * .62} ${z * .58} L${z * .42} ${z * .72} Z`);
    if (kind === 'chart') P2(`M${z * .22} ${z * .74} V${z * .6} M${z * .38} ${z * .74} V${z * .48} M${z * .54} ${z * .74} V${z * .54} M${z * .7} ${z * .74} V${z * .42}`);
    if (kind === 'window') P2(`M${z * .16} ${z * .42} H${z * .5} M${z * .16} ${z * .54} H${z * .62} M${z * .16} ${z * .66} H${z * .44}`);
    if (kind === 'cloud') P2(`M${z * .28} ${z * .7} C${z * .1} ${z * .7} ${z * .1} ${z * .44} ${z * .3} ${z * .44} C${z * .32} ${z * .24} ${z * .62} ${z * .22} ${z * .66} ${z * .42} C${z * .9} ${z * .4} ${z * .9} ${z * .7} ${z * .72} ${z * .7} Z M${z * .5} ${z * .76} V${z * .9} M${z * .3} ${z * .9} H${z * .7}`);
    if (kind === 'doc') P2(`M${z * .2} ${z * .08} H${z * .62} L${z * .8} ${z * .26} V${z * .92} H${z * .2} Z M${z * .32} ${z * .44} H${z * .68} M${z * .32} ${z * .58} H${z * .68} M${z * .32} ${z * .72} H${z * .56}`);
    s.style.transformOrigin = '50% 50%'; return s; };
  /* outlined column card: icon, cyan serif title, bullet list, footer line. Good for 3 options / 3 steps */
  T.colCard = (L, x, y, w, h, icon, title, bullets, foot) => { const c = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', border: `2px solid rgba(98,180,255,.55)`, background: 'rgba(4,24,80,.35)', borderRadius: '4px', transformOrigin: '50% 100%' });
    const ic = T.icon(c, icon, w / 2 - 50, 34, 100, '#fff'); ic.style.position = 'absolute';
    el(c, 'div', 'abs', { left: 0, width: w + 'px', top: '160px', textAlign: 'center', fontFamily: T.TECH.SERIF, fontWeight: 700, fontSize: '42px', color: T.TECH.CYAN }, title);
    const ul = el(c, 'ul', 'abs cn', { left: '36px', right: '30px', top: '236px', margin: 0, paddingLeft: '22px', fontSize: '24px', fontWeight: 400, color: '#fff', lineHeight: 1.45, whiteSpace: 'normal' }); bullets.forEach(b => el(ul, 'li', '', { marginBottom: '10px' }, b));
    if (foot) { el(c, 'div', 'abs', { left: '30px', right: '30px', bottom: '78px', height: '1px', background: 'rgba(98,180,255,.4)' }); el(c, 'div', 'abs', { left: 0, width: w + 'px', bottom: '24px', textAlign: 'center', fontFamily: T.TECH.SERIF, fontWeight: 700, fontSize: '34px', color: '#fff' }, foot); } return c; };
  /* image band with a blue fade + icon/text cards under it (real screenshot only) */
  T.band = (L, src, x, y, w, h) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', overflow: 'hidden' }); const im = el(b, 'img', '', { width: '100%', height: '100%', objectFit: 'cover', display: 'block', filter: 'saturate(.9) brightness(.85)' }); C.setSrc(im, src);
    el(b, 'div', 'abs', { left: 0, top: 0, right: 0, bottom: 0, background: 'linear-gradient(180deg, rgba(2,19,53,0) 40%, rgba(6,41,122,.9))' }); return b; };
  T.infoCard = (L, icon, title, desc, x, y, w) => { const c = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: (w || 560) + 'px', transformOrigin: '0 50%' }); const ic = T.icon(c, icon, 0, 0, 92, '#fff'); ic.style.position = 'absolute';
    el(c, 'div', 'abs', { left: '120px', top: 0, fontFamily: T.TECH.SERIF, fontWeight: 700, fontSize: '36px', color: '#fff', whiteSpace: 'nowrap' }, title); el(c, 'div', 'abs cn', { left: '120px', top: '54px', right: 0, fontSize: '22px', fontWeight: 400, color: T.TECH.DIM, whiteSpace: 'normal', lineHeight: 1.4 }, desc); return c; };
  /* corner accent: two parallel slanted strokes + long line (as on the deck corners) */
  T.corner = (L, x, y, flip) => { const s = K.svg(L, 360, 200, x, y); s.style.transform = flip ? 'scale(-1,-1)' : ''; const a = { fill: 'none', stroke: T.TECH.LINE, 'stroke-width': 3 };
    K.sv(s, 'path', Object.assign({ d: 'M0 4 H240 L330 94 V196' }, a)); K.sv(s, 'path', Object.assign({ d: 'M268 4 L356 92' }, a)); return s; };

  /* ---------- T14 Future Style: wave mesh, rotating globe, circuit chip, wireframe ring ---------- */
  T.FUT = { CYAN: '#2ee6ff', BLUE: '#2f5bff', VIOLET: '#8a5cff', PINK: '#ff8adf', WHITE: '#ffffff', SANS: "'Inter','Noto Sans CJK SC',sans-serif" };
  T.futBg = 'linear-gradient(180deg, #02041f 0%, #050d55 55%, #0a1c96 100%)';
  const fcan = (L, z) => { const cv = el(L, 'canvas', 'abs', { left: 0, top: 0, zIndex: z || 1 }); cv.width = 1920; cv.height = 1080; return cv; };
  /* undulating 3D wireframe floor. opts {horizon, amp, speed, rows, cols}. T.waveAt(w, t) — call every frame so it keeps moving */
  T.wave = (L, opts) => { const o = Object.assign({ horizon: 560, amp: 70, speed: 1, rows: 34, cols: 56, cam: 260, f: 760 }, opts || {}); o.cv = fcan(L, 1); o.g = o.cv.getContext('2d'); return o; };
  T.waveAt = (o, t) => { const { g } = o; g.clearRect(0, 0, 1920, 1080); g.globalCompositeOperation = 'lighter';
    const H = (x, z) => o.amp * (Math.sin(x * .006 + t * 1.1 * o.speed) * Math.cos(z * .004 - t * .8 * o.speed) + .6 * Math.sin((x + z) * .004 + t * .6 * o.speed));
    const proj = (x, z) => { const y = H(x, z); return [960 + x * o.f / z, o.horizon + (o.cam - y) * o.f / z]; };
    const col = (sx, a) => { const e = Math.min(1, Math.abs(sx - 960) / 960); const r = Math.round(60 + 195 * e * e), gg = Math.round(120 - 40 * e), b = 255; return `rgba(${r},${gg},${b},${a})`; };
    const zs = []; for (let i = 0; i < o.rows; i++) zs.push(240 + i * i * 2.6 + i * 40); const xs = []; for (let j = 0; j <= o.cols; j++) xs.push(-2600 + j * (5200 / o.cols));
    for (const pass of [[5, .10], [1.4, .55]]) { g.lineWidth = pass[0];
      zs.forEach((z, i) => { const a = pass[1] * Math.max(.08, 1 - i / o.rows); g.beginPath(); xs.forEach((x, j) => { const [sx, sy] = proj(x, z); j ? g.lineTo(sx, sy) : g.moveTo(sx, sy); }); g.strokeStyle = col(960, a); g.stroke(); });
      xs.forEach(x => { g.beginPath(); zs.forEach((z, i) => { const [sx, sy] = proj(x, z); i ? g.lineTo(sx, sy) : g.moveTo(sx, sy); }); const [ex] = proj(x, zs[0]); g.strokeStyle = col(ex, pass[1] * .8); g.stroke(); }); }
    g.fillStyle = 'rgba(200,230,255,.9)'; zs.forEach((z, i) => { if (i % 2) return; xs.forEach((x, j) => { if ((i + j) % 5) return; const [sx, sy] = proj(x, z); g.beginPath(); g.arc(sx, sy, Math.max(.8, 3 - i * .08), 0, 7); g.fill(); }); });
    g.globalCompositeOperation = 'source-over'; };
  /* glowing dotted globe with real continents (engine/land.js) + lat/long grid + orbit ring. T.globeTAt(G, t) rotates it slowly */
  let LANDPTS = null; const landPts = () => { if (LANDPTS) return LANDPTS; LANDPTS = []; const Lm = window.EVA_LAND; if (!Lm) return LANDPTS; const raw = atob(Lm.b), rb = Lm.w / 8;
    const on = (lon, lat) => { const x = Math.floor((lon + 180) / 360 * Lm.w) % Lm.w, y = Math.min(Lm.h - 1, Math.floor((90 - lat) / 180 * Lm.h)); return (raw.charCodeAt(y * rb + (x >> 3)) >> (7 - (x & 7))) & 1; };
    for (let lat = -84; lat <= 84; lat += 0.95) { const st = 0.95 / Math.max(.25, Math.cos(lat * Math.PI / 180)); for (let lon = -180; lon < 180; lon += st) if (on(lon, lat)) LANDPTS.push([lon * Math.PI / 180, lat * Math.PI / 180]); } return LANDPTS; };
  T.globeT = (L, cx, cy, r, opts) => { const o = Object.assign({ cx, cy, r, tilt: 14, lon0: -125, speed: 6, orbit: true }, opts || {}); o.back = fcan(L, 2); o.cv = fcan(L, 3); o.front = fcan(L, 4); landPts(); return o; };
  T.globeTAt = (G, t, u) => { const { cx, cy, r } = G; const vis = u === undefined ? 1 : clamp(u); [G.back, G.cv, G.front].forEach(c => { c.style.opacity = vis; }); const g = G.cv.getContext('2d'), gb = G.back.getContext('2d'), gf = G.front.getContext('2d');
    [g, gb, gf].forEach(x => x.clearRect(0, 0, 1920, 1080)); const rot = (G.lon0 + G.speed * t) * Math.PI / 180, ti = G.tilt * Math.PI / 180, ct = Math.cos(ti), stt = Math.sin(ti);
    const P3 = (lon, lat) => { const x = Math.cos(lat) * Math.sin(lon + rot), y = Math.sin(lat), z = Math.cos(lat) * Math.cos(lon + rot); const y2 = y * ct - z * stt, z2 = y * stt + z * ct; return [cx + x * r, cy - y2 * r, z2]; };
    let gr = g.createRadialGradient(cx, cy, r * .2, cx, cy, r * 1.25); gr.addColorStop(0, 'rgba(40,90,255,.0)'); gr.addColorStop(.78, 'rgba(60,120,255,.18)'); gr.addColorStop(.82, 'rgba(90,170,255,.45)'); gr.addColorStop(1, 'rgba(40,80,255,0)'); g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, r * 1.25, 0, 7); g.fill();
    gr = g.createRadialGradient(cx - r * .35, cy - r * .35, r * .1, cx, cy, r); gr.addColorStop(0, 'rgba(40,110,255,.55)'); gr.addColorStop(1, 'rgba(8,20,110,.85)'); g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
    g.globalCompositeOperation = 'lighter'; g.lineWidth = 1.2;
    for (let lo = 0; lo < 360; lo += 15) { g.beginPath(); let st = false; for (let la = -90; la <= 90; la += 4) { const [x, y, z] = P3(lo * Math.PI / 180, la * Math.PI / 180); if (z < 0) { st = false; continue; } st ? g.lineTo(x, y) : g.moveTo(x, y); st = true; } g.strokeStyle = 'rgba(120,180,255,.22)'; g.stroke(); }
    for (let la = -75; la <= 75; la += 15) { g.beginPath(); let st = false; for (let lo = 0; lo <= 360; lo += 4) { const [x, y, z] = P3(lo * Math.PI / 180, la * Math.PI / 180); if (z < 0) { st = false; continue; } st ? g.lineTo(x, y) : g.moveTo(x, y); st = true; } g.strokeStyle = 'rgba(120,180,255,.35)'; g.stroke(); }
    for (const [lo, la] of LANDPTS) { const [x, y, z] = P3(lo, la); if (z < .02) continue; g.fillStyle = `rgba(${90 + 140 * z | 0},245,255,${.55 + .45 * z})`; g.fillRect(x - 1.6, y - 1.6, 3.2, 3.2); }
    g.globalCompositeOperation = 'source-over'; g.strokeStyle = 'rgba(140,200,255,.9)'; g.lineWidth = 2.5; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.stroke();
    if (G.orbit) { const R1 = r * 1.42, R2 = r * .3, ang = -12 * Math.PI / 180; const pt = a => { const x = R1 * Math.cos(a), y = R2 * Math.sin(a); return [cx + x * Math.cos(ang) - y * Math.sin(ang), cy + r * .1 + x * Math.sin(ang) + y * Math.cos(ang)]; };
      const arcDraw = (ctx, a0, a1, al) => { for (const [w, a] of [[8, .15 * al], [2.2, .9 * al]]) { ctx.lineWidth = w; ctx.strokeStyle = `rgba(190,215,255,${a})`; ctx.beginPath(); for (let a2 = a0; a2 <= a1; a2 += .02) { const [x, y] = pt(a2); a2 === a0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); } ctx.stroke(); } };
      arcDraw(gb, Math.PI, 2 * Math.PI, .6); arcDraw(gf, 0, Math.PI, 1);
      [0, Math.PI].forEach(k => { const a = (t * .5 + k) % (2 * Math.PI), [x, y] = pt(a), ctx = Math.sin(a) > 0 ? gf : gb; const rg = ctx.createRadialGradient(x, y, 0, x, y, 22); rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(1, 'rgba(160,190,255,0)'); ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(x, y, 22, 0, 7); ctx.fill(); }); } };
  /* glowing chip with circuit traces and travelling pulses (perspective floor). T.chipAt(c, t) */
  T.chip = (L, cx, cy, size) => { const c = { cx, cy, s: size || 300, cv: fcan(L, 3) }; const R = C.rng(17); c.tr = [];
    for (let i = 0; i < 22; i++) { const side = i % 2 ? -1 : 1, sy = cy - c.s * .2 + (i / 22) * c.s * .55; const pts = [[cx - c.s * .55, sy]]; let x = cx - c.s * .55, y = sy;
      for (let k = 0; k < 4; k++) { x -= 120 + R() * 220; pts.push([x, y]); const dy = (R() - .3) * 90; x -= Math.abs(dy); y += dy; pts.push([x, y]); } c.tr.push({ pts, ph: R(), sp: .15 + R() * .2 }); }
    /* traces also fan out behind/right of the chip */
    for (let i = 0; i < 10; i++) { const sy = cy - c.s * .1 + i * c.s * .05; const pts = [[cx + c.s * .4, sy]]; let x = cx + c.s * .4, y = sy; for (let k = 0; k < 3; k++) { x += 80 + R() * 120; pts.push([x, y]); const dy = (R() - .6) * 70; x += Math.abs(dy); y += dy; pts.push([x, y]); } c.tr.push({ pts, ph: R(), sp: .2 + R() * .2 }); }
    return c; };
  T.chipAt = (c, t) => { const g = c.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); g.globalCompositeOperation = 'lighter';
    for (const tr of c.tr) { g.lineWidth = 2; g.strokeStyle = 'rgba(80,170,255,.55)'; g.beginPath(); tr.pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
      const segs = []; let tot = 0; for (let i = 1; i < tr.pts.length; i++) { const d = Math.hypot(tr.pts[i][0] - tr.pts[i - 1][0], tr.pts[i][1] - tr.pts[i - 1][1]); segs.push(d); tot += d; }
      let dd = ((t * tr.sp + tr.ph) % 1) * tot; for (let i = 0; i < segs.length; i++) { if (dd <= segs[i]) { const k = dd / segs[i], x = tr.pts[i][0] + (tr.pts[i + 1][0] - tr.pts[i][0]) * k, y = tr.pts[i][1] + (tr.pts[i + 1][1] - tr.pts[i][1]) * k; const rg = g.createRadialGradient(x, y, 0, x, y, 14); rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(1, 'rgba(90,170,255,0)'); g.fillStyle = rg; g.beginPath(); g.arc(x, y, 14, 0, 7); g.fill(); break; } dd -= segs[i]; } }
    g.globalCompositeOperation = 'source-over'; const { cx, cy, s } = c; const sk = (x, y) => [cx + x - y * .55, cy + y * .45];
    const quad = (o, col, st, lw) => { const p = [sk(-s / 2 + o, -s / 2 + o), sk(s / 2 - o, -s / 2 + o), sk(s / 2 - o, s / 2 - o), sk(-s / 2 + o, s / 2 - o)]; g.beginPath(); p.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); if (col) { g.fillStyle = col; g.fill(); } if (st) { g.strokeStyle = st; g.lineWidth = lw || 3; g.stroke(); } };
    g.save(); g.translate(0, 26); quad(0, 'rgba(40,60,160,.9)'); g.restore(); g.shadowColor = 'rgba(120,180,255,.9)'; g.shadowBlur = 40; quad(0, '#0d1240', 'rgba(170,220,255,.95)', 5); g.shadowBlur = 0; quad(18, '#090c2c', 'rgba(140,200,255,.6)', 2);
    const pul = .5 + .5 * Math.sin(t * 2); g.globalAlpha = .15 + .15 * pul; quad(18, '#4f8cff'); g.globalAlpha = 1; };
  /* rotating wireframe torus (ring). T.torusAt(o, t) */
  T.torus = (L, cx, cy, R, r) => ({ cx, cy, R, r, cv: fcan(L, 3) });
  T.torusAt = (o, t) => { const g = o.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); g.globalCompositeOperation = 'lighter'; const ry = -0.55 + .12 * Math.sin(t * .4), rx = .12, spin = t * .25;
    const P3 = (u, v) => { const x0 = (o.R + o.r * Math.cos(v)) * Math.cos(u + spin), y0 = (o.R + o.r * Math.cos(v)) * Math.sin(u + spin), z0 = o.r * Math.sin(v); let x = x0 * Math.cos(ry) + z0 * Math.sin(ry), z = -x0 * Math.sin(ry) + z0 * Math.cos(ry); let y = y0 * Math.cos(rx) - z * Math.sin(rx); z = y0 * Math.sin(rx) + z * Math.cos(rx); const k = 1400 / (1400 + z); return [o.cx + x * k, o.cy + y * k, z]; };
    const colr = (u, a) => { const e = (Math.cos(u) + 1) / 2; return `rgba(${Math.round(60 + 160 * e)},${Math.round(200 - 60 * e)},255,${a})`; };
    for (const [lw, al] of [[4, .12], [1.2, .7]]) { g.lineWidth = lw;
      for (let i = 0; i < 64; i++) { const u = i / 64 * 2 * Math.PI; g.beginPath(); for (let j = 0; j <= 24; j++) { const [x, y] = P3(u, j / 24 * 2 * Math.PI); j ? g.lineTo(x, y) : g.moveTo(x, y); } g.strokeStyle = colr(u, al); g.stroke(); }
      for (let j = 0; j < 14; j++) { const v = j / 14 * 2 * Math.PI; g.beginPath(); for (let i = 0; i <= 96; i++) { const u = i / 96 * 2 * Math.PI; const [x, y] = P3(u, v); i ? g.lineTo(x, y) : g.moveTo(x, y); } g.strokeStyle = `rgba(120,200,255,${al})`; g.stroke(); } }
    g.globalCompositeOperation = 'source-over'; };
  /* glowing white headline + white CN line + cyan underline sweep */
  T.futTitle = (L, l1, l2, cn, x, y, size) => { size = size || 150; const d = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', zIndex: 6 }); const sh = '0 0 18px rgba(140,190,255,.8), 0 0 50px rgba(80,140,255,.6)';
    d.a = el(d, 'div', '', { fontFamily: T.FUT.SANS, fontWeight: 900, fontSize: size + 'px', lineHeight: .95, color: '#fff', textShadow: sh, whiteSpace: 'nowrap', letterSpacing: '-.01em' }, l1);
    d.b = el(d, 'div', '', { fontFamily: T.FUT.SANS, fontWeight: 900, fontSize: size + 'px', lineHeight: .95, color: '#fff', textShadow: sh, whiteSpace: 'nowrap', letterSpacing: '-.01em' }, l2 || '');
    d.c = el(d, 'div', 'cn', { fontSize: (size * .5) + 'px', fontWeight: 700, color: '#fff', marginTop: '22px', letterSpacing: '.08em', textShadow: '0 0 20px rgba(120,180,255,.6)' }, cn || '');
    d.u = el(d, 'div', '', { height: '4px', width: (size * 3) + 'px', marginTop: '22px', background: `linear-gradient(90deg, ${T.FUT.CYAN}, rgba(46,230,255,0))`, boxShadow: `0 0 14px ${T.FUT.CYAN}`, transformOrigin: '0 50%' }); return d; };
  T.futTitleAt = (d, t, t0) => { tf(d.a, slide(t, t0, .5, -80, 0)); tf(d.b, slide(t, t0 + .15, .5, -80, 0)); tf(d.c, { o: P(t, t0 + .5, .3) }); d.u.style.transform = `scaleX(${ease.outExpo(P(t, t0 + .6, .7))})`; };
  /* RULE 1/2/3 list: white word + cyan number, CN under, glowing dividers */
  T.rules = (L, items, x, y, word, size) => { size = size || 120; const rows = []; items.forEach((cn, i) => { const r = el(L, 'div', 'abs', { left: x + 'px', top: (y + i * size * 1.7) + 'px', zIndex: 6 });
      el(r, 'div', '', { fontFamily: T.FUT.SANS, fontWeight: 900, fontSize: size + 'px', lineHeight: 1, color: '#fff', textShadow: '0 0 20px rgba(140,190,255,.7)', whiteSpace: 'nowrap' }, `${word || 'RULE'} <span style="color:${T.FUT.CYAN};text-shadow:0 0 24px rgba(46,230,255,.8)">${i + 1}</span>`);
      el(r, 'div', 'cn', { fontSize: (size * .4) + 'px', fontWeight: 700, color: '#fff', marginTop: '6px' }, cn);
      if (i < items.length - 1) r.line = el(L, 'div', 'abs', { left: (x - 60) + 'px', top: (y + i * size * 1.7 + size * 1.55) + 'px', width: '700px', height: '2px', background: 'linear-gradient(90deg, rgba(80,140,255,0), rgba(110,170,255,.9), rgba(80,140,255,0))', transformOrigin: '0 50%', zIndex: 6 }); rows.push(r); }); return rows; };
  T.rulesAt = (rows, t, t0, step) => rows.forEach((r, i) => { tf(r, slide(t, t0 + i * (step || .5), .45, -70, 0)); if (r.line) r.line.style.transform = `scaleX(${ease.outExpo(P(t, t0 + i * (step || .5) + .3, .6))})`; });

  /* ---------- T15 Learning Style: flat storybook illustration on indigo ---------- */
  T.LRN = { BG: '#372a8c', CLOUD: '#7b6ee6', STAR: '#ffc533', RED: '#ff5d5d', ORANGE: '#ffb02e', GREEN: '#2fd3a6', BLUE: '#47a7ff', PURPLE: '#a77bff', PINK: '#e8438f', CREAM: '#fff3dc', WHITE: '#ffffff',
    EN: "'Inter','Noto Sans CJK SC',sans-serif", CN: "'Noto Sans CJK SC',sans-serif" };
  T.learnBg = `radial-gradient(1300px 900px at 50% 45%, #3d2f99, #372a8c 60%, #2e2378 100%)`;
  const NSV = (L, w, h, x, y, z) => { const s = K.svg(L, w, h, x, y); if (z) s.style.zIndex = z; return s; };
  /* bubbly rounded lettering: heavy font + thick round-joined stroke in the same colour (works for CN + EN) */
  T.bubbly = (L, txt, x, y, size, opts) => { const o = Object.assign({ fill: '#fff', anchor: 'start', font: T.LRN.EN }, opts || {}); if (o.stroke === undefined) o.stroke = o.font === T.LRN.CN ? .018 : .05; const w = 1920, h = Math.ceil(size * 1.4); const s = NSV(L, w, h, 0, y, 6);
    const tx = K.sv(s, 'text', { x: x, y: size * 1.05, 'font-family': o.font, 'font-weight': 900, 'font-size': size, fill: o.fill, stroke: o.fill, 'stroke-width': size * o.stroke, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'paint-order': 'stroke', 'text-anchor': o.anchor, 'letter-spacing': size * (o.font === T.LRN.CN ? .04 : .025) }); tx.textContent = txt; s.style.transformOrigin = `${o.anchor === 'middle' ? x : x + 200}px 50%`; return s; };
  /* twinkling stars + drifting clouds. T.skyAt(sky, t) */
  T.sky = (L, nStars, seed, clouds) => { const R = C.rng(seed || 5), s = NSV(L, 1920, 1080, 0, 0, 1); const o = { stars: [], clouds: [] };
    const star = (cx, cy, r) => { const p = []; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; p.push((cx + rr * Math.cos(a)).toFixed(1) + ',' + (cy + rr * Math.sin(a)).toFixed(1)); } const e = K.sv(s, 'polygon', { points: p.join(' '), fill: T.LRN.STAR, 'stroke-linejoin': 'round', stroke: T.LRN.STAR, 'stroke-width': r * .25 }); e.style.transformOrigin = `${cx}px ${cy}px`; e.style.transformBox = 'view-box'; return e; };
    for (let i = 0; i < (nStars || 14); i++) o.stars.push({ e: star(R() * 1920, R() * 1080, 12 + R() * 12), ph: R() * 6.28, sp: 1.5 + R() * 2 });
    (clouds || [[120, 860, 1], [1560, 130, .9], [380, 110, .7], [1700, 640, .8]]).forEach(([x, y, k]) => { const g = K.sv(s, 'g', {}); const sc = k * 1.2;
      [[0, 30, 60, 30], [55, 0, 75, 75], [120, 25, 55, 55]].forEach(([cx, cy, rw]) => K.sv(g, 'circle', { cx: cx * sc + 40 * sc, cy: (cy + 45) * sc, r: rw / 2 * sc + 10 * sc, fill: T.LRN.CLOUD }));
      K.sv(g, 'rect', { x: 20 * sc, y: 70 * sc, width: 180 * sc, height: 40 * sc, rx: 20 * sc, fill: T.LRN.CLOUD }); o.clouds.push({ g, x, y, k }); }); return o; };
  T.skyAt = (o, t) => { o.stars.forEach(st => { const k = .75 + .25 * Math.sin(t * st.sp + st.ph); st.e.style.transform = `scale(${k}) rotate(${Math.sin(t + st.ph) * 8}deg)`; st.e.style.opacity = .65 + .35 * k; });
    o.clouds.forEach((c, i) => c.g.setAttribute('transform', `translate(${c.x + Math.sin(t * .35 + i) * 30} ${c.y})`)); };
  /* one closed book seen from the side (cover colour, cream page block, spine stripes) */
  T.book = (L, x, y, w, h, col, z) => { const s = NSV(L, w + 30, h + 30, x, y, z || 3); const d = Math.round(h * .22);
    K.sv(s, 'rect', { x: 6, y: 12, width: w, height: h, rx: 14, fill: 'rgba(20,10,60,.35)' });
    K.sv(s, 'rect', { x: 0, y: 0, width: w, height: h, rx: 14, fill: col });
    K.sv(s, 'path', { d: `M${w * .58} ${d} H${w - 12} Q${w + 6} ${h / 2} ${w - 12} ${h - d} H${w * .58} Z`, fill: T.LRN.CREAM });
    for (let i = 0; i < 3; i++) K.sv(s, 'line', { x1: w * .64, y1: d + 10 + i * (h - 2 * d - 20) / 2, x2: w - 26, y2: d + 10 + i * (h - 2 * d - 20) / 2, stroke: '#e9c9a0', 'stroke-width': 3, 'stroke-linecap': 'round' });
    [w * .09, w * .13, w * .5].forEach(sx => K.sv(s, 'rect', { x: sx, y: 10, width: 7, height: h - 20, rx: 3, fill: 'rgba(255,255,255,.85)' })); s.style.transformOrigin = '50% 100%'; return s; };
  /* staircase of books from bottom-left to top-right. T.stairsAt(st, t, t0, step) */
  T.stairs = (L, x, y, cols) => (cols || [T.LRN.RED, T.LRN.ORANGE, T.LRN.GREEN, T.LRN.BLUE, T.LRN.PURPLE]).map((c, i) => T.book(L, x + i * 105, y - i * 118, 490 - i * 25, 118, c, 3 + i));
  T.stairsAt = (bs, t, t0, step) => bs.forEach((b, i) => { const u = P(t, t0 + i * (step || .22), .45); tf(b, { y: -160 * (1 - ease.outBack(u, 1.6)), o: u > 0 ? 1 : 0 }); });
  /* sun with rotating rays */
  T.sun = (L, cx, cy, r) => { const s = NSV(L, r * 4, r * 4, cx - r * 2, cy - r * 2, 2); const g = K.sv(s, 'g', {}); for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5; K.sv(g, 'line', { x1: 2 * r + Math.cos(a) * r * 1.3, y1: 2 * r + Math.sin(a) * r * 1.3, x2: 2 * r + Math.cos(a) * r * 1.75, y2: 2 * r + Math.sin(a) * r * 1.75, stroke: T.LRN.STAR, 'stroke-width': r * .16, 'stroke-linecap': 'round' }); }
    K.sv(s, 'circle', { cx: 2 * r, cy: 2 * r, r, fill: T.LRN.STAR }); s.rays = g; s.r = r; return s; };
  T.sunAt = (s, t, u) => { s.rays.setAttribute('transform', `rotate(${t * 12} ${2 * s.r} ${2 * s.r})`); tf(s, { s: ease.outBack(clamp(u ?? 1), 1.5), o: clamp((u ?? 1) * 3) }); };
  /* paper plane flying along a dashed path. pts: [[x,y],...] (smooth). T.planeAt(p, u) */
  T.plane = (L, pts, size) => { const s = NSV(L, 1920, 1080, 0, 0, 7); let d = `M${pts[0][0]} ${pts[0][1]}`; for (let i = 1; i < pts.length - 1; i++) { const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2; d += ` Q${pts[i][0]} ${pts[i][1]} ${mx} ${my}`; } d += ` L${pts[pts.length - 1][0]} ${pts[pts.length - 1][1]}`;
    const path = K.sv(s, 'path', { d, fill: 'none', stroke: '#fff', 'stroke-width': 5, 'stroke-dasharray': '16 14', 'stroke-linecap': 'round' }); const l = path.getTotalLength();
    const z = size || 90, g = K.sv(s, 'g', {}); K.sv(g, 'polygon', { points: `0,0 ${-z},${-z * .38} ${-z * .62},0`, fill: '#ffffff' }); K.sv(g, 'polygon', { points: `0,0 ${-z * .62},0 ${-z * .78},${z * .3}`, fill: '#cfe2ff' }); K.sv(g, 'polygon', { points: `0,0 ${-z},${-z * .38} ${-z * .55},${z * .12}`, fill: '#e8f1ff' });
    return { path, l, g }; };
  T.planeAt = (p, u) => { u = clamp(u); const L2 = p.l * u; p.path.setAttribute('stroke-dasharray', dashUpTo(L2)); p.path.setAttribute('opacity', u > 0 ? 1 : 0);
    const pt = p.path.getPointAtLength(Math.max(.1, L2)), pt2 = p.path.getPointAtLength(Math.max(0, L2 - 4)); const a = Math.atan2(pt.y - pt2.y, pt.x - pt2.x) * 180 / Math.PI; p.g.setAttribute('transform', `translate(${pt.x} ${pt.y}) rotate(${a})`); p.g.setAttribute('opacity', u > 0 ? 1 : 0); };
  function dashUpTo(len) { const parts = []; let d = 0; while (d + 30 <= len) { parts.push(16, 14); d += 30; } const rest = Math.max(0, len - d); parts.push(Math.min(16, rest), 99999); return parts.join(' '); }
  /* soft blob behind an icon */
  T.blob = (L, cx, cy, r, col, seed) => { const R = C.rng(seed || 3), s = NSV(L, r * 3, r * 3, cx - r * 1.5, cy - r * 1.5, 2); let d = ''; const n = 7, pts = [];
    for (let i = 0; i < n; i++) { const a = i / n * 2 * Math.PI, rr = r * (.85 + R() * .3); pts.push([1.5 * r + rr * Math.cos(a), 1.5 * r + rr * Math.sin(a)]); }
    const mid = (p, q) => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]; const m0 = mid(pts[n - 1], pts[0]); d = `M${m0[0]} ${m0[1]}`; pts.forEach((p, i) => { const m = mid(p, pts[(i + 1) % n]); d += ` Q${p[0]} ${p[1]} ${m[0]} ${m[1]}`; });
    K.sv(s, 'path', { d: d + ' Z', fill: col }); s.style.transformOrigin = '50% 50%'; return s; };
  /* flat icons: 'openbook' | 'bulb' | 'pencil' (with notebook) | 'notebook' */
  T.lIcon = (L, kind, cx, cy, size) => { const z = size, s = NSV(L, z * 2, z * 2, cx - z, cy - z, 4); const g = K.sv(s, 'g', { transform: `translate(${z} ${z})` }); const S = (tag, a) => K.sv(g, tag, a);
    if (kind === 'openbook') { S('path', { d: `M${-z * .78} ${-z * .38} Q${-z * .4} ${-z * .5} 0 ${-z * .3} Q${z * .4} ${-z * .5} ${z * .78} ${-z * .38} L${z * .82} ${z * .42} Q${z * .4} ${z * .32} 0 ${z * .5} Q${-z * .4} ${z * .32} ${-z * .82} ${z * .42} Z`, fill: T.LRN.RED });
      S('path', { d: `M${-z * .72} ${-z * .46} Q${-z * .36} ${-z * .56} 0 ${-z * .36} V${z * .4} Q${-z * .36} ${z * .22} ${-z * .74} ${z * .32} Z`, fill: '#fff' }); S('path', { d: `M${z * .72} ${-z * .46} Q${z * .36} ${-z * .56} 0 ${-z * .36} V${z * .4} Q${z * .36} ${z * .22} ${z * .74} ${z * .32} Z`, fill: '#f4f1ff' });
      for (let i = 0; i < 4; i++) { S('path', { d: `M${-z * .6} ${-z * .28 + i * z * .16} Q${-z * .32} ${-z * .34 + i * z * .16} ${-z * .1} ${-z * .22 + i * z * .16}`, stroke: '#b9a9ff', 'stroke-width': z * .04, fill: 'none', 'stroke-linecap': 'round' }); S('path', { d: `M${z * .1} ${-z * .22 + i * z * .16} Q${z * .32} ${-z * .34 + i * z * .16} ${z * .6} ${-z * .28 + i * z * .16}`, stroke: '#b9a9ff', 'stroke-width': z * .04, fill: 'none', 'stroke-linecap': 'round' }); }
      S('path', { d: `M${z * .08} ${-z * .42} H${z * .24} V${z * .1} L${z * .16} ${z * .02} L${z * .08} ${z * .1} Z`, fill: T.LRN.STAR }); }
    if (kind === 'bulb') { S('circle', { cx: 0, cy: -z * .12, r: z * .48, fill: T.LRN.STAR }); S('rect', { x: -z * .22, y: z * .3, width: z * .44, height: z * .26, rx: z * .08, fill: '#6b5ce7' }); S('rect', { x: -z * .14, y: z * .54, width: z * .28, height: z * .1, rx: z * .05, fill: '#4b3fc4' });
      S('path', { d: `M${-z * .12} ${z * .3} V${z * .02} Q${-z * .22} ${-z * .2} ${-z * .04} ${-z * .14} Q${z * .12} ${-z * .2} ${z * .04} ${-z * .02} M${z * .12} ${z * .3} V${z * .02}`, stroke: '#fff', 'stroke-width': z * .05, fill: 'none', 'stroke-linecap': 'round' }); S('path', { d: `M${-z * .3} ${-z * .34} Q${-z * .22} ${-z * .48} ${-z * .08} ${-z * .5}`, stroke: '#fff7d0', 'stroke-width': z * .07, fill: 'none', 'stroke-linecap': 'round' }); }
    if (kind === 'notebook' || kind === 'pencil') { S('rect', { x: -z * .2, y: -z * .45, width: z * .62, height: z * .86, rx: z * .07, fill: T.LRN.GREEN, transform: 'rotate(-8)' }); S('rect', { x: -z * .02, y: -z * .3, width: z * .3, height: z * .14, rx: z * .03, fill: '#eafff8', transform: 'rotate(-8)' });
      for (let i = 0; i < 5; i++) S('circle', { cx: -z * .2 + i * 0, cy: -z * .34 + i * z * .17, r: z * .05, fill: 'none', stroke: '#4b3fc4', 'stroke-width': z * .025, transform: 'rotate(-8)' }); }
    if (kind === 'pencil') { const pg = K.sv(g, 'g', { transform: `translate(${-z * .25} ${z * .05}) rotate(38)` }); K.sv(pg, 'rect', { x: -z * .1, y: -z * .72, width: z * .2, height: z * .9, fill: T.LRN.RED }); K.sv(pg, 'rect', { x: -z * .1, y: -z * .86, width: z * .2, height: z * .16, rx: z * .06, fill: '#ff8a8a' }); K.sv(pg, 'rect', { x: -z * .1, y: -z * .72, width: z * .2, height: z * .08, fill: '#6b5ce7' });
      K.sv(pg, 'path', { d: `M${-z * .1} ${z * .18} L${z * .1} ${z * .18} L0 ${z * .42} Z`, fill: '#ffd7b0' }); K.sv(pg, 'path', { d: `M${-z * .04} ${z * .32} L${z * .04} ${z * .32} L0 ${z * .42} Z`, fill: '#2a1f66' }); }
    s.style.transformOrigin = '50% 50%'; return s; };
  /* little burst lines around an icon */
  T.rays = (L, cx, cy, r, n, a0, a1) => { const s = NSV(L, r * 3, r * 3, cx - r * 1.5, cy - r * 1.5, 5); for (let i = 0; i < n; i++) { const a = (a0 + (a1 - a0) * i / Math.max(1, n - 1)) * Math.PI / 180; K.sv(s, 'line', { x1: 1.5 * r + Math.cos(a) * r, y1: 1.5 * r + Math.sin(a) * r, x2: 1.5 * r + Math.cos(a) * r * 1.3, y2: 1.5 * r + Math.sin(a) * r * 1.3, stroke: T.LRN.STAR, 'stroke-width': 10, 'stroke-linecap': 'round' }); } s.style.transformOrigin = '50% 50%'; return s; };
  /* white dashed arc between two points (drawn in) */
  T.dashArc = (L, x1, y1, x2, y2, lift) => { const s = NSV(L, 1920, 1080, 0, 0, 5); const p = K.sv(s, 'path', { d: `M${x1} ${y1} Q${(x1 + x2) / 2} ${Math.min(y1, y2) - (lift || 80)} ${x2} ${y2}`, fill: 'none', stroke: '#fff', 'stroke-width': 5, 'stroke-linecap': 'round' }); p.l = p.getTotalLength(); return p; };
  T.dashArcAt = (p, u) => p.setAttribute('stroke-dasharray', dashUpTo(p.l * clamp(u)));
  /* open book with fanned pages and a glowing pink sunrise behind it */
  T.bigBook = (L, cx, by, w) => { const s = NSV(L, w * 1.4, w * .9, cx - w * .7, by - w * .7, 3); const ox = w * .7, oy = w * .7; const o = { s };
    o.glow = K.sv(s, 'g', {}); [[w * .42, 'rgba(232,67,143,.35)'], [w * .33, 'rgba(232,67,143,.6)'], [w * .24, '#ff4d8d']].forEach(([r, c]) => K.sv(o.glow, 'path', { d: `M${ox - r} ${oy - w * .12} A${r} ${r} 0 0 1 ${ox + r} ${oy - w * .12} Z`, fill: c }));
    o.rays = K.sv(s, 'g', {}); for (let i = 0; i < 5; i++) { const a = (-150 + i * 30) * Math.PI / 180; K.sv(o.rays, 'line', { x1: ox + Math.cos(a) * w * .1, y1: oy - w * .2 + Math.sin(a) * w * .1, x2: ox + Math.cos(a) * w * .17, y2: oy - w * .2 + Math.sin(a) * w * .17, stroke: T.LRN.STAR, 'stroke-width': 9, 'stroke-linecap': 'round' }); }
    K.sv(s, 'path', { d: `M${ox - w * .5} ${oy - w * .02} L${ox + w * .5} ${oy - w * .02} L${ox + w * .46} ${oy + w * .08} L${ox - w * .46} ${oy + w * .08} Z`, fill: T.LRN.GREEN });
    o.pages = []; for (let i = 0; i < 6; i++) { const k = i / 5; const lp = K.sv(s, 'path', { d: `M${ox} ${oy - w * .02} Q${ox - w * .2} ${oy - w * (.16 + .03 * k)} ${ox - w * (.44 - .02 * k)} ${oy - w * (.12 + .02 * k)} L${ox - w * .46} ${oy - w * .02} Z`, fill: i % 2 ? '#fff0d6' : T.LRN.CREAM, stroke: '#e9c9a0', 'stroke-width': 1.5 });
      const rp = K.sv(s, 'path', { d: `M${ox} ${oy - w * .02} Q${ox + w * .2} ${oy - w * (.16 + .03 * k)} ${ox + w * (.44 - .02 * k)} ${oy - w * (.12 + .02 * k)} L${ox + w * .46} ${oy - w * .02} Z`, fill: i % 2 ? '#fff0d6' : T.LRN.CREAM, stroke: '#e9c9a0', 'stroke-width': 1.5 }); o.pages.push(lp, rp); }
    K.sv(s, 'ellipse', { cx: ox, cy: oy + w * .02, rx: w * .06, ry: w * .045, fill: '#7d62e8' }); return o; };
  T.bigBookAt = (o, t, u) => { u = clamp(u); o.s.style.opacity = clamp(u * 3); o.glow.setAttribute('transform', `translate(0 ${30 * (1 - ease.out3(u))})`); o.glow.style.opacity = u; o.rays.style.opacity = .6 + .4 * Math.sin(t * 4);
    o.pages.forEach((p, i) => { const k = Math.sin(t * 2.2 + i * .5) * 2.5; p.setAttribute('transform', `rotate(${k * (i % 2 ? -1 : 1)} ${o.s.width.baseVal.value / 2} ${o.s.height.baseVal.value * .78})`); }); };
  /* sticky-note style goal chip */
  T.goal = (L, txt, x, y, col, rot) => el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: '44px', fontWeight: 900, color: '#2a1f66', background: col || T.LRN.STAR, padding: '14px 30px', borderRadius: '22px', transform: `rotate(${rot || 0}deg)`, transformOrigin: '0 50%', boxShadow: '0 10px 0 rgba(20,10,60,.3)', zIndex: 6 }, txt);

  /* ---------- T16 Comic Pop: sunburst + halftone, outlined comic clouds, zigzag split screens ---------- */
  T.CMC = { GREEN: ['#3fae2a', '#8fd63a'], YELLOW: ['#f7a90f', '#ffd43b'], BLUE: ['#1e8fe0', '#4cc3f5'], PURPLE: ['#7b3fb8', '#a868d8'], CYAN: ['#14b5e0', '#3fe6f5'], LIME: ['#4cd61f', '#a8f53a'],
    INK: '#111111', SHADE: '#d9e6f2', STAR: '#ffd21f', EN: "'Inter','Noto Sans CJK SC',sans-serif", CN: "'Noto Sans CJK SC',sans-serif" };
  /* sunburst rays (rotating) + halftone dots, clipped to an optional polygon. pal = [dark, light]. T.burstAt(b, t) */
  T.burst = (L, cx, cy, pal, clip, opts) => { const o = Object.assign({ rays: 18, dots: true, glow: true }, opts || {}); const box = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', overflow: 'hidden', clipPath: clip || 'none', background: pal[0] });
    const deg = 360 / o.rays; box.r = el(box, 'div', 'abs', { left: (cx - 1800) + 'px', top: (cy - 1800) + 'px', width: '3600px', height: '3600px', background: `repeating-conic-gradient(from 0deg, ${pal[1]} 0deg ${deg * .45}deg, ${pal[0]} ${deg * .45}deg ${deg}deg)` });
    if (o.glow) el(box, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: `radial-gradient(700px 500px at ${cx}px ${cy}px, rgba(255,255,190,.55), rgba(255,255,190,0) 70%)` });
    if (o.dots) el(box, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', backgroundImage: 'radial-gradient(rgba(0,0,0,.16) 3.2px, transparent 3.8px)', backgroundSize: '22px 22px', WebkitMaskImage: `radial-gradient(1100px 800px at ${cx}px ${cy}px, rgba(0,0,0,.15), rgba(0,0,0,1) 75%)` });
    box.cx = cx; box.cy = cy; return box; };
  T.burstAt = (b, t, speed) => { b.r.style.transform = `rotate(${t * (speed ?? 5)}deg)`; };
  /* white zigzag lightning divider between two halves; returns the two clip polygons + svg */
  T.zigzag = (L, pts) => { pts = pts || [[640, 0], [760, 330], [1010, 470], [1220, 1080]]; const s = K.svg(L, 1920, 1080, 0, 0); s.style.zIndex = 4; const d = 'M' + pts.map(p => p.join(' ')).join(' L');
    K.sv(s, 'path', { d, fill: 'none', stroke: T.CMC.INK, 'stroke-width': 40, 'stroke-linejoin': 'miter' }); K.sv(s, 'path', { d, fill: 'none', stroke: '#fff', 'stroke-width': 28, 'stroke-linejoin': 'miter' });
    const poly = pts.map(p => `${p[0]}px ${p[1]}px`).join(','); return { s, left: `polygon(0 0, ${poly}, 0 1080px)`, right: `polygon(${poly}, 1920px 1080px, 1920px 0)` }; };
  /* puffy comic cloud with thick black outline and soft inner shading. T.cloudAt(c, t) bobs it */
  T.comicCloud = (L, x, y, w, seed, z) => { const R = C.rng(seed || 7), h = w * .62, s = K.svg(L, w + 40, h + 40, x - 20, y - 20); s.style.zIndex = z || 5; const g = K.sv(s, 'g', { transform: 'translate(20 20)' });
    const cs = []; const n = 6; for (let i = 0; i < n; i++) { const a = Math.PI + i / (n - 1) * Math.PI; cs.push([w / 2 + Math.cos(a) * w * .36, h * .58 + Math.sin(a) * h * .34, w * (.17 + R() * .07)]); }
    for (let i = 0; i < 4; i++) cs.push([w * (.2 + i * .2), h * .74, w * (.13 + R() * .04)]);
    cs.forEach(([cx, cy, r]) => K.sv(g, 'circle', { cx, cy, r: r + 7, fill: T.CMC.INK })); K.sv(g, 'ellipse', { cx: w / 2, cy: h * .64, rx: w * .4, ry: h * .2, fill: T.CMC.SHADE }); cs.forEach(([cx, cy, r]) => K.sv(g, 'circle', { cx, cy, r, fill: T.CMC.SHADE })); K.sv(g, 'ellipse', { cx: w / 2, cy: h * .52, rx: w * .38, ry: h * .24, fill: '#fff' }); cs.forEach(([cx, cy, r]) => K.sv(g, 'circle', { cx: cx - r * .08, cy: cy - r * .14, r: r * .9, fill: '#fff' })); K.sv(g, 'ellipse', { cx: w / 2, cy: h * .55, rx: w * .36, ry: h * .2, fill: '#fff' });
    s.ph = R() * 6.28; s.by = y; return s; };
  T.cloudAt = (c, t, amp) => { c.style.transform = `translateY(${Math.sin(t * 1.3 + c.ph) * (amp ?? 8)}px)`; };
  /* outlined comic star (yellow with black edge) */
  T.cStar = (L, cx, cy, r, col) => { const s = K.svg(L, r * 3, r * 3, cx - r * 1.5, cy - r * 1.5); s.style.zIndex = 6; const p = []; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .48 : r; p.push((1.5 * r + rr * Math.cos(a)).toFixed(1) + ',' + (1.5 * r + rr * Math.sin(a)).toFixed(1)); }
    K.sv(s, 'polygon', { points: p.join(' '), fill: col || T.CMC.STAR, stroke: T.CMC.INK, 'stroke-width': Math.max(3, r * .14), 'stroke-linejoin': 'round' }); s.style.transformOrigin = '50% 50%'; return s; };
  /* black action wedges radiating from a point (emphasis marks) */
  T.action = (L, cx, cy, r, angles) => { const s = K.svg(L, 1920, 1080, 0, 0); s.style.zIndex = 6; (angles || [-150, -125, -35, -10, 30, 150, 205, 235]).forEach(a => { const A = a * Math.PI / 180, l = r * .35, w = 9;
      const x1 = cx + Math.cos(A) * r, y1 = cy + Math.sin(A) * r, x2 = cx + Math.cos(A) * (r + l), y2 = cy + Math.sin(A) * (r + l), nx = -Math.sin(A) * w, ny = Math.cos(A) * w;
      K.sv(s, 'polygon', { points: `${x1},${y1} ${x2 + nx},${y2 + ny} ${x2 - nx},${y2 - ny}`, fill: T.CMC.INK }); }); s.style.transformOrigin = `${cx}px ${cy}px`; return s; };
  /* comic lettering: heavy fill + thick black outline + hard offset shadow (EN or CN) */
  T.comicText = (L, txt, x, y, size, fill, opts) => { const o = Object.assign({ anchor: 'start', font: T.CMC.EN, rot: 0 }, opts || {}); const s = K.svg(L, 1920, Math.ceil(size * 1.5), 0, y); s.style.zIndex = 7; s.style.overflow = 'visible';
    const a = { x, y: size * 1.08, 'font-family': o.font, 'font-weight': 900, 'font-size': size, 'text-anchor': o.anchor, 'stroke-linejoin': 'round', 'paint-order': 'stroke', 'letter-spacing': size * .02 };
    const sh = K.sv(s, 'text', Object.assign({}, a, { x: x + size * .06, y: size * 1.08 + size * .06, fill: T.CMC.INK, stroke: T.CMC.INK, 'stroke-width': size * .16 })); sh.textContent = txt;
    const tx = K.sv(s, 'text', Object.assign({}, a, { fill: fill || '#fff', stroke: T.CMC.INK, 'stroke-width': size * .14 })); tx.textContent = txt;
    s.style.transformOrigin = `${o.anchor === 'middle' ? x : x + size}px ${size * .7}px`; if (o.rot) s.style.rotate = o.rot + 'deg'; return s; };
  /* big speech cloud with a title inside */
  T.speechCloud = (L, cx, cy, w, txt, size, font) => { const c = T.comicCloud(L, cx - w / 2, cy - w * .31, w, 11, 5); const t = el(L, 'div', 'abs', { left: (cx - w / 2) + 'px', width: w + 'px', top: (cy - (size || 64) * .55) + 'px', textAlign: 'center', fontFamily: font || "Georgia,'Noto Serif CJK SC',serif", fontSize: (size || 64) + 'px', fontWeight: 700, color: T.CMC.INK, zIndex: 6, whiteSpace: 'nowrap' }, txt);
    return { c, t }; };
  /* twinkling 4-point sparkles (white) */
  T.sparkles = (L, n, seed) => { const R = C.rng(seed || 3), s = K.svg(L, 1920, 1080, 0, 0); s.style.zIndex = 3; const a = []; for (let i = 0; i < n; i++) { const x = R() * 1920, y = R() * 700, r = 6 + R() * 12; const p = K.sv(s, 'path', { d: `M${x} ${y - r} Q${x} ${y} ${x + r} ${y} Q${x} ${y} ${x} ${y + r} Q${x} ${y} ${x - r} ${y} Q${x} ${y} ${x} ${y - r} Z`, fill: '#fff' }); a.push({ p, ph: R() * 6.28, sp: 2 + R() * 3 }); } return a; };
  T.sparklesAt = (a, t) => a.forEach(q => q.p.setAttribute('opacity', (.3 + .7 * Math.max(0, Math.sin(t * q.sp + q.ph))).toFixed(2)));
  /* row of clouds along the bottom (ground) */
  T.cloudGround = (L, y, n, seed) => { const out = []; const R = C.rng(seed || 2); for (let i = 0; i < n; i++) out.push(T.comicCloud(L, -120 + i * (2160 / n) + R() * 40, y - R() * 60, 2160 / n * 1.5, 30 + i, 5)); return out; };
  /* outlined sticker card for bullet points */
  T.sticker = (L, txt, x, y, bg, rot) => el(L, 'div', 'abs cn', { left: x + 'px', top: y + 'px', fontSize: '46px', fontWeight: 900, color: T.CMC.INK, background: bg || '#fff', border: `6px solid ${T.CMC.INK}`, borderRadius: '18px', padding: '10px 28px', boxShadow: `8px 8px 0 ${T.CMC.INK}`, transform: `rotate(${rot || 0}deg)`, transformOrigin: '0 50%', zIndex: 7, whiteSpace: 'nowrap' }, txt);

  /* ---------- T17 Science Network: plexus ribbon, plexus globe, sphere chain, tunnel, bokeh ---------- */
  T.SCN = { BG: '#03060f', CYAN: '#18e0f2', BLUE: '#2a7fff', ORANGE: '#ff8a3d', EN: "'Inter','Noto Sans CJK SC',sans-serif" };
  T.sciNetBg = 'radial-gradient(1400px 900px at 60% 45%, #0a1630, #03060f 70%)';
  const scv = (L, z, blur) => { const cv = el(L, 'canvas', 'abs', { left: 0, top: 0, zIndex: z || 2, filter: blur ? `blur(${blur}px)` : 'none' }); cv.width = 1920; cv.height = 1080; return cv; };
  const glowDot = (g, x, y, r, rgb, a) => { const gr = g.createRadialGradient(x, y, 0, x, y, r * 3); gr.addColorStop(0, `rgba(255,255,255,${a})`); gr.addColorStop(.25, `rgba(${rgb},${a})`); gr.addColorStop(1, `rgba(${rgb},0)`); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 3, 0, 7); g.fill(); };
  const NODECOL = (k) => k < .22 ? '255,140,60' : k < .55 ? '60,200,255' : '200,225,255';
  /* soft out-of-focus bokeh dots drifting. T.bokehAt(b, t) */
  T.bokeh = (L, n, seed) => { const R = C.rng(seed || 13), o = { cv: scv(L, 1, 6), p: [] }; for (let i = 0; i < (n || 40); i++) o.p.push([R() * 1920, R() * 1080, 8 + R() * 34, R() < .45 ? '255,130,60' : '60,150,255', .15 + R() * .35, (R() - .5) * 10]); return o; };
  T.bokehAt = (o, t) => { const g = o.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); for (const [x, y, r, c, a, v] of o.p) { const xx = (x + v * t + 1920) % 1920; const gr = g.createRadialGradient(xx, y, 0, xx, y, r); gr.addColorStop(0, `rgba(${c},${a})`); gr.addColorStop(.7, `rgba(${c},${a * .6})`); gr.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gr; g.beginPath(); g.arc(xx, y, r, 0, 7); g.fill(); } };
  /* rippling plexus ribbon: a 3D wave of connected nodes. opts {y, amp, width, cols, rows, tilt}. T.ribbonAt(r, t) */
  T.ribbon = (L, opts) => { const o = Object.assign({ y: 520, amp: 160, width: 220, cols: 46, rows: 7, x0: -100, x1: 2020, seed: 5 }, opts || {}); o.cv = scv(L, 3); const R = C.rng(o.seed); o.j = []; for (let i = 0; i < o.cols * o.rows; i++) o.j.push([(R() - .5) * .6, (R() - .5) * .6, R()]); return o; };
  T.ribbonAt = (o, t) => { const g = o.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); g.globalCompositeOperation = 'lighter'; const P2 = [];
    for (let i = 0; i < o.cols; i++) for (let j = 0; j < o.rows; j++) { const k = o.j[i * o.rows + j]; const u = (i + k[0]) / (o.cols - 1), v = (j + k[1]) / (o.rows - 1) - .5;
      const x = o.x0 + (o.x1 - o.x0) * u, ph = u * 7 - t * .9, cy = o.y - o.amp * Math.sin(ph) - u * 120, tw = Math.cos(ph * .8 + t * .4); const z = 1 + .35 * v * tw; P2.push([x + v * o.width * .3 * Math.sin(ph), cy + v * o.width * tw, z, k[2]]); }
    const idx = (i, j) => i * o.rows + j;
    g.lineWidth = 1.1; for (let i = 0; i < o.cols; i++) for (let j = 0; j < o.rows; j++) { const a = P2[idx(i, j)]; [[1, 0], [0, 1], [1, 1], [1, -1]].forEach(([di, dj]) => { const ii = i + di, jj = j + dj; if (ii >= o.cols || jj < 0 || jj >= o.rows) return; const b = P2[idx(ii, jj)]; const al = .18 + .22 * Math.min(a[2], b[2]); g.strokeStyle = `rgba(150,200,255,${al})`; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }); }
    for (const [x, y, z, k] of P2) glowDot(g, x, y, 2.2 + 1.8 * z, NODECOL(k), .55 + .35 * z);
    g.globalCompositeOperation = 'source-over'; };
  /* plexus sphere (optionally with real continents) rotating slowly. T.pSphereAt(s, t) */
  T.pSphere = (L, cx, cy, r, opts) => { const o = Object.assign({ cx, cy, r, n: 240, land: false, speed: 9, lon0: -60, tilt: 15, link: 1.0 }, opts || {}); o.cv = scv(L, 3); const R = C.rng(9); o.p = [];
    for (let i = 0; i < o.n; i++) { const y = 1 - (i + .5) / o.n * 2, rr = Math.sqrt(1 - y * y), th = i * 2.39996; o.p.push([Math.cos(th) * rr, y, Math.sin(th) * rr, R()]); }
    o.e = []; const th = o.link * 3.6 / Math.sqrt(o.n); for (let i = 0; i < o.n; i++) for (let j = i + 1; j < o.n; j++) { const a = o.p[i], b = o.p[j]; if (Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) < th) o.e.push([i, j]); }
    if (o.land) landPts(); return o; };
  T.pSphereAt = (o, t, u) => { const g = o.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); o.cv.style.opacity = u === undefined ? 1 : clamp(u); g.globalCompositeOperation = 'lighter';
    const rot = (o.lon0 + o.speed * t) * Math.PI / 180, ti = o.tilt * Math.PI / 180; const pr = (x, y, z) => { const x1 = x * Math.cos(rot) + z * Math.sin(rot), z1 = -x * Math.sin(rot) + z * Math.cos(rot); const y2 = y * Math.cos(ti) - z1 * Math.sin(ti), z2 = y * Math.sin(ti) + z1 * Math.cos(ti); return [o.cx + x1 * o.r, o.cy - y2 * o.r, z2]; };
    const gr = g.createRadialGradient(o.cx, o.cy, o.r * .2, o.cx, o.cy, o.r * 1.15); gr.addColorStop(0, 'rgba(20,60,140,.25)'); gr.addColorStop(.85, 'rgba(40,120,255,.12)'); gr.addColorStop(1, 'rgba(40,120,255,0)'); g.fillStyle = gr; g.beginPath(); g.arc(o.cx, o.cy, o.r * 1.15, 0, 7); g.fill();
    const Q = o.p.map(([x, y, z, k]) => pr(x, y, z).concat(k));
    g.lineWidth = 1; for (const [i, j] of o.e) { const a = Q[i], b = Q[j], d = (a[2] + b[2]) / 2; g.strokeStyle = `rgba(150,200,255,${(.08 + .32 * (d + 1) / 2).toFixed(3)})`; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }
    if (o.land && LANDPTS) { for (let n = 0; n < LANDPTS.length; n += 1) { const [lo, la] = LANDPTS[n]; const x = Math.cos(la) * Math.sin(lo), y = Math.sin(la), z = Math.cos(la) * Math.cos(lo); const [sx, sy, sz] = pr(x, y, z); if (sz < 0) continue; g.fillStyle = `rgba(185,225,255,${(.35 + .65 * sz).toFixed(2)})`; g.fillRect(sx - 1.4, sy - 1.4, 2.8, 2.8); } }
    for (const [x, y, z, k] of Q) { if (z < -.3) continue; glowDot(g, x, y, 2 + 1.6 * (z + 1) / 2, NODECOL(k), .35 + .55 * (z + 1) / 2); }
    g.globalCompositeOperation = 'source-over'; };
  /* plexus tunnel / vortex flowing toward the viewer. T.tunnelAt(o, t) */
  T.tunnel = (L, cx, cy, opts) => { const o = Object.assign({ cx, cy, rings: 22, per: 28, rmax: 900, speed: .35 }, opts || {}); o.cv = scv(L, 3); const R = C.rng(3); o.k = []; for (let i = 0; i < o.rings * o.per; i++) o.k.push(R()); return o; };
  T.tunnelAt = (o, t) => { const g = o.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080); g.globalCompositeOperation = 'lighter'; const rings = [];
    for (let i = 0; i < o.rings; i++) { const z = ((i / o.rings + t * o.speed * .1) % 1); const d = .06 + z * z * 1.0, rr = o.rmax * d, sp = t * .25 + i * .21; const pts = []; for (let j = 0; j < o.per; j++) { const a = j / o.per * 2 * Math.PI + sp; pts.push([o.cx + Math.cos(a) * rr * (1 + .08 * Math.sin(a * 3 + t)), o.cy + Math.sin(a) * rr * .82, z, o.k[i * o.per + j]]); } rings.push(pts); }
    rings.sort((a, b) => a[0][2] - b[0][2]);
    rings.forEach((pts, ri) => { const z = pts[0][2], al = Math.min(1, z * 1.6) * (1 - Math.max(0, z - .85) / .15); g.lineWidth = .6 + z * 1.4; g.strokeStyle = `rgba(120,190,255,${(.35 * al).toFixed(3)})`; g.beginPath(); pts.forEach(([x, y], j) => j ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.stroke();
      const nx = rings[ri + 1]; if (nx) { g.strokeStyle = `rgba(150,200,255,${(.18 * al).toFixed(3)})`; pts.forEach(([x, y], j) => { const q = nx[j]; g.beginPath(); g.moveTo(x, y); g.lineTo(q[0], q[1]); g.stroke(); }); }
      pts.forEach(([x, y, zz, k]) => glowDot(g, x, y, 1.2 + zz * 3, NODECOL(k), .6 * al)); });
    g.globalCompositeOperation = 'source-over'; };
  /* white headline with one cyan word + small sub line. T.sciHeadAt(h, t, t0) */
  T.sciHead = (L, lines, sub, x, y, size) => { size = size || 92; const d = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', zIndex: 8 }); d.ls = lines.map(l => el(d, 'div', '', { fontFamily: T.SCN.EN, fontWeight: 900, fontSize: size + 'px', lineHeight: 1.02, color: '#fff', whiteSpace: 'nowrap', textShadow: '0 4px 30px rgba(0,0,0,.6)' }, l.replace(/\[(.+?)\]/g, `<span style="color:${T.SCN.CYAN}">$1</span>`)));
    d.s = el(d, 'div', 'cn', { fontSize: (size * .32) + 'px', fontWeight: 400, color: '#e8f2ff', marginTop: '20px', lineHeight: 1.35, whiteSpace: 'pre' }, sub || ''); return d; };
  T.sciHeadAt = (d, t, t0) => { d.ls.forEach((l, i) => tf(l, slide(t, t0 + i * .14, .5, -60, 0))); tf(d.s, { o: P(t, t0 + .5, .4) }); };

})();
