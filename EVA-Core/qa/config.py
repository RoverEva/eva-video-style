"""Thresholds: defaults < category < template < user override file. Values are plain JSON (qa/thresholds.json)."""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_BASE = json.loads((HERE / "thresholds.json").read_text(encoding="utf-8"))


def merge(a, b):
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if k.startswith("_"): continue
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


class Config:
    def __init__(self, override=None, category=None):
        base = _BASE
        if override:
            o = json.loads(Path(override).read_text(encoding="utf-8")) if isinstance(override, (str, Path)) else override
            base = merge(base, {k: o[k] for k in ("defaults", "categories", "templates") if k in o})
            if not any(k in o for k in ("defaults", "categories", "templates")): base = merge(base, {"defaults": o})
        self.raw, self.category, self._cache = base, category, {}

    def known_templates(self):
        return set(self.raw.get("templates", {}))

    def for_template(self, tpl=None):
        """full threshold dict for one template (None = defaults + category)"""
        key = tpl or ""
        if key not in self._cache:
            d = merge(self.raw["defaults"], self.raw.get("categories", {}).get(self.category or "", {}))
            self._cache[key] = merge(d, self.raw.get("templates", {}).get(tpl or "", {}))
        return self._cache[key]

    def __getitem__(self, section):
        return self.for_template(None)[section]
