#!/usr/bin/env python3
"""Zodiac glow beat video — render one sign (or all 12) to MP4, same music and beat logic as the MBTI template.

  python3 template/zodiac/render.py --sign aries --music media/MBTI_music.mp3 --out out/zodiac/01_aries.mp4
  python3 template/zodiac/render.py --sign all   --music media/MBTI_music.mp3 --out out/zodiac/
  python3 template/zodiac/render.py --sign leo --stills 2.8,8.4,24.4 --out out/zodiac_check
"""
import argparse, json, os, subprocess, sys, tempfile, time
from multiprocessing import Process
HERE = os.path.dirname(os.path.abspath(__file__))
MBTI = os.path.join(HERE, '..', 'mbti')
sys.path.insert(0, HERE); sys.path.insert(0, MBTI)


def make(args, key):
    import cv2
    from zodiac_scene import load
    from engine.beats import beat_grid
    if args.grid: off, e8 = map(float, args.grid.split(','))
    elif args.music: off, e8, _ = beat_grid(args.music)
    else: off, e8 = 0.367, 1 / 3.
    brand = {}
    bp = os.path.join(MBTI, 'brand.json')
    if os.path.exists(bp):
        with open(bp, encoding='utf-8') as f: brand = json.load(f)
    logo = None; lp = args.logo or brand.get('logo')
    if lp:
        lp = lp if os.path.isabs(lp) else os.path.join(MBTI, lp)
        if os.path.exists(lp): logo = cv2.imread(lp).astype('float32') / 255.0
    return make.cache.setdefault((key, off, e8), None) or load(key, off, e8, logo, brand)
make.cache = {}


def worker(args, key, a, b, path):
    sc = make(args, key)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1920x1080', '-r', '30', '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    for n in range(a, b): p.stdin.write(sc.frame(n / 30).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def render_one(args, key, out):
    sc = make(args, key)
    print(f"{sc.sign['cn']} {sc.sign['en']}: element={sc.sign['element']} prop={sc.prop} duration={sc.duration:.2f}s", flush=True)
    if args.stills:
        import cv2
        os.makedirs(out, exist_ok=True)
        for s in args.stills.split(','):
            t = float(s); f = os.path.join(out, f'{key}_{t:05.2f}.jpg'); cv2.imwrite(f, sc.frame(t), [cv2.IMWRITE_JPEG_QUALITY, 92])
        return
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    N = int(sc.duration * 30); k = args.workers; tmp = tempfile.mkdtemp(prefix='zod_')
    parts = [os.path.join(tmp, f'p{i}.mp4') for i in range(k)]; cuts = [N * i // k for i in range(k + 1)]
    t0 = time.time()
    procs = [Process(target=worker, args=(args, key, cuts[i], cuts[i + 1], parts[i])) for i in range(k)]
    for p in procs: p.start()
    for p in procs: p.join()
    if not all(os.path.exists(p) for p in parts): sys.exit('a render worker failed')
    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w') as f: f.writelines(f"file '{p}'\n" for p in parts)
    video = os.path.join(tmp, 'v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    if args.music:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', args.music, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', f'afade=t=out:st={sc.duration - 0.6:.2f}:d=0.6', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                        '-movflags', '+faststart', out], check=True)
    else: os.replace(video, out)
    print(f'wrote {out} in {time.time() - t0:.0f}s', flush=True)


def main():
    from zodiac_signs import SIGNS
    ap = argparse.ArgumentParser()
    ap.add_argument('--sign', default='aries', help="sign key (aries ... pisces) or 'all'")
    ap.add_argument('--music'); ap.add_argument('--grid'); ap.add_argument('--logo')
    ap.add_argument('--out', default='out/zodiac/')
    ap.add_argument('--stills'); ap.add_argument('--workers', type=int, default=max(1, os.cpu_count() or 2))
    args = ap.parse_args()
    keys = [s['key'] for s in SIGNS] if args.sign == 'all' else [args.sign]
    for i, key in enumerate(keys):
        s = next(x for x in SIGNS if x['key'] == key); n = [x['key'] for x in SIGNS].index(key) + 1
        if args.stills: out = args.out
        elif args.sign == 'all' or args.out.endswith('/'): out = os.path.join(args.out, f"{n:02d}_{key}_{s['cn']}.mp4")
        else: out = args.out
        if not args.stills and os.path.exists(out): print('skip', out); continue
        render_one(args, key, out)


if __name__ == '__main__':
    main()
