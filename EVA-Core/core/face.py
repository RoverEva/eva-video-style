#!/usr/bin/env python3
"""Local face calibration for the independent EVA Core pipeline."""

import json
import sys
from pathlib import Path


DEFAULT = {"x": 0.5, "y": 0.38, "h": 0.46}


def main(frames_dir, out):
    result = dict(DEFAULT, source="default")
    try:
        import cv2
        cascade = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        if not cascade.is_file():
            raise FileNotFoundError(f"no Haar cascade at {cascade}")
        detector = cv2.CascadeClassifier(str(cascade))
        frames = sorted(Path(frames_dir).glob("f_*.jpg"))
        picks = [frames[int(i * (len(frames) - 1) / 8)] for i in range(9)] if frames else []
        boxes = []
        for frame in picks:
            image = cv2.imread(str(frame))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(width // 14, width // 14))
            if len(faces):
                x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
                boxes.append((x / width, y / height, w / width, h / height))
        if len(boxes) >= 3:
            median = lambda i: sorted(box[i] for box in boxes)[len(boxes) // 2]
            x, y, w, h = median(0), median(1), median(2), median(3)
            top, chin = y - h * .38, y + h * 1.07
            result = {"x": round(x + w / 2, 4), "y": round((top + chin) / 2, 4),
                      "h": round(min(.95, h * 1.45), 4), "source": f"opencv:{len(boxes)}/9"}
    except Exception as exc:
        result["warning"] = f"{type(exc).__name__}: {exc}"
    Path(out).write_text(json.dumps(result), encoding="utf-8")
    print("face:", result)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
