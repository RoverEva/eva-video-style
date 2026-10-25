/* T21 MINIMAL · Clean & Minimal — demo (12 s). Warm sand paper, ink serif headlines (Playfair Display) with one italic word,
 * Inter body, single 1 px taupe hairlines, compass-drawn circles; slow, quiet motion. Presenter: AI model sample. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K;
  C.src0 = 0; C.end = 12; C.evaDir = '../media/model/seq'; C.face = { x: .51, y: .27, h: .44 };
  const M = { BG: '#ece8e0', INK: '#1c1b18', MUTE: '#6f6a61', HAIR: '#cbbfa9', DASH: '#d8cfbf', SERIF: "'Playfair Display', 'Noto Serif CJK SC', serif", SANS: "'Inter', 'Noto Sans CJK SC', sans-serif" };
  const CIR = { x: 1140, y: 230, w: 440, h: 440, r: 220, s: 2.2 }, SMALL = { x: 1520, y: 120, w: 260, h: 260, r: 130, s: 2.6 }, RECT = { x: 1240, y: 220, w: 520, h: 640, r: 0, s: 1.4 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CIR, { o: 0 }) }, { t: .6, d: .9, L: CIR }, { t: 4.4, d: 1.0, L: SMALL }, { t: 8.4, d: 1.0, L: RECT }];
  C.ringFn = () => ({ color: M.HAIR, width: 2, shadow: 0 });
  const ease2 = u => ease.io3(clamp(u));
  const rise = (e, t, t0, d) => { const u = ease2(P(t, t0, d || .9)); tf(e, { y: 24 * (1 - u), o: u }); };

  C.scene({ t0: 0, t1: C.end + .05, bg: M.BG, quiet: true, build(L) {
      const st = {}; st.v = el(L, 'div', 'abs', { left: '80px', top: '0px', width: '1px', height: '1080px', background: M.HAIR, transformOrigin: '50% 0' });
      const sv = k.svg(L, 1920, 1080, 0, 0); st.c1 = k.sv(sv, 'circle', { cx: 1360, cy: 450, r: 370, fill: 'none', stroke: M.HAIR, 'stroke-width': 1.5 }); st.c1.l = 2 * Math.PI * 370;
      st.c1.setAttribute('stroke-dasharray', st.c1.l); st.c2g = k.sv(sv, 'g', {}); st.c2 = k.sv(st.c2g, 'circle', { cx: 1360, cy: 450, r: 270, fill: 'none', stroke: M.DASH, 'stroke-width': 1.5, 'stroke-dasharray': '4 7' });
      st.tick = k.sv(sv, 'line', { x1: 1360, y1: 60, x2: 1360, y2: 100, stroke: M.HAIR, 'stroke-width': 1.5 });
      // A · title page
      st.A = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });
      st.kick = el(st.A, 'div', 'abs', { left: '128px', top: '150px', fontFamily: M.SANS, fontWeight: 500, fontSize: '22px', letterSpacing: '.22em', color: M.MUTE }, 'EVA VIDEO STYLE — MINIMAL');
      st.h = ['Less noise,', 'more <i>meaning.</i>'].map((x, i) => el(st.A, 'div', 'abs', { left: '124px', top: (210 + i * 150) + 'px', fontFamily: M.SERIF, fontWeight: 400, fontSize: '150px', lineHeight: 1.05, color: M.INK, letterSpacing: '-1px' }, x));
      st.par = el(st.A, 'div', 'abs', { left: '128px', top: '560px', width: '720px', fontFamily: M.SANS, fontSize: '32px', lineHeight: 1.5, color: M.MUTE, whiteSpace: 'normal' }, 'Quiet type, slow motion and one thin line — for tutorials, business analysis and education.');
      st.meta = [['16 : 9', 'FORMAT'], ['T21', 'TEMPLATE'], ['Sand / Ink', 'PALETTE']].map(([a, b], i) => { const d = el(st.A, 'div', 'abs', { left: (128 + i * 200) + 'px', top: '760px' }); el(d, 'div', '', { fontFamily: M.SERIF, fontSize: '34px', color: M.INK }, a); el(d, 'div', '', { fontFamily: M.SANS, fontSize: '15px', letterSpacing: '.2em', color: M.MUTE, marginTop: '6px' }, b); return d; });
      // B · three principles
      st.B = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });
      st.bk = el(st.B, 'div', 'abs', { left: '128px', top: '130px', fontFamily: M.SANS, fontWeight: 500, fontSize: '22px', letterSpacing: '.22em', color: M.MUTE }, 'THREE PRINCIPLES');
      st.rows = [['01', 'Clarity', 'one idea per frame'], ['02', 'Pace', 'let every line breathe'], ['03', 'Proof', 'real numbers, real screens']].map(([n, a, b], i) => { const d = el(st.B, 'div', 'abs', { left: '128px', top: (220 + i * 190) + 'px', width: '1240px', height: '160px' });
        el(d, 'div', 'abs', { left: 0, top: '20px', fontFamily: M.SERIF, fontStyle: 'italic', fontSize: '44px', color: M.MUTE }, n); el(d, 'div', 'abs', { left: '120px', top: '0px', fontFamily: M.SERIF, fontSize: '96px', color: M.INK, lineHeight: 1 }, a); el(d, 'div', 'abs', { left: '560px', top: '40px', fontFamily: M.SANS, fontSize: '32px', color: M.MUTE }, b);
        d.ln = el(d, 'div', 'abs', { left: 0, top: '150px', width: '1240px', height: '1px', background: M.HAIR, transformOrigin: '0 50%' }); return d; });
      // C · one quote
      st.Cq = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });
      st.q = el(st.Cq, 'div', 'abs', { left: '128px', top: '300px', fontFamily: M.SERIF, fontStyle: 'italic', fontSize: '128px', color: M.INK, lineHeight: 1.1 }, '“One idea<br>per frame.”');
      st.ql = el(st.Cq, 'div', 'abs', { left: '132px', top: '640px', width: '560px', height: '1px', background: M.INK, transformOrigin: '0 50%' });
      st.qs = el(st.Cq, 'div', 'abs', { left: '132px', top: '670px', fontFamily: M.SANS, fontSize: '22px', letterSpacing: '.2em', color: M.MUTE }, 'EVA VIDEO STYLE · T21 CLEAN & MINIMAL');
      k.sfx('riser', .1, .04, { d: 1.2 }); k.sfx('ding', 1.4, .04); k.sfx('whoosh', 4.4, .05); [5.0, 5.9, 6.8].forEach(x => k.sfx('click', x, .06)); k.sfx('whoosh', 8.4, .05); k.sfx('ding', 9.3, .04); return st; },
    update(lt, st, t) { st.v.style.transform = `scaleY(${ease2(P(t, 0, 1.2))})`; st.c1.setAttribute('stroke-dashoffset', st.c1.l * (1 - ease2(P(t, .2, 1.8))));
      st.c2g.setAttribute('transform', `rotate(${t * 6} 1360 450)`); st.c2.style.opacity = ease2(P(t, .8, 1)); st.tick.setAttribute('transform', `rotate(${t * 6} 1360 450)`);
      const A = t < 4.4, B = t >= 4.4 && t < 8.4; st.A.style.opacity = A ? 1 - P(t, 4.1, .3) : 0; st.B.style.opacity = B ? P(t, 4.4, .4) * (1 - P(t, 8.1, .3)) : 0; st.Cq.style.opacity = t >= 8.4 ? P(t, 8.4, .5) : 0;
      rise(st.kick, t, .2, .8); st.h.forEach((h, i) => rise(h, t, .5 + i * .35)); rise(st.par, t, 1.5); st.meta.forEach((m, i) => rise(m, t, 2.1 + i * .2, .7));
      rise(st.bk, t, 4.5, .7); st.rows.forEach((r, i) => { rise(r, t, 5.0 + i * .9, .8); r.ln.style.transform = `scaleX(${ease2(P(t, 5.2 + i * .9, 1.0))})`; });
      rise(st.q, t, 8.6, 1.1); st.ql.style.transform = `scaleX(${ease2(P(t, 9.3, 1.2))})`; rise(st.qs, t, 9.6, .8); } });
})();
