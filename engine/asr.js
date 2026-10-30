/* Eva Video Style · eva-asr word timings for scenes.js (optional).
 *
 * scripts/asr.py writes OUT.transcript.js (window.EV_ASR = {...}) from eva-asr's word-aligned result.
 * Load it and this file before scenes.js:
 *   <script src="../srt/talk.transcript.js"></script>
 *   <script src="../../engine/asr.js"></script>
 * Then, inside scenes.js, land elements on the words instead of typing times by hand:
 *   const at = EV.asr.at;              // absolute seconds in the source video, like SRT times
 *   k.sfx('pop', T(at('HatchElite')), .14);
 *   tf(st.c, pop(lt, T(at('三个月', { from: 12 })) - t0, .35));
 *
 * EV.asr.at(text, {from=0, nth=0, end=false}) -> start time of the first word of the nth match at or after
 *   `from` (absolute seconds); end:true returns the end time of the last matched word. Matching ignores case,
 *   spaces and punctuation, and works across word boundaries (Chinese characters, multi-word phrases).
 *   Throws if the text is not in the transcript, so a render never silently mistimes a cue.
 * EV.asr.segments / EV.asr.en / EV.asr.words  raw data (absolute seconds).
 * EV.asr.has(text) -> boolean.
 */
(function (root) {
  const D = root.EV_ASR || null;
  const norm = s => String(s).toLowerCase().replace(/[\s\p{P}\p{S}]/gu, '');
  const words = [];
  if (D) for (const s of D.segments) {
    const ws = s.words && s.words.length ? s.words : [{ w: s.text, start: s.start, end: s.end }];
    let last = s.start;
    for (const w of ws) {
      const a = Number.isFinite(w.start) ? w.start : last, z = Number.isFinite(w.end) ? w.end : a;
      words.push({ w: w.w, start: a, end: z }); last = z;
    }
  }
  let text = '', owner = [];
  words.forEach((w, i) => { const n = norm(w.w); text += n; for (let j = 0; j < n.length; j++) owner.push(i); });

  function find(q, o) {
    const nq = norm(q);
    if (!nq) throw new Error('EV.asr.at: empty query');
    let from = o.from || 0, nth = o.nth || 0, pos = text.indexOf(nq);
    while (pos >= 0) {
      const i0 = owner[pos], i1 = owner[pos + nq.length - 1];
      if (words[i0].start >= from - 1e-6) { if (nth-- === 0) return [i0, i1]; }
      pos = text.indexOf(nq, pos + 1);
    }
    return null;
  }
  const A = {
    data: D, words, segments: D ? D.segments : [], en: D ? (D.en || []) : [],
    has(q, o = {}) { return !!(D && find(q, o)); },
    at(q, o = {}) {
      if (!D) throw new Error('EV.asr.at: no transcript loaded (include OUT.transcript.js from scripts/asr.py before engine/asr.js)');
      const r = find(q, o);
      if (!r) throw new Error(`EV.asr.at: "${q}" not found in the eva-asr transcript` + (o.from ? ` after ${o.from}s` : ''));
      return o.end ? words[r[1]].end : words[r[0]].start;
    },
  };
  if (root.EV) root.EV.asr = A; else root.EV_ASR_API = A;
  if (typeof module !== 'undefined') module.exports = A;
})(typeof window !== 'undefined' ? window : globalThis);
