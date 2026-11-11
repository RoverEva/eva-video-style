#!/usr/bin/env python3
"""Rebuild site/fonts/eva-sc-{400,700}.woff: Noto Sans CJK SC (OFL) subset to the Chinese characters the website uses.
   python3 saas/tools/build_cjk_font.py [--check]     (--check: exit 1 if the site uses a character the font lacks)
Needs fonttools and the Noto CJK fonts (/usr/share/fonts/opentype/noto/NotoSansCJK-{Regular,Bold}.ttc)."""
import subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; SITE = ROOT / "site"
CJK = lambda c: 0x3000 <= ord(c) <= 0x303F or 0x3400 <= ord(c) <= 0x9FFF or 0xFF00 <= ord(c) <= 0xFFEF   # = the @font-face unicode-range


def site_chars():
    txt = "".join(p.read_text(encoding="utf-8", errors="ignore") for p in SITE.rglob("*")
                  if p.suffix in (".js", ".json", ".html", ".css") and "demos" not in p.parts)
    return sorted({c for c in txt if CJK(c)})


def font_chars(path):
    from fontTools.ttLib import TTFont
    return set(chr(u) for u in TTFont(path).getBestCmap())


if __name__ == "__main__":
    want = site_chars()
    if "--check" in sys.argv:
        miss = [c for c in want if c not in font_chars(SITE / "fonts/eva-sc-400.woff") or c not in font_chars(SITE / "fonts/eva-sc-700.woff")]
        print(f"{len(want)} Chinese characters on the site; missing from the EVA SC subset: {''.join(miss) or 'none'}")
        sys.exit(1 if miss else 0)
    from fontTools.ttLib import TTCollection
    with tempfile.TemporaryDirectory() as d:
        chars = Path(d) / "chars.txt"; chars.write_text("".join(want), encoding="utf-8")
        for w, name in ((400, "Regular"), (700, "Bold")):
            col = TTCollection(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{name}.ttc")
            sc = next(f for f in col.fonts if f["name"].getDebugName(1).startswith("Noto Sans CJK SC")); src = Path(d) / f"sc-{w}.otf"; sc.save(src)
            subprocess.run(["pyftsubset", str(src), f"--text-file={chars}", "--flavor=woff", "--layout-features=*", "--no-hinting",
                            "--desubroutinize", f"--output-file={SITE / f'fonts/eva-sc-{w}.woff'}"], check=True)
    print(f"built eva-sc-400/700.woff with {len(want)} characters")
