/* T19 FOOTAGE · 真实影像引入 Footage Intro — demo (12.6 s, J8 4.1–16.7 s).
 * Eva is cut out (AI matte, original colours) while backgrounds swap fast; the real footage pushes in;
 * the cut-out shrinks into a circle that lands where it does not cover the footage; end title card.
 * Background plates are Eva's own images; footage is her real HatchElite website recording. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, T = K.T;
  C.src0 = 4.1; C.end = 12.6; C.evaDir = '../media/eva'; C.face = { x: .54, y: .35, h: .47 };
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }];   // the presenter is drawn by the cut-out rig below
  C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const CYAN = '#2ee6ff', LIME = '#7dff3a', F0 = 123;                           // first J8 frame of this demo
  const CUT = t => `../media/t19/cut/f_${String(F0 + Math.round(t * 30)).padStart(5, '0')}.webp`;
  const PL = i => `../media/t19/plates/p${i}.jpg`;
  // background beats: plate swaps then the real footage (push). type = transition into that layer
  const SW = [[0, 'flash'], [.6, 'whip'], [1.2, 'zoom'], [1.75, 'glitch'], [2.3, 'iris'], [2.85, 'push']];
  const FOOT = 2.85, MORPH = 4.0, HOP = 7.3, CARD = 8.7;
  const FACE = [.54 * 1920, .35 * 1080];
  // circle stops (centre x, y, radius) — chosen to leave the footage's main content clear
  const BL = [260, 790, 200], TL = [260, 300, 200], BL2 = [270, 790, 215];

  C.scene({ t0: 0, t1: C.end + .05, bg: '#000', quiet: true, build(L) {
      const st = { L: [] };
      // ---------- background stack: 5 plates + real footage ----------
      SW.forEach(([t0, ty], i) => {
        const w = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', overflow: 'hidden', zIndex: 2 + i });
        const im = el(w, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', transformOrigin: '50% 50%' });
        if (i < 5) C.setSrc(im, PL(i + 1));
        let sl = null; if (ty === 'glitch') { w.style.overflow = 'visible'; sl = [];
          for (let j = 0; j < 8; j++) { const s = el(w, 'div', 'abs', { left: 0, top: (j * 135) + 'px', width: '1920px', height: '135px', overflow: 'hidden' }); const si = el(s, 'img', 'abs', { left: 0, top: (-j * 135) + 'px', width: '1920px', height: '1080px', objectFit: 'cover' }); C.setSrc(si, PL(i + 1)); sl.push(s); } im.style.display = 'none'; }
        st.L.push({ w, im, t0, ty, sl, i });
      });
      st.flash = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: '#fff', zIndex: 20, opacity: 0 });
      // end-card dimming over the footage
      st.dim = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 12, background: 'linear-gradient(90deg, rgba(3,8,30,.92) 0%, rgba(3,8,30,.78) 45%, rgba(3,8,30,.66) 75%, rgba(3,8,30,.55))', opacity: 0 });
      st.spots = [0, 1, 2, 3].map(i => el(L, 'div', 'abs', { left: (980 + i * 240) + 'px', top: '960px', width: '160px', height: '160px', borderRadius: '50%', zIndex: 13, background: 'radial-gradient(circle, rgba(140,200,255,.9), rgba(60,140,255,.25) 35%, rgba(0,0,0,0) 70%)', opacity: 0 }));

      // ---------- presenter rig: cut-out that shrinks into a circle ----------
      st.rig = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 30, overflow: 'hidden' });
      st.inner = el(st.rig, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transformOrigin: '0 0' });
      st.pb = el(st.inner, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', filter: 'blur(14px) brightness(1.05)', opacity: 0 }); C.setSrc(st.pb, PL(1));
      st.cut = el(st.inner, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });
      st.ring = el(L, 'div', 'abs', { left: 0, top: 0, borderRadius: '50%', zIndex: 31, boxSizing: 'border-box', border: '8px solid #fff', opacity: 0 });

      // ---------- end card ----------
      st.card = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 25 });
      const hs = (txt, x, y, size, grad, glow) => el(st.card, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: "'Inter','Noto Sans CJK SC',sans-serif", fontWeight: 900, fontStyle: 'italic', fontSize: size + 'px', lineHeight: 1, letterSpacing: '-2px', whiteSpace: 'nowrap', transform: 'skewX(-6deg)', transformOrigin: '0 50%',
        color: grad ? 'transparent' : '#fff', backgroundImage: grad || 'none', WebkitBackgroundClip: grad ? 'text' : 'border-box', backgroundClip: grad ? 'text' : 'border-box', filter: `drop-shadow(0 0 ${glow || 14}px rgba(46,230,255,.75)) drop-shadow(0 6px 0 rgba(0,0,0,.45))` }, txt);
      st.h1 = hs("Eva's", 110, 60, 92); st.h2 = hs('TECH VIDEO', 100, 150, 170, 'linear-gradient(180deg, #ffffff 0%, #bff6ff 35%, #2ee6ff 70%, #1a8cff 100%)', 22); st.h3 = hs('STYLE', 104, 318, 150, 'linear-gradient(180deg, #ffffff, #d7dde6 60%, #9aa6b8)', 10);
      st.bn = el(st.card, 'div', 'abs cn', { left: '150px', top: '486px', padding: '12px 34px', fontSize: '52px', fontWeight: 900, color: LIME, border: `3px solid ${LIME}`, background: 'rgba(10,40,10,.55)', boxShadow: `0 0 26px rgba(125,255,58,.6), inset 0 0 18px rgba(125,255,58,.25)`, transform: 'rotate(-4deg)', transformOrigin: '0 50%' }, '科技类视频 · 动效模版');
      st.wm = el(st.card, 'div', 'abs mono', { right: '70px', top: '60px', fontSize: '28px', letterSpacing: '.45em', color: '#fff' }, 'EVA VIDEO STYLE');
      // original blueprint line drawing (a laptop), drawn on with stroke-dash
      const s = k.svg(st.card, 560, 330, 1230, 300); st.bp = [];
      ['M60 250 L500 250 L540 300 L20 300 Z', 'M110 40 L450 40 L450 245 L110 245 Z', 'M140 70 L420 70 L420 215 L140 215 Z', 'M180 110 L300 110 M180 140 L380 140 M180 170 L340 170', 'M230 275 L330 275'].forEach(d => { const p = k.sv(s, 'path', { d, fill: 'none', stroke: 'rgba(120,200,255,.85)', 'stroke-width': 2.5, 'stroke-linejoin': 'round' }); const l = p.getTotalLength ? p.getTotalLength() || 1400 : 1400; p.setAttribute('stroke-dasharray', l); p.setAttribute('stroke-dashoffset', l); p.l = l; st.bp.push(p); });
      st.tags = ['FAST CUTS?', 'REAL FOOTAGE?', 'SMART CAPTIONS?', 'REUSABLE?'].map((tx, i) => { const d = el(st.card, 'div', 'abs', { left: (560 + i * 22) + 'px', top: (640 + i * 74) + 'px', padding: '6px 24px', fontFamily: "'Inter',sans-serif", fontWeight: 800, fontSize: '36px', color: '#fff', border: '2px solid rgba(46,230,255,.8)', background: 'rgba(5,20,60,.75)', boxShadow: '0 0 16px rgba(46,230,255,.35)', transform: 'skewX(-8deg)', transformOrigin: '0 50%' }, tx);
        el(d, 'div', 'abs', { left: '-36px', top: '24px', width: '30px', height: '2px', background: 'rgba(46,230,255,.8)' }); return d; });

      // ---------- sound ----------
      SW.forEach(([t0, ty], i) => k.sfx(i === 5 ? 'whoosh' : (i % 2 ? 'whoosh' : 'click'), t0 + .02, i === 5 ? .14 : .09));
      k.sfx('impact', FOOT + .4, .14); k.sfx('pop', MORPH + .55, .14); k.sfx('whoosh', HOP, .1); k.sfx('pop', HOP + .45, .1, { f: 1100 });
      k.sfx('riser', CARD - .6, .07, { d: .6 }); k.sfx('impact', CARD + .05, .18); k.sfx('ding', CARD + .9, .07); st.tags.forEach((_, i) => k.sfx('click', CARD + 1.5 + i * .3, .1));
      return st; },

    update(lt, st, t) {
      // backgrounds
      st.L.forEach((Ly, i) => { const nx = SW[i + 1] ? SW[i + 1][0] : 99, u = P(t, Ly.t0, Ly.ty === 'push' ? .45 : .28), e = ease.outExpo(u), life = t - Ly.t0;
        Ly.w.style.display = t >= Ly.t0 && t < nx + .5 ? '' : 'none'; if (Ly.w.style.display) return;
        if (Ly.i === 5) C.setSrc(Ly.im, C.seq('../media/web', Math.max(0, life) * 1.15 + 1, 451));
        const kb = Ly.i < 5 ? 1.12 - .08 * clamp(life / .9) : 1.0;              // Ken Burns push on every plate
        let x = (Ly.i % 2 ? -1 : 1) * 30 * clamp(life / .9), s = kb, blur = 0, clip = 'none';
        if (Ly.ty === 'whip') { x += 1920 * (1 - e); blur = 30 * (1 - e); }
        if (Ly.ty === 'zoom') { s *= 1 + .35 * (1 - e); }
        if (Ly.ty === 'iris') clip = `circle(${(1 - Math.pow(1 - u, 3)) * 1250}px at ${FACE[0]}px ${FACE[1]}px)`;
        if (Ly.ty === 'push') { x = 1920 * (1 - e); blur = 18 * (1 - e); }
        Ly.w.style.clipPath = clip; tf(Ly.im, { x, s }); Ly.im.style.filter = blur ? `blur(${blur}px)` : 'none';
        if (Ly.sl) Ly.sl.forEach((sl, j) => { const off = (1 - e) * ((j * 7919) % 11 - 5) * 120; tf(sl, { x: off }); sl.firstChild.style.transform = `scale(${s})`; sl.firstChild.style.transformOrigin = `960px ${540 + j * 135}px`; });
        // the outgoing plate gets pushed too, so the slide reads as one motion
        const nxt = st.L[i + 1]; if (nxt && t >= nxt.t0 && (nxt.ty === 'push' || nxt.ty === 'whip')) { const ue = ease.outExpo(P(t, nxt.t0, nxt.ty === 'push' ? .45 : .28)); tf(Ly.im, { x: x - (nxt.ty === 'push' ? 700 : 1920) * ue, s }); Ly.im.style.filter = `blur(${20 * ue}px)`; } });
      const fl = SW.reduce((m, [t0, ty]) => Math.max(m, (ty === 'flash' || ty === 'zoom' ? .85 : ty === 'glitch' ? .35 : 0) * (1 - P(t, t0, .18)) * (t >= t0 ? 1 : 0)), 0);
      st.flash.style.opacity = fl;

      // presenter rig
      C.setSrc(st.cut, CUT(t));
      const m = ease.io3(P(t, MORPH, .6));                                        // cut-out -> circle
      let [cx, cy, r] = BL; const hp = ease.outBack(P(t, HOP, .5), 1.4);            // hop to top-left, then back for the end card
      if (t >= HOP) { cx = lerp(BL[0], TL[0], hp); cy = lerp(BL[1], TL[1], hp) - 50 * Math.sin(Math.PI * clamp(P(t, HOP, .5))); r = BL[2]; }
      const bk = ease.outBack(P(t, CARD - .25, .5), 1.3); if (t >= CARD - .25) { cx = lerp(TL[0], BL2[0], bk); cy = lerp(TL[1], BL2[1], bk); r = lerp(TL[2], BL2[2], bk); }
      const R = lerp(1500, r, m), CX = lerp(FACE[0], cx, m), CY = lerp(FACE[1], cy - .12 * r, m), S = lerp(1, (r * 2 * .5) / 460, m);
      st.rig.style.clipPath = m > 0 ? `circle(${R}px at ${CX}px ${CY + .12 * r * m}px)` : 'none';
      st.inner.style.transform = `translate(${CX - S * FACE[0]}px, ${CY - S * FACE[1]}px) scale(${S})`;
      st.pb.style.opacity = clamp((m - .6) / .4);
      const rc = CY + .12 * r * m, ring = P(t, MORPH + .35, .25), card = P(t, CARD, .4);
      Object.assign(st.ring.style, { left: (CX - R) + 'px', top: (rc - R) + 'px', width: 2 * R + 'px', height: 2 * R + 'px', opacity: ring,
        borderColor: card > .5 ? CYAN : '#fff', boxShadow: card > .5 ? `0 0 ${30 + 10 * Math.sin(t * 5)}px rgba(46,230,255,.85), inset 0 0 20px rgba(46,230,255,.4)` : '0 12px 40px rgba(0,0,0,.45)' });
      if (m > 0 && m < 1) st.ring.style.transform = `scale(${1 + .06 * Math.sin(Math.PI * m)})`; else st.ring.style.transform = '';

      // end card
      st.dim.style.opacity = card; st.spots.forEach((sp, i) => sp.style.opacity = card * (.55 + .45 * Math.sin(t * 2 + i)));
      st.card.style.display = t >= CARD - .05 ? '' : 'none';
      tf(st.h1, slide(t, CARD + .05, .4, -120, 0)); st.h1.style.transform += ' skewX(-6deg)';
      const h2 = pop(t, CARD + .25, .45, 1.6); tf(st.h2, { s: h2.s, o: h2.o }); st.h2.style.transform += ' skewX(-6deg)';
      tf(st.h3, slide(t, CARD + .6, .4, -160, 0)); st.h3.style.transform += ' skewX(-6deg)';
      const b = pop(t, CARD + .9, .4, 1.8); tf(st.bn, { s: b.s, o: b.o, r: -4 });
      st.wm.style.opacity = P(t, CARD + .3, .4);
      st.bp.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.l * (1 - ease.out3(P(t, CARD + .6 + i * .15, .9)))));
      st.tags.forEach((d, i) => { tf(d, slide(t, CARD + 1.5 + i * .3, .4, 120, 0)); d.style.transform += ' skewX(-8deg)'; });
    } });
})();
