#!/usr/bin/env python3
"""EVA Video Studio · automatic face calibration (replaces the manual step 3 of references/pipeline.md).

Detects the speaker's face on ~9 frames spread over the clip (OpenCV Haar cascade, CPU, < 1 s) and writes
EV.face = {x, y, h} as fractions of the 1920x1080 frame: x = face centre, y = head centre, h = head height
(hair top to chin). A detected face box covers brows-to-chin, so the head is estimated as 1.45x the box height,
extended upwards. Falls back to a centred default (and says so) if no face is found.

usage: face.py FRAMES_DIR OUT.json
"""
import json, sys
from pathlib import Path

DEFAULT = {"x": 0.5, "y": 0.38, "h": 0.46}


def main(frames_dir, out):
    res = dict(DEFAULT, source="default")
    try:
        import cv2
        casc = Path(getattr(cv2, "data", None).haarcascades if hasattr(cv2, "data") else "") / "haarcascade_frontalface_default.xml"
        if not casc.is_file(): raise FileNotFoundError(f"no Haar cascade at {casc}")
        det = cv2.CascadeClassifier(str(casc))
        fs = sorted(Path(frames_dir).glob("f_*.jpg"))
        picks = [fs[int(i * (len(fs) - 1) / 8)] for i in range(9)] if fs else []
        boxes = []
        for f in picks:
            im = cv2.imread(str(f)); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); hh, ww = g.shape
            faces = det.detectMultiScale(g, scaleFactor=1.1, minNeighbors=6, minSize=(ww // 14, ww // 14))
            if len(faces): x, y, w, h = max(faces, key=lambda b: b[2] * b[3]); boxes.append((x / ww, y / hh, w / ww, h / hh))
        if len(boxes) >= 3:
            med = lambda i: sorted(b[i] for b in boxes)[len(boxes) // 2]
            x, y, w, h = med(0), med(1), med(2), med(3)
            head_h = h * 1.45; top = y - h * .38; chin = y + h * 1.07
            res = {"x": round(x + w / 2, 4), "y": round((top + chin) / 2, 4), "h": round(min(.95, head_h), 4), "source": f"opencv:{len(boxes)}/9"}
    except Exception as e:
        res["warning"] = f"{type(e).__name__}: {e}"
    Path(out).write_text(json.dumps(res))
    print("face:", res)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
