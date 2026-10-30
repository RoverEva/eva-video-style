"""Tests for scripts/asr.py (eva-asr integration).

eva-asr's real code is used wherever it runs without torch: the `whisperx` package import, `whisperx.utils.WriteSRT`
(the SRT writer), the dependency check. Only the model layer (load_model / load_audio / load_align_model / align),
which needs torch + downloaded Whisper/wav2vec2 weights, is replaced by FakeWX with eva-asr-shaped results.
Set EVA_ASR_PATH to an eva-asr checkout (default: ../eva-asr next to this repo).
"""
import importlib.util, json, os, subprocess, sys, types
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EVA_ASR = Path(os.environ.get("EVA_ASR_PATH", ROOT.parent / "eva-asr"))
if not (EVA_ASR / "whisperx" / "asr.py").is_file():
    pytest.skip(f"eva-asr checkout not found at {EVA_ASR} (set EVA_ASR_PATH)", allow_module_level=True)
sys.path.insert(0, str(EVA_ASR))
spec = importlib.util.spec_from_file_location("asr", ROOT / "scripts" / "asr.py")
asr = importlib.util.module_from_spec(spec); spec.loader.exec_module(asr)

ZH = [  # eva-asr transcribe() result shape: {"segments":[{start,end,text}], "language"}
    {"start": 0.50, "end": 2.40, "text": "大家好，我是Eva。"},
    {"start": 2.80, "end": 5.10, "text": "今天聊聊三个月的变化。"},
]
EN = [
    {"start": 0.50, "end": 2.40, "text": " Hi everyone, I'm Eva."},
    {"start": 2.80, "end": 5.10, "text": " Today let's talk about three months of change."},
]


def chars(seg, nan_at=None):
    """eva-asr align() output for Chinese: one 'word' per character, evenly spread."""
    cs = [c for c in seg["text"]]; d = (seg["end"] - seg["start"]) / len(cs); out = []
    for i, c in enumerate(cs):
        w = {"word": c, "start": round(seg["start"] + i * d, 3), "end": round(seg["start"] + (i + 1) * d, 3), "score": .9}
        if nan_at == i: w = {"word": c}          # eva-asr leaves unalignable chars without times
        out.append(w)
    return out


class FakeModel:
    def __init__(self, wx): self.wx = wx
    def transcribe(self, audio, batch_size=None, chunk_size=30, language=None, task=None, **kw):
        self.wx.calls.append(("transcribe", task, language))
        if self.wx.fail_transcribe: raise RuntimeError("CUDA out of memory")
        if task == "translate": return {"segments": [dict(s) for s in self.wx.en], "language": language}
        return {"segments": [dict(s) for s in self.wx.src], "language": language or "zh"}


class FakeWX(types.SimpleNamespace):
    def __init__(self, src=ZH, en=EN, fail_load=False, fail_transcribe=False, nan=False):
        super().__init__(src=src, en=en, fail_load=fail_load, fail_transcribe=fail_transcribe, nan=nan, calls=[])
    def load_model(self, arch, device, **kw):
        self.calls.append(("load_model", arch, device, kw["task"], kw["language"]))
        if self.fail_load: raise OSError("We couldn't connect to 'https://huggingface.co'")
        return FakeModel(self)
    def load_audio(self, path): self.calls.append(("load_audio", path)); return [0.0] * 16000
    def load_align_model(self, lang, device, **kw): self.calls.append(("load_align_model", lang)); return object(), {"language": lang}
    def align(self, segments, model, meta, audio, device, **kw):
        segs = []
        for j, s in enumerate(segments):
            if meta["language"] == "zh": ws = chars(s, nan_at=2 if (self.nan and j == 0) else None)
            else:
                toks = s["text"].split(); d = (s["end"] - s["start"]) / len(toks)
                ws = [{"word": t, "start": s["start"] + i * d, "end": s["start"] + (i + 1) * d, "score": .9} for i, t in enumerate(toks)]
            segs.append({**s, "words": ws})
        return {"segments": segs, "word_segments": [w for s in segs for w in s["words"]]}


