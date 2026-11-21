/* T73 Highlighter 荧光笔标注 · 10 s sample (illustrative copy). A paragraph; highlighter sweeps line by line; margin note + star. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#26241f', HY = 'rgba(255,233,0,.75)', HP = 'rgba(255,120,180,.55)';
  const LN = [['好的开头，第一句就告诉观众：', HY, 1.5], ['你能得到什么，', HY, 3.6], ['为什么现在就要看。', HP, 4.4]];
  M.setup({ bg: '#fbfaf5', win: { x: 1280, y: 160, w: 480, h: 480, r: 240, o: 1, s: 1.15 }, ring: () => ({ color: '#e9e6dc', width: 12, shadow: .2 }), port: { box: [90, 40, 1080, 780] },
    captions: M.caps([['划重点', 'Key point'], ['告诉观众能得到什么', 'Say what viewers will get'], ['再告诉他们，为什么是现在', 'And why it matters now']]),
    build(L) { const s = {};
      s.tag = M.txt(L, 110, 80, f(700, 28, M.MONO), '#a79f8a', 'NOTES · 划重点');
      s.ln = LN.map(([txt, col], i) => { const e = M.txt(L, 110, 150 + i * 120, f(900, 72, M.SERIF), INK, txt, { padding: '0 6px', backgroundImage: `linear-gradient(${col}, ${col})`, backgroundRepeat: 'no-repeat', backgroundPosition: '0 70%', backgroundSize: '0% 45%' }); return e; });
      s.en = M.txt(L, 116, 520, f('italic 700', 32, M.PF), '#7d7663', 'Say what they get — and why now.');
      s.note = M.txt(L, 640, 610, f(900, 46, M.CN), '#e0353a', '← 这句最重要！', { transform: 'rotate(-4deg)' });
      s.star = M.path(L, 540, 590, 90, 90, 'M45 4 L56 34 L88 36 L62 56 L72 86 L45 68 L18 86 L28 56 L2 36 L34 34Z', '#e0353a', 5);
      s.circ = M.path(L, 90, 360, 640, 140, 'M330 10 C 600 6, 640 60, 600 100 C 540 140, 120 140, 40 100 C -10 70, 30 10, 340 14', '#e0353a', 5);
      return s; },
    update(s, t) { M.rise(s.tag, t, .75, 9.2, { dy: 10 });
      s.ln.forEach((e, i) => { M.rise(e, t, .9 + i * .14, 9.2, { dy: 16 }); e.style.backgroundSize = `${(100 * M.io((t - LN[i][2]) / .6)).toFixed(1)}% 45%`; });
      M.rise(s.en, t, 1.4, 9.2); M.draw(s.circ, t, 6.8, .6, 9.2); M.draw(s.star, t, 7.3, .5, 9.2); M.hero(s.note, t, 7.5, 9.2, { base: 'rotate(-4deg)' }); } });
})();
