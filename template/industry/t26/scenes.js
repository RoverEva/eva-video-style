/* T26 Real Estate Social (native 9:16 only) — Chinese social "property tour" look:
 * cut-out presenter with a white sticker outline, heavy dark headline with a white keyline and one red phrase,
 * yellow brush underline, yellow spark strokes, red hearts, icon list that builds up line by line.
 *
 * Data: window.RE from scripts/srt_to_beats.py (every on-screen word is copied from the SRT; nothing is rewritten).
 * Media (URL params, all optional):
 *   plate=IMG still background with the presenter removed (default ../media/re_plate.jpg; made from her own footage)
 *   bg=DIR    instead of the plate: 30 fps JPG frames for a moving background (property footage)
 *   cut=DIR   RGBA cut-out frames from scripts/matte.py (default ../media/re_cut)
 *   n=FRAMES  number of frames in those folders (default: end * 30)
 * With bg=DIR, a beat with `src: SECONDS` (srt_to_beats.py --bgcuts) cuts the footage to that shot when the beat starts.
 * A beat may carry `bg: 'path/to/photo.jpg'` (a real property photo) to replace the footage background for that beat. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, D = window.RE, Q = C.params;
  const BG = Q.get('bg'), PLATE = Q.get('plate') || '../media/re_plate.jpg', CUT = Q.get('cut') || '../media/re_cut', N = +(Q.get('n') || Math.round(D.end * 30));
  const INK = '#2b1a12', RED = '#ff2d4b', YEL = '#ffd21f', FONT = "'Noto Sans CJK SC', 'Noto Sans SC', sans-serif";
  C.end = D.end; C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, o: 0 } }]; C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });

  const hero = D.beats.find(b => b.role === 'hero'), close = D.beats.find(b => b.role === 'close'), items = D.beats.filter(b => b.role === 'item');
  const A1 = items.length ? items[0].t0 - .15 : (close ? close.t0 - .1 : D.end), B1 = close ? close.t0 - .1 : D.end;
  /* when a phrase inside a line is spoken: proportional to its character position (SRT has line timing only) */
  const wordAt = (b, s) => { const i = Math.max(0, b.text.indexOf(s)); return b.t0 + (b.t1 - b.t0) * i / Math.max(1, b.text.length); };

  /* ---------- design pieces ---------- */
  const outline = (r, col) => { const s = []; for (let a = 0; a < 16; a++) { const q = a / 16 * Math.PI * 2; s.push(`${(Math.cos(q) * r).toFixed(1)}px ${(Math.sin(q) * r).toFixed(1)}px 0 ${col}`); } return s.join(',') + `, 0 ${r * 1.4}px ${r * 2.2}px rgba(60,30,10,.28)`; };
  const txt = (p, html, size, x, y, extra) => el(p, 'div', 'abs', Object.assign({ left: x + 'px', top: y + 'px', fontFamily: FONT, fontWeight: 900, fontSize: size + 'px', lineHeight: 1.12, color: INK, whiteSpace: 'nowrap', textShadow: outline(Math.max(5, size * .085), '#fff'), transformOrigin: '0 60%' }, extra || {}), html);
  const hlLine = (line, hl, big) => hl && line.includes(hl) ? line.replace(hl, `<span style="color:${RED};font-size:${big}em">${hl}</span>`) : line;
  const svg = (p, w, h, x, y, z) => { const s = k.svg(p, w, h, x, y); s.style.zIndex = z || 5; return s; };
  const brush = (p, x, y, w) => { const s = svg(p, w + 40, 60, x - 20, y); const d = `M20 38 C ${w * .3} 18, ${w * .65} 30, ${w + 20} 16`;
    const a = k.sv(s, 'path', { d, fill: 'none', stroke: YEL, 'stroke-width': 22, 'stroke-linecap': 'round', 'stroke-dasharray': w * 1.2, 'stroke-dashoffset': w * 1.2 }); a.len = w * 1.2; return a; };
  const brushAt = (a, u) => a.setAttribute('stroke-dashoffset', (a.len * (1 - ease.out3(u))).toFixed(1));
  const sparks = (p, x, y, rot) => { const s = svg(p, 120, 120, x, y); s.style.transformOrigin = '60px 60px'; s.style.transform = `rotate(${rot || 0}deg)`;
    [[18, 70, 46, 82], [40, 34, 70, 58], [74, 14, 92, 46]].forEach(([a, b, c, d]) => k.sv(s, 'line', { x1: a, y1: b, x2: c, y2: d, stroke: YEL, 'stroke-width': 13, 'stroke-linecap': 'round' })); return s; };
  const heart = (p, x, y, size) => { const s = svg(p, size, size, x, y, 6); s.setAttribute('viewBox', '0 0 100 100'); s.style.transformOrigin = '50% 50%';
    k.sv(s, 'path', { d: 'M50 86 C 18 64, 6 46, 10 30 C 14 14, 36 8, 50 26 C 64 8, 86 14, 90 30 C 94 46, 82 64, 50 86 Z', fill: '#fff', stroke: RED, 'stroke-width': 9, 'stroke-linejoin': 'round' }); return s; };
  const ICON = {
    sun: s => { k.sv(s, 'circle', { cx: 50, cy: 50, r: 19, fill: YEL, stroke: INK, 'stroke-width': 6 }); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; k.sv(s, 'line', { x1: 50 + Math.cos(a) * 30, y1: 50 + Math.sin(a) * 30, x2: 50 + Math.cos(a) * 42, y2: 50 + Math.sin(a) * 42, stroke: INK, 'stroke-width': 6, 'stroke-linecap': 'round' }); } },
    space: s => { k.sv(s, 'rect', { x: 26, y: 26, width: 48, height: 48, rx: 6, fill: YEL, stroke: INK, 'stroke-width': 6 });
      [['M10 26 V10 H26', 'M16 16 L32 32'], ['M74 10 H90 V26', 'M84 16 L68 32'], ['M10 74 V90 H26', 'M16 84 L32 68'], ['M90 74 V90 H74', 'M84 84 L68 68']].forEach(([a, b]) => { k.sv(s, 'path', { d: a, fill: 'none', stroke: INK, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); k.sv(s, 'path', { d: b, stroke: INK, 'stroke-width': 6, 'stroke-linecap': 'round' }); }); },
    tree: s => { k.sv(s, 'path', { d: 'M50 10 C 74 10, 86 30, 80 48 C 90 60, 80 78, 62 76 L 38 76 C 20 78, 10 60, 20 48 C 14 30, 26 10, 50 10 Z', fill: YEL, stroke: INK, 'stroke-width': 6, 'stroke-linejoin': 'round' });
      k.sv(s, 'path', { d: 'M50 40 V94 M50 58 L36 46 M50 66 L64 54', fill: 'none', stroke: INK, 'stroke-width': 6, 'stroke-linecap': 'round' }); },
    house: s => { k.sv(s, 'path', { d: 'M12 48 L50 14 L88 48 M22 40 V88 H78 V40', fill: 'none', stroke: INK, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); k.sv(s, 'rect', { x: 40, y: 58, width: 20, height: 30, fill: YEL, stroke: INK, 'stroke-width': 6 }); },
    check: s => { k.sv(s, 'rect', { x: 12, y: 12, width: 76, height: 76, rx: 14, fill: YEL, stroke: INK, 'stroke-width': 6 }); k.sv(s, 'path', { d: 'M28 52 L44 68 L74 32', fill: 'none', stroke: INK, 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); },
  };
  const icon = (p, name, x, y, size) => { const s = svg(p, size, size, x, y, 6); s.setAttribute('viewBox', '0 0 100 100'); s.style.transformOrigin = '50% 50%'; (ICON[name] || ICON.check)(s); s.style.filter = 'drop-shadow(0 0 0 #fff) drop-shadow(3px 0 0 #fff) drop-shadow(-3px 0 0 #fff) drop-shadow(0 3px 0 #fff) drop-shadow(0 -3px 0 #fff)'; return s; };

  /* ---------- background + cut-out presenter (whole video) ---------- */
  /* 16:9: presenter stands in the right third (x = offset of her centre from the frame centre), text in the left two thirds */
  const V = C.portrait, pk = C.pick, PW = V ? C.W : Math.round(C.H * 9 / 16);
  const POSE = pk([{ x: 420, y: 40, s: 1.04 }, { x: 500, y: 60, s: .98 }, { x: 400, y: 70, s: 1.02 }], [{ x: 30, y: 60, s: 1.0 }, { x: 330, y: 110, s: .92 }, { x: 40, y: 560, s: .96 }]);
  const BGZ = [{ s: 1.16, ox: 50, oy: 40 }, { s: 1.55, ox: 15, oy: 18 }, { s: 1.22, ox: 60, oy: 30 }];
  /* background shots: each beat with `src` starts its own shot (items cut a little before they are spoken) */
  const SHOTS = BG ? D.beats.filter(b => b.src != null).map(b => ({ at: b.role === 'hero' ? 0 : b.role === 'close' ? b.t0 - .1 : b.t0 - .15, src: b.src })) : [];
  const shotAt = t => SHOTS.reduce((m, s) => t >= s.at ? s : m, SHOTS[0]);
  const beatIx = t => t < A1 ? 0 : t < B1 ? 1 : 2, starts = [0, A1, B1];
  const blend = (arr, t) => { const i = beatIx(t), u = i ? ease.outBack(P(t, starts[i], .5), 1.2) : 1, a = arr[Math.max(0, i - 1)], b = arr[i], o = {}; for (const key in b) o[key] = lerp(a[key], b[key], u); return o; };
  C.scene({ t0: 0, t1: D.end + .05, bg: '#efe6dc', quiet: true, build(L) {
      const st = {}; st.bgw = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', overflow: 'hidden' });
      st.bg = el(st.bgw, 'img', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', objectFit: 'cover', filter: Q.get('bg') ? 'none' : 'blur(10px) brightness(1.07) saturate(.92)' });
      el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', background: 'linear-gradient(180deg, rgba(255,250,242,.22), rgba(255,246,236,.06) 50%, rgba(70,45,30,.16))' });
      st.pw = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', zIndex: 3, transformOrigin: '50% 100%' });
      st.p = el(st.pw, 'img', 'abs', { left: ((C.W - PW) / 2) + 'px', top: 0, width: PW + 'px', height: C.H + 'px',
        filter: 'drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 18px 30px rgba(70,40,20,.35))' });
      st.fl = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', background: '#fff', zIndex: 40, opacity: 0 }); return st; },
    update(lt, st, t) { const i = beatIx(t), b = D.beats.find(x => x.bg && t >= x.t0 - .2 && t < x.t1 + .2), sh = shotAt(t);
      C.setSrc(st.bg, b ? b.bg : BG ? C.seq(BG, sh ? sh.src + t - sh.at : t) : PLATE); const z = BG ? { s: 1, ox: 50, oy: 50 } : BGZ[i], push = 1 + .035 * P(t, sh ? sh.at : starts[i], 4);
      st.bg.style.transformOrigin = `${z.ox}% ${z.oy}%`; st.bg.style.transform = `scale(${(z.s * push).toFixed(4)})`;
      C.setSrc(st.p, `${CUT}/f_${String(Math.min(N - 1, Math.round(t * 30))).padStart(5, '0')}.webp`);
      const p = blend(POSE, t); tf(st.pw, { x: p.x, y: p.y + 6 * Math.sin(t * 1.6), s: p.s * (1 + .006 * Math.sin(t * 2.1)) });
      st.fl.style.opacity = Math.max(...starts.slice(1).map(s => t >= s ? .55 * (1 - P(t, s, .28)) : 0), ...SHOTS.slice(1).map(s => t >= s.at ? .35 * (1 - P(t, s.at, .22)) : 0)); } });

  /* ---------- A · hero line: two-line headline over the presenter's body ---------- */
  if (hero) C.scene({ t0: 0, t1: A1 + .03, z: 10, quiet: true, build(L) {
      const st = {}, [l1, l2] = hero.lines, hat = wordAt(hero, hero.hl || l2);
      st.sp = sparks(L, pk(70, 34), pk(470, 980), -20); st.a = C.fit(txt(L, hlLine(l1, hero.hl, 1.22), pk(104, 98), pk(110, 64), pk(560, 1050)), pk(1060, 952));
      st.b = C.fit(txt(L, hlLine(l2, hero.hl, 1.22), pk(112, 104), pk(110, 64), pk(690, 1172)), pk(1060, 952)); st.u = brush(L, pk(116, 70), pk(845, 1316), pk(900, 820)); st.h = heart(L, pk(1010, 880), pk(450, 960), pk(130, 120));
      st.at = [hero.t0, hero.t0 + .25, hat, hat + .25]; k.sfx('pop', hero.t0, .12); k.sfx('impact', hat, .12); k.sfx('pop', hat + .3, .1, { f: 1200 }); return st; },
    update(lt, st, t) { const [a, b, h, u] = st.at; tf(st.a, slide(t, a, .45, 0, 50)); const q = pop(t, b, .45, 1.6); tf(st.b, q);
      brushAt(st.u, P(t, u, .5)); const s = pop(t, a + .15, .35, 2); tf(st.sp, { s: s.s, o: s.o }); st.sp.style.transform += ' rotate(-20deg)';
      const hh = pop(t, h, .4, 2.4); tf(st.h, { s: hh.s * (1 + .06 * Math.sin(t * 6)), o: hh.o, r: 12 }); } });

  /* ---------- B · icon list builds line by line, presenter on the right ---------- */
  if (items.length) C.scene({ t0: A1, t1: B1 + .03, z: 10, build(L) {
      const st = {}, n = items.length, gap = pk(Math.min(230, 700 / n), Math.min(262, 780 / n)), y0 = pk(540 - (n - 1) * gap / 2 - 60, 640 - (n - 1) * gap / 2 + 120);
      st.sp = sparks(L, pk(70, 40), y0 - 150, -10);
      st.rows = items.map((b, i) => { const r = el(L, 'div', 'abs', { left: '0px', top: '0px', width: C.W + 'px', height: '0px', transformOrigin: `120px ${y0 + i * gap + 60}px` });
        icon(r, b.icon, pk(110, 56), y0 + i * gap, pk(140, 132)); const tx = V ? txt(r, b.text, 76, 210, y0 + i * gap + 14, { whiteSpace: 'normal', width: '400px', lineHeight: 1.08 }) : C.fit(txt(r, b.text, 88, 280, y0 + i * gap + 16), 820); return r; });
      items.forEach((b, i) => k.sfx('pop', b.t0, .12, { f: 800 + i * 140 })); return st; },
    update(lt, st, t) { const s = pop(t, A1 + .1, .35, 2); tf(st.sp, { s: s.s, o: s.o }); st.sp.style.transform += ' rotate(-10deg)';
      st.rows.forEach((r, i) => { const b = items[i], q = pop(t, b.t0, .42, 1.7), sl = slide(t, b.t0, .42, -80, 0); tf(r, { x: sl.x, s: q.s, o: q.o }); }); } });

  /* ---------- C · closing line: big headline on top, presenter lower ---------- */
  if (close) C.scene({ t0: B1, t1: D.end + .05, z: 10, build(L) {
      const st = {}, [l1, l2] = close.lines, hat = wordAt(close, close.hl || l2);
      st.sp = sparks(L, pk(70, 30), pk(300, 200), -24); st.a = C.fit(txt(L, hlLine(l1, close.hl, 1.2), pk(132, 128), pk(116, 72), pk(360, 250)), pk(1040, 940));
      st.b = C.fit(txt(L, hlLine(l2, close.hl, 1.2), pk(144, 136), pk(116, 72), pk(510, 400)), pk(1040, 940)); st.u = brush(L, pk(124, 80), pk(720, 600), pk(640, 640)); st.h = heart(L, pk(690, 800), pk(560, 380), 150);
      st.at = [close.t0, hat, hat + .3]; k.sfx('pop', close.t0, .12); k.sfx('ding', hat + .1, .07); return st; },
    update(lt, st, t) { const [a, h, u] = st.at; tf(st.a, slide(t, a, .45, 0, 50)); tf(st.b, pop(t, h, .45, 1.8)); brushAt(st.u, P(t, u, .5));
      const s = pop(t, a + .1, .35, 2); tf(st.sp, { s: s.s, o: s.o }); st.sp.style.transform += ' rotate(-24deg)';
      const hh = pop(t, h + .15, .4, 2.4); tf(st.h, { s: hh.s * (1 + .07 * Math.sin(t * 7)), o: hh.o, r: -10 }); } });
})();
