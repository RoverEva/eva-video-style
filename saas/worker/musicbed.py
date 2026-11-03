#!/usr/bin/env python3
"""EVA Video Studio · background bed for one order, from rights-cleared tracks only.

    musicbed.py TRACKS_DIR PLAN.json TRANSCRIPT.js OUT.wav --mode track|mix [--tracks id1,id2,id3]

track  the customer's 1-3 chosen tracks: one per section in order (looping the list), 1 s crossfades at section cuts.
mix    AI Auto Mix: ranks the library by the talk's pace (words per second) and gives each section the next best track.
Only tracks listed in TRACKS_DIR/manifest.json with a license in CLEARED are used; anything else is refused, so a paid
video can never carry music without confirmed rights. The bed is then ducked under the voice by scripts/music.py (manual).
Prints a JSON summary (tracks used, license) on stdout.
"""
import argparse, json, subprocess, sys
from pathlib import Path

CLEARED = {"eva-original", "CC0-1.0", "licensed-commercial"}
XF = 1.0   # crossfade seconds


def load(tracks_dir):
    man = json.loads((Path(tracks_dir) / "manifest.json").read_text())
    return {t["id"]: t for t in man["tracks"] if t.get("license", man.get("license")) in CLEARED}


def pace(transcript):
    d = json.loads(Path(transcript).read_text().split("=", 1)[1].rstrip().rstrip(";"))
    words = [w for s in d["segments"] for w in s.get("words", [])]
    if len(words) < 2: return 2.3
    span = max(1.0, words[-1].get("end", words[-1]["start"]) - words[0]["start"])
    return len(words) / span


def auto_pick(lib, wps, n):
    want = "fast" if wps >= 2.9 else "medium" if wps >= 2.2 else "slow"
    order = {"fast": ["fast", "medium", "slow"], "medium": ["medium", "fast", "slow"], "slow": ["slow", "medium", "fast"]}[want]
    ranked = sorted(lib.values(), key=lambda t: (order.index(t.get("pace", "medium")), t["id"]))
    return [ranked[i % len(ranked)]["id"] for i in range(n)], want


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracks_dir"); ap.add_argument("plan"); ap.add_argument("transcript"); ap.add_argument("out")
    ap.add_argument("--mode", choices=["track", "mix"], required=True); ap.add_argument("--tracks", default="")
    a = ap.parse_args(argv)
    lib = load(a.tracks_dir)
    if not lib: raise SystemExit("no rights-cleared tracks in " + a.tracks_dir)
    plan = json.loads(Path(a.plan).read_text()); secs = plan["sections"]; dur = float(plan["end"])
    info = {"mode": a.mode}
    if a.mode == "mix":
        ids, info["pace"] = auto_pick(lib, pace(a.transcript), len(secs))
    else:
        req = [t for t in a.tracks.split(",") if t][:3]
        bad = [t for t in req if t not in lib]
        if not req or bad: raise SystemExit(f"tracks not available or not cleared: {bad or 'none chosen'}")
        ids = [req[i % len(req)] for i in range(len(secs))]
    # merge neighbouring sections that use the same track (no crossfade into itself)
    segs = []
    for s, tid in zip(secs, ids):
        if segs and segs[-1][2] == tid: segs[-1][1] = s["t1"]
        else: segs.append([s["t0"], s["t1"], tid])
    # each segment plays its track from the top, padded by the crossfade; ffmpeg acrossfade chains them
    cmd, flt = ["ffmpeg", "-loglevel", "error", "-y"], []
    for i, (t0, t1, tid) in enumerate(segs):
        ln = (t1 - t0) + (XF if i < len(segs) - 1 else 0)
        cmd += ["-t", f"{ln + .05:.3f}", "-i", str(Path(a.tracks_dir) / lib[tid]["file"])]
        flt.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
    cur = "a0"
    for i in range(1, len(segs)):
        flt.append(f"[{cur}][a{i}]acrossfade=d={XF}:c1=tri:c2=tri[x{i}]"); cur = f"x{i}"
    flt.append(f"[{cur}]atrim=0:{dur:.3f},asetpts=N/SR/TB[out]")
    cmd += ["-filter_complex", ";".join(flt), "-map", "[out]", a.out]
    subprocess.run(cmd, check=True)
    info.update({"tracks": [s[2] for s in segs], "titles": [lib[s[2]]["title"] for s in segs], "license": "eva-original"
                 if all(lib[s[2]].get("license", "eva-original") == "eva-original" for s in segs) else "cleared"})
    print(json.dumps(info)); return 0


if __name__ == "__main__":
    sys.exit(main())
