#!/usr/bin/env node
/* Eva Video QA · Stage A page trace. Loads a section page exactly like scripts/render.mjs (same Chromium flags, same
 * page contract) but takes NO screenshots: it steps renderAt(t) over every scene and records
 *   - failed asset requests, HTTP errors, page errors and console errors (missing images, fonts, scripts, frame folders)
 *   - broken <img> elements, fonts used by visible text that are not installed
 *   - per sample time: the presenter window, where the engine puts her head (EV.face), the planned subject scale,
 *     visible text boxes, text drawn ON TOP of the face (elementsFromPoint), text overflowing its box, and a
 *     signature of every element's transform/opacity (to see whether a scene animates at all)
 *
 *   node qa/trace.mjs SECTION/index.html --out trace.json [--ar 9:16] [--query k=v&..] [--times a,b] [--browser PATH]
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const args = process.argv.slice(2);
const entry = args[0];
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
if (!entry || !opt('out')) { console.error('usage: trace.mjs SECTION/index.html --out trace.json [--ar 9:16] [--query ..]'); process.exit(2); }
const qs = new URLSearchParams(opt('query', '')); if (opt('ar')) qs.set('ar', opt('ar'));
let pw; for (const base of [process.cwd(), dirname(resolve(entry)), dirname(new URL(import.meta.url).pathname) + '/..']) {
  const req = createRequire(join(base, 'noop.js'));
  for (const m of ['playwright', 'playwright-core']) { try { pw = req(m); break; } catch { } }
  if (pw) break;
}
if (!pw) { console.error('playwright not found'); process.exit(3); }

const T = { page: entry, query: qs.toString(), requests_failed: [], http_errors: [], page_errors: [], console_errors: [], samples: [] };
const browser = await pw.chromium.launch({ executablePath: opt('browser', process.env.CHROME) || undefined, args: ['--allow-file-access-from-files', '--disable-web-security', '--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('requestfailed', r => T.requests_failed.push({ url: r.url(), error: (r.failure() || {}).errorText }));
page.on('response', r => { if (r.status() >= 400) T.http_errors.push({ url: r.url(), status: r.status() }); });
page.on('pageerror', e => T.page_errors.push(String(e.message || e)));
page.on('console', m => { if (m.type() === 'error') T.console_errors.push(m.text().slice(0, 300)); });
try {
  await page.goto(pathToFileURL(resolve(entry)).href + (qs.toString() ? '?' + qs : ''));
  await page.waitForFunction(() => window.READY, null, { timeout: 60000 });
  await page.evaluate(() => window.READY);
  T.ready = true;
} catch (e) { T.ready = false; T.ready_error = String(e.message || e).slice(0, 300); }

if (T.ready) {
  const meta = await page.evaluate(() => ({ END: window.END, W: (window.EV && EV.W) || 1920, H: (window.EV && EV.H) || 1080, portrait: !!(window.EV && EV.portrait),
    scenes: ((window.EV && EV.scenes) || []).map(s => ({ t0: s.t0, t1: s.t1, z: s.z || 1 })), face: window.EV && EV.face, src: window.EV && EV.src,
    safe: window.EV && EV.SAFE, caption: window.EV && EV.zone && EV.zone('caption') }));
  Object.assign(T, meta);
  if (meta.W !== 1920 || meta.H !== 1080) await page.setViewportSize({ width: meta.W, height: meta.H });
  await page.addStyleTag({ content: '*{pointer-events:auto !important}' });   // trace page only: makes every element hit-testable
  let times = opt('times') ? opt('times').split(',').map(Number) : [];
  if (!times.length) {
    const s = new Set();
    for (const sc of meta.scenes) { const a = Math.max(0, sc.t0), b = Math.min(meta.END, sc.t1); if (b - a < .05) continue;
      [a + .12, (a + b) / 2, b - .12].forEach(t => s.add(+t.toFixed(3))); }
    for (let t = .5; t < meta.END; t += 1) s.add(+t.toFixed(3));
    times = [...s].filter(t => t >= 0 && t < meta.END).sort((a, b) => a - b);
    if (times.length > 140) times = times.filter((_, i) => i % Math.ceil(times.length / 140) === 0);
  }
  for (const t of times) {
    const smp = await page.evaluate(async t => {
      window.renderAt(t); await window.imgWait(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      const W = EV.W, H = EV.H, out = { t, broken: [], text: [], over_face: [], overflow: [] };
      const vis = e => { if (!e.checkVisibility || !e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
        let o = 1; for (let p = e; p && p.nodeType === 1; p = p.parentElement) o *= +getComputedStyle(p).opacity; return o > .05; };
      for (const im of document.images) if (im.getAttribute('src') && vis(im) && (!im.complete || im.naturalWidth === 0)) out.broken.push(im.getAttribute('src').slice(0, 200));
      /* presenter window + where the engine put her head (same maths as engine.js evaRender) */
      const box = document.getElementById('eva');
      if (box && EV.evaImg && getComputedStyle(box).visibility !== 'hidden' && +getComputedStyle(box).opacity > .05) {
        const b = box.getBoundingClientRect(), r = EV.evaImg.getBoundingClientRect(), f = EV.face;
        const hh = f.h * r.height, cx = r.left + f.x * r.width, cy = r.top + f.y * r.height, hw = hh * .78;
        const head = { x: cx - hw / 2, y: cy - hh / 2, w: hw, h: hh };
        const rad = parseFloat(getComputedStyle(box).borderTopLeftRadius) || 0;
        /* visible part of the head: inside the window (rounded corners approximated by insetting the radius' 29% chord) and the frame */
        const ins = rad * .29, cx0 = Math.max(b.left + (rad > b.width / 2.2 ? ins : 0), 0), cy0 = Math.max(b.top + (rad > b.height / 2.2 ? ins : 0), 0);
        const cx1 = Math.min(b.right - (rad > b.width / 2.2 ? ins : 0), W), cy1 = Math.min(b.bottom - (rad > b.height / 2.2 ? ins : 0), H);
        const ix = Math.max(0, Math.min(cx1, head.x + head.w) - Math.max(cx0, head.x)), iy = Math.max(0, Math.min(cy1, head.y + head.h) - Math.max(cy0, head.y));
        const full = Math.max(W / EV.src.w, H / EV.src.h);
        out.face = Object.assign(head, { visible_frac: +(ix * iy / (head.w * head.h)).toFixed(3), scale: +(r.width / EV.src.w / full).toFixed(3),
          window: { x: b.left, y: b.top, w: b.width, h: b.height, r: rad }, visible: true,
          cut: { top: Math.max(0, cy0 - head.y) / hh, bottom: Math.max(0, head.y + hh - cy1) / hh, left: Math.max(0, cx0 - head.x) / hw, right: Math.max(0, head.x + hw - cx1) / hw } });
      }
      /* visible text */
      const texts = [];
      const walk = document.createTreeWalker(document.getElementById('stage') || document.body, NodeFilter.SHOW_TEXT);
      const seen = new Set();
      for (let n; (n = walk.nextNode());) {
        const e = n.parentElement; if (!e || seen.has(e) || !n.textContent.trim()) continue; seen.add(e);
        if (!vis(e)) continue;
        const rr = e.getBoundingClientRect(); if (rr.width < 2 || rr.height < 2) continue;
        if (rr.right < 0 || rr.bottom < 0 || rr.left > W || rr.top > H) continue;
        const cs = getComputedStyle(e);
        texts.push({ e, rect: { x: rr.left, y: rr.top, w: rr.width, h: rr.height }, txt: n.textContent.trim().slice(0, 40), font: cs.fontFamily, size: parseFloat(cs.fontSize) });
        if ((cs.overflow === 'hidden' || cs.overflowX === 'hidden' || cs.overflow === 'clip') && e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0)
          out.overflow.push({ txt: n.textContent.trim().slice(0, 40), scroll: e.scrollWidth, client: e.clientWidth });
      }
      out.text = texts.map(x => ({ rect: x.rect, txt: x.txt, font: x.font, size: x.size }));
      /* text drawn on top of the face: hit-test a 5x5 grid inside the head box */
      if (out.face) {
        const h = out.face, tset = new Set(texts.map(x => x.e)), hits = new Map(); let pts = 0;
        for (let i = 1; i <= 5; i++) for (let j = 1; j <= 5; j++) {
          const x = h.x + h.w * (.1 + .8 * (i - 1) / 4), y = h.y + h.h * (.12 + .8 * (j - 1) / 4);
          if (x < 0 || y < 0 || x >= W || y >= H) continue; pts++;
          const top = document.elementFromPoint(x, y);
          for (let p = top; p; p = p.parentElement) { if (tset.has(p)) { hits.set(p, (hits.get(p) || 0) + 1); break; } if (p.id === 'eva') break; }
        }
        for (const [e, c] of hits) out.over_face.push({ txt: e.textContent.trim().slice(0, 40), frac: +(c / Math.max(1, pts)).toFixed(2) });
      }
      /* animation signature of the visible scene layers */
      let sig = '';
      for (const L of document.querySelectorAll('#stage > .layer')) if (L.style.display !== 'none')
        for (const e of L.querySelectorAll('*')) sig += (e.style.transform || '') + (e.style.opacity || '') + (e.style.clipPath || '') + (e.style.left || '') + (e.style.top || '') + '|';
      let hsh = 0; for (let i = 0; i < sig.length; i++) hsh = (hsh * 31 + sig.charCodeAt(i)) | 0;
      out.sig = hsh; out.layers = [...document.querySelectorAll('#stage > .layer')].map((L, i) => L.style.display !== 'none' ? i : -1).filter(i => i >= 0);
      return out;
    }, t);
    T.samples.push(smp);
  }
  /* fonts: is the first family of every visible text style installed? (width test against two generic fallbacks) */
  const fams = [...new Set(T.samples.flatMap(s => s.text.map(x => x.font)))];
  T.fonts = await page.evaluate(async fams => {
    /* @font-face fonts load lazily: load each family first, so a declared-but-not-yet-used face is not reported missing */
    for (const stack of fams) { const f = stack.split(',')[0].trim(); try { await document.fonts.load(`40px ${f.startsWith('"') || f.startsWith("'") ? f : `"${f}"`}`); } catch { } }
    await document.fonts.ready;
    const c = document.createElement('canvas').getContext('2d'), probe = 'Eva 视频 Style WMmw0123', gen = new Set(['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'inherit', 'emoji']);
    const w = f => { c.font = `40px ${f}`; return c.measureText(probe).width; };
    const res = {};
    for (const stack of fams) {
      const first = stack.split(',')[0].trim();
      if (gen.has(first.replace(/["']/g, ''))) continue;
      const q = first.startsWith('"') || first.startsWith("'") ? first : `"${first}"`;
      res[first.replace(/["']/g, '')] = document.fonts.check(`40px ${q}`) && (w(`${q}, monospace`) !== w('monospace') || w(`${q}, serif`) !== w('serif'));
    }
    return res;
  }, fams);
}
await browser.close();
mkdirSync(dirname(resolve(opt('out'))), { recursive: true });
writeFileSync(opt('out'), JSON.stringify(T));
console.log(`trace: ${T.samples.length} samples, ${T.requests_failed.length} failed requests, ${T.page_errors.length} page errors -> ${opt('out')}`);
