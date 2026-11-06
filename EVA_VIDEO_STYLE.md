---
name: eva-video-style
description: Edit Eva's talking-head videos in "Eva Video Style": adusample-inspired kinetic motion design, morphing Eva window, solid color cards, bilingual CN+EN captions, no BGM.
---

# Eva Video Style

The house style approved on the CasualTalk project (Oct 2026). Use it for every Eva video unless she asks otherwise. Visual reference: `~/Desktop/adusample.mp4`. Approved example: `~/Documents/ChatGPT/Video/projects/casualtalk/v4_full/` (CasualTalk_v4_FULL_CN-EN.mp4 + editable project zip).

## Non-negotiables
- 16:9, 1920×1080, 30 fps. No chapter bars, shot numbers, timecodes or render badges in the output.
- **No background music**, ever (including music inside any template or cartoon clip — mute them). Keep Eva's original voice untouched (trim only). Short SFX only, delivered also as a separate stem. Final loudness about -16 LUFS.
- **Templates carry no sound.** Never use the sound cues built into a template or demo (they are muted in the engine: `K.sfx` does nothing). Claude designs the SFX for each video from its content: read the script and the cut, then add a cue only where something happens (soft `impact` under the hook or a key claim, `whoosh` on a scene/template change, `pop` when a word or card lands, `ding` on a check or result, `riser` before a reveal, `applause` only for a real win or the finale). Keep it sparse, off her key syllables, gain about .05–.16. Written with `K.cue(kind, t, gain)` in the section's `scenes.js`.
- **Presenter on top, never enlarged for layout.** In cut-out templates Eva is always the top layer: big titles sit behind her (they may be partly hidden by her), never over her face, features or hands. Templates move her sideways to make room for text; they do not scale her up beyond the footage's own size (no extra zoom that crops head, face or gestures). Her pixels come from the full HD frame masked by the cut-out, so she stays sharp.
- **Eva's whole head is always visible** in every window (hair to chin). Never crop her face.
- **Vertical (9:16, 1080×1920) versions** for TikTok / Reels / Shorts / 抖音 / 小红书: every template also renders vertical (branch `feat/vertical-layouts-demos`, `--ar 9:16`). Rules, safe zones and the vertical template card: `Eva_Video_Style_Vertical.md` (next to this file).
- Never overwrite source videos, templates, old projects or approved samples. Every output goes to a new versioned folder.
- Never invent facts, numbers or software screens. Real UI only from her real recordings (e.g. `工作台.mov`). Anything conceptual (dashboards, charts, upload tiles, cost splits) is labelled `示意 · ILLUSTRATIVE`, uses bars without fake numbers, and personal estimates are labelled as such.
- Captions are bilingual: Chinese line on top, English line underneath, from her bilingual SRT. Deliver a Clean (no captions) version, a burned `_CN-EN` version, and the editable `.srt`. Don't change the video design when only captions change.
- Workflow: samples first (3 short sections, different themes), she reviews, then the full video.

