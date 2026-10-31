"""Tests for scripts/music.py (optional background music + Kenney jingles).

Everything runs on a synthetic library (drum loops at known tempi, short jingles) and a synthetic talking video built
with FFmpeg, so the tests never need the real Open Lo-Fi / Kenney files and nothing licensed enters the repo.
"""
import importlib.util, json, shutil, subprocess, wave
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if not shutil.which("ffmpeg"):
    pytest.skip("ffmpeg not installed", allow_module_level=True)
SR = 48000


def load(lib):
    import os
    os.environ["EVA_MUSIC_LIBRARY"] = str(lib)
    spec = importlib.util.spec_from_file_location("music", ROOT / "scripts" / "music.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def wav(path, x, sr=SR):
    path.parent.mkdir(parents=True, exist_ok=True)
    w = wave.open(str(path), "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()); w.close()


def drum_loop(bpm, secs, level=.5, seed=0):
    """Kick on every beat, accent on beat 1, hats on 8ths, a quiet pad; quieter 4-bar intro."""
    rng = np.random.default_rng(seed); n = int(secs * SR); x = np.zeros(n, np.float32); beat = 60 / bpm
    t = np.arange(int(.15 * SR)) / SR
    kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-t * 30)) * t) * np.exp(-t * 18)
    hat = rng.normal(0, 1, int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / SR * 150) * .25
    k = 0
    while k * beat / 2 < secs - .2:
        i = int(k * beat / 2 * SR)
        if k % 2 == 0: x[i:i + len(kick)] += kick * (1.0 if k % 8 == 0 else .7)
        x[i:i + len(hat)] += hat; k += 1
    x += .05 * np.sin(2 * np.pi * 220 * np.arange(n) / SR)
    x[:int(4 * 4 * beat * SR)] *= .3
    return x / np.abs(x).max() * level


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("music")
    lib = tmp / "music-library"
    wav(lib / "background/open-lofi/terminal-neon-cursor.wav", drum_loop(88, 60, seed=1))
    wav(lib / "background/open-lofi/pancakes-in-the-sun.wav", drum_loop(98, 60, seed=2))
    wav(lib / "background/open-lofi/graphite-morning-pages.wav", drum_loop(76, 60, seed=3))
    for fam, d in (("8bit", 2.2), ("hit", .6), ("pizzicato", 1.4), ("pizzicato", 2.4)):
        t = np.arange(int(d * SR)) / SR
        wav(lib / f"jingles/kenney/{fam}/jingles_{fam}_{d}.wav", .4 * np.sin(2 * np.pi * 660 * t) * np.exp(-t * 2))
    # talking video: 12 s, voice-like noise bursts at speech times, silent pauses, 30 fps
    speech = [(1.5, 4.0, "Today I will show you how to build an AI workflow."), (4.6, 7.2, "Step one: choose a template."),
              (8.8, 10.0, "The key number is 3!")]
    rng = np.random.default_rng(7); v = np.zeros(int(12 * SR), np.float32)
    for a, b, _ in speech:
        i, j = int(a * SR), int(b * SR); tt = np.arange(j - i) / SR
        v[i:j] = (rng.normal(0, .15, j - i) * (.6 + .4 * np.sin(2 * np.pi * 4 * tt)) + .1 * np.sin(2 * np.pi * 180 * tt))
    wav(tmp / "voice.wav", v)
    video = tmp / "talk.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x180:rate=30:duration=12", "-i", str(tmp / "voice.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(video)], check=True)
    srt = tmp / "talk.srt"
    def ts(s): return f"00:00:{int(s):02d},{int(round(s % 1 * 1000)):03d}"
    srt.write_text("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(speech, 1)))
    m = load(lib)
    assert m.main(["analyze"]) == 0
    return {"tmp": tmp, "lib": lib, "m": m, "video": video, "srt": srt, "speech": speech}


def cfg(tmp, **kw):
    p = tmp / f"cfg_{abs(hash(json.dumps(kw, sort_keys=True)))}.json"; p.write_text(json.dumps(kw)); return p


def test_catalog_bpm_and_cache(env, capsys):
    cat = json.loads((env["lib"] / "catalog.json").read_text())["tracks"]
    bpm = {Path(r).stem: i["bpm"] for r, i in cat.items() if i["type"] == "background"}
    assert abs(bpm["terminal-neon-cursor"] - 88) < 2 and abs(bpm["pancakes-in-the-sun"] - 98) < 2 and abs(bpm["graphite-morning-pages"] - 76) < 2
    t = cat["background/open-lofi/terminal-neon-cursor.wav"]
    assert {"tech", "night"} <= set(t["tags"]) and t["intro_end"] >= 8 and t["license"] == "UNVERIFIED"
    assert all(abs(b - a - 4 * 60 / 88) < .05 for a, b in zip(t["downbeats"][:6], t["downbeats"][1:7]))
    assert cat["jingles/kenney/8bit/jingles_8bit_2.2.wav"]["family"] == "8bit"
    j = cat["jingles/kenney/hit/jingles_hit_0.6.wav"]
    assert j["family"] == "hit" and "transition" in j["roles"] and j["license"] == "CC0-1.0"
    capsys.readouterr(); assert env["m"].main(["analyze"]) == 0
    assert "0 analysed, 7 cached" in capsys.readouterr().out          # second run re-analyses nothing


def test_mode_none_is_a_no_op(env, tmp_path):
    m = env["m"]
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(tmp_path), "--config", str(cfg(tmp_path))]) == 0
    assert json.loads((tmp_path / "music_plan.json").read_text())["mode"] == "none"
    assert m.main(["apply", str(tmp_path / "music_plan.json"), str(tmp_path / "out.mp4")]) == 0
    assert not (tmp_path / "out.mp4").exists() and not (tmp_path / "music_stem.wav").exists()


