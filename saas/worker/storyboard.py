#!/usr/bin/env python3
"""EVA Video Studio · AI storyboard: Claude Opus 5.5 plans the edit, EVA templates render it.

    Upload → ASR → storyboard (this file: ONE Claude Opus 5.5 call) → validator → plan.json → EVA renderer → visual QA

Claude reads the whole transcript (with word times), the person's optional instructions, the selected templates and the
REGISTRY of what the renderer can really draw, and returns a scene-by-scene storyboard through a forced tool call
(JSON schema). validate() checks every beat against the registry and the transcript; on errors Claude gets ONE retry with
the exact list. If it still fails — or the API is unreachable — the job fails (no heuristic plan, no raw footage), and the
worker releases the free preview / credits as for any failed render. HD export reuses the saved plan.json (no second call).

Only the transcript TEXT and word times leave our servers (no video, no images, no account data).
Model: claude-opus-5-5 only (EVA_STORYBOARD_MODEL may not name another family).
"""
import json, os, re, time, urllib.error, urllib.request
from pathlib import Path

MODEL = "claude-opus-5-5"
API = "https://api.anthropic.com/v1/messages"
PRICE = {"in": 4.00, "out": 20.00, "cache_read": 0.20, "cache_write": 5.00}   # USD per 1M tokens (Opus 5.5, Nov 2026 — confirm on Anthropic's price page)


class StoryboardError(RuntimeError):
    """info: machine-readable details for logs/diagnosis — HTTP status, Anthropic error type/message, usage, attempts."""
    def __init__(self, msg, **info): super().__init__(msg); self.info = info


# ───────────────────────── what the renderer can draw (single source of truth) ─────────────────────────
ICONS = ["idea", "plan", "build", "grow", "audience", "monetize", "success", "search", "publish", "analyze", "script", "footage",
         "cut", "caption", "sound", "effects", "export", "film", "rocket", "chat", "minimal", "check", "play", "heart", "star", "code", "github"]
