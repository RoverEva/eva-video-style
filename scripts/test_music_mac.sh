#!/usr/bin/env bash
# test_music_mac.sh — 在 Mac 上一键实测自动配乐（MVP：3 首 Open Lo-Fi + 3 个 Kenney 音效）
#
# 流程：链接 3+3 个音乐文件 → 分析并缓存 catalog.json → 读字幕/音效时间点自动选曲 → 截取 → 音频试听
#       → 混音生成最终 MP4（画面直接复制，不重新渲染）→ 检查口播清晰度、音画同步、响度
# 用法：bash scripts/test_music_mac.sh [VIDEO] [-y]
#   VIDEO              默认：~/eva-test/runs/ 里最新的 out/eva_asr_test_EN.mp4（需要同一 run 里的 srt/ 和 sec/）
#   -y                 试听后不等待确认，直接生成最终 MP4
#   LOFI_DIR=...       Open Lo-Fi 文件夹（默认 ~/Downloads/openlofi）
#   KENNEY_DIR=...     Kenney Music Jingles 文件夹（默认 ~/Downloads/kenney_music-jingles）
#   EVA_TEST_DIR=...   测试工作目录（默认 ~/eva-test）
# 不修改仓库和原视频：所有结果写到 EVA_TEST_DIR/music-runs/<时间>/。兼容 macOS 自带的 bash 3.2。
set -uo pipefail
VIDEO=""; YES=0
for a in "$@"; do case "$a" in -y|--yes) YES=1 ;; -h|--help) sed -n 2,13p "$0" | sed 's/^# \{0,1\}//'; exit 0 ;; *) VIDEO="$a" ;; esac; done
HERE="$(cd "$(dirname "$0")" && pwd)"; EVS="$(dirname "$HERE")"
WORK="${EVA_TEST_DIR:-$HOME/eva-test}"
LOFI="${LOFI_DIR:-$HOME/Downloads/openlofi}"; KENNEY="${KENNEY_DIR:-$HOME/Downloads/kenney_music-jingles}"
MVP_LOFI="cursor-after-midnight.mp3 first-coffee-thoughts.mp3 golden-afternoon-groove.mp3"
MVP_KENNEY="Hit jingles/jingles_HIT00.ogg|Pizzicato jingles/jingles_PIZZI01.ogg|8-Bit jingles/jingles_NES01.ogg"
RUN="$WORK/music-runs/$(date +%Y%m%d-%H%M%S)"
if [ -t 1 ]; then G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'; else G=; R=; Y=; B=; N=; fi
STEP=0
step() { STEP=$((STEP + 1)); printf '\n%s[%d] %s%s\n' "$B" "$STEP" "$1" "$N"; }
ok()   { printf '  %s✅%s %s\n' "$G" "$N" "$*"; }
die()  { printf '\n%s❌ 第 %d 步失败：%s%s\n' "$R" "$STEP" "$*" "$N" >&2; printf '   测试已停止。结果目录：%s\n' "$RUN" >&2; exit 1; }

step "检查 FFmpeg、Python、numpy"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || die "没有 ffmpeg/ffprobe：brew install ffmpeg"
PY=python3; [ -x "$WORK/.venv/bin/python" ] && PY="$WORK/.venv/bin/python"
"$PY" -c "import numpy" 2>/dev/null || die "$PY 没有 numpy：$PY -m pip install numpy"
ok "$(ffmpeg -version | head -1 | cut -c1-40) · $PY"

step "找到测试视频、字幕和音效时间点"
if [ -z "$VIDEO" ]; then
  VIDEO="$(ls -t "$WORK"/runs/*/out/eva_asr_test_EN.mp4 2>/dev/null | head -1)"
  [ -n "$VIDEO" ] || die "在 $WORK/runs/*/out/ 找不到 eva_asr_test_EN.mp4，请把视频路径作为参数传入"
fi
[ -f "$VIDEO" ] || die "视频不存在：$VIDEO"
SRC_RUN="$(cd "$(dirname "$VIDEO")/.." && pwd)"
SRT="$SRC_RUN/srt/talk.en.srt"; [ -f "$SRT" ] || SRT="$(ls "$SRC_RUN"/srt/*.srt 2>/dev/null | head -1)"
[ -f "$SRT" ] || die "找不到字幕：$SRC_RUN/srt/*.srt"
CUES="$SRC_RUN/sec/all_cues.json"; CUE_ARGS=""; [ -f "$CUES" ] && CUE_ARGS="--cues $CUES"
CLEAN="$SRC_RUN/out/eva_asr_test_Clean.mp4"
ok "视频 $VIDEO"; ok "字幕 $SRT"; [ -n "$CUE_ARGS" ] && ok "音效时间点 $CUES"

