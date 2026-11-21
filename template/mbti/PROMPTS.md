# MBTI template — prompts | 提示词

## 1. Music prompt | 音乐生成提示词

For an AI music tool (Suno, Udio, Stable Audio and similar). Generate an instrumental, then pick the take whose big hits fall closest to 2.7 s, 8 s and 24 s.

用于 AI 音乐工具（Suno、Udio、Stable Audio 等）。生成纯音乐后，挑一条大鼓点最接近 2.7 秒、8 秒、24 秒的版本。

**English**

```
Instrumental, 90 BPM, 4/4, 30 seconds. Cinematic emotional pop with a warm, uplifting, heroic mood.
0-2.5s: soft intro, airy pad and twinkling bell / music-box notes, no drums.
2.7s: first big impact (deep boom + cymbal swell), then a kick drum on every beat.
2.7-8s: building groove, plucked synth arpeggio, rising strings.
8s: lift, full drums, bright piano chords, wide strings.
8-21s: steady driving groove with a clear kick on every beat and claps on 2 and 4, light percussion ticks on eighth notes.
21-23.5s: build-up, snare roll and riser.
24s: biggest hit of the track (huge impact + choir "ah" + cymbal), full arrangement.
24-27s: triumphant peak. 27-30s: gentle outro with ringing bells, quick fade.
No vocals with lyrics. Clean mix, punchy low end, strong transients on every beat.
```

**中文**

```
纯音乐，90 BPM，4/4 拍，30 秒。电影感情绪流行，温暖、向上、带英雄感。
0–2.5 秒：轻柔前奏，空气感铺底 + 闪烁的铃音/八音盒，没有鼓。
2.7 秒：第一个大重音（低频轰鸣 + 镲片），之后每拍一个底鼓。
2.7–8 秒：渐强，拨弦合成器琶音 + 弦乐上行。
8 秒：段落抬升，鼓组全开，明亮钢琴和弦，宽广弦乐。
8–21 秒：稳定律动，每拍清晰底鼓，2、4 拍拍手，八分音符轻打击。
21–23.5 秒：铺垫，军鼓滚奏 + 上升音效。
24 秒：全曲最大重音（巨大冲击 + 合唱“啊” + 镲），配器全开。
24–27 秒：高潮。27–30 秒：铃音余韵收尾，快速淡出。
不要带歌词的人声。混音干净，低频有力，每拍瞬态清晰。
```

Check the result before rendering: `python3 -m engine.beats media/MBTI_music.mp3` (run inside `template/mbti/`) should report the tempo you asked for.

## 2. Copywriting prompt | 文案提示词

Fill in the type, then paste the output into `types/XXXX.json`.

```
你是短视频文案写手。请为 MBTI 类型 {CODE}（{中文名}）写一组卡点视频文案，用于“发光线稿人物 + 音乐卡点”的 29 秒视频。
要求：
- 统一用“他”，语气温暖、有力量，像在夸一个你很珍惜的人；不要贬低任何类型，不要用“最”“唯一”这类绝对词。
- 共 10 组，每组两行：第一行铺垫，第二行反转或点题；每行不超过 11 个字。
- 每组给出第二行里的一个“金色关键词”（必须是第二行里原样出现的连续文字）。
- 顺序和含义：
  open   有一种人……（第一行固定“有一种人”）
  light  黑暗/困境中他带来光
  speak  他的一句话/一个动作带来的改变
  title  他不……却……（标题出现时的点题句）
  s1     第一个字母（E 外向 / I 内向）的表现
  s2     第二个字母（N 直觉 / S 实感）的表现
  s3     第三个字母（F 情感 / T 思考）的表现
  s4     第四个字母（J 判断 / P 感知）的表现
  low    当所有人……的时候，他……（低谷转折）
  climax 他不是……只是……（高潮，最戳心的一句）
- 输出 JSON：{"open":["第一行","第二行","金色关键词"], ... "climax":[...]}
```

## 3. Prompts for Claude | 让 Claude 直接出片

With this repository attached, ask Claude in plain words:

```
用 MBTI 模板做一个 INTJ 的视频，音乐用 media/MBTI_music.mp3，先给我 6 张关键帧，再出成片。
```
```
用 MBTI 模板把 16 个类型都渲染一遍，每个类型出 4 张关键帧拼成一张总览图。
```
```
新建一个 ISFJ 的版本：文案换成下面这组（……），道具用 lantern，配色用 azure。
```
```
换一首音乐 media/new_track.mp3，先测一下节拍，告诉我大鼓点和模板卡点差多少，再渲染 ENFP。
```

Claude should:
1. measure the grid with `engine/beats.py`;
2. render stills at the peak beats (T(2), T(7), T(23), T(47), T(57), T(72)) and look at them before the full render;
3. render the video;
4. check that the big flashes sit on the grid (± 1 frame).

## 4. Visual brief | 画面说明（给设计/外包参考）

```
16:9 深色夜景（大类配色：NF 翡翠绿 / NT 紫 / SJ 蓝 / SP 琥珀），细发光线稿，配少量金色高光。
主角：兜帽、闭眼、金色波浪披肩、长斗篷，双手扶着立在身前的道具（剑 / 提灯杖 / 星杖 / 光球杖）。
地面是一排排小金色火苗（蜡烛）。人物背后有带火苗点的椭圆背光，头顶一圈光环。
爽点：道具落地光圈、蜡烛成波点亮、光束落下、扇形光线、线条带光点生长、标题十字星爆、
每段光环扩散、快推到脸、手中光球、一拍一面旗、斗篷展开碎片、举起道具冲天光束、人群举烛起立。
```
