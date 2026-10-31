/* EVA Card System tests (Playwright, no video render): node tests/test_cards.mjs */
import { createRequire } from 'node:module'; import { resolve } from 'node:path'; import { pathToFileURL } from 'node:url';
const pw = createRequire(resolve('noop.js'))('playwright'); let fails = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
const b = await pw.chromium.launch({ args: ['--allow-file-access-from-files'] });
async function open(p) { const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } }), errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto(pathToFileURL(resolve(p)).href); await pg.waitForFunction(() => window.READY); await pg.evaluate(() => window.READY); return { pg, errs }; }

// 1 · preview sections load, render and use the shared components
for (const d of ['layouts', 't17', 't20', 't01', 't09']) { const { pg, errs } = await open(`template/cards/${d}/index.html`);
  await pg.evaluate(() => window.renderAt(3)); ok(errs.length === 0, `cards/${d} renders without page errors ${errs.join(' ')}`); await pg.close(); }

// 2 · API: 5 components, 9 layouts, themes, schema
const { pg, errs } = await open('template/cards/layouts/index.html');
const r = await pg.evaluate(() => { const EC = K.EC, L = document.createElement('div'); document.getElementById('stage').appendChild(L); const th = EC.theme('t17'), S = CS, out = {};
  out.components = ['HeroCard', 'StepCard', 'IconCard', 'FlowCard', 'FeatureCard'].filter(n => typeof EC[n] === 'function').length;
  out.layouts = Object.keys(EC.LAYOUTS); out.themes = Object.keys(EC.THEMES);
  const data = { hero: S.HERO, statement: S.STATEMENT, steps: S.STEPS, items: S.SEVEN, feature: S.FEATURE };
  out.built = out.layouts.filter(n => { const o = EC.layout(L, n, data, { x: 900, y: 100, w: 900, h: 800 }, th); o.at(5, EC.times(1, 7)); return true; }).length;
  const spec = { id: 'card_001', type: 'step', layout: 'steps-v', style: 'premium-soft-3d', content: { number: 1, title: 'IDEA', subtitle: 'Find the opportunity', icon: 'idea' },
    position: { anchor: 'right', x: .55, y: .2, w: .4, h: .25 }, animation: { preset: 'fade-slide', start: 2.5, duration: .6 } };
  out.validGood = EC.validate(spec).length; out.validBad = EC.validate({ id: 'x', type: 'nope', animation: {} }).length;
  const list = EC.fromSchema(L, [spec, { id: 'c2', type: 'layout', layout: 'grid', content: { items: S.SEVEN }, position: { anchor: 'right' }, animation: { start: 10, stagger: .1 } }], th, { toLocal: s => s - 1 });
  EC.schemaAt(list, 4); out.schemaTimes = list.map(c => c.times[0]); out.cards = L.querySelectorAll('div').length;
  const t = EC.theme('t01', { acc: '#f00' }); out.override = t.acc === '#f00' && t.surf[0] === '#ffffff';
  out.safe = !EC.overlapsFace(EC.region('right', { x: 150, y: 300, w: 560, h: 560 }), { x: 150, y: 300, w: 560, h: 560 }); return out; });
ok(r.components === 5, 'five card components exported'); ok(r.layouts.length === 9 && r.built === 9, `nine layouts build + animate (${r.layouts.join(', ')})`);
ok(['t17', 't20', 't01', 't09'].every(t => r.themes.includes(t)), 'themes for T17 / T20 / T01 / T09'); ok(r.validGood === 0 && r.validBad >= 2, 'schema validation');
ok(r.schemaTimes[0] === 1.5 && Math.abs(r.schemaTimes[1] - 9) < 1e-9, 'schema timing converts absolute -> section time'); ok(r.override, 'theme overrides'); ok(r.safe, 'right region keeps clear of presenter window');
ok(errs.length === 0, 'no page errors in API test'); await pg.close();

// 3 · backward compatibility: original demos load unchanged and never see the card layer
for (const d of ['t17', 't20', 't01', 't09']) { const { pg, errs } = await open(`template/demo/${d}/index.html`);
  const ec = await pg.evaluate(() => { window.renderAt(5); return typeof K.EC; }); ok(errs.length === 0 && ec === 'undefined', `demo/${d} unchanged (no errors, card layer not loaded)`); await pg.close(); }
await b.close(); console.log(fails ? `${fails} failed` : 'all passed'); process.exit(fails ? 1 : 0);
