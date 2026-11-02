/* T20 Fast-Paced Social Media — demo on the shared 15 s intro. Loud kinetic type, vivid lavender/lime/violet,
 * word-by-word caption bars, beat-cut punches. Built for TikTok / Shorts / Reels energy, laid out 16:9 and 9:16. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, I = IN, V = C.portrait, pk = C.pick; I.setup(C);
  /* Responsive: every position goes through pk(16:9 value, 9:16 value); the 16:9 values are the original ones. */
  const S = { BG: '#ece6fb', VI: '#7b5cff', LI: '#d6ff3a', INK: '#111015', MONO: "'Space Mono', monospace", HEAD: "'Anton', 'Archivo Black', sans-serif" };
  const CARD = pk({ x: 150, y: 70, w: 640, h: 820, r: 52, s: 1.6 }, { x: 150, y: 400, w: 780, h: 760, r: 52, s: 1.6 }),
    CARD2 = pk({ x: 110, y: 90, w: 600, h: 780, r: 48, s: 1.6 }, { x: 64, y: 1000, w: 420, h: 440, r: 40, s: 1.6 });
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .05, d: .45, L: CARD }, { t: 3.87, d: .5, L: CARD2 }, { t: 7.73, d: .35, L: C.pose('full') }];
  C.ringFn = t => t < 7.73 ? { color: '#fff', width: 10, shadow: .35 } : { color: 'transparent', width: 0, shadow: 0 };

  const AX = pk(880, 470), AY = pk(190, 260);
  const blob = (L, x, y, w, h, grad, z) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: grad, zIndex: z || 1, filter: 'saturate(1.1)' }); return b; };
  const blobAt = (b, t, ph) => { const r = n => (50 + 12 * Math.sin(t * 1.3 + ph + n)).toFixed(1) + '%'; b.style.borderRadius = `${r(0)} ${r(1)} ${r(2)} ${r(3)} / ${r(4)} ${r(5)} ${r(6)} ${r(7)}`; b.style.transform = `rotate(${Math.sin(t * .6 + ph) * 8}deg)`; };
  const capBar = (L, words, hi, x, y) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', height: '96px', padding: '0 36px 0 18px', display: 'flex', alignItems: 'center', gap: '22px', background: S.INK, borderRadius: '18px', zIndex: 40, boxShadow: '0 14px 30px rgba(20,10,60,.25)', transformOrigin: '50% 50%' });
    const ic = el(b, 'div', '', { width: '64px', height: '64px', borderRadius: '12px', background: S.LI, display: 'flex', alignItems: 'center', justifyContent: 'center' }); const sv = k.svg(ic, 40, 40, 0, 0); sv.style.position = 'static';
    k.sv(sv, 'path', { d: 'M6 15 h7 l9 -8 v26 l-9 -8 h-7 z', fill: S.INK }); k.sv(sv, 'path', { d: 'M27 15 l8 10 M35 15 l-8 10', stroke: S.INK, 'stroke-width': 3.5, 'stroke-linecap': 'round' });
    b.w = words.map((w, i) => { const s = el(b, 'span', '', { fontFamily: S.MONO, fontSize: '44px', color: '#fff', position: 'relative', opacity: 0 }, w); if (i === hi) { s.style.color = S.LI; s.u = k.svg(s, 140, 18, 0, 50); k.sv(s.u, 'path', { d: 'M2 10 Q35 2 70 9 T138 7', stroke: S.LI, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round', 'stroke-dasharray': 160, 'stroke-dashoffset': 160 }); } return s; }); return b; };
  const capAt = (b, t, t0, step) => { b.w.forEach((s, i) => { const u = P(t, t0 + i * step, .2); s.style.opacity = u; s.style.top = (8 * (1 - ease.outBack(u))) + 'px'; if (s.u) s.u.firstChild.setAttribute('stroke-dashoffset', 160 * (1 - ease.out3(P(t, t0 + i * step + .15, .35)))); }); };

  // A · HI → EVA VIDEO STYLE: sticker, speed type, kinetic caption bar
  C.scene({ t0: 0, t1: 3.9, bg: S.BG, quiet: true, build(L) { const st = {}; st.b1 = blob(L, ...pk([560, 560, 620, 420], [480, 820, 560, 420]), 'linear-gradient(135deg, #2fe0b4, #3aa0ff)', 1); return st; },
    update(lt, st, t) { blobAt(st.b1, t, 0); } });
  C.scene({ t0: 0, t1: 3.9, z: 60, quiet: true, build(L) {
      const st = {}; st.b2 = blob(L, ...pk([70, 760], [870, 250]), 150, 170, 'radial-gradient(circle at 40% 35%, #8fb4ff, #4a6cff)', 45);
      st.eyes = el(L, 'div', 'abs', { left: pk(118, 918) + 'px', top: pk(815, 305) + 'px', zIndex: 46 }); [0, 1].forEach(i => el(st.eyes, 'div', 'abs', { left: (i * 26) + 'px', top: 0, width: '13px', height: '15px', borderRadius: '50%', background: S.INK }));
      st.streaks = Array.from({ length: 9 }, (_, i) => el(L, 'div', 'abs', { left: '0px', top: pk(690 + i * 22, 1200 + i * 18) + 'px', width: (300 + (i * 97) % 260) + 'px', height: (i % 3 ? 3 : 6) + 'px', borderRadius: '3px', background: 'rgba(255,255,255,.9)', zIndex: 34 }));
      st.launch = el(L, 'div', 'abs', { left: pk(360, 40) + 'px', top: pk(600, 1150) + 'px', fontFamily: S.HEAD, fontSize: pk(230, 190) + 'px', lineHeight: 1, color: '#fff', fontStyle: 'italic', transform: 'skewX(-8deg)', zIndex: 35, textShadow: '0 10px 30px rgba(40,20,90,.35)', transformOrigin: '0 50%' }, 'EVA VIDEO');
      st.day = el(L, 'div', 'abs', { left: pk(1400, 650) + 'px', top: pk(720, 1040) + 'px', fontFamily: S.HEAD, fontSize: pk(130, 104) + 'px', lineHeight: 1, color: '#fff', background: S.VI, padding: '6px 34px', borderRadius: '22px', transform: 'rotate(-6deg)', zIndex: 36, transformOrigin: '50% 50%', boxShadow: '0 16px 30px rgba(80,40,200,.35)' }, 'STYLE');
      st.newt = el(L, 'div', 'abs', { left: pk(860, 90) + 'px', top: pk(280, 230) + 'px', fontFamily: S.HEAD, fontSize: pk(140, 118) + 'px', lineHeight: 1, color: S.INK, background: S.LI, padding: '10px 44px', borderRadius: '18px', transform: 'rotate(-8deg)', zIndex: 36, transformOrigin: '50% 50%', boxShadow: '0 14px 28px rgba(60,80,0,.25)' }, "HI, I'M EVA!");
      const sv = k.svg(L, 600, 400, AX, AY); if (V) sv.style.transform = 'scale(.9,-.9)'; sv.style.zIndex = 34; st.arc = k.sv(sv, 'path', { d: 'M40 60 C240 0 420 40 410 120 C400 200 260 230 180 250', fill: 'none', stroke: S.INK, 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-dasharray': 700, 'stroke-dashoffset': 700 });
      st.dot = el(L, 'div', 'abs', { left: '0px', top: '0px', width: '30px', height: '30px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 0 6px rgba(255,255,255,.5)', zIndex: 38 });
      st.cap = capBar(L, ['Open-source', 'AI', 'video', 'editing.'], 0, pk(700, 64), pk(920, 1370));
      k.sfx('pop', .12, .14); k.sfx('whoosh', .85, .12); k.sfx('impact', .95, .16); k.sfx('pop', 1.35, .14, { f: 1100 }); [1.95, 2.3, 2.65, 3.0].forEach(x => k.sfx('click', x, .12)); return st; },
    update(lt, st, t) { blobAt(st.b2, t, 2); tf(st.b2, { y: 10 * Math.sin(t * 3), r: Math.sin(t * 1.4) * 6 }); tf(st.eyes, { y: 10 * Math.sin(t * 3), x: 4 * Math.sin(t * .9) });
      const n = pop(lt, .1, .4, 2.4); tf(st.newt, { s: n.s * (1 + .03 * Math.sin(t * 6)), o: n.o, r: -8 }); st.arc.setAttribute('stroke-dashoffset', 700 * (1 - ease.out3(P(lt, .3, .6))));
      const a = P(lt, .9, 1.6); const pt = st.arc.getPointAtLength ? st.arc.getPointAtLength(700 * ease.io3(a)) : { x: 0, y: 0 }; tf(st.dot, V ? { x: AX + 300 + (pt.x - 300) * .9 - 15, y: AY + 200 - (pt.y - 200) * .9 - 15, o: P(lt, .9, .1) } : { x: 880 + pt.x - 15, y: 190 + pt.y - 15, o: P(lt, .9, .1) });
      const l = ease.outExpo(P(lt, .9, .45)); tf(st.launch, { x: -900 * (1 - l), o: clamp(l * 4) }); st.launch.style.transform += ' skewX(-8deg)'; st.launch.style.filter = `blur(${(1 - l) * 12}px)`;
      st.streaks.forEach((s, i) => { const u = P(lt, .9 + i * .02, .5); tf(s, { x: -400 + 900 * ease.outExpo(u), o: clamp(u * 4) * (1 - P(lt, 1.5 + i * .03, .5)) }); });
      const d = pop(lt, 1.35, .4, 2.2); tf(st.day, { s: d.s, o: d.o, r: -6 }); tf(st.cap, pop(lt, 1.85, .3, 1.6)); capAt(st.cap, t, 1.95, .35); } });

  // B · style panel with a vertical preview that captions each style as it is named
  C.scene({ t0: 3.87, t1: 7.76, bg: S.BG, build(L) {
      const st = {}; st.b1 = blob(L, ...pk([740, 640, 520, 360], [520, 1080, 480, 360]), 'linear-gradient(135deg, #2fe0b4, #3aa0ff)', 1);
      st.p = el(L, 'div', 'abs', { left: pk(1180, 230) + 'px', top: pk(80, 220) + 'px', width: '620px', height: '880px', borderRadius: '44px', background: '#fff', boxShadow: '0 30px 60px rgba(60,40,140,.18)', zIndex: 20, transformOrigin: '50% 50%' });
      el(st.p, 'div', 'abs', { left: '44px', top: '44px', fontFamily: S.MONO, fontSize: '24px', letterSpacing: '.12em', color: '#333' }, 'CHOOSE A STYLE');
      const tg = el(st.p, 'div', 'abs', { left: '40px', top: '96px', width: '540px', height: '84px', borderRadius: '20px', background: '#ece6fb', display: 'flex', alignItems: 'center', gap: '22px', paddingLeft: '26px', boxSizing: 'border-box' });
      el(tg, 'span', '', { fontSize: '36px', fontFamily: "'Noto Color Emoji'" }, '🎬'); el(tg, 'span', '', { fontFamily: S.MONO, fontSize: '28px', color: '#222' }, 'Ready-to-use templates');
      el(st.p, 'div', 'abs', { left: '44px', top: '214px', fontFamily: S.MONO, fontSize: '20px', letterSpacing: '.12em', color: '#555' }, 'PREVIEW · 9:16');
      st.ph = el(st.p, 'div', 'abs', { left: '190px', top: '256px', width: '240px', height: '426px', borderRadius: '26px', overflow: 'hidden', background: '#000' }); const PW = C.src.w / C.src.h * 426; st.phi = el(st.ph, 'img', 'abs', { left: (C.src.w < C.src.h ? (240 - PW) / 2 : -260) + 'px', top: '0px', width: (C.src.w < C.src.h ? PW : 757) + 'px', height: '426px', objectFit: 'cover' });
      st.line = [el(st.ph, 'div', 'abs', { left: 0, width: '240px', top: '250px', textAlign: 'center', fontFamily: S.HEAD, fontSize: '40px', color: '#fff', textShadow: '0 2px 6px #000' }), el(st.ph, 'div', 'abs', { left: 0, width: '240px', top: '298px', textAlign: 'center', fontFamily: S.HEAD, fontSize: '40px', color: '#fff', textShadow: '0 2px 6px #000' })];
      el(st.p, 'div', 'abs', { left: '44px', top: '714px', fontFamily: S.MONO, fontSize: '20px', letterSpacing: '.12em', color: '#555' }, 'STYLES');
      st.chips = ['Cinematic', 'Futuristic', 'Social', 'Minimal'].map((c, i) => el(st.p, 'div', 'abs', { left: (40 + [0, 160, 312, 430][i]) + 'px', top: '758px', padding: '12px 20px', fontFamily: "'Inter',sans-serif", fontSize: '22px', color: '#333', border: '2px solid #e2dcef', borderRadius: '12px', background: '#fff' }, c));
      [3.95, 4.73, 5.87, 6.6].forEach(x => k.sfx('click', x, .1)); k.sfx('whoosh', 3.9, .1); return st; },
    update(lt, st, t) { blobAt(st.b1, t, 1); const p = slide(lt, .05, .5, 500, 0); tf(st.p, p); C.setSrc(st.phi, C.seq(C.evaDir, t, 451)); const AT = [3.87, 4.73, 5.87, 6.6];
      const wi = AT.reduce((m, x, i) => t >= x ? i : m, 0), HI = w => `<span style="background:#7b5cff;padding:0 6px;border-radius:4px">${w}</span>`;
      st.line[0].innerHTML = HI(['CINEMATIC', 'FUTURISTIC', 'SOCIAL', 'MINIMAL'][wi]); st.line[1].textContent = '';
      st.line.forEach(l => l.style.opacity = P(lt, .4, .1));
      st.chips.forEach((c, i) => { const on = i === wi; c.style.borderColor = on ? S.VI : '#e2dcef'; c.style.background = on ? '#f1ecff' : '#fff'; c.style.color = on ? S.VI : '#333'; });
    } });
  C.scene({ t0: 3.87, t1: 7.76, z: 60, quiet: true, build(L) { const st = {}; st.cap = capBar(L, ['Pick', 'your', 'style.'], 2, pk(110, 520), pk(900, 1180)); return st; },
    update(lt, st, t) { tf(st.cap, pop(lt, .05, .3, 1.6)); capAt(st.cap, t, 3.95, .3); } });

  // C · beat-cut punches over the full frame + segmented progress bar, then the CTA
  C.scene({ t0: 7.73, t1: C.end + .05, z: 60, build(L) {
      const st = {}; st.bar = el(L, 'div', 'abs', { left: pk(60, 64) + 'px', top: pk(40, 200) + 'px', width: pk(1800, 952) + 'px', height: '8px', display: 'flex', gap: '10px', zIndex: 50 }); st.seg = [0, 1, 2, 3, 4, 5].map(() => { const s = el(st.bar, 'div', '', { flex: 1, height: '8px', borderRadius: '4px', background: 'rgba(255,255,255,.45)', overflow: 'hidden' }); s.f = el(s, 'div', '', { width: '0%', height: '100%', background: '#fff' }); return s; });
      st.w = [['TEMPLATES', S.LI, S.INK], ['PICK', S.VI, '#fff'], ['APPLY', '#fff', S.INK], ['AI EDITS', S.LI, S.INK], ['LESS EDITING', '#fff', S.INK], ['MORE CREATING', S.VI, '#fff']].map(([w, bg, fg]) => el(L, 'div', 'abs', { left: 0, width: C.W + 'px', top: pk(560, 1200) + 'px', textAlign: 'center', zIndex: 40, opacity: 0 }, `<span style="font-family:${S.HEAD};font-size:${pk(200, 140)}px;line-height:1;color:${fg};background:${bg};padding:0 50px;border-radius:30px;display:inline-block;transform:rotate(-4deg)">${w}</span>`));
      st.fl = el(L, 'div', 'abs', { left: 0, top: 0, width: C.W + 'px', height: C.H + 'px', background: '#fff', zIndex: 45, opacity: 0 });
      st.end = el(L, 'div', 'abs', { left: 0, width: C.W + 'px', top: pk(620, 1230) + 'px', textAlign: 'center', zIndex: 40 }, `<span style="font-family:${S.HEAD};font-size:${pk(110, 76)}px;color:#fff;background:${S.VI};padding:10px 50px;border-radius:24px;display:inline-block">TRY EVA VIDEO STYLE →</span>`);
      [7.75, 8.97, 9.87, 10.67, 12.1, 12.9].forEach(x => { k.sfx('impact', x, .14); k.sfx('whoosh', x - .05, .06); }); k.sfx('pop', 13.8, .14); return st; },
    update(lt, st, t) { const beats = [7.75, 8.97, 9.87, 10.67, 12.1, 12.9], ends = [8.97, 9.87, 10.67, 12.07, 12.9, 13.77]; let fl = 0;
      st.w.forEach((w, i) => { const on = t >= beats[i] && t < ends[i]; w.style.display = on ? '' : 'none'; const u = P(t, beats[i], .18); tf(w, { s: 1.6 - .6 * ease.outBack(u, 2), o: 1 }); fl = Math.max(fl, (1 - P(t, beats[i], .12)) * (t >= beats[i] ? .6 : 0)); });
      st.fl.style.opacity = fl; st.seg.forEach((s, i) => s.f.style.width = (100 * P(t, beats[i], .5)) + '%');
      const e = pop(t, 13.8, .4, 1.8); tf(st.end, { s: e.s, o: e.o }); st.end.style.display = t >= 13.75 ? '' : 'none';
    } });
})();
