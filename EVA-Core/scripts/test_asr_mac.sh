#!/usr/bin/env bash
# test_asr_mac.sh — 在 macOS Apple Silicon 上一键实测 eva-asr + eva-video-style
#
# 流程：真实视频 → eva-asr 真实语音识别（自动判断中文/英文）→ SRT → 字幕 → 现有模板渲染 → 带字幕 MP4 → 同步检查
# 用法：bash test_asr_mac.sh /path/to/video.mp4 [-y]
#   -y                  安装依赖时不再逐项询问（默认会先列出要安装的内容并询问）
#   EVA_TEST_DIR=...    工作目录（默认 ~/eva-test）
#   EVA_ASR_MODEL=...   Whisper 模型（默认 small）
#
# 运行设置：Whisper small · CPU · int8。不使用 MPS：eva-asr 的转写用 faster-whisper（CTranslate2，
# 只有 CPU/CUDA 后端），scripts/asr.py 让转写、对齐、VAD 共用同一设备，所以全部走 CPU。
# 脚本不修改两个仓库的任何文件：每次测试都在 EVA_TEST_DIR/runs/<时间>/ 下新建工程，模板只复制不改。
# 兼容 macOS 自带的 bash 3.2。

set -uo pipefail

usage() { sed -n 2,12p "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
VIDEO=""; YES=0
for a in "$@"; do
  case "$a" in
    -y|--yes) YES=1 ;;
    -h|--help) usage 0 ;;
    -*) echo "未知参数：$a"; usage 2 ;;
    *) VIDEO="$a" ;;
  esac
done
[ -n "$VIDEO" ] || { echo "请给出视频路径，例如：bash test_asr_mac.sh ~/Downloads/eva_model02template.mp4"; exit 2; }

WORK="${EVA_TEST_DIR:-$HOME/eva-test}"
MODEL="${EVA_ASR_MODEL:-small}"
DEVICE=cpu
COMPUTE=int8
ASR_URL=https://github.com/RoverEva/eva-asr
ASR_BRANCH=main
EVS_URL=https://github.com/RoverEva/eva-video-style
EVS_BRANCH=feat/eva-asr-integration
ASR="$WORK/eva-asr"; EVS="$WORK/eva-video-style"; VENV="$WORK/.venv"
TS=$(date +%Y%m%d-%H%M%S); RUN="$WORK/runs/$TS"; LOGDIR="$RUN/logs"
T_START=$(date +%s)

if [ -t 1 ]; then G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'; else G=; R=; Y=; B=; N=; fi
STEP=0; CUR_LOG=""
step() { STEP=$((STEP + 1)); CUR_LOG=""; printf '\n%s[%d] %s%s\n' "$B" "$STEP" "$1" "$N"; }
ok()   { printf '  %s✅ 成功%s %s\n' "$G" "$N" "$*"; }
info() { printf '  %s\n' "$*"; }
warn() { printf '  %s⚠️  %s%s\n' "$Y" "$*" "$N"; }
die() {
  printf '\n%s❌ 第 %d 步失败：%s%s\n' "$R" "$STEP" "$1" "$N" >&2; shift
  for l in "$@"; do printf '   %s\n' "$l" >&2; done
  if [ -n "$CUR_LOG" ] && [ -s "$CUR_LOG" ]; then
    printf '   —— 日志最后 25 行（完整日志：%s）——\n' "$CUR_LOG" >&2
    tail -n 25 "$CUR_LOG" | sed 's/^/   | /' >&2
  fi
  printf '   测试已停止，没有继续后面的步骤。\n' >&2
  exit 1
}
ask() {
  [ "$YES" = 1 ] && return 0
  printf '  %s [y/N] ' "$1"
  local ans; read -r ans </dev/tty || return 1
  case "$ans" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac
}
# run NAME CMD...  静默运行，输出写入日志；返回命令的退出码
run() { local name="$1"; shift; CUR_LOG="$LOGDIR/$(printf %02d "$STEP")_$name.log"; "$@" >"$CUR_LOG" 2>&1; }
# live NAME CMD... 同时显示在屏幕上（安装、识别等耗时步骤）
live() { local name="$1"; shift; CUR_LOG="$LOGDIR/$(printf %02d "$STEP")_$name.log"; "$@" 2>&1 | tee "$CUR_LOG"; return "${PIPESTATUS[0]}"; }

