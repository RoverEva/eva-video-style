/* T97 Event Invite 活动邀请 · 10 s logo-only sample. Envelope flap opens, invite card rises; time/place are SAMPLE placeholders; RSVP pops. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, R = '#b8324a', GOLD = '#c9a25a', INK = '#2a1a1e';
  M.setup({ noface: true, bg: 'linear-gradient(160deg,#f7ece6,#ecd5cd)', port: { box: [360, 20, 1200, 800] },
    captions: M.caps([['你被邀请了', "You're invited"], ['时间、地点，都在这里（示例）', 'Time and place, all here (sample)'], ['等你来', 'Hope to see you']]),
    build(L) { const s = {};
      s.back = M.box(L, 610, 420, { width: '700px', height: '380px', background: '#c9455e', borderRadius: '10px' });
      s.card = M.box(L, 650, 440, { width: '620px', height: '560px', background: '#fffaf3', borderRadius: '12px', boxShadow: '0 10px 30px rgba(80,20,30,.25)', border: `3px solid ${GOLD}`, boxSizing: 'border-box', textAlign: 'center' });
      M.txt(s.card, 0, 40, f('italic 700', 40, M.PF), GOLD, "You're invited", { width: '620px' }); M.txt(s.card, 0, 100, f(900, 70, M.SERIF), INK, '诚挚邀请', { width: '620px' });
      s.fl = [['时间', '示例：周六 19:00', 'Sat 7 pm (sample)'], ['地点', '示例地点 · 一号厅', 'Sample venue, Hall 1']].map(([k, v, e], i) => { const g = M.box(s.card, 0, 220 + i * 110, { width: '620px' }); M.txt(g, 0, 0, f(700, 24, M.MONO), R, k, { width: '620px' }); M.txt(g, 0, 32, f(900, 40, M.CN), INK, v, { width: '620px' }); M.txt(g, 0, 82, f(600, 20, M.INTER), '#8a7a7a', e, { width: '620px' }); return g; });
      s.front = M.svg(L, 610, 560, 700, 240, `<path d="M0 0 L350 120 L700 0 V240 H0Z" fill="#d85a72"/><path d="M0 240 L300 100 M700 240 L400 100" stroke="rgba(0,0,0,.08)" stroke-width="3"/>`);
      s.flap = M.svg(L, 610, 420, 700, 200, `<path d="M0 0 H700 L350 190Z" fill="#c03c56"/>`, { transformOrigin: '50% 0' });
      s.seal = M.box(L, 920, 560, { width: '80px', height: '80px', borderRadius: '50%', background: GOLD, boxShadow: '0 4px 8px rgba(0,0,0,.2)', font: f(400, 26, M.AN), color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }, 'EVA');
      s.rsvp = M.txt(L, 830, 720, f(900, 46, M.CN), '#fff', 'RSVP · 我会来', { background: R, padding: '10px 30px', borderRadius: '999px', transformOrigin: '50% 50%', zIndex: 3 });
      return s; },
    update(s, t) { [s.back, s.front, s.flap].forEach(e => M.rise(e, t, .6, 10.3, { dy: 60 })); const sv = M.env(t, .6, 1.7, .3, .2); s.seal.style.opacity = sv.a; s.seal.style.transform = `scale(${(1 + .3 * sv.x).toFixed(3)})`;
      const op = M.io((t - 1.6) / .5); s.flap.style.transform += ` perspective(1200px) rotateX(${(180 * op).toFixed(1)}deg)`; s.flap.style.zIndex = op > .5 ? 0 : 2;
      const up = M.os((t - 2.0) / .8); s.card.style.opacity = t > 2.0 ? 1 : 0; s.card.style.transform = `translateY(${(-380 * Math.max(0, up)).toFixed(1)}px)`; s.card.style.zIndex = 1; s.front.style.zIndex = 2;
      s.fl.forEach((g, i) => M.rise(g, t, 3.6 + i * .3, 10.3, { dy: 16 })); M.pop(s.rsvp, t, 6.85, 10.3, { from: .4 }); if (t > 7.4) s.rsvp.style.transform += ` scale(${(1 + .04 * Math.sin((t - 7.4) * 6)).toFixed(3)})`; } });
})();
