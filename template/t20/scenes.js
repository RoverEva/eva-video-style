/* T20 SOCIAL · Fast-Paced Social Media — demo (12 s). Loud kinetic type, vivid lavender/lime/violet, word-by-word captions,
 * beat-cut punches. Built for TikTok / Shorts / Reels energy, laid out 16:9. Presenter: AI model sample. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K;
  C.src0 = 0; C.end = 12; C.evaDir = '../media/model/seq'; C.face = { x: .51, y: .27, h: .44 };
  const S = { BG: '#ece6fb', VI: '#7b5cff', LI: '#d6ff3a', INK: '#111015', MONO: "'Space Mono', monospace", HEAD: "'Anton', 'Archivo Black', sans-serif" };
  const CARD = { x: 150, y: 70, w: 640, h: 820, r: 52, s: 1.6 }, CARD2 = { x: 110, y: 90, w: 600, h: 780, r: 48, s: 1.6 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .05, d: .45, L: CARD }, { t: 4.4, d: .5, L: CARD2 }, { t: 8.4, d: .35, L: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 } }];
  C.ringFn = t => t < 8.4 ? { color: '#fff', width: 10, shadow: .35 } : { color: 'transparent', width: 0, shadow: 0 };

  const blob = (L, x, y, w, h, grad, z) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: grad, zIndex: z || 1, filter: 'saturate(1.1)' }); return b; };
  const blobAt = (b, t, ph) => { const r = n => (50 + 12 * Math.sin(t * 1.3 + ph + n)).toFixed(1) + '%'; b.style.borderRadius = `${r(0)} ${r(1)} ${r(2)} ${r(3)} / ${r(4)} ${r(5)} ${r(6)} ${r(7)}`; b.style.transform = `rotate(${Math.sin(t * .6 + ph) * 8}deg)`; };
  const capBar = (L, words, hi, x, y) => { const b = el(L, 'div', 'abs', { left: x + 'px', top: y + 'px', height: '96px', padding: '0 36px 0 18px', display: 'flex', alignItems: 'center', gap: '22px', background: S.INK, borderRadius: '18px', zIndex: 40, boxShadow: '0 14px 30px rgba(20,10,60,.25)', transformOrigin: '50% 50%' });
    const ic = el(b, 'div', '', { width: '64px', height: '64px', borderRadius: '12px', background: S.LI, display: 'flex', alignItems: 'center', justifyContent: 'center' }); const sv = k.svg(ic, 40, 40, 0, 0); sv.style.position = 'static';
    k.sv(sv, 'path', { d: 'M6 15 h7 l9 -8 v26 l-9 -8 h-7 z', fill: S.INK }); k.sv(sv, 'path', { d: 'M27 15 l8 10 M35 15 l-8 10', stroke: S.INK, 'stroke-width': 3.5, 'stroke-linecap': 'round' });
    b.w = words.map((w, i) => { const s = el(b, 'span', '', { fontFamily: S.MONO, fontSize: '44px', color: '#fff', position: 'relative', opacity: 0 }, w); if (i === hi) { s.style.color = S.LI; s.u = k.svg(s, 140, 18, 0, 50); k.sv(s.u, 'path', { d: 'M2 10 Q35 2 70 9 T138 7', stroke: S.LI, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round', 'stroke-dasharray': 160, 'stroke-dashoffset': 160 }); } return s; }); return b; };
  const capAt = (b, t, t0, step) => { b.w.forEach((s, i) => { const u = P(t, t0 + i * step, .2); s.style.opacity = u; s.style.top = (8 * (1 - ease.outBack(u))) + 'px'; if (s.u) s.u.firstChild.setAttribute('stroke-dashoffset', 160 * (1 - ease.out3(P(t, t0 + i * step + .15, .35)))); }); };

  // A · LAUNCH DAY: sticker, speed type, kinetic caption bar
  C.scene({ t0: 0, t1: 4.43, bg: S.BG, quiet: true, build(L) { const st = {}; st.b1 = blob(L, 560, 560, 620, 420, 'linear-gradient(135deg, #2fe0b4, #3aa0ff)', 1); return st; },
    update(lt, st, t) { blobAt(st.b1, t, 0); } });
  C.scene({ t0: 0, t1: 4.43, z: 60, quiet: true, build(L) {
      const st = {}; st.b2 = blob(L, 70, 760, 150, 170, 'radial-gradient(circle at 40% 35%, #8fb4ff, #4a6cff)', 45);
      st.eyes = el(L, 'div', 'abs', { left: '118px', top: '815px', zIndex: 46 }); [0, 1].forEach(i => el(st.eyes, 'div', 'abs', { left: (i * 26) + 'px', top: 0, width: '13px', height: '15px', borderRadius: '50%', background: S.INK }));
      st.streaks = Array.from({ length: 9 }, (_, i) => el(L, 'div', 'abs', { left: '0px', top: (690 + i * 22) + 'px', width: (300 + (i * 97) % 260) + 'px', height: (i % 3 ? 3 : 6) + 'px', borderRadius: '3px', background: 'rgba(255,255,255,.9)', zIndex: 34 }));
      st.launch = el(L, 'div', 'abs', { left: '360px', top: '600px', fontFamily: S.HEAD, fontSize: '230px', lineHeight: 1, color: '#fff', fontStyle: 'italic', transform: 'skewX(-8deg)', zIndex: 35, textShadow: '0 10px 30px rgba(40,20,90,.35)', transformOrigin: '0 50%' }, 'LAUNCH');
      st.day = el(L, 'div', 'abs', { left: '1240px', top: '650px', fontFamily: S.HEAD, fontSize: '150px', lineHeight: 1, color: '#fff', background: S.VI, padding: '6px 34px', borderRadius: '22px', transform: 'rotate(-6deg)', zIndex: 36, transformOrigin: '50% 50%', boxShadow: '0 16px 30px rgba(80,40,200,.35)' }, 'DAY');
      st.newt = el(L, 'div', 'abs', { left: '900px', top: '300px', fontFamily: S.HEAD, fontSize: '170px', lineHeight: 1, color: S.INK, background: S.LI, padding: '10px 44px', borderRadius: '18px', transform: 'rotate(-8deg)', zIndex: 36, transformOrigin: '50% 50%', boxShadow: '0 14px 28px rgba(60,80,0,.25)' }, 'NEW');
      const sv = k.svg(L, 600, 400, 880, 190); sv.style.zIndex = 37; st.arc = k.sv(sv, 'path', { d: 'M40 60 C240 0 420 40 410 120 C400 200 260 230 180 250', fill: 'none', stroke: S.INK, 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-dasharray': 700, 'stroke-dashoffset': 700 });
      st.dot = el(L, 'div', 'abs', { left: '0px', top: '0px', width: '30px', height: '30px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 0 6px rgba(255,255,255,.5)', zIndex: 38 });
      st.cap = capBar(L, ['Short.', 'Loud.', 'Clear.'], 1, 760, 920);
      k.sfx('whoosh', .05, .1); k.sfx('pop', .55, .14); k.sfx('whoosh', 1.0, .12); k.sfx('impact', 1.15, .16); k.sfx('pop', 1.5, .14, { f: 1100 }); [2.2, 2.6, 3.0].forEach((x, i) => k.sfx('click', x, .12)); return st; },
    update(lt, st, t) { blobAt(st.b2, t, 2); tf(st.b2, { y: 10 * Math.sin(t * 3), r: Math.sin(t * 1.4) * 6 }); tf(st.eyes, { y: 10 * Math.sin(t * 3), x: 4 * Math.sin(t * .9) });
      const n = pop(lt, .55, .4, 2.4); tf(st.newt, { s: n.s * (1 + .03 * Math.sin(t * 6)), o: n.o, r: -8 }); st.arc.setAttribute('stroke-dashoffset', 700 * (1 - ease.out3(P(lt, .7, .6))));
      const a = P(lt, 1.3, 1.6); const pt = st.arc.getPointAtLength ? st.arc.getPointAtLength(700 * ease.io3(a)) : { x: 0, y: 0 }; tf(st.dot, { x: 880 + pt.x - 15, y: 190 + pt.y - 15, o: P(lt, 1.3, .1) });
      const l = ease.outExpo(P(lt, 1.0, .45)); tf(st.launch, { x: -900 * (1 - l), o: clamp(l * 4) }); st.launch.style.transform += ' skewX(-8deg)'; st.launch.style.filter = `blur(${(1 - l) * 12}px)`;
      st.streaks.forEach((s, i) => { const u = P(lt, 1.0 + i * .02, .5); tf(s, { x: -400 + 900 * ease.outExpo(u), o: clamp(u * 4) * (1 - P(lt, 1.6 + i * .03, .5)) }); });
      const d = pop(lt, 1.5, .4, 2.2); tf(st.day, { s: d.s, o: d.o, r: -6 }); tf(st.cap, pop(lt, 2.0, .3, 1.6)); capAt(st.cap, t, 2.2, .4); } });

  // B · caption-style panel with a vertical preview that captions word by word
  C.scene({ t0: 4.4, t1: 8.43, bg: S.BG, build(L) {
      const st = {}; st.b1 = blob(L, 740, 640, 520, 360, 'linear-gradient(135deg, #2fe0b4, #3aa0ff)', 1);
      st.p = el(L, 'div', 'abs', { left: '1180px', top: '80px', width: '620px', height: '880px', borderRadius: '44px', background: '#fff', boxShadow: '0 30px 60px rgba(60,40,140,.18)', zIndex: 20, transformOrigin: '50% 50%' });
      el(st.p, 'div', 'abs', { left: '44px', top: '44px', fontFamily: S.MONO, fontSize: '24px', letterSpacing: '.12em', color: '#333' }, 'KINETIC CAPTIONS');
      const tg = el(st.p, 'div', 'abs', { left: '40px', top: '96px', width: '540px', height: '84px', borderRadius: '20px', background: '#ece6fb', display: 'flex', alignItems: 'center', gap: '22px', paddingLeft: '26px', boxSizing: 'border-box' });
      el(tg, 'span', '', { fontSize: '36px', fontFamily: "'Noto Color Emoji'" }, '🔇'); el(tg, 'span', '', { fontFamily: S.MONO, fontSize: '28px', color: '#222' }, 'Mute-first');
      el(st.p, 'div', 'abs', { left: '44px', top: '214px', fontFamily: S.MONO, fontSize: '20px', letterSpacing: '.12em', color: '#555' }, 'PREVIEW · 9:16');
      st.ph = el(st.p, 'div', 'abs', { left: '190px', top: '256px', width: '240px', height: '426px', borderRadius: '26px', overflow: 'hidden', background: '#000' }); st.phi = el(st.ph, 'img', 'abs', { left: '-260px', top: '0px', width: '757px', height: '426px', objectFit: 'cover' });
      st.line = [el(st.ph, 'div', 'abs', { left: 0, width: '240px', top: '250px', textAlign: 'center', fontFamily: S.HEAD, fontSize: '40px', color: '#fff', textShadow: '0 2px 6px #000' }), el(st.ph, 'div', 'abs', { left: 0, width: '240px', top: '298px', textAlign: 'center', fontFamily: S.HEAD, fontSize: '40px', color: '#fff', textShadow: '0 2px 6px #000' })];
      el(st.p, 'div', 'abs', { left: '44px', top: '714px', fontFamily: S.MONO, fontSize: '20px', letterSpacing: '.12em', color: '#555' }, 'STYLE');
      st.chips = ['Bold', 'Clean', 'Typewriter', 'Punchy'].map((c, i) => el(st.p, 'div', 'abs', { left: (40 + [0, 120, 250, 430][i]) + 'px', top: '758px', padding: '12px 20px', fontFamily: "'Inter',sans-serif", fontSize: '22px', color: '#333', border: '2px solid #e2dcef', borderRadius: '12px', background: '#fff' }, c));
      [5.0, 5.8, 6.6, 7.4].forEach((x, i) => k.sfx('click', x, .1)); k.sfx('whoosh', 4.45, .1); return st; },
    update(lt, st, t) { blobAt(st.b1, t, 1); const p = slide(lt, .05, .5, 500, 0); tf(st.p, p); C.setSrc(st.phi, C.seq('../media/model/seq', t, 900));
      const wi = Math.min(3, Math.max(0, Math.floor((lt - .4) / .5) % 4)), HI = w => `<span style="background:#7b5cff;padding:0 6px;border-radius:4px">${w}</span>`;
      st.line[0].innerHTML = ['BIG', 'BIG ' + HI('WORDS.'), 'FAST', 'FAST ' + HI('CUTS.')][wi]; st.line[1].textContent = '';
      st.line.forEach(l => l.style.opacity = P(lt, .4, .1));
      const ac = Math.floor(P(t, 5.0, 3.2) * 4 - .001); st.chips.forEach((c, i) => { const on = i === Math.max(0, ac); c.style.borderColor = on ? S.VI : '#e2dcef'; c.style.background = on ? '#f1ecff' : '#fff'; c.style.color = on ? S.VI : '#333'; });
    } });
  C.scene({ t0: 4.4, t1: 8.43, z: 60, quiet: true, build(L) { const st = {}; st.cap = capBar(L, ['Reads', 'with', 'sound', 'off.'], 2, 110, 900); return st; },
    update(lt, st, t) { tf(st.cap, pop(lt, .3, .3, 1.6)); capAt(st.cap, t, 4.8, .35); } });

  // C · beat-cut punches over the full frame + segmented progress bar
  C.scene({ t0: 8.4, t1: C.end + .05, z: 60, build(L) {
      const st = {}; st.bar = el(L, 'div', 'abs', { left: '60px', top: '40px', width: '1800px', height: '8px', display: 'flex', gap: '10px', zIndex: 50 }); st.seg = [0, 1, 2, 3].map(() => { const s = el(st.bar, 'div', '', { flex: 1, height: '8px', borderRadius: '4px', background: 'rgba(255,255,255,.45)', overflow: 'hidden' }); s.f = el(s, 'div', '', { width: '0%', height: '100%', background: '#fff' }); return s; });
      st.w = [['3', S.LI, S.INK], ['TIPS', S.VI, '#fff'], ['IN', '#fff', S.INK], ['30s', S.LI, S.INK]].map(([w, bg, fg]) => el(L, 'div', 'abs', { left: 0, width: '1920px', top: '560px', textAlign: 'center', zIndex: 40, opacity: 0 }, `<span style="font-family:${S.HEAD};font-size:260px;line-height:1;color:${fg};background:${bg};padding:0 50px;border-radius:30px;display:inline-block;transform:rotate(-4deg)">${w}</span>`));
      st.fl = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: '#fff', zIndex: 45, opacity: 0 });
      st.end = el(L, 'div', 'abs', { left: 0, width: '1920px', top: '620px', textAlign: 'center', zIndex: 40 }, `<span style="font-family:${S.HEAD};font-size:110px;color:#fff;background:${S.VI};padding:10px 50px;border-radius:24px;display:inline-block">FOLLOW FOR MORE →</span>`);
      [8.5, 9.0, 9.5, 10.0].forEach((x, i) => { k.sfx('impact', x, .14); k.sfx('whoosh', x - .05, .06); }); k.sfx('pop', 10.6, .14); return st; },
    update(lt, st, t) { const beats = [8.5, 9.0, 9.5, 10.0]; let fl = 0;
      st.w.forEach((w, i) => { const on = t >= beats[i] && t < beats[i] + .5; w.style.display = on ? '' : 'none'; const u = P(t, beats[i], .18); tf(w, { s: 1.6 - .6 * ease.outBack(u, 2), o: 1 }); fl = Math.max(fl, (1 - P(t, beats[i], .12)) * (t >= beats[i] ? .6 : 0)); });
      st.fl.style.opacity = fl; st.seg.forEach((s, i) => s.f.style.width = (100 * P(t, beats[i], .5)) + '%');
      const e = pop(t, 10.6, .4, 1.8); tf(st.end, { s: e.s, o: e.o }); st.end.style.display = t >= 10.55 ? '' : 'none';
    } });
})();
