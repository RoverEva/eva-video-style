/* T03 Dark 3D Stage — demo on the shared 15 s intro (real screen recordings on tilted 3D screens) */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, I = IN; I.setup(C);
  const TR = { x: 1620, y: 40, w: 240, h: 240, r: 120, s: 3 }, BIG = { x: 1300, y: 230, w: 520, h: 640, r: 24, s: 1.5 };
  C.evaKeys = [{ t: 0, d: 0, L: BIG }, { t: 3.87, d: .5, L: TR }];
  C.ringFn = () => ({ color: k.OR, width: 5, glow: 'rgba(255,122,26,.45)', shadow: .4 });
  const N = { web: 451, wb: 3327, fly: 286, whis: 403, sent: 2088, match: 387 };
  C.scene({ t0: 0, t1: C.end + .05, bg: k.stageBg, quiet: true, build(L) {
      const st = {}; st.fl = k.floor(L); const rig = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', perspective: '1600px' });
      const scr = (x, y, w, dir, lab) => { const s = k.screen(rig, x, y, w, 16 / 9, { transformOrigin: '50% 50%', borderRadius: '14px' }); s.src_ = dir; if (lab) { s.lab = el(L, 'div', 'abs disp', { left: x + 'px', top: (y + w * 9 / 16 + 18) + 'px', width: w + 'px', textAlign: 'center', fontSize: '44px', color: '#fff', transformOrigin: '50% 0' }, lab); } return s; };
      st.hi = k.disp(L, "HI, I'M EVA", '#fff', 120, 110, 80); st.name = el(L, 'div', 'abs disp', { left: '110px', top: '210px', fontSize: '130px', color: 'transparent', backgroundImage: `linear-gradient(90deg, ${k.OR}, ${k.PU})`, WebkitBackgroundClip: 'text', backgroundClip: 'text' }, 'EVA VIDEO STYLE');
      st.oss = k.hud(L, 'OPEN-SOURCE · AI VIDEO-EDITING SKILL', k.OR, 116, 350, 26, { opacity: 1 });
      st.s0 = scr(110, 430, 760, 'web'); st.s0.ry = 18;
      st.s = [['fly', 'CINEMATIC'], ['whis', 'FUTURISTIC TECH'], ['sent', 'SOCIAL MEDIA'], ['match', 'MINIMALIST']].map(([d, lab], i) => { const s = scr(70 + i * 380, 360, 350, d, lab); s.ry = [24, 8, -8, -24][i]; return s; });
      st.big = scr(250, 150, 1100, 'wb'); st.big.ry = 0;
      st.steps = ['① PICK', '② APPLY', '③ AI EDITS'].map((x, i) => k.O(k.chip(L, x, i === 2 ? k.OR : '#fff', k.INK, 48, 250 + i * 380, 800), '50% 50%'));
      st.a = scr(110, 300, 640, 'wb', 'LESS TIME EDITING'); st.a.ry = 20; st.b = scr(820, 260, 700, 'fly', 'MORE TIME CREATING'); st.b.ry = -16;
      st.cta = k.O(k.chip(L, 'TRY EVA VIDEO STYLE TODAY →', k.OR, '#0b0b0d', 54, 500, 120), '50% 50%');
      k.sfx('whoosh', .1, .1); k.sfx('pop', .95, .12); k.sfx('pop', 1.95, .1); [3.9, 4.75, 5.9, 6.6].forEach((x, i) => k.sfx('whoosh', x, .08)); k.sfx('impact', 7.75, .14); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .12, { f: 900 + i * 150 })); k.sfx('whoosh', 12.1, .1); k.sfx('pop', 12.9, .12); k.sfx('ding', 13.8, .08); return st; },
    update(lt, st, t) { const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      const show = (s, on, t0) => { s.style.display = on ? '' : 'none'; if (s.lab) s.lab.style.display = on ? '' : 'none'; if (!on) return; const u = ease.outExpo(P(t, t0, .6)); s.style.opacity = clamp(u * 3); s.style.transform = `rotateY(${s.ry + 3 * Math.sin(t * .7)}deg) translateY(${(1 - u) * 240}px) translateZ(${-220 * (1 - u)}px)`; k.play(s, '../media/' + s.src_, 0, (t - t0) * 1.2, N[s.src_]); if (s.lab) tf(s.lab, pop(t, t0 + .3, .35, 1.6)); };
      [st.hi, st.name, st.oss].forEach(e => e.style.display = b[0] ? '' : 'none'); tf(st.hi, slide(t, .1, .4, -100, 0)); tf(st.name, slide(t, .9, .45, -100, 0)); tf(st.oss, { o: P(t, 1.95, .3) }); show(st.s0, b[0], .3);
      st.s.forEach((s, i) => show(s, b[1], [3.87, 4.73, 5.87, 6.6][i])); show(st.big, b[2], 7.73); st.steps.forEach((c, i) => { c.style.display = b[2] ? '' : 'none'; tf(c, pop(t, [8.97, 9.87, 10.67][i], .35, 1.8)); });
      show(st.a, b[3], 12.1); show(st.b, b[3], 12.9); st.a.style.filter = b[3] ? `grayscale(${P(t, 12.9, .4)}) brightness(${1 - .4 * P(t, 12.9, .4)})` : ''; st.cta.style.display = b[3] ? '' : 'none'; tf(st.cta, pop(t, 13.8, .4, 1.8)); } });
})();
