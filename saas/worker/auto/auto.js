/* EVA Video Studio · data-driven section page (no hand-written scenes.js).
 *
 * Reads window.EVA_PLAN (written by saas/worker/planner.py) and composes EXISTING engine pieces only:
 *   - each template's stage (background, presenter window, ring) exactly as in template/cards/<t>/scenes.js,
 *   - EVA Card System cards from JSON specs (K.EC.fromSchema), timed on eva-asr word times,
 *   - the engine's presenter-window path, sound cues and automatic scene-change whoosh.
 * Templates, cards and the engine are not modified.
 *
 * EVA_PLAN = { end, face:{x,y,h}, evaDir, sections:[{t0,t1,template}], cards:[{spec, t_in, t_out, section}] }
 */
(function () {
  const C = EV, { el, tf, P, clamp } = C, k = K, T = K.T, EC = K.EC, PL = window.EVA_PLAN;
  if (!PL) throw new Error('EVA_PLAN missing (plan.js)');
  C.src0 = 0; C.end = PL.end; C.evaDir = PL.evaDir || '../media/eva'; if (PL.face) C.face = PL.face;

  const FULL = { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 };
  /* Stages: values copied from the Card System previews (template/cards/t17|t20|t01|t09/scenes.js) and the template demos. */
  const SKINS = {
    T17: { win: { x: 150, y: 300, w: 560, h: 560, r: 280, s: 1.5 }, side: 'right', theme: 't17',
      ring: () => ({ color: T.SCN.CYAN, width: 3, glow: 'rgba(24,224,242,.5)', shadow: .5 }), bg: T.sciNetBg,
      build: L => ({ bk: T.bokeh(L, 45, 13), r: T.ribbon(L, { y: 1050, amp: 50, width: 70, rows: 4 }) }),
      update: (st, t) => { T.bokehAt(st.bk, t); T.ribbonAt(st.r, t); } },
    T20: { win: { x: 130, y: 110, w: 600, h: 820, r: 52, s: 1.6 }, side: 'right', theme: 't20',
      ring: () => ({ color: '#fff', width: 10, shadow: .35 }), bg: '#ece6fb',
      build: L => ({ b: el(L, 'div', 'abs', { left: '440px', top: '640px', width: '520px', height: '380px', background: 'linear-gradient(135deg, #2fe0b4, #3aa0ff)',
        borderRadius: '48% 52% 44% 56% / 55% 45% 55% 45%', transform: 'rotate(-8deg)' }) }),
      update: () => {} },
    T01: { win: { x: 1240, y: 150, w: 600, h: 740, r: 36, s: 1.5 }, side: 'left', theme: 't01', cls: 'dotgrid',
      ring: () => ({ color: k.INK, width: 6, shadow: .22 }), bg: k.LIME,
      build: L => ({ rows: Array.from({ length: 7 }, (_, r) => k.disp(L, Array(8).fill(r % 2 ? 'EVA VIDEO STYLE' : 'AI EDITING').join(' · '), 'rgba(11,11,13,.08)', 104, -200, -30 + r * 150)) }),
      update: (st, t, lt) => st.rows.forEach((d, i) => tf(d, { x: (i % 2 ? -1 : 1) * (lt * 90) - 300, o: 1 })) },
    T09: { win: { x: 1290, y: 180, w: 520, h: 700, r: 0, s: 1.5 }, side: 'left', theme: 't09', cls: 'linegrid',
      ring: () => ({ width: 0, color: 'transparent', hud: 'rgba(255,255,255,.55)' }), bg: T.hudBg,
      build: L => ({ f: T.hudFrame(L, 'EVA · VIDEO STUDIO', 'T09') }),
      update: (st, t) => T.hudFrameAt(st.f, t) },
    /* launch set 2026-11: stage values copied from template/demo/t23|t21|t02/scenes.js (window = the demo's main card window) */
    T23: { win: { x: 1180, y: 160, w: 620, h: 760, r: 40, s: 1.5 }, side: 'left', theme: 't23',
      themeOver: { surf: ['#ffffff', '#fff8ef'], ink: T.CP.INK, mute: '#5b587a', acc: T.CP.PINK, head: T.CP.KEY, headW: 400, upper: true, cardHead: T.CP.KEY,
        type: T.CP.INK, typeMode: 'pop', popC: T.CP.YEL, numMode: 'chip', chip: [T.CP.PINK, '#fff'], sh: [29, 27, 58], shA: 1, line: T.CP.INK, motion: 'pop', dur: .45, heroRot: -3, r: 28 },
      ring: () => ({ color: '#fff', width: 10, shadow: .35 }), bg: T.cpBg,
      build: (L, i) => ({ sb: T.cpSplashBg(L, (i || 0) + 2), sp: T.cpSparkles(L, 16, (i || 0) + 5) }),
      update: (st, t, lt) => { T.cpSplashBgAt(st.sb, t); T.cpSparklesAt(st.sp, t, P(lt, 0, .3)); } },
    T21: { win: { x: 1240, y: 220, w: 520, h: 640, r: 0, s: 1.4 }, side: 'left', theme: 't21',
      themeOver: { surf: ['#f7f4ee', '#ece8e0'], ink: '#1c1b18', mute: '#6f6a61', acc: '#1c1b18', head: "'Playfair Display', 'Noto Serif CJK SC', serif", headW: 400, upper: false,
        cardHead: "'Playfair Display', 'Noto Serif CJK SC', serif", type: '#1c1b18', typeMode: 'pop', popC: 'rgba(0,0,0,0)', numMode: '3d', tint: [236, 232, 224],
        sh: [111, 106, 97], shA: .35, border: '1px solid #cbbfa9', line: '#cbbfa9', motion: 'fade-slide', dur: .9, bob: 0, heroRot: 0, r: 2 },
      ring: () => ({ color: '#cbbfa9', width: 2, shadow: 0 }), bg: '#ece8e0',
      build: L => { const sv = k.svg(L, 1920, 1080, 0, 0);
        return { v: el(L, 'div', 'abs', { left: '80px', top: '0px', width: '1px', height: '1080px', background: '#cbbfa9' }),
          c: k.sv(sv, 'circle', { cx: 1500, cy: 540, r: 420, fill: 'none', stroke: '#d8cfbf', 'stroke-width': 1.5, 'stroke-dasharray': '4 7' }) }; },
      update: (st, t) => st.c.setAttribute('transform', `rotate(${(t * 3).toFixed(2)} 1500 540)`) },
    T02: { win: { x: 1260, y: 200, w: 560, h: 680, r: 30, s: 1.5 }, side: 'left', theme: 't02', cls: 'linegrid',
      themeOver: { surf: ['#ffffff', '#eef1ff'], ink: k.INK, mute: '#4a4f6e', acc: k.BLUE, kick: k.BLUE, head: "'Anton', 'Archivo Black', 'Noto Sans CJK SC', sans-serif", headW: 400,
        upper: true, cardHead: "'Anton', 'Archivo Black', 'Noto Sans CJK SC', sans-serif", type: '#fff', typeMode: 'glow', glow: '212,255,46', numMode: 'chip', chip: [k.BLUE, '#fff'],
        sh: [7, 11, 46], shA: 1.4, line: k.LIME, motion: 'fade-slide', dur: .45, bob: 0, heroRot: 0, r: 26 },
      ring: () => ({ color: k.LIME, width: 6, glow: 'rgba(212,255,46,.4)' }), bg: `radial-gradient(1400px 900px at 40% 30%, #12206b, ${k.NAVY})`,
      build: () => ({}), update: () => {} },
  };
  /* Card boxes (beside the window, above the caption zone) are computed by planner.py (SKIN_BOX) and arrive in spec.position. */
  window.EVA_AUTO_SKINS = SKINS;

  const secs = PL.sections, skinOf = i => SKINS[secs[i].template] || SKINS.T17;
  const cards = PL.cards || [];

  /* presenter window: template window per section; full-bleed in long stretches without cards */
  /* 9:16: a talking head owns the phone screen, so the presenter is full-bleed whenever no card is up (gaps ≥ 1.2 s) */
  const W0 = C.portrait ? FULL : skinOf(0).win, GAP = C.portrait ? 1.0 : 3.2;
  const keys = [{ t: 0, d: 0, L: Object.assign({}, W0, { o: 0 }) }, { t: .05, d: .4, L: W0 }];
  secs.forEach((s, i) => {
    const sk = skinOf(i); if (i > 0 && !C.portrait) keys.push({ t: s.t0, d: .45, L: sk.win });
    const inSec = cards.filter(c => c.section === i).sort((a, b) => a.t_in - b.t_in);
    let free = s.t0 + (C.portrait ? 0 : .6); const gaps = [];
    inSec.forEach(c => { gaps.push([free, c.t_in]); free = c.t_out + .4; }); gaps.push([free, s.t1]);
    gaps.forEach(([a, b]) => { if (b - a >= GAP) { keys.push({ t: a, d: .5, L: FULL }); if (b < s.t1 - .05) keys.push({ t: b - .55, d: .45, L: sk.win }); } });
  });
  C.evaKeys = keys;
  const secAt = t => { for (let i = secs.length - 1; i >= 0; i--) if (t >= secs[i].t0) return i; return 0; };
  C.ringFn = t => skinOf(secAt(t)).ring(t);

  /* one background scene per section (engine adds a whoosh on every non-quiet scene change) */
  secs.forEach((s, i) => { const sk = skinOf(i);
    C.scene({ t0: s.t0, t1: i === secs.length - 1 ? C.end + .05 : s.t1, bg: sk.bg, cls: sk.cls, quiet: i === 0,
      build: L => sk.build(L, i), update: (lt, st, t) => sk.update(st, t, lt) }); });

  /* cards: each in its own full-frame group so it can leave on time.
     9:16 (?ar=9:16): one card scene per section, so EV.portLayout can scale each template's 16:9 card block into the top
     zone (backgrounds cover the frame, the presenter window is re-laid below the block, full-bleed stays full-bleed). */
  const cardScene = (t0, t1, only) => C.scene({ t0, t1, z: 60, quiet: true,
    build(L) {
      return { list: cards.filter(c => only == null || c.section === only).map(c => {
        const sk = skinOf(c.section), g = EC.group(L, 0, 0, 1920, 1080, 15), th = EC.theme(sk.theme, sk.themeOver);
        const o = EC.fromSchema(g, [c.spec], th, { toLocal: s => s, win: sk.win })[0];
        o.times.forEach((x, j) => k.sfx('pop', +x.toFixed(3), .09, { f: 760 + 120 * (j % 4) }));
        return { g, o, c };
      }) };
    },
    update(lt, st, t) {
      for (const it of st.list) {
        const a = it.c.t_in - .02, z = it.c.t_out + .35, on = t >= a && t < z;
        it.g.style.display = on ? '' : 'none'; if (!on) continue;
        it.g.style.opacity = (1 - P(t, it.c.t_out, .35)).toFixed(3);
        it.o.o.at(t, it.o.times);
      }
    } });
  if (!C.portrait) cardScene(0, C.end + .05, null);
  else {
    const n = secs.length, at = {}, boxOf = i => secs[i].box || [780, 90, 1070, 780];
    secs.forEach((s, i) => { cardScene(s.t0, i === n - 1 ? C.end + .05 : s.t1, i); at[n + i] = { box: boxOf(i), maxH: 600 }; });
    /* talking-head first: the card block gets the top ~600 px, the presenter the larger zone below it */
    C.portLayout({ box: boxOf(0), maxH: 600, circle: 640, cover: secs.map((_, i) => i), at });
  }
})();
