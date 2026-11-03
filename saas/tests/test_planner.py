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
    for mode, tpl, n in (("single", "T20", 1), ("multi", "T17,T20,T01", 3), ("auto", "T17", 4)):
        out = d / mode
        subprocess.run([sys.executable, HERE.parent / "worker/planner.py", d / "job/srt/talk.transcript.js", out, "--duration", str(D),
                        "--templates", tpl, "--mode", mode, "--no-llm"], check=True)
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
