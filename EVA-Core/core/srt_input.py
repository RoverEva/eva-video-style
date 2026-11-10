#!/usr/bin/env python3
"""Convert a user-supplied SRT into EVA's transcript/timing contract."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


TIME = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})")
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")


def seconds(value: str) -> float:
    match = TIME.fullmatch(value.strip())
    if not match:
        raise ValueError(f"invalid SRT timestamp: {value!r}")
    h, m, s, ms = (int(x) for x in match.groups())
    return h * 3600 + m * 60 + s + ms / 1000


def parse_srt(path: str | Path) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        time_i = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if time_i is None:
            continue
        left, right = [part.strip().split()[0] for part in lines[time_i].split("-->", 1)]
        start, end = seconds(left), seconds(right)
        caption = " ".join(lines[time_i + 1:]).strip()
        if caption and end > start:
            cues.append({"start": start, "end": end, "text": caption})
    if not cues:
        raise ValueError(f"{path} contains no usable SRT cues")
    if any(cues[i]["start"] < cues[i - 1]["start"] for i in range(1, len(cues))):
        raise ValueError("SRT cues are not in chronological order")
    return cues


def tokens(text: str, cjk: bool) -> list[str]:
    if cjk:
        return re.findall(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]|[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)?|[^\s]", text)
    return re.findall(r"\S+", text)


def transcript(cues: list[dict]) -> dict:
    joined = " ".join(cue["text"] for cue in cues)
    cjk = bool(CJK.search(joined))
    language = "zh" if cjk else "en"
    segments = []
    for cue in cues:
        words = tokens(cue["text"], cjk)
        span = cue["end"] - cue["start"]
        step = span / max(1, len(words))
        timed = [{
            "w": word,
            "start": round(cue["start"] + i * step, 3),
            "end": round(cue["start"] + (i + 1) * step, 3),
        } for i, word in enumerate(words)]
        segments.append({"start": cue["start"], "end": cue["end"], "text": cue["text"], "words": timed})
    return {"source": "user-srt", "language": language, "segments": segments, "en": []}


def write_outputs(srt: str | Path, out_base: str | Path) -> list[Path]:
    source, base = Path(srt).resolve(), Path(out_base)
    cues = parse_srt(source)
    data = transcript(cues)
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs = [base.with_suffix(".bilingual.srt"), base.with_suffix(".en.srt")]
    for output in outputs:
        if output.exists():
            raise FileExistsError(output)
        shutil.copyfile(source, output)
    asr = base.with_suffix(".asr.json")
    js = base.with_suffix(".transcript.js")
    if asr.exists() or js.exists():
        raise FileExistsError(asr if asr.exists() else js)
    asr.write_text(json.dumps({"source": {"language": data["language"], "segments": data["segments"]}, "en": None}, ensure_ascii=False, indent=1), encoding="utf-8")
    js.write_text("/* generated from a user-supplied SRT; word times are interpolated within each cue */\nwindow.EV_ASR = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    return outputs + [asr, js]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("srt", type=Path)
    parser.add_argument("out_base", type=Path)
    args = parser.parse_args()
    for path in write_outputs(args.srt, args.out_base):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
