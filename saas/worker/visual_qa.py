#!/usr/bin/env python3
"""Visual coverage QA of a rendered video, checked on the actual frames (not only the plan).

    visual_qa.py OUT.mp4 SOURCE.mp4 PLAN.json OUT_DIR [--aspect 9:16|16:9] [--selected T23,T21,...] [--fps 4]

For each sampled frame (4 per second) the rendered frame is compared with the source footage at the same moment, scaled
to fill the frame like the renderer's full-bleed presenter. A close match (normalised correlation >= RAW_SIM on a small
grey thumbnail, sampled over a few crops) means the viewer sees raw footage (+ captions). The planned state of the same
moment comes from coverage.timeline(plan). Output in OUT_DIR:
  coverage.json   — plan timeline, visual timeline, metrics, targets, templates selected/used/dropped, unexplained raw
  coverage.md     — readable report
  timeline.png    — per-second strip: planned state, seen state, thumbnails every second
Metrics: Template Coverage (any template look), Meaningful Editing Coverage (a card/infographic from the speech on screen;
a static template background alone does not count), raw seconds, longest raw stretch, unexplained raw (raw on screen
where the plan says card/template). Verdict PASS / WARN / FAIL against configurable targets (planner.COVERAGE_TARGET).
"""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coverage, planner

RAW_SIM = 0.80
MOTION_MIN = 1.5   # mean grey-level change per frame step (0–255) beyond the footage's own motion = something is animating


def content_relevance(plan, transcript):
    """per card: share of its content words spoken while it is on screen (±3 s before, +1 s after); keyword-only cards
    (one short headline, no sub/steps) are flagged — they are on-topic but are not storytelling"""
    if not transcript: return None
    DIAGRAMS = {"steps", "process", "compare", "checklist", "stat", "bars", "network", "orbit", "journey", "feature"}   # structured explanations, never "keyword cards"
    _, words = planner.load_transcript(transcript)
    norm = planner.norm; out = []
    for c in plan.get("cards", []):
        k = c["spec"]["content"]
        side = lambda x: " ".join([(x or {}).get("title", ""), *((x or {}).get("points") or [])])
        text = " ".join([*(k.get("words") or []), k.get("sub") or "", k.get("title") or "", k.get("body") or "", k.get("center") or "", k.get("kicker") or "", k.get("label") or "",
                         side(k.get("left")), side(k.get("right")), *[i.get("title", "") + " " + i.get("sub", "") + " " + i.get("label", "") for i in k.get("items") or []]])
        kws = [norm(w) for w in planner.keywords(text)]
        near = {norm(w["w"]) for w in words if c["t_in"] - 3 <= w["start"] <= c["t_out"] + 1}
        hit = sum(1 for w in kws if w in near) / max(len(kws), 1)
        keyword_only = c.get("kind") not in DIAGRAMS and len((k.get("words") or [""])[0].split()) <= 1 and len((k.get("sub") or "").split()) <= 3
        out.append({"t_in": c["t_in"], "relevance": round(hit, 2), "keyword_only": keyword_only, "kind": c.get("kind")})
    return {"cards": out, "mean_relevance": round(sum(x["relevance"] for x in out) / max(len(out), 1), 2),
            "keyword_only_cards": sum(x["keyword_only"] for x in out), "kinds": sorted({x["kind"] for x in out})}
TW, TH = 48, 27


def frames(path, fps, w, h, n=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},format=gray",
           "-f", "rawvideo", "-"]
    b = subprocess.run(cmd, capture_output=True, check=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, h, w).astype(np.float32)
    return a[:n] if n else a


