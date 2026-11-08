#!/usr/bin/env python3
"""Per-video cost from MEASURED stage times/CPU (saas/tests/image_qa_check.py summaries, e.g. from the Modal staging run).

Compute is priced the way Modal bills: per container, max(reserved cores x wall, used core-seconds) x CPU price, plus
reserved memory x wall x memory price, using the production allocation of each function (saas/modal_app.py RES):
  prepare (ASR, face, plan) + pre-render QA  → `prepare` container (3 cores, 6 GiB)
  render chunks                              → `render_chunk` containers (1 core, 3 GiB each, run in parallel)
  finish (audio, captions, assembly) + post-render QA → `finish` container (2 cores, 4 GiB)
  orchestrator                               → `render_job` (0.25 core, 0.5 GiB) for the whole wall time
Storage: R2 $0.015/GB-month for the retention period (preview 30 d, HD 90 d). AI: planner tokens x price (0 if no key).

usage: cost_report.py SUMMARY.json [...]  → markdown table on stdout, JSON on stderr-free --json FILE
"""
import json, sys
from pathlib import Path

CPU_S, MEM_GIB_S = 0.0000131, 0.00000222            # Modal list prices (checked 2026-11-08)
RES = {"prepare": (3.0, 6.0), "render_chunk": (1.0, 3.0), "finish": (2.0, 4.0), "render_job": (0.25, 0.5)}
R2_GB_MONTH, RETAIN = 0.015, {"preview": 30, "hd": 90}
AI_PER_MTOK = {"input": 1.0, "output": 5.0}        # Haiku-class planner model, USD per million tokens (estimate)


VCPU_PER_CORE = 2                                   # Modal bills physical cores (2 vCPU); rusage counts vCPU-seconds


def container(fn, wall, used):
    used = used / VCPU_PER_CORE
    c, m = RES[fn]; wall_prod = max(wall, used / c)   # a container with fewer cores than the test box runs longer
    return max(c * wall_prod, used) * CPU_S + m * wall_prod * MEM_GIB_S, wall_prod


def price(run, kind):
    s, u = run["seconds"], run.get("cpu_s") or {}
    prep, w_prep = container("prepare", s["prepare"] + s["qa_pre"], u.get("prepare", 0) + u.get("qa_pre", 0))
    n = max(1, run.get("chunks") or 1); per = (u.get("render") or s["render"]) / n
    rend = n * container("render_chunk", per, per)[0]
    fin, w_fin = container("finish", s["finish"] + s["qa_post"], u.get("finish", 0) + u.get("qa_post", 0))
    wall = w_prep + per + w_fin + 10                     # chunks in parallel; +10 s scheduling
    orch = container("render_job", wall, 0)[0]
    qa = (container("prepare", s["qa_pre"], u.get("qa_pre", 0))[0] + container("finish", s["qa_post"], u.get("qa_post", 0))[0])
    asr_s = run.get("asr_s") or 0
    asr = container("prepare", asr_s, asr_s * 3 * VCPU_PER_CORE)[0] if asr_s else 0.0     # upper bound: ASR keeps all 3 cores busy
    storage = (run.get("output_bytes") or 0) / 1e9 * R2_GB_MONTH * RETAIN[kind] / 30
    us = run.get("planner_usage") or {}
    ai = us.get("input_tokens", 0) / 1e6 * AI_PER_MTOK["input"] + us.get("output_tokens", 0) / 1e6 * AI_PER_MTOK["output"]
    total = prep + rend + fin + orch + storage + ai
    return {"compute": round(prep + rend + fin + orch, 5), "of_which_asr": round(asr, 5), "of_which_render": round(rend, 5),
            "of_which_qa": round(qa, 5), "storage": round(storage, 6), "ai": round(ai, 5), "total": round(total, 5),
            "est_wall_s": round(wall), "chunks": n}


def main(files):
    rows = []
    for f in files:
        d = json.loads(Path(f).read_text()); d = d.get("summary", d)
        for kind, run in (d.get("runs") or {}).items():
            if "seconds" not in run: continue
            rows.append(dict(file=Path(f).stem, kind=kind, size="x".join(map(str, run.get("size") or [])), duration=run.get("duration"),
                             qa=run["qa"]["status"], **price(run, kind)))
    print("| run | kind | size | s | QA | compute $ | ASR $ | render $ | QA $ | storage $ | AI $ | total $ | est. wall |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['file']} | {r['kind']} | {r['size']} | {r['duration']} | {r['qa']} | {r['compute']:.4f} | {r['of_which_asr']:.4f} | "
              f"{r['of_which_render']:.4f} | {r['of_which_qa']:.4f} | {r['storage']:.5f} | {r['ai']:.4f} | **{r['total']:.4f}** | {r['est_wall_s']} s |")
    Path("cost_report.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1:])