step "准备 MVP 音乐库（3 首 Open Lo-Fi + 3 个 Kenney，复制到本次测试目录）"
[ -d "$LOFI" ] || die "找不到 Open Lo-Fi 文件夹：$LOFI（用 LOFI_DIR=... 指定）"
[ -d "$KENNEY" ] || die "找不到 Kenney 文件夹：$KENNEY（用 KENNEY_DIR=... 指定）"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/eva-music-stage.XXXXXX")" || die "无法创建临时目录"; trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$RUN" "$STAGE/lofi" "$STAGE/kenney" || die "无法创建 $RUN"
for f in $MVP_LOFI; do [ -f "$LOFI/$f" ] || die "缺少 $LOFI/$f"; ln -s "$LOFI/$f" "$STAGE/lofi/$f"; done
OLDIFS="$IFS"; IFS='|'
for f in $MVP_KENNEY; do
  [ -f "$KENNEY/Audio/$f" ] || die "缺少 $KENNEY/Audio/$f"
  mkdir -p "$STAGE/kenney/$(dirname "$f")"; ln -s "$KENNEY/Audio/$f" "$STAGE/kenney/$f"
done
IFS="$OLDIFS"
[ -f "$KENNEY/License.txt" ] && cp "$KENNEY/License.txt" "$STAGE/kenney/"
export EVA_MUSIC_LIBRARY="$RUN/music-library"
"$PY" "$EVS/scripts/music.py" import --copy --lofi "$STAGE/lofi" --kenney "$STAGE/kenney" || die "导入失败"

step "分析音乐（BPM、能量、高潮、可截取位置）并缓存"
"$PY" "$EVS/scripts/music.py" analyze || die "分析失败"
"$PY" "$EVS/scripts/music.py" analyze | tail -1 | grep -q "0 analysed" && ok "第二次运行全部命中缓存，没有重复分析" || die "缓存没有生效"

step "自动选曲 + 截取 + 音效方案 + 音频试听（不渲染视频）"
bash "$EVS/scripts/auto_music.sh" "$VIDEO" "$SRT" "$RUN/out" --mode auto $CUE_ARGS || die "选曲或试听失败"
ok "方案：$RUN/out/music_plan.md"; ok "试听：$RUN/out/music_preview.m4a"
command -v afplay >/dev/null && [ -t 0 ] && [ "$YES" = 0 ] && { printf '  正在播放试听…（Ctrl-C 停止）\n'; afplay "$RUN/out/music_preview.m4a" || true; }
if [ "$YES" = 0 ]; then
  printf '  确认用这个方案生成最终 MP4？[y/N] '; read -r ans </dev/tty || ans=n
  case "$ans" in y|Y|yes) ;; *) printf '  已停止。确认后运行：\n  bash %s %s %s %s --apply\n' "$EVS/scripts/auto_music.sh" "$VIDEO" "$SRT" "$RUN/out"; exit 0 ;; esac
fi

step "FFmpeg 混音，生成最终 MP4（画面流直接复制）"
bash "$EVS/scripts/auto_music.sh" "$VIDEO" "$SRT" "$RUN/out" --apply || die "最终混音失败"
cp "$RUN/out/music_check.json" "$RUN/out/music_check_EN.json"
if [ -f "$CLEAN" ]; then
  bash "$EVS/scripts/auto_music.sh" "$CLEAN" "$SRT" "$RUN/out" --apply || die "无字幕版本混音失败"
fi

step "检查结果"
"$PY" - "$RUN/out/music_check_EN.json" "$RUN/out/music_plan.json" <<'EOF' || die "检查未通过"
import json, sys
c, p = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
b = p["background"]; rows = [
 ("自动选曲", True, f"{b['file'].split('/')[-1]}（{p['category']}，{b['bpm']} BPM）"),
 ("音乐截取", b["start"] > 0 or not b["loops"], f"{b['start']:.2f}s → {b['end']:.2f}s"),
 ("背景音量 / 口播清晰度", c["speech_clear"], f"人声比音乐高 {c['speech_to_music_db']} dB（要求 ≥ 15 dB）"),
 ("淡入淡出", c["fade_in_start_gain"] < .01 and c["fade_out_end_gain"] < .01, f"首尾音乐增益 {c['fade_in_start_gain']} / {c['fade_out_end_gain']}"),
 ("无削波", c["true_peak_dbfs"] is not None and c["true_peak_dbfs"] < -1.0, f"真峰值 {c['true_peak_dbfs']} dBFS"),
 ("响度", c["lufs"] is not None and abs(c["lufs"] + 16) <= 1.5, f"{c['lufs']} LUFS（目标 -16）"),
 ("音画同步", c["sync_ok"], f"帧数 {c['frames_in']} → {c['frames_out']}，音频 {c['audio_duration_out']:.3f}s 从 {c['audio_start']:.3f}s 开始"),
 ("Kenney 音效", True, f"放置 {len(p['jingles'])} 个；未放置 {len(p['jingles_skipped'])} 个（原因见 music_plan.md）"),
 ("MP4 输出", True, c["output"])]
bad = 0
for name, good, info in rows:
    print(f"  {'✅' if good else '❌'} {name}：{info}"); bad += not good
sys.exit(1 if bad else 0)
EOF
printf '\n%s全部检查通过。%s\n  带字幕 + 配乐：%s\n' "$G" "$N" "$(ls "$RUN"/out/*_EN_Music.mp4 2>/dev/null)"
[ -f "$CLEAN" ] && printf '  无字幕 + 配乐：%s\n' "$(ls "$RUN"/out/*_Clean_Music.mp4 2>/dev/null)"
printf '  方案：%s\n  试听：%s\n' "$RUN/out/music_plan.md" "$RUN/out/music_preview.m4a"