@pytest.fixture(scope="session")
def video(tmp_path_factory):
    d = tmp_path_factory.mktemp("media")
    v = d / "talk.mp4"; mute = d / "mute.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=320x180:r=30:d=6",
                    "-f", "lavfi", "-i", "sine=f=220:d=6", "-shortest", "-c:v", "libx264", "-c:a", "aac", str(v)], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=320x180:r=30:d=2",
                    "-c:v", "libx264", str(mute)], check=True)
    return {"ok": str(v), "mute": str(mute)}


def run(video, base, wx=None, *extra):
    return asr.main([video, str(base), *extra], wx=wx or FakeWX())


def test_full_chain_writes_bilingual_srt_for_captions(video, tmp_path):
    wx = FakeWX(); base = tmp_path / "srt" / "talk"
    assert run(video["ok"], base, wx) == 0
    # one model load, two tasks on it, aligned in the source language
    assert [c[0] for c in wx.calls] == ["load_model", "load_audio", "transcribe", "transcribe", "load_align_model"]
    assert ("transcribe", "transcribe", "zh") in wx.calls and ("transcribe", "translate", "zh") in wx.calls
    zh = (tmp_path / "srt" / "talk.zh.srt").read_text("utf-8")
    assert "00:00:00,500 --> 00:00:02,400\n大家好，我是Eva。" in zh   # eva-asr WriteSRT joins zh chars without spaces
    bi = (tmp_path / "srt" / "talk.bilingual.srt").read_text("utf-8")
    blocks = [b.splitlines() for b in bi.strip().split("\n\n")]
    assert [b[0] for b in blocks] == ["1", "2", "3", "4"]
    assert blocks[0][2] == "大家好，我是Eva。" and blocks[2][2] == "Hi everyone, I'm Eva."
    # the existing caption step consumes it unchanged
    out = tmp_path / "out" / "NAME_CN-EN"; out.parent.mkdir()
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "captions.py"), str(base) + ".bilingual.srt", "0", "99999", str(out)],
                       capture_output=True, text=True, check=True)
    assert "2 cues" in r.stdout
    srt = (tmp_path / "out" / "NAME_CN-EN.srt").read_text("utf-8")
    assert "大家好，我是Eva。\nHi everyone, I'm Eva." in srt
    ass = (tmp_path / "out" / "NAME_CN-EN.ass").read_text("utf-8")
    assert r"大家好，我是Eva。\N{\rEN}Hi everyone, I'm Eva." in ass


def test_transcript_js_has_word_times(video, tmp_path):
    base = tmp_path / "talk"; assert run(video["ok"], base, FakeWX(nan=True)) == 0
    js = (tmp_path / "talk.transcript.js").read_text("utf-8")
    assert js.splitlines()[1].startswith("window.EV_ASR = ")
    data = json.loads(js.splitlines()[1][len("window.EV_ASR = "):-1])
    assert data["source"] == "eva-asr" and data["language"] == "zh"
    w0 = data["segments"][0]["words"]
    assert w0[0] == {"w": "大", "start": 0.5, "end": 0.69} and w0[2] == {"w": "好"}   # untimed char kept, no NaN
    assert data["en"][1]["text"].startswith("Today")
    full = json.loads((tmp_path / "talk.asr.json").read_text("utf-8"))
    assert len(full["source"]["word_segments"]) == sum(len(s["text"]) for s in ZH)


def test_refuses_to_overwrite(video, tmp_path):
    base = tmp_path / "talk"; (tmp_path / "talk.bilingual.srt").write_text("keep")
    assert run(video["ok"], base) == 1
    assert (tmp_path / "talk.bilingual.srt").read_text() == "keep"


def test_input_errors(video, tmp_path, capsys):
    assert run(str(tmp_path / "missing.mp4"), tmp_path / "a") == 2
    assert run(video["mute"], tmp_path / "b") == 2
    assert "no audio stream" in capsys.readouterr().err


