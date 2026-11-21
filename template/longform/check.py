#!/usr/bin/env python3
"""Smoke-test a script: render one still in the middle of every chapter (+ hook + outro) to catch crashes."""
import sys, os, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_long as R, cv2
for p in sys.argv[1:]:
    sc = R.scene(argparse.Namespace(script=p, music='media/Vibecoding_music.mp3', eighth=None, logo=None))
    ts = [4.0] + [sc.T((s['start'] + s['end']) / 2) for s in sc.segs] + [sc.T(sc.outro_n + 18)]
    od = '/tmp/chk/' + os.path.basename(p)[:-5]; os.makedirs(od, exist_ok=True)
    for t in ts: cv2.imwrite(f'{od}/{t:07.2f}.jpg', cv2.resize(sc.frame(t), (640, 360)))
    print(f"OK {sc.s['title']} {sc.duration/60:.2f}min cps={sc.cps:.1f}", flush=True)
