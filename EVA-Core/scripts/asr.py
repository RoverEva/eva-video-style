#!/usr/bin/env python3
"""Eva Video Style · speech recognition through eva-asr (https://github.com/RoverEva/eva-asr).

Turns a raw talking-head video into the subtitle files the rest of the pipeline already uses. All ASR work
(VAD, Whisper transcription, wav2vec2 word alignment, X->English translation, SRT writing) is done by
eva-asr's own library API (`whisperx.load_model`, `.transcribe`, `whisperx.load_align_model`, `whisperx.align`,
`whisperx.utils.WriteSRT`); this script only wires it into Eva Video Style.

usage: asr.py VIDEO OUT_BASENAME [--config asr.json] [--model NAME] [--device cpu|cuda] [--language zh]
              [--no-translate] [--no-align] [--model-dir DIR] [--model-cache-only]

writes (never overwrites; refuses if any already exists):
  OUT_BASENAME.zh.srt         source-language cues (word-aligned), named by the language code
  OUT_BASENAME.en.srt         English translation cues (only when translating a non-English source)
  OUT_BASENAME.bilingual.srt  source block followed by English block: the bilingual SRT captions.py expects
  OUT_BASENAME.asr.json       full eva-asr results (segments + word timestamps)
  OUT_BASENAME.transcript.js  window.EV_ASR = {...}: word timings for scenes.js (see engine/asr.js)

Next step:  python3 scripts/captions.py OUT_BASENAME.bilingual.srt 0 99999 out/NAME_CN-EN [display_fix.json]

exit codes: 0 ok · 1 refusing to overwrite · 2 bad input/config · 3 eva-asr or its dependencies missing ·
            4 model load / inference failure · 5 no speech recognised
"""
import argparse, gc, importlib, importlib.util, json, os, shutil, subprocess, sys

DEFAULTS = {
    "eva_asr_path": None,          # path to an eva-asr checkout; None = use the installed `whisperx` package
    "model": "large-v3",           # Whisper model name or local CTranslate2 dir (turbo models cannot translate)
    "device": "auto",              # auto | cpu | cuda
    "device_index": 0,
    "compute_type": "default",     # default | float16 | float32 | int8 (int8 is the fast choice on CPU)
    "batch_size": 8,
    "threads": 0,
    "language": "zh",              # source language code, or null to let eva-asr detect it
    "translate_to_en": True,       # also run eva-asr's translate task to get the English line
    "align": True,                 # word-level timestamps via eva-asr's wav2vec2 alignment
    "align_model": None,
    "interpolate_method": "nearest",
    "vad_method": "pyannote",      # pyannote (bundled in eva-asr) | silero
    "vad_onset": 0.5,
    "vad_offset": 0.363,
    "chunk_size": 30,
    "initial_prompt": None,
    "hotwords": None,
    "model_dir": None,
    "model_cache_only": False,
    "hf_token_env": "HF_TOKEN",    # env var holding a Hugging Face token (only for gated models)
    "max_line_width": None,        # passed to eva-asr's SRT writer for the aligned source cues
    "max_line_count": None,
}
REQUIRED_MODULES = ["torch", "faster_whisper", "ctranslate2", "transformers", "pyannote.audio", "nltk", "pandas"]


class AsrError(Exception):
    def __init__(self, msg, code):
        super().__init__(msg); self.code = code


def load_config(path, overrides):
    cfg = dict(DEFAULTS)
    if path:
        try:
            user = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise AsrError(f"cannot read config {path}: {e}", 2)
        unknown = sorted(set(user) - set(DEFAULTS) - {"_comment"})
        if unknown: raise AsrError(f"unknown config keys in {path}: {', '.join(unknown)}", 2)
        cfg.update({k: v for k, v in user.items() if k != "_comment"})
    cfg.update({k: v for k, v in overrides.items() if v is not None})
    if cfg["language"]: cfg["language"] = str(cfg["language"]).lower()
    return cfg


