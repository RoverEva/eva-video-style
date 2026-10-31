/* EVA Card System — all nine layout presets in turn (2 s each), premium theme. Reference for every EC.layout call. */
(function () {
  const C = EV, k = K, EC = K.EC, S = CS; S.setup(C, 18);
  const th = EC.theme('premium'), SIDE = { x: -470, y: 0, w: 1920, h: 1080, r: 0, s: 1 }, MID = { x: 560, y: 330, w: 800, h: 750, r: 0, s: 1 };
  const L9 = [ // [layout, data, box, presenter window]
    ['hero', { hero: S.HERO2, size: 220 }, { x: 1000, y: 120, w: 820, h: 700 }, SIDE],
    ['steps-v', { steps: S.STEPS, n: 3 }, { x: 1000, y: 170, w: 790, h: 730 }, SIDE],
    ['steps-h', { steps: S.STEPS, n: 4 }, { x: 990, y: 190, w: 860, h: 500 }, SIDE],
    ['orbit', { items: S.SEVEN, n: 6, c: [960, 700], R: 540, size: 200 }, { x: 0, y: 0, w: 1920, h: 1080 }, MID],
    ['statement', { statement: S.STATEMENT, size: 220 }, { x: 1000, y: 240, w: 820, h: 600 }, SIDE],
    ['stack', { steps: S.STEPS, n: 4 }, { x: 1010, y: 170, w: 820, h: 740 }, SIDE],
    ['feature', { feature: S.FEATURE }, { x: 880, y: 270, w: 940, h: 540 }, SIDE],
    ['journey', { items: S.SEVEN, n: 7, size: 140, amp: 300 }, { x: 230, y: 250, w: 1460, h: 330 }, MID],
    ['grid', { items: S.SEVEN, n: 7, cols: 3 }, { x: 1040, y: 120, w: 720, h: 900 }, SIDE],
  ];
  C.evaKeys = L9.map((l, i) => ({ t: i * 2, d: 0, L: l[3] })); C.ringFn = () => ({ color: 'transparent', width: 0, shadow: 0 });
  C.scene({ t0: 0, t1: C.end + .05, bg: 'radial-gradient(1400px 900px at 55% 25%, rgba(255,255,255,.18), rgba(255,255,255,0) 60%), #dac6b6', quiet: true, build() { return {}; }, update() {} });
  C.scene({ t0: 0, t1: C.end + .05, z: 60, quiet: true, build(L) {
      return { g: L9.map(([name, data, box]) => { const w = EC.group(L, 0, 0, 1920, 1080, 15); return { w, o: EC.layout(w, name, data, box, th), n: data.n || 3 }; }) }; },
    update(lt, st, t) { const i = Math.min(8, Math.floor(t / 2)); st.g.forEach((g, k) => g.w.style.display = k === i ? '' : 'none');
      const g = st.g[i], t0 = i * 2 + .15; g.o.at(t, EC.times(t0, g.n, i === 3 || i >= 7 ? .1 : .22)); } });
})();
