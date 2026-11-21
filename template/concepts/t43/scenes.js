/* T43 Whiteboard 白板手绘 · 10 s sample (illustrative copy). Marker writes a formula, boxes it, arrows to notes. */
(function () { const C = EV, M = K.T.mo, f = M.f, B = '#1f3d8a', R = '#d0342c', G = '#1b8a4a';
  M.setup({ bg: 'linear-gradient(180deg,#fbfbf8,#eef0ee)', win: { x: 1240, y: 170, w: 500, h: 500, r: 250, o: 1, s: 1.15 }, ring: () => ({ color: '#c9ced6', width: 14, shadow: .3 }), port: { box: [90, 60, 1060, 740] },
    captions: M.caps([['一个公式讲清楚流量', 'Reach in one formula'], ['曝光乘以点击率', 'Impressions times click rate'], ['两个都要抓', 'Work on both']]),
    build(L) { const s = {};
      s.t = M.txt(L, 110, 80, f(900, 64, M.CN), B, '一个公式讲清流量');
      s.ul = M.path(L, 110, 170, 700, 24, 'M4 14 C 200 4, 420 22, 690 8', B, 7);
      s.w = [['流量', B, 110], ['=', '#333', 300], ['曝光', R, 380], ['×', '#333', 575], ['点击率', G, 650]].map(([w, c, x]) => M.txt(L, x, 280, f(900, 86, M.CN), c, w));
      s.box = M.path(L, 355, 262, 640, 150, 'M14 22 Q 320 2 620 18 Q 636 76 618 132 Q 320 150 14 132 Q 0 76 14 22Z', R, 6);
      s.a1 = M.path(L, 420, 410, 160, 150, 'M40 6 C 20 60, 40 110, 110 138 M88 126 L112 139 L100 114', R, 6);
      s.a2 = M.path(L, 730, 410, 160, 150, 'M60 6 C 40 60, 60 110, 130 138 M108 126 L132 139 L120 114', G, 6);
      s.n1 = M.txt(L, 380, 560, f(900, 46, M.CN), R, '发得稳'); s.n1e = M.txt(L, 382, 618, f(600, 26, M.INTER), '#555', 'Post consistently');
      s.n2 = M.txt(L, 700, 560, f(900, 46, M.CN), G, '开头抓人'); s.n2e = M.txt(L, 702, 618, f(600, 26, M.INTER), '#555', 'Strong hook');
      s.ok = M.path(L, 110, 660, 520, 130, 'M10 60 L40 92 L96 20', B, 9); s.okt = M.txt(L, 180, 690, f(900, 58, M.CN), B, '两个都要抓！');
      return s; },
    update(s, t) { M.hero(s.t, t, .85, 9.2, { dx: -30 }); M.draw(s.ul, t, 1.3, .5, 9.2);
      s.w.forEach((e, i) => M.hero(e, t, 1.7 + i * .14, 9.2, { dx: -24, din: .3 }));
      M.draw(s.box, t, 3.6, .6, 9.2); M.draw(s.a1, t, 4.2, .45, 9.2); M.draw(s.a2, t, 4.6, .45, 9.2);
      M.rise(s.n1, t, 4.55, 9.2); M.rise(s.n1e, t, 4.7, 9.2); M.rise(s.n2, t, 4.95, 9.2); M.rise(s.n2e, t, 5.1, 9.2);
      M.draw(s.ok, t, 6.85, .35, 9.2); M.hero(s.okt, t, 7.0, 9.2); } });
})();
