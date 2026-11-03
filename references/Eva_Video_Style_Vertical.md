# Eva Video Style · Vertical (9:16)

The vertical house style for Eva's short videos (TikTok, Reels, Shorts, 抖音, 小红书), built on the same engine and look
as the 16:9 Eva Video Style. Use it whenever the output is 9:16. Every template from T01 to T24 renders in both
aspects (16:9 output is pixel-identical to before); **T26 Real Estate Social is vertical only**. Branch:
`feat/vertical-layouts-demos`. Technical reference: `references/responsive-layout.md`.

## Non-negotiables
- **9:16, 1080×1920, 30 fps.** Render with `--ar 9:16` (or `?ar=9:16`). No chapter bars, shot numbers, timecodes or render badges.
- **Never crop the frame from a 16:9 render.** Each template has its own vertical layout: hand-placed (native) or zone remap (the 16:9 design block scaled into the top zone, presenter re-placed below or kept inside the graphic).
- **Eva's whole head is always visible** (hair to chin) in every window and cut-out, and **her face stays above y 1300** so captions and platform UI never cover it.
- **Respect the phone UI:** nothing important in the top bar (0–210), the bottom UI band (1490–1920) or the right action rail (x 930–1080 from y 860). Text stays inside the safe area (x 64–930).
- **No background music by default.** Keep Eva's original voice untouched (trim only). Short SFX only, also delivered as a stem. Final loudness about -16 LUFS.
- **Never invent facts, numbers or screens.** On-screen text comes from her SRT; property facts, prices and sizes appear only when she supplies them. Conceptual graphics are labelled `示意 · ILLUSTRATIVE`.
- Never overwrite source videos, templates or approved samples. Every output goes to a new versioned folder.
- Workflow: vertical keyframe previews first, she reviews, then the full render.

## Look and feel
- **Rhythm:** same as 16:9 — a new composition every 1.5–3 s, cut on her phrases, one focal idea per beat. Vertical beats read top to bottom: headline first, then the point, then her face.
- **Vertical zones:** headline / cards in the top content zone (y 210–~900), presenter below (to ~1490), captions in the caption zone (1300–1490).
- **Presenter window in 9:16 morphs between:** full-bleed → card under the content block (about 700×660, centred) → circle (240–480 px, centred under the content or inside a globe / sun / hub) → cut-out with no frame (T19, T24, T26). Ring colour matches the scene, as in 16:9.
- **Presenter footage:** horizontal or vertical both work. Calibrate the face on the new footage (`face = x, y, h` as fractions of the frame) and pass the footage size (`srcw`, `srch`); the window centres on her face and caps the zoom to keep the whole head in.
- **Type:** the same fonts as 16:9 (Anton display, Noto Sans CJK SC Black). Long lines shrink to the safe width (`EV.fit`) instead of running off the edge.
- **Backgrounds:** full-frame backgrounds fill the 9:16 frame (footage, neon grade, grid floor, sky, comic rays). Real footage plays sharp in real time; never blur a real property or product shot.
- **T26 look (property tours):** cut-out presenter with a white sticker outline over real property footage, one shot per spoken line; heavy dark Chinese headline with a white keyline and one red phrase, yellow brush underline drawn on, yellow spark strokes, red hearts, icon list that builds as each point is spoken.

## Captions (exact style, 9:16)
Set `"aspect": "9:16"` in the captions config (`scripts/captions.py`):
- Canvas 1080×1920.
- CN: Noto Sans CJK SC Black 64 px, white, black outline 5, shadow 2, bottom-centre.
- EN: Inter Bold 40 px, light grey, outline 3, directly under the Chinese line.
- Margins: left 90, right 160 (clears the action rail), vertical 430 (bottom edge at y 1490, above the platform caption and buttons).
- English-only mode (`"mode": "en"`): Inter Black 64 px, same margins, vertical 440.
- One keyword per Chinese line highlighted in lime `#d4ff2e`; short fade 60/40 ms; never edit her original SRT.
- T26 shows the SRT lines as headlines and the icon list, so it is usually delivered without burned captions.

## Production pipeline
1. **Media:** extract her video to 30 fps JPGs (`f_00000.jpg`); for cut-out templates (T19, T24, T26) run `scripts/matte.py` for RGBA cut-outs. B-roll folders keep their names (`web`, `wb`, `fly`, `whis`, `sent`, `match`, `egg`, `jmw`); swap in her footage there.
2. **Calibrate** the face on a gridded frame and note the footage size.
3. **Preview:** `node scripts/render.mjs template/demo/tNN/index.html --ar 9:16 --stills check --times 1,4,8,12 --query "eva=…&srcw=1080&srch=1920&face=x,y,h&guides=1"` (`guides=1` draws the safe zones). Send keyframe sheets first.
4. **T26 from an SRT:** `python3 scripts/srt_to_beats.py talk.srt template/industry/t26/data.js --end SECONDS --bgcuts S1,S2,…` (one footage shot per line), then render with `--query "bg=../media/house"`.
5. **Render** the full video with `--ar 9:16 --out …`; dump SFX cues with `--cues`, build the stem with `scripts/sfx.py`.
6. **Audio:** original voice + SFX stem → loudnorm -16 LUFS. No music unless she asks.
7. **Captions:** `captions.py` with `"aspect": "9:16"`, then burn for the `_CN-EN` version.
8. **Verify:** 1080×1920, frame count, full decode, loudness, a contact sheet; check the face never enters the caption zone.
9. **Deliver** to a new folder: Clean MP4, CN-EN MP4, .srt, SFX stem.