def import_eva_asr(cfg):
    """Import eva-asr's `whisperx` package, from cfg['eva_asr_path'] / $EVA_ASR_PATH if given. Checks the heavy
    runtime deps up front so a missing install fails with one clear message instead of mid-run."""
    path = cfg.get("eva_asr_path") or os.environ.get("EVA_ASR_PATH")
    if path:
        if not os.path.isfile(os.path.join(path, "whisperx", "asr.py")):
            raise AsrError(f"eva_asr_path {path} is not an eva-asr checkout (no whisperx/asr.py)", 2)
        sys.path.insert(0, os.path.abspath(path))
    if importlib.util.find_spec("whisperx") is None:
        raise AsrError("eva-asr is not importable. Install it (pip install -e /path/to/eva-asr) or set "
                       "eva_asr_path in the config / EVA_ASR_PATH.", 3)
    missing = []
    for m in REQUIRED_MODULES:
        try:
            if importlib.util.find_spec(m) is None: missing.append(m)
        except ModuleNotFoundError:
            missing.append(m)
    if missing:
        raise AsrError("eva-asr's runtime dependencies are missing: " + ", ".join(missing) +
                       ". Install them with: pip install -e /path/to/eva-asr  (CPU-only torch: add "
                       "--extra-index-url https://download.pytorch.org/whl/cpu)", 3)
    return importlib.import_module("whisperx")


def probe_audio(video):
    if not os.path.isfile(video): raise AsrError(f"input not found: {video}", 2)
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None: raise AsrError(f"{tool} not found on PATH (eva-asr decodes audio with ffmpeg)", 2)
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                        "-of", "csv=p=0", video], capture_output=True, text=True)
    if r.returncode != 0: raise AsrError(f"ffprobe cannot read {video}: {r.stderr.strip()}", 2)
    if not r.stdout.strip(): raise AsrError(f"{video} has no audio stream", 2)


def pick_device(cfg):
    if cfg["device"] != "auto": return cfg["device"]
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def run_asr(wx, video, cfg, log=print):
    """Run eva-asr on `video`. Returns {"source": aligned/transcribed result, "en": translation result or None}.
    `wx` is the eva-asr `whisperx` module (injected so tests can substitute the model layer)."""
    device = pick_device(cfg)
    lang = cfg["language"]
    asr_options = {"initial_prompt": cfg["initial_prompt"], "hotwords": cfg["hotwords"]}
    log(f"[asr] eva-asr model={cfg['model']} device={device} compute={cfg['compute_type']} language={lang or 'auto'}")
    try:
        model = wx.load_model(cfg["model"], device=device, device_index=cfg["device_index"],
                              compute_type=cfg["compute_type"], language=lang, asr_options=asr_options,
                              vad_method=cfg["vad_method"],
                              vad_options={"chunk_size": cfg["chunk_size"], "vad_onset": cfg["vad_onset"], "vad_offset": cfg["vad_offset"]},
                              task="transcribe", download_root=cfg["model_dir"], local_files_only=cfg["model_cache_only"],
                              threads=cfg["threads"] or 4, use_auth_token=os.environ.get(cfg["hf_token_env"] or "") or None)
    except Exception as e:
        raise AsrError(f"eva-asr could not load model '{cfg['model']}': {type(e).__name__}: {e}. If this machine is "
                       "offline, download the model first or point `model` / `model_dir` at a local copy.", 4)
    try:
        audio = wx.load_audio(video)
        src = model.transcribe(audio, batch_size=cfg["batch_size"], chunk_size=cfg["chunk_size"], language=lang, task="transcribe")
        lang = src.get("language") or lang
        log(f"[asr] transcribed {len(src['segments'])} segments (language {lang})")
        if not src["segments"]: raise AsrError("eva-asr found no speech in the audio", 5)
        en = None
        if cfg["translate_to_en"] and lang != "en":
            if "turbo" in str(cfg["model"]):
                log("[asr] warning: Whisper turbo models are not trained for translation; the English line may be poor")
            en = model.transcribe(audio, batch_size=cfg["batch_size"], chunk_size=cfg["chunk_size"], language=lang, task="translate")
            en["language"] = "en"
            log(f"[asr] translated {len(en['segments'])} segments to English")
    except AsrError:
        raise
    except Exception as e:
        raise AsrError(f"eva-asr transcription failed: {type(e).__name__}: {e}", 4)
    finally:
        model = None; gc.collect()
    if cfg["align"]:
        try:
            am, meta = wx.load_align_model(lang, device, model_name=cfg["align_model"], model_dir=cfg["model_dir"],
                                           model_cache_only=cfg["model_cache_only"])
        except Exception as e:
            raise AsrError(f"eva-asr could not load the alignment model for '{lang}': {type(e).__name__}: {e}. "
                           "Set align=false to keep segment-level timings.", 4)
        try:
            aligned = wx.align(src["segments"], am, meta, audio, device, interpolate_method=cfg["interpolate_method"])
        except Exception as e:
            raise AsrError(f"eva-asr alignment failed: {type(e).__name__}: {e}", 4)
        aligned["language"] = lang
        src = aligned
        log(f"[asr] aligned {len(src.get('word_segments', []))} words")
    src["language"] = lang
    return {"source": src, "en": en}


