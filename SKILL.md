---
name: eva-video-style
description: Edit talking-head videos in Eva Video Style — kinetic motion graphics, a morphing presenter window, solid high-saturation color cards, bilingual Chinese + English captions, and no background music. Use when asked to edit, design, or animate a talking-head / vlog / product-promo video "in Eva Video Style", or when given a raw video plus a bilingual SRT to turn into a motion-designed video.
---

# Eva Video Style

A motion-design house style for Eva's talking-head videos (bilingual creator, Chinese + English). The speaker stays on screen the whole time inside a window that keeps changing shape, while bold solid-color cards, giant condensed words and real screen recordings pop in exactly on the words she says.

Read these before building:
- `references/templates.md` — **the 20 named templates (T01–T21; T18 and T22 were retired)** with sample images. The user picks them by ID or name ("use T10 HUD Keynote for this part").
- `references/style-guide.md` — the look: palette, type, Eva window, motion vocabulary, themes, signature beats, captions.
- `references/pipeline.md` — step-by-step production, from raw video to delivered masters.
- `references/engine-api.md` — how to write a section with the bundled engine (`engine/`, `template/section/`).

## Templates

| ID | Chinese name | Name | Best for |
|---|---|---|---|
| T01 | 酸性青柠 | Acid Lime Kinetic | openings, hooks, bold claims, wins |
| T02 | 电光蓝控制台 | Electric Blue Console | numbers, results, comparisons |
| T03 | 暗黑 3D 舞台 | Dark 3D Stage | real screen recordings, demos |
| T04 | 纸张 | Paper | pain points, calm explanations |
| T05 | 红色放射 | Red Sunburst | key point, call to action, finale |
| T06 | 品牌紫 | Brand Purple | product reveal |
| T07 | 卡通 Eva | Cartoon Eva | storytelling (needs her cartoon clips) |
| T08 | 霓虹讲解 | Neon Explainer | explaining a concept, tutorials |
| T09 | 作品墙开场 | Showcase Wall Opener | channel/series openings, launches |
| T10 | HUD 发布会 | HUD Keynote | announcements, milestones |
| T11 | HUD 仪表盘 | HUD Dashboard | how-to, workflows, features, iteration |
| T12 | 旧报纸 | Old Newspaper | stories, look-backs, opinion, calling out a problem |
| T13 | 科技蓝 | Tech Blue | tech, AI and product talks, agendas, chapter titles, comparing options |
| T14 | 未来科技 | Future Style | big news, rules / key points, AI and future topics, endings |
| T15 | 学习风 | Learning Style | education, study tips, vocabulary and reading, videos for kids and parents |
| T16 | 漫画风 | Comic Pop | playful talks, before-vs-after comparisons, key points, tip lists |
| T17 | 科学风 | Science Network | tech and AI trends, science topics, how learning works, future outlooks |
| T20 | 快节奏社媒 | Fast-Paced Social Media | TikTok / Shorts / Reels energy: kinetic word-by-word captions, stickers, beat cuts (laid out 16:9) |
| T21 | 简洁极简 | Clean & Minimal | tutorials, business analysis, education: serif headlines, hairlines, slow motion |
| T19 | 真实影像引入 | Footage Intro | bringing in real footage / news clips: cut-out + fast swaps through the background images or footage the user imports (no bundled images), footage push-in, presenter circle that keeps the footage clear, captions that move off the footage |

When the user names templates, use exactly those for those parts. When they don't, choose per section from "Best for" and follow the mixing rules in `references/templates.md`. T08–T17 have ready-made helpers in `engine/templates.js`, and every template has a full demo section in `template/demo/t01` … `template/demo/t21` (all on the same 15 s intro, so they are easy to compare and copy from). T19 also uses `scripts/matte.py` (AI cut-out, keeps natural face colour; the GPL-3.0 model downloads on first use) and `scripts/caption_zones.py` (moves each caption to the clearest zone and adds a soft plate on busy footage). T19 never ships or invents background images: it only uses images and clips the user provides (their footage, screen recordings, photos), passed in as frame folders. Never draw brand logos on a T19 title card, and remove logos visible in imported backgrounds; its headline and tags come only from the script. Every template is 16:9 (1920×1080); vertical references are re-laid out for landscape.

## Non-negotiables

1. **16:9, 1920×1080, 30 fps.** No chapter bars, shot numbers, timecodes or watermarks in the output.
2. **No background music, ever.** This includes music inside any clip or template, which must be muted. Keep the speaker's original voice untouched (trim only). Add short SFX only (whoosh, pop, click, impact, ding, applause). Final loudness is about **-16 LUFS**.
3. **The speaker's whole head is always visible**, from hair to chin, in every window shape. Never crop the face; calibrate the face position on every new shoot.
4. **Never overwrite** source videos, old projects or approved samples. Every output goes to a new versioned folder (`v1_samples/`, `v1_full/`, `v2_full/` ...).
5. **Never invent facts, numbers or software screens.** Show real UI only from real screen recordings. Label anything conceptual `ILLUSTRATIVE` and draw it without fake numbers. Show stated results (scores, prices, dates) exactly as spoken.
6. **Bilingual captions:** Chinese line on top, English line underneath, built from the speaker's bilingual SRT. Obvious typos or machine-translation errors may be fixed **in the burned captions only**. Never edit the original SRT, and tell the user which lines were corrected.
7. **When only captions change, don't touch the video design.**
8. **Workflow:** for a new series or a first video, make about three short sample sections in different themes, get approval, then do the full video. For a follow-up video in an approved style, go straight to the full video.

## Deliverables

- `NAME_CN-EN.mp4`: burned bilingual captions.
- `NAME_Clean.mp4`: no captions. Skip it if the user says they only want the captioned version.
- `NAME_CN-EN.srt`: editable paired captions.
- The SFX stem (`.wav`) and an editable project zip.

## Quick start

```bash
# 1. media
scripts/extract_frames.sh raw/talk.mp4 media/eva          # speaker as 30 fps JPGs
scripts/extract_frames.sh raw/screen.mp4 media/screen     # real screen recording(s)
# 2. sections: copy template/section/ per 15–40 s chunk, write scenes.js (see references/engine-api.md)
node scripts/render.mjs s1/index.html --stills check/s1 --times 1,4,8,12   # layout check
node scripts/render.mjs s1/index.html --out sec/s1.mp4                     # silent render
node scripts/render.mjs s1/index.html --cues sec/s1_cues.json              # sound cues
# 3. audio + captions + assembly
python3 scripts/merge_cues.py sec/all_cues.json sec/s1_cues.json:0 sec/s2_cues.json:37.4
python3 scripts/sfx.py sec/all_cues.json 73.667 sec/sfx.wav
python3 scripts/captions.py raw/talk.srt 0 99999 out/NAME_CN-EN display_fix.json
scripts/assemble.sh raw/talk.mp4 sec/sfx.wav out/NAME_CN-EN.ass out/NAME sec/s1.mp4 sec/s2.mp4
```

Requirements: Node 18+ with `playwright` (Chromium), Python 3 with `numpy`, FFmpeg with libass and libx264, and the fonts listed in `engine/fonts/README.md`.

## Before delivering, verify

- The frame count of the final equals the source video's frame count. Section boundaries must be frame-exact.
- The whole video decodes without errors, and loudness is about -16 LUFS.
- On a contact sheet (`scripts/contact_sheet.sh`), no text sits under the Eva window, nothing is cut off at the frame edge, captions don't collide with graphics, and the face is never cropped.
- The Eva window pose at the end of each section equals the pose at the start of the next, so joins are invisible.