## Practical gotchas
- Cut-outs take about 2–3 s per frame on CPU (a 15 s clip ≈ 20 min); start `matte.py` first and preview other templates meanwhile.
- In zone-remap templates the 16:9 block is scaled down, so dense 16:9 layouts (T10, T13, T21) read smaller in 9:16; keep their copy short.
- In T14, T15, T16 and T23 the presenter sits inside the graphic and is small; use them for graphic-led beats.
- B-roll with its own burned subtitles shows through in footage templates (T19, T09 wall); prefer clean footage.
- Still not vertical: the SaaS cloud pipeline (landscape input only) and the two layout reference pages (`template/cards/layouts`, `template/sample5/t24-layouts`).

## Templates

| ID | Template | 中文名 | Vertical layout | Best for |
|---|---|---|---|---|
| T01 | Acid Lime Kinetic | 酸性青柠 | native · text stack on top, presenter card below | Openings, hooks, bold claims |
| T02 | Electric Blue Console | 电光蓝控制台 | zone remap | Numbers, results, comparisons |
| T03 | Dark 3D Stage | 暗黑 3D 舞台 | zone remap | Screen recordings, product demos |
| T04 | Paper | 纸张 | zone remap | Pain points, calm lists |
| T05 | Red Sunburst | 红色放射 | zone remap | Key point, CTA, finale |
| T06 | Brand Purple | 品牌紫 | zone remap | Product reveal |
| T07 | Cartoon Eva | 卡通 Eva | zone remap · cartoon footage fills the frame | Storytelling, milestones |
| T08 | Neon Explainer | 霓虹讲解 | zone remap · full-bleed presenter, text in the lower zone | Explaining a concept |
| T09 | Showcase Wall Opener | 作品墙开场 | native · tall wall of playing video slices | Channel / series openings |
| T10 | HUD Keynote | HUD 发布会 | zone remap | Announcements, big news |
| T11 | HUD Dashboard | HUD 仪表盘 | zone remap | How-to, workflows |
| T12 | Old Newspaper | 旧报纸 | zone remap | Stories, opinion pieces |
| T13 | Tech Blue | 科技蓝 | zone remap | Tech / AI talks, agendas |
| T14 | Future Style | 未来科技 | zone remap · grid floor covers the frame, presenter inside the globe | AI and future topics |
| T15 | Learning Style | 学习风 | zone remap · starry sky covers the frame | Education, study tips |
| T16 | Comic Pop | 漫画风 | zone remap · comic rays cover the frame | Playful talks, before / after |
| T17 | Science Network | 科学风 | native · circle presenter moves between beats | Tech and science trends |
| T19 | Footage Intro | 真实影像引入 | native · cut-out shrinks into a circle | Bringing in real footage |
| T20 | Fast-Paced Social Media | 快节奏社媒 | native · full-bleed beat cuts | High-energy short videos |
| T21 | Clean & Minimal | 简洁极简 | zone remap | Calm tutorials, summaries |
| T23 | Creative Pop | 创意波普 | zone remap · presenter inside the hub | Step lists, creator tips |
| T24 | Luxury Nude Motion | 奢华裸色 | native · cut-out lower and centred, cards on top | Premium personal brand |
| T26 | Real Estate Social | 房产种草 | **vertical only** · sticker cut-out over property footage | Property tours, listings |

Sample frames use the AI presenter test clip and the demo B-roll; real videos use her own footage.

### T01 · Acid Lime Kinetic · 酸性青柠
Black and white cards stack in the top zone over the scrolling lime type wall; the presenter card sits below.

![T01 v1](samples/vertical/T01_v1.jpg) ![T01 v2](samples/vertical/T01_v2.jpg)

### T02 · Electric Blue Console · 电光蓝控制台
Lime display type and the 2×2 style cards on navy; presenter card or circle below.

![T02 v1](samples/vertical/T02_v1.jpg) ![T02 v2](samples/vertical/T02_v2.jpg)

### T03 · Dark 3D Stage · 暗黑 3D 舞台
Tilted 3D screens playing her footage on the orange-lit stage; presenter below.

![T03 v1](samples/vertical/T03_v1.jpg) ![T03 v2](samples/vertical/T03_v2.jpg)

### T04 · Paper · 纸张
Dot-grid paper, colour tiles, stamps and the check list; presenter below.

![T04 v1](samples/vertical/T04_v1.jpg) ![T04 v2](samples/vertical/T04_v2.jpg)

### T05 · Red Sunburst · 红色放射
Rotating red rays fill the frame; yellow headlines and numbered steps on top, presenter circle below.

