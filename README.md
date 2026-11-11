# EVA Video Style

**Open-Source AI Video Editing | 开源 AI 自动视频剪辑**

Turn raw talking-head videos into professionally edited content with motion graphics, captions and quality checks.

将原始口播视频转换为包含专业动效、字幕和质量检测的成片。

**23 Modular Templates · AI-Powered Editing · MIT Licensed**

> **[Download EVA Video Style v1.0.0 | 下载正式版](https://github.com/RoverEva/eva-video-style/releases/tag/v1.0.0)**

## Get Started | 快速开始

| EVA Core — Required / 核心引擎（必装） | 23 Templates — Optional / 视频模板（按需安装） |
|---|---|
| **`EVA-Core.zip`** · download once / 只需下载一次 | **`TNN-1.0.0.zip`** · choose the styles you need / 按需选择 |
| ASR, AI Content Planner, Template Registry, Renderer, captions and QA | Template-owned animations, layouts, configuration and distributable assets |
| 语音识别、AI 内容规划、模板注册表、渲染、字幕与质量检测 | 每套模板独立包含视觉布局、动画、配置及可分发素材 |
| **[Download EVA-Core.zip](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/EVA-Core.zip)** | **[Browse all 23 template ZIPs](https://github.com/RoverEva/eva-video-style/releases/tag/v1.0.0)** |

**Install Core once → Download selected templates → Add a raw MP4 → AI automatic editing**

**安装一次 Core → 按需选择模板 → 输入原始 MP4 → AI 自动剪辑**

```text
Raw MP4 / optional SRT
        ↓
ASR → AI Content Planner → installed Template Registry
        ↓
Preview → Final Renderer → QA → Final MP4
```

### Automatic editing | AI 自动剪辑

Select one or more compatible installed templates. EVA Core transcribes the video (or reads an existing SRT), plans scenes against the real timeline, renders a preview and final video, then runs QA.

选择一个或多个兼容且已安装的模板。EVA Core 会识别语音（或读取已有 SRT）、根据真实时间轴规划分镜、生成预览和最终视频，并完成质量检测。

v1.0.0 supports:

- 3–30.5-second input videos; 60-second editing is not included yet
- 16:9 and 9:16 where declared by the template; T26 is 9:16 only
- automatic ASR or an existing SRT
- compatible multi-template editing
- local rendering with no Studio account, billing service or private cloud API

当前 v1.0.0 支持 3–30.5 秒视频、自动语音识别或已有字幕、兼容模板组合及本地渲染。60 秒功能尚未包含在本版本中。

## Demo Showcase | 视频效果展示

![Eva Video Style: 21 templates in 8 seconds](docs/montage.gif)

Explore the original showcase using the same AI-generated presenter. The table below contains 21 historical demo styles; labels embedded in the preserved GIF and collage may reflect earlier snapshot counts. This showcase is separate from the current 23-template modular package inventory.

使用相同的 AI 虚拟人物和口播内容，对比表格中的 21 种历史视觉效果。保留的 GIF 和拼图中可能仍显示旧版本数量；历史 Demo 展示与当前正式发布的 23 套可安装模板是两个不同范围。

- **Demo Reel / 演示合集:** English and Chinese + English MP4 files are preserved; **public hosting pending**.
- **Music Montages / 音乐合集:** 21-template and 10-template MP4 files are preserved; **public hosting pending**.

The former `v1.0.0/...mp4` URLs were removed because the official v1.0.0 Release contains ZIP and manifest assets only. No replacement URL is listed until a durable public host is verified.

原来的 `v1.0.0/...mp4` 地址并不是正式 Release 资产，因此已移除失效链接。确认长期有效的公开托管地址前，不提供未经验证的视频 URL。

[![Demo Showcase / 模板演示](docs/templates.jpg)](references/templates.md)

| ID | Historical demo / 历史演示 | Public preview / 公开预览 |
|---|---|---|
| T01 | Acid Lime Kinetic · EN + CN/EN MP4 | [Frame](references/samples/T01_a.jpg) · video hosting pending |
| T02 | Electric Blue Console · EN + CN/EN MP4 | [Frame](references/samples/T02_a.jpg) · video hosting pending |
| T03 | Dark 3D Stage · EN + CN/EN MP4 | [Frame](references/samples/T03_a.jpg) · video hosting pending |
| T04 | Paper · EN + CN/EN MP4 | [Frame](references/samples/T04_a.jpg) · video hosting pending |
| T05 | Red Sunburst · EN + CN/EN MP4 | [Frame](references/samples/T05_a.jpg) · video hosting pending |
| T06 | Brand Purple · EN + CN/EN MP4 | [Frame](references/samples/T06_a.jpg) · video hosting pending |
| T07 | Cartoon Eva · EN + CN/EN MP4 | [Frame](references/samples/T07_a.jpg) · video hosting pending |
| T09 | Showcase Wall Opener · EN + CN/EN MP4 | [Frame](references/samples/T09_a.jpg) · video hosting pending |
| T10 | HUD Keynote · EN + CN/EN MP4 | [Frame](references/samples/T10_a.jpg) · video hosting pending |
| T11 | HUD Dashboard · EN + CN/EN MP4 | [Frame](references/samples/T11_a.jpg) · video hosting pending |
| T12 | Old Newspaper · EN + CN/EN MP4 | [Frame](references/samples/T12_a.jpg) · video hosting pending |
| T13 | Tech Blue · EN + CN/EN MP4 | [Frame](references/samples/T13_a.jpg) · video hosting pending |
| T14 | Future Style · EN + CN/EN MP4 | [Frame](references/samples/T14_a.jpg) · video hosting pending |
| T15 | Learning Style · EN + CN/EN MP4 | [Frame](references/samples/T15_a.jpg) · video hosting pending |
| T16 | Comic Pop · EN + CN/EN MP4 | [Frame](references/samples/T16_a.jpg) · video hosting pending |
| T17 | Science Network · EN + CN/EN MP4 | [Frame](references/samples/T17_a.jpg) · video hosting pending |
| T19 | Footage Intro · EN + CN/EN MP4 | [Frame](references/samples/T19_a.jpg) · video hosting pending |
| T20 | Fast-Paced Social Media · EN + CN/EN MP4 | [Frame](references/samples/T20_a.jpg) · video hosting pending |
| T21 | Clean & Minimal · EN + CN/EN MP4 | [Frame](references/samples/T21_a.jpg) · video hosting pending |
| T23 | Creative Pop · EN + CN/EN MP4 | [Frame](references/samples/T23_a.jpg) · video hosting pending |
| T24 | Luxury Nude Motion · 5-second MP4 | [Frame](references/samples/T24_a.jpg) · video hosting pending |

T08 remains excluded from the showcase and v1.0.0 package set. T26 and T27 are not represented as public demos.

T08 继续排除在展示和 v1.0.0 安装包之外；T26、T27 暂不标注为已有公开 Demo。

## Available Templates | 已发布模板

All 23 templates are MIT-licensed, Free and independently installable. Download only the ZIPs you need.

23 套模板均为 MIT 开源授权，可免费独立安装并按需下载。

| ID | Template / 模板 | Supported formats | ZIP |
|---|---|---|---|
| T01 | Acid Lime Kinetic | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T01-1.0.0.zip) |
| T02 | Electric Blue Console | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T02-1.0.0.zip) |
| T03 | Dark 3D Stage | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T03-1.0.0.zip) |
| T04 | Paper | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T04-1.0.0.zip) |
| T05 | Red Sunburst | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T05-1.0.0.zip) |
| T06 | Brand Purple | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T06-1.0.0.zip) |
| T07 | Cartoon Eva | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T07-1.0.0.zip) |
| T09 | Showcase Wall Opener | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T09-1.0.0.zip) |
| T10 | HUD Keynote | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T10-1.0.0.zip) |
| T11 | HUD Dashboard | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T11-1.0.0.zip) |
| T12 | Old Newspaper | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T12-1.0.0.zip) |
| T13 | Tech Blue | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T13-1.0.0.zip) |
| T14 | Future Style | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T14-1.0.0.zip) |
| T15 | Learning Style | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T15-1.0.0.zip) |
| T16 | Comic Pop | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T16-1.0.0.zip) |
| T17 | Science Network | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T17-1.0.0.zip) |
| T19 | Footage Intro | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T19-1.0.0.zip) |
| T20 | Fast-Paced Social Media | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T20-1.0.0.zip) |
| T21 | Clean & Minimal | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T21-1.0.0.zip) |
| T23 | Creative Pop | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T23-1.0.0.zip) |
| T24 | Luxury Nude Motion | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T24-1.0.0.zip) |
| T26 | Vintage Story / 复古拼贴故事 | **9:16 only** | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T26-1.0.0.zip) |
| T27 | Video Wall Kinetic Typography | 16:9 / 9:16 | [Download](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/T27-1.0.0.zip) |

