#!/usr/bin/env node
/* Eva Video Style · section renderer (Playwright + FFmpeg).
 *
 *   node scripts/render.mjs SECTION/index.html --out out/sec/s1.mp4      full section -> silent H.264 MP4
 *   node scripts/render.mjs SECTION/index.html --stills out/check --times 1,4.5,9   PNG stills for layout checks
 *   node scripts/render.mjs SECTION/index.html --cues out/s1_cues.json             dump sound cues only
 *
 * Options: --fps 30  --from SECONDS  --to SECONDS  --crf 16  --browser /path/to/chromium
 * The page must follow the contract in engine/engine.js (READY, END, renderAt, imgWait).
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

const req = createRequire(join(process.cwd(), 'noop.js'));
let pw; for (const m of ['playwright', 'playwright-core']) { try { pw = req(m); break; } catch { } }
if (!pw) { console.error('Install Playwright first: npm i playwright  (or playwright-core with your own Chromium)'); process.exit(1); }

const browser = await pw.chromium.launch({ executablePath: opt('browser', process.env.CHROME) || undefined, args: ['--allow-file-access-from-files', '--disable-web-security', '--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('[page error]', e.message));
await page.goto(pathToFileURL(resolve(entry)).href);
await page.waitForFunction(() => window.READY);
await page.evaluate(() => window.READY);
const END = await page.evaluate(() => window.END);

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
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.log(`frame ${f - f0}/${f1 - f0}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await done;
  console.log('done', out, f1 - f0, 'frames');
}
await browser.close();
