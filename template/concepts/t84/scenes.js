/* T84 Logo Line Draw 描边生成 · 10 s logo-only sample. Outline draws, wordmark wipes in, colour floods the mark, tagline types. */
(function () { const C = EV, M = K.T.mo, f = M.f, INK = '#141414', B = '#2f5bff';
  M.setup({ noface: true, bg: '#f6f6f3', port: { box: [360, 40, 1200, 780] },
    captions: M.caps([['一笔一画，画出品牌', 'Line by line, a brand takes shape'], ['简洁，就是记忆点', 'Simple is memorable'], ['EVA Video Studio', 'EVA Video Studio']]),
    build(L) { const s = {};
      s.guides = M.svg(L, 660, 60, 600, 600, `<g stroke="rgba(0,0,0,.08)" stroke-width="2"><path d="M0 300H600M300 0V600"/><circle cx="300" cy="300" r="240" fill="none"/></g>`);
      s.fill = M.box(L, 760, 160, { width: '400px', height: '400px', borderRadius: '96px', background: B, transformOrigin: '50% 50%' });
      s.logo = M.logo(L, 760, 160, 400, INK); s.lr = s.logo.querySelector('.lr'); s.lt = s.logo.querySelector('.lt');
      s.tag = M.txt(L, 0, 620, f(700, 44, M.MONO), INK, '', { width: '1920px', textAlign: 'center' });
      s.cn = M.txt(L, 0, 700, f(900, 48, M.CN), B, '简洁，就是记忆点', { width: '1920px', textAlign: 'center' });
      return s; },
    update(s, t) { M.rise(s.guides, t, .5, 10.3, { dy: 0 }); M.draw(s.lr, t, .7, 1.4, 10.3);
      const u = M.o5((t - 1.8) / .6); s.lt.style.clipPath = `inset(0 ${((1 - u) * 100).toFixed(1)}% 0 0)`; s.logo.style.opacity = 1 - M.i2((t - 10.1) / .25);
      const fl = M.os((t - 3.6) / .5); s.fill.style.opacity = t > 3.6 ? (1 - M.i2((t - 10.1) / .25)) : 0; s.fill.style.transform = `scale(${Math.max(0, fl).toFixed(3)})`;
      const white = t > 3.8; s.lr.setAttribute('stroke', white ? '#fff' : INK); s.lt.setAttribute('fill', white ? '#fff' : INK);
      M.type(s.tag, 'EVA VIDEO STUDIO', t, 4.3, .9, true); s.tag.style.opacity = t > 4.3 ? 1 - M.i2((t - 10.1) / .25) : 0; M.rise(s.cn, t, 6.8, 10.3); } });
})();