T08, T25 and T28 are excluded. T18 and T22 are retired and their IDs are not reused.

## Installation | 安装指南

**Requirements / 系统要求**

- Node.js 20+
- Python 3.10–3.13
- Chromium-compatible browser
- FFmpeg with H.264/AAC encoding and libass/subtitles support
- Template-specific dependencies where documented

Download Core, the checksum file and your selected template ZIPs. This minimal example installs T01:

先下载 Core、校验文件和所需模板 ZIP。以下最小示例安装 T01：

```sh
RELEASE_BASE="https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0"
curl -LO "$RELEASE_BASE/EVA-Core.zip"
curl -LO "$RELEASE_BASE/T01-1.0.0.zip"
curl -LO "$RELEASE_BASE/SHA256SUMS"

grep -E '  (EVA-Core.zip|T01-1.0.0.zip)$' SHA256SUMS | shasum -a 256 -c -

mkdir eva-video-style
unzip EVA-Core.zip -d eva-video-style
python3 eva-video-style/EVA-Core/tools/packages/install.py \
  --root eva-video-style install-template T01-1.0.0.zip \
  --id T01 --version 1.0.0
```

Linux users may use `sha256sum -c` instead of `shasum -a 256 -c`. Use the verified [`SHA256SUMS`](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/SHA256SUMS) and [`download-manifest.json`](https://github.com/RoverEva/eva-video-style/releases/download/v1.0.0/download-manifest.json) for selective downloads.

For virtual environments, locked `eva-asr` setup, dependencies, template removal and editing commands, follow the [complete v1.0.0 installation guide](https://github.com/RoverEva/eva-video-style/blob/v1.0.0/EVA-Core/docs/independent-core.md).

完整的虚拟环境、锁定版 ASR、依赖、模板卸载和剪辑命令，请查看 v1.0.0 安装文档。

## Architecture | 模块化架构

- **EVA Core:** shared ASR/SRT ingestion, Planner, Registry, Engine, Renderer, captions and QA.
- **Template ZIP:** one style's source, configuration, metadata, dependencies and distributable assets.
- **Registry:** discovers installed templates and rejects incompatible IDs, versions, aspect ratios or dependencies.

Core 负责公共剪辑能力；模板 ZIP 只包含单个风格；Registry 负责模板发现、版本及兼容性检查。模板不会重复打包公共引擎。

See the [Core architecture and usage guide](https://github.com/RoverEva/eva-video-style/blob/v1.0.0/EVA-Core/docs/independent-core.md) for details.

## EVA Video Studio | 在线云端版本

EVA Video Style is the open-source local editing toolkit. EVA Video Studio is a separate cloud product.

EVA Video Style 是本地开源工具；EVA Video Studio 是独立的在线云端产品。开源版本不需要 Studio 账号、支付系统或私有云服务。

## Principles | 原则

- Preserve user inputs and keep presenter framing safe.
- Plan graphics and captions against real speech timing.
- Do not invent facts, numbers or screens; label conceptual material **ILLUSTRATIVE**.
- Treat QA warnings as review items rather than silently ignoring them.

保护用户原始素材，基于真实语音时间轴进行剪辑，并对 QA 警告进行人工复核。

## License | 开源许可

**[MIT License](LICENSE) © 2026 RoverEva**

Bundled fonts and third-party components retain their respective license terms. See the [v1.0.0 third-party notices](https://github.com/RoverEva/eva-video-style/blob/v1.0.0/THIRD_PARTY_NOTICES.md).

本项目采用 MIT 开源协议；第三方字体、模型及依赖仍遵循各自许可证。
