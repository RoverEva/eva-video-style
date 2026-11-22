/* T126 终端启动 Terminal Boot (tech): a terminal types commands, progress bars fill, deploy succeeds — generic shell, sample output. */
(function () { const M = K.T.mo, X = M.X, G = '#4ade80', BG = '#0b0f14';
  const term = (c, x, y, w, h) => { const g = M.box(c, x, y, { width: w + 'px', height: h + 'px', borderRadius: '16px', background: '#0f141b', border: '2px solid #233041', overflow: 'hidden', boxShadow: '0 30px 60px rgba(0,0,0,.5)' }); M.box(g, 0, 0, { width: w + 'px', height: '44px', background: '#16202b' }); [0, 1, 2].forEach(i => M.box(g, 20 + i * 28, 14, { width: '16px', height: '16px', borderRadius: '50%', background: ['#ff5f57', '#febc2e', '#28c840'][i] })); return g; };
  const typ = (e, txt, t, a, cps) => { const n = Math.max(0, Math.min(txt.length, Math.floor((t - a) * (cps || 24)))); e.textContent = t > a ? txt.slice(0, n) + (n < txt.length && Math.floor(t * 3) % 2 ? '▌' : '') : ''; };
  M.story({ bg: BG, sbg: [BG, '#0d1219', BG], tr: ['shutter', 'blur'], ring: () => ({ color: G, width: 4, glow: 'rgba(74,222,128,.4)', shadow: .5 }),
    wins: [M.q(1420, 200, 380, 460, 14), M.q(1420, 200, 380, 460, 14), M.c(1440, 200, 360)],
    caps: [['开机，敲第一行命令', 'Boot up, type the first command'], ['安装、构建、测试', 'Install, build, test'], ['上线成功', 'Deployed']], port: { box: [60, 40, 1800, 900] },
    scenes: [
      [c => { const g = term(c, 140, 160, 1160, 640); return { g, l: [0, 1, 2].map(i => X(g, 30, 80 + i * 60, 34, i ? '#9fb3c8' : G, '', 500, M.MONO, { whiteSpace: 'pre' })) }; },
       (s, t, a) => { M.pop(s.g, t, a, 99, { from: .8 }); typ(s.l[0], '$ eva init my-video', t, a + .5); typ(s.l[1], '  ✓ project created', t, a + 1.5, 60); typ(s.l[2], '  ✓ 185 templates ready', t, a + 1.9, 60); }],
      [c => { const g = term(c, 140, 160, 1160, 640); return { g, rows: [['install', .9], ['build', .7], ['test', .5]].map(([k, d], i) => { const r = M.box(g, 30, 90 + i * 150, {}); X(r, 0, 0, 34, '#9fb3c8', '$ eva ' + k, 500, M.MONO); r.bar = M.box(r, 0, 60, { width: '0px', height: '26px', background: G, borderRadius: '4px' }); M.box(r, 0, 60, { width: '1000px', height: '26px', border: '2px solid #233041', borderRadius: '4px', boxSizing: 'border-box' }); r.d = d; return r; }) }; },
       (s, t, a) => { s.g.style.opacity = 1; s.rows.forEach((r, i) => { M.rise(r, t, a - .1 + i * .5, 99); r.bar.style.width = (1000 * M.o3((t - a - i * .5) / (r.d + .4))) + 'px'; }); }],
      [c => ({ ok: X(c, 160, 300, 150, G, 'DEPLOYED', 400, M.MONO, { textShadow: `0 0 30px ${G}` }), u: X(c, 170, 520, 40, '#9fb3c8', 'https://my-video.example  ·  0 errors', 500, M.MONO) }),
       (s, t, a) => { M.hero(s.ok, t, a - .1, 99); M.rise(s.u, t, a + .5, 99); s.ok.style.opacity = t > a ? (Math.floor((t - a) * 8) % 2 || t > a + .6 ? 1 : .3) : 0; }]
    ] });
})();
