# MBTI · Glow Beat / MBTI 光之人格卡点

A 29-second, 16:9 music video for one MBTI type. A hero drawn in glowing line art stands in a candle-lit night, and every big moment lands on the beat: the prop falls from the sky, candles light in waves, a light beam drops, the title bursts, a light ring opens each trait section, and the crowd rises at the climax. Everything is drawn in Python (numpy + OpenCV + Pillow), with no images, no footage and no AI image generation.

一条 29 秒、16:9 的 MBTI 人格卡点短片。发光线稿人物站在烛光夜色里，所有爽点都踩在节拍上：道具从天而降、蜡烛按拍成波点亮、光束落下、标题爆闪、每个维度开场都有一圈光环，高潮时全场起立。画面全部由代码绘制，不用图片素材，也不用 AI 生图。

> **Music template.** Every other Eva Video Style template edits a talking-head video and uses no background music. This one is the exception: it is a standalone, music-driven piece with no presenter, built around a track you supply.
>
> **音乐模板。** 其他 Eva 模板都是口播剪辑、不加背景音乐；MBTI 模板是例外，它没有出镜人，由你提供的音乐驱动。

## Quick start | 快速开始

```bash
pip install numpy opencv-python pillow        # plus ffmpeg and Noto CJK fonts (fonts-noto-cjk)
mkdir -p media && cp /path/to/your_track.mp3 media/MBTI_music.mp3

# 1. check a few key moments as stills  先出几张关键帧检查
python3 template/mbti/render.py --type ENFJ --music media/MBTI_music.mp3 \
        --stills 1.1,2.8,8.1,24.4 --out out/ENFJ_check

# 2. render the video  渲染成片
python3 template/mbti/render.py --type ENFJ --music media/MBTI_music.mp3 --out out/ENFJ.mp4
```

| Option | Meaning |
|---|---|
| `--type` | any of the 16 presets in `types/` (ENFJ, INTJ, ISFP, …) |
| `--music` | your track. The beat grid is measured from it and the audio is muxed in with a 0.6 s fade-out. |
| `--grid 0.367,0.3333` | override the measured grid (`offset,eighth` in seconds) |
| `--logo brand/logo.png` | brand logo (bright artwork on black). Without one, a line-art eye is drawn. |
| `--stills t1,t2` | write JPG stills instead of a video |
| `--workers N` | parallel render processes (default: CPU count). About 0.5 s per frame per worker. |

## The 16 types | 16 型人格

The palette follows the type's group, so the four groups look like one family. The prop and the copy belong to each type. Every line can be edited in `types/XXXX.json`.

配色按人格大类区分，同组风格统一；道具和文案每型独立，可在 `types/XXXX.json` 里修改。

| Group | Palette | Types → prop |
|---|---|---|
| NF 外交家 | emerald 翡翠绿 + gold | ENFJ 主人公 sword · INFJ 提倡者 lantern · ENFP 竞选者 star · INFP 调停者 lantern |
| NT 分析家 | violet 紫 + gold | INTJ 建筑师 orb · INTP 逻辑学家 orb · ENTJ 指挥官 sword · ENTP 辩论家 star |
| SJ 守护者 | azure 蓝 + pale gold | ISTJ 物流师 sword · ISFJ 守卫者 lantern · ESTJ 总经理 sword · ESFJ 执政官 lantern |
| SP 探险家 | amber 琥珀 + white gold | ISTP 鉴赏家 orb · ISFP 探险家 star · ESTP 企业家 sword · ESFP 表演者 star |

Each trait section changes its visual with the letter:

| Section | Letter A | Letter B |
|---|---|---|
| 1 | **E**: light streaks fly in from all sides | **I**: calm rings close in, one per beat |
| 2 | **N / S**: punch-in on the face, then a beam lights small people one per beat | (same) |
| 3 | **F**: a glowing orb with orbit rings in the hand | **T**: a rotating geometric diagram in the hand |
| 4 | **J**: a flag drops in on each beat | **P**: a sky lantern rises on each beat |

### New type or new copy | 新建或改写

