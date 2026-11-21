/* T60 Workout Timer 健身计时 · 10 s sample (illustrative copy). Ring timer (sped-up, labelled), rounds, DONE burst. */
(function () { const C = EV, M = K.T.mo, f = M.f, LM = '#c6ff3d';
  M.setup({ bg: '#0f0f12', win: { x: 1260, y: 150, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: LM, width: 6, glow: 'rgba(198,255,61,.45)', shadow: .5 }), port: { box: [90, 40, 1060, 780] },
    captions: M.caps([['跟我一起：30 秒平板支撑', 'With me: a 30-second plank'], ['保持呼吸，核心收紧', 'Breathe, keep your core tight'], ['完成！明天继续', 'Done — again tomorrow']]),
    build(L) { const s = {};
      s.r = M.txt(L, 110, 70, f(700, 30, M.MONO), LM, 'ROUND 1 / 3'); s.t = M.txt(L, 110, 120, f(900, 92, M.CN), '#fff', '30 秒平板支撑'); s.e = M.txt(L, 114, 235, f(700, 36, M.INTER), '#9a9aa6', '30-second plank');
      s.ring = M.svg(L, 110, 310, 400, 400, `<circle cx="200" cy="200" r="170" fill="none" stroke="#24242b" stroke-width="28"/><circle class="p" cx="200" cy="200" r="170" fill="none" stroke="${LM}" stroke-width="28" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 200 200)"/>`); s.rp = s.ring.querySelector('.p');
      s.num = M.txt(L, 110, 440, f(400, 140, M.AN), '#fff', '30', { width: '400px', textAlign: 'center', lineHeight: 1 }); s.sp = M.txt(L, 230, 600, f(700, 22, M.INTER), '#9a9aa6', '示意 · sped up');
      s.tips = [['呼吸', 'Breathe'], ['收腹', 'Core'], ['别塌腰', 'Hips up']].map(([c, e], i) => M.txt(L, 580, 330 + i * 78, f(900, 50, M.CN), '#fff', `${c} · ${e}`));
      s.done = M.txt(L, 580, 610, f(400, 110, M.AN), '#0f0f12', 'DONE!', { background: LM, padding: '0 30px', transformOrigin: '50% 50%' });
      s.burst = M.svg(L, 560, 560, 420, 240, Array.from({ length: 10 }, (_, i) => { const a = i / 10 * Math.PI * 2; return `<path d="M${210 + Math.cos(a) * 140} ${120 + Math.sin(a) * 90} L${210 + Math.cos(a) * 200} ${120 + Math.sin(a) * 125}" stroke="${LM}" stroke-width="8" stroke-linecap="round"/>`; }).join(''), { transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { M.rise(s.r, t, .75, 9.2); M.hero(s.t, t, .95, 9.2); M.rise(s.e, t, 1.25, 9.2);
      M.pop(s.ring, t, 1.6, 9.2, { from: .6 }); M.rise(s.num, t, 1.8, 9.2, { dy: 20 }); M.rise(s.sp, t, 2.0, 9.2, { dy: 8 });
      const u = M.io((t - 3.5) / 3.0); s.rp.setAttribute('stroke-dashoffset', u.toFixed(4)); s.num.textContent = String(Math.ceil(30 * (1 - u))).padStart(2, '0');
      if (t > 3.5 && t < 6.6) s.num.style.transform = `scale(${(1 + .05 * Math.max(0, Math.sin((t - 3.5) * Math.PI * 2 * 1.6))).toFixed(3)})`;
      s.tips.forEach((e, i) => M.slide(e, t, 3.7 + i * .7, 9.2, { dx: 50 }));
      M.pop(s.done, t, 6.85, 9.2, { from: .4 }); M.pop(s.burst, t, 6.9, 7.9, { from: .5, dout: .5 }); } });
})();
