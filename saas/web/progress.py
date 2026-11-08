"""EVA Video Studio · real render progress (no time-based guessing).

Workers report facts into a shared key-value store (Modal Dict in the cloud, a dict locally), one key per writer so
parallel containers never overwrite each other:
    p:<job>:<kind>:meta   render_job   {"chunks": [0, 1], "t": ts}
    p:<job>:<kind>:prep   prepare      {"done": [...stages], "cur": "asr", "t": ts}
    p:<job>:<kind>:c<i>   render_chunk {"done": frames, "total": frames, "t": ts}
    p:<job>:<kind>:fin    finish       {"done": [...stages], "cur": "music", "t": ts}
summary() turns them into a 0-99 % (100 only when the worker says done) and the five customer-facing stages.
"""
import time

PREP = [("validate", 1), ("media", 4), ("asr", 20), ("face", 3), ("plan", 4), ("page", 3)]     # 5 → 40 %
FIN = [("audio", 3), ("captions", 2), ("assemble", 4), ("music", 3), ("deliver", 2)]             # 85 → 99 %
STAGES = [("upload", "Uploaded"), ("transcribe", "Transcribing your voice"), ("plan", "Planning captions and cards"),
          ("render", "Rendering video"), ("finish", "Adding music and final checks")]
STALL_S = 240


def key(job, kind, part): return f"p:{job}:{kind}:{part}"


class Reporter:
    """callable handed to the pipeline: rep(stage, "start"|"done") or rep(stage, "frames", done, total)"""
    def __init__(self, kv, job, kind): self.kv, self.job, self.kind, self.prep, self.fin = kv, job, kind, set(), set()

    def put(self, part, val):
        try: self.kv[key(self.job, self.kind, part)] = dict(val, t=time.time())
        except Exception: pass   # progress must never break a render

    def __call__(self, stage, phase, *a):
        if stage.startswith("render_"):
            if phase == "frames": self.put("c" + str(int(stage[7:])), {"done": a[0], "total": a[1]})
            elif phase == "done": self.put("c" + str(int(stage[7:])), {"done": 1, "total": 1})
            return
        name = stage.split("_", 1)[1] if stage.startswith(("preview_", "final_")) else stage
        part, s = ("fin", self.fin) if any(name == n for n, _ in FIN) else ("prep", self.prep)
        if phase == "done": s.add(name)
        self.put(part, {"done": sorted(s), "cur": None if phase == "done" else name})


def reset(kv, job, kind, chunks):
    for part in ["prep", "fin"] + [f"c{i}" for i in range(12)]:
        try: kv.pop(key(job, kind, part), None)
        except Exception:
            try: del kv[key(job, kind, part)]
            except Exception: pass
    try: kv[key(job, kind, "meta")] = {"chunks": list(chunks), "t": time.time()}
    except Exception: pass


def _get(kv, k):
    try: return kv.get(k)
    except Exception: return None


def summary(kv, job, kind, worker):
    """worker = jobs/<job>/<kind>.json (state running/done/failed/rejected). Returns progress, stages, stalled."""
    state = (worker or {}).get("state")
    meta = _get(kv, key(job, kind, "meta")) or {}
    prep = _get(kv, key(job, kind, "prep")) or {}; fin = _get(kv, key(job, kind, "fin")) or {}
    chunks = meta.get("chunks") or []
    cs = [_get(kv, key(job, kind, f"c{i}")) or {} for i in chunks]
    pd, fd = set(prep.get("done") or []), set(fin.get("done") or [])
    w = lambda spec, done, cur, lo, hi: lo + (hi - lo) * sum(x for n, x in spec if n in done) / sum(x for _, x in spec)
    pct = 5.0 if state else 0.0
    if prep or pd: pct = w(PREP, pd, prep.get("cur"), 5, 40)
    if cs and any(c for c in cs):
        f = sum(min(1.0, c.get("done", 0) / c["total"]) if c.get("total") else 0 for c in cs) / len(cs)
        pct = max(pct, 40 + 45 * f)
    if fin or fd: pct = max(pct, 85 + 14 * sum(x for n, x in FIN if n in fd) / sum(x for _, x in FIN))
    if state == "done": pct = 100.0
    elif pct >= 100: pct = 99.0
    rendered = bool(cs) and all(c.get("total") and c.get("done", 0) >= c["total"] for c in cs)
    status = {"upload": "done",
              "transcribe": "done" if "asr" in pd else "active" if state == "running" else "pending",
              "plan": "done" if {"face", "plan", "page"} <= pd else "active" if "asr" in pd else "pending",
              "render": "done" if rendered or fd or fin.get("cur") else "active" if {"face", "plan", "page"} <= pd else "pending",
              "finish": "done" if state == "done" else "active" if (rendered or fd or fin.get("cur")) else "pending"}
    if state in ("failed", "rejected"):
        status = {k: ("failed" if v == "active" else v) for k, v in status.items()}
    last = max([x.get("t", 0) for x in [meta, prep, fin, *cs]] + [(worker or {}).get("updated_ts", 0)])
    stalled = state == "running" and last > 0 and time.time() - last > STALL_S
    return {"progress": int(pct), "stages": [{"key": k, "label": l, "status": status[k]} for k, l in STAGES],
            "stalled": stalled, "updated": last or None}
