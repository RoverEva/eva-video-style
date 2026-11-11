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
    rep = {"schema": "eva-visual-coverage/1", "verdict": verdict, "issues": [{"severity": s, "text": t} for s, t in issues], "visual": m,
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
         f"| Unexplained raw (render fell back) | – | {m['unexplained_raw_s']} s |", "",
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
    print(f"visual QA {verdict}: meaningful {m['meaningful_coverage']:.0%} (plan {pt['meaningful_coverage']:.0%}), template {m['template_coverage']:.0%}, "
          f"raw {m['raw_s']} s, longest raw {m['longest_raw_s']} s, unexplained raw {m['unexplained_raw_s']} s, dropped {pt['templates_dropped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
