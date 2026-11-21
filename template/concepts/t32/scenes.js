/* T32 Chat Bubbles 聊天对话 · 10 s concept sample (16:9). Silent; sample copy (illustrative).
 * Soft background → circular presenter window → a generic chat thread (no real app UI) builds line by line. */
(function () {
  const C = EV, T = K.T, M = T.mo, { el } = C;
  const CN = "'Noto Sans CJK SC', sans-serif", BLUE = '#2f6fe8';
  const bubble = (L, me, y, cn, en) => { const b = M.box(L, me ? 0 : 820, y, { maxWidth: '640px', padding: '20px 26px', borderRadius: me ? '30px 30px 8px 30px' : '30px 30px 30px 8px',
      background: me ? BLUE : '#ffffff', color: me ? '#fff' : '#1f2937', boxShadow: '0 8px 20px rgba(30,50,90,.12)', transformOrigin: me ? '100% 100%' : '0 100%' });
    if (me) { b.style.left = ''; b.style.right = '120px'; }
    el(b, 'div', '', { font: `700 40px ${CN}`, lineHeight: 1.3, whiteSpace: 'nowrap' }, cn); el(b, 'div', '', { font: '500 25px Inter, sans-serif', opacity: .78, marginTop: '4px', whiteSpace: 'nowrap' }, en); return b; };
  const dots = (L, y) => { const d = M.box(L, 820, y, { display: 'flex', gap: '10px', padding: '22px 26px', borderRadius: '30px', background: '#ffffff', transformOrigin: '0 100%' });
    d.dots = [0, 1, 2].map(() => el(d, 'div', '', { width: '14px', height: '14px', borderRadius: '50%', background: '#9aa5b8' })); return d; };
  M.setup({
    bg: 'linear-gradient(160deg, #eef3fb, #dfe7f5)',
    win: { x: 150, y: 170, w: 500, h: 500, r: 250, o: 1, s: 1.15 },
    ring: () => ({ color: '#ffffff', width: 12, shadow: .28 }),
    port: { box: [800, 40, 1000, 700] },
    captions: [{ t0: .5, t1: 3.4, cn: '朋友问我：剪视频要多久？', en: 'A friend asked: how long does editing take?' },
               { t0: 3.5, t1: 6.6, cn: '我说：上传就好，几分钟', en: 'Me: just upload, a few minutes' },
               { t0: 6.7, t1: 9.7, cn: '字幕？中英双语，自动加', en: 'Captions? Bilingual, automatic' }],
    build(L) { const s = {};
      s.head = M.box(L, 820, 60, { font: `700 26px Inter, sans-serif`, color: '#3b4a66', letterSpacing: '.08em' }, 'CHAT · 对话');
      s.d1 = dots(L, 130); s.q1 = bubble(L, false, 130, '剪一条视频要多久？', 'How long does one edit take?');
      s.a1 = bubble(L, true, 285, '上传就好，几分钟搞定', 'Just upload — done in minutes');
      s.read = M.box(L, 0, 430, { right: '126px', left: '', font: '600 22px Inter, sans-serif', color: '#6b7280' }, '已读 Read ✓✓'); s.read.style.left = ''; s.read.style.right = '126px';
      s.d2 = dots(L, 480); s.q2 = bubble(L, false, 480, '字幕也会自动加吗？', 'Captions added too?');
      s.a2 = bubble(L, true, 635, '会，中英双语', 'Yes — Chinese & English');
      s.heart = M.svg(L, 1716, 610, 64, 64, `<circle cx="32" cy="32" r="30" fill="#ff5c8a"/><path d="M32 46 C 16 36, 14 24, 22 20 C 27 17, 31 20, 32 24 C 33 20, 37 17, 42 20 C 50 24, 48 36, 32 46Z" fill="#fff"/>`, { transformOrigin: '50% 50%' });
      return s; },
    update(s, t) {
      M.rise(s.head, t, .8, 9.2, { dy: 14 });
      const typing = (d, a, b) => { d.style.display = t >= a && t < b ? '' : 'none'; M.pop(d, t, a, b + .02, { from: .7, dout: .1 }); d.dots.forEach((x, i) => { x.style.transform = `translateY(${(-6 * Math.max(0, Math.sin((t - a) * 9 - i * .9))).toFixed(1)}px)`; }); };
      typing(s.d1, .95, 1.6); M.pop(s.q1, t, 1.6, 9.2, { from: .8 });
      M.pop(s.a1, t, 2.7, 9.2, { from: .8 }); M.rise(s.read, t, 3.15, 9.2, { dy: 8 });
      typing(s.d2, 4.1, 4.75); M.pop(s.q2, t, 4.75, 9.2, { from: .8 });
      M.pop(s.a2, t, 6.0, 9.2, { from: .8 }); M.pop(s.heart, t, 6.75, 9.2, { from: .3 });
    }
  });
})();