printf '%seva-asr × eva-video-style · Mac 实测%s\n工作目录：%s\n本次结果：%s\n' "$B" "$N" "$WORK" "$RUN"
mkdir -p "$LOGDIR" "$RUN/raw" "$RUN/srt" "$RUN/sec" "$RUN/out" || { echo "无法创建 $RUN"; exit 1; }

# ─────────────────────────────────────────────────────────────────────────────
step "检查 Mac 芯片与系统"
[ "$(uname -s)" = Darwin ] || die "此脚本只用于 macOS，当前系统是 $(uname -s)"
if [ "$(sysctl -n sysctl.proc_translated 2>/dev/null || echo 0)" = 1 ]; then
  die "终端正在 Rosetta（Intel 转译）下运行" "请在 Finder 里选中“终端”→ 显示简介 → 取消“使用 Rosetta 打开”，然后重新运行"
fi
ARCH=$(uname -m)
[ "$ARCH" = arm64 ] || die "需要 Apple Silicon（arm64），当前是 $ARCH" "eva-asr 依赖的 torch 2.8 没有 Intel Mac 安装包"
CHIP=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Apple Silicon")
MACOS=$(sw_vers -productVersion); MAJOR=${MACOS%%.*}
[ "$MAJOR" -ge 13 ] || die "需要 macOS 13 或更高版本，当前是 $MACOS" "eva-asr 的依赖 av / onnxruntime 只提供 macOS 13+ 的 arm64 安装包"
MEM_GB=$(( $(sysctl -n hw.memsize) / 1073741824 ))
mkdir -p "$WORK"; FREE_GB=$(df -g "$WORK" | awk 'NR==2 {print $4}')
[ "$FREE_GB" -ge 8 ] || die "磁盘剩余 ${FREE_GB} GB，至少需要 8 GB（Python 依赖约 3 GB，模型约 0.5–1.5 GB）"
ok "$CHIP · macOS $MACOS · 内存 ${MEM_GB} GB · 可用磁盘 ${FREE_GB} GB"

[ -f "$VIDEO" ] || die "找不到视频文件：$VIDEO"
VIDEO_ABS="$(cd "$(dirname "$VIDEO")" && pwd)/$(basename "$VIDEO")"
EXT="${VIDEO_ABS##*.}"; [ "$EXT" != "$VIDEO_ABS" ] || EXT=mp4

# ─────────────────────────────────────────────────────────────────────────────
step "检查 Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
if ! command -v brew >/dev/null 2>&1; then
  info "没有找到 Homebrew（用来安装 ffmpeg、Node、Python）。"
  info "将运行 brew.sh 官方安装脚本，期间会要求输入 Mac 登录密码。"
  ask "现在安装 Homebrew？" || die "未安装 Homebrew，无法继续" "也可以先按 https://brew.sh 手动安装，再重新运行本脚本"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || die "Homebrew 安装失败" "请按 https://brew.sh 手动安装后重试"
  eval "$(/opt/homebrew/bin/brew shellenv)" || die "Homebrew 已安装但无法加载 /opt/homebrew/bin/brew"
fi
BREW_PREFIX=$(brew --prefix)
ok "Homebrew $(brew --version | head -1 | awk '{print $2}')（$BREW_PREFIX）"

# ─────────────────────────────────────────────────────────────────────────────
step "检查 git、ffmpeg、Node.js、Python（eva-asr 要求 Python 3.10–3.13）"
PKGS=""
command -v git >/dev/null 2>&1 && git --version >/dev/null 2>&1 || PKGS="$PKGS git"
command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1 || PKGS="$PKGS ffmpeg"
NODE_OK=0
if command -v node >/dev/null 2>&1; then
  [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ] 2>/dev/null && NODE_OK=1
