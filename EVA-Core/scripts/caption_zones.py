#!/usr/bin/env python3
"""Move each bilingual caption to a spot that does not cover the important part of the picture (T19 and any
shot with real footage). Reads the rendered video WITHOUT captions, scores candidate caption boxes by visual
saliency (spectral residual) + edge density, refuses boxes that overlap given "keep clear" rectangles
(the Eva circle, titles, the footage subject), and writes a new .ass with a \\pos per line.

usage: caption_zones.py VIDEO_NO_CAPTIONS.mp4 IN.ass OUT.ass [avoid.json]
  avoid.json: [[t0, t1, x, y, w, h], ...] in seconds / 1920x1080 pixels (optional), or
              {"avoid": [...], "only": [[t0, t1], ...]} to move only the captions inside those time windows
              (e.g. just the T19 footage shots) and leave every other caption bottom-centre
Captions keep their style; only the position changes. Bottom-centre wins whenever it is clear enough.
"""
import json, re, subprocess, sys
import numpy as np, cv2

W, H = 1920, 1080
# name: (anchor x, baseline y, box w, box h, preference penalty)
ZONES = {'bc': (960, 1046, 1160, 150, 0.00), 'br': (1380, 1046, 1000, 150, .04), 'bl': (560, 1046, 1000, 150, .05),
         'tc': (960, 190, 1160, 150, .10), 'tr': (1380, 190, 1000, 150, .12)}

def ts(s):
    h, m, r = s.split(':'); return int(h) * 3600 + int(m) * 60 + float(r)

def frame_at(video, t):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=480:270', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(270, 480, 3) if len(raw) == 480 * 270 * 3 else None

def busy_map(im):
    # spectral-residual saliency (Hou & Zhang 2007), plain numpy so no opencv-contrib is needed
    small = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (128, 72)).astype(np.float32)
    F = np.fft.fft2(small); la = np.log(np.abs(F) + 1e-6); ph = np.angle(F)
    sal = np.abs(np.fft.ifft2(np.exp(la - cv2.blur(la, (3, 3)) + 1j * ph))) ** 2
    sal = cv2.resize(cv2.GaussianBlur(sal.astype(np.float32), (0, 0), 2.5), (im.shape[1], im.shape[0])); sal /= (sal.max() + 1e-6)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); e = cv2.Canny(g, 60, 160).astype(np.float32) / 255
    e = cv2.GaussianBlur(e, (0, 0), 4); e /= (e.max() + 1e-6)
    return .6 * sal + .4 * e

def rect(z):
    x, y, w, h, _ = ZONES[z]; return (x - w / 2, y - h, w, h)

def overlap(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0, min(ay + ah, by + bh) - max(ay, by)) / (aw * ah)

def main():
    video, src, out = sys.argv[1:4]; cfg = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else []
    avoid, only = (cfg.get('avoid', []), cfg.get('only')) if isinstance(cfg, dict) else (cfg, None)
    lines = open(src, encoding='utf-8').read().split('\n'); prev = 'bc'; res = []
    for ln in lines:
        m = re.match(r'(Dialogue: [^,]*,)([^,]*),([^,]*),(.*)', ln)
        if not m: res.append(ln); continue
        a, b = ts(m.group(2)), ts(m.group(3)); mid = (a + b) / 2
        if only is not None and not any(t0 <= mid < t1 for t0, t1 in only): res.append(ln); prev = 'bc'; continue
        im = frame_at(video, mid); bm = busy_map(im) if im is not None else None
        best, score = 'bc', 9
        for z in ZONES:
            x, y, w, h = rect(z); s = ZONES[z][4] + (0 if z == prev else .03)
            if bm is not None: s += float(bm[int(y / 4):int((y + h) / 4), int(x / 4):int((x + w) / 4)].mean())
            for t0, t1, ax, ay, aw, ah in avoid:
                if t0 < b and t1 > a: s += 5 * overlap((x, y, w, h), (ax, ay, aw, ah))
            if s < score: best, score = z, s
        prev = best; zx, zy = ZONES[best][0], ZONES[best][1]
        parts = ln.split(',', 9); body = parts[9]
        x, y, w, h = rect(best); lum = float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)[int(y / 4):int((y + h) / 4), int(x / 4):int((x + w) / 4)].mean()) / 255 if im is not None else 0
        if score - ZONES[best][4] > .22 or lum > .6:   # busy or bright picture behind the caption: add a soft dark plate (own layer, under the text)
            plain = re.sub(r'\{[^}]*\}', '', body).split('\\N'); cn = plain[0]; en = plain[1] if len(plain) > 1 else ''
            bw = max(len(cn) * 54, len(en) * 18) + 70; bh = 132 if en else 84
            box = parts[:9] + ['{\\an2\\pos(%d,%d)\\bord0\\shad0\\blur6\\1c&H1E0F06&\\1a&H58&\\p1}m 0 0 l %d 0 %d %d 0 %d{\\p0}' % (zx, zy + 10, bw, bw, bh, bh)]
            box[0] = box[0].replace('Dialogue: 0', 'Dialogue: 0'); res.append(','.join(box))
            parts[0] = parts[0].replace('Dialogue: 0', 'Dialogue: 1')
        parts[9] = '{\\an2\\pos(%d,%d)}' % (zx, zy) + body
        res.append(','.join(parts)); print(f'{a:7.2f}s  {best}  {score:.2f}')
    open(out, 'w', encoding='utf-8').write('\n'.join(res))

if __name__ == '__main__': main()