![T05 v1](samples/vertical/T05_v1.jpg) ![T05 v2](samples/vertical/T05_v2.jpg)

### T06 · Brand Purple · 品牌紫
Purple gradient, style cards and the product shot; presenter below.

![T06 v1](samples/vertical/T06_v1.jpg) ![T06 v2](samples/vertical/T06_v2.jpg)

### T07 · Cartoon Eva · 卡通 Eva
Cartoon footage fills the 9:16 frame (audio muted), rounded lettering in the sky, framed clip cards; presenter circle below.

![T07 v1](samples/vertical/T07_v1.jpg) ![T07 v2](samples/vertical/T07_v2.jpg)

### T08 · Neon Explainer · 霓虹讲解
Pixel title, then a full-bleed neon-graded presenter with glowing text below her face; article card and diagram later.

![T08 v1](samples/vertical/T08_v1.jpg) ![T08 v2](samples/vertical/T08_v2.jpg)

### T09 · Showcase Wall Opener · 作品墙开场
A tall 3D wall of playing video slices sweeps past (`wall=DIR&wallN=FRAMES`), the counter rolls, then HUD titles with the presenter card below.

![T09 v1](samples/vertical/T09_v1.jpg) ![T09 v2](samples/vertical/T09_v2.jpg)

### T10 · HUD Keynote · HUD 发布会
HUD frame, BREAKING tag, glowing curve, globe, metallic hero title; presenter card or circle below.

![T10 v1](samples/vertical/T10_v1.jpg) ![T10 v2](samples/vertical/T10_v2.jpg)

### T11 · HUD Dashboard · HUD 仪表盘
Terminal, progress bars, flow tiles and toggles; presenter below.

![T11 v1](samples/vertical/T11_v1.jpg) ![T11 v2](samples/vertical/T11_v2.jpg)

### T12 · Old Newspaper · 旧报纸
Masthead, film strip with her footage, typed notes and red marks; presenter photo card below.

![T12 v1](samples/vertical/T12_v1.jpg) ![T12 v2](samples/vertical/T12_v2.jpg)

### T13 · Tech Blue · 科技蓝
Tech frame, serif titles, numbered style list and column cards; presenter below.

![T13 v1](samples/vertical/T13_v1.jpg) ![T13 v2](samples/vertical/T13_v2.jpg)

### T14 · Future Style · 未来科技
The neon grid floor covers the whole frame; the presenter sits inside the spinning globe and the torus ring.

![T14 v1](samples/vertical/T14_v1.jpg) ![T14 v2](samples/vertical/T14_v2.jpg)

### T15 · Learning Style · 学习风
Starry purple sky across the frame, rounded lettering, books and the sun with the presenter inside.

![T15 v1](samples/vertical/T15_v1.jpg) ![T15 v2](samples/vertical/T15_v2.jpg)

### T16 · Comic Pop · 漫画风
Comic rays and the zigzag split fill the frame; speech clouds, stickers, presenter card or circle.

![T16 v1](samples/vertical/T16_v1.jpg) ![T16 v2](samples/vertical/T16_v2.jpg)

### T17 · Science Network · 科学风
Plexus ribbon, globe, sphere chain and tunnel re-centred for 9:16; the circle presenter moves between beats.

![T17 v1](samples/vertical/T17_v1.jpg) ![T17 v2](samples/vertical/T17_v2.jpg)

### T19 · Footage Intro · 真实影像引入
Cut-out presenter over fast-swapping footage, then she shrinks into a circle that keeps the footage clear; end card.

![T19 v1](samples/vertical/T19_v1.jpg) ![T19 v2](samples/vertical/T19_v2.jpg)

### T20 · Fast-Paced Social Media · 快节奏社媒
Stickers, speed type and the kinetic caption bar; full-bleed beat-cut punches with a segmented progress bar.

![T20 v1](samples/vertical/T20_v1.jpg) ![T20 v2](samples/vertical/T20_v2.jpg)

### T21 · Clean & Minimal · 简洁极简
Quiet serif lines on warm paper; presenter circle or card below.

![T21 v1](samples/vertical/T21_v1.jpg) ![T21 v2](samples/vertical/T21_v2.jpg)

### T23 · Creative Pop · 创意波普
Seven-colour pills, step path and hub; the presenter sits inside the hub.

![T23 v1](samples/vertical/T23_v1.jpg) ![T23 v2](samples/vertical/T23_v2.jpg)

### T24 · Luxury Nude Motion · 奢华裸色
Nude stage, 3D white type and ivory cards in the top zone; the cut-out presenter stands lower and centred.

![T24 v1](samples/vertical/T24_v1.jpg) ![T24 v2](samples/vertical/T24_v2.jpg)

### T26 · Real Estate Social · 房产种草 (vertical only)
Sticker cut-out presenter over real property footage, one shot per spoken line; dark headline with a red phrase, yellow brush underline and sparks, red hearts, icon list built line by line. Text only from the SRT.

![T26 v1](samples/vertical/T26_v1.jpg) ![T26 v2](samples/vertical/T26_v2.jpg)