fi
[ "$NODE_OK" = 1 ] || PKGS="$PKGS node"
find_python() {
  local c v
  for c in python3.12 python3.13 python3.11 python3.10 \
           "$BREW_PREFIX/bin/python3.12" "$BREW_PREFIX/bin/python3.13" "$BREW_PREFIX/bin/python3.11" "$BREW_PREFIX/bin/python3.10" python3; do
    command -v "$c" >/dev/null 2>&1 || continue
    v=$("$c" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null) || continue
    case "$v" in 3.10|3.11|3.12|3.13) "$c" -c 'import venv, ensurepip' 2>/dev/null && { command -v "$c"; return 0; } ;; esac
  done
  return 1
}
PY=$(find_python) || PKGS="$PKGS python@3.12"
if [ -n "$PKGS" ]; then
  info "需要用 Homebrew 安装：$PKGS"
  ask "现在安装？" || die "缺少依赖：$PKGS" "可手动运行：brew install$PKGS"
  CUR_LOG="$LOGDIR/0${STEP}_brew_install.log"
  # shellcheck disable=SC2086
  brew install $PKGS 2>&1 | tee "$CUR_LOG"; [ "${PIPESTATUS[0]}" = 0 ] || die "brew install$PKGS 失败"
  hash -r
  PY=$(find_python) || die "安装后仍找不到可用的 Python 3.10–3.13"
fi
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ] || die "Node.js 版本过低（$(node -v)），需要 18+" "运行 brew upgrade node 后重试"

# eva-video-style 的 assemble.sh 需要 libx264 编码器和 ass 字幕滤镜（libass）
ff_ok() {   # 先取完整输出再匹配：在 pipefail 下 `ffmpeg | grep -q` 会因 SIGPIPE 误判失败
  local enc flt; enc=$(ffmpeg -hide_banner -encoders 2>/dev/null); flt=$(ffmpeg -hide_banner -filters 2>/dev/null)
  printf '%s\n' "$enc" | grep -q libx264 && printf '%s\n' "$flt" | grep -Eq '[[:space:]]ass[[:space:]]+V->V'
}
if ! ff_ok; then
  info "当前 ffmpeg（$(command -v ffmpeg)）缺少 libx264 或 libass（烧录字幕要用）。"
  if brew info --formula ffmpeg-full >/dev/null 2>&1; then
    ask "安装 Homebrew 的 ffmpeg-full（包含 libass）？" || die "ffmpeg 不支持字幕烧录" "可手动运行：brew install ffmpeg-full"
    CUR_LOG="$LOGDIR/0${STEP}_ffmpeg_full.log"
    brew install ffmpeg-full 2>&1 | tee "$CUR_LOG"; [ "${PIPESTATUS[0]}" = 0 ] || die "安装 ffmpeg-full 失败"
    export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"; hash -r
    ff_ok || die "ffmpeg-full 仍缺少 libx264 或 ass 滤镜"
  else
    die "ffmpeg 不支持 libx264 或 ass 字幕滤镜，且 Homebrew 中没有 ffmpeg-full" "请安装一个带 --enable-libass --enable-libx264 的 ffmpeg 后重试"
  fi
fi
command -v realpath >/dev/null 2>&1 || die "缺少 realpath 命令（assemble.sh 需要）" "运行 brew install coreutils 后重试"
ok "git $(git --version | awk '{print $3}') · $(ffmpeg -version | head -1 | awk '{print $1, $3}') · node $(node -v) · $("$PY" --version)（$PY）"

# ─────────────────────────────────────────────────────────────────────────────
step "下载并切换到正确分支：eva-asr@$ASR_BRANCH，eva-video-style@$EVS_BRANCH"
update_repo() {
  git -C "$1" fetch origin "$2" || return 1
  git -C "$1" checkout -q "$2" 2>/dev/null || git -C "$1" checkout -q -b "$2" "origin/$2" || return 1
  git -C "$1" merge --ff-only "origin/$2"
}
get_repo() {
  local dir="$1" url="$2" br="$3"
  if [ -d "$dir/.git" ]; then
    [ -z "$(git -C "$dir" status --porcelain)" ] || die "$dir 有未提交的修改，为避免覆盖已停止" "请先提交或备份这些修改（或设置 EVA_TEST_DIR 换一个目录）"
    run "git_$(basename "$dir")" update_repo "$dir" "$br" \
      || die "更新 $dir 失败（检查网络是否能访问 github.com）"
  elif [ -e "$dir" ]; then
    die "$dir 已存在但不是 git 仓库" "请移走它，或设置 EVA_TEST_DIR 换一个目录"
  else
    run "git_$(basename "$dir")" git clone -b "$br" "$url" "$dir" || die "下载 $url 失败（检查网络是否能访问 github.com）"
  fi
}
get_repo "$ASR" "$ASR_URL" "$ASR_BRANCH"
get_repo "$EVS" "$EVS_URL" "$EVS_BRANCH"
[ -f "$ASR/whisperx/asr.py" ] || die "$ASR 不是 eva-asr 仓库（缺少 whisperx/asr.py）"
for f in scripts/asr.py scripts/captions.py scripts/render.mjs scripts/assemble.sh engine/asr.js template/section/scenes.js; do
  [ -f "$EVS/$f" ] || die "$EVS 缺少 $f，分支不对？"
