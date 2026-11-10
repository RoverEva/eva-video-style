/* EVA Core data-driven automatic-edit runtime.
 * Template implementations arrive from independently installed packages through template-skins.js.
 */
(function () {
  const C = EV, { P } = C, k = K, EC = K.EC, PL = window.EVA_PLAN;
  if (!PL) throw new Error('EVA_PLAN missing (plan.js)');
  const SKINS = window.EVA_TEMPLATE_SKINS || {};
  const missing = [...new Set((PL.sections || []).map(s => s.template).filter(id => !SKINS[id]))];
  if (missing.length) throw new Error(`installed template runtime missing: ${missing.join(', ')}`);
  C.src0 = 0;
  C.end = PL.end;
  C.evaDir = PL.evaDir || '../media/eva';
  if (PL.face) C.face = PL.face;

  const FULL = { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 };
  window.EVA_AUTO_SKINS = SKINS;
  const secs = PL.sections;
  if (!secs || !secs.length) throw new Error('EVA_PLAN has no sections');
  const skinOf = i => SKINS[secs[i].template];
  const cards = PL.cards || [];
  const secAt = t => { for (let i = secs.length - 1; i >= 0; i--) if (t >= secs[i].t0) return i; return 0; };

  /* Presenter window: template window per section; full-bleed in long stretches without cards. */
  /* In portrait, start from the template window so portLayout can place the
     presenter below the card block. Long card-free gaps still switch to FULL. */
  const W0 = skinOf(0).win, GAP = C.portrait ? 1.0 : 3.2;
  const keys = [{ t: 0, d: 0, L: Object.assign({}, W0, { o: 0 }) }, { t: .05, d: .4, L: W0 }];
  secs.forEach((s, i) => {
    const sk = skinOf(i);
    if (i > 0 && !C.portrait) keys.push({ t: s.t0, d: .45, L: sk.win });
    const inSec = cards.filter(c => c.section === i).sort((a, b) => a.t_in - b.t_in);
    let free = s.t0 + (C.portrait ? 0 : .6);
    const gaps = [];
    inSec.forEach(c => { gaps.push([free, c.t_in]); free = c.t_out + .4; });
    gaps.push([free, s.t1]);
    gaps.forEach(([a, b]) => {
      if (b - a >= GAP) {
        keys.push({ t: a, d: .5, L: FULL });
        if (b < s.t1 - .05) keys.push({ t: b - .55, d: .45, L: sk.win });
      }
    });
  });
  /* Additive hooks for a template-owned presenter/card system. Templates that
     omit these fields retain the existing Core behavior. */
  const own = i => skinOf(i).presenter === 'own';
  if (secs.some((_, i) => own(i))) {
    secs.forEach((s, i) => {
      if (i > 0 && own(i) !== own(i - 1)) {
        keys.push({ t: s.t0, d: 0, L: own(i) ? Object.assign({}, FULL, { o: 0 }) : (C.portrait ? FULL : skinOf(i).win) });
      }
    });
    keys.sort((a, b) => a.t - b.t);
    keys.forEach(key => { if (own(secAt(key.t))) key.L = Object.assign({}, key.L, { o: 0 }); });
  }
  C.evaKeys = keys;
  C.ringFn = t => skinOf(secAt(t)).ring(t);

  /* One background scene per section. */
  secs.forEach((s, i) => {
    const sk = skinOf(i);
    C.scene({
      t0: s.t0,
      t1: i === secs.length - 1 ? C.end + .05 : s.t1,
      bg: sk.bg,
      cls: sk.cls,
      quiet: i === 0,
      build: L => sk.build(L, i, sk.ownsCards ? cards.filter(c => c.section === i) : undefined),
      update: (lt, st, t) => sk.update(st, t, lt)
    });
  });

  const cardScene = (t0, t1, only) => C.scene({
    t0, t1, z: 60, quiet: true,
    build(L) {
      return { list: cards.filter(c => (only == null || c.section === only) && !skinOf(c.section).ownsCards).map(c => {
        const sk = skinOf(c.section), g = EC.group(L, 0, 0, 1920, 1080, 15);
        const theme = EC.theme(sk.theme, sk.themeOver);
        const object = EC.fromSchema(g, [c.spec], theme, { toLocal: s => s, win: sk.win })[0];
        object.times.forEach((x, j) => k.sfx('pop', +x.toFixed(3), .09, { f: 760 + 120 * (j % 4) }));
        return { g, o: object, c };
      }) };
    },
    update(lt, state, t) {
      for (const item of state.list) {
        const start = item.c.t_in - .02, end = item.c.t_out + .35;
        const on = t >= start && t < end;
        item.g.style.display = on ? '' : 'none';
        if (!on) continue;
        item.g.style.opacity = (1 - P(t, item.c.t_out, .35)).toFixed(3);
        item.o.o.at(t, item.o.times);
      }
    }
  });
  if (!C.portrait) cardScene(0, C.end + .05, null);
  else {
    const n = secs.length, at = {}, boxOf = i => secs[i].box || [780, 90, 1070, 780];
    secs.forEach((s, i) => {
      cardScene(s.t0, i === n - 1 ? C.end + .05 : s.t1, i);
      at[n + i] = { box: boxOf(i), maxH: 600 };
    });
    const native = secs.map((_, i) => i).filter(i => skinOf(i).portrait === 'native');
    C.portLayout({ box: boxOf(0), maxH: 600, circle: 640,
      cover: secs.map((_, i) => i).filter(i => !native.includes(i)), keep: native, at });
  }
})();
