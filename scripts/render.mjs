#!/usr/bin/env node
/* Eva Video Style · section renderer (Playwright + FFmpeg).
 *
 *   node scripts/render.mjs SECTION/index.html --out out/sec/s1.mp4      full section -> silent H.264 MP4
 *   node scripts/render.mjs SECTION/index.html --stills out/check --times 1,4.5,9   PNG stills for layout checks
 *   node scripts/render.mjs SECTION/index.html --cues out/s1_cues.json             dump sound cues only
 *
 * Options: --fps 30  --from SECONDS  --to SECONDS  --crf 16  --browser /path/to/chromium
 *          --ar 9:16    portrait 1080x1920 (default 16:9 = 1920x1080); the page's EV.W/EV.H set the viewport
 *          --query k=v&k2=v2   extra page URL parameters (e.g. eva=../media/eva_v&srcw=1080&srch=1920&face=.5,.24,.3)
 *          --no-qa      skip the built-in QA guard (below)
 * The page must follow the contract in engine/engine.js (READY, END, renderAt, imgWait).
 *
 * QA guard (qa/README.md): with --out, a missing image/font/script/frame or a JavaScript error is a confirmed defect, so
 * the render stops before the first frame (or as soon as it happens mid-render), the partial file is removed and the exit
 * code is 4. With --stills the same problems are only reported. Full Stage A checks: python3 -m qa pre --page PAGE.
 */
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync, writeFileSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const args = process.argv.slice(2);
const entry = args[0] && !args[0].startsWith('--') ? args[0] : null;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
if (!entry) { console.error('usage: render.mjs SECTION/index.html (--out file.mp4 | --stills DIR --times a,b | --cues file.json)'); process.exit(1); }
const fps = +opt('fps', 30), out = opt('out'), stills = opt('stills'), cues = opt('cues');
const qs = new URLSearchParams(opt('query', '')); if (opt('ar')) qs.set('ar', opt('ar'));

const req = createRequire(join(process.cwd(), 'noop.js'));
let pw; for (const m of ['playwright', 'playwright-core']) { try { pw = req(m); break; } catch { } }
if (!pw) { console.error('Install Playwright first: npm i playwright  (or playwright-core with your own Chromium)'); process.exit(1); }

const browser = await pw.chromium.launch({ executablePath: opt('browser', process.env.CHROME) || undefined, args: ['--allow-file-access-from-files', '--disable-web-security', '--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const noQa = args.includes('--no-qa'), qaIssues = [];
page.on('pageerror', e => { console.error('[page error]', e.message); qaIssues.push('JavaScript error: ' + e.message); });
page.on('requestfailed', r => qaIssues.push('missing file: ' + decodeURIComponent(r.url().replace('file://', ''))));
page.on('response', r => { if (r.status() >= 400) qaIssues.push(`HTTP ${r.status()}: ${r.url()}`); });
/* one line per problem; an image-sequence folder with many missing frames is one line */
function qaReport(when) {
  const seq = new Map(), other = [];
  for (const m of qaIssues) { const g = /^missing file: (.*)\/(f_\d+\.\w+)$/.exec(m); if (g) seq.set(g[1], [...(seq.get(g[1]) || []), g[2]]); else other.push(m); }
  const lines = [...new Set(other)].concat([...seq].map(([d, f]) => `missing ${f.length} frame(s) in ${d} (${f.sort()[0]} …)`));
  console.error(`QA ${when}: FAIL\n  ` + lines.slice(0, 12).join('\n  ') + '\n  fix the paths/media, or check the page with: python3 -m qa pre --page ' + entry);
}
await page.goto(pathToFileURL(resolve(entry)).href + (qs.toString() ? '?' + qs : ''));
await page.waitForFunction(() => window.READY);
await page.evaluate(() => window.READY);
const END = await page.evaluate(() => window.END);
if (qaIssues.length && out && !noQa) { qaReport('pre-render (page load)'); await browser.close(); process.exit(4); }
const [VW, VH] = await page.evaluate(() => [(window.EV && EV.W) || 1920, (window.EV && EV.H) || 1080]);
if (VW !== 1920 || VH !== 1080) await page.setViewportSize({ width: VW, height: VH });
console.log(`stage ${VW}x${VH}`);

async function frame(t) {
  await page.evaluate(async t => { window.renderAt(t); await window.imgWait(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }, t);
}

if (cues) {
  const list = await page.evaluate(() => window.EV.sfx);
  mkdirSync(dirname(resolve(cues)), { recursive: true }); writeFileSync(cues, JSON.stringify(list));
  console.log(cues, list.length, 'cues');
} else if (stills) {
  mkdirSync(stills, { recursive: true });
  for (const t of opt('times', '0').split(',').map(Number)) { await frame(t); await page.screenshot({ path: join(stills, `t_${t.toFixed(2).padStart(7, '0')}.png`) }); }
  console.log('stills ->', stills);
  if (qaIssues.length) qaReport('stills (report only)');
} else if (out) {
  if (existsSync(out)) { console.error('Refusing to overwrite', out); process.exit(1); }
  mkdirSync(dirname(resolve(out)), { recursive: true });
  const f0 = Math.round(+opt('from', 0) * fps), f1 = Math.round(+opt('to', END) * fps);
  const ff = spawn(process.env.FFMPEG || 'ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', opt('crf', '16'), '-pix_fmt', 'yuv420p', '-r', String(fps), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await frame(f / fps);
    if (qaIssues.length && !noQa) {   // an asset failed while rendering: stop early, never deliver a broken section
      ff.stdin.end(); await done.catch(() => { }); try { (await import('node:fs')).unlinkSync(out); } catch { }
      qaReport(`render (frame ${f}, ${(f / fps).toFixed(2)}s)`); await browser.close(); process.exit(4);
    }
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.log(`frame ${f - f0}/${f1 - f0}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await done;
  console.log('done', out, f1 - f0, 'frames');
}
await browser.close();