done
ok "eva-asr $(git -C "$ASR" rev-parse --short HEAD) · eva-video-style $(git -C "$EVS" rev-parse --short HEAD)（两个仓库都保持原样）"

# ─────────────────────────────────────────────────────────────────────────────
step "安装 eva-asr 的 Python 环境（torch 2.8、faster-whisper、pyannote…，首次约 3 GB）"
if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)' 2>/dev/null; then
  info "复用已有虚拟环境 $VENV"
else
  rm -rf "$VENV"
  run venv "$PY" -m venv "$VENV" || die "创建虚拟环境失败"
fi
PYV="$VENV/bin/python"
if ! "$PYV" -c 'import whisperx.asr' >/dev/null 2>&1; then
  info "将执行：pip install -e $ASR（依赖版本由 eva-asr 的 pyproject.toml 决定）"
  ask "现在安装 eva-asr 及其依赖？" || die "未安装 eva-asr 依赖"
  live pip_upgrade "$PYV" -m pip install --upgrade pip || die "升级 pip 失败（检查网络是否能访问 pypi.org）"
  live pip_eva_asr "$PYV" -m pip install -e "$ASR" || die "pip install -e eva-asr 失败" "常见原因：无法访问 pypi.org / files.pythonhosted.org，或 Python 版本不在 3.10–3.13"
else
  info "eva-asr 已安装，跳过"
fi
ok "eva-asr 已安装到 $VENV"

# ─────────────────────────────────────────────────────────────────────────────
step "检测可用的模型运行方式（CPU / int8 / MPS）"
smoke_fail() {
  if grep -qi torchcodec "$CUR_LOG" 2>/dev/null; then
    die "eva-asr 组件导入失败（与 torchcodec 有关）" "torchcodec 0.7 需要 FFmpeg 4–7 的动态库；若本机 Homebrew ffmpeg 更新，可尝试：" \
        "brew install ffmpeg@7 && export DYLD_FALLBACK_LIBRARY_PATH=\"\$(brew --prefix ffmpeg@7)/lib\"，然后重新运行"
  fi
  die "eva-asr 组件导入失败，依赖不完整或不兼容"
}
run smoke "$PYV" - <<'PY' || smoke_fail
import importlib, sys, warnings
warnings.simplefilter("always")
import torch, ctranslate2, faster_whisper
print("python", sys.version.split()[0])
print("torch", torch.__version__, "| MPS 可用:", torch.backends.mps.is_available())
ct = sorted(ctranslate2.get_supported_compute_types("cpu"))
print("ctranslate2", ctranslate2.__version__, "| CPU 计算类型:", ", ".join(ct), "| CUDA 设备数:", ctranslate2.get_cuda_device_count())
print("faster-whisper", faster_whisper.__version__)
if "int8" not in ct:
    sys.exit("CTranslate2 在本机 CPU 上不支持 int8")
for m in ("whisperx.asr", "whisperx.alignment", "whisperx.vads.pyannote", "whisperx.utils"):
    importlib.import_module(m); print("import ok:", m)
PY
sed 's/^/  /' "$CUR_LOG" | grep -Ev '^  *$' | grep -v -i warn | head -12
info "→ Whisper 用 CTranslate2，只有 CPU/CUDA 后端（无 MPS）；asr.py 让对齐和 VAD 使用同一设备，所以统一走 CPU。"
run nltk "$PYV" -c 'import nltk, sys; sys.exit(0 if nltk.download("punkt_tab", quiet=True) else 1)' \
  || die "下载 nltk punkt_tab 失败（eva-asr 的对齐需要它）" "检查网络能否访问 raw.githubusercontent.com"
ok "运行方式：device=$DEVICE · compute_type=$COMPUTE · model=$MODEL"

