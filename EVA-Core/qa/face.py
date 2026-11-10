"""Presenter face: detection in the SOURCE footage, and tracking of that face into each RENDERED frame.

Why track instead of detecting faces in the render: rendered frames are stylised (cut-outs, rings, grades, text), where
generic face detectors are least reliable. The source footage is a plain talking head, so the face is detected there
(OpenCV Haar cascade in the worker image, scikit-image's bundled LBP cascade as a fallback, or the job's face
calibration), and that exact face patch is then found in the render by multi-scale normalised cross-correlation.
The match gives position, scale (subject enlargement), aspect (stretch), the part outside the frame (crop) and a
per-cell visibility map (occlusion by text/graphics/window edges) with a confidence score. Low confidence -> WARN only.
"""
import math

import cv2
import numpy as np

# head box from a frontal-face detector box (brows-to-chin square): same geometry as saas/worker/face.py
HEAD_UP, HEAD_DOWN, HEAD_WIDE = .38, 1.07, 1.2


class Detector:
    def __init__(self, calibration=None):
        self.name, self._d = None, None
        self.calibration = calibration
        try:
            import os
            path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(path):   # some OpenCV wheels ship without the cascade files
                c = cv2.CascadeClassifier(path)
                if not c.empty(): self._d, self.name = c, "opencv-haar"
        except Exception:
            pass
        if self._d is None:
            try:
                from skimage import data
                from skimage.feature import Cascade
                self._d, self.name = Cascade(data.lbp_frontal_face_cascade_filename()), "skimage-lbp"
            except Exception:
                pass
        if self._d is None: self.name = "calibration" if calibration else None

    def detect_all(self, bgr):
        """candidate face boxes [(x, y, w, h, weight)] in pixels, most confident first"""
        if self._d is None or self.name == "calibration": return []
        H, W = bgr.shape[:2]; s = 360 / W
        g = cv2.cvtColor(cv2.resize(bgr, (360, int(round(H * s))), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        if self.name == "opencv-haar":
            # rank by the cascade's own confidence, not by size: on a plain talking head Haar sometimes also fires on a
            # large textured patch (e.g. a T-shirt), and "largest box" then picks that instead of the face
            fs, _, wts = self._d.detectMultiScale3(g, scaleFactor=1.1, minNeighbors=6, minSize=(24, 24), outputRejectLevels=True)
            boxes = [tuple(map(int, b)) + (float(np.ravel(w)[0]),) for b, w in zip(fs, wts)]
        else:
            d = self._d.detect_multi_scale(img=g / 255.0, scale_factor=1.15, step_ratio=1, min_size=(24, 24), max_size=(330, 330))
            boxes = [(int(b["c"]), int(b["r"]), int(b["width"]), int(b["height"]), float(b["width"] * b["height"])) for b in d]
        boxes.sort(key=lambda b: -b[4])
        return [(x / s, y / s, w / s, h / s, wt) for x, y, w, h, wt in boxes]

    def detect(self, bgr):
        """most confident face box (x, y, w, h) in pixels, or None"""
        b = self.detect_all(bgr)
        return tuple(b[0][:4]) if b else None

    def from_calibration(self, size):
        """face box from EV.face {x, y, h} (head centre / head height as fractions of the source frame)"""
        c = self.calibration
        if not c: return None
        W, H = size; hh = c["h"] * H; fh = hh / (HEAD_UP + HEAD_DOWN); top = c["y"] * H - hh / 2
        return (c["x"] * W - fh / 2, top + HEAD_UP * fh, fh, fh)


def consistent(boxes, calibration_box=None, max_shift=.6, max_size=1.45):
    """per-sample source face boxes -> the same list with outliers replaced.
    A presenter's face moves little between samples; a box whose centre is more than `max_shift` face widths from the
    reference (calibration box, else the median of all detections), or whose size differs by more than `max_size`x,
    is a false detection (shirt, hands, background). Each sample takes its best candidate near the reference, or the
    reference itself. Returns [(box, how)] with how in {detector, consistent, reference}."""
    picks = [c for c in boxes if c]
    if calibration_box: ref = calibration_box
    elif picks:
        firsts = [c[0] for c in picks]
        ref = tuple(float(np.median([b[i] for b in firsts])) for i in range(4))
    else: return [(None, None) for _ in boxes]
    rx, ry, rw, rh = ref[:4]
    ok = lambda b: (abs(b[0] + b[2] / 2 - rx - rw / 2) <= max_shift * rw and abs(b[1] + b[3] / 2 - ry - rh / 2) <= max_shift * rh
                    and 1 / max_size <= b[2] / rw <= max_size)
    out = []
    for i, cands in enumerate(boxes):
        good = [b for b in (cands or []) if ok(b)]
        if good: out.append((tuple(good[0][:4]), "detector" if cands[0] is good[0] else "consistent"))
        else: out.append((tuple(ref[:4]), "reference"))
    return out


def head_from_face(b):
    x, y, w, h = b
    return (x + w / 2 - w * HEAD_WIDE / 2, y - HEAD_UP * h, w * HEAD_WIDE, h * (HEAD_UP + HEAD_DOWN))


def _ncc(a, b):
    a = a.astype(np.float32) - a.mean(); b = b.astype(np.float32) - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 1e-6 else 0.0


def track(src_bgr, face_box, out_bgr, long_side=720, scales=(0.12, 3.6, 44)):
    """find the source face patch in the rendered frame.
    Returns None if the face patch is unusable, else a dict:
      score     best NCC (0..1) of the patch at the best position (part outside the frame counts as missing)
      inframe   NCC over the part of the patch that lies inside the frame
      scale     output px per source px; aspect  width/height distortion of the face vs the source (1 = none)
      box       face box in output pixels (x, y, w, h), may extend outside the frame
      out_frac  fraction of the face box outside the frame;  visible  fraction of textured cells that match
      cells     per-cell visibility grid (4x4, None = untextured cell)"""
    H, W = out_bgr.shape[:2]; ds = min(1.0, long_side / max(H, W))
    out = cv2.cvtColor(cv2.resize(out_bgr, (round(W * ds), round(H * ds)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    sg = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2GRAY)
    fx, fy, fw, fh = face_box
    # inner face patch (8% inset keeps background out of cut-out templates)
    ix, iy, iw, ih = fx + fw * .08, fy + fh * .04, fw * .84, fh * .92
    x0, y0, x1, y1 = int(max(0, ix)), int(max(0, iy)), int(min(sg.shape[1], ix + iw)), int(min(sg.shape[0], iy + ih))
    if x1 - x0 < 24 or y1 - y0 < 24: return None
    tpl = sg[y0:y1, x0:x1]
    if tpl.std() < 8: return None
    oh, ow = out.shape; fill = int(out.mean())
    best = (-2, None)

    def try_scale(s, a=1.0):
        tw, th = int(round((x1 - x0) * s * ds * a)), int(round((y1 - y0) * s * ds / a))
        # a face patch under ~1/30 of the frame's long side (24 px at 720) matches random texture; no EVA layout shows the
        # presenter's face that small (smallest window ≈ 260 px), and such matches out-scored half-visible real faces
        if min(tw, th) < max(14, round(max(ow, oh) / 30)) or tw > ow * 1.6 or th > oh * 1.6: return None
        px, py = tw // 2, th // 2   # half the face may hang outside the frame
        pad = cv2.copyMakeBorder(out, py, py, px, px, cv2.BORDER_CONSTANT, value=fill)
        if tw > pad.shape[1] or th > pad.shape[0]: return None
        t = cv2.resize(tpl, (tw, th), interpolation=cv2.INTER_AREA if s * ds < 1 else cv2.INTER_CUBIC)
        r = cv2.matchTemplate(pad, t, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(r)
        # a face partly outside the frame is scored on the padding too, which under-rates the real (half-visible) face
        # against small false matches elsewhere: rank such candidates by the NCC of their in-frame part instead
        X0, Y0 = ml[0] - px, ml[1] - py; ax0, ay0, ax1, ay1 = max(0, X0), max(0, Y0), min(ow, X0 + tw), min(oh, Y0 + th)
        inside = max(0, ax1 - ax0) * max(0, ay1 - ay0) / float(tw * th)
        if .35 <= inside < .95:
            mv = max(mv, _ncc(out[ay0:ay1, ax0:ax1], t[ay0 - Y0:ay1 - Y0, ax0 - X0:ax1 - X0]) - .05)
        return mv, (s, a, X0 / ds, Y0 / ds)

    for s in np.geomspace(*scales):
        r = try_scale(s)
        if r and r[0] > best[0]: best = r
    if best[1] is None: return None
    s0 = best[1][0]
    for s in s0 * np.linspace(.94, 1.06, 7):   # refine scale
        r = try_scale(s)
        if r and r[0] > best[0]: best = r
    s0 = best[1][0]; base_score = best[0]
    # stretch probe. try_scale(s, a) scales the patch by s·a horizontally and s/a vertically, so the picture's
    # width/height distortion is a². The best uniform scale found above sits between the two axis scales, so each
    # aspect is tried at a few scales around s0; coarse pass, then a fine pass around the winner.
    def probe(aspects):
        nonlocal best
        for a in aspects:
            if abs(a - 1) < 1e-3: continue
            for e in (-1, -.5, 0, .5, 1):
                r = try_scale(s0 * a ** e, a)
                if r and r[0] > best[0] + .01: best = r
    probe((.84, .89, .93, .965, 1.035, 1.07, 1.12, 1.18))
    if abs(best[1][1] - 1) > 1e-3:
        a1, s0 = best[1][1], best[1][0]
        probe(a1 * np.linspace(.97, 1.03, 5))
    score, (s, a, X, Y) = best
    # face box (full detector box) in output pixels
    bx, by = X - (x0 - fx) * s * a, Y - (y0 - fy) * s / a
    box = (bx, by, fw * s * a, fh * s / a)
    # visibility: compare the warped patch with the render cell by cell, inside the frame only
    tw, th = int(round((x1 - x0) * s * a)), int(round((y1 - y0) * s / a))
    if tw < 8 or th < 8: return None
    tfull = cv2.resize(tpl, (tw, th), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    og = cv2.cvtColor(out_bgr, cv2.COLOR_BGR2GRAY)
    Xi, Yi = int(round(X)), int(round(Y))
    cx0, cy0, cx1, cy1 = max(0, Xi), max(0, Yi), min(W, Xi + tw), min(H, Yi + th)
    inframe, cells, vis = 0.0, [[None] * 4 for _ in range(4)], []
    if cx1 - cx0 > 8 and cy1 - cy0 > 8:
        a_ = og[cy0:cy1, cx0:cx1]; b_ = tfull[cy0 - Yi:cy1 - Yi, cx0 - Xi:cx1 - Xi]
        inframe = _ncc(a_, b_)
        for r_ in range(4):
            for c_ in range(4):
                gx0, gx1 = Xi + tw * c_ // 4, Xi + tw * (c_ + 1) // 4; gy0, gy1 = Yi + th * r_ // 4, Yi + th * (r_ + 1) // 4
                if gx0 < 0 or gy0 < 0 or gx1 > W or gy1 > H: cells[r_][c_] = 0.0; vis.append(0.0); continue   # outside the frame
                tb = tfull[gy0 - Yi:gy1 - Yi, gx0 - Xi:gx1 - Xi]
                if tb.size < 16 or tb.std() < 6: continue   # flat skin: no evidence either way
                v = _ncc(og[gy0:gy1, gx0:gx1], tb); cells[r_][c_] = round(v, 2); vis.append(1.0 if v > .45 else 0.0)
    fx0, fy0, fx1, fy1 = box[0], box[1], box[0] + box[2], box[1] + box[3]
    inside = max(0, min(W, fx1) - max(0, fx0)) * max(0, min(H, fy1) - max(0, fy0))
    return {"score": round(float(score), 3), "base_score": round(float(base_score), 3), "inframe": round(inframe, 3),
            "scale": round(float(s), 4), "aspect": round(float(a * a), 3), "box": [round(v, 1) for v in box],
            "out_frac": round(1 - inside / max(1e-6, box[2] * box[3]), 3),
            "visible": round(float(np.mean(vis)), 3) if vis else None, "cells": cells}


def head_box_out(m, face_box_src):
    """head box (hair to chin) in output pixels, from the tracked face box"""
    x, y, w, h = m["box"]
    return head_from_face((x, y, w, h))


def out_fraction(box, W, H):
    x, y, w, h = box
    inside = max(0, min(W, x + w) - max(0, x)) * max(0, min(H, y + h) - max(0, y))
    return 1 - inside / max(1e-6, w * h)


def edges_out(box, W, H):
    """which frame edges cut the box, with the cut depth as a fraction of the box size"""
    x, y, w, h = box
    e = {"top": max(0, -y) / h, "bottom": max(0, y + h - H) / h, "left": max(0, -x) / w, "right": max(0, x + w - W) / w}
    return {k: round(v, 3) for k, v in e.items() if v > 0.005}
