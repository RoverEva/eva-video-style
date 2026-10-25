/* T22 BOLD · Bold Motion Graphics — demo (12 s). Night-neon stage: moving perspective grid, skyline, spinning light rays, sparks;
 * giant 3D extruded type (Bungee) with gold/cyan gradients, giant counting numbers, depth-layered words flying in. Presenter: AI model sample. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K;
  C.src0 = 0; C.end = 12; C.evaDir = '../media/model/seq'; C.face = { x: .51, y: .27, h: .44 };
  const N = { CY: '#2ef3ff', MG: '#ff3cac', GD: '#ffd23f', OR: '#ff8a00', VI: '#8a5cff', BLK: "'Bungee', 'Archivo Black', sans-serif" };
  const CIRC = { x: 70, y: 600, w: 380, h: 380, r: 190, s: 2.6 }, CIRC2 = { x: 1500, y: 60, w: 330, h: 330, r: 165, s: 2.8 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CIRC, { o: 0 }) }, { t: .9, d: .5, L: CIRC }, { t: 4.0, d: .5, L: CIRC2 }, { t: 8.0, d: .5, L: CIRC }];
  C.ringFn = t => ({ color: t < 4 || t >= 8 ? N.CY : N.MG, width: 6, glow: t < 4 || t >= 8 ? 'rgba(46,243,255,.85)' : 'rgba(255,60,172,.85)', shadow: .3 });
  const BG = 'radial-gradient(1400px 800px at 50% 35%, #2a1470, #120a45 55%, #07041f)';
  const ext = (col, n, dx, dy) => Array.from({ length: n }, (_, i) => `${(i + 1) * dx}px ${(i + 1) * dy}px 0 ${col}`).join(',');
  const big = (L, txt, size, grad, side, z) => { const d = el(L, 'div', 'abs', { left: 0, width: '1920px', textAlign: 'center', zIndex: z || 20, transformOrigin: '50% 50%' });
    const sh = el(d, 'div', '', { position: 'absolute', left: 0, width: '1920px', fontFamily: N.BLK, fontSize: size + 'px', lineHeight: 1, color: side, textShadow: ext(side, 14, 1.2, 1.6) + ', 0 30px 50px rgba(0,0,0,.6)' }, txt);
    const fg = el(d, 'div', '', { position: 'relative', fontFamily: N.BLK, fontSize: size + 'px', lineHeight: 1, color: 'transparent', backgroundImage: grad, WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextStroke: '3px rgba(255,255,255,.85)', filter: 'drop-shadow(0 0 18px rgba(46,243,255,.55))' }, txt); d.fg = fg; d.sh = sh; return d; };

  C.scene({ t0: 0, t1: C.end + .05, bg: BG, quiet: true, build(L) {
      const st = {}; st.cv = el(L, 'canvas', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' }); st.cv.width = 1920; st.cv.height = 1080;
      st.rays = el(L, 'div', 'abs', { left: '-540px', top: '-1060px', width: '3000px', height: '3000px', borderRadius: '50%', background: 'repeating-conic-gradient(from 0deg, rgba(255,255,255,.07) 0deg 5deg, rgba(0,0,0,0) 5deg 14deg)', mixBlendMode: 'screen' });
      const R = C.rng(31); st.sk = Array.from({ length: 26 }, (_, i) => ({ x: i * 78 - 30, w: 60 + R() * 40, h: 120 + R() * 260, win: R() })); st.sp = Array.from({ length: 70 }, () => ({ x: R() * 1920, y: R() * 1080, v: 200 + R() * 600, c: [N.CY, N.MG, N.GD][Math.floor(R() * 3)], l: 20 + R() * 60 }));
      st.slash = [0, 1, 2].map(i => el(L, 'div', 'abs', { left: '-400px', top: (180 + i * 260) + 'px', width: '2800px', height: (6 - i * 1.5) + 'px', background: `linear-gradient(90deg, rgba(0,0,0,0), ${[N.CY, N.MG, N.GD][i]}, rgba(0,0,0,0))`, transform: `rotate(${-14 + i * 4}deg)`, opacity: .8, boxShadow: `0 0 18px ${[N.CY, N.MG, N.GD][i]}` }));
      // A · BOLD / MOTION!
      st.a1 = big(L, 'BOLD', 300, `linear-gradient(180deg, #fff3b0, ${N.GD} 45%, ${N.OR})`, '#b3006b'); st.a1.style.top = '120px';
      st.a2 = big(L, 'MOTION!', 230, `linear-gradient(180deg, #e8ffff, ${N.CY} 50%, ${N.VI})`, '#3a0f9e'); st.a2.style.top = '430px';
      st.sub = el(L, 'div', 'abs', { left: 0, width: '1920px', textAlign: 'center', top: '720px', zIndex: 22 }, `<span style="font-family:${N.BLK};font-size:58px;color:transparent;background-image:linear-gradient(90deg,${N.GD},${N.OR});-webkit-background-clip:text;background-clip:text;filter:drop-shadow(0 4px 0 #3a0f9e);font-style:italic">GIANT TYPE · 3D DEPTH · NEON</span>`);
      // B · giant number
      st.num = big(L, '0', 420, `linear-gradient(180deg, #fff, ${N.MG} 55%, ${N.VI})`, '#24086b'); st.num.style.top = '200px';
      st.nl = el(L, 'div', 'abs', { left: 0, width: '1920px', textAlign: 'center', top: '700px', fontFamily: N.BLK, fontSize: '64px', color: N.CY, zIndex: 22, textShadow: `0 0 20px ${N.CY}` }, 'GIANT NUMBERS');
      // C · depth layers + CTA
      st.d = [['EPIC', N.GD, 140, 160], ['OPENERS', N.CY, 200, 340], ['READY?', N.MG, 160, 590]].map(([w, c, s, y]) => { const b = big(L, w, s, `linear-gradient(180deg, #fff, ${c})`, '#1a0650'); b.style.top = y + 'px'; return b; });
      st.cta = el(L, 'div', 'abs', { left: '1180px', top: '820px', zIndex: 24, padding: '14px 46px', borderRadius: '60px', fontFamily: N.BLK, fontSize: '54px', color: '#fff', background: `linear-gradient(90deg, ${N.VI}, ${N.MG})`, border: '4px solid #fff', boxShadow: `0 0 30px ${N.MG}`, transformOrigin: '50% 50%' }, '▶ WATCH NOW');
      st.fl = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: '#fff', zIndex: 30, opacity: 0 });
      k.sfx('riser', .05, .08, { d: .6 }); k.sfx('impact', .7, .2); k.sfx('impact', 1.5, .18); k.sfx('whoosh', 2.3, .1);
      k.sfx('whoosh', 4.0, .1); for (let i = 0; i < 16; i++) k.sfx('click', 4.4 + i * .12, .05); k.sfx('impact', 6.4, .2); k.sfx('whoosh', 8.0, .1); [8.4, 9.0, 9.6].forEach(x => k.sfx('impact', x, .14)); k.sfx('pop', 10.4, .16); return st; },
    update(lt, st, t) { const g = st.cv.getContext('2d'); g.clearRect(0, 0, 1920, 1080);
      // skyline
      st.sk.forEach(b => { const y = 640 - b.h; g.fillStyle = '#0b0630'; g.fillRect(b.x, y, b.w, b.h); g.fillStyle = 'rgba(255,210,63,.55)'; for (let yy = y + 12; yy < 630; yy += 18) for (let xx = b.x + 8; xx < b.x + b.w - 8; xx += 14) if (((xx * 7 + yy * 13 + Math.floor(t * 2) * (b.win > .5 ? 1 : 0)) % 11) < 3) g.fillRect(xx, yy, 5, 7); });
      // perspective grid floor
      g.save(); g.strokeStyle = 'rgba(255,60,172,.55)'; g.lineWidth = 2; g.shadowColor = N.MG; g.shadowBlur = 8; const hz = 640;
      for (let i = -24; i <= 24; i++) { g.beginPath(); g.moveTo(960 + i * 40, hz); g.lineTo(960 + i * 260, 1080); g.stroke(); }
      for (let j = 0; j < 14; j++) { const u = ((j + (t * 1.6) % 1) / 14), y = hz + (1080 - hz) * u * u; g.globalAlpha = .3 + .7 * u; g.beginPath(); g.moveTo(0, y); g.lineTo(1920, y); g.stroke(); } g.restore();
      g.fillStyle = 'rgba(46,243,255,.25)'; g.fillRect(0, hz - 2, 1920, 3);
      st.sp.forEach(p => { const x = (p.x + p.v * t) % 2100 - 90; g.strokeStyle = p.c; g.globalAlpha = .7; g.lineWidth = 2; g.beginPath(); g.moveTo(x, p.y); g.lineTo(x - p.l, p.y + p.l * .25); g.stroke(); }); g.globalAlpha = 1;
      st.rays.style.transform = `rotate(${t * 10}deg)`; st.slash.forEach((s, i) => { s.style.transform = `rotate(${-14 + i * 4}deg) translateX(${((t * 700 + i * 500) % 2400) - 1200}px)`; });
      const A = t < 4.0, B = t >= 4.0 && t < 8.0, Cc = t >= 8.0;
      [st.a1, st.a2, st.sub].forEach(e => e.style.display = A ? '' : 'none'); [st.num, st.nl].forEach(e => e.style.display = B ? '' : 'none'); [...st.d, st.cta].forEach(e => e.style.display = Cc ? '' : 'none');
      const shake = (t0) => (t >= t0 && t < t0 + .35 ? (1 - P(t, t0, .35)) * 14 : 0) * Math.sin(t * 90);
      const a1 = P(t, .7, .35); tf(st.a1, { s: 2.2 - 1.2 * ease.outBack(a1, 1.6), o: clamp(a1 * 5), y: shake(.7), r: -3 }); const a2 = P(t, 1.5, .35); tf(st.a2, { s: 2.2 - 1.2 * ease.outBack(a2, 1.6), o: clamp(a2 * 5), x: shake(1.5), r: 2 });
      tf(st.sub, slide(t, 2.3, .4, 0, 60));
      const n = Math.round(100 * ease.out3(P(t, 4.4, 2.0))); st.num.fg.textContent = st.num.sh.textContent = n; const nn = P(t, 6.4, .3); tf(st.num, { s: 1 + .25 * (1 - ease.outBack(nn, 2)) * (t >= 6.4 ? 1 : 0) + (t < 4.4 ? 0 : 0), o: P(t, 4.0, .2), y: shake(6.4) });
      tf(st.nl, slide(t, 4.6, .4, 0, 40));
      st.d.forEach((b, i) => { const u = P(t, 8.4 + i * .6, .55); const e = ease.out3(u); tf(b, { s: .15 + .85 * e, o: clamp(u * 3), y: shake(8.4 + i * .6) * .5 }); b.style.filter = `blur(${(1 - e) * 14}px)`; });
      tf(st.cta, { s: pop(t, 10.4, .4, 2).s * (1 + .04 * Math.sin(t * 8)), o: P(t, 10.4, .1) });
      st.fl.style.opacity = [.7, 1.5, 6.4, 8.4, 9.0, 9.6].reduce((m, x) => Math.max(m, t >= x ? .55 * (1 - P(t, x, .15)) : 0), 0); } });
})();