# ─────────────────────────────────────────────────────────────────────────────
step "安装 eva-video-style 的渲染依赖（Playwright + Chromium）"
npm_install() { (cd "$EVS" && npm install --no-audit --no-fund); }
pw_install() { (cd "$EVS" && npx playwright install chromium); }
if [ ! -d "$EVS/node_modules/playwright" ]; then
  run npm_install npm_install || die "npm install 失败（检查网络能否访问 registry.npmjs.org）"
fi
run pw_install pw_install || die "下载 Chromium 失败（npx playwright install chromium）"
ok "playwright $("$PYV" -c 'import json, sys; print(json.load(open(sys.argv[1]))["version"])' "$EVS/node_modules/playwright/package.json")"

# ─────────────────────────────────────────────────────────────────────────────
step "读取你的视频"
PROBE=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO_ABS" 2>&1) || die "ffprobe 无法读取 $VIDEO_ABS" "$PROBE"
AUD=$(ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 "$VIDEO_ABS")
[ -n "$AUD" ] || die "视频没有音轨，无法做语音识别"
VID=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$VIDEO_ABS")
[ -n "$VID" ] || die "文件里没有视频流"
cp "$VIDEO_ABS" "$RUN/raw/talk.$EXT" || die "复制视频到 $RUN/raw 失败"
ok "$(basename "$VIDEO_ABS") · 时长 ${PROBE}s · 视频 $VID · 音频 $AUD（已复制，原文件不动）"

# ─────────────────────────────────────────────────────────────────────────────
step "eva-asr 真实语音识别（自动判断中文/英文；首次会下载 Whisper $MODEL 和对齐模型）"
cat >"$RUN/srt/asr.json" <<EOF
{"eva_asr_path": "$ASR", "model": "$MODEL", "device": "$DEVICE", "compute_type": "$COMPUTE",
 "language": null, "translate_to_en": true, "align": true}
EOF
cd "$RUN" || die "无法进入 $RUN"
live asr "$PYV" "$EVS/scripts/asr.py" "raw/talk.$EXT" srt/talk --config srt/asr.json
RC=$?
case $RC in
  0) ;;
  3) die "eva-asr 或其依赖不可用（asr.py 退出码 3）" ;;
  4) die "模型加载或识别失败（asr.py 退出码 4）" "首次运行需要从 huggingface.co 下载模型；请检查网络或代理" ;;
  5) die "没有识别到语音（asr.py 退出码 5）" "确认视频有人声，或调整 vad_onset" ;;
  *) die "asr.py 退出码 $RC" ;;
esac
LANG_ID=$("$PYV" -c 'import json; print(json.load(open("srt/talk.asr.json", encoding="utf-8"))["source"]["language"])') \
  || die "无法从 srt/talk.asr.json 读取识别语言"
case "$LANG_ID" in
  zh) LANG_NAME="中文"; CAPBASE="out/eva_asr_test_CN-EN"; echo '{}' >srt/captions.json ;;
  en) LANG_NAME="英文"; CAPBASE="out/eva_asr_test_EN"; echo '{"mode": "en"}' >srt/captions.json ;;
  *) die "检测到的口播语言是 '$LANG_ID'，本测试只支持中文或英文" "识别结果已保存在 $RUN/srt/，可以查看" ;;
esac
SRC_SRT="$RUN/srt/talk.$LANG_ID.srt"
[ -s "$SRC_SRT" ] || die "识别完成但 $SRC_SRT 为空"
NCUE=$(grep -c -- '-->' "$SRC_SRT")
NWORD=$("$PYV" -c 'import json; d=json.load(open("srt/talk.asr.json", encoding="utf-8")); print(sum(1 for w in d["source"].get("word_segments", []) if "start" in w))')
ok "识别语言：$LANG_NAME（$LANG_ID）· $NCUE 条字幕 · $NWORD 个带时间戳的词"
printf '  —— %s ——\n' "$SRC_SRT"; sed 's/^/  | /' "$SRC_SRT"

