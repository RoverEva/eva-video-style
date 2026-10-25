/* T11 DASH · HUD 仪表盘 HUD Dashboard — demo (20 s). Gauge / timer values are illustrative placeholders. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T;
  C.src0 = 40; C.end = 20; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const CARD = { x: 1230, y: 70, w: 560, h: 640, r: 8, s: 1.5 }, CIRC = { x: 1600, y: 70, w: 240, h: 240, r: 120, s: 3 };
  C.evaKeys = [{ t: 0, d: 0, L: CARD }, { t: 3.0, d: .45, L: CIRC }, { t: 9.0, d: .45, L: CARD }, { t: 11.5, d: .45, L: CIRC }, { t: 14.0, d: .45, L: CARD }, { t: 16.0, d: .45, L: CIRC }];
  C.ringFn = t => { const card = t < 3.2 || (t >= 9 && t < 11.6) || (t >= 14 && t < 16.2); return card ? { color: 'transparent', width: 0, shadow: .5, hud: 'rgba(255,255,255,.55)' } : { color: 'rgba(255,255,255,.35)', width: 2, shadow: .5 }; };
  const frame = L => T.hudFrame(L, 'EVA · DASHBOARD', '04');

  // D1 · process flow
  C.scene({ t0: 0, t1: 3.03, bg: T.hudBg, quiet: true, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '使用', '更简单', 110, 110, 54); st.f = T.flow(L, 110, 330, [['📁', '素材'], ['🤖', 'AI 助手', T.HUD.BLUE], ['🎬', '成片', T.HUD.GOLD]], 220);
      [0, 1, 2].forEach(i => k.sfx('pop', .6 + i * .5, .12, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, slide(lt, .05, .4, -40, 0)); T.flowAt(st.f, t, .6, .5); } });

  // D2 · gauge
  C.scene({ t0: 3.0, t1: 6.03, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.g = T.gauge(L, 860, 640, 260, 'NEXT FEW MONTHS · 接下来几个月'); k.note(L, '示意 · ILLUSTRATIVE', 1650, 1000);
      k.sfx('riser', 3.6, .08, { d: 1 }); k.sfx('ding', 4.7, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.gaugeAt(st.g, ease.outBack(P(lt, .6, 1.2), 1.2) * .5, 100); } });

  // D3 · quote card + timer + big gold result
  C.scene({ t0: 6.0, t1: 9.03, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.q = T.quote(L, '素材丢进去，AI 直接出片', 110, 230, 'AI 直接出片'); st.tm = T.timer(L, 160, 420);
      st.big = el(L, 'div', 'abs disp', { left: '820px', top: '200px', fontSize: '150px', color: T.HUD.GOLD, textShadow: '0 0 40px rgba(245,184,61,.4)' }, '30 MIN'); k.note(L, '示意 · ILLUSTRATIVE', 1650, 1000);
      for (let i = 0; i < 10; i++) k.sfx('click', 6.9 + i * .12, .05); k.sfx('impact', 8.1, .16); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.q, slide(lt, .1, .4, -40, 0)); tf(st.tm, pop(t, 6.6, .3)); T.timerAt(st.tm, 1800 * ease.io3(P(t, 6.9, 1.2))); tf(st.big, pop(t, 8.1, .4, 1.8)); } });

  // D4 · editing timeline + red ✕ ("回不去了")
  C.scene({ t0: 9.0, t1: 11.53, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '回不去了', '', 110, 110, 54); st.tl = T.timeline(L, 110, 260, 900, 6); st.x = T.xStamp(L, 560, 420, 240);
      k.sfx('impact', 10.2, .18); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, { o: P(lt, .1, .3) }); tf(st.tl, slide(lt, .05, .4, 0, 40)); tf(st.x, pop(t, 10.2, .3, 2.6)); } });

  // D5 · chips tick on → gold summary + grid fill
  C.scene({ t0: 11.5, t1: 14.03, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.c = T.checks(L, 110, 330, ['ISEE', 'SSAT', '词汇', '游戏'], 230);
      st.s = el(L, 'div', 'abs cn', { left: '110px', top: '480px', fontSize: '66px', color: '#fff' }, `一个平台 <span style="color:${T.HUD.GOLD}">全部覆盖</span>`); st.g = T.grid(L, 110, 640, 26, 5, 30);
      [0, 1, 2, 3].forEach(i => k.sfx('pop', 11.9 + i * .35, .1, { f: 900 + i * 100 })); k.sfx('ding', 13.3, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.checksAt(st.c, t, 11.8, .35, 13.3); tf(st.s, slide(t, 13.3, .4, 0, 30)); T.gridAt(st.g, P(t, 12.0, 1.8)); } });

  // D6 · toggle + slider + linked curves
  C.scene({ t0: 14.0, t1: 16.03, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.h = T.title(L, '', 'TIP · 小提醒', 110, 110, 40, T.HUD.GOLD); st.tg = T.toggle(L, 110, 230, '工作模式'); st.sl = T.slider(L, 110, 340, '模型档位'); st.ln = T.lines(L, 110, 500, 700, 260, ['模型能力', '成片效果']);
      k.sfx('click', 14.5, .1); k.sfx('click', 15.0, .08); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); tf(st.h, { o: P(lt, .1, .3) }); T.toggleAt(st.tg, P(t, 14.5, .25)); T.sliderAt(st.sl, ease.io3(P(t, 14.9, .7))); T.linesAt(st.ln, ease.io3(P(t, 15.0, .9))); } });

  // D7 · terminal + gold stamp  ·  D8 · version counter (use real version history)
  C.scene({ t0: 16.0, t1: C.end + .05, bg: T.hudBg, build(L) {
      const st = {}; st.fr = frame(L); st.tm = T.terminal(L, 110, 200, 980, ['$ eva render --template T11', '> rendering 600 frames ...', '> done ✓']); st.st = T.goldStamp(L, '已上线', 860, 400);
      st.v = T.version(L, 110, 560); st.vk = T.kicker(L, 'VERSION · 迭代', 116, 540);
      k.sfx('pop', 17.4, .14); for (let i = 0; i < 6; i++) k.sfx('click', 18.2 + i * .2, .05); return st; },
    update(lt, st, t) { T.hudFrameAt(st.fr, t); T.terminalAt(st.tm, t, 16.2, 24); tf(st.st, pop(t, 17.4, .3, 2.4)); tf(st.v, { o: P(t, 18.0, .3) }); T.versionAt(st.v, P(t, 18.2, 1.2), 1, 3); tf(st.vk, { o: P(t, 18.0, .3) }); } });
})();