## Look and feel (learned from adusample)
- **Rhythm:** a new composition every 1.5–3 s, cut on her phrases. Each beat has one clear focal idea.
- **Eva window morphs continuously** between: full-bleed → large rounded card (right or left, about 620×720) → circle (about 270–340 px; top-right, top-left, top-center, bottom-left) → large centered circle for emphasis. It never covers key graphics or the caption zone (bottom ~150 px, centered). Ring color matches the scene (lime, ink, white, orange glow, cyan glow).
- **Palette:** ink `#0b0b0d`, acid lime `#d4ff2e`, red `#ff2b3d`, electric blue `#2a2cf2`, navy `#070b2e`, cyan `#22e3ff`, orange `#ff7a1a`, purple `#8a5cff`, paper `#f4f2ec`.
- **Type:** giant condensed English display words (Anton, uppercase) paired with heavy Chinese (Noto Sans CJK SC Black). Big Chinese display text is fine. Small mono HUD labels for English sublabels.
- **Cards and chips are solid** (high-saturation fills or white). Never outline-only empty boxes; any translucency at least 80% opaque.
- **Motion vocabulary:** pop with overshoot (easeOutBack), slide with outExpo, clip-path wipes for scene entries, counters/odometers, bars that grow, check marks that stamp, typewriter text in chat bubbles, confetti or heart bursts for celebration, slow 3–6% camera push on hero shots, 3D perspective screens for real footage.
- **Rotating themes (one per section, never the same twice in a row):**
  1. *Acid Lime Kinetic:* black with a colored symbol field, or full lime with a dot grid; marquee rows of a repeated word (e.g. UPGRADE); numbered white cards 01/02; calendar/tile grids.
  2. *Electric Blue Console:* blue/navy with a line grid; white solid panels; neon-lime numbers; rolling odometer; ring gauges; timelines.
  3. *Dark 3D Stage:* near-black with an orange/purple floor glow and a perspective grid floor; real screen recordings on tilted 3D screens; walls of screens; push-ins; split screens; funnels.
  4. *Paper:* off-white dot grid, colored solid tiles, stamps (MESSY!, 明后天).
  5. *Red sunburst:* rotating conic rays for key points and the like/follow finale (♥ 点赞, + 关注 pills).
  6. *Cartoon Eva:* her own AI cartoon clips (`eva_ai_buildup.mp4` tool tower, `eva_ai_buildup02.mp4` platformer/castle/GitHub block), full-bleed or in a framed screen, audio muted, text placed in open sky so it never covers the character.
- **Signature beats:** hook chip on full-bleed open; "01 / 02 / 03" section chips; "YEAH! + confetti + 掌声 chip" for wins; COMMENT bubbles with typed keywords; COMING NEXT cards; "SEE YOU TOMORROW" finale.

## Template T27 · Video Wall Kinetic Typography (视频墙动感大字)
- Approved on C06《内容战略引擎》(Nov 2026). Engine `engine/t27.js` (branch `feat/t27-video-wall`), 5 s sample `template/sample5/t27/`.
- Layers, fixed: scrolling, softly blurred wall of video frames → big CN words (Noto Sans CJK SC 900, white / lime `#c6ff1a` / indigo `#3b2bff` box, black stroke) **behind** Eva → Eva in front → a few hand-drawn white rays. Text never covers her face, body or hands.
- Eva = the original HD frame masked by the cached AI cut-out (RVM `scripts/matte.py`), so she stays sharp; grade person, words and wall separately, never one global filter.
- White outline about 18 px with a ~10 px gap, smooth, continuous and steady; follows arms and palms loosely, not pixel by pixel.
- Words come from the script (`T.vwPlan`), 1–2 lines per beat, layouts A–F with auto-fit; strong 3 s hook (white flash + push-in). If a second line would sit behind her head, use a layout that keeps it beside her.
- Good as the main look (~70%) with T11 for real screenshots, T05 for key points, T16 for the ending. Slow to render (~9 s/frame): render long sections in chunks with `--from/--to`.