S = lambda n: {"type": "string", "maxLength": n}
ITEM = {"type": "object", "properties": {"title": S(16), "sub": S(30), "icon": {"type": "string", "enum": ICONS}}, "required": ["title"], "additionalProperties": False}
REGISTRY = {
    "hero":      {"layout": "hero", "beats": 1, "content": {"title": S(16), "sub": S(40)}, "required": ["title"],
                  "use": "one strong idea, a hook or a key phrase; huge headline beside the speaker"},
    "statement": {"layout": "statement", "beats": 1, "content": {"title": S(16), "sub": S(40)}, "required": ["title"],
                  "use": "a bold claim or conclusion, with drawn arrows; good for the ending or a turning point"},
    "steps":     {"layout": "stack", "beats": "items", "content": {"items": {"type": "array", "items": ITEM, "minItems": 2, "maxItems": 4}}, "required": ["items"],
                  "use": "a list of 2–4 points or steps the speaker names one after another; each card appears on its word"},
    "process":   {"layout": "process", "beats": "items", "content": {"kicker": S(24), "items": {"type": "array", "items": ITEM, "minItems": 2, "maxItems": 5}}, "required": ["items"],
                  "use": "HOW something works: an animated pipeline where stages light up in order and data flows along the arrows "
                         "(Input → Model → Output, idea → script → video, cause → effect). Prefer this over plain cards for any explanation"},
    "compare":   {"layout": "compare", "beats": 2, "content": {"left": {"type": "object", "properties": {"title": S(18), "points": {"type": "array", "items": S(34), "maxItems": 3}}, "required": ["title"], "additionalProperties": False},
                                                              "right": {"type": "object", "properties": {"title": S(18), "points": {"type": "array", "items": S(34), "maxItems": 3}}, "required": ["title"], "additionalProperties": False}},
                  "required": ["left", "right"], "use": "before vs after, old way vs new way, A vs B; two solid panels revealed in turn with a VS chip"},
    "checklist": {"layout": "checklist", "beats": "items", "content": {"items": {"type": "array", "items": ITEM, "minItems": 2, "maxItems": 5}}, "required": ["items"],
                  "use": "things that are done / included / required; check marks stamp on the spoken words"},
    "stat":      {"layout": "stat", "beats": 1, "content": {"value": {"type": "number"}, "prefix": S(3), "suffix": S(6), "label": S(36)}, "required": ["value", "label"],
                  "use": "ONLY a number the speaker actually says; it counts up with its label"},
    "orbit":     {"layout": "orbit", "beats": "items", "content": {"items": {"type": "array", "items": ITEM, "minItems": 3, "maxItems": 6}}, "required": ["items"],
                  "use": "several related things around one idea (tools, channels, audiences) circling the speaker"},
    "journey":   {"layout": "journey", "beats": "items", "content": {"items": {"type": "array", "items": ITEM, "minItems": 3, "maxItems": 6}}, "required": ["items"],
                  "use": "a timeline or journey with milestones along a curved path"},
    "feature":   {"layout": "feature", "beats": 1, "content": {"title": S(18), "body": S(90), "icon": {"type": "string", "enum": ICONS}}, "required": ["title", "body"],
                  "use": "explain ONE concept in a little more detail: large card with title, one-sentence body and an icon"},
    "bars":      {"layout": "bars", "beats": "items", "content": {"items": {"type": "array", "minItems": 2, "maxItems": 5, "items": {"type": "object", "additionalProperties": False, "required": ["label", "level"],
                  "properties": {"label": S(16), "level": {"type": "string", "enum": ["low", "medium", "high", "full"]}}}}}, "required": ["items"],
                  "use": "an animated bar chart comparing amounts the speaker contrasts (more/less, faster/slower). Relative levels only, "
                         "no numbers unless spoken; mark illustrative = true when the sizes are conceptual"},
    "network":   {"layout": "network", "beats": "items", "content": {"center": S(16), "icon": {"type": "string", "enum": ICONS}, "items": {"type": "array", "items": ITEM, "minItems": 3, "maxItems": 6}}, "required": ["center", "items"],
                  "use": "a hub-and-spoke network: one central idea connected to the things it links or powers, with data pulses along the links"},
    "hook":      {"layout": "hook", "beats": "words", "content": {"kicker": S(14), "words": {"type": "array", "items": S(12), "minItems": 1, "maxItems": 4}}, "required": ["words"],
                  "use": "the opening hook or a signature punch line: 1–4 giant words popping in on the spoken words; best in the first 3 s"},
    "presenter": {"layout": None, "beats": 0, "content": {}, "required": [],
                  "use": "speaker alone, full frame, for a personal or emotional moment; at most 2.5 s each and rarely"},
}
LIMITS = {"min_beat_s": 1.6, "max_card_s": 8.0, "max_presenter_s": 2.5, "max_gap_s": 0.6, "max_presenter_share": .2, "min_template_s": 3.0}


def registry_for_prompt():
    return {k: {"use": v["use"], "content": v["content"], "required": v["required"],
                "timed_elements": v["beats"] if isinstance(v["beats"], int) else f"one per entry of {v['beats']}"} for k, v in REGISTRY.items()}


def tool_schema(templates):
    beat = {"type": "object", "additionalProperties": False, "required": ["start", "end", "template", "component", "spoken", "anchor_words", "content", "illustrative", "why"],
            "properties": {"start": {"type": "number"}, "end": {"type": "number"}, "template": {"type": "string", "enum": templates},
                           "component": {"type": "string", "enum": list(REGISTRY)}, "spoken": {"type": "string", "description": "the exact words spoken during this beat"},
                           "anchor_words": {"type": "array", "items": {"type": "string"}, "description": "one spoken word per timed element, in order, copied from the transcript"},
                           "content": {"type": "object"}, "illustrative": {"type": "boolean"}, "why": S(160)}}
    return {"name": "submit_storyboard", "description": "Submit the scene-by-scene EVA storyboard.",
            "input_schema": {"type": "object", "additionalProperties": False, "required": ["beats"], "properties": {"beats": {"type": "array", "items": beat, "minItems": 1}}}}