# ─────────────────────────────────────────────────────────────────────────────
step "把识别出的 SRT 导入 eva-video-style 的字幕流程（captions.py）"
run captions "$PYV" "$EVS/scripts/captions.py" srt/talk.bilingual.srt 0 99999 "$CAPBASE" srt/captions.json || die "captions.py 失败"
NCAP=$(awk '{print $(NF-1)}' "$CUR_LOG" | tail -1)
[ "${NCAP:-0}" -gt 0 ] 2>/dev/null || die "captions.py 生成了 0 条字幕"
ok "$NCAP 条字幕 → $CAPBASE.srt / .ass（$([ "$LANG_ID" = zh ] && echo '中文在上、英文翻译在下' || echo '英文单行')）"

# ─────────────────────────────────────────────────────────────────────────────
step "准备剪辑工程：抽帧 + 套用现有模板 template/section（只改复制出来的副本）"
cp -R "$EVS/engine" engine && ln -s "$EVS/node_modules" node_modules || die "复制 engine 失败"
run frames "$EVS/scripts/extract_frames.sh" "raw/talk.$EXT" media/eva || die "抽帧失败"
cp -R "$EVS/template/section" s1 || die "复制模板失败"
CUR_LOG="$LOGDIR/$(printf %02d "$STEP")_section.log"
"$PYV" - >"$CUR_LOG" 2>&1 <<'PY'
import os, sys
n = len([f for f in os.listdir("media/eva") if f.startswith("f_")])
h = open("s1/index.html", encoding="utf-8").read()
s = open("s1/scenes.js", encoding="utf-8").read()
if "../../engine/" not in h or "C.end = 6;" not in s or "'../../media/eva'" not in s:
    sys.exit("template/section 的内容与预期不符")
open("s1/index.html", "w", encoding="utf-8").write(h.replace("../../engine/", "../engine/"))
open("s1/scenes.js", "w", encoding="utf-8").write(s.replace("'../../media/eva'", "'../media/eva'").replace("C.end = 6;", "C.end = %d / 30;" % n))
print(n)
PY
[ $? = 0 ] || die "设置模板副本失败"
FRAMES=$(tail -1 "$CUR_LOG")
SECS=$("$PYV" -c "print(round($FRAMES / 30, 4))")
ok "$FRAMES 帧（30 fps，${SECS}s）· 工程在 $RUN"

# ─────────────────────────────────────────────────────────────────────────────
step "渲染画面（Playwright）和音效"
info "正在逐帧渲染，约需 1–3 分钟…"
run render node "$EVS/scripts/render.mjs" s1/index.html --out sec/s1.mp4 || die "render.mjs 渲染失败"
GOT=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 sec/s1.mp4)
[ "$GOT" = "$FRAMES" ] || die "渲染帧数 $GOT 与预期 $FRAMES 不一致"
run cues node "$EVS/scripts/render.mjs" s1/index.html --cues sec/s1_cues.json || die "导出音效时间点失败"
run merge "$PYV" "$EVS/scripts/merge_cues.py" sec/all_cues.json sec/s1_cues.json:0 || die "merge_cues.py 失败"
run sfx "$PYV" "$EVS/scripts/sfx.py" sec/all_cues.json "$SECS" sec/sfx.wav || die "sfx.py 失败"
ok "sec/s1.mp4（$GOT 帧）· sec/sfx.wav"

# ─────────────────────────────────────────────────────────────────────────────
step "合成带字幕的 MP4（assemble.sh：原声 + 音效，-16 LUFS，烧录字幕）"
run assemble env FONTSDIR="$EVS/engine/fonts" "$EVS/scripts/assemble.sh" "raw/talk.$EXT" sec/sfx.wav "$CAPBASE.ass" out/eva_asr_test sec/s1.mp4 \
  || die "assemble.sh 失败"
FINAL="$RUN/out/eva_asr_test_CN-EN.mp4"
if [ "$LANG_ID" = en ]; then cp "$FINAL" "$RUN/out/eva_asr_test_EN.mp4" && FINAL="$RUN/out/eva_asr_test_EN.mp4"; fi
run decode ffmpeg -v error -i "$FINAL" -f null - || die "成片解码出错"
[ -s "$CUR_LOG" ] && die "成片解码有错误输出"
LUFS=$(grep -E 'I:' "$LOGDIR/$(printf %02d "$STEP")_assemble.log" | tail -1 | awk '{print $2, $3}')
ok "$(basename "$FINAL") · 响度 ${LUFS:-?} · 解码无错误"
info "（assemble.sh 打印的“source”帧数按原视频帧率统计；原视频若是 60 fps，会是成片帧数的两倍，属正常）"

