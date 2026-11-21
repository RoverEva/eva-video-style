#!/usr/bin/env python3
"""Render a long-form glow-beat video (8+ min) from a script JSON, with a looped music bed.

  python3 template/longform/render_long.py --script template/longform/scripts/aries.json \
          --music media/Vibecoding_music.mp3 --out out/long/aries.mp4
  python3 template/longform/render_long.py --script ... --music ... --stills 2,6.5,9,30 --out out/check

The music is cut at its first grid point and looped in whole bars, so the beat grid continues across loops.
"""
import argparse, json, os, subprocess, sys, tempfile, time
from multiprocessing import Process
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); sys.path.insert(0, os.path.join(HERE, '..', 'zodiac'))


def grid(music):
    from engine.beats import beat_grid
    phase, e8, bpm = beat_grid(music)
    phase = phase % e8
    return phase, e8


def scene(args):
    import cv2
    from longform import LongScene
    with open(args.script, encoding='utf-8') as f: script = json.load(f)
    e8 = float(args.eighth) if args.eighth else (grid(args.music)[1] if args.music else 60 / 112.9 / 2)
    brand = {}
    bp = os.path.join(HERE, '..', 'mbti', 'brand.json')
    if os.path.exists(bp):
        with open(bp, encoding='utf-8') as f: brand = json.load(f)
    logo = None; lp = args.logo or brand.get('logo')
    if lp:
        lp = lp if os.path.isabs(lp) else os.path.join(HERE, '..', 'mbti', lp)
        if os.path.exists(lp): logo = cv2.imread(lp).astype('float32') / 255.0
    return LongScene(script, 0.0, e8, logo, brand)


def build_music(music, duration, out):
    phase, e8 = grid(music)
    probe = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', music],
                                 capture_output=True, text=True).stdout)
    bar = 8 * e8; nbars = int((probe - phase - 0.05) / bar); seg = nbars * bar
    n = int(duration / seg) + 1
    f = (f"[0:a]atrim={phase:.4f}:{phase + seg:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={seg - 0.008:.4f}:d=0.008[s];"
         + f"[s]asplit={n}" + ''.join(f'[c{k}]' for k in range(n)) + ';' + ''.join(f'[c{k}]' for k in range(n)) + f"concat=n={n}:v=0:a=1,"
         + f"atrim=0:{duration:.3f},afade=t=out:st={duration - 4:.3f}:d=4[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', music, '-filter_complex', f, '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', out], check=True)


def worker(args, a, b, path):
    sc = scene(args); fps = args.fps
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1920x1080', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', path + '.tmp.mp4'], stdin=subprocess.PIPE)
    for n in range(a, b): p.stdin.write(sc.frame(n / fps).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(path + '.tmp.mp4', path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--script', required=True); ap.add_argument('--music'); ap.add_argument('--out', required=True)
    ap.add_argument('--eighth'); ap.add_argument('--logo'); ap.add_argument('--stills')
    ap.add_argument('--fps', type=int, default=24); ap.add_argument('--workers', type=int, default=max(1, os.cpu_count() or 2))
    args = ap.parse_args()
    sc = scene(args)
    print(f"{sc.s['title']}: {len(sc.segs)} chapters, {sum(len(s['cards']) for s in sc.segs)} cards, "
          f"{sc.duration / 60:.2f} min (reading {sc.cps:.1f} chars/s)", flush=True)
    if args.stills:
        import cv2
        os.makedirs(args.out, exist_ok=True)
        for s in args.stills.split(','):
            t = float(s); cv2.imwrite(os.path.join(args.out, f'{t:07.2f}.jpg'), sc.frame(t), [cv2.IMWRITE_JPEG_QUALITY, 90])
        return
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    N = int(sc.duration * args.fps); k = args.workers; tmp = tempfile.mkdtemp(prefix='long_')
    parts = [os.path.join(tmp, f'p{i}.mp4') for i in range(k)]; cuts = [N * i // k for i in range(k + 1)]
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
        audio = os.path.join(tmp, 'a.m4a'); build_music(args.music, sc.duration, audio)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', audio, '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest',
                        '-movflags', '+faststart', args.out], check=True)
    else: os.replace(video, args.out)
    print(f'wrote {args.out} in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