## Template T28 · Real Estate Social — build notes (first built as T26 on `feat/vertical-layouts-demos`)
- Built Nov 2026 for property tours and listing intros. Source `template/industry/t26/` (branch `feat/vertical-layouts-demos`). **Native 9:16** (default, 1080×1920) **and 16:9** (`--ar 16:9`, 1920×1080). Demos: 9:16 on the house-tour footage, 16:9 on the model-home screen recordings.
- Layers: real property footage, sharp and playing in real time, one shot per spoken line, soft white flash at each cut → Eva cut out (RVM `scripts/matte.py`) with a white sticker outline and a soft shadow → text and stickers on top.
- Text style: heavy dark Chinese (Noto Sans CJK SC Black, `#2b1a12`) with a thick white keyline; one phrase per line in red `#ff2d4b`; yellow `#ffd21f` brush underline drawn on, yellow spark strokes, red heart stickers.
- Three beats from the SRT: opening line as a two-line headline → each point as an icon row (sun, space, tree, house, kitchen, bed, pin, school, pool, check) that pops in as she says it → closing line as a big headline. 16:9: Eva in the right third, text in the left two thirds. 9:16: text in the top zone, Eva centre / right / lower.
- Data-driven: `scripts/srt_to_beats.py talk.srt template/industry/t26/data.js --end S --bgcuts S1,S2,…` (one footage start second per line). Every on-screen word is copied from the SRT; rooms, size, price and other property facts appear only when Eva supplies them.
- SFX are content cues only (pop per point, soft impact on the red phrase, ding on the close). The T26 code still writes them with `k.sfx`; switch them to `K.cue` when the vertical branch is merged with the T27 branch.
- Cut-outs take about 2–3 s per frame; start `matte.py` first.

## Template T28 · Real Estate Social (房产种草)
- For agents' listing videos: one presenter in front of the house explains the property in a few lines, for Reels / TikTok / 抖音 / 小红书. 9:16 first, 16:9 too. (First numbered T26 on GitHub; renamed T28 so it doesn't clash with T26 Vintage Story.)
- Background: real property footage, sharp, normal speed; each spoken line cuts to the matching shot (exterior ↔ 外观, window-lit living room ↔ 采光, yard ↔ 庭院) with a soft white flash.
- Presenter: AI cut-out with a white outline and soft shadow, like a sticker on the footage; full size, never shrunk or blurred.
- Text: dark-brown bold CN with a thick white keyline; one red keyword per line (超心动, 自住了) with a yellow brush underline drawn on, yellow spark strokes and red heart stickers (小红书 种草 look).
- Three beats, all from the .srt: opening = two-line headline; points = one "icon + text" line pops in per spoken point and stacks into a list (sun = light, expand box = space, tree = yard, plus kitchen, bed, location, school, pool…); closing = big final line + heart.
- 9:16: text on top, presenter below or to the side, clear of the platform top bar, caption area and right-side buttons. 16:9: presenter in the right third, title and list on the left.
- Every on-screen word comes straight from the .srt, unchanged. Rooms, size, price appear only if Eva supplies them.
- Sound from the content: a pop per point, a light impact on the red word, a ding at the end. No music, original voice.