# ─────────────────────────────────────────────────────────────────────────────
step "检查字幕与口播是否同步"
mkdir -p out/check
run sync "$PYV" - "raw/talk.$EXT" "$CAPBASE.srt" "$FINAL" out/check <<'PY'
import re, subprocess, sys
import numpy as np
raw, capsrt, final, outdir = sys.argv[1:5]
def ts(s):
    h, m, r = s.strip().split(":"); sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
cues = []
for b in re.split(r"\n\s*\n", open(capsrt, encoding="utf-8").read().strip()):
    L = b.strip().splitlines()
    if len(L) >= 3 and "-->" in L[1]:
        a, z = [ts(x) for x in L[1].split("-->")]; cues.append((a, z, " / ".join(L[2:])))
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
hop = 320; n = len(x) // hop                                   # 20 ms frames
db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
thr = max(np.percentile(db, 10) + 15, np.percentile(db, 95) - 30, -50)
sp = db > thr; t = (np.arange(n) + .5) * hop / 16000
inside = np.zeros(n, bool)
for a, z, _ in cues: inside |= (t >= a) & (t < z)
cov = (sp & inside).sum() / max(sp.sum(), 1)
print("SYNC_COVERAGE %.3f" % cov)
bad = 0
for i, (a, z, txt) in enumerate(cues, 1):
    m = (t >= a) & (t < z); ratio = sp[m].mean() if m.any() else 0
    near = np.where(sp & (t >= a - 1) & (t <= z))[0]
    off = t[near[0]] - a if len(near) else float("nan")
    flag = "" if ratio >= .3 and (np.isnan(off) or abs(off) <= .4) else "  <-- 请重点看"
    bad += bool(flag)
    print("%2d  %6.2f–%6.2fs  有声 %3d%%  语音起点偏移 %+.2fs  %s%s" % (i, a, z, ratio * 100, off, txt, flag))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % ((a + z) / 2), "-i", final, "-frames:v", "1",
                    "-vf", "scale=960:-2", "%s/cue_%02d.jpg" % (outdir, i)], check=True)
print("SYNC_BAD %d" % bad)
PY
[ $? = 0 ] || die "同步检查脚本出错"
grep -v '^SYNC_' "$CUR_LOG" | sed 's/^/  /'
COV=$(awk '/^SYNC_COVERAGE/ {print $2}' "$CUR_LOG"); BAD=$(awk '/^SYNC_BAD/ {print $2}' "$CUR_LOG")
COVP=$("$PYV" -c "print(round($COV * 100))")
if "$PYV" -c "import sys; sys.exit(0 if $COV >= .85 and $BAD == 0 else 1)"; then
  ok "有声片段的 ${COVP}% 落在字幕显示时段内，每条字幕的起点都对得上语音"; SYNC_NOTE=""
else
  SYNC_NOTE="，但同步检查有提醒，请播放成片确认"
  warn "自动检查未完全通过：有声片段字幕覆盖率 ${COVP}%，${BAD} 条字幕需要重点看（基于音量的估算，请播放成片确认）"
fi
info "每条字幕中间时刻的截图：$RUN/out/check/"

# ─────────────────────────────────────────────────────────────────────────────
ELAPSED=$(( $(date +%s) - T_START ))
printf '\n%s✅ 全部完成%s（用时 %d 分 %d 秒%s）\n' "$G" "$N" $((ELAPSED / 60)) $((ELAPSED % 60)) "$SYNC_NOTE"
printf '  识别语言：%s · 模型：Whisper %s · %s · %s\n' "$LANG_NAME" "$MODEL" "$DEVICE" "$COMPUTE"
printf '  eva-asr 识别出的 SRT：  %s\n' "$SRC_SRT"
[ "$LANG_ID" = zh ] && printf '  eva-asr 英文翻译 SRT：  %s\n' "$RUN/srt/talk.en.srt"
printf '  导入剪辑流程的字幕：    %s\n' "$RUN/$CAPBASE.srt"
printf '  带字幕的测试 MP4：      %s\n' "$FINAL"
printf '  无字幕版本：            %s\n' "$RUN/out/eva_asr_test_Clean.mp4"
printf '  完整日志：              %s\n' "$LOGDIR"
printf '\n  播放成片：open "%s"\n' "$FINAL"
