# Eva Video Style · production pipeline

## 0. Inputs
- **Raw talking-head video.** 1080p is enough. Ask for a 1080p export if the master is a huge 4K file.
- **A bilingual SRT:** Chinese cues and English cues for the same speech, in one file.
- **Optional resources:** real screen recordings (product website, app, tools) and the speaker's own cartoon or B-roll clips.
- Check what tools are already installed before installing anything.

## 1. Project layout (new versioned folder; never write into source folders)
```
project/v1/
  engine/  (copy of this repo's engine/, with fonts)
  media/eva/      f_00000.jpg ...   speaker, 30 fps
  media/screen/   f_00000.jpg ...   each resource clip in its own folder
  s1/ s2/ ...     one folder per section: index.html + scenes.js (copied from template/section/)
  srt/            copy of the user's SRT + display_fix.json
  sec/            section renders, cue files, SFX stem
  out/            final masters, captions, contact sheets
```
Inside `s1/index.html`, point the `<link>` and `<script>` paths at `../engine/`.

## 2. Extract media
`scripts/extract_frames.sh raw/talk.mp4 media/eva` writes frames at exactly 30 fps, named by absolute frame number. Record the frame count: it is the target length of the final video. Extract each resource clip the same way and note its aspect ratio (screen width ÷ height) for `K.screen`.

## 3. Calibrate the face
Render or view 3–4 frames from different moments with a grid. Set `EV.face = { x, y, h }` as fractions of the frame: `x` is the face center, `y` is the head center, `h` is the head height from hair top to chin. Then render a still of the smallest circle and the largest card. The whole head must be visible in both. Re-measure for every new shoot or camera position.

## 4. Plan from the SRT
- Read the whole transcript for meaning first, then group cues into **sections of about 15–40 s** that cut at pauses.
- Give each section a theme (rotate them). Break each section into scenes of 1.5–6 s, one idea each.
- For every scene, write down: the background, the Eva window shape, the 2–4 elements that pop, and **the exact cue time each one lands on**.
- Choose section boundaries on exact frames (`frame / 30`) so that the section lengths add up to the source frame count.
- Use real footage where the speaker refers to it. Draw everything else as typographic or illustrative graphics, and label anything conceptual.
- Facts and numbers come only from what she says.

## 5. Build and check stills
Write each `scenes.js` (see `engine-api.md`). Render stills at the busiest moments of every scene:
```
node scripts/render.mjs s1/index.html --stills check/s1 --times 1.2,3.5,6,9.8
```
Tile them into a contact sheet and fix any collisions:
- text under the Eva window
- chips overlapping each other
- screens cut off at the frame edge
- empty frames while she is still talking
- graphics in the caption zone
Re-check the stills after every fix.

## 6. Render
```
node scripts/render.mjs s1/index.html --out sec/s1.mp4     # silent, frame-exact
node scripts/render.mjs s1/index.html --cues sec/s1_cues.json
```
Sections are independent, so they can render in parallel. Verify each section's frame count.

## 7. Audio (voice + SFX only)
```
python3 scripts/merge_cues.py sec/all_cues.json sec/s1_cues.json:0 sec/s2_cues.json:<s2 start seconds> ...
python3 scripts/sfx.py sec/all_cues.json <total seconds> sec/sfx.wav
```
`assemble.sh` mixes the original voice with this stem and normalizes the result to -16 LUFS. **Never add music.**

## 8. Captions
1. Copy the SRT.
2. List machine-translation errors and typos in `display_fix.json` (`{"fix": {"original line": "display line"}, "keys": ["highlight words"]}`).
3. Run:
```
python3 scripts/captions.py srt/talk.srt 0 99999 out/NAME_CN-EN srt/display_fix.json
```
This writes the editable `.srt` and the styled `.ass`.

## 9. Assemble and verify
```
scripts/assemble.sh raw/talk.mp4 sec/sfx.wav out/NAME_CN-EN.ass out/NAME sec/s1.mp4 sec/s2.mp4 ...
scripts/contact_sheet.sh out/NAME_CN-EN.mp4 out/sheet.jpg 5
```
Check:
- The frame count equals the source.
- Loudness is about -16 LUFS.
- The whole video decodes without errors.
- The contact sheet looks right.
- Each join frame shows the same Eva pose on both sides.

## 10. Deliver
- Put the masters in the new version folder, along with the `.srt`, the SFX stem and a zip of the project (without the media frames).
- Tell the user:
  - what each part of the video does, in 3–6 bullets
  - which caption lines were corrected for display
  - anything that was left out or labelled illustrative

## Troubleshooting
- **Black or blank speaker window:** check `EV.evaDir` relative to the section folder, and the frame naming (`f_00000.jpg`).
- **Fonts fall back to a default:** check `engine/fonts/` and the system font install, and pass `FONTSDIR` to `assemble.sh` for caption fonts.
- **"Refusing to overwrite":** the scripts never replace existing outputs. Choose a new name or version folder.
- **Joins jump:** the last `evaKeys` pose of section N must equal the first pose of section N+1, and `src0` must equal the exact start frame ÷ 30.