SYSTEM = """You are the creative director and editor of EVA Video Studio. You turn a talking-head clip into a premium short
video: EVA templates provide the look (colours, type, motion language, face-safe layouts); YOU decide the edit.

Rules
- Read the whole transcript for MEANING. Every beat illustrates what is being said at that moment, timed to the words.
- Explain, don't decorate: when the speaker explains how something works, use `process` (animated stages + flowing data),
  for A vs B use `compare`, for named steps `steps`, for included/required things `checklist`, for a spoken number `stat`,
  for more/less contrasts `bars`, for one idea linking many things `network`, for the opening line or a punch line `hook`.
  Rhythm: change the visual every 1.5–3 s where the speech allows (a multi-item component counts as one change per item).
  Use `hero`/`statement` for hooks, claims and endings. Vary components; never three identical components in a row.
- Rhythm: a new beat every 2–5 s, cut on phrase boundaries. Beats are contiguous: the next beat starts where the previous
  ends (gaps ≤ 0.6 s). The first beat starts at 0, the last ends at the clip end.
- Templates: use EVERY selected template for at least 3 s, each as one continuous stretch (a template change is a scene
  change). Order them so the looks contrast and suit the content.
- Words on screen: short (titles ≤ 16 characters), taken from or faithful to the speech. Never invent facts, numbers,
  brands or claims. A number may only appear if the speaker said it. Conceptual diagrams the speaker did not literally
  describe must set illustrative = true.
- anchor_words: for each timed element (see the registry), copy ONE word from the transcript spoken inside the beat, in
  order — that element appears exactly when the word is spoken.
- `presenter` (speaker alone) only for a short personal moment, ≤ 2.5 s, at most 20 % of the video.
- The speech is never cut or changed. Output only through the submit_storyboard tool."""


def transcript_text(words, segs):
    lines = [f"[{s['start']:.2f}–{s['end']:.2f}] {s['text']}" for s in segs]
    wl = " ".join(f"{w['w'].strip()}@{w['start']:.2f}" for w in words)
    return "Sentences:\n" + "\n".join(lines) + "\n\nWord times (word@seconds):\n" + wl


