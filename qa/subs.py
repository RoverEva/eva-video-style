"""SRT / ASS parsing and timing validation (Chinese, English and bilingual Chinese+English SRTs).

Only syntax and timing are validated here. Whether the words line up with speech is a separate, evidence-based
check (SYNC_SPEECH in qa/post.py) and is never inferred from SRT syntax."""
import re

TS = re.compile(r"^\s*(\d{1,2}):(\d{2}):(\d{2})([,.])(\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})([,.])(\d{1,3})")
cjk = lambda s: any("\u3400" <= c <= "\u9fff" or "\uf900" <= c <= "\ufaff" for c in s)


def _sec(h, m, s, ms): return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def parse_srt(text):
    """-> (cues, problems). cue = {i, index, start, end, text, line}; problems = [(severity, message, cue_or_None)]"""
    problems, cues = [], []
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    line = 1
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n"); start_line = line; line += len(lines) + 1
        if not block.strip(): continue
        k = 0
        idx = lines[0].strip()
        if idx.isdigit(): k = 1
        elif not TS.match(idx):
            problems.append(("FAIL", f"line {start_line}: block does not start with a cue number or a timestamp: {idx[:40]!r}", None)); continue
        if k >= len(lines) or not TS.match(lines[k]):
            problems.append(("FAIL", f"line {start_line}: missing or malformed 'HH:MM:SS,mmm --> HH:MM:SS,mmm' timestamp", None)); continue
        m = TS.match(lines[k]).groups()
        if "." in (m[3], m[8]): problems.append(("WARN", f"line {start_line + k}: '.' used as millisecond separator (SRT uses ',')", None))
        if int(m[1]) > 59 or int(m[2]) > 59 or int(m[6]) > 59 or int(m[7]) > 59:
            problems.append(("FAIL", f"line {start_line + k}: minutes/seconds above 59", None)); continue
        body = [l for l in lines[k + 1:]]
        c = {"i": len(cues), "index": int(idx) if k else None, "start": _sec(*m[0:3], m[4]), "end": _sec(*m[5:8], m[9]),
             "text": "\n".join(l.strip() for l in body).strip(), "line": start_line}
        cues.append(c)
    return cues, problems


def tracks(cues):
    """split a bilingual SRT into language tracks: blocks of cues where the timeline restarts (captions.py convention),
    else by script (CJK / Latin). -> {"cn": [...], "en": [...]} (a monolingual file gives one track)"""
    blocks, cur = [], []
    for i, c in enumerate(cues):
        if cur and c["start"] < cues[i - 1]["start"] - 5: blocks.append(cur); cur = []
        cur.append(c)
    if cur: blocks.append(cur)
    if len(blocks) > 1:
        out = {"cn": [], "en": []}
        for b in blocks: out["cn" if any(cjk(c["text"]) for c in b) else "en"] += b
        return {k: v for k, v in out.items() if v}
    cn = [c for c in cues if cjk(c["text"])]; en = [c for c in cues if not cjk(c["text"])]
    paired = lambda c: "\n" in c["text"] and cjk(c["text"].split("\n")[0]) and re.search(r"[A-Za-z]{2}", c["text"].split("\n", 1)[1])
    if cn and sum(1 for c in cn if paired(c)) >= .5 * len(cn):   # paired cues "中文\nEnglish" (captions.py output)
        return {"cn+en": cues}
    return {k: v for k, v in (("cn", cn), ("en", en)) if v}


