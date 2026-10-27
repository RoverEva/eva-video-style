/* T21 Clean & Minimal — demo on the shared 15 s intro. Warm sand paper, ink serif headlines (Playfair Display) with one italic word,
 * Inter body, single 1 px taupe hairlines, compass-drawn circles; slow, quiet motion. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, I = IN; I.setup(C);
  const M = { BG: '#ece8e0', INK: '#1c1b18', MUTE: '#6f6a61', HAIR: '#cbbfa9', DASH: '#d8cfbf', SERIF: "'Playfair Display', 'Noto Serif CJK SC', serif", SANS: "'Inter', 'Noto Sans CJK SC', sans-serif" };
  const CIR = { x: 1140, y: 230, w: 440, h: 440, r: 220, s: 2.2 }, SMALL = { x: 1520, y: 120, w: 260, h: 260, r: 130, s: 2.6 }, RECT = { x: 1240, y: 220, w: 520, h: 640, r: 0, s: 1.4 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CIR, { o: 0 }) }, { t: .1, d: .9, L: CIR }, { t: 3.87, d: 1.0, L: SMALL }, { t: 7.73, d: 1.0, L: RECT }, { t: 12.07, d: 1.0, L: CIR }];
  C.ringFn = () => ({ color: M.HAIR, width: 2, shadow: 0 });
  const ease2 = u => ease.io3(clamp(u));
  const rise = (e, t, t0, d) => { const u = ease2(P(t, t0, d || .9)); tf(e, { y: 24 * (1 - u), o: u }); };
  const page = L => el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });

  C.scene({ t0: 0, t1: C.end + .05, bg: M.BG, quiet: true, build(L) {
      const st = {}; st.v = el(L, 'div', 'abs', { left: '80px', top: '0px', width: '1px', height: '1080px', background: M.HAIR, transformOrigin: '50% 0' });
      const sv = k.svg(L, 1920, 1080, 0, 0); st.c1 = k.sv(sv, 'circle', { cx: 1360, cy: 450, r: 370, fill: 'none', stroke: M.HAIR, 'stroke-width': 1.5 }); st.c1.l = 2 * Math.PI * 370;
      st.c1.setAttribute('stroke-dasharray', st.c1.l); st.c2g = k.sv(sv, 'g', {}); st.c2 = k.sv(st.c2g, 'circle', { cx: 1360, cy: 450, r: 270, fill: 'none', stroke: M.DASH, 'stroke-width': 1.5, 'stroke-dasharray': '4 7' });
      st.tick = k.sv(sv, 'line', { x1: 1360, y1: 60, x2: 1360, y2: 100, stroke: M.HAIR, 'stroke-width': 1.5 });
      // A · title page
      st.A = page(L);
      st.kick = el(st.A, 'div', 'abs', { left: '128px', top: '150px', fontFamily: M.SANS, fontWeight: 500, fontSize: '22px', letterSpacing: '.22em', color: M.MUTE }, "HI, I'M EVA");
      st.h = ['Meet Eva', 'Video <i>Style.</i>'].map((x, i) => el(st.A, 'div', 'abs', { left: '124px', top: (210 + i * 150) + 'px', fontFamily: M.SERIF, fontWeight: 400, fontSize: '150px', lineHeight: 1.05, color: M.INK, letterSpacing: '-1px' }, x));
      st.par = el(st.A, 'div', 'abs', { left: '128px', top: '560px', width: '760px', fontFamily: M.SANS, fontSize: '36px', lineHeight: 1.5, color: M.MUTE, whiteSpace: 'normal' }, 'An open-source AI video-editing skill.');
      st.meta = [['16 : 9', 'FORMAT'], ['T01 – T21', 'TEMPLATES'], ['MIT', 'LICENSE']].map(([a, b], i) => { const d = el(st.A, 'div', 'abs', { left: (128 + i * 240) + 'px', top: '760px' }); el(d, 'div', '', { fontFamily: M.SERIF, fontSize: '34px', color: M.INK }, a); el(d, 'div', '', { fontFamily: M.SANS, fontSize: '15px', letterSpacing: '.2em', color: M.MUTE, marginTop: '6px' }, b); return d; });
      // B · four styles
      st.B = page(L);
      st.bk = el(st.B, 'div', 'abs', { left: '128px', top: '110px', fontFamily: M.SANS, fontWeight: 500, fontSize: '22px', letterSpacing: '.22em', color: M.MUTE }, 'CHOOSE A STYLE');
      st.rows = [['01', 'Cinematic', 'film light, big type'], ['02', 'Futuristic', 'HUD, glow, data'], ['03', 'Social', 'fast cuts, stickers'], ['04', 'Minimalist', 'quiet type, one line']].map(([n, a, b], i) => { const d = el(st.B, 'div', 'abs', { left: '128px', top: (180 + i * 180) + 'px', width: '1240px', height: '160px' });
        el(d, 'div', 'abs', { left: 0, top: '20px', fontFamily: M.SERIF, fontStyle: 'italic', fontSize: '44px', color: M.MUTE }, n); el(d, 'div', 'abs', { left: '120px', top: '0px', fontFamily: M.SERIF, fontSize: '96px', color: M.INK, lineHeight: 1 }, a); el(d, 'div', 'abs', { left: '700px', top: '40px', fontFamily: M.SANS, fontSize: '32px', color: M.MUTE }, b);
        d.ln = el(d, 'div', 'abs', { left: 0, top: '140px', width: '1240px', height: '1px', background: M.HAIR, transformOrigin: '0 50%' }); return d; });
      // C · ready-to-use templates: three quiet lines
      st.Cq = page(L);
      st.ck = el(st.Cq, 'div', 'abs', { left: '128px', top: '200px', fontFamily: M.SANS, fontWeight: 500, fontSize: '22px', letterSpacing: '.22em', color: M.MUTE }, 'READY-TO-USE TEMPLATES');
      st.cl = ['Pick your favorite.', 'Apply it to your footage.', 'Let AI do the <i>editing.</i>'].map((x, i) => el(st.Cq, 'div', 'abs', { left: '124px', top: (280 + i * 150) + 'px', fontFamily: M.SERIF, fontSize: '92px', color: M.INK, lineHeight: 1.1 }, x));
      // D · one quote
      st.Dq = page(L);
      st.q = el(st.Dq, 'div', 'abs', { left: '128px', top: '280px', fontFamily: M.SERIF, fontStyle: 'italic', fontSize: '104px', color: M.INK, lineHeight: 1.15 }, '“Less time editing,<br>more time creating.”');
      st.ql = el(st.Dq, 'div', 'abs', { left: '132px', top: '560px', width: '560px', height: '1px', background: M.INK, transformOrigin: '0 50%' });
      st.qs = el(st.Dq, 'div', 'abs', { left: '132px', top: '590px', fontFamily: M.SANS, fontSize: '24px', letterSpacing: '.2em', color: M.MUTE }, 'TRY EVA VIDEO STYLE TODAY · GITHUB.COM/ROVEREVA');
      k.sfx('riser', .1, .04, { d: 1.2 }); k.sfx('ding', .95, .04); k.sfx('whoosh', 3.87, .05); [3.95, 4.73, 5.87, 6.6].forEach(x => k.sfx('click', x, .06)); k.sfx('whoosh', 7.73, .05); [8.97, 9.87, 10.67].forEach(x => k.sfx('click', x, .06)); k.sfx('whoosh', 12.07, .05); k.sfx('ding', 13.8, .04); return st; },
    update(lt, st, t) { st.v.style.transform = `scaleY(${ease2(P(t, 0, 1.2))})`; st.c1.setAttribute('stroke-dashoffset', st.c1.l * (1 - ease2(P(t, .2, 1.8))));
      st.c2g.setAttribute('transform', `rotate(${t * 6} 1360 450)`); st.c2.style.opacity = ease2(P(t, .8, 1)); st.tick.setAttribute('transform', `rotate(${t * 6} 1360 450)`);
      const b = [t < 3.87, t >= 3.87 && t < 7.73, t >= 7.73 && t < 12.07, t >= 12.07];
      st.A.style.opacity = b[0] ? 1 - P(t, 3.6, .27) : 0; st.B.style.opacity = b[1] ? P(t, 3.87, .4) * (1 - P(t, 7.45, .28)) : 0; st.Cq.style.opacity = b[2] ? P(t, 7.73, .4) * (1 - P(t, 11.8, .27)) : 0; st.Dq.style.opacity = b[3] ? P(t, 12.07, .5) : 0;
      rise(st.kick, t, .1, .7); st.h.forEach((h, i) => rise(h, t, .9 + i * .3)); rise(st.par, t, 1.9); st.meta.forEach((m, i) => rise(m, t, 2.5 + i * .2, .7));
      rise(st.bk, t, 3.9, .7); st.rows.forEach((r, i) => { const t0 = [3.95, 4.73, 5.87, 6.6][i]; rise(r, t, t0, .8); r.ln.style.transform = `scaleX(${ease2(P(t, t0 + .2, 1.0))})`; });
      rise(st.ck, t, 7.8, .7); st.cl.forEach((c, i) => rise(c, t, [8.97, 9.87, 10.67][i], .8));
      rise(st.q, t, 12.1, 1.1); st.ql.style.transform = `scaleX(${ease2(P(t, 13.0, 1.0))})`; rise(st.qs, t, 13.8, .8); } });
})();
