# Long-form · 「X的内心世界」 8-minute story videos

One script, one hero, about 70–100 caption cards across 12–13 chapters. All of it rides the music grid. The same engine and line-art language as the MBTI and Zodiac templates, cut like a story:

- **Hook (first ~10 s):** heartbeat rings → question → glyph/type slam → prop drops with a beam and the candle wave → the hero grows → title + tagline.
- **Every card gets its own shot,** never the same framing twice in a row: `hero` (medium), `wide`, `face` (close-up), `side` / `sideL` (hero + insert), `icon` (insert, hero ghosted), `scene` (full-frame vignette), `quest` (question card).
- **Cards over 5 s cut to a second angle halfway,** so the picture changes every ~3–5 s.
- **Story inserts (`vis.py`):** 50+ glowing line-art vignettes that grow stroke by stroke on the eighth notes, plus a live layer that moves on the beat:
  - a book flips a page on every quarter note;
  - chat bubbles pop in a phone;
  - rain falls, a lock clicks open, a door opens to light;
  - coins drop, a sprout grows, footprints walk a road;
  - a climber goes up a mountain, a heart beats.
- **Face effects** (close-up on the hero): `tears` fall from both eyes, plus `blush`, `smile`, `think`, `sigh`, `sweat`.
- **Question cards (`?`) every ~15 s:** a flash, a punch-in, and a big centred question that turns the story.
- **Chapter cards:** `CHAPTER 0X` + a 150 px title over a dimmed world, with a ring burst and the chapter motif (any MBTI/zodiac signature or `duality` / `messages` / `heart` / `bolts`).
- **Mobile legibility:** normal cards are 56–72 px over a dark band at the bottom; key cards are 72–96 px centred.

## Script format (`src/*.txt` → `scripts/*.json`)

```
TITLE 白羊座的内心世界
SUBJ zodiac aries            # or: SUBJ mbti INFJ
Q 你有没有遇到过/这样一种人？      # hook question
B 明明天不怕地不怕/却最怕被在乎的人误解   # hook lines under the hero
TAG 外表有多【倔强】/内心就有多【柔软】  # under the title

# 矛盾 duality                # chapter name + motif
{smile}明明上一秒/还笑得很【灿烂】      # {vis} insert, / line break, 【gold】
{road@scene}遇到喜欢的事/可以不顾一切地【向前冲】   # @shot forces a framing
?可如果你真的/走进白羊的【内心】/会看到什么？        # question card
*他们/就是【白羊座】                               # key card
```

```bash
python3 template/longform/build_scripts.py              # compile every src/*.txt (validates motifs + visuals)
python3 template/longform/check.py template/longform/scripts/aries.json     # one still per chapter → /tmp/chk
python3 template/longform/sheet.py template/longform/scripts/aries.json 0 12 /tmp/sheet.jpg   # contact sheet of cards
python3 template/longform/render_long.py --script template/longform/scripts/aries.json \
        --music media/Vibecoding_music.mp3 --out out/long/aries.mp4
```

The renderer sizes every card in whole quarter notes, by reading time (key cards get extra time). It then solves a reading speed so the whole video lands at 8.0–8.4 min, and loops the music in whole bars from its first grid point. Each video takes about 15–20 min on 2 cores at 1080p / 24 fps.

Scripts included: all 12 signs and all 16 MBTI types.