def ncc(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 1e-6 else 0.0


def seen_raw(out_f, src_f):
    """raw if the rendered frame matches the source frame (allowing the renderer's face-framing shift and zoom)"""
    h, w = out_f.shape; best = 0.0
    big = np.kron(src_f, np.ones((2, 2), np.float32))   # 2x for sub-crops
    H2, W2 = big.shape
    for z in (1.0, 1.15, 1.3):
        ch, cw = int(H2 / z), int(W2 / z)
        for oy in (0, .5, 1):
            for ox in (0, .5, 1):
                y, x = int((H2 - ch) * oy), int((W2 - cw) * ox)
                crop = big[y:y + ch, x:x + cw]
                ys = (np.arange(h) * ch / h).astype(int); xs = (np.arange(w) * cw / w).astype(int)
                best = max(best, ncc(out_f, crop[np.ix_(ys, xs)]))
    return best


def runs(states, fps):
    out, cur = [], None
    for i, s in enumerate(states + [None]):
        if s != (cur and cur[0]):
            if cur: out.append({"state": cur[0], "t0": round(cur[1] / fps, 2), "t1": round(i / fps, 2)})
            cur = (s, i) if s else None
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("source"); ap.add_argument("plan"); ap.add_argument("dir")
    ap.add_argument("--aspect", default="16:9"); ap.add_argument("--selected", default=""); ap.add_argument("--fps", type=float, default=4)
    ap.add_argument("--transcript", help="srt/talk.transcript.js: for the content-relevance check of the cards")
    a = ap.parse_args(argv); d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(a.plan).read_text()); sel = [x for x in a.selected.split(",") if x] or None
    pt = coverage.timeline(plan, a.aspect, sel)
    tw, th = (TW, TH) if a.aspect == "16:9" else (TH, TW)
    O, S = frames(a.out, a.fps, tw, th), frames(a.source, a.fps, tw, th)
    n = min(len(O), len(S))
    sims = [seen_raw(O[i], S[i]) for i in range(n)]
    plan_state = []
    for i in range(n):
        t = i / a.fps; st = next((r["state"] for r in pt["runs"] if r["t0"] <= t < r["t1"]), "raw"); plan_state.append(st)
    seen = ["raw" if s >= RAW_SIM else ("card" if p == "card" else "template") for s, p in zip(sims, plan_state)]
    unexplained = [i / a.fps for i in range(n) if seen[i] == "raw" and plan_state[i] != "raw"]
    # motion: movement in the rendered frame beyond the movement already in the footage (animated cards, transitions, backgrounds)
    added = [0.0] + [float(np.abs(O[i] - O[i - 1]).mean() - np.abs(S[i] - S[i - 1]).mean()) for i in range(1, n)]
    moving = [x > MOTION_MIN for x in added]
    edited = [i for i in range(n) if seen[i] != "raw"]
    motion = {"animated_s": round(sum(moving[i] for i in edited) / a.fps, 2), "motion_coverage": round(sum(moving[i] for i in edited) / max(len(edited), 1), 3),
              "static_template_s": round(sum(1 for i in edited if seen[i] == "template" and not moving[i]) / a.fps, 2),
              "longest_static_s": round(max((r["t1"] - r["t0"] for r in runs(["static" if (seen[i] != "raw" and not moving[i]) else "x" for i in range(n)], a.fps) if r["state"] == "static"), default=0), 2)}
    relevance = content_relevance(plan, a.transcript)
    sec = lambda xs, k: round(xs.count(k) / a.fps, 2)
    tgt = planner.COVERAGE_TARGET; dur = n / a.fps
    raw_runs = [r for r in runs(seen, a.fps) if r["state"] == "raw"]
    m = {"duration_s": round(dur, 2), "meaningful_coverage": round(seen.count("card") / max(n, 1), 3),
         "template_coverage": round((n - seen.count("raw")) / max(n, 1), 3), "raw_s": sec(seen, "raw"),
         "longest_raw_s": round(max((r["t1"] - r["t0"] for r in raw_runs), default=0), 2), "unexplained_raw_s": round(len(unexplained) / a.fps, 2)}
    issues = []
    if pt["templates_dropped"]: issues.append(("FAIL", f"selected templates not used: {pt['templates_dropped']}"))
    if m["unexplained_raw_s"] > .5: issues.append(("FAIL", f"{m['unexplained_raw_s']} s of raw footage where the plan has a card/template (render fell back)"))
    if m["meaningful_coverage"] < tgt["meaningful"]: issues.append(("WARN", f"meaningful editing {m['meaningful_coverage']:.0%} < target {tgt['meaningful']:.0%}"))
    if m["template_coverage"] < tgt["template"]: issues.append(("WARN", f"template coverage {m['template_coverage']:.0%} < target {tgt['template']:.0%}"))
    if m["longest_raw_s"] > tgt["max_raw_s"]: issues.append(("WARN", f"longest raw stretch {m['longest_raw_s']} s > {tgt['max_raw_s']} s"))
    verdict = "FAIL" if any(s == "FAIL" for s, _ in issues) else "WARN" if issues else "PASS"
    if motion["longest_static_s"] > 4: issues.append(("WARN", f"{motion['longest_static_s']} s with nothing moving on screen"))
    if relevance and relevance["mean_relevance"] < .7: issues.append(("WARN", f"card text relevance {relevance['mean_relevance']:.0%} (words not spoken near the card)"))
    if relevance and relevance["keyword_only_cards"] > len(relevance["cards"]) / 2: issues.append(("WARN", f"{relevance['keyword_only_cards']}/{len(relevance['cards'])} cards are single keywords, not storytelling"))
    verdict = "FAIL" if any(s == "FAIL" for s, _ in issues) else "WARN" if issues else "PASS"
    rep = {"schema": "eva-visual-coverage/1", "verdict": verdict, "motion": motion, "content": relevance, "issues": [{"severity": s, "text": t} for s, t in issues], "visual": m,
           "planned": {k: pt[k] for k in ("meaningful_coverage", "template_coverage", "meaningful_s", "template_static_s", "raw_s", "longest_raw_s")},
           "targets": tgt, "templates": {"selected": pt["templates_selected"], "used": pt["templates_used"], "dropped": pt["templates_dropped"]},
           "per_template": pt["per_template"], "planned_segments": pt["runs"], "seen_segments": runs(seen, a.fps),
           "cards": [{"t_in": c["t_in"], "t_out": c["t_out"], "template": plan["sections"][c["section"]]["template"], "kind": c.get("kind")} for c in plan.get("cards", [])],
           "rejected_cards": pt["rejected"], "unexplained_raw_at": unexplained, "raw_similarity_threshold": RAW_SIM}
    (d / "coverage.json").write_text(json.dumps(rep, indent=1))
    L = [f"# Visual coverage — {verdict}", "", f"{Path(a.out).name} · {a.aspect} · {dur:.1f} s", "",
         "| | planned | seen on the frames |", "|---|---|---|",
         f"| Meaningful editing (card / infographic) | {pt['meaningful_coverage']:.0%} | {m['meaningful_coverage']:.0%} |",
         f"| Template coverage (any template look) | {pt['template_coverage']:.0%} | {m['template_coverage']:.0%} |",
         f"| Raw footage + captions | {pt['raw_s']} s | {m['raw_s']} s |", f"| Longest raw stretch | {pt['longest_raw_s']} s | {m['longest_raw_s']} s |",
         f"| Unexplained raw (render fell back) | – | {m['unexplained_raw_s']} s |",
         f"| Motion / animation (edited time with something moving) | – | {motion['motion_coverage']:.0%} ({motion['animated_s']} s) |",
         f"| Longest stretch with nothing moving | – | {motion['longest_static_s']} s |",
         f"| Card text spoken near the card (content relevance) | {relevance['mean_relevance']:.0%} |  |" if relevance else "| Content relevance | not run (no transcript) | |",
         f"| Keyword-only cards | {relevance['keyword_only_cards']} of {len(relevance['cards'])} |  |" if relevance else "", "",
         f"Templates selected {pt['templates_selected']} · used {pt['templates_used']} · dropped {pt['templates_dropped'] or 'none'}", "",
         "| Template | seconds | card | template only | raw |", "|---|---|---|---|---|"]
    L += [f"| {t} | {v['seconds']} | {v['card_s']} | {v['template_s']} | {v['raw_s']} |" for t, v in pt["per_template"].items()]
    L += ["", "Planned segments: " + ", ".join(f"{r['state']} {r['t0']}–{r['t1']}" for r in pt["runs"]),
          "", "Seen segments: " + ", ".join(f"{r['state']} {r['t0']}–{r['t1']}" for r in runs(seen, a.fps)),
          "", "Rejected cards: " + (", ".join(pt["rejected"]) or "none"), "", "Issues: " + ("; ".join(f"{s} {t}" for s, t in issues) or "none")]
    (d / "coverage.md").write_text("\n".join(L) + "\n")
    # timeline image: planned row, seen row, thumbnails each second
    from PIL import Image, ImageDraw
    col = {"card": (91, 61, 245), "template": (247, 178, 64), "raw": (200, 200, 200)}
    secs = int(dur) + 1; tw2, th2 = (160, 90) if a.aspect == "16:9" else (72, 128)
    img = Image.new("RGB", (max(secs * tw2, 600), 64 + th2 + 30), "white"); g = ImageDraw.Draw(img); px = img.width / max(dur, .1)
    for row, (lab, st, step) in enumerate((("plan", pt["runs"], None), ("seen", runs(seen, a.fps), None))):
        y = 6 + row * 26; g.text((2, y + 4), lab, fill="black")
        for r in st: g.rectangle([40 + r["t0"] * px * (img.width - 40) / img.width, y, 40 + r["t1"] * px * (img.width - 40) / img.width, y + 20], fill=col[r["state"]])
    thumbs = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.out, "-vf", f"fps=1,scale={tw2}:{th2}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    arr = np.frombuffer(thumbs, np.uint8).reshape(-1, th2, tw2, 3)
    for i, t in enumerate(arr[:secs]): img.paste(Image.fromarray(t), (i * tw2, 60))
    g.text((4, 64 + th2 + 8), "violet = card (meaningful) · orange = template look only · grey = raw footage + captions · thumbnails 1/s", fill="black")
    img.save(d / "timeline.png")
    print(f"motion {motion['motion_coverage']:.0%} of edited time, longest static {motion['longest_static_s']} s; "
          + (f"relevance {relevance['mean_relevance']:.0%}, keyword-only {relevance['keyword_only_cards']}/{len(relevance['cards'])}" if relevance else "relevance not run"))
    print(f"visual QA {verdict}: meaningful {m['meaningful_coverage']:.0%} (plan {pt['meaningful_coverage']:.0%}), template {m['template_coverage']:.0%}, "
          f"raw {m['raw_s']} s, longest raw {m['longest_raw_s']} s, unexplained raw {m['unexplained_raw_s']} s, dropped {pt['templates_dropped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
