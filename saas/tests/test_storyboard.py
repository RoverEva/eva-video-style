#!/usr/bin/env python3
"""AI storyboard (Claude Opus 5.5) without network: the Anthropic call is replaced by a fake, everything else is real.
   python3 saas/tests/test_storyboard.py
- a valid storyboard → sections + cards for the renderer; every template used; anchor times from the transcript
- an invalid one → Claude gets ONE retry with the exact errors (tool_result is_error); fixed → plan
- invalid twice / API down / no key / another model → StoryboardError (the job fails; no heuristic, no raw footage)
- request: model claude-opus-5-5, forced submit_storyboard tool, system prompt cached, only transcript text sent"""
import copy, json, os, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / "worker"))
import storyboard as S, planner as P

SEL = ["T23", "T21", "T17", "T02", "T01"]
SCRIPT = ("Most creators spend hours editing every short video. EVA turns your raw phone clip into a finished edit. You choose a style, "
          "we add captions, motion cards and music. Upload once and post everywhere today. It takes about five minutes from start to finish.")
GOOD = json.loads((HERE / "fixtures/storyboard_15s.json").read_text())
with tempfile.TemporaryDirectory() as d:
    d = Path(d); subprocess.run([sys.executable, HERE / "make_fixture.py", d, "-", "15.07", SCRIPT], check=True, stdout=subprocess.DEVNULL)
    doc, words = P.load_transcript(d / "srt/talk.transcript.js")
segs = P.segments_list(doc); calls = []

def fake(responses):
    def call(key, system, user, tool, prior=None, timeout=180):
        calls.append({"system": system, "user": user, "tool": tool, "prior": prior})
        r = responses.pop(0)
        if isinstance(r, Exception): raise r
        use = {"type": "tool_use", "id": f"tu{len(calls)}", "name": tool["name"], "input": copy.deepcopy(r)}
        return use, {"input_tokens": 9000, "output_tokens": 3500, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}, 1.0, {"content": [use]}
    return call

def run(responses, **kw):
    S.call_claude = fake(responses); calls.clear()
    return S.plan(words, segs, 15.07, SEL, P.box_for, key=kw.get("key", "test-key"), log=lambda m: None)

secs, cards, x = run([GOOD])
assert [s["template"] for s in secs] == SEL and secs[0]["t0"] == 0 and secs[-1]["t1"] == 15.07
assert [c["kind"] for c in cards] == ["hero", "process", "statement", "checklist", "compare"] and x["source"] == "llm:claude-opus-5-5"
pr = next(c for c in cards if c["kind"] == "process"); assert pr["spec"]["animation"]["times"][0] == P.find_word(words, "raw", 3, 6)
assert x["usage"]["usd"] == round((9000 * 4 + 3500 * 20) / 1e6, 4) and len(calls) == 1
c0 = calls[0]; assert "Word times" in c0["user"] and "process" in c0["user"] and "illustrative" in c0["system"]
print(f"valid storyboard → {len(secs)} sections, {len(cards)} cards, one call, ${x['usage']['usd']}")

bad = copy.deepcopy(GOOD); bad["beats"][1]["anchor_words"] = ["model", "into"]; bad["beats"][4]["content"]["left"]["points"] = ["saves 80% time"]
secs, cards, x = run([bad, GOOD])
fb = calls[1]["prior"][1]["content"][0]
assert len(calls) == 2 and fb["type"] == "tool_result" and fb["is_error"] and "'model' is not spoken" in fb["content"] and "number 80" in fb["content"]
assert x["attempts"][0]["errors"] and not x["attempts"][1]["errors"]
print("invalid storyboard → one retry with the exact errors → fixed")

for name, responses, kw in (("invalid twice", [bad, bad], {}), ("API down", [S.StoryboardError("Anthropic API unreachable: URLError")], {}), ("no key", [], {"key": ""})):
    os.environ.pop("ANTHROPIC_API_KEY", None)
    try: run(responses, **kw); raise AssertionError(name + " did not fail")
    except S.StoryboardError as e: print(f"{name} → StoryboardError ({str(e)[:70]})")
os.environ["EVA_STORYBOARD_MODEL"] = "claude-haiku-5-5"
try: run([GOOD]); raise AssertionError("other model accepted")
except S.StoryboardError as e: print("other model → refused"); os.environ.pop("EVA_STORYBOARD_MODEL")

t = S.tool_schema(SEL); assert t["input_schema"]["properties"]["beats"]["items"]["properties"]["template"]["enum"] == SEL
missing = copy.deepcopy(GOOD); missing["beats"] = [b for b in missing["beats"] if b["template"] != "T02"]
assert any("T02" in e for e in S.validate(missing, words, 15.07, SEL)), "a missing template must be an error"
print("storyboard tests: ok")
