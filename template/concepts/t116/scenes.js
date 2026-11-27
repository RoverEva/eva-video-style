/* T116 用药时间钟 Dose Clock (medical): a day dial with dose markers, hand sweeps, reminders pop; general info, sample schedule. */
(function () { const M = K.T.mo, X = M.X, TL = '#1aa39a', INK = '#183a37';
  const dial = (c, x, y, R) => { const g = M.svg(c, x - R - 20, y - R - 20, 2 * R + 40, 2 * R + 40, `<circle cx="${R + 20}" cy="${R + 20}" r="${R}" fill="#fff" stroke="#d6ebe8" stroke-width="16"/>` + Array.from({ length: 24 }, (_, i) => { const an = i / 24 * 6.2832 - 1.5708; return `<line x1="${R + 20 + Math.cos(an) * (R - 30)}" y1="${R + 20 + Math.sin(an) * (R - 30)}" x2="${R + 20 + Math.cos(an) * (R - (i % 6 ? 14 : 4))}" y2="${R + 20 + Math.sin(an) * (R - (i % 6 ? 14 : 4))}" stroke="${INK}" stroke-width="${i % 6 ? 3 : 6}"/>`; }).join('') + `<line class="h" x1="${R + 20}" y1="${R + 20}" x2="${R + 20}" y2="${40}" stroke="${TL}" stroke-width="10" stroke-linecap="round"/><circle cx="${R + 20}" cy="${R + 20}" r="16" fill="${TL}"/>`); g.R = R; g.cx = x; g.cy = y; return g; };
  const pill = (c, x, y, col) => M.box(c, x - 34, y - 18, { width: '68px', height: '36px', borderRadius: '18px', background: `linear-gradient(90deg, ${col} 50%, #fff 50%)`, border: `3px solid ${INK}`, boxSizing: 'border-box', transformOrigin: '50% 50%' });
  const at = (g, h) => { const an = h / 24 * 6.2832 - 1.5708; return [g.cx + Math.cos(an) * (g.R + 70), g.cy + Math.sin(an) * (g.R + 70)]; };
  M.story({ bg: '#eef8f6', sbg: ['#eef8f6', '#e6f4f1', '#eef8f6'], tr: ['iris', 'slide'], ring: () => ({ color: '#ffffff', width: 10, shadow: .25 }),
    wins: [M.q(1380, 180, 420, 500, 24), M.c(1400, 200, 380), M.q(110, 180, 420, 500, 24)],
    caps: [['药，什么时候吃？', 'When should you take it?'], ['早、中、晚，按时间来（示例）', 'Morning, noon, night (sample)'], ['具体用法，听医生的', 'Follow your doctor’s advice']], port: { box: [60, 40, 1800, 920] },
    scenes: [
      [c => ({ d: dial(c, 620, 500, 320), t: X(c, 1000, 640, 80, INK, '用药时间钟', 900), e: X(c, 1004, 750, 36, TL, 'DOSE CLOCK', 700, M.MONO) }),
       (s, t, a) => { M.pop(s.d, t, a, 99, { from: .6 }); s.d.querySelector('.h').setAttribute('transform', `rotate(${((t - a) * 120).toFixed(1)} ${s.d.R + 20} ${s.d.R + 20})`); M.hero(s.t, t, a + .3, 99); M.rise(s.e, t, a + .6, 99); }],
      [c => { const d = dial(c, 620, 500, 320); return { d, p: [[8, '#ff8fab', '08:00 早'], [13, '#ffd166', '13:00 中'], [20, '#9bb7ff', '20:00 晚']].map(([h, col, n]) => { const [x, y] = at(d, h); const e = pill(c, x, y, col); e.l = X(c, x + 50, y - 22, 34, INK, n, 900); return e; }) }; },
       (s, t, a) => { s.d.style.opacity = 1; const hh = Math.min(22, 6 + (t - a) * 6); s.d.querySelector('.h').setAttribute('transform', `rotate(${(hh / 24 * 360).toFixed(1)} ${s.d.R + 20} ${s.d.R + 20})`); s.p.forEach((e, i) => { const tt = a + ([8, 13, 20][i] - 6) / 6; M.pop(e, t, tt, 99, { from: 2 }); M.rise(e.l, t, tt + .1, 99); }); }],
      [c => ({ card: M.card(c, 700, 260, 900, 420, '#fff'), t: X(c, 760, 320, 64, INK, '具体用法，听医生的', 900), l: ['✓ 按时、按量', '✓ 不舒服及时就医', '✓ 本视频仅为一般信息'].map((n, i) => X(c, 770, 450 + i * 70, 40, '#3d6b66', n, 700)) }),
       (s, t, a) => { M.rise(s.card, t, a - .1, 99, { dy: 60 }); M.hero(s.t, t, a + .2, 99); s.l.forEach((e, i) => M.rise(e, t, a + .6 + i * .2, 99)); }]
    ] });
})();
