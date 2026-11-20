#!/usr/bin/env python3
"""MBTI glow beat video — render one personality type to MP4.

  python3 template/mbti/render.py --type ENFJ --music media/MBTI_music.mp3 --out out/ENFJ.mp4
  python3 template/mbti/render.py --type INTJ --music track.mp3 --stills 2.7,8.1,24.4 --out out/check
"""
import argparse, json, os, subprocess, sys, tempfile, time
from multiprocessing import Process
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_type(code):
    p = os.path.join(HERE, 'types', f'{code.upper()}.json')
    if not os.path.exists(p): sys.exit(f'no preset {p}; copy types/_TEMPLATE.json to make one')
    with open(p, encoding='utf-8') as f: cfg = json.load(f)
    brand = os.path.join(HERE, 'brand.json')
    if 'brand' not in cfg and os.path.exists(brand):
        with open(brand, encoding='utf-8') as f: cfg['brand'] = json.load(f)
    return cfg


def make_scene(args):
    import cv2
    from engine.scene import MBTIScene
    from engine.beats import beat_grid
    if args.group:
        from engine.group import GroupScene
        with open(os.path.join(HERE, 'groups', f'{args.group.upper()}.json'), encoding='utf-8') as f: gcfg = json.load(f)
        cfg = load_type(gcfg['members'][0]['code'])
    else:
        cfg = load_type(args.type)
    if args.grid: off, e8 = map(float, args.grid.split(','))
    elif args.music: off, e8, _ = beat_grid(args.music)
    else: off, e8 = 0.367, 1 / 3.
    logo = None
    lp = args.logo or (cfg.get('brand') or {}).get('logo')
    if lp:
        lp = lp if os.path.isabs(lp) else os.path.join(HERE, lp)
        if os.path.exists(lp): logo = cv2.imread(lp).astype('float32') / 255.0
    if args.group:
        sc = GroupScene(gcfg, os.path.join(HERE, 'types'), off, e8, logo)
        for m, _ in sc.members: m.cfg.setdefault('brand', cfg.get('brand', {}))
        sc.code, sc.cfg, sc.prop = gcfg['group'], {'name_cn': gcfg['title']}, 'group'
        return sc
    return MBTIScene(cfg, off, e8, logo)


def worker(args, a, b, path):
    sc = make_scene(args)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1920x1080', '-r', '30',
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'],
                         stdin=subprocess.PIPE)
    for n in range(a, b): p.stdin.write(sc.frame(n / 30).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--type', default='ENFJ')
    ap.add_argument('--group', help='render a group video instead, e.g. NT (see groups/)')
    ap.add_argument('--music', help='music track (beat grid is measured from it and it is muxed in)')
    ap.add_argument('--grid', help='override grid as "offset,eighth" seconds, e.g. 0.367,0.3333')
    ap.add_argument('--logo', help='brand logo image (PNG/JPG on black); default: drawn eye')
    ap.add_argument('--out', default='out/MBTI.mp4')
    ap.add_argument('--stills', help='comma-separated times: write JPG stills instead of a video')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2)))
    args = ap.parse_args()

    sc = make_scene(args)
    print(f'{sc.code} {sc.cfg["name_cn"]}: palette={sc.P.name} prop={sc.prop} grid=({sc.off:.3f}s + n*{sc.e8:.4f}s) duration={sc.duration:.2f}s')
    if args.stills:
        import cv2
        os.makedirs(args.out, exist_ok=True)
        for s in args.stills.split(','):
            t = float(s); f = os.path.join(args.out, f'{sc.code}_{t:05.2f}.jpg')
            cv2.imwrite(f, sc.frame(t), [cv2.IMWRITE_JPEG_QUALITY, 92]); print(f)
        return
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    N = int(sc.duration * 30); k = args.workers
    tmp = tempfile.mkdtemp(prefix='mbti_')
    parts = [os.path.join(tmp, f'p{i}.mp4') for i in range(k)]
    cuts = [N * i // k for i in range(k + 1)]
    t0 = time.time()
    procs = [Process(target=worker, args=(args, cuts[i], cuts[i + 1], parts[i])) for i in range(k)]
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
                        '-movflags', '+faststart', args.out], check=True)
    else:
        os.replace(video, args.out)
    print(f'wrote {args.out} in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
