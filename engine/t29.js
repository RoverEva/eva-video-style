/* T29 Depth Glow 景深光效 · template library. Load after templates.js.
 * Three depth layers per layout: (1) the presenter's real room, graded dark and cool (plate), (2) glowing motion graphics,
 * (3) the AI cut-out of the presenter on top (scripts/matte.py), so every graphic renders BEHIND the presenter.
 * Presenter: same frame, same scale as the footage (s = 1), never zoomed; whole head visible. No sound in the template.
 * Graphics are original and generic: no third-party logos or brand marks; copy comes from the script (w.a, w.b, w.items).
 * Coordinates are stage pixels; EV.pick(landscape, portrait) places each element for 16:9 and 9:16. */
(function () {
  const C = EV, { el, tf, clamp } = C, T = K.T;
  const DG = T.DG = { NIGHT: '#050a18', BLUE: '#2f7bff', CYAN: '#5fd3ff', ICE: '#cfeaff', GOLD: '#ffcf3a', WHITE: '#ffffff', GREEN: '#38e08c',
    UI: "'Inter', 'Noto Sans CJK SC', sans-serif", CN: "'Noto Sans CJK SC', sans-serif" };
  T.dgBg = DG.NIGHT;
  const pk = (a, b) => (C.portrait ? b : a);
  const o3 = u => 1 - Math.pow(1 - clamp(u), 3), ob = u => { u = clamp(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
  const NS = 'http://www.w3.org/2000/svg';
  const svg = (p, x, y, w, h, inner, st) => { const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    Object.assign(s.style, { position: 'absolute', left: x + 'px', top: y + 'px', overflow: 'visible' }, st || {}); s.innerHTML = inner; p.appendChild(s); return s; };
  const glowTxt = (col, k) => `0 0 ${14 * (k || 1)}px ${col || 'rgba(120,190,255,.95)'}, 0 0 ${44 * (k || 1)}px rgba(47,123,255,.65)`;
  const rng = s => () => (s = (s * 16807) % 2147483647) / 2147483647;
  const len = s => [...String(s)].reduce((a, ch) => a + (/[　-鿿＀-￯]/.test(ch) ? 1 : .56), 0);
  const fit = (s, size, maxW) => Math.min(size, maxW / Math.max(1, len(s)));

  /* ---------- depth layers ---------- */
  T.dgPlate = R => { const p = el(R, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', zIndex: 0, overflow: 'hidden', background: DG.NIGHT });
    if (C.portrait && C.src && C.src.w > C.src.h) {   /* landscape footage in 9:16: a blurred dark fill, then the real room at its own size at the bottom */
      p.fill = el(p, 'img', 'abs', { left: '-6%', top: '-6%', width: '112%', height: '112%', objectFit: 'cover', filter: 'blur(36px) brightness(.18) saturate(.4)' });
      p.im = el(p, 'img', 'abs', { left: 0, top: 0, width: '100%', height: '100%', objectFit: 'contain', objectPosition: '50% 100%', filter: 'brightness(.34) saturate(.55) contrast(1.12)' }); }
    else p.im = el(p, 'img', 'abs', { left: 0, top: 0, width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(.34) saturate(.55) contrast(1.12)' });
    el(p, 'div', 'abs', { left: 0, top: 0, width: '100%', height: '100%', background: 'linear-gradient(180deg, rgba(6,14,40,.55), rgba(5,10,24,.25) 55%, rgba(0,0,0,.55))', mixBlendMode: 'multiply' });
    el(p, 'div', 'abs', { left: 0, top: 0, width: '100%', height: '100%', background: 'radial-gradient(ellipse at 50% 38%, rgba(0,0,0,0) 35%, rgba(0,0,0,.6) 100%)' });
    return p; };
  T.dgCut = R => { const w = el(R, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', zIndex: 50, filter: 'drop-shadow(0 0 26px rgba(95,170,255,.28))' });
    const land = C.portrait && C.src && C.src.w > C.src.h, fit = land ? 'contain' : 'cover', pos = land ? '50% 100%' : '50% 50%';   /* landscape footage in 9:16: her own size at the bottom */
    w.im = el(w, 'img', 'abs', { left: 0, top: 0, width: '100%', height: '100%', objectFit: fit, objectPosition: pos, WebkitMaskSize: fit, maskSize: fit, WebkitMaskPosition: pos, maskPosition: pos, WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat' }); return w; };
  const depthAt = (o, m, t) => { C.setSrc(o.plate.im, m.frame(t)); if (o.plate.fill) C.setSrc(o.plate.fill, m.frame(t)); C.setSrc(o.cut.im, m.frame(t)); const mk = `url(${m.cut(t)})`;
    if (o.cut.im._m !== mk) { o.cut.im.style.webkitMaskImage = o.cut.im.style.maskImage = mk; o.cut.im._m = mk; } tf(o.cut, { x: 0, y: 0, s: 1 }); };

  /* ---------- shared graphic pieces ---------- */
  const chip = (p, x, y, txt, opt) => { opt = opt || {}; const c = el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', padding: '12px 26px 12px 14px', borderRadius: '40px', display: 'flex', alignItems: 'center', gap: '14px',
      background: 'rgba(8,16,36,.82)', border: '2px solid rgba(120,190,255,.55)', boxShadow: '0 0 22px rgba(47,123,255,.45)', font: `600 ${opt.size || 30}px ${DG.UI}`, color: DG.WHITE, whiteSpace: 'nowrap', transformOrigin: '0 50%' });
    el(c, 'div', '', { width: (opt.size || 30) * 1.25 + 'px', height: (opt.size || 30) * 1.25 + 'px', borderRadius: '50%', background: `radial-gradient(circle at 35% 35%, ${DG.ICE}, ${DG.BLUE})`, boxShadow: `0 0 12px ${DG.CYAN}`, flex: 'none' });
    el(c, 'span', '', {}, txt); return c; };
  /* original generic AI mark: a four-point spark inside a rounded square */
  const spark = (p, cx, cy, r, col) => svg(p, cx - r, cy - r, r * 2, r * 2,
    `<rect x="${r * .12}" y="${r * .12}" width="${r * 1.76}" height="${r * 1.76}" rx="${r * .5}" fill="rgba(8,18,40,.55)" stroke="${col || DG.ICE}" stroke-width="${r * .07}"/>
     <path d="M${r} ${r * .42} C${r * 1.08} ${r * .86} ${r * 1.14} ${r * .92} ${r * 1.58} ${r} C${r * 1.14} ${r * 1.08} ${r * 1.08} ${r * 1.14} ${r} ${r * 1.58} C${r * .92} ${r * 1.14} ${r * .86} ${r * 1.08} ${r * .42} ${r} C${r * .86} ${r * .92} ${r * .92} ${r * .86} ${r} ${r * .42}Z" fill="${col || DG.ICE}"/>
     <circle cx="${r * 1.42}" cy="${r * .58}" r="${r * .09}" fill="${col || DG.ICE}"/>`, { filter: `drop-shadow(0 0 ${r * .25}px ${DG.CYAN}) drop-shadow(0 0 ${r * .6}px rgba(47,123,255,.8))`, transformOrigin: '50% 50%' });
  const title = (p, x, y, txt, size, opt) => { opt = opt || {}; const e = el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', font: `900 ${size}px ${opt.cn === false ? DG.UI : DG.CN}`, color: opt.c || DG.WHITE,
      textShadow: glowTxt(opt.g), whiteSpace: 'pre', lineHeight: 1.08, letterSpacing: opt.ls || '.02em', textAlign: opt.al || 'left', transformOrigin: '50% 50%' }, txt);
    if (opt.al === 'center') { e.style.left = (x - 2000) + 'px'; e.style.width = '4000px'; } return e; };

  /* ---------- layouts ---------- */
  /* w.auto (Studio automatic edits): no sample copy ever appears — a missing text is an invisible zero-width space, and the
     skin hides the element (chip, ring, tag). Demos and the 9-layout sheets (no w.auto) are unchanged. */
  T.dgLayout = (n, L, w, m) => { w = w || {}; if (w.auto) { const Z = '\u200b'; w = Object.assign({}, w); ['a', 'b', 'k', 'ring'].forEach(k => { if (w[k] == null || w[k] === '') w[k] = Z; }); }
    const o = { n, w };
    const R = o.root = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', overflow: 'hidden' });
    o.plate = T.dgPlate(R); const F = o.fx = el(R, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', zIndex: 10 }); o.cut = T.dgCut(R);
    const W = C.W, H = C.H;
    if (n === 1) { /* headline: glowing title above / beside the head */
      const s = w.a || '资料很少', sz = fit(s, pk(150, 132), pk(460, 900));
      o.k = chip(F, pk(70, (W - 260) / 2), pk(180, 120), w.k || 'NEW', { size: 26 }); o.k.style.borderColor = DG.GOLD; o.k.style.boxShadow = `0 0 22px rgba(255,207,58,.5)`;
      o.t = title(F, pk(70, W / 2), pk(250, 200), s, sz, { al: pk('left', 'center') });
      o.u = el(F, 'div', 'abs', { left: pk(70, W / 2 - 300) + 'px', top: pk(250, 200) + sz * 1.14 + 'px', width: pk(len(s) * sz, 600) + 'px', height: '6px', borderRadius: '3px',
        background: `linear-gradient(90deg, rgba(95,211,255,0), ${DG.CYAN}, rgba(95,211,255,0))`, boxShadow: `0 0 18px ${DG.CYAN}`, transformOrigin: '0 50%' });
      o.upd = u => { tf(o.k, { o: o3(u / .25), s: ob(u / .35) }); o.t.style.filter = `blur(${(1 - o3(u / .45)) * 18}px)`; tf(o.t, { o: o3(u / .35), s: 1.12 - .12 * o3(u / .5), y: 30 * (1 - o3(u / .5)) });
        tf(o.u, { o: o3((u - .3) / .3), s: o3((u - .3) / .5) }); };
    }
    if (n === 2) { /* trend: rising glowing curve behind the presenter, live tip + label */
      const x0 = -40, y0 = pk(.62 * H, .5 * H), x1 = W - pk(260, 130), y1 = pk(150, 260);
      const d = `M${x0} ${y0} C${W * .25} ${y0 - 20} ${W * .35} ${y0 - 120} ${W * .5} ${(y0 + y1) / 2 + 60} S${W * .72} ${y1 + 120} ${x1} ${y1}`;
      o.s = svg(F, 0, 0, W, H, `<defs><linearGradient id="dgl" x1="0" x2="1"><stop offset="0" stop-color="${DG.BLUE}" stop-opacity=".2"/><stop offset=".55" stop-color="${DG.CYAN}"/><stop offset="1" stop-color="${DG.GOLD}"/></linearGradient>
        <linearGradient id="dga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${DG.BLUE}" stop-opacity=".35"/><stop offset="1" stop-color="${DG.BLUE}" stop-opacity="0"/></linearGradient></defs>
        <path class="ar" d="${d} L${x1} ${H} L${x0} ${H}Z" fill="url(#dga)"/>
        <path class="ln" d="${d}" fill="none" stroke="url(#dgl)" stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>`, { filter: `drop-shadow(0 0 10px ${DG.CYAN})` });
      o.p = o.s.querySelector('.ln'); o.ar = o.s.querySelector('.ar');
      o.dot = el(F, 'div', 'abs', { left: '-14px', top: '-14px', width: '28px', height: '28px', borderRadius: '50%', background: DG.WHITE, boxShadow: `0 0 0 8px rgba(255,207,58,.35), 0 0 30px ${DG.GOLD}` });
      o.rip = el(F, 'div', 'abs', { left: x1 - 40 + 'px', top: y1 - 40 + 'px', width: '80px', height: '80px', borderRadius: '50%', border: `3px solid ${DG.GOLD}` });
      const s = w.a || 'AI VIDEO';
      o.k = chip(F, pk(70, 90), pk(200, 120), w.k || 'TRENDING', { size: 26 }); o.k.style.borderColor = DG.GOLD;
      o.t = title(F, pk(70, 90), pk(280, 200), s, fit(s, pk(84, 78), pk(440, 700)), { cn: false, ls: '0' });
      o.upd = u => { const q = o3(u / 1.1), L2 = o.p.getTotalLength(); o.p.setAttribute('stroke-dashoffset', 1 - q); o.ar.style.opacity = q * .9;
        const pt = o.p.getPointAtLength(L2 * q); tf(o.dot, { x: pt.x, y: pt.y, o: u > .02 ? 1 : 0 });
        const r = ((u - 1.1) % 1.2 + 1.2) % 1.2; tf(o.rip, { s: u < 1.1 ? 0 : .4 + r * 1.6, o: u < 1.1 ? 0 : 1 - r / 1.2 });
        tf(o.k, { o: o3((u - .5) / .25), s: ob((u - .5) / .35) }); tf(o.t, { o: o3((u - .6) / .3), y: 24 * (1 - o3((u - .6) / .4)) }); };
    }
    if (n === 3) { /* dot globe behind the head + result chips */
      const cx = W * pk(.5, .5), cy = H * pk(.42, .3), r = pk(470, 470);
      o.cv = el(F, 'canvas', 'abs', { left: cx - r - 60 + 'px', top: cy - r - 60 + 'px', filter: `drop-shadow(0 0 30px rgba(47,123,255,.8))` }); o.cv.width = o.cv.height = 2 * r + 120; o.r = r;
      const R2 = rng(29), pts = []; for (let i = 0; i < 1400; i++) { const z = R2() * 2 - 1, a = R2() * 6.283; pts.push([Math.sqrt(1 - z * z) * Math.cos(a), z, Math.sqrt(1 - z * z) * Math.sin(a), R2() < .26]); } o.pts = pts;
      const it = w.items || ['AI tutorial', 'How-to guide', 'Your website'];
      o.ch = it.slice(0, 3).map((s, i) => chip(F, pk([cx - 760, cx + 300, cx - 720][i], [40, W - 470, 60][i]), pk([cy - 330, cy - 240, cy + 40][i], [cy - 360, cy - 300, cy - 150][i]), s, { size: 28 }));
      o.upd = u => { const g = o.cv.getContext('2d'), Rr = o.r * (.6 + .4 * o3(u / .6)), c0 = Rr + 60 + (o.r - Rr); g.clearRect(0, 0, o.cv.width, o.cv.height);
        const gr = g.createRadialGradient(c0 - Rr * .3, c0 - Rr * .35, Rr * .1, c0, c0, Rr); gr.addColorStop(0, 'rgba(110,190,255,.85)'); gr.addColorStop(.7, 'rgba(36,104,230,.75)'); gr.addColorStop(1, 'rgba(12,40,120,.55)');
        g.globalAlpha = o3(u / .4); g.fillStyle = gr; g.beginPath(); g.arc(c0, c0, Rr, 0, 7); g.fill(); const rot = u * .5;
        for (const [x, y, z, land] of o.pts) { const xr = x * Math.cos(rot) + z * Math.sin(rot), zr = -x * Math.sin(rot) + z * Math.cos(rot); if (zr < 0) continue;
          g.fillStyle = land ? `rgba(220,240,255,${.35 + .6 * zr})` : `rgba(140,200,255,${.12 + .25 * zr})`; g.fillRect(c0 + xr * Rr - 2, c0 + y * Rr - 2, land ? 5 : 3, land ? 5 : 3); }
        g.globalAlpha = 1; o.ch.forEach((c, i) => tf(c, { o: o3((u - .5 - i * .22) / .2), s: ob((u - .5 - i * .22) / .35) })); };
    }
    if (n === 4) { /* glowing AI mark + label + orbiting text ring */
      const cx = pk(W * .22, W / 2), cy = pk(H * .3, 230), r = pk(120, 110);
      o.ic = spark(F, cx, cy, r); const s = w.a || 'AI ASSISTANT';
      o.t = title(F, cx, cy + r * 1.2, s, fit(s, 46, 600), { cn: false, al: 'center', ls: '.04em' });
      const ring = (w.ring || 'ask  ·  search  ·  answer  ·  recommend  ·  ').repeat(2), rr = r * 1.75;
      o.rg = svg(F, cx - rr - 40, cy - rr - 40, 2 * rr + 80, 2 * rr + 80, `<defs><path id="dgr" d="M${rr + 40} ${rr + 40} m-${rr} 0 a${rr} ${rr} 0 1 1 ${2 * rr} 0 a${rr} ${rr} 0 1 1 -${2 * rr} 0"/></defs>
        <text font-family="Inter, sans-serif" font-size="30" font-style="italic" letter-spacing="3" fill="${DG.ICE}"><textPath href="#dgr">${ring}</textPath></text>`, { filter: `drop-shadow(0 0 8px ${DG.CYAN})`, transformOrigin: '50% 50%' });
      o.upd = u => { tf(o.ic, { s: ob(u / .45), o: o3(u / .2) }); tf(o.t, { o: o3((u - .3) / .3), y: 20 * (1 - o3((u - .3) / .4)) });
        o.rg.style.opacity = o3((u - .45) / .4) * .85; o.rg.style.transform = `rotate(${-u * 28}deg) scaleY(.42)`; };
    }
    if (n === 5) { /* glowing search box, typing */
      const bw = pk(500, 900), x = pk(50, (W - bw) / 2), y = pk(H * .3, 300), bh = pk(170, 104);
      o.ic = spark(F, x + bw / 2, y - pk(110, 150), 62); o.ic.style.opacity = .55;
      o.b = el(F, 'div', 'abs', { left: x + 'px', top: y + 'px', width: bw + 'px', height: bh + 'px', borderRadius: pk('40px', '52px'), background: 'rgba(10,20,46,.86)', border: `3px solid ${DG.CYAN}`,
        boxShadow: `0 0 26px rgba(95,211,255,.7), inset 0 0 22px rgba(47,123,255,.35)`, transformOrigin: '50% 50%' });
      o.tx = el(o.b, 'div', 'abs', { left: pk('36px', '44px'), top: pk('24px', '26px'), width: pk((bw - 150) + 'px', ''), font: `500 ${pk(40, 44)}px ${DG.UI}`, lineHeight: pk(1.3, 'normal'), color: DG.WHITE, whiteSpace: pk('normal', 'nowrap') });
      o.go = el(o.b, 'div', 'abs', { right: '18px', top: (bh - 72) / 2 + 'px', width: '72px', height: '72px', borderRadius: '50%', background: DG.ICE, boxShadow: `0 0 18px ${DG.CYAN}` });
      svg(o.go, 18, 16, 36, 40, `<path d="M18 36 V6 M5 18 L18 5 L31 18" stroke="${DG.NIGHT}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`);
      o.q = w.a || 'best way to make an AI video?';
      o.upd = u => { tf(o.b, { o: o3(u / .25), s: .9 + .1 * ob(u / .4) }); const k = Math.floor(clamp((u - .35) / 1.4) * [...o.q].length);
        o.tx.textContent = [...o.q].slice(0, k).join('') + ((u * 2.2 | 0) % 2 || k < [...o.q].length ? '|' : ' '); tf(o.go, { s: k >= [...o.q].length ? 1 + .12 * Math.sin(u * 9) : 1 }); };
    }
    if (n === 6) { /* data wall: tile grid behind the presenter, scan brackets lock onto one tile */
      const cols = pk(16, 9), rows = pk(8, 12), gw = W / cols, gh = pk(H * .75, H * .62) / rows, R2 = rng(61); o.tiles = [];
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) o.tiles.push({ e: el(F, 'div', 'abs', { left: c * gw + 6 + 'px', top: r * gh + 6 + 'px', width: gw - 12 + 'px', height: gh - 12 + 'px', borderRadius: '6px',
        background: 'rgba(60,120,230,.16)', border: '1px solid rgba(110,180,255,.22)' }), ph: R2() * 6.28, sp: .6 + R2() * 1.6 });
      const tc = pk(cols - 4, 7), tr = pk(2, 2); o.tg = o.tiles[tr * cols + tc]; o.tgx = tc * gw + gw / 2; o.tgy = tr * gh + gh / 2; o.gw = gw; o.gh = gh;
      o.br = [0, 1, 2, 3].map(i => el(F, 'div', 'abs', { width: '46px', height: '46px', borderColor: DG.GOLD, borderStyle: 'solid', borderWidth: `${i < 2 ? 5 : 0}px ${i % 2 ? 5 : 0}px ${i > 1 ? 5 : 0}px ${i % 2 ? 0 : 5}px`, filter: `drop-shadow(0 0 8px ${DG.GOLD})` }));
      const s = w.a || 'INDEXED'; o.t = title(F, pk(60, W / 2), pk(H * .5, 90), s, fit(s, pk(96, 88), pk(440, 900)), { cn: !/^[\x00-\x7f]*$/.test(s), al: pk('left', 'center') });
      o.upd = u => { o.tiles.forEach((q, i) => { const on = o3((u - (i % 7) * .03) / .4); q.e.style.opacity = on * (.45 + .4 * Math.sin(u * q.sp * 3 + q.ph)); });
        const lk = o3((u - .4) / .7), sx = W * .5, sy = H * .25, bx = sx + (o.tgx - sx) * lk, by = sy + (o.tgy - sy) * lk, hw = (pk(380, 300) * (1 - lk) + o.gw * .62) , hh = (pk(260, 300) * (1 - lk) + o.gh * .62);
        o.br.forEach((b, i) => tf(b, { x: bx + (i % 2 ? hw - 46 : -hw), y: by + (i > 1 ? hh - 46 : -hh), o: o3((u - .3) / .2) }));
        const hit = u > 1.1; o.tg.e.style.opacity = 1; o.tg.e.style.background = hit ? 'rgba(255,207,58,.85)' : o.tg.e.style.background; o.tg.e.style.boxShadow = hit ? `0 0 30px ${DG.GOLD}` : 'none';
        tf(o.t, { o: o3((u - 1.15) / .3), y: 24 * (1 - o3((u - 1.15) / .4)) }); };
    }
    if (n === 7) { /* particle stream from the AI mark to a glowing site card */
      const ax = pk(W * .18, 230), ay = pk(H * .28, 300), cw = pk(380, 330), ch = pk(250, 220), bx = pk(W - cw - 120, W - cw - 70), by = pk(H * .1, 170);
      o.ic = spark(F, ax, ay, pk(100, 92));
      o.c = el(F, 'div', 'abs', { left: bx + 'px', top: by + 'px', width: cw + 'px', height: ch + 'px', borderRadius: '22px', background: 'rgba(14,18,34,.9)', border: `4px solid ${DG.GOLD}`, boxShadow: `0 0 34px rgba(255,207,58,.6), inset 0 0 26px rgba(255,207,58,.18)`, transformOrigin: '50% 50%' });
      svg(o.c, cw / 2 - 34, 34, 68, 50, `<rect width="68" height="50" rx="12" fill="${DG.GOLD}"/><path d="M27 14 L45 25 L27 36Z" fill="${DG.NIGHT}"/>`);
      const s = w.a || '我的网站'; el(o.c, 'div', 'abs', { left: 0, width: cw + 'px', top: '98px', textAlign: 'center', font: `900 ${fit(s, 62, cw - 40)}px ${DG.CN}`, color: DG.GOLD, textShadow: `0 0 16px rgba(255,207,58,.8)` }, s);
      el(o.c, 'div', 'abs', { left: '40px', right: '40px', bottom: '34px', height: '10px', borderRadius: '5px', background: `repeating-linear-gradient(90deg, rgba(255,207,58,.55) 0 22px, transparent 22px 30px)` });
      const ex = bx + 20, ey = by + ch / 2, mx = (ax + ex) / 2, my = Math.min(ay, by) - pk(160, 140); o.P = u => { const v = 1 - u; return [v * v * ax + 2 * v * u * mx + u * u * ex, v * v * ay + 2 * v * u * my + u * u * ey]; };
      o.cv = el(F, 'canvas', 'abs', { left: 0, top: 0 }); o.cv.width = W; o.cv.height = H; const R2 = rng(7); o.ps = Array.from({ length: 220 }, () => [R2(), (R2() - .5) * 46, (R2() - .5) * 46, .6 + R2()]);
      o.upd = u => { tf(o.ic, { s: ob(u / .4), o: o3(u / .2) }); tf(o.c, { s: ob((u - .45) / .35), o: o3((u - .45) / .2) }); const g = o.cv.getContext('2d'); g.clearRect(0, 0, W, H);
        const flow = clamp((u - .15) / .5); for (const [f, dx, dy, sp] of o.ps) { const k = (f + u * .55 * sp) % 1; if (k > flow) continue; const [x, y] = o.P(k), a = Math.sin(k * 3.14);
          g.fillStyle = `rgba(255,${200 + 40 * a | 0},${90 + 120 * (1 - k) | 0},${.25 + .7 * a})`; g.beginPath(); g.arc(x + dx * a, y + dy * a, 2.2 + 2.6 * a, 0, 7); g.fill(); }
        g.shadowBlur = 0; };
    }
    if (n === 8) { /* checklist card: items tick one by one */
      const it = (w.items || ['How do I make it?', 'How long does it take?', 'What do I need?']).slice(0, 4), cw = pk(470, 860), x = pk(W - cw - 50, (W - cw) / 2), y = pk(H * .12, 40), rh = pk(92, 80);
      o.c = el(F, 'div', 'abs', { left: x + 'px', top: y + 'px', width: cw + 'px', height: 100 + it.length * rh + 'px', borderRadius: '26px', background: 'rgba(10,18,40,.88)', border: `3px solid ${DG.GOLD}`,
        boxShadow: `0 0 30px rgba(255,207,58,.5)`, transformOrigin: '50% 0' });
      const s = w.a || 'FAQ'; el(o.c, 'div', 'abs', { left: '40px', top: '26px', font: `900 ${fit(s, 50, cw - 80)}px ${DG.CN}`, color: DG.GOLD, textShadow: `0 0 14px rgba(255,207,58,.7)` }, s);
      const fs = Math.min(...it.map(q => fit(q, 36, cw - 190))); o.rows = it.map((q, i) => { const r = el(o.c, 'div', 'abs', { left: '40px', top: 100 + i * rh + 'px', width: cw - 80 + 'px', height: rh - 16 + 'px', borderRadius: '14px', background: 'rgba(60,120,230,.16)', display: 'flex', alignItems: 'center', gap: '22px', padding: '0 22px', boxSizing: 'border-box' });
        r.bx = el(r, 'div', '', { position: 'relative', width: '40px', height: '40px', flex: 'none', borderRadius: '50%', border: `3px solid ${DG.ICE}` });
        r.ck = svg(r.bx, 4, 7, 26, 20, `<path d="M2 10 L10 18 L24 2" stroke="${DG.NIGHT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`); el(r, 'span', '', { font: `500 ${fs}px ${DG.UI}`, color: DG.WHITE, whiteSpace: 'nowrap' }, q); return r; });
      o.upd = u => { tf(o.c, { o: o3(u / .25), s: .85 + .15 * ob(u / .45) }); o.rows.forEach((r, i) => { tf(r, { o: o3((u - .15 - i * .08) / .2), x: 40 * (1 - o3((u - .15 - i * .08) / .3)) });
        const on = u > .55 + i * .22; r.bx.style.background = on ? DG.GOLD : 'transparent'; r.bx.style.borderColor = on ? DG.GOLD : DG.ICE; r.bx.style.boxShadow = on ? `0 0 16px ${DG.GOLD}` : 'none'; r.ck.style.opacity = on ? 1 : 0; }); };
    }
    if (n === 9) { /* spotlight: a gold ring draws around a tag card beside the head, then pulses */
      const cx = pk(W * .8, W * .8), cy = pk(H * .28, 560), rr = pk(150, 130), s = w.a || 'NEW';
      o.c = el(F, 'div', 'abs', { left: cx - 70 + 'px', top: cy - 92 + 'px', width: '140px', height: '184px', borderRadius: '16px', background: DG.GOLD, boxShadow: `0 0 30px rgba(255,207,58,.8)`, transformOrigin: '50% 50%' });
      el(o.c, 'div', 'abs', { left: '-60px', width: '260px', top: '-112px', textAlign: 'center', font: `900 ${fit(s, 44, 250)}px ${DG.CN}`, color: DG.GOLD, textShadow: `0 0 14px rgba(255,207,58,.8)` }, s);
      el(o.c, 'div', 'abs', { left: '24px', right: '24px', top: '112px', height: '12px', borderRadius: '6px', background: 'rgba(5,10,24,.45)' });
      o.rg = svg(F, cx - rr - 20, cy - rr - 20, 2 * rr + 40, 2 * rr + 40, `<circle cx="${rr + 20}" cy="${rr + 20}" r="${rr}" fill="none" stroke="${DG.GOLD}" stroke-width="7" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 ${rr + 20} ${rr + 20})"/>`, { filter: `drop-shadow(0 0 12px ${DG.GOLD})`, transformOrigin: '50% 50%' });
      const t2 = w.b || '一键直达', t2s = fit(t2, pk(110, 120), pk(440, 620)); o.t = title(F, pk(70, 70), pk(250, 200), t2, t2s);
      o.upd = u => { tf(o.c, { s: ob(u / .4), o: o3(u / .2), r: -4 * (1 - o3(u / .5)) }); o.rg.querySelector('circle').setAttribute('stroke-dashoffset', 1 - o3((u - .25) / .55));
        tf(o.rg, { s: 1 + .05 * Math.sin(Math.max(0, u - .8) * 6) }); tf(o.t, { o: o3((u - .7) / .3), y: 24 * (1 - o3((u - .7) / .4)) }); };
    }
    if (!o.upd) o.upd = () => {};
    return o; };
  /* t: global time, t0: layout start, m: media {frame(t), cut(t)} */
  T.dgLayoutAt = (o, t, t0, m) => { depthAt(o, m, t); o.upd(t - t0); };
})();
