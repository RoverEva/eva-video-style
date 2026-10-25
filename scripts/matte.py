#!/usr/bin/env python3
"""Cut the presenter out of her real background (for T19 background swaps).

Writes RGBA WebP frames that keep the ORIGINAL pixel colours (natural face colour) with an AI alpha matte.
Model: Robust Video Matting (MobileNetV3, ONNX). It is GPL-3.0 licensed, so it is downloaded on first use
into ~/.cache/eva-video-style/ and never shipped with this skill.

usage: matte.py FRAMES_DIR FIRST LAST OUT_DIR [--ratio 0.25]
  FRAMES_DIR  30 fps JPG sequence from extract_frames.sh (f_00000.jpg ...)
  FIRST LAST  absolute frame numbers (inclusive FIRST, exclusive LAST)
  OUT_DIR     receives f_XXXXX.webp with the same absolute numbering
Needs: numpy, opencv-python, onnxruntime.  ~4 fps at 1080p on a laptop CPU.
"""
import os, sys, urllib.request
import numpy as np, cv2, onnxruntime as ort

URL = 'https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx'

def model_path():
    d = os.path.expanduser('~/.cache/eva-video-style'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'rvm_mobilenetv3_fp32.onnx')
    if not os.path.exists(p):
        print('downloading matting model (GPL-3.0, Robust Video Matting) ...'); urllib.request.urlretrieve(URL, p)
    return p

def main():
    a = sys.argv[1:]
    if len(a) < 4: sys.exit(__doc__)
    src, first, last, out = a[0], int(a[1]), int(a[2]), a[3]
    ratio = float(a[a.index('--ratio') + 1]) if '--ratio' in a else .25
    os.makedirs(out, exist_ok=True)
    s = ort.InferenceSession(model_path(), providers=['CPUExecutionProvider'])
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4; ds = np.array([ratio], np.float32)
    # warm the recurrent state on a few frames before FIRST so the first written matte is already stable
    for f in list(range(max(0, first - 8), first)) + list(range(first, last)):
        im = cv2.imread(os.path.join(src, 'f_%05d.jpg' % f))
        if im is None: continue
        x = (cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255).transpose(2, 0, 1)[None]
        _, pha, *rec = s.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': ds})
        if f < first: continue
        al = np.clip(pha[0, 0] * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(out, 'f_%05d.webp' % f), np.dstack([im, al]), [cv2.IMWRITE_WEBP_QUALITY, 92])
        if (f - first) % 60 == 0: print('matte', f)
    print('done', last - first, 'frames ->', out)

if __name__ == '__main__': main()