def srt_text(result, opts):
    from whisperx.utils import WriteSRT   # eva-asr's own SRT writer
    import io
    buf = io.StringIO()
    WriteSRT(".").write_result(result, file=buf, options=opts)
    return buf.getvalue()


def renumber(*srts):
    out, n = [], 0
    for s in srts:
        for block in [b for b in s.strip().split("\n\n") if b.strip()]:
            lines = block.strip().splitlines()
            if len(lines) < 3 or "-->" not in lines[1]: continue
            n += 1; out.append(f"{n}\n" + "\n".join(lines[1:]))
    return "\n\n".join(out) + "\n"


def _timed(w):
    import math
    try: return math.isfinite(float(w["start"])) and math.isfinite(float(w["end"]))
    except (KeyError, TypeError, ValueError): return False


def transcript_data(res):
    src, en = res["source"], res["en"]
    segs = [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip(),
             "words": [{"w": w["word"], **({"start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)} if _timed(w) else {})}
                       for w in s.get("words", [])]} for s in src["segments"]]
    return {"source": "eva-asr", "language": src["language"], "segments": segs,
            "en": [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip()} for s in (en or {}).get("segments", [])]}


def write_outputs(res, base, cfg):
    lang = res["source"]["language"]
    opts = {"max_line_width": cfg["max_line_width"], "max_line_count": cfg["max_line_count"], "highlight_words": False}
    files = {f"{base}.{lang}.srt": srt_text(res["source"], opts)}
    if res["en"] is not None:
        files[f"{base}.en.srt"] = srt_text(res["en"], {"max_line_width": None, "max_line_count": None, "highlight_words": False})
    files[f"{base}.bilingual.srt"] = renumber(*files.values())
    data = transcript_data(res)
    files[f"{base}.asr.json"] = json.dumps({"source": res["source"], "en": res["en"]}, ensure_ascii=False, indent=1)
    files[f"{base}.transcript.js"] = ("/* generated by scripts/asr.py from eva-asr; times are absolute seconds in the source video */\n"
                                     "window.EV_ASR = " + json.dumps(data, ensure_ascii=False) + ";\n")
    for p, content in files.items():
        with open(p, "x", encoding="utf-8") as f: f.write(content)
    return list(files)


def main(argv=None, wx=None):
    ap = argparse.ArgumentParser(description="Video -> eva-asr -> Eva Video Style subtitles")
    ap.add_argument("video"); ap.add_argument("out_base")
    ap.add_argument("--config"); ap.add_argument("--model"); ap.add_argument("--device"); ap.add_argument("--language")
    ap.add_argument("--compute-type", dest="compute_type"); ap.add_argument("--batch-size", dest="batch_size", type=int)
    ap.add_argument("--model-dir", dest="model_dir"); ap.add_argument("--eva-asr-path", dest="eva_asr_path")
    ap.add_argument("--no-translate", dest="translate_to_en", action="store_const", const=False)
    ap.add_argument("--no-align", dest="align", action="store_const", const=False)
    ap.add_argument("--model-cache-only", dest="model_cache_only", action="store_const", const=True)
    a = vars(ap.parse_args(argv))
    video, base, cfgpath = a.pop("video"), a.pop("out_base"), a.pop("config")
    try:
        cfg = load_config(cfgpath, a)
        lang_guess = cfg["language"] or "auto"
        planned = [f"{base}.{x}" for x in (f"{lang_guess}.srt", "en.srt", "bilingual.srt", "asr.json", "transcript.js")]
        clash = [p for p in planned if os.path.exists(p)]
        if clash: raise AsrError("Refusing to overwrite " + ", ".join(clash), 1)
        probe_audio(video)
        if wx is None: wx = import_eva_asr(cfg)
        res = run_asr(wx, video, cfg)
        d = os.path.dirname(os.path.abspath(base)); os.makedirs(d, exist_ok=True)
        written = write_outputs(res, base, cfg)
    except FileExistsError as e:
        print(f"Refusing to overwrite {e.filename}", file=sys.stderr); return 1
    except AsrError as e:
        print(f"[asr] error: {e}", file=sys.stderr); return e.code
    for p in written: print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