Copy `types/_TEMPLATE.json` to `types/XXXX.json`. Each caption slot holds `[line 1, line 2, gold word]`. Line 1 lands on the section's beat, line 2 lands one beat later, and the gold word must appear in line 2. Keep each line to about 11 characters; longer lines automatically drop to a smaller size. `PROMPTS.md` has a prompt for writing a full set of copy.

复制 `types/_TEMPLATE.json`；每个字幕位是 `[第一行, 第二行, 金色关键词]`，关键词必须出现在第二行里，每行建议不超过 11 个字。写文案的提示词见 `PROMPTS.md`。

## Music | 音乐

The track is **not** in this repository. Bring a track you have the rights to and put it in `media/` (git-ignored).

音乐文件不随仓库分发，请使用你有授权的曲子，放到 `media/`（已加入 .gitignore）。

| Spec | Value |
|---|---|
| Tempo | 90 BPM reference; anything from about 80 to 110 BPM works |
| Length | ≥ 30 s. The video is 87 eighths long: 29.4 s at 90 BPM, shorter at faster tempos. |
| Feel | cinematic, warm and uplifting, with a clear kick on every beat |
| Structure | soft intro (0–2.5 s) → a hit at about 2.7 s (the beam) → build → lift at about 8 s (the title) → steady groove → build at 21–23 s → biggest hit at about 24 s (the climax) → outro |

`engine/beats.py` measures the eighth-note grid (`offset + n × eighth`) from the track, and all 87 beat positions follow it, so a different track still lines up. The generation prompt for an AI music tool is in `PROMPTS.md`.

## Beat map | 卡点表

T(n) = offset + n × eighth. At 90 BPM, T(n) = 0.367 + n/3 s.

| Beat | Time @90 | Moment |
|---|---|---|
| T(0) | 0.37 | star; line 1 「有一种人」 |
| T(2) | 1.03 | **prop lands**: gold ground ring flash, ripples, micro-shake |
| T(3) T(5) T(6) | 1.4 / 2.0 / 2.4 | single candles pop, one per beat |
| **T(7)** | 2.70 | **light beam falls** on the prop head; first candle wave |
| T(8) T(9) | 3.0 / 3.4 | candle waves 2 and 3 cover the ground |
| T(10) | 3.70 | 36 rays fan from the prop head; camera pushes low |
| T(13)→T(21) | 4.7–7.4 | hero grows from the hands up, with glowing tip dots; camera tilts up, then pulls back |
| **T(23)** | 8.03 | **title burst**: chest star flare, ring, mandorla of flames, type code and name |
| T(31) T(35) | 10.7 / 12.0 | section 1 (E/I), with light rings |
| T(38) | 13.0 | section 2 (N/S): punch-in on the face; T(42)–T(45) beam, then people one per beat |
| T(47) | 16.0 | section 3 (F/T): object in the hand |
| T(55)–T(61) | 18.7–20.7 | section 4 (J/P): flags or lanterns, one per beat |
| T(65) T(67) T(69) | 22.0 / 22.7 / 23.4 | prop lights up → cloak spreads → shards burst |
| **T(71) T(72)** | 24.0 / 24.4 | **raise**: sword arc or staff lift, sky beam, the crowd rises in three waves |
| T(77) T(78) | 26.0 / 26.4 | 「他就是」 + type name |
| T(81)→end | 27.4–29.4 | logo, brand line, fade |

Every quarter beat also brightens the frame for 1 frame and bumps the camera 1.2 %, which keeps the rhythm going between the big hits.

## Files

```
template/mbti/
  render.py            CLI: stills or video, parallel render, music mux
  brand.json           brand line + logo path (default 洞悉 / INSIGHT, brand/logo.png if present)
  types/XXXX.json      16 presets + _TEMPLATE.json
  engine/core.py       canvas (crisp + glow layers), splines, flames, palettes, text
  engine/scene.py      the scene: timeline in beats, camera, hero, props, all effects
  engine/beats.py      beat-grid detector (python3 -m engine.beats track.mp3)
  PROMPTS.md           music prompt, copywriting prompt, Claude prompts
```
