#!/usr/bin/env python3
"""Contact sheet of card mid-points: sheet.py script.json first count out.jpg [frac]"""
import sys, os, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_long as R, cv2, numpy as np
p, a, k, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]; fr = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
sc = R.scene(argparse.Namespace(script=p, music='media/Vibecoding_music.mp3', eighth=None, logo=None))
cards = [c for s in sc.segs for c in s['cards']][a:a + k]; ims = []
for (cn, ce, c) in cards:
    t = sc.T(cn + ce * fr); im = cv2.resize(sc.frame(t), (640, 360))
    cv2.putText(im, f"{c['_shot']} {c['vis']}", (8, 24), 0, 0.7, (255, 255, 255), 2); ims.append(im)
ims += [np.zeros_like(ims[0])] * (-len(ims) % 3)
cv2.imwrite(out, np.vstack([np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
