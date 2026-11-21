"""Measure the eighth-note grid of a music track: T(n) = offset + n * eighth.

Spectral flux with a small hop; onset times use window *centres* (window starts land ~2 frames early).
The period comes from the flux autocorrelation, the offset from the phase that best fits the strongest onsets.
"""
import subprocess, numpy as np

SR = 22050


def load_mono(path, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def beat_grid(path, bpm_range=(70, 180)):
    x = load_mono(path)
    hop, n = 128, 1024
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    S = np.log1p(10 * np.abs(np.fft.rfft(fr, axis=1)))
    flux = np.maximum(0, np.diff(S, axis=0)).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    dt = hop / SR
    centre = lambda i: (i * hop + n / 2) / SR
    # beat period from autocorrelation (quarter note), then eighth = period / 2
    ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
    lags = np.arange(len(ac)) * dt
    lo, hi = 60 / bpm_range[1], 60 / bpm_range[0]
    m = (lags >= lo) & (lags <= hi)
    quarter = float(lags[m][np.argmax(ac[m])])
    # refine the period with the comb that best matches the whole track
    best = None
    for p in np.linspace(quarter * 0.98, quarter * 1.02, 81):
        e8 = p / 2
        ph = np.linspace(0, e8, 60, endpoint=False)
        idx = ((ph[:, None] + np.arange(0, len(x) / SR - e8, e8)[None, :]) / dt).astype(int)
        idx = np.clip(idx - int(n / 2 / hop), 0, len(flux) - 1)
        score = flux[idx].mean(1)
        k = int(np.argmax(score))
        if best is None or score[k] > best[0]: best = (score[k], e8, ph[k])
    _, eighth, phase = best
    # the timeline's beat 0 is the first grid point after ~0.3 s (room for the opening star)
    offset = phase + eighth * max(0, int(np.ceil((0.30 - phase) / eighth)))
    return float(offset), float(eighth), 60 / (2 * eighth)


if __name__ == '__main__':
    import sys
    o, e, bpm = beat_grid(sys.argv[1])
    print(f'offset={o:.3f}s  eighth={e:.4f}s  bpm={bpm:.1f}')
