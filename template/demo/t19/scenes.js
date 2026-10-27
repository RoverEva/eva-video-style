/* T19 Footage Intro — demo on the shared 15 s intro.
 * The presenter is cut out (AI matte, original colours) while backgrounds you import swap fast; real footage pushes in and
 * changes with every style she names; the cut-out shrinks into a circle that lands where it does not cover the footage;
 * end title card. Footage: HatchElite screen recordings and cartoon clips. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp, lerp } = C, k = K, T = K.T, I = IN; I.setup(C);
  C.evaKeys = [{ t: 0, d: 0, L: { x: 0, y: 0, w: 10, h: 10, r: 0, o: 0 } }];   // the presenter is drawn by the cut-out rig below
  C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  const CYAN = '#2ee6ff', LIME = '#7dff3a', BIG = "'Inter','Noto Sans CJK SC',sans-serif";
  const CUT = t => `../media/cut/f_${String(Math.min(450, Math.max(0, Math.round(t * 30)))).padStart(5, '0')}.webp`;
  // backgrounds: only material you import — here, single frames from the screen recordings and cartoon clips (no bundled images)
  const BG = ['../media/web/f_00150.jpg', '../media/fly/f_00100.jpg', '../media/wb/f_01200.jpg', '../media/egg/f_00060.jpg', '../media/sent/f_00800.jpg'];
  const PL = i => BG[i - 1];
  const SW = [[0, 'flash'], [.9, 'whip'], [1.9, 'zoom'], [2.9, 'glitch'], [3.4, 'iris'], [3.87, 'push']];
  const FOOT = 3.87, MORPH = 4.3, HOP = 7.73, CARD = 12.07;
  // footage per line: [start, folder, frames, label]
  const CLIPS = [[3.87, 'web', 451, 'CINEMATIC'], [4.73, 'fly', 286, 'FUTURISTIC TECH'], [5.87, 'sent', 2088, 'SOCIAL MEDIA'], [6.6, 'whis', 403, 'MINIMALIST'], [7.73, 'wb', 3327, '']];
  const FACE = [.51 * 1920, .25 * 1080];
  const BL = [250, 800, 190], TL = [250, 290, 190], BL2 = [270, 800, 210];

  C.scene({ t0: 0, t1: C.end + .05, bg: '#000', quiet: true, build(L) {
      const st = { L: [] };
      SW.forEach(([t0, ty], i) => {
        const w = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', overflow: 'hidden', zIndex: 2 + i });
        const im = el(w, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', transformOrigin: '50% 50%' });
        if (i < 5) C.setSrc(im, PL(i + 1));
        let sl = null; if (ty === 'glitch') { w.style.overflow = 'visible'; sl = [];
          for (let j = 0; j < 8; j++) { const s = el(w, 'div', 'abs', { left: 0, top: (j * 135) + 'px', width: '1920px', height: '135px', overflow: 'hidden' }); const si = el(s, 'img', 'abs', { left: 0, top: (-j * 135) + 'px', width: '1920px', height: '1080px', objectFit: 'cover' }); C.setSrc(si, PL(i + 1)); sl.push(s); } im.style.display = 'none'; }
        st.L.push({ w, im, t0, ty, sl, i });
      });
      st.flash = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', background: '#fff', zIndex: 20, opacity: 0 });
      st.dim = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 12, background: 'linear-gradient(90deg, rgba(3,8,30,.92) 0%, rgba(3,8,30,.78) 45%, rgba(3,8,30,.66) 75%, rgba(3,8,30,.55))', opacity: 0 });

      // intro lines over the backgrounds (left of the face)
      const lab = (txt, y, size, col) => el(L, 'div', 'abs', { left: '90px', top: y + 'px', zIndex: 35, fontFamily: BIG, fontWeight: 900, fontStyle: 'italic', fontSize: size + 'px', color: col || '#fff', whiteSpace: 'nowrap', transform: 'skewX(-6deg)', textShadow: '0 4px 0 rgba(0,0,0,.45), 0 0 24px rgba(0,0,0,.55)' }, txt);
      st.sh = el(L, 'div', 'abs', { left: 0, top: 0, width: '1200px', height: '520px', zIndex: 34, background: 'radial-gradient(120% 100% at 0% 0%, rgba(3,8,30,.82), rgba(3,8,30,.5) 55%, rgba(3,8,30,0) 80%)' });
      st.i1 = lab("HI, I'M EVA", 120, 96); st.i2 = lab('EVA VIDEO STYLE', 230, 84, CYAN); st.i3 = lab('OPEN-SOURCE · AI VIDEO EDITING', 340, 48, LIME);
      // footage label chip (top-right) + step chips
      st.chip = el(L, 'div', 'abs', { right: '70px', top: '60px', zIndex: 35, padding: '10px 30px', fontFamily: BIG, fontWeight: 900, fontSize: '46px', color: '#04121f', background: CYAN, boxShadow: '0 0 30px rgba(46,230,255,.6)', transform: 'skewX(-8deg)', transformOrigin: '100% 50%' }, '');
      st.steps = ['① PICK YOUR FAVORITE', '② APPLY IT TO YOUR FOOTAGE', '③ LET AI DO THE EDITING'].map((s, i) => el(L, 'div', 'abs', { right: '70px', top: (170 + i * 86) + 'px', zIndex: 35, padding: '8px 26px', fontFamily: BIG, fontWeight: 900, fontSize: '40px', color: '#fff', background: i === 2 ? 'rgba(10,40,10,.85)' : 'rgba(5,20,60,.85)', border: `3px solid ${i === 2 ? LIME : CYAN}`, transform: 'skewX(-8deg)', transformOrigin: '100% 50%' }, s));
      st.tpl = el(L, 'div', 'abs', { left: '470px', top: '60px', zIndex: 35, fontFamily: BIG, fontWeight: 900, fontStyle: 'italic', fontSize: '56px', color: '#fff', background: 'rgba(5,20,60,.88)', padding: '6px 26px', textShadow: '0 0 20px rgba(46,230,255,.6)' }, 'READY-TO-USE TEMPLATES');

      // presenter rig: cut-out that shrinks into a circle
      st.rig = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 30, overflow: 'hidden' });
      st.inner = el(st.rig, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', transformOrigin: '0 0' });
      st.pb = el(st.inner, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', objectFit: 'cover', filter: 'blur(14px) brightness(1.05)', opacity: 0 }); C.setSrc(st.pb, PL(1));
      st.cut = el(st.inner, 'img', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px' });
      st.ring = el(L, 'div', 'abs', { left: 0, top: 0, borderRadius: '50%', zIndex: 31, boxSizing: 'border-box', border: '8px solid #fff', opacity: 0 });

      // end card
      st.card = el(L, 'div', 'abs', { left: 0, top: 0, width: '1920px', height: '1080px', zIndex: 25 });
      const hs = (txt, x, y, size, grad, glow) => el(st.card, 'div', 'abs', { left: x + 'px', top: y + 'px', fontFamily: BIG, fontWeight: 900, fontStyle: 'italic', fontSize: size + 'px', lineHeight: 1, letterSpacing: '-2px', whiteSpace: 'nowrap', transformOrigin: '0 50%',
        color: grad ? 'transparent' : '#fff', backgroundImage: grad || 'none', WebkitBackgroundClip: grad ? 'text' : 'border-box', backgroundClip: grad ? 'text' : 'border-box', filter: `drop-shadow(0 0 ${glow || 14}px rgba(46,230,255,.75)) drop-shadow(0 6px 0 rgba(0,0,0,.45))` }, txt);
      st.h1 = hs('Less time editing,', 110, 70, 88); st.h2 = hs('MORE CREATING', 100, 170, 160, 'linear-gradient(180deg, #ffffff 0%, #bff6ff 35%, #2ee6ff 70%, #1a8cff 100%)', 22); st.h3 = hs('EVA VIDEO STYLE', 104, 350, 110, 'linear-gradient(180deg, #ffffff, #d7dde6 60%, #9aa6b8)', 10);
      st.bn = el(st.card, 'div', 'abs', { left: '150px', top: '500px', padding: '12px 34px', fontFamily: BIG, fontSize: '48px', fontWeight: 900, color: LIME, border: `3px solid ${LIME}`, background: 'rgba(10,40,10,.55)', boxShadow: `0 0 26px rgba(125,255,58,.6), inset 0 0 18px rgba(125,255,58,.25)`, transform: 'rotate(-4deg)', transformOrigin: '0 50%' }, 'TRY IT TODAY →');
      st.wm = el(st.card, 'div', 'abs mono', { right: '70px', top: '60px', fontSize: '28px', letterSpacing: '.3em', color: '#fff' }, 'GITHUB.COM/ROVEREVA');
      const s = k.svg(st.card, 560, 330, 1230, 300); st.bp = [];
      ['M60 250 L500 250 L540 300 L20 300 Z', 'M110 40 L450 40 L450 245 L110 245 Z', 'M140 70 L420 70 L420 215 L140 215 Z', 'M180 110 L300 110 M180 140 L380 140 M180 170 L340 170', 'M230 275 L330 275'].forEach(d => { const p = k.sv(s, 'path', { d, fill: 'none', stroke: 'rgba(120,200,255,.85)', 'stroke-width': 2.5, 'stroke-linejoin': 'round' }); const l = p.getTotalLength ? p.getTotalLength() || 1400 : 1400; p.setAttribute('stroke-dasharray', l); p.setAttribute('stroke-dashoffset', l); p.l = l; st.bp.push(p); });
      st.tags = ['OPEN SOURCE', '20 TEMPLATES', 'EN / CN + EN CAPTIONS', 'MIT LICENSE'].map((tx, i) => { const d = el(st.card, 'div', 'abs', { left: (620 + i * 22) + 'px', top: (650 + i * 74) + 'px', padding: '6px 24px', fontFamily: BIG, fontWeight: 800, fontSize: '36px', color: '#fff', border: '2px solid rgba(46,230,255,.8)', background: 'rgba(5,20,60,.75)', boxShadow: '0 0 16px rgba(46,230,255,.35)', transform: 'skewX(-8deg)', transformOrigin: '0 50%' }, tx);
        el(d, 'div', 'abs', { left: '-36px', top: '24px', width: '30px', height: '2px', background: 'rgba(46,230,255,.8)' }); return d; });

      SW.forEach(([t0, ty], i) => k.sfx(i === 5 ? 'whoosh' : (i % 2 ? 'whoosh' : 'click'), t0 + .02, i === 5 ? .14 : .09));
      k.sfx('impact', FOOT + .4, .14); k.sfx('pop', MORPH + .55, .14); CLIPS.slice(1).forEach(c => k.sfx('whoosh', c[0], .08)); [5.9, 6.6].forEach(x => k.sfx('pop', x + .05, .1));
      k.sfx('pop', HOP + .45, .1, { f: 1100 }); [8.97, 9.87, 10.67].forEach((x, i) => k.sfx('pop', x, .1, { f: 900 + i * 140 }));
      k.sfx('riser', CARD - .6, .07, { d: .6 }); k.sfx('impact', CARD + .05, .18); k.sfx('pop', 12.9, .12); k.sfx('ding', 13.8, .07); st.tags.forEach((_, i) => k.sfx('click', 14.0 + i * .2, .08));
      return st; },

    update(lt, st, t) {
      // backgrounds
      st.L.forEach((Ly, i) => { const nx = SW[i + 1] ? SW[i + 1][0] : 99, u = P(t, Ly.t0, Ly.ty === 'push' ? .45 : .28), e = ease.outExpo(u), life = t - Ly.t0;
        Ly.w.style.display = t >= Ly.t0 && t < nx + .5 ? '' : 'none'; if (Ly.w.style.display) return;
        let cu = 0; if (Ly.i === 5) { const c = CLIPS.reduce((m, x) => t >= x[0] ? x : m, CLIPS[0]); cu = P(t, c[0], .3); C.setSrc(Ly.im, C.seq('../media/' + c[1], Math.max(0, t - c[0]) * 1.15 + 1, c[2])); }
        const kb = Ly.i < 5 ? 1.12 - .08 * clamp(life / .9) : 1.0 + .06 * (1 - ease.outExpo(cu));
        let x = Ly.i < 5 ? (Ly.i % 2 ? -1 : 1) * 30 * clamp(life / .9) : 0, s = kb, blur = 0, clip = 'none';
        if (Ly.ty === 'whip') { x += 1920 * (1 - e); blur = 30 * (1 - e); }
        if (Ly.ty === 'zoom') { s *= 1 + .35 * (1 - e); }
        if (Ly.ty === 'iris') clip = `circle(${(1 - Math.pow(1 - u, 3)) * 1250}px at ${FACE[0]}px ${FACE[1]}px)`;
        if (Ly.ty === 'push') { x = 1920 * (1 - e); blur = 18 * (1 - e); }
        Ly.w.style.clipPath = clip; tf(Ly.im, { x, s }); Ly.im.style.filter = blur ? `blur(${blur}px)` : 'none';
        if (Ly.sl) Ly.sl.forEach((sl, j) => { const off = (1 - e) * ((j * 7919) % 11 - 5) * 120; tf(sl, { x: off }); sl.firstChild.style.transform = `scale(${s})`; sl.firstChild.style.transformOrigin = `960px ${540 + j * 135}px`; });
        const nxt = st.L[i + 1]; if (nxt && t >= nxt.t0 && (nxt.ty === 'push' || nxt.ty === 'whip')) { const ue = ease.outExpo(P(t, nxt.t0, nxt.ty === 'push' ? .45 : .28)); tf(Ly.im, { x: x - (nxt.ty === 'push' ? 700 : 1920) * ue, s }); Ly.im.style.filter = `blur(${20 * ue}px)`; } });
      const fl = SW.reduce((m, [t0, ty]) => Math.max(m, (ty === 'flash' || ty === 'zoom' ? .85 : ty === 'glitch' ? .35 : 0) * (1 - P(t, t0, .18)) * (t >= t0 ? 1 : 0)), 0);
      const fc = CLIPS.slice(1, 4).reduce((m, c) => Math.max(m, t >= c[0] ? .5 * (1 - P(t, c[0], .15)) : 0), 0);
      st.flash.style.opacity = Math.max(fl, fc);

      // intro lines
      st.sh.style.display = t < FOOT ? '' : 'none'; st.sh.style.opacity = P(t, .05, .3);
      [st.i1, st.i2, st.i3].forEach((e, i) => { e.style.display = t < FOOT ? '' : 'none'; tf(e, slide(t, [.1, .9, 1.9][i], .35, -120, 0)); e.style.transform += ' skewX(-6deg)'; });
      const c = CLIPS.reduce((m, x) => t >= x[0] ? x : m, CLIPS[0]); st.chip.textContent = c[3]; st.chip.style.display = t >= FOOT && t < HOP ? '' : 'none';
      const cp = pop(t, c[0] + .05, .3, 2); tf(st.chip, { s: cp.s, o: cp.o }); st.chip.style.transform += ' skewX(-8deg)';
      st.steps.forEach((e, i) => { e.style.display = t >= HOP && t < CARD ? '' : 'none'; tf(e, slide(t, [8.97, 9.87, 10.67][i], .35, 140, 0)); e.style.transform += ' skewX(-8deg)'; });
      st.tpl.style.display = t >= HOP && t < CARD ? '' : 'none'; tf(st.tpl, slide(t, HOP + .4, .4, 0, -40)); st.tpl.style.top = '60px';

      // presenter rig
      C.setSrc(st.cut, CUT(t));
      const m = ease.io3(P(t, MORPH, .6));
      let [cx, cy, r] = BL; const hp = ease.outBack(P(t, HOP, .5), 1.4);
      if (t >= HOP) { cx = lerp(BL[0], TL[0], hp); cy = lerp(BL[1], TL[1], hp) - 50 * Math.sin(Math.PI * clamp(P(t, HOP, .5))); r = BL[2]; }
      const bk = ease.outBack(P(t, CARD - .25, .5), 1.3); if (t >= CARD - .25) { cx = lerp(TL[0], BL2[0], bk); cy = lerp(TL[1], BL2[1], bk); r = lerp(TL[2], BL2[2], bk); }
      const R = lerp(1500, r, m), CX = lerp(FACE[0], cx, m), CY = lerp(FACE[1], cy - .12 * r, m), S = lerp(1, (r * 2 * .5) / 460, m);
      st.rig.style.clipPath = m > 0 ? `circle(${R}px at ${CX}px ${CY + .12 * r * m}px)` : 'none';
      st.inner.style.transform = `translate(${CX - S * FACE[0]}px, ${CY - S * FACE[1]}px) scale(${S})`;
      st.pb.style.opacity = clamp((m - .6) / .4);
      const rc = CY + .12 * r * m, ring = P(t, MORPH + .35, .25), card = P(t, CARD, .4);
      Object.assign(st.ring.style, { left: (CX - R) + 'px', top: (rc - R) + 'px', width: 2 * R + 'px', height: 2 * R + 'px', opacity: ring,
        borderColor: card > .5 ? CYAN : '#fff', boxShadow: card > .5 ? `0 0 ${30 + 10 * Math.sin(t * 5)}px rgba(46,230,255,.85), inset 0 0 20px rgba(46,230,255,.4)` : '0 12px 40px rgba(0,0,0,.45)' });
      st.ring.style.transform = m > 0 && m < 1 ? `scale(${1 + .06 * Math.sin(Math.PI * m)})` : '';

      // end card
      st.dim.style.opacity = card; st.card.style.display = t >= CARD - .05 ? '' : 'none';
      tf(st.h1, slide(t, CARD + .05, .4, -120, 0)); st.h1.style.transform += ' skewX(-6deg)';
      const h2 = pop(t, 12.9, .45, 1.6); tf(st.h2, { s: h2.s, o: h2.o }); st.h2.style.transform += ' skewX(-6deg)';
      tf(st.h3, slide(t, 13.77, .4, -160, 0)); st.h3.style.transform += ' skewX(-6deg)';
      const b = pop(t, 13.95, .4, 1.8); tf(st.bn, { s: b.s, o: b.o, r: -4 });
      st.wm.style.opacity = P(t, 14.0, .4);
      st.bp.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.l * (1 - ease.out3(P(t, CARD + .3 + i * .15, .9)))));
      st.tags.forEach((d, i) => { tf(d, slide(t, 14.0 + i * .2, .35, 120, 0)); d.style.transform += ' skewX(-8deg)'; });
    } });
})();
