#!/usr/bin/env python3
"""Transcript-aware local Content Planner for independently installed EVA templates.

The planner never invents display text: every title and subtitle is selected from the
user's transcript, while all timing derives from ASR or supplied-SRT word times.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from template_registry import resolve


W, H, FPS = 1920, 1080, 30
ICONS = ["idea", "plan", "build", "grow", "audience", "monetize", "success", "search", "publish", "analyze",
         "script", "footage", "cut", "caption", "sound", "effects", "export", "film", "rocket", "chat", "minimal",
         "check", "play", "heart", "star", "code", "github"]
ICON_HINTS = {"idea": "idea think concept why insight", "plan": "plan strategy goal map", "build": "build make create tool work",
              "grow": "grow growth scale increase more", "audience": "audience people customer users community viewers",
              "monetize": "money price pay revenue sell earn cost", "success": "success win result best",
              "search": "search find discover research", "publish": "publish post share upload", "analyze": "analyze data numbers measure test",
              "script": "script write text story", "footage": "video footage camera record", "cut": "cut edit trim",
              "caption": "caption subtitle words", "sound": "sound music audio voice", "export": "export download deliver",
              "rocket": "launch fast start rocket speed", "chat": "talk chat message ask question", "check": "done easy simple ready check",
              "play": "play watch", "heart": "love care feel", "star": "star favorite quality", "code": "code software app ai tech", "film": "film movie"}
STOP = set("""a an the and or but if so of to in on at for with from by as is are was were be been being am i me my we our you your he she it its they
them their this that these those there here what which who whom how when where why not no yes do does did done have has had will would can could
should just very really also than then too more most much many some any all each every one two about into over after before again out up down off
like get got go going gonna wanna let lets okay ok yeah um uh oh well right now today thing things stuff kind sort lot lots make made way
because want know think say said see look mean actually basically literally maybe something someone everything anything""".split())


def load_transcript(path):
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text[text.index("{"):text.rindex("}") + 1])
    words = []
    for segment in data.get("segments", []):
        last = float(segment["start"])
        fallback = [{"w": segment["text"], "start": segment["start"], "end": segment["end"]}]
        for word in segment.get("words") or fallback:
            start = float(word.get("start", last)); end = float(word.get("end", start)); last = end
            if str(word.get("w", "")).strip():
                words.append({"w": str(word["w"]).strip(), "start": start, "end": end})
    return data, words


def norm(value):
    return re.sub(r"[^\w']", "", value.lower())


def find_word(words, text, start=0.0, end=1e9):
    wanted = [norm(x) for x in text.split() if norm(x)]
    if not wanted:
        return None
    for i, word in enumerate(words):
        if word["start"] < start - 1e-3 or word["start"] > end:
            continue
        if all(i + j < len(words) and norm(words[i + j]["w"]) == wanted[j] for j in range(len(wanted))):
            return word["start"]
    return None


def choose_templates(mode, templates, duration):
    if mode == "single":
        return templates[:1]
    if mode == "auto":
        count = max(1, min(len(templates), round(duration / 8)))
        return templates[:count]
    count = max(1, min(len(templates), int(duration // 5)))
    return templates[:count]


def sections(words, duration, templates):
    count, bounds = len(templates), [0.0]
    gaps = [((words[i]["end"] + words[i + 1]["start"]) / 2, words[i + 1]["start"] - words[i]["end"])
            for i in range(len(words) - 1)]
    for index in range(1, count):
        target = duration * index / count
        candidates = [(abs(at - target) - 2.5 * gap, at) for at, gap in gaps
                      if abs(at - target) < duration / (2 * count) and at > bounds[-1] + 4]
        at = min(candidates)[1] if candidates else target
        bounds.append(round(round(at * FPS) / FPS, 3))
    bounds.append(round(duration, 3))
    return [{"t0": bounds[i], "t1": bounds[i + 1], "template": templates[i]} for i in range(count)]


def segment_list(data):
    result = []
    for segment in data.get("segments", []):
        if not segment.get("text", "").strip():
            continue
        words = [word for word in segment.get("words", []) if "start" in word and "end" in word]
        if segment["end"] - segment["start"] <= 4.5 or len(words) < 4:
            result.append({"start": segment["start"], "end": segment["end"], "text": segment["text"].strip()})
            continue
        sentence_pieces, current = [], []
        for word in words:
            current.append(word)
            if str(word["w"]).strip()[-1:] in ".!?。！？":
                sentence_pieces.append(current); current = []
        if current:
            sentence_pieces.append(current)
        pieces = []
        for sentence in sentence_pieces:
            if sentence[-1]["end"] - sentence[0]["start"] <= 4.5 or len(sentence) < 6:
                pieces.append(sentence); continue
            part = []
            for word in sentence:
                part.append(word)
                if str(word["w"]).strip()[-1:] in ",;，；":
                    pieces.append(part); part = []
            if part:
                pieces.append(part)
        result.extend({"start": piece[0]["start"], "end": piece[-1]["end"],
                       "text": " ".join(str(word["w"]).strip() for word in piece)} for piece in pieces)
    return [dict(segment, id=i) for i, segment in enumerate(result)]


def keywords(text):
    candidates = re.findall(r"[A-Za-z][A-Za-z'\-]+|\d+%?|[\u3400-\u9fff]{2,8}", text)
    return [token for token in candidates if norm(token) not in STOP and (len(token) > 3 or not token.isascii() or token[0].isdigit())]


def clip(value, length):
    value = re.sub(r"\s+", " ", (value or "").strip())
    if len(value) <= length:
        return value
    shortened = value[:length]
    return shortened.rsplit(" ", 1)[0] or shortened


def box_for(skin):
    window, margin = skin["window"], 70
    x, y, width, height = (window[key] for key in ("x", "y", "w", "h"))
    if skin["side"] == "right":
        box_x = x + width + margin
        return box_x, 90, W - box_x - margin, 780
    return 90, 90, x - 90 - margin, 780


def pick_icon(text):
    words = {norm(word) for word in text.split()}
    best = max(ICON_HINTS, key=lambda key: len(words & set(ICON_HINTS[key].split())))
    return best if words & set(ICON_HINTS[best].split()) else "check"


def beats_for(segments, planned_sections):
    beats, used = [], set()
    for section in planned_sections:
        count = max(1, round((section["t1"] - section["t0"]) / 6.5))
        step = (section["t1"] - section["t0"]) / count
        for index in range(count):
            start, end = section["t0"] + index * step, section["t0"] + (index + 1) * step
            choices = [segment for segment in segments if start - .5 <= segment["start"] < end and segment["id"] not in used
                       and segment["end"] - segment["start"] >= 1.2 and segment["start"] > section["t0"] + .3
                       and segment["end"] <= section["t1"] + .1]
            if not choices:
                continue
            segment = max(choices, key=lambda item: (len(set(map(str.lower, keywords(item["text"])))), -item["start"]))
            words = keywords(segment["text"])
            if not words:
                continue
            used.add(segment["id"])
            title = max(words, key=len)
            beats.append({"seg": segment["id"], "kind": "statement" if len(beats) % 3 == 2 else "hero",
                          "title": title, "sub": clip(segment["text"].rstrip(".!?。！？"), 34), "anchor": [title], "items": []})
    return beats


def card_for(index, beat, segments, words, planned_sections, skins):
    segment = next((item for item in segments if item["id"] == beat["seg"]), None)
    if not segment:
        return None, "unknown segment"
    section_i = next(i for i, section in enumerate(planned_sections)
                     if section["t0"] <= segment["start"] < section["t1"] or i == len(planned_sections) - 1)
    section = planned_sections[section_i]
    skin = skins[section["template"]]
    box_x, box_y, box_w, box_h = box_for(skin)
    start = find_word(words, beat["title"], segment["start"] - .05, segment["end"] + .05) or segment["start"] + .1
    title, subtitle = clip(beat["title"], 16).upper(), clip(beat["sub"], 34)
    condensed = bool(skin.get("condensed"))
    glyph = .5 if condensed else .66
    size = int(min(150, .92 * box_w / (glyph * max(len(title), 1) + .12),
                   .92 * box_w / (.5 + .32 * glyph * len(subtitle)) if subtitle else 150))
    size = max(70, size)
    content = {"words": [title], "sub": subtitle.upper() if condensed else subtitle}
    layout = "statement" if beat["kind"] == "statement" else "hero"
    if layout == "statement":
        content["script"] = ""
    spec = {"id": f"card_{index:03}", "type": "layout", "layout": layout, "content": content,
            "position": {"x": box_x / W, "y": box_y / H, "w": box_w / W, "h": box_h / H, "size": size},
            "animation": {"times": [round(start + .2 * i, 3) for i in range(3)]}}
    cap = min(start + 6.5, section["t1"] - .1)
    if cap - start < 2.4:
        start = max(section["t0"] + .35, min(start, cap - 2.4), segment["start"] - 1.0)
        spec["animation"]["times"] = [round(start + .2 * i, 3) for i in range(3)]
    end = min(max(segment["end"] + .4, start + 2.6), start + 6.5, section["t1"] - .1)
    return {"spec": spec, "t_in": round(start, 3), "t_out": round(end, 3), "section": section_i, "kind": beat["kind"]}, None


def build_cards(beats, segments, words, planned_sections, skins):
    cards, rejected = [], []
    for beat in sorted(beats, key=lambda item: item["seg"]):
        card, reason = card_for(len(cards) + 1, beat, segments, words, planned_sections, skins)
        if not card:
            rejected.append({"beat": beat, "why": reason}); continue
        if cards and card["t_in"] < cards[-1]["t_out"] + .4:
            rejected.append({"beat": beat, "why": "overlaps previous card"}); continue
        if card["t_in"] < planned_sections[card["section"]]["t0"] + .3 or card["t_out"] - card["t_in"] < 2.0:
            rejected.append({"beat": beat, "why": "insufficient safe screen time"}); continue
        cards.append(card)
    return cards, rejected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript")
    parser.add_argument("out_dir")
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--templates", default="T17")
    parser.add_argument("--mode", choices=["single", "multi", "auto"], default="single")
    parser.add_argument("--aspect", choices=["16:9", "9:16"], default="9:16")
    parser.add_argument("--face")
    args = parser.parse_args(argv)
    requested = [value.strip() for value in args.templates.split(",") if value.strip()]
    installed = resolve(args.install_root, requested, args.aspect)
    skins = {item.id: item.skin for item in installed}
    versions = {item.id: item.version for item in installed}
    data, words = load_transcript(args.transcript)
    if not words:
        print("planner: transcript has no words", file=sys.stderr); return 5
    selected = choose_templates(args.mode, requested, args.duration)
    planned_sections = sections(words, args.duration, selected)
    segments = segment_list(data)
    cards, rejected = build_cards(beats_for(segments, planned_sections), segments, words, planned_sections, skins)
    for section in planned_sections:
        section["box"] = list(box_for(skins[section["template"]]))
    face = json.loads(Path(args.face).read_text()) if args.face else None
    plan = {"version": 1, "schema": "legacy-v1", "end": round(args.duration, 3), "evaDir": "../media/eva", "face": face,
            "templates": versions, "sections": planned_sections, "cards": cards,
            "planner": {"source": "local-transcript-heuristic", "rejected": rejected, "text_policy": "verbatim-transcript-only"}}
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "plan.js").write_text("window.EVA_PLAN = " + json.dumps(plan, ensure_ascii=False) + ";\n", encoding="utf-8")
    storyboard = {"sections": [{"start": section["t0"], "template": section["template"]} for section in planned_sections],
                  "highlights": [card["t_in"] for card in cards]}
    (out / "storyboard.json").write_text(json.dumps(storyboard), encoding="utf-8")
    print(f"planner: {len(planned_sections)} section(s) {[s['template'] for s in planned_sections]}, {len(cards)} card(s), source=local-transcript-heuristic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
