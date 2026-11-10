"""QA regression fixtures built with FFmpeg from a REAL presenter clip (saas/tests/media/education.mp4).

The presenter, her face and her voice are real footage; each DEFECT is synthetic (a known crop, zoom, caption position,
stretch, black gap ...), so every test knows the right answer. They test the QA logic, not real-world face-detection
accuracy (see qa/README.md "What is verified").

    python3 -m qa.tests.fixtures OUT_DIR      build everything (≈ 20 s, cached)
"""
import json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "saas/tests/media/education.mp4"
FONT = REPO / "engine/fonts/Anton-Regular.ttf"
DUR = 5.0
BEIGE = "0xd8c5b5"


def ff(*a):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *map(str, a)], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-500:])


def ass(path, W, H, events, wrap=0, margin_v=440):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: {wrap}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ENB,Inter Black,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0.5,0,1,4,2,2,110,170,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    f = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02}:{t % 60:05.2f}"
    Path(path).write_text(head + "".join(f"Dialogue: 0,{f(a)},{f(b)},ENB,,0,0,0,,{{\\fad(60,40)}}{txt}\n" for a, b, txt in events), encoding="utf-8")


def srt(path, events):
    f = lambda t: f"{int(t // 3600):02}:{int(t % 3600 // 60):02}:{int(t % 60):02},{round(t % 1 * 1000) % 1000:03}"
    Path(path).write_text("\n".join(f"{i}\n{f(a)} --> {f(b)}\n{re_plain(t)}\n" for i, (a, b, t) in enumerate(events, 1)), encoding="utf-8")


def re_plain(t):
    import re
    return re.sub(r"\{[^}]*\}", "", t)


# caption times follow the two spoken phrases in the first 5 s of the clip (0.13-1.49 s and 1.78-4.09 s, energy VAD);
# the caption WORDS are placeholders, not a transcript
CUES = [(0.15, 1.55, "Hi, I'm Eva."), (1.8, 4.2, "Welcome to Eva Video Style.")]
X264 = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30"]


