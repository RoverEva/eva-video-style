#!/usr/bin/env python3
"""EVA Video Studio · editing planner: eva-asr transcript -> plan.json (+ plan.js for the auto section page).

The plan decides, without a human:
  1. sections: which template (T17 / T20 / T01 / T09) plays when, cut at real pauses in the speech;
  2. cards: EVA Card System JSON specs (references/cards.md) with on-screen text taken from the spoken words,
     each item landing on the time eva-asr aligned for its anchor word;
  3. a storyboard for scripts/music.py (section starts + card highlights) so music cuts follow the visuals.

Text selection: one optional LLM call (Anthropic Messages API, ANTHROPIC_API_KEY) chooses the key ideas; every
word it returns is checked against the transcript. Without a key, or if the answer fails validation, a
deterministic keyword planner is used. Either way, timing always comes from eva-asr word times.

usage: planner.py TRANSCRIPT.js OUT_DIR --duration SEC [--templates T17,T20] [--mode single|multi|auto] [--no-llm]
"""
import argparse, json, os, re, sys, urllib.request
from pathlib import Path

# launch set (approved 2026-11-08): T23, T21, T17, T02, T01 rendered by the worker; T19 needs a matte + B-roll (not yet).
# T20 / T09 stay renderable for existing projects and saved plans.
LAUNCH = ["T23", "T21", "T17", "T02", "T01"]
TEMPLATES = LAUNCH + ["T20", "T09"]
W, H, FPS = 1920, 1080, 30
# presenter windows of the auto page (saas/worker/auto/auto.js SKINS) and the card box beside each one
WIN = {"T23": (1180, 160, 620, 760), "T21": (1240, 220, 520, 640), "T02": (1260, 200, 560, 680), "T17": (150, 300, 560, 560), "T20": (130, 110, 600, 820), "T01": (1240, 150, 600, 740), "T09": (1290, 180, 520, 700)}
SIDE = {"T23": "left", "T21": "left", "T02": "left", "T17": "right", "T20": "right", "T01": "left", "T09": "left"}
CONDENSED = {"T20", "T01", "T02"}    # Anton; T23 uses Archivo Black (wide)           # Anton headline themes: narrower glyphs
ICONS = ["idea", "plan", "build", "grow", "audience", "monetize", "success", "search", "publish", "analyze", "script", "footage",
         "cut", "caption", "sound", "effects", "export", "film", "rocket", "chat", "minimal", "check", "play", "heart", "star", "code", "github"]
ICON_HINTS = {"idea": "idea think concept why insight", "plan": "plan strategy goal map", "build": "build make create tool work",
              "grow": "grow growth scale increase more", "audience": "audience people customer users community viewers", "monetize": "money price pay revenue sell earn cost",
              "success": "success win result best", "search": "search find discover research", "publish": "publish post share upload",
              "analyze": "analyze data numbers measure test", "script": "script write text story", "footage": "video footage camera record",
              "cut": "cut edit trim", "caption": "caption subtitle words", "sound": "sound music audio voice", "export": "export download deliver",
              "rocket": "launch fast start rocket speed", "chat": "talk chat message ask question", "check": "done easy simple ready check",
              "play": "play watch", "heart": "love care feel", "star": "star favorite quality", "code": "code software app ai tech", "film": "film movie"}
STOP = set("""a an the and or but if so of to in on at for with from by as is are was were be been being am i me my we our you your he she it its they
them their this that these those there here what which who whom how when where why not no yes do does did done have has had will would can could
should just very really also than then too more most much many some any all each every one two about into over after before again out up down off
like get got go going gonna wanna let lets let's okay ok yeah um uh oh well right now today thing things stuff kind sort lot lots make made way
because want know think say said see look mean actually basically literally maybe something someone everything anything""".split())


def load_transcript(p):
    s = Path(p).read_text(encoding="utf-8")
    s = s[s.index("{"): s.rindex("}") + 1]
    d = json.loads(s)
    words = []
    for seg in d["segments"]:
        last = seg["start"]
        for w in seg.get("words") or [{"w": seg["text"], "start": seg["start"], "end": seg["end"]}]:
            a = w.get("start", last); z = w.get("end", a); last = z
            words.append({"w": w["w"].strip(), "start": float(a), "end": float(z)})
    return d, words


def norm(s): return re.sub(r"[^\w']", "", s.lower())