def validate_srt(text, duration=None, th=None, label="SRT"):
    """-> list of (severity, check, message, t) ; check ids: SRT_SYNTAX, SRT_TIMING, SRT_ORDER, SRT_BOUNDS, SRT_READ, SRT_PAIRING"""
    th = th or {}; out = []
    try:
        cues, probs = parse_srt(text)
    except Exception as e:
        return [("FAIL", "SRT_SYNTAX", f"{label}: cannot parse ({e})", None)], []
    for sev, msg, _ in probs: out.append((sev, "SRT_SYNTAX", f"{label}: {msg}", None))
    if not cues:
        out.append(("FAIL", "SRT_SYNTAX", f"{label}: no cues", None)); return out, cues
    nums = [c["index"] for c in cues if c["index"] is not None]
    if nums and nums != list(range(nums[0], nums[0] + len(nums))) and len(tracks(cues)) < 2:
        out.append(("WARN", "SRT_SYNTAX", f"{label}: cue numbers are not consecutive", None))
    for c in cues:
        t = (c["start"], c["end"])
        if not c["text"]: out.append(("WARN", "SRT_SYNTAX", f"{label} cue {c['index'] or c['i'] + 1}: empty text", t))
        if c["end"] <= c["start"]:
            out.append(("FAIL", "SRT_TIMING", f"{label} cue {c['index'] or c['i'] + 1}: end {c['end']:.3f}s is not after start {c['start']:.3f}s", t)); continue
        d = c["end"] - c["start"]
        if d < th.get("min_cue_s", .3): out.append(("WARN", "SRT_READ", f"{label} cue {c['index'] or c['i'] + 1}: on screen only {d:.2f}s", t))
        if d > th.get("max_cue_s", 10): out.append(("WARN", "SRT_READ", f"{label} cue {c['index'] or c['i'] + 1}: on screen {d:.1f}s (very long)", t))
        n_cjk = sum(1 for ch in c["text"] if cjk(ch)); n_lat = len(re.sub(r"\s", "", "".join(ch for ch in c["text"] if not cjk(ch))))
        if n_cjk / d > th.get("max_cps_cjk", 11) or n_lat / d > th.get("max_cps_latin", 25):
            out.append(("WARN", "SRT_READ", f"{label} cue {c['index'] or c['i'] + 1}: reading speed too high ({max(n_cjk, n_lat) / d:.0f} chars/s)", t))
        if duration is not None:
            if c["start"] >= duration:
                out.append(("FAIL", "SRT_BOUNDS", f"{label} cue {c['index'] or c['i'] + 1}: starts at {c['start']:.2f}s, after the video ends ({duration:.2f}s)", t))
            elif c["end"] > duration + th.get("end_tolerance_s", .05):
                out.append(("WARN", "SRT_BOUNDS", f"{label} cue {c['index'] or c['i'] + 1}: ends {c['end'] - duration:.2f}s after the video ends", t))
    tol = th.get("overlap_tolerance_s", .05)
    for name, tr in tracks(cues).items():
        for a, b in zip(tr, tr[1:]):
            if b["start"] < a["start"] - 1e-6:
                out.append(("FAIL", "SRT_ORDER", f"{label} [{name}] cue {b['index'] or b['i'] + 1} starts before the previous cue ({b['start']:.2f}s < {a['start']:.2f}s)", (b["start"], a["start"])))
            elif b["start"] < a["end"] - tol:
                out.append(("WARN", "SRT_ORDER", f"{label} [{name}] cues {a['index'] or a['i'] + 1} and {b['index'] or b['i'] + 1} overlap by {a['end'] - b['start']:.2f}s (two captions at once)", (b["start"], a["end"])))
    tr = tracks(cues)
    if "cn" in tr and "en" in tr:   # bilingual: every Chinese cue should have an English partner (captions.py pairs by overlap)
        ov = lambda x, y: max(0, min(x["end"], y["end"]) - max(x["start"], y["start"]))
        lone = [c for c in tr["cn"] if not any(ov(c, e) >= .5 * min(c["end"] - c["start"], e["end"] - e["start"]) for e in tr["en"])]
        for c in lone[:10]:
            out.append(("WARN", "SRT_PAIRING", f"{label}: Chinese cue {c['index'] or c['i'] + 1} has no English cue with matching timing", (c["start"], c["end"])))
    return out, cues


def parse_ass(text):
    """Dialogue events -> [{start, end, style, text, pos}] (pos = explicit \\pos(x,y) if any) and the script's PlayRes."""
    play, ev, fmt = {}, [], None
    for ln in text.replace("\r\n", "\n").split("\n"):
        if ln.startswith("PlayResX:"): play["x"] = int(ln.split(":")[1])
        if ln.startswith("PlayResY:"): play["y"] = int(ln.split(":")[1])
        if ln.startswith("Format:") and fmt is None and "Start" in ln: fmt = [f.strip() for f in ln[7:].split(",")]
        if ln.startswith("Dialogue:"):
            f = ln[9:].split(",", len(fmt or range(10)) - 1)
            def tt(s): h, m, r = s.strip().split(":"); return int(h) * 3600 + int(m) * 60 + float(r)
            d = dict(zip(fmt or ["Layer", "Start", "End", "Style", "Name", "MarginL", "MarginR", "MarginV", "Effect", "Text"], f))
            txt = d.get("Text", "")
            pos = re.search(r"\\pos\(([-\d.]+),([-\d.]+)\)", txt)
            plain = re.sub(r"\{[^}]*\}", "", txt).replace("\\N", "\n").replace("\\n", "\n")
            ev.append({"start": tt(d["Start"]), "end": tt(d["End"]), "style": d.get("Style", "").strip(), "text": plain,
                       "pos": [float(pos.group(1)), float(pos.group(2))] if pos else None})
    return ev, play


def compare_srt_ass(srt_cues, ass_events, tol=.02):
    """burned captions must follow the delivered SRT: same number of events, same times (ASS has centisecond resolution)"""
    probs = []
    if len(srt_cues) != len(ass_events):
        probs.append(f"SRT has {len(srt_cues)} cues but the burned .ass has {len(ass_events)} events")
    for c, e in zip(sorted(srt_cues, key=lambda c: c["start"]), sorted(ass_events, key=lambda e: e["start"])):
        if abs(c["start"] - e["start"]) > tol + .005 or abs(c["end"] - e["end"]) > tol + .005:
            probs.append(f"cue at {c['start']:.2f}s: SRT {c['start']:.2f}–{c['end']:.2f}s vs burned {e['start']:.2f}–{e['end']:.2f}s")
    return probs
