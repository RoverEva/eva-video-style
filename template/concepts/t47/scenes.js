/* T47 Film Strip 胶片放映 · 10 s sample (illustrative copy). 35mm strip of the presenter's own frames scrolls; one frame gets picked. */
(function () { const C = EV, M = K.T.mo, { el } = C, f = M.f, Y = '#ffcf3f';
  M.setup({ bg: '#121212', win: { x: 1250, y: 410, w: 540, h: 400, r: 20, o: 1, s: 1.1 }, ring: () => ({ color: '#f5f1e6', width: 8, shadow: .5 }), port: { box: [90, 40, 1100, 780] },
    captions: M.caps([['一条视频的幕后', 'Behind one video'], ['每一帧，都是挑出来的', 'Every frame is a choice'], ['完整版，下次见', 'Full cut next time']]),
    build(L) { const s = {};
      s.strip = M.box(L, 0, 50, { width: '3400px', height: '300px', background: '#1f1c19', backgroundImage: 'repeating-linear-gradient(90deg, #f1ead8 0 22px, transparent 22px 52px), repeating-linear-gradient(90deg, #f1ead8 0 22px, transparent 22px 52px)', backgroundSize: '100% 22px, 100% 22px', backgroundPosition: '0 14px, 0 264px', backgroundRepeat: 'no-repeat' });
      s.fr = Array.from({ length: 8 }, (_, i) => M.img(s.strip, 30 + i * 420, 52, 390, 196, 15 + i * 36, { filter: 'sepia(.25) contrast(1.05)' }));
      s.pick = el(s.strip, 'div', 'abs', { left: (30 + 3 * 420 - 8) + 'px', top: '44px', width: '406px', height: '212px', border: `6px solid ${Y}`, boxSizing: 'border-box', borderRadius: '6px' });
      s.pl = M.txt(s.strip, 30 + 3 * 420, 262, f(900, 30, M.CN), Y, '就选这一帧 · This one');
      s.t = M.txt(L, 110, 420, f(900, 100, M.CN), '#f5f1e6', '幕后花絮'); s.e = M.txt(L, 114, 545, f(700, 38, M.INTER), '#bdb6a6', 'Behind the scenes');
      s.tc = M.txt(L, 114, 620, f(700, 54, M.MONO), Y, '00:00:00:00');
      s.fin = M.txt(L, 110, 700, f(900, 56, M.CN), '#f5f1e6', '完整版 · 下次见'); s.fl = M.path(L, 110, 775, 470, 16, 'M2 8H460', Y, 5);
      return s; },
    update(s, t) { const scroll = t < 3.6 ? -t * 90 : t < 6.6 ? -324 - 240 * M.io((t - 3.6) / .8) : -564 - (t - 6.6) * 90;   /* glides, settles on the picked frame, glides on */
      s.strip.style.transform = `translateX(${scroll.toFixed(1)}px)`; s.strip.style.opacity = M.env(t, .5, 9.2, .4).a;
      M.pop(s.pick, t, 4.3, 6.75, { from: 1.15 }); M.rise(s.pl, t, 4.5, 6.75, { dy: 10 });
      M.hero(s.t, t, .95, 9.2); M.rise(s.e, t, 1.25, 9.2); M.rise(s.tc, t, 1.5, 9.2);
      const fr = Math.floor(Math.max(0, t) * 24); s.tc.textContent = `00:00:${String(Math.floor(fr / 24)).padStart(2, '0')}:${String(fr % 24).padStart(2, '0')}`;
      M.hero(s.fin, t, 6.9, 9.2); M.draw(s.fl, t, 7.2, .5, 9.2); } });
})();
