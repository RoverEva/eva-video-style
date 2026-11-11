#!/usr/bin/env python3
"""Editing-coverage timeline of a plan.json, using the same layout rules as saas/worker/auto/auto.js.

Every frame is classified as
  card      — a card / infographic is on screen (MEANINGFUL editing: words, steps, data from the speech)
  template  — the template's look is visible (background, presenter window, ring) but nothing content-specific
  raw       — the presenter fills the frame: raw footage + captions only
Template Coverage = card + template; Meaningful Editing Coverage = card. Selected-but-unused templates are listed.

    coverage.py PLAN.json [--aspect 9:16|16:9] [--selected T23,T21,...] [--json OUT]   (also importable: timeline(plan, aspect))
"""
import argparse, json, sys

FPS = 30
GAP = {"9:16": 1.0, "16:9": 3.2}          # auto.js: a free stretch at least this long turns the presenter full-bleed


def layout_keys(plan, aspect):
    """[(t, 'full'|'win')] — the presenter-window keyframes auto.js builds (target state applied at t + d/2)"""
    secs, cards, port = plan["sections"], plan.get("cards", []), aspect == "9:16"
    keys = [(0.0, "full" if port else "win")]
    if port:   # same as auto.js (9:16): window for each run of cards, full-bleed only in gaps >= GAP
        cl = []
        for c in sorted(cards, key=lambda c: c["t_in"]):
            if cl and c["t_in"] - (cl[-1][1] + .4) < GAP[aspect]: cl[-1][1] = max(cl[-1][1], c["t_out"])
            else: cl.append([c["t_in"], c["t_out"]])
        for j, (a, b) in enumerate(cl):
            keys.append((max(.05, a - .55) + .225, "win"))
            if j + 1 == len(cl) or cl[j + 1][0] - (b + .4) >= GAP[aspect]: keys.append((b + .4 + .25, "full"))
        return sorted(keys)
    for i, s in enumerate(secs):
        if i > 0 and not port: keys.append((s["t0"] + .225, "win"))
        free = s["t0"] + (0 if port else .6); gaps = []
        for c in sorted((c for c in cards if c["section"] == i), key=lambda c: c["t_in"]):
            gaps.append((free, c["t_in"])); free = c["t_out"] + .4
        gaps.append((free, s["t1"]))
        for a, b in gaps:
            if b - a >= GAP[aspect]:
                keys.append((a + .25, "full"))
                if b < s["t1"] - .05: keys.append((b - .55 + .225, "win"))
    return sorted(keys)


def timeline(plan, aspect="16:9", selected=None):
    end = float(plan.get("end") or plan["sections"][-1]["t1"]); keys = layout_keys(plan, aspect); cards = plan.get("cards", [])
    frames, k = [], 0
    for f in range(int(round(end * FPS))):
        t = f / FPS
        while k + 1 < len(keys) and keys[k + 1][0] <= t: k += 1
        if any(c["t_in"] <= t < c["t_out"] for c in cards): frames.append("card")
        elif aspect == "9:16" and keys[k][1] == "win": frames.append("template")   # portrait: window only around cards
        else: frames.append("raw" if keys[k][1] == "full" else "template")
    n = max(len(frames), 1); sec = lambda s: round(frames.count(s) / FPS, 2)
    runs, cur = [], None   # contiguous stretches
    for i, s in enumerate(frames + [None]):
        if s != (cur and cur[0]):
            if cur: runs.append({"state": cur[0], "t0": round(cur[1] / FPS, 2), "t1": round(i / FPS, 2)})
            cur = (s, i) if s else None
    used = sorted({s["template"] for s in plan["sections"]})
    per_tpl = {}
    for i, s in enumerate(plan["sections"]):
        a, b = int(s["t0"] * FPS), int(s["t1"] * FPS); fr = frames[a:b] or ["raw"]
        per_tpl.setdefault(s["template"], {"seconds": 0, "card_s": 0, "template_s": 0, "raw_s": 0})
        d = per_tpl[s["template"]]; d["seconds"] = round(d["seconds"] + (b - a) / FPS, 2)
        for st in ("card", "template", "raw"): d[st + "_s"] = round(d[st + "_s"] + fr.count(st) / FPS, 2)
    raw_runs = [r for r in runs if r["state"] == "raw"]
    return {"schema": "eva-coverage/1", "aspect": aspect, "duration_s": round(end, 2),
            "meaningful_s": sec("card"), "template_static_s": sec("template"), "raw_s": sec("raw"),
            "meaningful_coverage": round(frames.count("card") / n, 3), "template_coverage": round((frames.count("card") + frames.count("template")) / n, 3),
            "longest_raw_s": max((r["t1"] - r["t0"] for r in raw_runs), default=0), "raw_stretches": raw_runs,
            "templates_used": used, "templates_selected": selected or used,
            "templates_dropped": [t for t in (selected or []) if t not in used], "per_template": per_tpl, "runs": runs,
            "cards": len(cards), "rejected": [r.get("why") for r in (plan.get("planner") or {}).get("rejected", [])]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("--aspect", default="16:9"); ap.add_argument("--selected", default="")
    ap.add_argument("--json"); a = ap.parse_args()
    r = timeline(json.load(open(a.plan)), a.aspect, [x for x in a.selected.split(",") if x])
    if a.json: open(a.json, "w").write(json.dumps(r, indent=1))
    print(json.dumps({k: v for k, v in r.items() if k not in ("runs", "per_template")}, indent=1))
