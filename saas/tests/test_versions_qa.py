#!/usr/bin/env python3
"""QA hook in the version worker: reads qa-report.json (schema eva-qa/1), records it, and only with EVA_QA_GATE=block
turns a blocking FAIL into qa_failed (which releases the free preview / credits in eva_finish)."""
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "worker"))
import versions as V

with tempfile.TemporaryDirectory() as d:
    w = Path(d)
    qa, p = V.qa_result(w, "preview"); assert qa == {"status": "pending_module"} and p is None
    (w / "preview/master_qa").mkdir(parents=True)
    for verdict, blocking, want in (("PASS", False, "pass"), ("WARN", False, "warn"), ("FAIL", True, "fail")):
        (w / "preview/master_qa/qa-report.json").write_text(json.dumps({"schema": "eva-qa/1", "qa_version": "1.0", "verdict": verdict, "blocking": blocking,
            "counts": {"PASS": 20, "WARN": int(verdict == "WARN"), "FAIL": int(blocking)}, "issues": [{}] * int(verdict != "PASS")}))
        qa, p = V.qa_result(w, "preview"); assert qa["status"] == want and qa["blocking"] == blocking and p.name == "qa-report.json", qa
        os.environ["EVA_QA_GATE"] = "report"; assert V.gate(qa) == "done"                     # default: record, never block
        os.environ["EVA_QA_GATE"] = "block"; assert V.gate(qa) == ("qa_failed" if blocking else "done")
print("version QA hook tests: ok")