## Template fixes and layouts (Nov 6 2026)
- **T26 Vintage Story (复古拼贴故事):** the presenter cut-out keeps the original scale in every layout (no 1.25–1.75× zoom, no entrance zoom); poses only move her (01 centre, 02 left, 03/08/09 right) so the whole head, shoulders and hands stay in frame and the titles sit behind her. The pixels come from the HD frame masked by the cut-out, with the cream outline and shadow on top.
- **T17 Science Network:** original look unchanged. Face-safe headlines: the presenter is always on top; `T.sciAvoid` keeps big type upper-left (reflowed into a taller left column at full size, or above the head, or on the far side) and never across the face or hands; with a full-bleed presenter `T.sciCutTop` puts her sharp cut-out above the type.
- **T19 Footage Intro · product demo:** the product screen recording plays full-bleed behind at normal speed with a slow push-in; Eva, cut out, stands in front at full size, then shrinks into a small white-ringed circle with a cyan glow (head and shoulders break out of its top) that lands bottom-left and then hops top-left ↔ bottom-left; optional slanted label with text from the screen. `T.ftDemo` / `T.ftDemoAt`, sample `template/sample5/t19-demo/`. SFX from the content: whoosh on the shrink, light pop on each landing.
- **T08 Neon Explainer v2 (preview, waiting for Eva's OK):** T24-level presenter clarity: the purple-blue mood is only in the background (original frame softened, dimmed, light purple-blue wash); Eva is the HD frame masked by the cut-out, sharpened and lifted slightly, never under haze; headline in bold sans (white + warm cream), soft glow only, dark shadow, upper-left, clear of the face. `T.neonStage` / `T.neonStageAt` / `T.neonTitle`.
- **No template sound (engine):** besides `K.sfx`, the engine's automatic whoosh on every scene change is off too (only with `C.templateSfx`).

## Captions (exact style)
- Style CN: Noto Sans CJK SC Black 52 px, white, black outline 4, shadow 2, bottom-center, margin 34.
- Style EN: Inter Bold 34 px, light grey, outline 3, directly under the Chinese line. Side margins 380 px so long English lines wrap instead of hitting corner Eva circles.
- One keyword per Chinese line highlighted in lime `#d4ff2e`.
- Bilingual SRT format: Chinese cues and English cues share identical timestamps; pair them by timestamp.
- Short fade 60/40 ms. Obvious typos can be fixed in display, but never edit her original SRT file.

## Production pipeline (what worked)
1. **Check what exists first**, don't reinstall. Engine: adu-motion-video (`render_project.mjs`, `export_project.py`, `presenter_motion.js`). Needs Node 22+, Python, Chromium/Playwright, FFmpeg 9+ (a static BtbN 9.x build works; it reports `n9.x`, so a version-line wrapper may be needed). Add `output-signature.json` with `{"schema":"adu-output-signature/1","enabled":false}` to every section folder to remove Adu's corner badge.
2. **Reuse the approved engine** from `CasualTalk_v4_FULL_editable_project.zip`: `lib/engine.js` (deterministic `renderAt(t)` timeline, Eva window, image-sequence media), `lib/kit.js` (palette, chips, cards, screens, floors, sunburst, symbol field, `k.sfx` cues), `lib/engine.css`, fonts (Anton), and `tools/` (`captions.py`, `sfx.py`, `dump_sfx.mjs`, `render_sections.sh`, `build.sh`). Each section is a folder with `index.html` and `scenes.js` built from `C.scene({t0,t1,bg,build,update})` plus `C.evaKeys`.
3. **Media:** extract Eva's video and screen recordings to 30 fps JPG sequences named by absolute source frame (`f_00000.jpg`). Cartoon clips likewise.
4. **Calibrate the face** on the new footage (gridded frames): set `face {x, y, h}` in `engine.js` (CasualTalk: x .625, y .31, h .48). The engine caps zoom so the head fills about 52–60% of any window.
5. **Plan from the SRT:** group cues into sections of about 15–30 s, give each a theme, and time every chip pop to the exact word. Read the transcript for meaning and map visuals to what she actually says.
6. **Render samples** (3 sections, ~25 s each): stills check → full render → bilingual caption burn → send. After approval, render the remaining sections with exact frame boundaries so they concatenate to the source frame count, and make each section start and end on the neighboring section's Eva pose.
7. **Audio:** full original voice + the content-designed SFX (only the `K.cue` cues written for this video, offset to their section start) → loudnorm -16 LUFS. Never add music, never use template sound.
8. **Assemble:** concat the section videos, mux audio, then burn captions for the `_CN-EN` version. Verify the frame count, a full decode, loudness, join frames and a contact sheet.
9. **Deliver** to a new folder under the project (`vN_samples/`, `vN_full/`): Clean MP4, CN-EN MP4, .srt, SFX stem, editable project zip.

## Practical gotchas
- Files staged from her Mac must be under 400 MB. For big 4K masters ask her to export from QuickTime: File → Export As → 1080p → "Smaller File Size" (it saves as `.mov`; that's fine).
- Writing back to the Mac is limited to 30 MB per file; large videos are delivered as chat downloads for her to save.
- The `.motion` MotionGit packages need motiongit.com. If it is blocked, say so plainly and use the local Adu engine; never fake a `.motion` render.
- Cartoon clips imitate a famous platformer look; usable at her discretion.
