#!/usr/bin/env python3
"""Template Gallery checks.

    python3 saas/tests/test_gallery.py [ASSET_DIR]

Always (no files needed): saas/web/gallery.json is consistent with the selectable templates — T19 never offered, every
selectable template has an approved asset set for at least one aspect, pending assets are never signed, keys sit under
the staging prefix, no original/superseded/CN-EN demo is referenced.
With ASSET_DIR (output of saas/tools/template_previews.py): every approved file exists, sha256/bytes match gallery.json,
size budgets (WebP <= 60 KB, 5 s clip <= 400 KB, 15 s preview <= 2 MB), dimensions/orientation per aspect, WebP format,
clip 5.0 s muted H.264 faststart 30 fps, full preview 15 s.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "web"))
import api_v2 as A                                   # noqa: E402

G = A.GALLERY
BUDGET = {"thumb": 60_000, "clip5": 400_000, "full15": 2_000_000}
DIMS = {"16:9": {"thumb": (640, 360), "clip5": (640, 360), "full15": (960, 540)},
        "9:16": {"thumb": (360, 640), "clip5": (360, 640), "full15": (540, 960)}}
ok = lambda c, m: (print(("PASS " if c else "FAIL ") + m), c)[1]
fails = 0


def check(c, m):
    global fails
    if not ok(c, m): fails += 1


def top_atoms(f):
    """top-level MP4 box types in file order (moov before mdat = plays before fully downloaded)"""
    import struct
    b = Path(f).read_bytes(); i, out = 0, []
    while i + 8 <= len(b):
        n, t = struct.unpack(">I4s", b[i:i + 8]); n = struct.unpack(">Q", b[i + 8:i + 16])[0] if n == 1 else (n or len(b) - i)
        out.append(t.decode("latin1")); i += n
    return out


class FakeStore:
    def presign_get(self, key, seconds=3600, filename=None): return f"https://r2.example/{key}?ttl={seconds}"


# ── list / API rules ──
ids = [t["id"] for t in G["templates"]]
check("T19" not in A.TEMPLATES and "T19" not in [t["id"] for t in A.gallery_payload(FakeStore())["templates"]], "T19 is not selectable and not offered by the gallery")
check(set(ids) == set(A.TEMPLATES), f"gallery covers exactly the selectable launch templates {sorted(A.TEMPLATES)}")
p = A.gallery_payload(FakeStore())
for t in p["templates"]:
    check(bool(t["assets"]), f"{t['id']}: at least one approved aspect offered ({', '.join(t['assets'])})")
    for ar, a in t["assets"].items():
        check(set(a) == {"thumb", "clip5", "full15"}, f"{t['id']} {ar}: thumb + 5 s clip + 15 s preview")
        check(all(v["url"].startswith(f"https://r2.example/{A.GALLERY_PREFIX}{t['id']}/") and "ttl=900" in v["url"] for v in a.values()),
              f"{t['id']} {ar}: signed 15-min links under {A.GALLERY_PREFIX}")
# customer availability: the order API itself refuses T19 (not just the UI)
try: A.Accounts.options(None, {"aspect": "9:16", "templates": ["T19"], "template_mode": "single"}); t19_refused = False
except ValueError: t19_refused = True
check(t19_refused, "order API refuses a T19-only request")
o = A.Accounts.options(None, {"aspect": "16:9", "templates": ["T23", "T19", "T21"], "template_mode": "multi"})
check(o["templates"] == ["T23", "T21"], f"T19 dropped from a mixed request: {o['templates']}")
sys.path.insert(0, str(HERE.parent / "worker")); import planner as PLN   # noqa: E402
check("T19" not in PLN.TEMPLATES and PLN.choose_templates("single", ["T19"], 10) == ["T17"], "worker planner never renders T19")
pending = [(t["id"], ar) for t in G["templates"] for ar, a in t["assets"].items() if a["status"] != "approved"]
offered = {(t["id"], ar) for t in p["templates"] for ar in t["assets"]}
check(not (set(pending) & offered), f"pending assets never signed: {pending}")
srcs = [a["source"] for t in G["templates"] for a in t["assets"].values()]
check(not any("superseded" in s or "CN-EN" in s for s in srcs), "no superseded or CN-EN demo used")
t17 = next(t for t in G["templates"] if t["id"] == "T17")
check(t17["assets"]["9:16"]["source"].endswith("v2-face-safe.mp4") and t17["assets"]["9:16"]["status"] == "approved", "T17 9:16 = approved face-safe v2")

# ── files ──
if len(sys.argv) > 1:
    d = Path(sys.argv[1])
    def probe(f):
        return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,format_name:stream=codec_type,codec_name,width,height,r_frame_rate",
                                          "-of", "json", str(f)], capture_output=True, text=True).stdout)
    for t in G["templates"]:
        for ar, a in t["assets"].items():
            for k in ("thumb", "clip5", "full15"):
                f = d / a[k]["key"]; tag = f"{t['id']} {ar} {k}"
                if not f.exists(): check(False, f"{tag}: missing {f}"); continue
                check(hashlib.sha256(f.read_bytes()).hexdigest() == a[k]["sha256"] and f.stat().st_size == a[k]["bytes"], f"{tag}: sha256 + size match gallery.json")
                check(f.stat().st_size <= BUDGET[k], f"{tag}: {f.stat().st_size / 1000:.0f} KB <= {BUDGET[k] // 1000} KB")
                pr = probe(f); v = next(s for s in pr["streams"] if s["codec_type"] == "video")
                check((v["width"], v["height"]) == DIMS[ar][k], f"{tag}: {v['width']}x{v['height']} ({ar})")
                if k == "thumb": check(v["codec_name"] == "webp", f"{tag}: WebP")
                else:
                    dur = float(pr["format"]["duration"]); want = 5.0 if k == "clip5" else 15.03
                    check(abs(dur - want) < .08 and v["codec_name"] == "h264" and v["r_frame_rate"] == "30/1", f"{tag}: {dur:.2f} s H.264 30 fps")
                    if k == "clip5": check(not any(s["codec_type"] == "audio" for s in pr["streams"]), f"{tag}: muted")
                    order = top_atoms(f); check("moov" in order and "mdat" in order and order.index("moov") < order.index("mdat"), f"{tag}: faststart ({' '.join(order)})")
print("gallery tests:", "ok" if not fails else f"{fails} FAILED"); sys.exit(1 if fails else 0)
