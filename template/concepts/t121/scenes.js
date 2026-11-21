/* T121 维权三步 Three Steps (legal info, not legal advice). Labour arbitration in China is free of charge. */
(function () { const M = K.T.mo, X = M.X, INK = '#1e2d38';
  M.story({ bg: '#f3f1ec', sbg: ['#f3f1ec', '#1e2d38', '#f3f1ec'], tr: ['rise', 'push'], ring: () => ({ color: '#ffffff', width: 10, shadow: .3 }),
    wins: [M.c(1440, 140, 380), M.c(1560, 110, 300), M.q(120, 160, 420, 500, 24)],
    caps: [['工资被拖欠，分三步走', 'Unpaid wages? Three steps'], ['先留证据：工资条、聊天、考勤', 'Keep proof: payslips, chats, attendance'], ['劳动仲裁，不收费', 'Labour arbitration is free']], port: { box: [100, 60, 1820, 800] },
    scenes: [
      [c => ({ st: ['留证据', '去协商', '走仲裁'].map((s2, i) => { const g = M.box(c, 140 + i * 360, 720 - (i + 1) * 170, { width: '360px', height: (i + 1) * 170 + 'px', background: ['#c9d6df', '#8fa9b8', '#3d5a6c'][i], transformOrigin: '50% 100%' }); X(g, 30, 24, 52, i === 2 ? '#fff' : INK, `${i + 1} ${s2}`); return g; }), t: X(c, 140, 70, 70, INK, '三步，拿回你的钱'), d: X(c, 144, 160, 28, '#6b7b86', '法律常识分享 · 非法律意见') }),
       (s, t, a) => { s.st.forEach((g, i) => { const u = M.os((t - a - .3 - i * .25) / .4); g.style.transform = `scaleY(${Math.max(0, u).toFixed(3)})`; g.style.opacity = u > 0 ? 1 : 0; }); M.hero(s.t, t, a + .2, 99); M.rise(s.d, t, a + .5, 99); }],
      [c => ({ h: X(c, 140, 150, 80, '#fff', '第一步：留证据'), it: ['工资条', '聊天记录', '考勤打卡'].map((s2, i) => { const g = M.card(c, 140 + i * 430, 380, 390, 260, '#2d4250', { border: '2px solid #4d6a7c' }); X(g, 36, 40, 80, '#8fd3ff', ['📄', '💬', '🕘'][i], 400, M.INTER); X(g, 36, 160, 50, '#fff', s2); return g; }) }),
       (s, t, a) => { M.hero(s.h, t, a - .1, 99); s.it.forEach((g, i) => M.rise(g, t, a + .2 + i * .2, 99, { dy: 100 })); }],
      [c => ({ big: X(c, 640, 260, 130, INK, '劳动仲裁'), free: M.box(c, 640, 460, { padding: '16px 44px', background: '#2fbf71', borderRadius: '999px', font: M.f(900, 64, M.CN), color: '#fff', transformOrigin: '50% 50%' }, '不收费'), d: X(c, 644, 620, 28, '#6b7b86', '法律常识分享 · 具体请咨询专业律师') }),
       (s, t, a) => { M.hero(s.big, t, a - .1, 99, { dx: 60 }); M.pop(s.free, t, a + .5, 99, { from: 1.5 }); M.rise(s.d, t, a + .9, 99); }]
    ] });
})();
