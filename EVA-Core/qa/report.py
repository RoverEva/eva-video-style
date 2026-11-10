"""QA report: issues (check id, severity, time range, scene/template, message, evidence, fix) -> qa-report.json + qa-summary.md."""
import json, time
from pathlib import Path

from . import __version__

ORDER = {"PASS": 0, "WARN": 1, "FAIL": 2}
MAX_EVIDENCE_PER_CHECK = 3


def _t(t):
    if t is None: return None
    if isinstance(t, (list, tuple)): return [round(float(t[0]), 3), round(float(t[1]), 3)]
    return [round(float(t), 3), round(float(t), 3)]


class Report:
    def __init__(self, stage, out_dir, context=None):
        self.stage, self.out = stage, Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.context = context or {}
        self.issues, self.ran_checks, self.not_run, self.info = [], {}, {}, {}
        self._ev_count = {}
        self.t0 = time.time()

    # ---- recording ----
    def ran(self, check, note=None):
        self.ran_checks.setdefault(check, note)

    def skip(self, check, reason):
        """a check that could not run (missing input/backend): listed so nothing is silently treated as verified"""
        if check not in self.ran_checks: self.not_run[check] = reason

    def add(self, check, severity, message, t=None, fix=None, evidence=None, scene=None, template=None, data=None):
        assert severity in ("WARN", "FAIL"), severity
        self.ran(check)
        self.issues.append({"check": check, "severity": severity, "t": _t(t), "scene": scene, "template": template,
                            "message": message, "evidence": evidence, "fix": fix, "data": data or {}})

    def evidence(self, check, t, image):
        """save an evidence JPG (BGR numpy image); at most MAX_EVIDENCE_PER_CHECK per check id. Returns the relative path."""
        n = self._ev_count.get(check, 0)
        if n >= MAX_EVIDENCE_PER_CHECK or image is None: return None
        import cv2
        self._ev_count[check] = n + 1
        h, w = image.shape[:2]; s = min(1.0, 960 / max(h, w))
        if s < 1: image = cv2.resize(image, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
        rel = f"evidence/{check.lower()}_{float(t or 0):07.2f}.jpg"
        (self.out / "evidence").mkdir(exist_ok=True)
        cv2.imwrite(str(self.out / rel), image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return rel

    # ---- output ----
    def merged(self):
        """consecutive issues of the same check/severity/scene (gap <= 1.2 s) become one issue with a time range"""
        out = []
        key = lambda i: (i["check"], i["severity"], i["scene"], i["template"], i["fix"])
        for it in sorted(self.issues, key=lambda i: (i["check"], i["severity"], (i["t"] or [-1])[0])):
            prev = out[-1] if out else None
            if (prev and key(prev) == key(it) and prev["t"] and it["t"] and it["t"][0] - prev["t"][1] <= 1.2
                    and prev["message"].split(":")[0] == it["message"].split(":")[0]):
                prev["t"][1] = max(prev["t"][1], it["t"][1]); prev["count"] = prev.get("count", 1) + 1
                prev["evidence"] = prev["evidence"] or it["evidence"]
                for k, v in it["data"].items():   # keep the worst value of numeric measurements
                    if isinstance(v, (int, float)) and isinstance(prev["data"].get(k), (int, float)) and k.startswith(("max_", "worst_")):
                        prev["data"][k] = max(prev["data"][k], v)
                continue
            out.append(dict(it, t=list(it["t"]) if it["t"] else None))
        return sorted(out, key=lambda i: (-ORDER[i["severity"]], (i["t"] or [0])[0], i["check"]))

    def verdict(self):
        sev = max([ORDER[i["severity"]] for i in self.issues] or [0])
        return {0: "PASS", 1: "WARN", 2: "FAIL"}[sev]

    def to_dict(self):
        issues = self.merged()
        failed = {i["check"] for i in issues}
        checks = []
        for c, note in sorted(self.ran_checks.items()):
            sev = max([ORDER[i["severity"]] for i in issues if i["check"] == c] or [0])
            checks.append({"check": c, "severity": {0: "PASS", 1: "WARN", 2: "FAIL"}[sev], **({"note": note} if note and c not in failed else {})})
        v = self.verdict()
        return {"schema": "eva-qa/1", "qa_version": __version__, "stage": self.stage, "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "verdict": v, "blocking": v == "FAIL",
                "counts": {s: sum(1 for c in checks if c["severity"] == s) for s in ("PASS", "WARN", "FAIL")},
                "issues": issues, "checks": checks,
                "not_run": [{"check": c, "reason": r} for c, r in sorted(self.not_run.items())],
                "context": self.context, "info": self.info, "elapsed_s": round(time.time() - self.t0, 2)}

    def write(self, name="qa-report.json"):
        d = self.to_dict()
        (self.out / name).write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        (self.out / name.replace("report", "summary").replace(".json", ".md")).write_text(summary_md(d), encoding="utf-8")
        return d


def _fmt_t(t):
    if not t: return "—"
    return f"{t[0]:.2f}s" if abs(t[1] - t[0]) < 1e-3 else f"{t[0]:.2f}–{t[1]:.2f}s"


def summary_md(d):
    L = [f"# Eva Video QA · {d['stage']} · **{d['verdict']}**", "",
         f"{d['counts']['FAIL']} failed · {d['counts']['WARN']} warnings · {d['counts']['PASS']} passed checks"
         + (" · **delivery blocked**" if d["blocking"] else ""), ""]
    if d["issues"]:
        L += ["| Severity | Check | Time | Scene | Problem | Fix | Evidence |", "|---|---|---|---|---|---|---|"]
        for i in d["issues"]:
            sc = "" if i["scene"] is None else f"{i['scene']}" + (f" ({i['template']})" if i["template"] else "")
            msg = i["message"] + (f" ×{i['count']}" if i.get("count") else "")
            L.append(f"| {i['severity']} | {i['check']} | {_fmt_t(i['t'])} | {sc} | {msg} | {i['fix'] or ''} | {i['evidence'] or ''} |".replace("\n", " "))
        L.append("")
    ok = [c["check"] for c in d["checks"] if c["severity"] == "PASS"]
    if ok: L += ["Passed: " + ", ".join(ok), ""]
    if d["not_run"]: L += ["Not run (unverified): " + "; ".join(f"{n['check']} ({n['reason']})" for n in d["not_run"]), ""]
    return "\n".join(L)
