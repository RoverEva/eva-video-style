/* T34 Finance Ticker 财经快讯 · 10 s concept sample (16:9). Silent; ALL numbers are illustrative sample data (labelled on screen). */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", GOLD = '#f2c14e', UP = '#2fd17a', DN = '#ff5a5f';
  M.setup({
    bg: 'linear-gradient(180deg, #0a1730, #0d2148)',
    win: { x: 1250, y: 170, w: 540, h: 540, r: 30, o: 1, s: 1.15 },
    ring: () => ({ color: GOLD, width: 5, shadow: .45 }),
    port: { box: [0, 100, 1180, 740] },
    captions: [{ t0: .5, t1: 3.4, cn: '本周数据，一分钟看懂', en: "This week's numbers in a minute" },
               { t0: 3.5, t1: 6.6, cn: '增长来自三个方向', en: 'Growth came from three places' },
               { t0: 6.7, t1: 9.7, cn: '关注我，每周更新', en: 'Follow for weekly updates' }],
    build(L) { const s = {};
      s.band = M.box(L, 0, 0, { width: C.W + 'px', height: '64px', background: '#06101f', borderBottom: `2px solid ${GOLD}`, overflow: 'hidden' }); M.bg(s.band);
      s.tape = el(s.band, 'div', 'abs', { left: 0, top: '14px', whiteSpace: 'nowrap', font: `700 28px 'Space Mono', monospace`, color: '#cfd8ea' });
      const it = [['ALPHA', '+2.4%', UP], ['BETA', '-0.8%', DN], ['GAMMA', '+1.1%', UP], ['DELTA', '+3.6%', UP], ['OMEGA', '-1.2%', DN]];
      s.tape.innerHTML = Array(4).fill(it.map(([n, v, c]) => `${n} <span style="color:${c}">${v}</span>`).join(' &nbsp;·&nbsp; ')).join(' &nbsp;·&nbsp; ');
      s.tag = M.box(L, 110, 110, { font: `700 22px Inter, sans-serif`, color: '#0a1730', background: GOLD, padding: '6px 14px', borderRadius: '4px', letterSpacing: '.06em' }, '示例数据 SAMPLE DATA');
      s.label = M.box(L, 110, 170, { font: `700 40px ${CN}`, color: '#cfd8ea' }, '本周增长 · Weekly growth');
      s.num = M.box(L, 104, 220, { font: `400 230px Anton, sans-serif`, color: '#ffffff', lineHeight: 1 }, '0.0%');
      s.yoy = M.box(L, 740, 330, { font: `700 44px Inter, sans-serif`, color: UP }, '▲ +4.2 YoY');
      const H = [60, 90, 75, 120, 105, 150, 140, 190], O = [40, 70, 60, 95, 85, 120, 118, 160];
      s.cs = M.svg(L, 120, 470, 900, 280, H.map((h, i) => { const x = 30 + i * 108, up = i % 3 !== 2, y = 260 - Math.max(h, O[i]);
        return `<g class="c"><line x1="${x + 22}" x2="${x + 22}" y1="${y - 20}" y2="${260 - Math.min(h, O[i]) + 18}" stroke="${up ? UP : DN}" stroke-width="3"/><rect x="${x}" y="${y}" width="44" height="${Math.abs(h - O[i]) + 10}" fill="${up ? UP : DN}" rx="3"/></g>`; }).join('') +
        `<path class="tr" d="M50 230 L160 200 L270 210 L380 160 L490 175 L600 120 L710 128 L820 80" fill="none" stroke="${GOLD}" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>`);
      s.cg = [...s.cs.querySelectorAll('.c')]; s.tr = s.cs.querySelector('.tr');
      s.lower = M.box(L, 0, 760, { width: '1180px', height: '78px', background: '#c8102e', display: 'flex', alignItems: 'center', gap: '22px', paddingLeft: '110px', boxSizing: 'border-box' });
      el(s.lower, 'div', '', { font: `400 40px Anton, sans-serif`, color: '#fff', letterSpacing: '.06em' }, 'BREAKING');
      el(s.lower, 'div', '', { font: `700 36px ${CN}`, color: '#fff' }, '三大板块同时走强（示例）');
      return s; },
    update(s, t) {
      s.tape.style.transform = `translateX(${(-t * 120).toFixed(1)}px)`;
      M.slide(s.band, t, .7, 9.2, { dx: 0, dy: -64 });
      M.pop(s.tag, t, .85, 9.2, { from: .6 }); M.rise(s.label, t, 1.0, 9.2);
      M.hero(s.num, t, 1.15, 9.2, { dx: -40 }); M.count(s.num, 12.8, t, 1.15, 1.4, v => v + '%');
      M.rise(s.yoy, t, 2.4, 9.2, { dy: 20 });
      s.cg.forEach((g, i) => { const u = M.os((t - (3.6 + i * .1)) / .3); g.style.transformOrigin = '0 260px'; g.style.transformBox = 'view-box'; g.style.transform = `scaleY(${Math.max(0, u).toFixed(4)})`; g.style.opacity = (u > 0 ? 1 : 0) * (1 - M.i2((t - 8.97) / .23)); });
      M.draw(s.tr, t, 4.5, .9, 9.2);
      M.panel(s.lower, t, 6.8, 9.2, { din: .45 });
    }
  });
})();
