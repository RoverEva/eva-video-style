/* T75 Crayon Kids 童趣蜡笔 · 10 s sample (illustrative copy). Wobbly crayon strokes (SVG displacement), bouncy multicolour letters, doodles. */
(function () { const C = EV, M = K.T.mo, f = M.f, COL = ['#ff5a5f', '#ffb400', '#3ec300', '#1fa2ff', '#a35bff'];
  const filt = `<defs><filter id="cr"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="5"/></filter></defs>`;
  const doodle = (p, x, y, w, h, d, c, sw) => M.svg(p, x, y, w, h, filt + `<path d="${d}" fill="none" stroke="${c}" stroke-width="${sw || 10}" stroke-linecap="round" stroke-linejoin="round" filter="url(#cr)" pathLength="1" stroke-dasharray="1 1"/>`).querySelector('path');
  M.setup({ bg: '#fff8dc', win: { x: 1270, y: 160, w: 490, h: 490, r: 245, o: 1, s: 1.15 }, ring: () => ({ color: '#1fa2ff', width: 12, shadow: .2 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['今天画什么呢？', 'What shall we draw today?'], ['太阳、房子，还有花', 'A sun, a house and a flower'], ['画得真棒！', 'Great job!']]),
    build(L) { const s = {};
      s.ch = [...'我的画画日记'].map((c, i) => M.txt(L, 110 + i * 100, 90, f(900, 96, M.CN), COL[i % 5], c, { transformOrigin: '50% 100%', textShadow: '3px 3px 0 rgba(0,0,0,.08)' }));
      s.sun = doodle(L, 110, 300, 240, 240, 'M120 70 a50 50 0 1 0 0.1 0 M120 10 V40 M120 200 V230 M10 120 H40 M200 120 H230 M42 42 L62 62 M178 178 L198 198 M42 198 L62 178 M178 62 L198 42', '#ffb400');
      s.house = doodle(L, 420, 320, 260, 260, 'M30 120 L130 30 L230 120 M50 110 V240 H210 V110 M110 240 V170 H150 V240', '#ff5a5f');
      s.flower = doodle(L, 740, 330, 220, 260, 'M110 250 V120 M110 180 Q 60 160 50 120 M110 120 a30 30 0 1 0 0.1 0 M110 60 a26 26 0 1 1 0.1 0 M60 110 a26 26 0 1 1 0.1 0 M160 110 a26 26 0 1 1 0.1 0', '#3ec300');
      s.stars = [[140, 640], [300, 680], [460, 630]].map(([x, y], i) => doodle(L, x, y, 110, 110, 'M55 6 L68 40 L104 42 L76 64 L86 100 L55 80 L24 100 L34 64 L6 42 L42 40Z', COL[i + 2], 8));
      s.gj = M.txt(L, 620, 650, f(400, 90, M.AN), '#ff5a5f', 'Good job!', { transformOrigin: '50% 50%' });
      return s; },
    update(s, t) { s.ch.forEach((e, i) => { const a = .85 + i * .1; M.pop(e, t, a, 9.2, { from: .2 }); e.style.transform += ` translateY(${(-10 * Math.max(0, Math.sin((t - a) * 4 + i))).toFixed(1)}px) rotate(${(4 * Math.sin(t * 2 + i)).toFixed(1)}deg)`; });
      M.draw(s.sun, t, 3.5, .8, 9.2); M.draw(s.house, t, 4.2, .9, 9.2); M.draw(s.flower, t, 5.0, .9, 9.2);
      s.stars.forEach((p, i) => M.draw(p, t, 6.75 + i * .2, .4, 9.2)); M.pop(s.gj, t, 7.3, 9.2, { from: .3 }); s.gj.style.transform += ` rotate(${(3 * Math.sin(t * 5)).toFixed(1)}deg)`; } });
})();
