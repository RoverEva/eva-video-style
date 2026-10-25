/* Eva Video Style · design kit (palette, chips, cards, screens, backgrounds, sound cues). Load after engine.js. */
(function () {
  const C = window.EV, { el } = C;
  const K = {
    LIME: '#d4ff2e', RED: '#ff2b3d', BLUE: '#2a2cf2', INK: '#0b0b0d', NAVY: '#070b2e', CYAN: '#22e3ff',
    PAPER: '#f4f2ec', OR: '#ff7a1a', PU: '#8a5cff', WHITE: '#ffffff',
  };
  /* text + blocks: (parent, text, ...) all absolutely positioned in 1920x1080 stage pixels */
  K.chip = (p, txt, bg, fg, size, x, y, extra) => el(p, 'div', 'chip', Object.assign({ background: bg, color: fg, fontSize: size + 'px', left: x + 'px', top: y + 'px' }, extra || {}), txt);
  K.disp = (p, txt, color, size, x, y, extra) => el(p, 'div', 'abs disp', Object.assign({ color, fontSize: size + 'px', left: x + 'px', top: y + 'px' }, extra || {}), txt);
  K.cn = (p, txt, color, size, x, y, extra) => el(p, 'div', 'abs cn', Object.assign({ color, fontSize: size + 'px', left: x + 'px', top: y + 'px' }, extra || {}), txt);
  K.hud = (p, txt, color, x, y, size, extra) => el(p, 'div', 'abs hud', Object.assign({ color, left: x + 'px', top: y + 'px', fontSize: (size || 18) + 'px' }, extra || {}), txt);
  K.card = (p, x, y, w, h, bg, extra) => el(p, 'div', 'card', Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: bg }, extra || {}));
  K.O = (e, o) => { e.style.transformOrigin = o || '0 50%'; return e; };
  K.center = e => { e.style.left = '0'; e.style.width = '1920px'; e.style.textAlign = 'center'; return e; };
  K.emoji = (p, ch, size, x, y) => el(p, 'div', 'abs', { left: x + 'px', top: y + 'px', fontSize: size + 'px', fontFamily: "'Noto Color Emoji'", transformOrigin: '50% 50%' }, ch);
  const NS = 'http://www.w3.org/2000/svg';
  K.svg = (p, w, h, x, y) => { const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', w); s.setAttribute('height', h); Object.assign(s.style, { position: 'absolute', left: x + 'px', top: y + 'px', overflow: 'visible' }); p.appendChild(s); return s; };
  K.sv = (p, tag, a) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); p.appendChild(e); return e; };

  /* real screen recordings: K.screen(parent, x, y, width, aspect) then K.play(screen, dir, offsetSeconds, localT, frameCount) */
  K.screen = (p, x, y, w, aspect, extra) => { const s = el(p, 'div', 'screen', Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px', height: (w / (aspect || 16 / 9)) + 'px', boxShadow: '0 30px 80px rgba(0,0,0,.55), 0 0 0 3px rgba(255,255,255,.08)' }, extra || {})); s.img = el(s, 'img'); return s; };
  K.play = (s, dir, off, t, count) => C.setSrc(s.img, C.seq(dir, off + Math.max(0, t), count));
  K.imgLayer = p => el(p, 'img', '', { position: 'absolute', left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover' });

  /* backgrounds */
  K.stageBg = `radial-gradient(1300px 520px at 50% 108%, rgba(255,122,26,.55), rgba(138,92,255,.18) 45%, rgba(0,0,0,0) 70%), radial-gradient(900px 600px at 15% 0%, rgba(138,92,255,.25), rgba(0,0,0,0) 60%), #07070b`;
  K.floor = (L, col) => el(L, 'div', 'abs', { left: '-600px', top: '640px', width: '3120px', height: '900px', backgroundImage: `linear-gradient(${col || 'rgba(255,122,26,.35)'} 2px, transparent 2px), linear-gradient(90deg, ${col || 'rgba(255,122,26,.35)'} 2px, transparent 2px)`, backgroundSize: '120px 120px', transform: 'perspective(700px) rotateX(62deg)', transformOrigin: '50% 0', WebkitMaskImage: 'linear-gradient(rgba(0,0,0,1), rgba(0,0,0,0) 80%)' });
  K.symbols = (L, seed) => { const cv = el(L, 'canvas', 'abs', { left: '-60px', top: '-60px' }); cv.width = 2040; cv.height = 1200;
    const g = cv.getContext('2d'), R = C.rng(seed || 7), cols = [K.LIME, K.RED, K.BLUE, '#ffffff'];
    for (let y = 30; y < 1200; y += 96) for (let x = 30; x < 2040; x += 96) {
      const c = cols[Math.floor(R() * 4)], k = Math.floor(R() * 6), s = 16; g.globalAlpha = .22 + R() * .22; g.strokeStyle = g.fillStyle = c; g.lineWidth = 5; g.beginPath();
      if (k === 0) { g.arc(x, y, s * .7, 0, 7); g.fill(); } else if (k === 1) { g.moveTo(x - s, y - s); g.lineTo(x + s, y + s); g.moveTo(x + s, y - s); g.lineTo(x - s, y + s); g.stroke(); }
      else if (k === 2) { g.moveTo(x - s, y); g.lineTo(x + s, y); g.moveTo(x, y - s); g.lineTo(x, y + s); g.stroke(); }
      else if (k === 3) { g.moveTo(x, y - s); g.lineTo(x + s, y + s * .8); g.lineTo(x - s, y + s * .8); g.closePath(); g.fill(); }
      else if (k === 4) { g.rect(x - s * .7, y - s * .7, s * 1.4, s * 1.4); g.fill(); } else { g.arc(x, y, s * .75, 0, 7); g.stroke(); } }
    return cv; };
  K.sunburst = (L, col) => el(L, 'div', 'abs', { left: '-540px', top: '-960px', width: '3000px', height: '3000px', background: `repeating-conic-gradient(from 0deg, ${col || 'rgba(255,255,255,.14)'} 0deg 7deg, rgba(0,0,0,0) 7deg 15deg)`, borderRadius: '50%' });
  /* label for anything conceptual (never pass off a mock-up as real data) */
  K.note = (L, txt, x, y, color) => K.hud(L, txt || 'ILLUSTRATIVE', color || '#fff', x ?? 1650, y ?? 1040, 15, { opacity: .55 });

  /* celebration confetti: const c = K.confetti(L, 80, seed, x0, width); then K.burst(c, t, t0) in update() */
  K.confetti = (L, n, seed, x0, w) => { const R = C.rng(seed), cols = [K.LIME, '#fff', K.BLUE, K.OR, K.PU, K.CYAN, K.RED], a = [];
    for (let i = 0; i < n; i++) a.push({ c: el(L, 'div', 'abs', { width: (10 + R() * 14) + 'px', height: (18 + R() * 22) + 'px', background: cols[i % 7], borderRadius: '3px' }), x0: x0 + R() * w, vx: (R() - .5) * 900, vy: -900 - R() * 800, d: R() * .2 }); return a; };
  K.burst = (a, t, t0) => a.forEach(q => { const u = t - t0 - q.d; if (u < 0) { q.c.style.opacity = 0; return; } C.tf(q.c, { x: q.x0 + q.vx * u, y: 1100 + q.vy * u + 1100 * u * u, r: 400 * u, o: C.clamp(2 - u) }); });

  /* sound cues: kinds whoosh | pop | click | impact | riser | ding | applause (rendered by scripts/sfx.py) */
  K.sfx = (kind, t, g, args) => C.sfx.push([kind, +t.toFixed(3), g, args || {}]);
  window.K = K;
})();