def find_word(words, text, t_from=0.0, t_to=1e9):
    """time of the first transcript word matching `text` (one or more words) inside [t_from, t_to]."""
    q = [norm(x) for x in text.split() if norm(x)]
    if not q: return None
    for i, w in enumerate(words):
        if w["start"] < t_from - 1e-3 or w["start"] > t_to: continue
        if all(i + j < len(words) and norm(words[i + j]["w"]) == q[j] for j in range(len(q))): return w["start"]
    return None


# ───────────────────────── sections ─────────────────────────
def choose_templates(mode, templates, dur):
    templates = [t for t in (templates or []) if t in TEMPLATES] or ["T17"]
    if mode == "single": return templates[:1]
    if mode == "auto":   # AI Auto Mix: about one look per 8 s (videos are ≤ 30 s), at most four
        n = max(1, min(4, round(dur / 8)))
        return ["T17", "T23", "T01", "T21"][:n] if n > 1 else ["T17"]   # launch looks, contrasting order
    n = max(1, min(len(templates), int(dur // 5)))    # each look gets at least ~5 s
    return templates[:n]


def sections(words, dur, tpls):
    n = len(tpls); bounds = [0.0]
    gaps = [((words[i]["end"] + words[i + 1]["start"]) / 2, words[i + 1]["start"] - words[i]["end"]) for i in range(len(words) - 1)]
    for k in range(1, n):
        target = dur * k / n
        cands = [(abs(t - target) - 2.5 * g, t) for t, g in gaps if abs(t - target) < dur / (2 * n) and t > bounds[-1] + 4]
        t = min(cands)[1] if cands else target
        bounds.append(round(round(t * FPS) / FPS, 3))
    bounds.append(round(dur, 3))
    return [{"t0": bounds[i], "t1": bounds[i + 1], "template": tpls[i]} for i in range(n)]


# ───────────────────────── beats (what the cards say) ─────────────────────────
def segments_list(d):
    """Sentence-sized segments. eva-asr's VAD segments can hold several sentences (one 8 s segment for a 10 s clip), which
    leaves too few card anchors; long segments are split at sentence ends (then commas) using the aligned word times."""
    out = []
    for s in d["segments"]:
        if not s["text"].strip(): continue
        ws = [w for w in (s.get("words") or []) if "start" in w and "end" in w]
        if s["end"] - s["start"] <= 4.5 or len(ws) < 4:
            out.append({"start": s["start"], "end": s["end"], "text": s["text"].strip()}); continue
        def split(ws, marks):
            parts, cur = [], []
            for w in ws:
                cur.append(w)
                if w["w"].strip()[-1:] in marks: parts.append(cur); cur = []
            if cur: parts.append(cur)
            return parts
        pieces = []
        for p in split(ws, ".!?"):
            pieces += split(p, ",;") if p[-1]["end"] - p[0]["start"] > 4.5 and len(p) >= 6 else [p]
        out += [{"start": p[0]["start"], "end": p[-1]["end"], "text": " ".join(w["w"].strip() for w in p)} for p in pieces]
    return [dict(x, id=i) for i, x in enumerate(out)]


def llm_beats(segs, dur, model, key):
    want = max(2, min(10, round(dur / 6)))
    prompt = (f"Here is a {dur:.0f}-second talking-head transcript, one numbered segment per line.\n"
              + "\n".join(f"[{s['id']}] ({s['start']:.1f}-{s['end']:.1f}s) {s['text']}" for s in segs)
              + f"\n\nChoose about {want} on-screen cards for a motion-graphics edit. Rules: on-screen text must use the speaker's own words "
              "(short extracts, no new claims, no numbers she did not say); never two cards in the same segment; spread them out. "
              "kind: hero (one key phrase), statement (a strong claim), steps (2-4 items she lists). "
              "title: 1-3 words, max 16 characters. sub: max 5 words. items: [{title<=16 chars, sub<=30 chars}]. "
              "anchor: for each element (title, then each item) the exact spoken word where it should appear. "
              f"icon (steps items only): one of {', '.join(ICONS)}.\n"
              'Reply with JSON only: {"beats":[{"seg":0,"kind":"hero","title":"...","sub":"...","anchor":["word"],"items":[]}]}')
    body = json.dumps({"model": model, "max_tokens": 1500, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body, {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: out = json.load(r)
    txt = "".join(c.get("text", "") for c in out.get("content", []))
    return json.loads(txt[txt.index("{"): txt.rindex("}") + 1])["beats"], out.get("usage", {})


def keywords(text):
    toks = [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]+|\d+%?", text)]
    return [t for t in toks if norm(t) not in STOP and (len(t) > 3 or t[0].isdigit())]


def heuristic_beats(segs, dur, secs):
    """Deterministic fallback: windows of ~6 s inside each section (so every look gets at least one card);
    in each window the segment with the most content words becomes a card. Text = the speaker's own words."""
    beats, used = [], set()
    for sec in secs:
        n = max(1, round((sec["t1"] - sec["t0"]) / 6.5)); step = (sec["t1"] - sec["t0"]) / n
        for k in range(n):
            a, z = sec["t0"] + k * step, sec["t0"] + (k + 1) * step
            cands = [s for s in segs if a - .5 <= s["start"] < z and s["id"] not in used and s["end"] - s["start"] >= 1.2 and s["start"] > sec["t0"] + .3]
            if not cands: continue
            s = max(cands, key=lambda s: (len(set(map(str.lower, keywords(s["text"])))), -s["start"]))
            kw = keywords(s["text"])
            if not kw: continue
            used.add(s["id"])
            parts = [p.strip(" .!?") for p in re.split(r",|;| and | then ", s["text"]) if keywords(p)]
            if len(parts) >= 3:
                items = [{"title": max(keywords(p), key=len), "sub": clip(p, 30)} for p in parts[:4]]
                if len(set(i["title"].lower() for i in items)) == len(items):
                    beats.append({"seg": s["id"], "kind": "steps", "title": "", "sub": "", "anchor": [i["title"] for i in items], "items": items}); continue
            title = max(kw, key=len)
            kind = "statement" if len(beats) % 3 == 2 else "hero"
            beats.append({"seg": s["id"], "kind": kind, "title": title, "sub": clip(s["text"].rstrip(".!?"), 34), "anchor": [title], "items": []})
    return beats


# ───────────────────────── cards ─────────────────────────
def box_for(tpl):
    x, y, w, h = WIN[tpl]; m = 70
    if SIDE[tpl] == "right": bx = x + w + m; return (bx, 90, W - bx - m, 780)
    return (90, 90, x - 90 - m, 780)


def clip(s, n): s = re.sub(r"\s+", " ", (s or "").strip()); return s if len(s) <= n else s[:n].rsplit(" ", 1)[0]


def to_card(i, b, segs, words, secs):
    seg = next((s for s in segs if s["id"] == b.get("seg")), None)
    if not seg: return None, "unknown segment"
    sec = next(k for k, s in enumerate(secs) if s["t0"] <= seg["start"] < s["t1"] or k == len(secs) - 1)
    tpl = secs[sec]["template"]; bx, by, bw, bh = box_for(tpl)
    lo, hi = seg["start"] - .05, seg["end"] + .05
    kind = b.get("kind") if b.get("kind") in ("hero", "statement", "steps") else "hero"
    anchors = [a for a in (b.get("anchor") or []) if isinstance(a, str)]
    times = [find_word(words, a, lo, hi) for a in anchors]
    t0 = next((t for t in times if t is not None), seg["start"] + .1)
    if kind == "steps":
        items = [{"title": clip(it.get("title"), 16).upper(), "sub": clip(it.get("sub"), 30),
                  "icon": it.get("icon") if it.get("icon") in ICONS else pick_icon(it.get("title", "") + " " + it.get("sub", ""))}
                 for it in (b.get("items") or [])[:4] if clip(it.get("title"), 16)]
        if len(items) < 2: return None, "steps needs 2+ items"
        ts = (times + [None] * len(items))[:len(items)]
        ts = [t if t is not None else None for t in ts]
        for j in range(len(ts)):
            if ts[j] is None or (j and ts[j] <= ts[j - 1]): ts[j] = (ts[j - 1] + .45) if j else t0
        ih = min(160, (bh - 18 * (len(items) - 1)) / len(items))
        spec = {"id": f"card_{i:03}", "type": "layout", "layout": "stack", "content": {"items": items},
                "position": {"x": bx / W, "y": by / H, "w": bw / W, "h": (ih * len(items) + 18 * (len(items) - 1)) / H},
                "animation": {"times": [round(t, 3) for t in ts]}}
        t_in, last = ts[0], ts[-1]
    else:
        title = clip(b.get("title"), 16).upper(); sub = clip(b.get("sub"), 34)
        if not title: return None, "empty title"
        maxlen = max(len(title), 1)
        k = .5 if tpl in CONDENSED else .66
        # headline: k*size per char; sub line sits at x=.5*size with .32*size type (see EC.HeroCard)
        size = int(min(150, .92 * bw / (k * maxlen + .12), .92 * bw / (.5 + .32 * k * len(sub)) if sub else 150))
        size = max(70, size)
        content = {"words": [title], "sub": sub.upper() if tpl in CONDENSED else sub}
        if kind == "statement": content = {"script": "", "words": [title], "sub": content["sub"]}
        spec = {"id": f"card_{i:03}", "type": "layout", "layout": "hero" if kind == "hero" else "statement", "content": content,
                "position": {"x": bx / W, "y": by / H, "w": bw / W, "h": bh / H, "size": size},
                "animation": {"times": [round(t0 + .2 * j, 3) for j in range(3)]}}
        cap = min(t0 + 6.5, secs[sec]["t1"] - .1)
        if cap - t0 < 2.4:   # keyword late in a short section: show the card up to 1 s before its sentence so it stays ≥ 2.4 s
            t0 = max(secs[sec]["t0"] + .35, min(t0, cap - 2.4), seg["start"] - 1.0)
            spec["animation"]["times"] = [round(t0 + .2 * j, 3) for j in range(3)]
        t_in, last = t0, t0 + .4
    t_out = min(max(seg["end"] + .4, last + 2.2, t_in + 2.5), t_in + 6.5, secs[sec]["t1"] - .1)
    return {"spec": spec, "t_in": round(t_in, 3), "t_out": round(t_out, 3), "section": sec, "kind": kind}, None


def pick_icon(text):
    ws = set(norm(w) for w in text.split())
    best = max(ICON_HINTS, key=lambda k: len(ws & set(ICON_HINTS[k].split())))
    return best if ws & set(ICON_HINTS[best].split()) else "check"


def build_cards(beats, segs, words, secs):
    cards, rejected = [], []
    for b in sorted(beats, key=lambda b: b.get("seg", 0)):
        c, why = to_card(len(cards) + 1, b, segs, words, secs)
        if not c: rejected.append({"beat": b, "why": why}); continue
        if cards and c["t_in"] < cards[-1]["t_out"] + .4:        # one card at a time
            if c["section"] == cards[-1]["section"] and c["t_in"] > cards[-1]["t_in"] + 1.5: cards[-1]["t_out"] = round(c["t_in"] - .45, 3)
            else: rejected.append({"beat": b, "why": "overlaps previous card"}); continue
        if c["t_in"] < secs[c["section"]]["t0"] + .3: rejected.append({"beat": b, "why": "too close to a section cut"}); continue
        if c["t_out"] - c["t_in"] < 2.0: rejected.append({"beat": b, "why": "less than 2 s on screen"}); continue
        cards.append(c)
    return cards, rejected


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript"); ap.add_argument("out_dir"); ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--templates", default="T17"); ap.add_argument("--mode", choices=["single", "multi", "auto"], default="single")
    ap.add_argument("--face", help="face calibration JSON {x,y,h}"); ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--model", default=os.environ.get("EVA_PLANNER_MODEL", "claude-haiku-5-5"))
    a = ap.parse_args(argv)
    d, words = load_transcript(a.transcript)
    if not words: print("planner: transcript has no words", file=sys.stderr); return 5
    dur = a.duration
    secs = sections(words, dur, choose_templates(a.mode, a.templates.split(","), dur))
    segs = segments_list(d)
    source, usage, beats = "heuristic", None, None
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key and not a.no_llm:
        try:
            beats, usage = llm_beats(segs, dur, a.model, key); source = "llm:" + a.model
        except Exception as e:  # never fail a paid job because of the planner model
            print(f"planner: LLM unavailable ({type(e).__name__}: {e}); using the keyword planner", file=sys.stderr)
    cards, rejected = build_cards(beats, segs, words, secs) if beats else ([], [])
    if len(cards) < max(1, round(dur / 15)):   # too little survived validation
        source += "+heuristic" if beats else ""
        cards, rejected2 = build_cards(heuristic_beats(segs, dur, secs), segs, words, secs); rejected += rejected2
    face = json.loads(Path(a.face).read_text()) if a.face else None
    for sec in secs: sec["box"] = list(box_for(sec["template"]))   # card block: 9:16 pages scale it into the top zone (auto.js)
    plan = {"version": 1, "end": round(dur, 3), "evaDir": "../media/eva", "face": face, "sections": secs, "cards": cards,
            "planner": {"source": source, "usage": usage, "rejected": rejected}}
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    (out / "plan.js").write_text("window.EVA_PLAN = " + json.dumps(plan, ensure_ascii=False) + ";\n")
    sb = {"sections": [{"start": s["t0"], "template": s["template"]} for s in secs], "highlights": [c["t_in"] for c in cards]}
    (out / "storyboard.json").write_text(json.dumps(sb))
    print(f"planner: {len(secs)} section(s) {[s['template'] for s in secs]}, {len(cards)} card(s), source={source}, rejected={len(rejected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