def _post(key, body, timeout):
    req = urllib.request.Request(API, json.dumps(body).encode(), {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for n in range(4):   # transient API states (rate limit, overload, 5xx): back off and retry; anything else fails at once
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r: j = json.loads(r.read()); break
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 504, 529) and n < 3:
                time.sleep(min(60, float(e.headers.get("retry-after") or 0) or 5 * 2 ** n)); continue
            try: err = json.loads(body).get("error") or {}
            except Exception: err = {}
            raise StoryboardError(f"Anthropic API HTTP {e.code}: {body}", http_status=e.code, api_error_type=err.get("type"),
                                  api_error_message=err.get("message") or body[:200], request_id=e.headers.get("request-id"))
        except Exception as e:
            if n < 3 and isinstance(e, (TimeoutError, urllib.error.URLError)): time.sleep(5 * 2 ** n); continue
            raise StoryboardError(f"Anthropic API unreachable: {type(e).__name__}", http_status=None, api_error_type=type(e).__name__)
    return j


def call_claude(key, system, user, tool, prior=None, timeout=180):
    """Opus 5.5 does not accept a forced tool_choice ("tool"/"any" → HTTP 400), so the tool is offered with "auto" and the
    system prompt requires it. If a reply has no tool call, Claude is asked once more to submit through the tool."""
    msgs = [{"role": "user", "content": user}] + (prior or []); t = time.time(); usages = []
    for nudge in (0, 1):
        body = {"model": MODEL, "max_tokens": 8000, "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                "tools": [tool], "tool_choice": {"type": "auto"}, "messages": msgs}
        j = _post(key, body, timeout); usages.append(j.get("usage", {}))
        use = next((c for c in j.get("content", []) if c.get("type") == "tool_use" and c.get("name") == tool["name"]), None)
        if use: break
        msgs = msgs + [{"role": "assistant", "content": j.get("content") or [{"type": "text", "text": "(no output)"}]},
                       {"role": "user", "content": f"Submit the complete storyboard now by calling the {tool['name']} tool. No other text."}]
    if not use: raise StoryboardError("Claude returned no storyboard (no tool call after a reminder)", http_status=200, api_error_type="no_tool_call", model=j.get("model"))
    usage = {k: sum((u.get(k) or 0) for u in usages) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
    if nudge: j = dict(j, content=j["content"])   # the retry history (prior) continues from the final reply
    return use, usage, round(time.time() - t, 1), j


def cost(usages):
    u = {k: sum(x.get(k, 0) or 0 for x in usages) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
    usd = (u["input_tokens"] * PRICE["in"] + u["output_tokens"] * PRICE["out"] + u["cache_read_input_tokens"] * PRICE["cache_read"]
           + u["cache_creation_input_tokens"] * PRICE["cache_write"]) / 1e6
    return dict(u, usd=round(usd, 4))


# ───────────────────────── validation ─────────────────────────
def _norm(s): return re.sub(r"[^\w']", "", (s or "").lower())
NUMWORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
            "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "hundred": 100, "thousand": 1000, "million": 1000000}


def spoken_numbers(words):
    out = set()
    for w in words:
        t = _norm(w["w"]).replace(",", "")
        if re.fullmatch(r"\d+(\.\d+)?", t): out.add(float(t))
        if t in NUMWORDS: out.add(float(NUMWORDS[t]))
    return out


def _schema_errors(val, sch, path):
    e = []
    if sch.get("type") == "string":
        if not isinstance(val, str): return [f"{path} must be text"]
        if len(val) > sch.get("maxLength", 999): e.append(f"{path} is {len(val)} characters (max {sch['maxLength']})")
        if "enum" in sch and val not in sch["enum"]: e.append(f"{path} '{val}' is not one of {sch['enum']}")
    elif sch.get("type") == "number":
        if not isinstance(val, (int, float)): e.append(f"{path} must be a number")
    elif sch.get("type") == "array":
        if not isinstance(val, list): return [f"{path} must be a list"]
        if len(val) < sch.get("minItems", 0) or len(val) > sch.get("maxItems", 99): e.append(f"{path} needs {sch.get('minItems', 0)}–{sch.get('maxItems')} items (has {len(val)})")
        for i, v in enumerate(val): e += _schema_errors(v, sch["items"], f"{path}[{i}]")
    elif sch.get("type") == "object":
        if not isinstance(val, dict): return [f"{path} must be an object"]
        for r in sch.get("required", []):
            if r not in val: e.append(f"{path}.{r} is required")
        for k, v in val.items():
            if k not in sch["properties"]: e.append(f"{path}.{k} is not a supported field")
            else: e += _schema_errors(v, sch["properties"][k], f"{path}.{k}")
    return e


def find_word(words, text, lo, hi):
    n = _norm(text)
    for w in words:
        if lo - .05 <= w["start"] <= hi + .05 and _norm(w["w"]) == n: return w["start"]
    return None


def min_template_s(dur, templates):   # about 3 s each; a clip that is exactly long enough (15.07 s, 5 templates) gets 3 % slack
    return round(min(LIMITS["min_template_s"], .97 * dur / max(1, len(templates))), 2)


def validate(sb, words, dur, templates):
    errs, beats = [], sb.get("beats") or []
    spoken = " ".join(_norm(w["w"]) for w in words); nums = spoken_numbers(words)
    if not beats: return ["no beats"]
    if abs(beats[0]["start"]) > .3: errs.append(f"the first beat must start at 0 (starts at {beats[0]['start']})")
    if abs(beats[-1]["end"] - dur) > .5: errs.append(f"the last beat must end at {dur:.2f} (ends at {beats[-1]['end']})")
    for i, b in enumerate(beats):
        p = f"beat {i + 1} ({b.get('start')}–{b.get('end')} s, {b.get('component')})"; reg = REGISTRY.get(b.get("component"))
        if not reg: errs.append(f"{p}: unknown component"); continue
        if b.get("template") not in templates: errs.append(f"{p}: template {b.get('template')} was not selected")
        d = b["end"] - b["start"]
        if d < LIMITS["min_beat_s"]: errs.append(f"{p}: {d:.2f} s is shorter than {LIMITS['min_beat_s']} s")
        if reg["layout"] and d > LIMITS["max_card_s"]: errs.append(f"{p}: {d:.2f} s is longer than {LIMITS['max_card_s']} s; split it")
        if not reg["layout"] and d > LIMITS["max_presenter_s"] + .05: errs.append(f"{p}: presenter beats are at most {LIMITS['max_presenter_s']} s")
        if i and b["start"] - beats[i - 1]["end"] > LIMITS["max_gap_s"]: errs.append(f"{p}: gap of {b['start'] - beats[i - 1]['end']:.2f} s after the previous beat (max {LIMITS['max_gap_s']})")
        if i and b["start"] < beats[i - 1]["end"] - .05: errs.append(f"{p}: overlaps the previous beat")
        errs += _schema_errors(b.get("content") or {}, {"type": "object", "properties": reg["content"], "required": reg["required"]}, f"{p} content")
        need = reg["beats"] if isinstance(reg["beats"], int) else len((b.get("content") or {}).get(reg["beats"]) or [])
        aw = b.get("anchor_words") or []
        if len(aw) != need: errs.append(f"{p}: needs exactly {need} anchor_words (one per timed element), got {len(aw)}")
        for w in aw:
            if find_word(words, w, b["start"], b["end"]) is None: errs.append(f"{p}: anchor word '{w}' is not spoken between {b['start']} and {b['end']} s")
        text = json.dumps(b.get("content") or {}, ensure_ascii=False)
        for n in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text):
            if float(n) not in nums: errs.append(f"{p}: the number {n} is not spoken in the clip")
        if b.get("component") == "stat" and float((b.get("content") or {}).get("value", -1)) not in nums: errs.append(f"{p}: stat value must be a number the speaker says")
        kws = [_norm(x) for x in re.findall(r"[A-Za-z']{4,}", text) if _norm(x) not in ("title", "items", "points", "left", "right", "label", "kicker", "body", "icon", "prefix", "suffix", "value", "level", "center", "words", "full", "high", "medium") + tuple(ICONS)]
        if kws and not b.get("illustrative") and sum(1 for k in kws if k in spoken) / len(kws) < .35:
            errs.append(f"{p}: on-screen words are mostly not from the speech; use the speaker's words or set illustrative = true")
    used = {}
    for b in beats: used[b.get("template")] = used.get(b.get("template"), 0) + b["end"] - b["start"]
    for t in templates:
        if used.get(t, 0) < min_template_s(dur, templates) - .05: errs.append(f"template {t} is used for {used.get(t, 0):.2f} s (needs ≥ {min_template_s(dur, templates):.2f} s)")
    runs = [b["template"] for i, b in enumerate(beats) if not i or b["template"] != beats[i - 1]["template"]]
    if len(runs) != len(set(runs)): errs.append(f"each template must be one continuous stretch (order used: {runs})")
    pres = sum(b["end"] - b["start"] for b in beats if b.get("component") == "presenter")
    if pres > LIMITS["max_presenter_share"] * dur: errs.append(f"presenter-only beats take {pres:.1f} s (> {LIMITS['max_presenter_share']:.0%} of the clip)")
    return errs


# ───────────────────────── storyboard → plan.json (what auto.js renders) ─────────────────────────
W, H = 1920, 1080


def to_plan(sb, words, dur, box_for):
    beats = sb["beats"]; secs = []
    for b in beats:
        if not secs or secs[-1]["template"] != b["template"]: secs.append({"t0": 0.0 if not secs else round(b["start"], 3), "t1": None, "template": b["template"]})
    for i, s in enumerate(secs): s["t1"] = round(secs[i + 1]["t0"], 3) if i + 1 < len(secs) else round(dur, 3)
    cards = []
    for b in beats:
        reg = REGISTRY[b["component"]]
        if not reg["layout"]: continue
        k = next(i for i, s in enumerate(secs) if s["template"] == b["template"])
        bx, by, bw, bh = box_for(b["template"]); c = dict(b["content"])
        times = [find_word(words, w, b["start"], b["end"]) for w in b["anchor_words"]] or [b["start"] + .1]
        times = [max(b["start"] + .05, t) for t in times]
        for j in range(1, len(times)): times[j] = max(times[j], times[j - 1] + .35)
        if reg["layout"] in ("hero", "statement"):
            title = c["title"].upper(); size = int(max(70, min(150, .92 * bw / (.62 * max(len(title), 1) + .12))))
            content = {"words": [title], "sub": c.get("sub", "")} if reg["layout"] == "hero" else {"script": "", "words": [title], "sub": c.get("sub", "")}
            times = [round(times[0] + .2 * j, 3) for j in range(3)]
            pos = {"x": bx / W, "y": by / H, "w": bw / W, "h": bh / H, "size": size}
        else:
            content = c; pos = {"x": bx / W, "y": by / H, "w": bw / W, "h": bh / H}
            if reg["layout"] == "stack": content = {"items": [dict(it, title=it["title"].upper()) for it in c["items"]]}
            if reg["layout"] == "bars": content = {"items": [{"label": it["label"], "level": {"low": .3, "medium": .55, "high": .8, "full": 1.0}[it["level"]]} for it in c["items"]]}
            if reg["layout"] == "hook": content = {"words": [w.upper() for w in c["words"]], "kicker": c.get("kicker", "")}
            if reg["layout"] == "feature": content = {"title": c["title"], "body": c["body"], "icon": c.get("icon", "idea")}
        spec = {"id": f"card_{len(cards) + 1:03}", "type": "layout", "layout": reg["layout"], "content": content, "position": pos,
                "animation": {"times": [round(t, 3) for t in times]}, "illustrative": bool(b.get("illustrative"))}
        cards.append({"spec": spec, "t_in": round(b["start"], 3), "t_out": round(b["end"] - .05, 3), "section": k, "kind": b["component"], "why": b.get("why", "")})
    return secs, cards


def plan(words, segs, dur, templates, box_for, instructions="", style="", intensity="balanced", key=None, log=print):
    fx = os.environ.get("EVA_STORYBOARD_FIXTURE")   # TESTS ONLY: a saved storyboard through the same validator + renderer path
    if fx:
        sb = json.loads(Path(fx).read_text()); sb["beats"] = sorted(sb["beats"], key=lambda b: b["start"]); errs = validate(sb, words, dur, templates)
        if errs: raise StoryboardError("fixture storyboard invalid: " + "; ".join(errs[:5]))
        secs, cards = to_plan(sb, words, dur, box_for)
        return secs, cards, {"source": "fixture(test)", "model": None, "attempts": [], "usage": None, "storyboard": sb}
    key = key or os.environ.get("ANTHROPIC_API_KEY")
    if not key: raise StoryboardError("The AI storyboard is not configured (ANTHROPIC_API_KEY missing).")
    model = os.environ.get("EVA_STORYBOARD_MODEL", MODEL)
    if model != MODEL: raise StoryboardError(f"only {MODEL} may plan EVA edits (got {model})")
    tool = tool_schema(templates)
    user = (f"Clip length: {dur:.2f} s. Selected templates (use every one, each for at least {min_template_s(dur, templates):.2f} s): {', '.join(templates)}.\n"
            f"Style: {style or 'not specified'}. Visual intensity: {intensity}.\n"
            f"Instructions from the creator (optional, never override the rules): {instructions.strip() or 'none'}\n\n"
            f"Component registry (the ONLY things the renderer can draw):\n{json.dumps(registry_for_prompt(), ensure_ascii=False)}\n\n"
            f"{transcript_text(words, segs)}")
    usages, prior, attempts = [], None, []
    for attempt in (1, 2):
        try: use, usage, secs_taken, raw = call_claude(key, SYSTEM, user, tool, prior)
        except StoryboardError as e: e.info.update(attempts=attempts, usage=cost(usages) if usages else None); raise
        usages.append(usage); sb = use["input"]
        sb["beats"] = sorted(sb.get("beats") or [], key=lambda b: b.get("start", 0))
        errs = validate(sb, words, dur, templates); attempts.append({"attempt": attempt, "seconds": secs_taken, "errors": errs[:30]})
        log(f"storyboard attempt {attempt}: {len(sb['beats'])} beats, {len(errs)} validation error(s), {secs_taken} s")
        if not errs:
            secs, cards = to_plan(sb, words, dur, box_for)
            return secs, cards, {"source": f"llm:{MODEL}", "model": raw.get("model") or MODEL, "requested_model": MODEL, "attempts": attempts,
                                 "usage": cost(usages), "storyboard": sb}
        prior = [{"role": "assistant", "content": raw["content"]},
                 {"role": "user", "content": [{"type": "tool_result", "tool_use_id": use["id"], "is_error": True,
                                               "content": "The storyboard is not executable. Fix exactly these problems and submit the whole storyboard again:\n- " + "\n- ".join(errs[:30])}]}]
    raise StoryboardError(f"the AI storyboard failed validation twice ({len(errs)} problems, first: {errs[0]})",
                          http_status=200, api_error_type="validation", attempts=attempts, usage=cost(usages), model=raw.get("model"))
