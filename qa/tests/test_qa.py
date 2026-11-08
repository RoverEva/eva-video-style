"""Eva Video QA regression tests.

    python3 -m pytest qa/tests -q            (≈ 4 min the first time: fixtures are built once and cached)

Fixtures (qa/tests/fixtures.py) are built from a REAL presenter clip with one known, synthetic defect each, plus the
committed real production renders in site/demos/ (rendered by the worker image from real uploads). They test the QA
logic and its thresholds; they do not measure real-world face-detection accuracy on arbitrary footage.
Stage A page tests need node + Playwright (Chromium) and are skipped without them.
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from qa import post, pre, subs                      # noqa: E402
from qa.config import Config                        # noqa: E402
from qa.tests import fixtures as FX                 # noqa: E402

CACHE = Path(os.environ.get("EVA_QA_FIXTURES", Path(tempfile.gettempdir()) / "eva-qa-fixtures-v2"))
DEMO = REPO / "site/demos"


@pytest.fixture(scope="session")
def fx():
    meta = FX.build(CACHE)
    return Path(meta["dir"]), meta


def _sev(d, check):
    """worst severity of one check in a report ('PASS', 'WARN', 'FAIL'), or None if it did not run"""
    for c in d["checks"]:
        if c["check"] == check: return c["severity"]
    return None


def _fails(d):
    return sorted({i["check"] for i in d["issues"] if i["severity"] == "FAIL"})


def run_post(tmp_path, video, config=None, **ctx):
    return post.run(dict(video=str(video), **{k: (str(v) if isinstance(v, Path) else v) for k, v in ctx.items()}), tmp_path / "qa", config)


def run_post_cfg(tmp_path, video, config, **ctx):
    return run_post(tmp_path, video, config, **ctx)


# ───────────────────────── successful videos: no false critical failures ─────────────────────────
def test_good_9x16_full_context_passes(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "good_final.mp4", clean=d / "good_clean.mp4", source=d / "src.mp4", ass=d / "good.ass",
                 srt=d / "good.srt", aspect="9:16", expected_frames=150)
    assert _fails(r) == [], r["issues"]
    for c in ("RENDER_SIZE", "RENDER_FPS", "RENDER_DURATION", "FACE_CROP", "FACE_SCALE", "CAP_FACE", "CAP_BOUNDS", "CAP_TIMING", "CAP_BURN"):
        assert _sev(r, c) == "PASS", (c, r["issues"])
    assert not r["blocking"]


def test_correct_16x9_export(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "land_final.mp4", clean=d / "land_clean.mp4", source=d / "src.mp4", ass=d / "land.ass", aspect="16:9")
    assert _fails(r) == [], r["issues"]
    assert _sev(r, "RENDER_SIZE") == "PASS" and r["info"]["video"]["video"]["width"] == 1920


def test_wrong_export_size_and_orientation(fx, tmp_path):
    d, _ = fx
    assert _sev(run_post(tmp_path / "a", d / "small_final.mp4", aspect="9:16"), "RENDER_SIZE") == "FAIL"   # 720p as the HD master
    assert _sev(run_post(tmp_path / "b", d / "land_final.mp4", aspect="9:16"), "RENDER_SIZE") == "FAIL"    # 16:9 file for a 9:16 job
    assert _sev(run_post(tmp_path / "c", d / "small_final.mp4", aspect="9:16", size=[720, 1280]), "RENDER_SIZE") == "PASS"


def test_engine_render_good_passes(fx, tmp_path):
    d, meta = fx
    if not meta.get("engine"): pytest.skip("node/Playwright not available")
    r = run_post(tmp_path, meta["engine"]["good"], source=d / "src.mp4", aspect="16:9", template="T26")
    assert _fails(r) == [], r["issues"]
    assert _sev(r, "FACE_SCALE") == "PASS"


# ───────────────────────── T26: face enlargement and head clipping ─────────────────────────
def test_t26_moved_right_and_enlarged_fails(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "t26_bad_clean.mp4", source=d / "src.mp4", aspect="9:16", template="T26", captions_burned=False)
    assert "FACE_CROP" in _fails(r) and "FACE_SCALE" in _fails(r), r["issues"]
    crop = next(i for i in r["issues"] if i["check"] == "FACE_CROP" and i["severity"] == "FAIL")
    assert crop["evidence"] and (tmp_path / "qa" / crop["evidence"]).exists() and crop["fix"] and crop["t"]


def test_t26_moved_right_at_own_scale_passes(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "t26_ok_clean.mp4", source=d / "src.mp4", aspect="9:16", template="T26", captions_burned=False)
    assert _fails(r) == [], r["issues"]
    assert _sev(r, "FACE_SCALE") == "PASS" and _sev(r, "FACE_CROP") == "PASS"


def test_t26_engine_render_zoom_fails(fx, tmp_path):
    d, meta = fx
    if not meta.get("engine"): pytest.skip("node/Playwright not available")
    r = run_post(tmp_path, meta["engine"]["zoom"], source=d / "src.mp4", aspect="16:9", template="T26")
    assert {"FACE_CROP", "FACE_SCALE"} <= set(_fails(r)), r["issues"]


def test_forehead_and_chin_crop_fail(fx, tmp_path):
    d, _ = fx
    top = run_post(tmp_path / "t", d / "crop_top_clean.mp4", source=d / "src.mp4", aspect="9:16")
    chin = run_post(tmp_path / "c", d / "crop_chin_clean.mp4", source=d / "src.mp4", aspect="9:16")
    assert "FACE_HEAD_EDGE" in _fails(top) or "FACE_CROP" in _fails(top), top["issues"]
    assert "FACE_CROP" in _fails(chin), chin["issues"]


def test_face_not_found_is_unverified_not_pass(fx, tmp_path):
    """a face pushed completely out of frame must never be reported as a PASSED face check"""
    d, _ = fx
    if not (d / "crop_gone_clean.mp4").exists():
        FX.ff("-f", "lavfi", "-i", f"color=c={FX.BEIGE}:s=1080x1920:r=30:d={FX.DUR}", "-i", d / "src.mp4", "-filter_complex",
              "[1:v]scale=1080:1920[p];[0:v][p]overlay=x=0:y=1250:shortest=1", *FX.X264, "-map", "1:a", "-c:a", "copy", d / "crop_gone_clean.mp4")
    r = run_post(tmp_path, d / "crop_gone_clean.mp4", source=d / "src.mp4", aspect="9:16")
    assert _sev(r, "FACE_TRACK") == "WARN"
    assert _sev(r, "FACE_CROP") is None and "FACE_CROP" in {n["check"] for n in r["not_run"]}


def test_intentional_crop_and_zoom_are_honoured(fx, tmp_path):
    """a template that crops/zooms on purpose declares it in its thresholds; QA then does not block it"""
    d, _ = fx
    cfg = Config({"templates": {"TX": {"face": {"allow_crop": True, "max_subject_scale": 2.0, "fail_subject_scale": 2.5}}}})
    r = run_post_cfg(tmp_path, d / "t26_bad_clean.mp4", cfg, source=d / "src.mp4", aspect="9:16", template="TX", captions_burned=False)
    assert _fails(r) == [], r["issues"]


def test_stretch_and_non_square_pixels_fail(fx, tmp_path):
    d, _ = fx
    assert "FACE_STRETCH" in _fails(run_post(tmp_path / "s", d / "stretch_clean.mp4", source=d / "src.mp4", aspect="9:16"))
    assert "RENDER_SAR" in _fails(run_post(tmp_path / "p", d / "sar_final.mp4", aspect="9:16"))


# ───────────────────────── T17 and other subtitle safety ─────────────────────────
def test_t17_caption_over_face_fails(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "t17_face_final.mp4", clean=d / "good_clean.mp4", source=d / "src.mp4", ass=d / "t17_face.ass",
                 srt=d / "t17_face.srt", aspect="9:16", template="T17")
    assert "CAP_FACE" in _fails(r), r["issues"]
    i = next(i for i in r["issues"] if i["check"] == "CAP_FACE")
    assert i["evidence"] and i["template"] == "T17" and i["data"]["worst_cover"] > .04


def test_caption_beyond_frame_fails(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "oob_final.mp4", clean=d / "good_clean.mp4", source=d / "src.mp4", ass=d / "oob.ass", srt=d / "oob.srt", aspect="9:16")
    assert "CAP_BOUNDS" in _fails(r), r["issues"]
    i = next(i for i in r["issues"] if i["check"] == "CAP_BOUNDS")
    assert 1.8 <= i["t"][0] <= 4.2   # the second cue, not the first


def test_captions_not_burned_fails(fx, tmp_path):
    d, _ = fx   # the .ass says captions are on screen, the delivered file has none
    r = run_post(tmp_path, d / "good_clean.mp4", clean=d / "good_clean.mp4", ass=d / "good.ass", srt=d / "good.srt", aspect="9:16")
    assert "CAP_BURN" in _fails(r)


# ───────────────────────── render / assets / timing ─────────────────────────
def test_render_defects_fail(fx, tmp_path):
    d, _ = fx
    assert "RENDER_BLACK" in _fails(run_post(tmp_path / "b", d / "black_final.mp4", aspect="9:16"))
    assert "RENDER_STREAMS" in _fails(run_post(tmp_path / "a", d / "noaudio_final.mp4", aspect="9:16"))
    assert "RENDER_FPS" in _fails(run_post(tmp_path / "f", d / "fps25_final.mp4", aspect="9:16"))
    assert "RENDER_DURATION" in _fails(run_post(tmp_path / "t", d / "good_final.mp4", aspect="9:16", expected_frames=200))


def test_unreadable_output_fails(tmp_path):
    bad = tmp_path / "broken.mp4"; bad.write_bytes(b"not a video")
    r = run_post(tmp_path, bad)
    assert r["blocking"] and "RENDER_STREAMS" in _fails(r)


# ───────────────────────── animation: static scenes ─────────────────────────
def test_intentional_static_scene_not_flagged(fx, tmp_path):
    d, _ = fx
    marked = run_post(tmp_path / "m", d / "static_clean.mp4", source=d / "src.mp4", aspect="9:16", static_ranges=[[1.5, 4.0]])
    assert not [i for i in marked["issues"] if i["check"] in ("RENDER_FREEZE", "MOTION_ANIMATION")], marked["issues"]
    scenes = [{"t0": 0, "t1": 1.5}, {"t0": 1.5, "t1": 4.0, "static": True}, {"t0": 4.0, "t1": 5.0}]
    by_plan = run_post(tmp_path / "p", d / "static_clean.mp4", source=d / "src.mp4", aspect="9:16", scenes=scenes)
    in_static = lambda i: i["t"] and i["t"][0] < 3.9 and i["t"][1] > 1.6   # (scene 0 is a bare talking head: a WARN there is fair)
    assert not [i for i in by_plan["issues"] if i["check"] in ("RENDER_FREEZE", "MOTION_ANIMATION") and in_static(i)], by_plan["issues"]
    assert _fails(by_plan) == []
    unmarked = run_post(tmp_path / "u", d / "static_clean.mp4", source=d / "src.mp4", aspect="9:16")
    assert _fails(unmarked) == []   # never a blocking failure just because the picture holds still


# ───────────────────────── clarity: T24 / T25 references ─────────────────────────
def test_clarity_reference(fx, tmp_path):
    d, _ = fx
    sharp = run_post(tmp_path / "s", d / "good_clean.mp4", source=d / "src.mp4", aspect="9:16", template="T24", captions_burned=False)
    soft = run_post(tmp_path / "b", d / "blur_clean.mp4", source=d / "src.mp4", aspect="9:16", template="T24", captions_burned=False)
    assert _sev(sharp, "QUALITY_SHARPNESS") == "PASS"
    assert _sev(soft, "QUALITY_SHARPNESS") == "WARN" and _fails(soft) == []   # possible blur is a WARN, never a block
    assert Config().for_template("T24")["quality"]["min_sharpness_ratio"] > Config().for_template("T05")["quality"]["min_sharpness_ratio"]


# ───────────────────────── SRT / ASR ─────────────────────────
def _srt(fx, name):
    return (fx[0] / "srt" / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("name,check", [("end_before_start.srt", "SRT_TIMING"), ("out_of_order.srt", "SRT_ORDER"),
                                        ("after_end.srt", "SRT_BOUNDS"), ("bad_syntax.srt", "SRT_SYNTAX")])
def test_invalid_srt_fails(fx, name, check):
    probs, _ = subs.validate_srt(_srt(fx, name), duration=5.0)
    assert ("FAIL", check) in {(p[0], p[1]) for p in probs}, probs


def test_srt_overlap_is_warning(fx):
    probs, _ = subs.validate_srt(_srt(fx, "overlap.srt"), duration=5.0)
    assert {p[0] for p in probs} == {"WARN"} and probs[0][1] == "SRT_ORDER"


def test_bilingual_and_monolingual_srt(fx):
    probs, cues = subs.validate_srt(_srt(fx, "good_bilingual.srt"), duration=5.0)
    assert not [p for p in probs if p[0] == "FAIL"] and set(subs.tracks(cues)) == {"cn", "en"}
    zh = "1\n00:00:00,500 --> 00:00:02,000\n大家好\n\n2\n00:00:02,100 --> 00:00:03,500\n我是 Eva\n"
    en = "1\n00:00:00,500 --> 00:00:02,000\nHello\n\n2\n00:00:02,100 --> 00:00:03,500\nI'm Eva\n"
    paired = "1\n00:00:00,500 --> 00:00:02,000\n大家好\nHello everyone\n\n2\n00:00:02,100 --> 00:00:03,500\n我是 Eva\nI'm Eva\n"
    for text, tr in ((zh, {"cn"}), (en, {"en"}), (paired, {"cn+en"})):
        p, c = subs.validate_srt(text, duration=4.0)
        assert not [x for x in p if x[0] == "FAIL"] and set(subs.tracks(c)) == tr, (tr, p)


def test_bilingual_missing_english_partner_warns(fx):
    text = _srt(fx, "good_bilingual.srt").replace("2\n00:00:02,200 --> 00:00:04,600\nWelcome to Eva Video Style.\n", "")
    probs, _ = subs.validate_srt(text, duration=5.0)
    assert ("WARN", "SRT_PAIRING") in {(p[0], p[1]) for p in probs}


def test_burned_captions_must_follow_srt(fx, tmp_path):
    d, _ = fx
    shifted = tmp_path / "shifted.srt"
    shifted.write_text((d / "good.srt").read_text().replace("00:00:01,800", "00:00:02,600"), encoding="utf-8")
    r = run_post(tmp_path, d / "good_final.mp4", clean=d / "good_clean.mp4", ass=d / "good.ass", srt=shifted, aspect="9:16")
    assert "CAP_TIMING" in _fails(r)


def test_srt_cli_exit_codes(fx):
    ok = subprocess.run([sys.executable, "-m", "qa", "srt", str(fx[0] / "srt/good_bilingual.srt"), "--duration", "5"], cwd=REPO, capture_output=True)
    bad = subprocess.run([sys.executable, "-m", "qa", "srt", str(fx[0] / "srt/end_before_start.srt")], cwd=REPO, capture_output=True)
    assert ok.returncode == 0 and bad.returncode == 1


# ───────────────────────── Stage A: page trace (assets, layout, animation) ─────────────────────────
def _has_playwright():
    if not shutil.which("node"): return False
    return subprocess.run(["node", "-e", "require('playwright')"], cwd=REPO, capture_output=True).returncode == 0


needs_browser = pytest.mark.skipif(not _has_playwright(), reason="node + Playwright not available")


def run_pre(fx, tmp_path, case, **ctx):
    q = f"case={case}&eva={fx[0] / 'media/eva'}&{FX.FACE_Q}"
    return pre.run(dict(page=str(FX.PAGE), query=q, **ctx), tmp_path / "pre")


@needs_browser
def test_pre_good_page_passes(fx, tmp_path):
    r = run_pre(fx, tmp_path, "good", template="T17")
    assert r["verdict"] == "PASS", r["issues"]


@needs_browser
def test_pre_missing_image_and_font_fail(fx, tmp_path):
    r = run_pre(fx, tmp_path, "missing")
    assert {"ASSET_MISSING", "ASSET_FONT"} <= set(_fails(r)), r["issues"]


@needs_browser
def test_pre_missing_presenter_frames_fail(fx, tmp_path):
    frames = tmp_path / "eva"; shutil.copytree(fx[0] / "media/eva", frames)
    for n in range(40, 70): (frames / f"f_{n:05d}.jpg").unlink()
    r = pre.run(dict(page=str(FX.PAGE), query=f"case=good&eva={frames}&{FX.FACE_Q}", frames_dir=str(frames)), tmp_path / "pre")
    assert {"ASSET_FRAMES", "ASSET_MISSING"} <= set(_fails(r)), r["issues"]
    i = next(i for i in r["issues"] if i["check"] == "ASSET_MISSING")
    assert "missing in" in i["message"]   # one grouped issue per frame folder, not one per file


@needs_browser
def test_pre_t17_text_over_face_fails(fx, tmp_path):
    r = run_pre(fx, tmp_path, "face_text", template="T17")
    assert "LAYOUT_TEXT_FACE" in _fails(r), r["issues"]


@needs_browser
def test_pre_t26_zoom_layout_fails(fx, tmp_path):
    r = run_pre(fx, tmp_path, "zoom", template="T26")
    assert {"LAYOUT_SCALE", "LAYOUT_FACE_CLIP"} <= set(_fails(r)), r["issues"]


@needs_browser
def test_pre_static_scene(fx, tmp_path):
    unmarked = run_pre(fx, tmp_path / "u", "static")
    assert _sev(unmarked, "ANIM_STATIC") == "WARN" and _fails(unmarked) == []
    marked = run_pre(fx, tmp_path / "m", "static", static_ranges=[[2.0, 4.0]])
    assert _sev(marked, "ANIM_STATIC") == "PASS", marked["issues"]


def test_pre_plan_and_srt(fx, tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"end": 5, "sections": [{"t0": 0, "t1": 2, "template": "T17"}, {"t0": 2.5, "t1": 5, "template": "T99"}],
                                "cards": [{"t_in": 4, "t_out": 3}]}))
    r = pre.run(dict(input=str(fx[0] / "src.mp4"), srt=str(fx[0] / "srt/end_before_start.srt"), plan=str(plan),
                     face={"x": .5, "y": .36, "h": .26}), tmp_path / "pre")
    assert {"PRE_PLAN", "SRT_TIMING"} <= set(_fails(r)), r["issues"]
    assert _sev(r, "PRE_TEMPLATE") == "WARN"   # unknown template id: default thresholds, said so
    assert _sev(r, "PRE_INPUT") == "PASS"


# ───────────────────────── real production renders (site/demos, worker image, real uploads) ─────────────────────────
real = pytest.mark.skipif(not (DEMO / "education/after.mp4").exists(), reason="site/demos not present")


@real
@pytest.mark.parametrize("clip", ["education", "realestate"])
def test_real_production_render_passes(clip, tmp_path):
    """720x1280 website copies of real worker renders (education = T17 + T20, real estate = T20 + T01)"""
    r = run_post(tmp_path, DEMO / clip / "after.mp4", source=DEMO / clip / "before.mp4", aspect="9:16", size=[720, 1280], expected_frames=301)
    assert _fails(r) == [], r["issues"]
    assert r["info"]["face_samples"]["matched_high"] >= 15


@real
def test_real_render_with_defects_is_caught(tmp_path):
    """the same real render with a T26-style reposition (moved right + enlarged 1.35x) and a truncated ending"""
    src, good = DEMO / "education/before.mp4", DEMO / "education/after.mp4"
    bad = tmp_path / "t26_real.mp4"
    FX.ff("-i", good, "-vf", "scale=972:1728,pad=1260:1728:0:0,crop=720:1280:0:224", *FX.X264, "-c:a", "copy", bad)   # head pushed past the right edge
    r = run_post(tmp_path / "a", bad, source=src, aspect="9:16", size=[720, 1280], template="T26")
    assert {"FACE_SCALE", "FACE_CROP"} & set(_fails(r)), r["issues"]
    cut = tmp_path / "cut.mp4"; FX.ff("-i", good, "-t", "8.5", "-c", "copy", cut)
    assert "RENDER_DURATION" in _fails(run_post(tmp_path / "b", cut, aspect="9:16", size=[720, 1280], expected_frames=301))


@real
def test_real_render_caption_over_face_is_caught(tmp_path):
    src, good = DEMO / "education/before.mp4", DEMO / "education/after.mp4"
    a = tmp_path / "face.ass"
    FX.ass(a, 720, 1280, [(1.0, 6.0, "{\\an5\\pos(360,470)}COVERING THE FACE")])
    out = tmp_path / "face.mp4"; FX.ff("-i", good, "-vf", f"ass={a}", *FX.X264, "-c:a", "copy", out)
    r = run_post(tmp_path / "q", out, clean=good, source=src, ass=a, aspect="9:16", size=[720, 1280], template="T17")
    assert "CAP_FACE" in _fails(r), r["issues"]


# ───────────────────────── config + report ─────────────────────────
def test_threshold_resolution_order(tmp_path):
    c = Config({"templates": {"T26": {"face": {"max_subject_scale": 1.01}}}}, category="science")
    assert c.for_template("T26")["face"]["max_subject_scale"] == 1.01          # override file > template
    assert c.for_template("T05")["face"]["face_safe_text"] is True             # category science
    assert Config().for_template("T26")["face"]["max_subject_scale"] == 1.08   # template > defaults
    assert Config().for_template("T05")["face"]["max_subject_scale"] == 1.35


def test_report_files_and_issue_fields(fx, tmp_path):
    d, _ = fx
    r = run_post(tmp_path, d / "oob_final.mp4", clean=d / "good_clean.mp4", source=d / "src.mp4", ass=d / "oob.ass", aspect="9:16")
    js = json.loads((tmp_path / "qa/qa-report.json").read_text())
    assert js["schema"] == "eva-qa/1" and js["verdict"] == r["verdict"] == "FAIL" and js["blocking"]
    for i in js["issues"]:
        assert {"check", "severity", "t", "scene", "template", "message", "evidence", "fix"} <= set(i)
        assert i["severity"] in ("WARN", "FAIL")
    assert (tmp_path / "qa/qa-summary.md").read_text().startswith("# Eva Video QA")
    assert any((tmp_path / "qa" / i["evidence"]).exists() for i in js["issues"] if i["evidence"])
