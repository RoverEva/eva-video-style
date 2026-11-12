#!/usr/bin/env python3
"""Build EVA-Core.zip reproducibly from a release-source checkout and (optionally) verify it against SHA256SUMS.

    python3 -B EVA-Core/tools/packages/build_core.py OUT_DIR [--check SHA256SUMS]

Payload = every file under EVA-Core/ (no __pycache__), including EVA-Core/checksums.sha256, which must already cover
every other file. The archive is written by package_common.write_zip (stored members, sorted, fixed time and mode),
so any OS / Python / compression library produces the same bytes."""
from __future__ import annotations

import argparse, sys
from pathlib import Path

sys.dont_write_bytecode = True
import package_common as P  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("out", type=Path); ap.add_argument("--check", type=Path)
    a = ap.parse_args()
    core = ROOT / "EVA-Core"
    files = {str(p.relative_to(ROOT)): p.read_bytes() for p in sorted(core.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    out = a.out / "EVA-Core.zip"; P.write_zip(out, files)
    info = P.verify_checksums(out); print(f"EVA-Core.zip: {len(files)} members, {info['files']} checksummed, sha256 {info['sha256']}")
    if a.check:
        want = next(line.split()[0] for line in a.check.read_text().splitlines() if line.endswith("  EVA-Core.zip"))
        if want != info["sha256"]:
            print(f"MISMATCH: SHA256SUMS expects {want}", file=sys.stderr); return 1
        print("matches SHA256SUMS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
