#!/usr/bin/env python3
"""Keyframe preview: one frame per card (once its text is typed) + the hook beats, 1 s each, with music.
   keyframes.py script.json music out.mp4"""
import sys, os, argparse, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_long as R, cv2, numpy as np
p, music, out = sys.argv[1:4]
sc = R.scene(argparse.Namespace(script=p, music=music, eighth=None, logo=None))
ts = [sc.T(m) for m in (1.5, 4.5, 12, 15.5, 17, 23, 27, 31, 35, 38.5, 41, 47, 54)]
for s in sc.segs:
    ts.append(sc.T(s['start'] + 1.5))
    for (cn, ce, c) in s['cards']: ts.append(sc.T(cn + ce * 0.72))
ts += [sc.T(sc.outro_n + 6), sc.T(sc.outro_n + 18)]
tmp = tempfile.mkdtemp(); per = 1.0
p_ = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1920x1080', '-r', '24', '-i', '-',
                       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp + '/v.mp4'], stdin=subprocess.PIPE)
for t in ts:
    im = sc.frame(t).copy()
    mm, ss = divmod(t, 60)
    cv2.putText(im, f'{int(mm)}:{ss:05.2f}', (24, 1056), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2, cv2.LINE_AA)
    for _ in range(int(per * 24)): p_.stdin.write(im.tobytes())
p_.stdin.close(); p_.wait()
dur = len(ts) * per
R.build_music(music, dur + 1, tmp + '/a.m4a', sc.s.get('music_start_e8', 0))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp + '/v.mp4', '-i', tmp + '/a.m4a', '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest', out], check=True)
print(out, len(ts), 'keyframes')
