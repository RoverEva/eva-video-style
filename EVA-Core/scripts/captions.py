#!/usr/bin/env python3
"""Eva Video Style captions: bilingual SRT -> editable .srt (CN line + EN line) and styled .ass for burning.

Input: one SRT that holds Chinese cues and English cues for the same speech (any order, timings may differ
slightly). Each Chinese cue is paired with the English cue it overlaps most.

usage: captions.py SRC.srt START END OUT_BASENAME [config.json]
  START/END   seconds to cut (use 0 and a large number for the whole video)
  config.json optional: {"fix": {"original Chinese line": "display text"}, "keys": ["keyword", ...]}
              "fix" corrects obvious typos/mistranslations (Chinese or English lines) in the burned captions only (the source SRT is never edited);
              "keys" are words to highlight in lime (first match per line);
              "mode": "en" writes English-only captions (one larger line) for international versions.
"""
import re, sys
src, start, end, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
import json as _j
_cfg = _j.load(open(sys.argv[5], encoding='utf-8')) if len(sys.argv) > 5 else {}
DISPLAY_FIX = _cfg.get('fix', {})
KEYS = []
cjk = lambda s: any('一' <= c <= '鿿' for c in s)
def ts(s):
    h, m, r = s.strip().split(':'); sec, ms = r.split(',')
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
def fmt_srt(t):
    t = max(0, t); ms = round(t * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def fmt_ass(t):
    t = max(0, t); cs = round(t * 100); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
raw = []
for b in re.split(r'\n\s*\n', open(src, encoding='utf-8-sig').read().strip()):
    lines = b.strip().splitlines()
    if len(lines) < 3 or '-->' not in lines[1]: continue
    a, z = [ts(x) for x in lines[1].split('-->')]
    raw.append((a, z, re.sub(r'\s{2,}', ' ', ' '.join(l.strip() for l in lines[2:]).strip())))
# A bilingual SRT is usually made of blocks: all Chinese cues, then all English cues (timestamps restart at each block;
# re-exports can add more Chinese/English block pairs). Classify whole blocks so Chinese-side cues spoken in English
# (e.g. "oh my god") stay on the Chinese line; with a single block, fall back to per-cue script detection.
blocks, cur = [], []
for i, r in enumerate(raw):
    if cur and r[0] < raw[i - 1][0] - 5: blocks.append(cur); cur = []
    cur.append(r)
if cur: blocks.append(cur)
if len(blocks) > 1 and any(not any(cjk(r[2]) for r in b) for b in blocks):
    cnl = sorted(r for b in blocks if any(cjk(x[2]) for x in b) for r in b); enl = [r for b in blocks if not any(cjk(x[2]) for x in b) for r in b]
else: cnl = sorted([r for r in raw if cjk(r[2])]); enl = [r for r in raw if not cjk(r[2])]
if not cnl: cnl, enl = sorted(enl), []   # English-only SRT (e.g. eva-asr on an English talk): each cue is its own line
def ov(x, y): return max(0, min(x[1], y[1]) - max(x[0], y[0]))
used = set(); cues = []
for c in cnl:
    best = max(((ov(c, e), i) for i, e in enumerate(enl) if i not in used), default=(0, -1))
    en = ''
    if best[1] >= 0 and best[0] >= .5 * min(c[1] - c[0], enl[best[1]][1] - enl[best[1]][0]): en = DISPLAY_FIX.get(enl[best[1]][2].strip(), enl[best[1]][2]); used.add(best[1])
    a, z = c[0], c[1]
    if z <= start or a >= end or min(z, end) - max(a, start) < 0.2: continue
    cn = DISPLAY_FIX.get(c[2].strip(), c[2])
    if not en: en = DISPLAY_FIX.get('EN:' + c[2].strip(), '')   # a Chinese line with no English cue: supply one in config as "EN:<chinese>"
    if not cjk(cn): en = ''   # spoken in English already: show it once
    cues.append((max(a, start) - start, min(z, end) - start, cn, en))
MODE = _cfg.get('mode', 'cn-en')   # "cn-en" (Chinese line + English line) or "en" (English only, one bigger line)
if MODE == 'en': cues = [(a, z, '', e or (c if not cjk(c) else '')) for a, z, c, e in cues]; cues = [q for q in cues if q[3]]
with open(out + '.srt', 'w', encoding='utf-8') as f:
    for i, (a, z, c, e) in enumerate(cues, 1): f.write(f'{i}\n{fmt_srt(a)} --> {fmt_srt(z)}\n' + '\n'.join(x for x in (c, e) if x) + '\n\n')
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CN,Noto Sans CJK SC Black,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,4,2,2,380,380,34,1
Style: EN,Inter,34,&H00F2F2F2,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0.5,0,1,3,1.5,2,380,380,34,1
Style: ENB,Inter Black,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0.5,0,1,4,2,2,300,300,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
HL, WH = r'{\c&H2EFFD4&}', r'{\c&HFFFFFF&}'  # lime #d4ff2e (BGR)
KEYS = KEYS + _cfg.get('keys', [])
def hl(t):
    for k in sorted(KEYS, key=len, reverse=True):
        if k in t: return t.replace(k, HL + k + WH, 1)
    return t
with open(out + '.ass', 'w', encoding='utf-8') as f:
    f.write(head)
    for a, z, c, e in cues:
        if MODE == 'en': f.write(f'Dialogue: 0,{fmt_ass(a)},{fmt_ass(z)},ENB,,0,0,0,,{{\\fad(60,40)}}{hl(e)}\n'); continue
        body = hl(c) if c else ''
        if e: body += (r'\N' if c else '') + r'{\rEN}' + e
        f.write(f'Dialogue: 0,{fmt_ass(a)},{fmt_ass(z)},CN,,0,0,0,,{{\\fad(60,40)}}{body}\n')
print(out, len(cues), 'cues')
