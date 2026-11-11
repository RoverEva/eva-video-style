#!/usr/bin/env python3
"""Planner checks (no network, no LLM): sections cut at pauses, every section gets a card, cards never overlap,
stay above the caption zone and only use words from the transcript."""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    D = 30   # MVP upload limit: 30 s
    subprocess.run([sys.executable, HERE / "make_fixture.py", d / "job", "-", str(D)], check=True, capture_output=True)
    for mode, tpl, n in (("single", "T21", 1), ("multi", "T23,T21,T02", 3), ("single", "T02", 1), ("auto", "T17", 4)):
        out = d / mode
        subprocess.run([sys.executable, HERE.parent / "worker/planner.py", d / "job/srt/talk.transcript.js", out, "--duration", str(D),
                        "--templates", tpl, "--mode", mode, "--legacy-heuristic"], check=True)
        p = json.loads((out / "plan.json").read_text()); secs, cards = p["sections"], p["cards"]
        assert len(secs) == n, (mode, len(secs)); assert secs[0]["t0"] == 0 and secs[-1]["t1"] == D
        assert all(a["t1"] == b["t0"] for a, b in zip(secs, secs[1:]))
        assert {c["section"] for c in cards} == set(range(n)), f"{mode}: a section has no card"
        assert all(a["t_out"] + .35 <= b["t_in"] for a, b in zip(cards, cards[1:])), "cards overlap"
        text = " ".join(s["text"] for s in json.loads((d / "job/srt/talk.transcript.js").read_text().split("=", 1)[1].rstrip(";\n"))["segments"]).upper()
        for c in cards:
            pos = c["spec"]["position"]; assert (pos["y"] + pos["h"]) * 1080 <= 900, "card enters caption zone"
            words = c["spec"]["content"].get("words") or [i["title"] for i in c["spec"]["content"]["items"]]
            assert all(w in text for w in words), f"invented text {words}"
            assert c["t_out"] - c["t_in"] >= 2.0
print("planner tests: ok")

# real eva-asr shape (seen on Modal's image in CI): one 8 s VAD segment + a short one in a 10 s clip → still one card per look
with tempfile.TemporaryDirectory() as d:
    d = Path(d); words = "Hi, I'm Eva. Welcome to Eva Video Style. Just upload your video, choose a template, and let AI".split()
    ws = [{"w": w, "start": round(.332 + i * 7.85 / len(words), 3), "end": round(.632 + i * 7.85 / len(words), 3)} for i, w in enumerate(words)]
    w2 = [{"w": x, "start": 8.285 + i * .45, "end": 8.685 + i * .45} for i, x in enumerate("create something amazing.".split())]
    tr = {"source": "eva-asr", "language": "en", "segments": [{"start": .332, "end": 8.184, "text": " ".join(words), "words": ws},
                                                              {"start": 8.285, "end": 9.711, "text": "create something amazing.", "words": w2}]}
    (d / "t.js").write_text("window.EV_ASR = " + json.dumps(tr) + ";\n")
    subprocess.run([sys.executable, HERE.parent / "worker/planner.py", d / "t.js", d / "o", "--duration", "10.033", "--templates", "T20,T01", "--mode", "multi", "--no-llm"], check=True)
    p = json.loads((d / "o/plan.json").read_text())
    assert {c["section"] for c in p["cards"]} == {0, 1}, p["planner"]["rejected"]
    assert all(c["t_out"] - c["t_in"] >= 2.0 for c in p["cards"])
print("planner tests (long ASR segments): ok")