def test_category_picks_style(env, tmp_path):
    m = env["m"]
    for cat, want in (("tech", "terminal-neon-cursor"), ("product", "pancakes-in-the-sun"), ("business", "graphite-morning-pages")):
        d = tmp_path / cat
        assert m.main(["plan", str(env["video"]), str(env["srt"]), str(d), "--config",
                       str(cfg(tmp_path, background_music="auto", category=cat))]) == 0
        assert Path(json.loads((d / "music_plan.json").read_text())["background"]["file"]).stem == want


def test_auto_detects_tutorial_and_jingles_are_sparse(env, tmp_path):
    m = env["m"]; d = tmp_path / "auto"
    cues = tmp_path / "cues.json"; cues.write_text(json.dumps([["whoosh", 4.3, .1], ["impact", 7.25, .1]]))
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(d), "--cues", str(cues), "--config",
                   str(cfg(tmp_path, background_music="auto"))]) == 0
    p = json.loads((d / "music_plan.json").read_text())
    assert p["category"] == "tutorial"
    b = p["background"]; assert b["start"] >= 0 and b["end"] - b["start"] == pytest.approx(12, abs=.01) and not b["loops"]
    roles = [j["role"] for j in p["jingles"]]
    assert roles.count("opening") == 1 and roles.count("ending") == 1 and len(roles) <= 3
    for j in p["jingles"]:  # never on speech, never on an existing SFX cue
        assert all(not (a < j["at"] + .01 < b) for a, b, _ in env["speech"])
        assert all(abs(j["at"] - t) > .3 for t in (4.3, 7.25))
    assert (d / "music_plan.md").read_text().startswith("# 配乐方案")
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(d)]) == 1   # refuses to overwrite a plan


