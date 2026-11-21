/* EVA template showcase · P15 Orb Guide × P12 Option Orbit · 24.4 s, cut to the supplied music (172 BPM).
 * 0–5.1  P15 intro: blue nebula, black glass orb, title letters slide in behind the orb, scrolling template column, presenter circle.
 * 5.1–13.4  P15 beat section: on every second beat the orb lands and a template clip pops out of it (liquid blue↔white wipes from the orb).
 * 13.4–15.3 break: wipe to the P12 stage, cards fly onto the sphere.  15.3–22.4 drop: sphere spins fast, card rows stream past,
 * camera dives on strong beats.  22.4–24.4 P12 final pick + CTA.  Card media = real renders of the EVA concept templates (T30–T100).
 * Nebula + orb are drawn procedurally (P15 source assets not available here). */
(function () {
  const C = EV, M = K.T.mo, { el, clamp } = C, f = M.f, MED = '../../sample10/media/montage/', INTER = "Inter, 'Noto Sans CJK SC', sans-serif";
  const W = 1920, H = 1080, END = 24.4;
  C.end = END; C.src0 = 0; C.evaDir = '../../sample10/media/eva1080'; C.src = { w: 1920, h: 1080 }; C.face = { x: .52, y: .3, h: .34 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 60, y: 820, w: 170, h: 170, r: 85, o: 0, s: 1.6 } }, { t: .9, d: .45, L: { x: 60, y: 820, w: 170, h: 170, r: 85, o: 1, s: 1.6 } }, { t: 4.7, d: .3, L: { x: 60, y: 820, w: 170, h: 170, r: 85, o: 0, s: 1.6 } }];
  C.ringFn = () => ({ color: 'rgba(255,255,255,.9)', width: 4, shadow: .45 });
  const NM = { T38: ['NEON', 'Neon Night 霓虹夜店'], T48: ['RETRO', 'Synthwave 合成波'], T33: ['INK', 'Ink Wash 水墨国风'], T76: ['FESTIVE', 'Lunar New Year 新春红金'], T36: ['PIXEL', 'Pixel Game 像素游戏'], T79: ['GLITCH', 'Glitch 故障风'],
    T47: ['FILM', 'Film Strip 胶片放映'], T61: ['QUIZ', 'Quiz Show 问答竞猜'], T46: ['TRAVEL', 'Boarding Pass 登机牌'], T87: ['LOGO', 'Logo Shatter 碎片重组'], T81: ['COSMIC', 'Galaxy 星空宇宙'], T52: ['POP', 'Memphis 孟菲斯'],
    T86: ['', 'Logo Light Sweep 金属扫光'], T74: ['', 'Spotlight Stage 聚光舞台'], T49: ['', 'Y2K Chrome 千禧金属'], T85: ['', 'Logo Liquid 液体溅落'], T37: ['', 'Magazine 杂志封面'] };
  const BEAT = [5.13, 5.94, 6.66, 7.48, 8.17, 8.89, 9.71, 10.40, 11.59, 12.28, 12.86], BK = ['T38', 'T48', 'T33', 'T76', 'T36', 'T79', 'T47', 'T61', 'T46', 'T87', 'T81'];
  const DIVE = [[16.02, 'T86'], [17.90, 'T74'], [19.78, 'T49'], [21.29, 'T85']], DROP = [15.33, 15.67, 16.02, 16.37, 16.6, 17.21, 17.55, 17.9, 18.25, 18.72, 19.06, 19.41, 19.78, 20.11, 20.36, 20.6, 20.94, 21.29, 21.64, 21.99];
  const TH = []; for (let i = 30; i <= 100; i++) TH.push(MED + 'th/T' + i + '.jpg');
  /* backgrounds in order; each grows as a circle from the orb at its start time */
  const BG = [[0, 'neb'], [5.13, 'white'], [8.17, 'neb'], [11.59, 'white'], [13.44, 'p12']];
  const blue = t => { let k = 0; BG.forEach((b, i) => { if (t >= b[0] + .2) k = i; }); return BG[k][1] === 'neb'; };
  /* orb path: keyframes [t, x, y] */
  const OK = [[0, 810, 551], [.35, 810, 551], [.95, 90, 200], [1.9, 1060, 200], [2.15, 90, 350], [2.8, 760, 350], [3.5, 330, 520], [4.6, 860, 600], [5.13, 960, 540]];
  const anchor = i => i % 2 ? [450, 300] : [660, 330];   /* card top-left corner = orb landing spot */
  BEAT.forEach((b, i) => { const [x, y] = anchor(i); OK.push([b - .26, OK[OK.length - 1][1], OK[OK.length - 1][2]]); OK.push([b, x, y]); });
  OK.push([13.2, 660, 330], [13.44, 960, 540]);
  const orbAt = t => { let a = OK[0], b = OK[OK.length - 1]; for (let i = 0; i < OK.length - 1; i++) if (t >= OK[i][0] && t <= OK[i + 1][0]) { a = OK[i]; b = OK[i + 1]; break; }
    if (t > OK[OK.length - 1][0]) return [b[1], b[2]]; const u = M.io((t - a[0]) / Math.max(.001, b[0] - a[0])), lift = Math.sin(u * Math.PI) * Math.min(120, Math.hypot(b[1] - a[1], b[2] - a[2]) * .25);
    return [a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u - lift]; };
  /* sphere spin angle: integral of speed (slow → fast in the drop → slow) */
  const speed = t => 22 + 190 * clamp((t - 15.1) / .5) * (1 - clamp((t - 22.1) / .6)) + 40 * clamp((t - 13.4) / 1.5) * (1 - clamp((t - 15.3) / .4));
  const ANG = []; { let a = 0; for (let i = 0; i <= END * 30 + 2; i++) { ANG.push(a); a += speed(i / 30) / 30; } }
  const spin = t => ANG[Math.min(ANG.length - 1, Math.max(0, Math.round(t * 30)))];
  const beatK = (t, list, d) => list.reduce((a, b) => Math.max(a, t >= b ? Math.exp(-(t - b) / (d || .12)) : 0), 0);
  C.scene({ t0: 0, t1: END + .1, bg: '#0a1a4a', quiet: true,
    build(L) { const s = {};
      /* ---- backgrounds ---- */
      s.bg = BG.map(([t0, k]) => { const d = M.box(L, 0, 0, { width: W + 'px', height: H + 'px', overflow: 'hidden', background: k === 'white' ? '#f4f4f7' : k === 'p12' ? '#EEECE8' : '#0a1a4a' });
        if (k === 'neb') { d.im = el(d, 'img', 'abs', { left: '-60px', top: '-40px', width: (W + 120) + 'px', height: (H + 80) + 'px', transformOrigin: '42% 51%' }); d.im.src = MED + 'neb_16x9.jpg'; }
        if (k === 'white') d.trail = el(d, 'canvas', 'abs', { left: 0, top: 0, width: W + 'px', height: H + 'px' }); d.t0 = t0; return d; });
      /* ---- P15 intro: title, subtitle, scrolling template column ---- */
      s.col = M.box(L, 1330, 0, { width: '420px', height: H + 'px', perspective: '1200px' });
      s.colIn = el(s.col, 'div', 'abs', { left: 0, top: 0, width: '420px', transform: 'rotateY(-20deg) rotateX(6deg)', transformStyle: 'preserve-3d' });
      s.colC = Array.from({ length: 10 }, (_, i) => { const c = el(s.colIn, 'img', 'abs', { left: (i % 2 ? 40 : 0) + 'px', top: (i * 250) + 'px', width: '380px', height: '214px', borderRadius: '12px', boxShadow: '0 16px 30px rgba(0,0,0,.45)', objectFit: 'cover' }); c.src = TH[(i * 7 + 3) % TH.length]; return c; });
      const word = (x, y, txt, col) => { const b = M.box(L, x, y, { display: 'flex', whiteSpace: 'pre', font: f(900, 150, INTER), color: col || '#fff', lineHeight: 1, letterSpacing: '-.01em' }); return [...txt].map(ch => { const e = el(b, 'span', '', { display: 'inline-block' }, ch); e.x0 = x; return e; }); };
      const lt = (txt, x, y) => word(x, y, txt);
      s.l1 = lt('EVA VIDEO', 90, 130); s.l2 = lt('STYLE', 90, 280);
      s.sub = M.txt(L, 96, 450, f(600, 34, INTER), 'rgba(255,255,255,.9)', '100 templates · 100 款模版 · 一键成片');
      /* ---- P15 beat cards ---- */
      s.key = M.box(L, 90, 70, {}); s.keyL = [];
      s.cards = BK.map((k, i) => { const [ax, ay] = anchor(i), c = M.box(L, ax, ay, { width: '816px', height: '459px', borderRadius: '18px', overflow: 'hidden', boxShadow: '0 30px 60px rgba(10,20,60,.35)', transformOrigin: '0 0', background: '#000' });
        c.im = el(c, 'img', 'abs', { left: 0, top: 0, width: '816px', height: '459px' }); c.k = k;
        c.lb = M.txt(L, ax, ay + 478, f(800, 30, INTER), '#111', `${k} · ${NM[k][1]}`, { background: '#fff', padding: '8px 18px', borderRadius: '999px', boxShadow: '0 8px 18px rgba(0,0,0,.15)' }); return c; });
      s.kw = BK.map(k => word(90, 80, NM[k][0]));
      /* ---- P12 sphere ---- */
      s.sph = M.box(L, 960, 540, { width: '0px', height: '0px', perspective: '1500px' });
      s.ball = el(s.sph, 'div', 'abs', { left: 0, top: 0, transformStyle: 'preserve-3d' });
      const R = 380, CW = 128, CH = 72; s.R = R; s.sc = []; let k = 0;
      for (let lat = -72; lat <= 72; lat += 16) { const n = Math.max(5, Math.round(2 * Math.PI * R * Math.cos(lat * Math.PI / 180) / (CW + 14)));
        for (let j = 0; j < n; j++) { const lon = j * 360 / n + (lat / 16) * 11, c = el(s.ball, 'img', 'abs', { left: (-CW / 2) + 'px', top: (-CH / 2) + 'px', width: CW + 'px', height: CH + 'px', borderRadius: '6px', objectFit: 'cover', backfaceVisibility: 'visible',
          transform: `rotateY(${lon}deg) rotateX(${-lat}deg) translateZ(${R}px)` }); c.src = TH[(k * 13) % TH.length]; c.lat = lat * Math.PI / 180; c.lon = lon * Math.PI / 180; c.k = k++; s.sc.push(c); } }
      s.arcs = M.svg(L, 460, 40, 1000, 1000, `<circle cx="500" cy="500" r="470" fill="none" stroke="#18181A" stroke-width="2" stroke-dasharray="380 2600" opacity=".55"/><circle cx="500" cy="500" r="440" fill="none" stroke="#18181A" stroke-width="2" stroke-dasharray="240 2600" opacity=".35"/>`, { transformOrigin: '50% 50%' });
      s.rows = [60, 880].map((y, r) => { const row = M.box(L, 0, y, { width: '6000px', height: '135px', display: 'flex', gap: '16px' }); for (let i = 0; i < 24; i++) { const c = el(row, 'img', '', { width: '240px', height: '135px', borderRadius: '10px', objectFit: 'cover', boxShadow: '0 10px 20px rgba(0,0,0,.18)' }); c.src = TH[(i * 5 + r * 31) % TH.length]; } return row; });
      s.p12t = M.box(L, 90, 90, {}); M.txt(s.p12t, 0, 0, f('italic 400', 84, M.PF), '#18181A', 'Choose', { position: 'static', display: 'inline' }); M.txt(s.p12t, 0, 0, f(500, 80, INTER), '#18181A', ' one template', { position: 'static', display: 'inline' });
      s.p12d = M.txt(L, 96, 200, f(600, 26, INTER), '#18181A', '● 选一个，或混搭几个 · Pick one or mix a few'); s.p12d.firstChild && 0;
      s.mix = M.box(L, 1440, 720, { textAlign: 'right', width: '400px' }); M.txt(s.mix, 0, 0, f('italic 400', 64, M.PF), '#18181A', 'Mix', { position: 'static' }); M.txt(s.mix, 0, 0, f(500, 52, INTER), '#18181A', 'and match', { position: 'static' });
      s.dive = DIVE.map(([t0, k]) => { const c = M.box(L, 360, 200, { width: '1200px', height: '675px', borderRadius: '22px', overflow: 'hidden', boxShadow: '0 40px 80px rgba(0,0,0,.35)', transformOrigin: '50% 50%', background: '#000' });
        c.im = el(c, 'img', 'abs', { left: 0, top: 0, width: '1200px', height: '675px' }); c.k = k; c.t0 = t0; c.lb = M.txt(c, 24, 600, f(800, 28, INTER), '#111', `${k} · ${NM[k][1]}`, { background: '#fff', padding: '8px 18px', borderRadius: '999px' }); return c; });
      /* ---- final pick ---- */
      s.fin = M.box(L, 660, 250, { width: '760px', height: '428px', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 30px 60px rgba(0,0,0,.25)', transformOrigin: '50% 50%', background: '#000' }); s.fin.im = el(s.fin, 'img', 'abs', { left: 0, top: 0, width: '760px', height: '428px' });
      s.chk = M.box(L, 1380, 230, { width: '64px', height: '64px', borderRadius: '50%', background: '#F25C26', color: '#fff', font: f(900, 40, INTER), display: 'flex', alignItems: 'center', justifyContent: 'center', transformOrigin: '50% 50%' }, '✓');
      s.ft = M.box(L, 90, 90, {}); M.txt(s.ft, 0, 0, f('italic 400', 84, M.PF), '#18181A', 'Your', { position: 'static', display: 'inline' }); M.txt(s.ft, 0, 0, f(500, 80, INTER), '#18181A', ' video style', { position: 'static', display: 'inline' });
      s.try = M.txt(L, 830, 720, f(700, 40, INTER), '#fff', 'Try it today  →', { background: '#18181A', padding: '16px 44px', borderRadius: '999px', transformOrigin: '50% 50%' });
      s.url = M.txt(L, 0, 820, f(600, 30, INTER), '#555', 'EvaVideoStudio.com · 100 templates', { width: W + 'px', textAlign: 'center' });
      /* ---- chrome + pill ---- */
      s.chL = M.txt(L, 60, 30, f(700, 24, INTER), '#fff', 'Eva Video Studio'); s.chR = M.txt(L, 1640, 30, f(600, 24, INTER), '#fff', 'Index, Templates ◐');
      s.cnt = M.txt(L, 1700, 1010, f(700, 24, M.MONO), '#0a1a4a', '01 / 100 ↗', { background: '#fff', padding: '4px 10px' });
      s.pill = M.box(L, 760, 990, { display: 'flex', alignItems: 'center', gap: '22px', background: '#fff', borderRadius: '999px', padding: '10px 26px 10px 10px', boxShadow: '0 8px 20px rgba(0,0,0,.12)' });
      el(s.pill, 'div', '', { width: '44px', height: '44px', borderRadius: '50%', background: '#18181A', color: '#fff', font: f(700, 30, INTER), display: 'flex', alignItems: 'center', justifyContent: 'center' }, '+'); el(s.pill, 'div', '', { font: f(600, 24, INTER), color: '#18181A' }, 'Templates ¹⁰⁰'); el(s.pill, 'div', '', { font: f(600, 24, INTER), color: '#18181A' }, 'Try it today');
      /* ---- orb (black glass) + streak ---- */
      s.ghost = Array.from({ length: 8 }, (_, i) => M.box(L, 0, 0, { width: '46px', height: '46px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(140,200,255,.55), rgba(60,120,255,0) 70%)' }));
      s.orb = M.box(L, 0, 0, { width: '46px', height: '46px', borderRadius: '50%', background: 'radial-gradient(circle at 34% 28%, #9fb3d6 0 6%, #1d2433 22%, #05070c 62%, #000 100%)', boxShadow: '0 8px 18px rgba(0,0,0,.45), inset -4px -6px 10px rgba(255,255,255,.08)' });
      s.tr = s.bg[1].trail.getContext('2d'); s.bg[1].trail.width = W; s.bg[1].trail.height = H;
      return s; },
    update(lt, s, t) {
      const [ox, oy] = orbAt(t), isBlue = blue(t), onP12 = t >= 13.6;
      /* backgrounds: circle wipes from the orb */
      s.bg.forEach((d, i) => { const r = i === 0 ? 3000 : 2300 * M.io((t - d.t0) / .5), [cx, cy] = orbAt(d.t0); d.style.display = t >= d.t0 ? '' : 'none'; d.style.clipPath = i === 0 ? '' : `circle(${r.toFixed(0)}px at ${cx.toFixed(0)}px ${cy.toFixed(0)}px)`;
        if (d.im) d.im.style.transform = `scale(${(1.06 + .02 * Math.sin(t * .4)).toFixed(4)}) rotate(${(t * 1.2).toFixed(2)}deg)`; });
      /* nebula paint trail on the white page (P15 V03): stamp the orb's path */
      if (t >= 5.13 && t < 8.3) { const g = s.tr; g.clearRect(0, 0, W, H); for (let k = 0; k < 14; k++) { const tt = t - k * .03; if (tt < 5.2) break; const [x, y] = orbAt(tt), rg = g.createRadialGradient(x, y, 0, x, y, 70 - k * 3);
        rg.addColorStop(0, `rgba(40,110,255,${(.28 - k * .018).toFixed(3)})`); rg.addColorStop(1, 'rgba(40,110,255,0)'); g.fillStyle = rg; g.beginPath(); g.arc(x, y, 70, 0, 7); g.fill(); } }
      /* intro */
      const introOut = 1 - M.i2((t - 4.8) / .3);
      const pass = (arr, x0, y0, t0) => arr.forEach((e, i) => { const ex = parseFloat(e.style.left); const reached = t > t0 && ox > ex + 10 && oy < y0 + 160 || t > t0 + 1.2;
        const u = e.u = reached ? Math.min(1, (e.u || 0) + 0) : 0; const st = e.st ?? (reached ? (e.st = t) : null); const v = st == null ? 0 : M.os((t - st) / .3);
        e.style.opacity = (st == null ? 0 : Math.min(1, (t - st) / .12) * introOut).toFixed(3); e.style.transform = `translateX(${(-50 * (1 - v)).toFixed(1)}px)`; e.style.filter = `blur(${((1 - Math.min(1, v)) * 6).toFixed(1)}px)`; });
      /* letters appear as the orb passes them (orb runs ahead along each line) */
      [[s.l1, .95, 1.9, 90], [s.l2, 2.15, 2.8, 90]].forEach(([arr, a, b]) => arr.forEach((e, i) => { const ex = e.x0 + e.offsetLeft, tx = a + (b - a) * clamp((ex - 90 + 60) / 970);
        const v = M.os((t - tx) / .3); e.style.opacity = (clamp((t - tx) / .12) * introOut).toFixed(3); e.style.transform = `translateX(${(-46 * (1 - Math.min(1, v))).toFixed(1)}px)`; e.style.filter = `blur(${(Math.max(0, 1 - v) * 6).toFixed(1)}px)`; }));
      M.rise(s.sub, t, 3.3, 5.1); s.col.style.opacity = M.env(t, .5, 5.1, .5).a; s.colIn.style.transform = `rotateY(-20deg) rotateX(6deg) translateY(${(-t * 160).toFixed(1)}px)`;
      /* beat cards */
      s.cards.forEach((c, i) => { const b = BEAT[i], nb = BEAT[i + 1] || 13.44, on = t >= b && t < nb + .2, u = M.os((t - b) / .28), out = M.i2((t - nb) / .18);
        c.style.display = on ? '' : 'none'; c.lb.style.display = on ? '' : 'none'; if (!on) return; const fi = Math.min(44, Math.floor((t - b) * 30)); C.setSrc(c.im, `${MED}clip/${c.k}/f_${String(fi).padStart(5, '0')}.jpg`);
        const ry = (i % 2 ? 1 : -1) * 10; c.style.opacity = (1 - out).toFixed(3); c.style.transform = `perspective(1600px) rotateY(${(ry * (1 - .4 * u)).toFixed(2)}deg) scale(${(.12 + .88 * u).toFixed(4)}) translateX(${(out * (i % 2 ? -260 : 260)).toFixed(1)}px)`;
        c.lb.style.opacity = (clamp((t - b - .15) / .15) * (1 - out)).toFixed(3); c.lb.style.transform = `translateY(${(14 * (1 - M.o3((t - b - .15) / .25))).toFixed(1)}px)`; });
      s.kw.forEach((arr, i) => { const b = BEAT[i], nb = BEAT[i + 1] || 13.44; arr.forEach((e, j) => { const v = M.os((t - b - .03 * j) / .25), on = t >= b && t < nb; e.parentNode.style.display = on ? '' : 'none';
        e.style.opacity = (clamp((t - b - .03 * j) / .1) * (1 - M.i2((t - nb + .12) / .12))).toFixed(3); e.style.transform = `translateX(${(-60 * (1 - Math.min(1, v))).toFixed(1)}px)`; e.style.color = isBlue ? '#fff' : '#0b1440'; }); });
      /* P12 sphere */
      const sIn = M.o3((t - 13.5) / 1.4), dIn = DIVE.reduce((a, [d]) => Math.max(a, t >= d - .05 && t < d + 1.25 ? Math.min(M.io((t - d + .05) / .25), 1 - M.io((t - d - 1.0) / .25)) : 0), 0), fin = M.io((t - 22.4) / .6);
      const pulse = beatK(t, t > 15.2 && t < 22.4 ? DROP : [], .12);
      s.sph.style.display = t > 13.45 ? '' : 'none'; s.sph.style.opacity = (Math.min(1, sIn * 1.2) * (1 - .78 * fin) * (1 - .9 * dIn)).toFixed(3);
      s.sph.style.filter = fin > 0 ? `blur(${(4 * fin).toFixed(1)}px)` : '';
      const a = spin(t), tilt = -14 + 6 * Math.sin(t * .7);
      s.ball.style.transform = `scale(${((.4 + .6 * sIn) * (1 + .05 * pulse) * (1 + 1.6 * dIn)).toFixed(4)}) rotateX(${tilt.toFixed(2)}deg) rotateY(${a.toFixed(2)}deg)`;
      const ar = a * Math.PI / 180, tr = tilt * Math.PI / 180;
      s.sc.forEach(c => { const lon = c.lon + ar, x = Math.cos(c.lat) * Math.sin(lon), z0 = Math.cos(c.lat) * Math.cos(lon), y = Math.sin(c.lat), z = z0 * Math.cos(tr) - y * Math.sin(tr);
        const fly = clamp((t - 13.5 - (c.k % 23) * .04) / .9), fu = M.o3(fly); c.style.opacity = (fly <= 0 ? 0 : (z > 0 ? 1 : .32) * Math.min(1, fly * 3)).toFixed(3);
        c.style.transform = `rotateY(${(c.lon * 57.2958).toFixed(2)}deg) rotateX(${(-c.lat * 57.2958).toFixed(2)}deg) translateZ(${(s.R + 1400 * (1 - fu)).toFixed(1)}px)`; });
      s.arcs.style.opacity = (clamp((t - 15.3) / .3) * (1 - clamp((t - 22.2) / .3)) * (1 - dIn)).toFixed(3); s.arcs.style.transform = `rotate(${(a * 1.4).toFixed(1)}deg)`;
      s.rows.forEach((r, i) => { const v = clamp((t - 15.3) / .25) * (1 - clamp((t - 22.2) / .3)); r.style.opacity = (v * (1 - dIn)).toFixed(3); const x = (t - 15.3) * 1500 * (i ? 1 : -1); r.style.transform = `translateX(${((i ? -3600 : 0) + x).toFixed(1)}px)`; });
      const drop = clamp((t - 15.2) / .25) * (1 - clamp((t - 22.2) / .3)), txtA = clamp((t - 13.9) / .3) * (1 - clamp((t - 22.3) / .2)); [s.p12t, s.p12d, s.mix].forEach((e, j) => { e.style.opacity = (txtA * (1 - dIn) * (j === 2 ? clamp((t - 15.3) / .3) : 1 - drop)).toFixed(3); e.style.transform = `translateY(${(16 * (1 - clamp((t - 13.9) / .3))).toFixed(1)}px)`; });
      s.dive.forEach(c => { const d = c.t0, on = t >= d && t < d + 1.3; c.style.display = on ? '' : 'none'; if (!on) return; const u = M.os((t - d - .08) / .3), o = M.i2((t - d - 1.02) / .25);
        c.style.opacity = (clamp((t - d - .08) / .1) * (1 - o)).toFixed(3); c.style.transform = `scale(${(.5 + .5 * u - .3 * o).toFixed(4)})`; C.setSrc(c.im, `${MED}clip/${c.k}/f_${String(Math.min(44, Math.floor((t - d) * 30) + 2)).padStart(5, '0')}.jpg`); });
      /* final pick */
      const fv = M.os((t - 22.5) / .4); s.fin.style.display = t > 22.45 ? '' : 'none'; s.fin.style.opacity = clamp((t - 22.5) / .12) * (1 - clamp((t - 24.1) / .3)); s.fin.style.transform = `scale(${(.5 + .5 * fv).toFixed(4)})`;
      if (t > 22.45) C.setSrc(s.fin.im, `${MED}clip/T37/f_${String(Math.min(44, Math.floor((t - 22.45) * 22))).padStart(5, '0')}.jpg`);
      M.pop(s.chk, t, 22.85, 24.15, { from: .2 }); M.hero(s.ft, t, 22.55, 24.15, { dx: 0, dy: 20, noclip: true }); M.pop(s.try, t, 22.95, 24.15, { from: .6 }); M.rise(s.url, t, 23.15, 24.15);
      /* chrome */
      const chc = isBlue ? '#fff' : '#18181A'; s.chL.style.color = s.chR.style.color = chc; const cA = 1 - clamp((t - 24.0) / .3); s.chL.style.opacity = s.chR.style.opacity = cA;
      let n = 1; BEAT.forEach((b, i) => { if (t >= b) n = [38, 48, 33, 76, 36, 79, 47, 61, 46, 87, 81][i]; }); s.cnt.textContent = `${String(n).padStart(2, '0')} / 100 ↗`; s.cnt.style.opacity = (t < 13.44 ? clamp((t - .6) / .3) : 0).toFixed(3);
      s.cnt.style.background = isBlue ? '#fff' : '#0b1440'; s.cnt.style.color = isBlue ? '#0a1a4a' : '#fff';
      s.pill.style.opacity = (clamp((t - 14.0) / .3) * (1 - dIn) * (1 - clamp((t - 22.3) / .2))).toFixed(3);
      /* orb + streak (blue) */
      const orbOn = t > .3 && t < 14.0, os = orbOn ? (t < .6 ? M.os((t - .3) / .3) : t > 13.44 ? 1 - M.i2((t - 13.44) / .5) : 1) : 0, land = beatK(t, BEAT, .1);
      s.orb.style.opacity = os > 0 ? 1 : 0; s.orb.style.transform = `translate(${(ox - 23).toFixed(1)}px, ${(oy - 23).toFixed(1)}px) scale(${(os * (1 + .35 * land)).toFixed(3)})`;
      s.ghost.forEach((g, k) => { const [gx, gy] = orbAt(t - (k + 1) * .025); g.style.opacity = (orbOn && isBlue ? (.5 - k * .055) : 0).toFixed(3); g.style.transform = `translate(${(gx - 23).toFixed(1)}px, ${(gy - 23).toFixed(1)}px) scale(${(1.4 - k * .06).toFixed(3)})`; });
    } });
})();