def test_bad_config(video, tmp_path, capsys):
    cfg = tmp_path / "c.json"; cfg.write_text('{"modle": "small"}')
    assert run(video["ok"], tmp_path / "a", None, "--config", str(cfg)) == 2
    assert "unknown config keys" in capsys.readouterr().err
    cfg.write_text("{not json")
    assert run(video["ok"], tmp_path / "b", None, "--config", str(cfg)) == 2


def test_model_failures_are_reported(video, tmp_path, capsys):
    assert run(video["ok"], tmp_path / "a", FakeWX(fail_load=True)) == 4
    assert "could not load model 'large-v3'" in capsys.readouterr().err
    assert run(video["ok"], tmp_path / "b", FakeWX(fail_transcribe=True)) == 4
    assert run(video["ok"], tmp_path / "c", FakeWX(src=[])) == 5
    assert not list(tmp_path.glob("*.srt"))


def test_english_source_skips_translation_and_captions_still_work(video, tmp_path):
    src = [{"start": 0.4, "end": 2.0, "text": " Hello, I'm Eva."}, {"start": 2.4, "end": 4.0, "text": " Welcome back."}]
    wx = FakeWX(src=src); base = tmp_path / "talk"
    assert run(video["ok"], base, wx, "--language", "en", "--model", "small") == 0
    assert not any(c[1] == "translate" for c in wx.calls if c[0] == "transcribe")
    assert "Hello, I'm Eva." in (tmp_path / "talk.en.srt").read_text("utf-8")   # source-language file, aligned words
    for mode, style in (("cn-en", "CN"), ("en", "ENB")):
        cfg = tmp_path / f"{mode}.json"; cfg.write_text(json.dumps({"mode": mode}))
        out = tmp_path / f"o_{mode}"
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "captions.py"), str(base) + ".bilingual.srt", "0", "99999", str(out), str(cfg)],
                           capture_output=True, text=True, check=True)
        assert "2 cues" in r.stdout
        assert f",{style},,0,0,0,,{{\\fad(60,40)}}Hello, I'm Eva." in (tmp_path / f"o_{mode}.ass").read_text("utf-8")


def test_missing_eva_asr_dependencies_are_named():
    """Real check against this machine's environment (no fake): reports exactly which eva-asr deps are absent."""
    try:
        asr.import_eva_asr({"eva_asr_path": str(EVA_ASR)})
    except asr.AsrError as e:
        assert e.code == 3 and "pip install -e" in str(e)
        missing = [m for m in asr.REQUIRED_MODULES if importlib.util.find_spec(m.split(".")[0]) is None]
        assert all(m.split(".")[0] in str(e) for m in missing)
    else:
        pass  # all deps installed: nothing to report


def test_bad_eva_asr_path(tmp_path):
    with pytest.raises(asr.AsrError) as e: asr.import_eva_asr({"eva_asr_path": str(tmp_path)})
    assert e.value.code == 2


def test_captions_py_unchanged_for_bilingual_input(tmp_path):
    """Regression: the captions.py edit only affects SRTs with no Chinese cues."""
    srt = tmp_path / "bi.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:03,000\n你好\n\n2\n00:00:03,500 --> 00:00:05,000\noh my god\n\n"
                   "3\n00:00:01,000 --> 00:00:03,000\nHello\n\n4\n00:00:03,500 --> 00:00:05,000\nOh my god\n", "utf-8")
    old = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:scripts/captions.py"], capture_output=True, text=True)
    if old.returncode != 0 or "if not cnl" in old.stdout: pytest.skip("no pre-integration captions.py in HEAD")
    (tmp_path / "old_captions.py").write_text(old.stdout)
    for name, script in (("old", tmp_path / "old_captions.py"), ("new", ROOT / "scripts" / "captions.py")):
        subprocess.run([sys.executable, str(script), str(srt), "0", "99", str(tmp_path / name)], check=True, capture_output=True)
    for ext in (".srt", ".ass"):
        assert (tmp_path / ("old" + ext)).read_text() == (tmp_path / ("new" + ext)).read_text()
