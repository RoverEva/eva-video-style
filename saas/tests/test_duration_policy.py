#!/usr/bin/env python3
"""Duration scope: the shared worker pipeline has NO fixed duration cap; the 30 s limit is the hosted Studio's launch
policy (saas/web/studio_policy.py), applied explicitly at the Studio boundary.

    python3 saas/tests/test_duration_policy.py            # policy + full-coverage checks (about 1 minute)
    python3 saas/tests/test_duration_policy.py --render   # also renders the 45 s clip end to end (several minutes)

MOCKED / LOCAL ONLY: synthetic 45 s video + synthetic transcript (make_fixture.py) and a generated storyboard through the
EVA_STORYBOARD_FIXTURE test hook. No ASR model, no network, no Anthropic request — this says nothing about token use.
  1. engine default: a 45 s input is accepted; plan, cards and render chunks cover the whole source, up to the ending
  2. an environment variable cannot impose a cap on the engine (EVA_MAX_SECONDS is ignored)
  3. Studio (worker_limits): a 45 s file is rejected on its REAL duration before ASR/planning/rendering, nothing cut
  4. Studio: a within-limit clip (20 s) passes the same validation
  5. Studio API: declared 45 s → the user-facing limit message; 30.4 s accepted (container rounding)
  6. modal_app adds the Studio limits to every worker job (preview, HD export, legacy API)
  7. --render: final.mp4 reaches the 45 s ending with audio and captions to the end
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE.parent / "worker"), str(HERE.parent / "web")]
import pipeline, planner, studio_policy as POLICY  # noqa: E402

OK = True


def check(cond, msg):
    global OK
    print(("PASS " if cond else "FAIL ") + msg); OK = OK and bool(cond)


def fixture(d: Path, seconds: float):
    script = " ".join(f"Part {n} explains another useful editing idea clearly." for n in range(1, int(seconds / 3.2)))
    subprocess.run([sys.executable, HERE / "make_fixture.py", d, d / "in.mp4", str(seconds), script], check=True, stdout=subprocess.DEVNULL)
    _, words = planner.load_transcript(d / "srt/talk.transcript.js")
    return d / "in.mp4", words


def storyboard(words, dur, path):
    """contiguous ≤ 7 s hero beats over the WHOLE clip, each anchored on a word spoken inside it (test hook only)"""
    beats, t0 = [], 0.0
    while t0 < dur - .01:
        t1 = min(dur, t0 + 7.0)
        if dur - t1 < 2.0: t1 = dur
        w = next(w for w in words if t0 <= w["start"] < t1 - .3 and len(re.sub(r"\W", "", w["w"])) >= 4)
        word = re.sub(r"\W", "", w["w"])
        beats.append({"start": round(t0, 2), "end": round(t1, 2), "template": "T17", "component": "hero", "spoken": "", "anchor_words": [word],
                      "content": {"title": word.upper()}, "illustrative": False, "why": "test"})
        t0 = t1
    path.write_text(json.dumps({"beats": beats}))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--render", action="store_true"); a = ap.parse_args()
    base = {"aspect": "9:16", "templates": ["T17"], "template_mode": "single"}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 1 + 2: engine default, with a cap in the environment that must be ignored
        d = tmp / "long"; src, words = fixture(d, 45.0); dur = float(pipeline.probe(src)["format"]["duration"])
        storyboard(words, dur, tmp / "sb.json"); os.environ["EVA_STORYBOARD_FIXTURE"] = str(tmp / "sb.json"); os.environ["EVA_MAX_SECONDS"] = "30"
        check(dur > 30, f"synthetic input is {dur:.2f} s")
        pipeline.prepare(src, d, dict(base))
        J = json.loads((d / "job.json").read_text())
        check(J["options"].get("max_seconds") is None, "engine default options carry no duration cap (EVA_MAX_SECONDS ignored)")
        check(abs(J["end"] - dur) < .1, f"job covers the source: {J['end']} s of {dur:.2f} s")
        ch = J["chunks"]
        check(ch[0][0] == 0 and abs(ch[-1][1] - J["end"]) < 1e-6 and all(abs(x[1] - y[0]) < 1e-9 for x, y in zip(ch, ch[1:])),
              f"{len(ch)} contiguous render chunks reach {ch[-1][1]:.2f} s")
        plan = json.loads((d / "plan.json").read_text())
        check(abs(plan["sections"][-1]["t1"] - J["end"]) < .2 and plan["cards"][-1]["t_out"] > J["end"] - 7.5,
              f"plan covers 0–{plan['sections'][-1]['t1']:.1f} s; last card {plan['cards'][-1]['t_in']:.1f}–{plan['cards'][-1]['t_out']:.1f} s")
        os.environ.pop("EVA_MAX_SECONDS")

        # 3: Studio limits reject the 45 s file on its real duration, before ASR / planning / rendering
        d3 = tmp / "studio_long"; d3.mkdir()
        rc = pipeline.prepare(src, d3, dict(base, **POLICY.worker_limits()))   # Reject → exit 2 + report (API releases the reservation)
        rep = json.loads((d3 / "out/report.json").read_text()); st = sorted(p.stem for p in (d3 / "stages").glob("*.json"))
        check(rc == 2 and "accepts up to 30 s" in rep.get("rejected", "") and not {"asr", "plan", "media"} & set(st),
              f"Studio rejects the real 45 s file before media/ASR/planning (exit {rc}, stages {st}): {rep.get('rejected')}")

        # 4: Studio accepts a within-limit clip
        d4 = tmp / "studio_ok"; src4, w4 = fixture(d4, 20.0); storyboard(w4, float(pipeline.probe(src4)["format"]["duration"]), tmp / "sb20.json")
        os.environ["EVA_STORYBOARD_FIXTURE"] = str(tmp / "sb20.json")
        pipeline.prepare(src4, d4, dict(base, **POLICY.worker_limits()))
        check((d4 / "plan.json").exists(), "Studio accepts a 20 s clip (validated, planned)")

        # 5: Studio API policy (user-facing, before a project exists)
        check(POLICY.too_long(45) and POLICY.message(45) == "This video is 45 seconds long. The limit is 30 seconds.", "API: 45 s refused with the limit message")
        check(not POLICY.too_long(30.4) and not POLICY.too_long(None), "API: 30.4 s (rounding) and unknown duration pass to the worker check")
        api = (HERE.parent / "web/api_v2.py").read_text()
        check("POLICY.too_long(dur)" in api, "api_v2.create_project uses the Studio policy")

        # 6: every worker job started by the Studio carries its limits
        ma = (HERE.parent / "modal_app.py").read_text()
        check(ma.count("POLICY.worker_limits()") == 2 and "**POLICY.worker_limits()" in ma, "modal_app adds Studio limits to account versions and legacy jobs")

        # 7: full local render of the 45 s clip
        if a.render:
            os.environ["EVA_STORYBOARD_FIXTURE"] = str(tmp / "sb.json")
            d7 = tmp / "render"; fixture(d7, 45.0)
            rc = pipeline.main(["run", str(d7 / "in.mp4"), str(d7), "--options", str(_opts(tmp, base)), "--workers", "2"])
            fin = d7 / "out/final.mp4"; check(rc in (0, None) and fin.exists(), f"run exit {rc}")
            if fin.exists():
                p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", fin], capture_output=True, text=True).stdout)
                ds = {s["codec_type"]: float(s["duration"]) for s in p["streams"]}
                check(abs(ds["video"] - dur) < .25, f"final video {ds['video']:.2f} s reaches the ending ({dur:.2f} s)")
                check(abs(ds["audio"] - ds["video"]) < .25, f"audio {ds['audio']:.2f} s matches")
                cap = (d7 / "out/captions.srt").read_text(); ends = re.findall(r"--> (\d+):(\d+):(\d+),(\d+)", cap)
                last = max(int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000 for h, m, s, ms in ends)
                check(last > dur - 5, f"captions run to {last:.2f} s")
    print("duration policy tests:", "ok" if OK else "FAILED"); return 0 if OK else 1


def _opts(tmp, base):
    p = tmp / "opts.json"; p.write_text(json.dumps(dict(base, music="none"))); return p


if __name__ == "__main__":
    raise SystemExit(main())
