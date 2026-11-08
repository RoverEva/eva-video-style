#!/usr/bin/env python3
"""QA integration in the version worker (QA module qa/ v1.0): job-level pre/post reports (schema eva-qa/1) are summarised,
combined (worst of pre/post), saved with the version, and only EVA_QA_GATE=block turns a blocking FAIL into qa_failed.
Report mode never blocks: warnings, failures, QA errors and missing reports all deliver."""
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "worker")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "web"))
import versions as V, store


def report(verdict, issues=()):
    return {"schema": "eva-qa/1", "qa_version": "1.0.0", "verdict": verdict, "blocking": verdict == "FAIL",
            "counts": {"PASS": 30, "WARN": int(verdict == "WARN"), "FAIL": int(verdict == "FAIL")},
            "issues": [{"check": c, "severity": verdict, "message": "m", "t": [1, 2]} for c in issues], "not_run": [{"check": "X", "reason": "r"}]}


with tempfile.TemporaryDirectory() as d:
    w = Path(d) / "work"; w.mkdir()
    os.environ["EVA_QA"] = "off"; assert V.run_qa(w, "pre") == ({"status": "off"}, None)
    os.environ["EVA_QA"] = "report"
    # pre already checked (HD export of a checked version) → reused, not re-run
    V.qa_dir(w, "pre").mkdir(parents=True); (V.qa_dir(w, "pre") / "qa-report.json").write_text(json.dumps(report("PASS")))
    s, p = V.run_qa(w, "pre"); assert s["status"] == "pass" and s.get("reused") and p.name == "qa-report.json"
    # a QA crash / missing report → status error, never an exception
    s, p = V.run_qa(w, "post", preview=True, timeout=60); assert s["status"] == "error" and p is None, s
    for pre_v, post_v, want, blocking in (("PASS", "PASS", "pass", False), ("PASS", "WARN", "warn", False), ("WARN", "PASS", "warn", False), ("PASS", "FAIL", "fail", True)):
        q = V.qa_combined(V._qa_summary(report(pre_v)), V._qa_summary(report(post_v, ["CAP_FACE"] if post_v != "PASS" else [])))
        assert q["status"] == want and q["blocking"] == blocking and q["mode"] == "report", q
        os.environ["EVA_QA_GATE"] = "report"; assert V.gate(q) == "done"                                  # report: always delivered
        os.environ["EVA_QA_GATE"] = "block"; assert V.gate(q) == ("qa_failed" if blocking else "done")     # block: only a blocking FAIL
    os.environ["EVA_QA_GATE"] = "block"
    assert V.gate(V.qa_combined({"status": "error"}, None)) == "done" and V.gate(V.qa_combined(None, None)) == "done"   # QA problems never block
    os.environ["EVA_QA_GATE"] = "report"
    # reports saved with the version
    (w / "out").mkdir(); (w / "out/preview.mp4").write_bytes(b"0"); (w / "out/report_preview.json").write_text(json.dumps({"width": 720}))
    V.qa_dir(w, "post", True).mkdir(parents=True); (V.qa_dir(w, "post", True) / "qa-report.json").write_text(json.dumps(report("WARN")))
    (V.qa_dir(w, "post", True) / "qa-summary.md").write_text("# QA")
    S = store.Local(Path(d) / "bucket"); keys, _, _ = V.outputs(S, "vtest0000001", w, True)
    saved = sorted(p.name for p in (Path(d) / "bucket/versions/vtest0000001").iterdir())
    assert keys["qa_key"] == "versions/vtest0000001/qa-report.json" and {"qa-report.json", "qa-pre-report.json", "qa-summary.md"} <= set(saved), saved
print("version QA hook tests: ok")
