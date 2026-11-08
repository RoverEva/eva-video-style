"""Small on-disk cache for the expensive, deterministic parts of QA (the full decode pass, face tracking per frame).

Keys include each input file's path, size and modification time plus the analysis parameters, so a changed file or
parameter is simply a miss. Thresholds are NOT part of the cached data: re-running QA with other thresholds reuses
the measurements and re-judges them.

    EVA_QA_CACHE=off              disable
    EVA_QA_CACHE_DIR=/some/dir    location (default ~/.cache/eva-qa)
"""
import hashlib, json, os
from pathlib import Path

VERSION = "3"   # bump when a cached measurement changes meaning


def _dir():
    if os.environ.get("EVA_QA_CACHE", "").lower() in ("0", "off", "no", "false"): return None
    d = Path(os.environ.get("EVA_QA_CACHE_DIR") or Path.home() / ".cache/eva-qa")
    try:
        d.mkdir(parents=True, exist_ok=True); return d
    except OSError:
        return None


def file_sig(path):
    try:
        st = os.stat(path); return [str(Path(path).resolve()), st.st_size, int(st.st_mtime_ns)]
    except OSError:
        return [str(path), None, None]


def key(*parts):
    return hashlib.sha1(json.dumps([VERSION, *parts], sort_keys=True, default=str).encode()).hexdigest()


def get(k):
    d = _dir()
    if not d: return None
    f = d / f"{k}.json"
    try:
        return json.loads(f.read_text()) if f.exists() else None
    except (OSError, ValueError):
        return None


def put(k, value):
    d = _dir()
    if not d: return value
    try:
        tmp = d / f".{k}.{os.getpid()}.tmp"; tmp.write_text(json.dumps(value)); tmp.replace(d / f"{k}.json")
    except OSError:
        pass
    return value


def memo(k, fn):
    v = get(k)
    return v if v is not None else put(k, fn())