def build(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    done = out / "fixtures.json"
    if done.exists(): return json.loads(done.read_text())
    P = lambda n: out / n
    # the "upload": 5 s of the real 720x1280 clip at 30 fps
    ff("-i", SRC, "-t", DUR, "-vf", "fps=30", *X264, "-c:a", "aac", P("src.mp4"))
    ass(P("good.ass"), 1080, 1920, CUES); srt(P("good.srt"), CUES)
    # good 9:16 render: footage at its own size (full-bleed), captions in the caption zone
    ff("-i", P("src.mp4"), "-vf", "scale=1080:1920:flags=lanczos", *X264, "-c:a", "copy", P("good_clean.mp4"))
    ff("-i", P("good_clean.mp4"), "-vf", f"ass={P('good.ass')}", *X264, "-c:a", "copy", P("good_final.mp4"))
    # T26 regression: presenter moved right AND enlarged 1.5x -> half the face beyond the right edge
    ff("-f", "lavfi", "-i", f"color=c={BEIGE}:s=1080x1920:r=30:d={DUR}", "-i", P("src.mp4"),
       "-filter_complex", "[1:v]scale=1620:2880[p];[0:v][p]overlay=x=300:y=-560:shortest=1", *X264, "-map", "1:a", "-c:a", "copy", P("t26_bad_clean.mp4"))
    # T26 done right: moved right, original scale, whole head in frame
    ff("-f", "lavfi", "-i", f"color=c={BEIGE}:s=1080x1920:r=30:d={DUR}", "-i", P("src.mp4"),
       "-filter_complex", "[1:v]scale=1080:1920[p];[0:v][p]overlay=x=220:y=0:shortest=1", *X264, "-map", "1:a", "-c:a", "copy", P("t26_ok_clean.mp4"))
    # T17 regression: caption placed over the face
    face_cues = [(a, b, "{\\an5\\pos(540,700)}" + t) for a, b, t in CUES]
    ass(P("t17_face.ass"), 1080, 1920, face_cues); srt(P("t17_face.srt"), face_cues)
    ff("-i", P("good_clean.mp4"), "-vf", f"ass={P('t17_face.ass')}", *X264, "-c:a", "copy", P("t17_face_final.mp4"))
    # caption beyond the frame edge (no wrapping, positioned at the right)
    oob = [CUES[0], (CUES[1][0], CUES[1][1], "{\\an4\\pos(620,1420)}" + CUES[1][2])]
    ass(P("oob.ass"), 1080, 1920, oob, wrap=2); srt(P("oob.srt"), oob)
    ff("-i", P("good_clean.mp4"), "-vf", f"ass={P('oob.ass')}", *X264, "-c:a", "copy", P("oob_final.mp4"))
    # 16:9 export: presenter in a right-hand card on a solid stage, captions bottom
    ass(P("land.ass"), 1920, 1080, CUES, margin_v=34)
    ff("-f", "lavfi", "-i", f"color=c=0x0b0b0d:s=1920x1080:r=30:d={DUR}", "-i", P("src.mp4"),
       "-filter_complex", "[1:v]scale=540:960[p];[0:v][p]overlay=x=1240:y=60:shortest=1", *X264, "-map", "1:a", "-c:a", "copy", P("land_clean.mp4"))
    ff("-i", P("land_clean.mp4"), "-vf", f"ass={P('land.ass')}", *X264, "-c:a", "copy", P("land_final.mp4"))
    # wrong export size (a 720p file delivered as the 9:16 HD master)
    ff("-i", P("good_final.mp4"), "-vf", "scale=720:1280", *X264, "-c:a", "copy", P("small_final.mp4"))
    # presenter stretched 1.25x horizontally (fixed width AND height); setsar=1 so the pixels really are distorted
    ff("-i", P("src.mp4"), "-vf", "scale=1350:1920,crop=1080:1920,setsar=1", *X264, "-c:a", "copy", P("stretch_clean.mp4"))
    # head cut at the top (forehead/hair) and at the bottom (chin) by moving the full-size presenter up / down
    for name, y in (("crop_top", -560), ("crop_chin", 1060)):
        ff("-f", "lavfi", "-i", f"color=c={BEIGE}:s=1080x1920:r=30:d={DUR}", "-i", P("src.mp4"),
           "-filter_complex", f"[1:v]scale=1080:1920[p];[0:v][p]overlay=x=0:y={y}:shortest=1", *X264, "-map", "1:a", "-c:a", "copy", P(f"{name}_clean.mp4"))
    # 25 fps export (Eva Video Style masters are 30 fps)
    ff("-i", P("good_final.mp4"), "-vf", "fps=25", *X264[:-2], "-r", "25", "-c:a", "copy", P("fps25_final.mp4"))
    # non-square pixels: player shows it stretched
    ff("-i", P("good_final.mp4"), "-vf", "setsar=4/3", *X264, "-c:a", "copy", P("sar_final.mp4"))
    # intentional static card 1.5-4.0 s (no presenter), voice continues
    ff("-i", P("good_clean.mp4"), "-vf",
       f"drawbox=x=0:y=0:w=iw:h=ih:color=0xd4ff2e:t=fill:enable='between(t,1.5,4.0)',"
       f"drawtext=fontfile={FONT}:text='KEY POINT':fontsize=150:fontcolor=0x0b0b0d:x=(w-text_w)/2:y=600:enable='between(t,1.5,4.0)'",
       *X264, "-c:a", "copy", P("static_clean.mp4"))
    # 1.5 s black gap (failed chunk)
    ff("-i", P("good_final.mp4"), "-vf", "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,2.0,3.5)'", *X264, "-c:a", "copy", P("black_final.mp4"))
    # no audio stream
    ff("-i", P("good_final.mp4"), "-an", "-c:v", "copy", P("noaudio_final.mp4"))
    # soft presenter (blur) for the T24/T25 clarity reference
    ff("-i", P("good_clean.mp4"), "-vf", "gblur=sigma=4", *X264, "-c:a", "copy", P("blur_clean.mp4"))
    # source frames for Stage A pages (30 fps JPGs, like scripts/extract_frames.sh)
    (out / "media/eva").mkdir(parents=True, exist_ok=True)
    ff("-i", P("src.mp4"), "-vf", "fps=30,scale=1080:-2", "-q:v", "3", "-start_number", "0", out / "media/eva/f_%05d.jpg")
    # SRT files
    (out / "srt").mkdir(exist_ok=True)
    (out / "srt/good_bilingual.srt").write_text("1\n00:00:00,300 --> 00:00:02,000\n嗨，我是 Eva。\n\n2\n00:00:02,200 --> 00:00:04,600\n欢迎来到 Eva 视频风格。\n\n"
                                                "1\n00:00:00,300 --> 00:00:02,000\nHi, I'm Eva.\n\n2\n00:00:02,200 --> 00:00:04,600\nWelcome to Eva Video Style.\n", encoding="utf-8")
    (out / "srt/end_before_start.srt").write_text("1\n00:00:02,000 --> 00:00:01,000\nbackwards\n", encoding="utf-8")
    (out / "srt/out_of_order.srt").write_text("1\n00:00:03,000 --> 00:00:04,000\nsecond\n\n2\n00:00:01,000 --> 00:00:02,000\nfirst\n", encoding="utf-8")
    (out / "srt/after_end.srt").write_text("1\n00:00:01,000 --> 00:00:02,000\nok\n\n2\n00:00:07,000 --> 00:00:08,000\nafter the video ends\n", encoding="utf-8")
    (out / "srt/bad_syntax.srt").write_text("1\n00:00:01 --> 00:00:02\nno milliseconds\n", encoding="utf-8")
    (out / "srt/overlap.srt").write_text("1\n00:00:01,000 --> 00:00:03,000\none\n\n2\n00:00:02,000 --> 00:00:04,000\ntwo\n", encoding="utf-8")
    meta = {"dir": str(out), "frames": int(DUR * 30), "engine": render_pages(out)}
    done.write_text(json.dumps(meta)); return meta


PAGE = REPO / "qa/tests/pages/case/index.html"
FACE_Q = "srcw=1080&srch=1920&face=.501,.362,.264"   # calibration of the fixture footage (QA detector, median of 10 frames)


def render_pages(out):
    """engine renders of the test page (scripts/render.mjs, the real renderer): good and the T26 zoom case.
    Skipped (returns {}) when node/Playwright are not available."""
    import shutil
    if not shutil.which("node"): return {}
    res = {}
    for case in ("good", "zoom"):
        mp4 = out / f"engine_{case}.mp4"
        if not mp4.exists():
            r = subprocess.run(["node", str(REPO / "scripts/render.mjs"), str(PAGE), "--out", str(mp4), "--query",
                                f"case={case}&eva={out / 'media/eva'}&{FACE_Q}"], capture_output=True, text=True, cwd=str(REPO))
            if r.returncode: return {}
            # add the real voice so the file is a complete export (render.mjs writes silent sections)
            ff("-i", mp4, "-i", out / "src.mp4", "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", out / f"engine_{case}_av.mp4")
        res[case] = str(out / f"engine_{case}_av.mp4")
    return res


if __name__ == "__main__":
    print(build(sys.argv[1]))
