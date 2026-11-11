#!/usr/bin/env python3
"""Editing-coverage regression (Phase B, 2026-11-11).   python3 saas/tests/test_coverage.py
1. The production job of 2026-11-11 (15.07 s, 16:9, 5 templates selected, old planner: 3 sections, 1 card) scores as
   failing: 2 templates dropped, 16 % meaningful, 8.8 s raw, 0 s meaningful in the 10 s preview.
2. New planner, 15.07 s clip, all five launch templates, 16:9 and 9:16: every template used in order, meaningful
   editing >= target, template coverage >= target, no raw stretch > max_raw_s, each section has a card, no invented text.
3. Too many templates for the clip: planner exits 6 with a clear message (never drops one silently)."""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / "worker"))
import coverage, planner

old = {"end": 15.07, "sections": [{"t0": 0, "t1": 5.7, "template": "T23"}, {"t0": 5.7, "t1": 10.1, "template": "T21"}, {"t0": 10.1, "t1": 15.07, "template": "T17"}],
       "cards": [{"t_in": 12.53, "t_out": 14.93, "section": 2}]}
r = coverage.timeline(old, "16:9", ["T23", "T21", "T17", "T02", "T01"])
assert r["templates_dropped"] == ["T02", "T01"] and r["meaningful_coverage"] < .2 and r["raw_s"] > 8 and r["longest_raw_s"] > 5, r
p10 = coverage.timeline(dict(old, end=10.0, sections=[dict(s, t1=min(s["t1"], 10)) for s in old["sections"][:2]], cards=[]), "16:9")
assert p10["meaningful_s"] == 0 and p10["raw_s"] > 8
print(f"old production plan: meaningful {r['meaningful_coverage']:.0%}, raw {r['raw_s']} s, dropped {r['templates_dropped']} — scored as failing")

T = planner.COVERAGE_TARGET; SEL = ["T23", "T21", "T17", "T02", "T01"]
SCRIPT = ("Most creators spend hours editing every short video. EVA turns your raw phone clip into a finished edit. You choose a style, "
          "we add captions, motion cards and music. Upload once and post everywhere today. It takes about five minutes from start to finish.")
with tempfile.TemporaryDirectory() as d:
    d = Path(d); subprocess.run([sys.executable, HERE / "make_fixture.py", d / "job", "-", "15.07", SCRIPT], check=True, stdout=subprocess.DEVNULL)
    for ar in ("16:9", "9:16"):
        out = d / ar.replace(":", "x")
        subprocess.run([sys.executable, HERE.parent / "worker/planner.py", d / "job/srt/talk.transcript.js", out, "--duration", "15.07",
                        "--templates", ",".join(SEL), "--mode", "multi", "--aspect", ar, "--no-llm"], check=True, stdout=subprocess.DEVNULL)
        p = json.loads((out / "plan.json").read_text()); c = coverage.timeline(p, ar, SEL)
        assert [s["template"] for s in p["sections"]] == SEL and not c["templates_dropped"], p["sections"]
        assert min(s["t1"] - s["t0"] for s in p["sections"]) >= .8 * 15.07 / 5, "a look got far less than an equal share"
        assert {k["section"] for k in p["cards"]} == set(range(5)), "a template has no card"
        assert c["meaningful_coverage"] >= T["meaningful"] and c["template_coverage"] >= T["template"] and c["longest_raw_s"] <= T["max_raw_s"], c
        assert all(k["t_out"] - k["t_in"] >= 2.0 for k in p["cards"]) and all(a["t_out"] + .35 <= b["t_in"] for a, b in zip(p["cards"], p["cards"][1:]))
        text = SCRIPT.upper()
        assert all(w in text for k in p["cards"] for w in (k["spec"]["content"].get("words") or [i["title"] for i in k["spec"]["content"]["items"]])), "invented text"
        assert p["coverage"]["templates_dropped"] == [] and p["coverage"]["targets"] == T
        print(f"new planner {ar}: 5/5 templates, meaningful {c['meaningful_coverage']:.0%}, template {c['template_coverage']:.0%}, longest raw {c['longest_raw_s']} s")
    r = subprocess.run([sys.executable, HERE.parent / "worker/planner.py", d / "job/srt/talk.transcript.js", d / "short", "--duration", "8",
                        "--templates", ",".join(SEL), "--mode", "multi", "--no-llm"], capture_output=True, text=True)
    assert r.returncode == 6 and "Choose up to 2 templates" in r.stderr, r.stderr
    print("8 s clip with 5 templates: refused with a clear message (exit 6), nothing dropped silently")
print("coverage tests: ok")
