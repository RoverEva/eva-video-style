/* T13 TECH · 科技蓝 Tech Blue — demo (16 s). Screens are real recordings; copy describes Eva Video Style itself. */
(function () {
  const C = EV, { el, tf, pop, slide, P, ease, clamp } = C, k = K, T = K.T, X = T.TECH;
  C.src0 = 30; C.end = 16; C.evaDir = '../../media/eva'; C.face = { x: .54, y: .35, h: .5 };
  const CARD = { x: 1280, y: 230, w: 480, h: 600, r: 4, s: 1.5 }, CIRC = { x: 1620, y: 60, w: 230, h: 230, r: 115, s: 3 }, SIDE = { x: 1440, y: 120, w: 400, h: 500, r: 4, s: 1.7 };
  C.evaKeys = [{ t: 0, d: 0, L: Object.assign({}, CARD, { o: 0 }) }, { t: .6, d: .4, L: CARD }, { t: 3.5, d: .45, L: CIRC }, { t: 10.0, d: .45, L: SIDE }, { t: 13.0, d: .45, L: CIRC }];
  C.ringFn = t => ({ color: X.CYAN, width: 2, glow: 'rgba(98,240,255,.35)', shadow: .5, hud: X.CYAN });

  // B1 · title slide inside the HUD frame
  C.scene({ t0: 0, t1: 3.53, bg: T.techBg, quiet: true, build(L) {
      const st = {}; st.f = T.techFrame(L); st.t = T.techTitle(L, 'Eva Video Style', 'Tech Blue · 科技蓝模版', 200, 400, 120);
      k.sfx('riser', .1, .08, { d: .8 }); k.sfx('impact', .9, .14); k.sfx('pop', 1.5, .1); return st; },
    update(lt, st) { T.techFrameAt(st.f, P(lt, 0, 1.4)); tf(st.t.a, slide(lt, .9, .5, -60, 0)); tf(st.t.b, { o: P(lt, 1.5, .4) }); } });

  // B2 · table of contents
  C.scene({ t0: 3.5, t1: 7.03, bg: T.techBg, build(L) {
      const st = {}; st.c1 = T.corner(L, 1180, 90); st.c2 = T.corner(L, 120, 820, true);
      st.h = T.techTitle(L, 'Table of Contents', '', 0, 120, 76, 'center'); st.h.b.remove();
      st.toc = T.toc(L, [['Opening', '开场钩子'], ['Explain', '讲清一个概念'], ['Results', '成果和数字'], ['Demo', '真实录屏'], ['How-to', '步骤教程'], ['Finale', '行动号召']], 640);
      for (let i = 0; i < 6; i++) k.sfx('pop', 3.9 + i * .22, .07, { f: 800 + i * 80 }); return st; },
    update(lt, st, t) { tf(st.h, { o: P(lt, .05, .3) }); st.c1.style.opacity = st.c2.style.opacity = P(lt, 0, .3); T.tocAt(st.toc, t, 3.9, .22); } });

  // B3 · chamfered section-title panel
  C.scene({ t0: 7.0, t1: 10.03, bg: T.techBg, build(L) {
      const st = {}; st.p = T.panel(L, 360, 380, 1200, 300, 'Introduction', '一种可复用的视频模版 · 双语字幕 · 不加背景音乐');
      st.r = el(L, 'div', 'abs', { left: '1180px', top: '760px', width: '440px', height: '22px', backgroundImage: `repeating-linear-gradient(90deg, ${X.LINE} 0 4px, transparent 4px 9px)` });
      st.d = el(L, 'div', 'abs', { left: '1640px', top: '340px', width: '6px', height: '120px', backgroundImage: `repeating-linear-gradient(180deg, ${X.DIM} 0 3px, transparent 3px 8px)` });
      k.sfx('whoosh', 7.1, .08); k.sfx('ding', 7.9, .07); return st; },
    update(lt, st) { T.panelAt(st.p, P(lt, .05, 1.1)); st.r.style.transform = `scaleX(${ease.outExpo(P(lt, .8, .6))})`; st.r.style.transformOrigin = '0 50%'; st.d.style.opacity = P(lt, .9, .3); } });

  // B4 · real screen band + icon cards (Eva in a side card)
  C.scene({ t0: 10.0, t1: 13.03, bg: T.techBg, build(L) {
      const st = {}; st.b = T.band(L, '../../media/screen/f_01200.jpg', 0, 0, 1380, 560);
      st.l = el(L, 'div', 'abs', { left: '60px', top: '600px', width: '1300px', height: '2px', background: X.LINE });
      st.a = T.infoCard(L, 'code', 'Real Screens', '真实录屏 · 只用你自己的软件和网站画面', 80, 660, 560); st.c = T.infoCard(L, 'play', 'One Click', '一键套用 · 同一套模版用在每条视频', 720, 660, 600);
      st.bc = el(L, 'div', 'abs', { left: '300px', top: '880px', width: '240px', height: '20px', backgroundImage: `repeating-linear-gradient(90deg, ${X.LINE} 0 3px, transparent 3px 7px)` });
      k.sfx('pop', 10.6, .1); k.sfx('pop', 11.0, .1, { f: 1100 }); return st; },
    update(lt, st, t) { const u = ease.outExpo(P(lt, 0, .6)); st.b.style.clipPath = `inset(0 ${100 - 100 * u}% 0 0)`; st.l.style.transform = `scaleX(${ease.outExpo(P(lt, .3, .6))})`; st.l.style.transformOrigin = '0 50%';
      tf(st.a, slide(t, 10.6, .4, -40, 0)); tf(st.c, slide(t, 11.0, .4, -40, 0)); st.bc.style.opacity = P(lt, 1.2, .3); } });

  // B5 · three outlined column cards
  C.scene({ t0: 13.0, t1: C.end + .05, bg: T.techBg, build(L) {
      const st = {}; st.c1 = T.corner(L, 1240, 70); st.h = T.techTitle(L, 'Three Steps · 三步', '', 0, 80, 64, 'center'); st.h.b.remove();
      st.cards = [T.colCard(L, 250, 230, 440, 640, 'doc', 'Script', ['口播 + 双语字幕 SRT', '按句子分段', '标出关键词'], '01'),
                  T.colCard(L, 740, 230, 440, 640, 'window', 'Design', ['选模版 T01–T13', '每个镜头对齐字幕', 'Eva 头部完整'], '02'),
                  T.colCard(L, 1230, 230, 440, 640, 'cloud', 'Export', ['16:9 · 1920×1080', '中英双语字幕', '无背景音乐'], '03')];
      [0, 1, 2].forEach(i => k.sfx('pop', 13.3 + i * .3, .1, { f: 800 + i * 150 })); return st; },
    update(lt, st, t) { tf(st.h, { o: P(lt, .05, .3) }); st.c1.style.opacity = P(lt, 0, .3); st.cards.forEach((c, i) => { const u = ease.outExpo(P(t, 13.3 + i * .3, .5)); tf(c, { y: 60 * (1 - u), o: u }); }); } });
})();