def test_preview_and_apply_keep_voice_clear_and_sync(env, tmp_path):
    m = env["m"]; d = tmp_path / "mix"
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(d), "--config",
                   str(cfg(tmp_path, background_music="auto", category="tech"))]) == 0
    assert m.main(["preview", str(d / "music_plan.json")]) == 0
    assert (d / "music_preview.m4a").stat().st_size > 1000
    meta = json.loads((d / "music_stem.json").read_text())["metrics"]
    assert meta["speech_to_music_db"] >= 18 and meta["stem_peak"] <= .89
    assert meta["fade_in_start_gain"] < .01 and meta["fade_out_end_gain"] < .01
    stem = m.decode(d / "music_stem.wav", SR, 1)
    sp = np.concatenate([stem[int(a * SR):int(b * SR)] for a, b, _ in env["speech"]])
    gap = stem[int(7.6 * SR):int(8.4 * SR)]
    assert m.db(m.rms(gap)) - m.db(m.rms(sp)) > 3                  # ducked under speech, louder in the pause
    out = tmp_path / "final.mp4"
    assert m.main(["apply", str(d / "music_plan.json"), str(out)]) == 0
    chk = json.loads((d / "music_check.json").read_text())
    assert chk["sync_ok"] and chk["frames_in"] == chk["frames_out"] == 360
    assert -17.5 < chk["lufs"] < -14.5 and chk["true_peak_dbfs"] < 0
    assert m.main(["apply", str(d / "music_plan.json"), str(out)]) == 1            # never overwrites


def test_manual_mode_and_bad_config(env, tmp_path):
    m = env["m"]; d = tmp_path / "man"
    c = cfg(tmp_path, background_music="manual", manual={"file": "pancakes-in-the-sun.wav", "start": 12.0})
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(d), "--config", str(c)]) == 0
    b = json.loads((d / "music_plan.json").read_text())["background"]
    assert b["file"].endswith("pancakes-in-the-sun.wav") and b["start"] == 12.0
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(tmp_path / "x"), "--config",
                   str(cfg(tmp_path, background_music="loud"))]) == 1
    assert m.main(["plan", str(env["video"]), str(env["srt"]), str(tmp_path / "y"), "--config",
                   str(cfg(tmp_path, background_music="manual", manual={"file": "nope.mp3"}))]) == 1


def test_assemble_without_music_is_unchanged():
    s = (ROOT / "scripts" / "assemble.sh").read_text()
    assert 'MUSIC_STEM' in s and 'amix=inputs=2:normalize=0,loudnorm' in s   # the default (no music) filter is untouched


def test_import_links_kenney_families_and_license(tmp_path):
    src = tmp_path / "dl"; t = np.arange(SR // 2) / SR; x = .3 * np.sin(2 * np.pi * 440 * t)
    wav(src / "kenney/Audio/8-Bit jingles/jingles_NES00.wav", x); wav(src / "kenney/Audio/Hit jingles/jingles_HIT00.wav", x)
    wav(src / "kenney/Preview.wav", x); (src / "kenney/License.txt").write_text("Creative Commons Zero, CC0")
    wav(src / "lofi/cursor-after-midnight.wav", x)
    m = load(tmp_path / "lib")
    assert m.main(["import", "--lofi", str(src / "lofi"), "--kenney", str(src / "kenney")]) == 0
    lib = tmp_path / "lib"
    assert (lib / "background/open-lofi/cursor-after-midnight.wav").is_symlink()
    assert (lib / "jingles/kenney/8bit/jingles_NES00.wav").exists() and (lib / "jingles/kenney/hit/jingles_HIT00.wav").exists()
    assert not list(lib.rglob("Preview.wav")) and (lib / "jingles/kenney/SOURCE_LICENSE.txt").is_file()
    assert m.main(["import", "--lofi", str(src / "lofi")]) == 0                 # idempotent
    assert m.main(["import", "--lofi", str(src / "missing")]) == 1
    assert m.main(["analyze"]) == 0
    cat = json.loads((lib / "catalog.json").read_text())["tracks"]
    assert cat["jingles/kenney/8bit/jingles_NES00.wav"]["family"] == "8bit"
