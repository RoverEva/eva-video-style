// node tests/test_asr_js.mjs — engine/asr.js word-time lookups over an eva-asr transcript
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const src = readFileSync(new URL('../engine/asr.js', import.meta.url), 'utf8');
function load(data) {
  const win = { EV: {} }; if (data) win.EV_ASR = data; win.window = win;
  vm.runInNewContext(src, { window: win, globalThis: win });
  return win.EV.asr;
}
const data = { source: 'eva-asr', language: 'zh', en: [{ start: .5, end: 2.4, text: "Hi, I'm Eva." }], segments: [
  { start: .5, end: 2.4, text: '大家好，我是Eva。', words: [
    { w: '大', start: .5, end: .69 }, { w: '家', start: .69, end: .88 }, { w: '好' }, { w: '，', start: 1.07, end: 1.26 },
    { w: '我', start: 1.26, end: 1.45 }, { w: '是', start: 1.45, end: 1.64 }, { w: 'Eva', start: 1.64, end: 2.2 }, { w: '。', start: 2.2, end: 2.4 }] },
  { start: 2.8, end: 5.1, text: 'Eva 的 HatchElite App', words: [
    { w: 'Eva', start: 2.8, end: 3.2 }, { w: '的', start: 3.2, end: 3.4 }, { w: 'HatchElite', start: 3.5, end: 4.3 }, { w: 'App', start: 4.4, end: 5.1 }] },
  { start: 6, end: 7, text: 'segment without words' },
] };

const A = load(data);
assert.equal(A.at('大家'), .5);
assert.equal(A.at('家好'), .69);
assert.equal(A.at('好'), .88, 'untimed word inherits previous end');
assert.equal(A.at('我是eva'), 1.26, 'case/space/punctuation-insensitive, across words');
assert.equal(A.at('eva', { end: true }), 2.2);
assert.equal(A.at('Eva', { nth: 1 }), 2.8);
assert.equal(A.at('eva', { from: 2.5 }), 2.8);
assert.equal(A.at('hatchelite app', { end: true }), 5.1);
assert.equal(A.at('without words'), 6, 'segment-level fallback');
assert.equal(A.has('不存在'), false);
assert.throws(() => A.at('不存在'), /not found in the eva-asr transcript/);
assert.throws(() => A.at('eva', { from: 4 }), /after 4s/);
assert.equal(A.en[0].text, "Hi, I'm Eva.");
const none = load(null);
assert.equal(none.has('x'), false);
assert.throws(() => none.at('x'), /no transcript loaded/);
console.log('engine/asr.js: all assertions passed');
