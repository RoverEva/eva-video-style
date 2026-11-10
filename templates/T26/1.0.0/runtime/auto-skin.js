/* T26 Vintage Story automatic-edit skin (Core runtime). Needs runtime/lib.js (the T26 library, loaded first) and the AI
 * cut-out of the presenter in ../media/cut (Core runs scripts/matte.py when a template declares "presenter-cutout").
 * The skin owns its presenter (Core's presenter window is hidden in T26 sections) and its cards: each planner card becomes a
 * T26 layout with verbatim transcript text (hero → 01 giant title / 03 story card, statement → 05 newspaper statement);
 * between cards the collage with the presenter (layout 0) stays on. The presenter keeps the footage's own scale. */
(function (root) {
  const C = EV, T = K.T; /* templates carry no sound: SFX are designed per video */
  root.EVA_TEMPLATE_SKINS = root.EVA_TEMPLATE_SKINS || {};
  const pad = v => String(v).padStart(5, '0');
  const media = () => { const PL = root.EVA_PLAN || {}, n = Math.max(1, Math.round((PL.end || 1) * 30)), f = t => Math.max(0, Math.min(n - 1, Math.round(t * 30)));
    return { frame: t => `${C.evaDir}/f_${pad(f(t))}.jpg`, cut: t => `../media/cut/f_${pad(f(t))}.webp` }; };
  const split = s => { const w = String(s || '').trim().split(/\s+/); if (w.length < 4) return [w.join(' '), null]; const h = Math.ceil(w.length / 2); return [w.slice(0, h).join(' '), w.slice(h).join(' ')]; };
  root.EVA_TEMPLATE_SKINS.T26 = {
    win: { x: 0, y: 0, w: 1920, h: 1080, r: 0, s: 1 }, side: 'left', theme: 't26', presenter: 'own', ownsCards: true, portrait: 'native',
    ring: () => ({ color: 'transparent', width: 0, shadow: 0 }), bg: T.VT.BASE,
    build: (L, i, cards) => { const m = media(); let hero = 0;
      const st = { m, base: T.vtLayout(0, L, { auto: true }, m), items: (cards || []).map(c => {
        const ct = (c.spec && c.spec.content) || {}, title = (ct.words || [])[0], sub = ct.sub;
        let n, w;
        if (c.kind === 'statement' && sub) { const [a, b] = split(sub); n = 5; w = { auto: true, a, b }; }
        else { n = hero++ % 2 ? 3 : 1; w = { auto: true, a: title || sub }; }
        const o = T.vtLayout(n, L, w, m); o.root.style.display = 'none';
        return { o, c }; }) };
      return st; },
    update: (st, t, lt) => { const t0 = t - lt; T.vtLayoutAt(st.base, t, t0, st.m, 4);
      st.items.forEach(({ o, c }) => { const on = t >= c.t_in - .02 && t < c.t_out + .3; o.root.style.display = on ? '' : 'none'; if (!on) return;
        const q = 1 - Math.pow(1 - Math.min(1, (t - c.t_in + .02) / .25), 3), out = C.P(t, c.t_out, .3);
        o.root.style.transform = `translateX(${(C.W * (1 - q) - C.W * out).toFixed(1)}px) rotate(${(3 * (1 - q)).toFixed(2)}deg)`;
        T.vtLayoutAt(o, t, c.t_in + .1, st.m, c.t_out - c.t_in); }); }
  };
})(window);
