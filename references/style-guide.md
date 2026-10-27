# Eva Video Style · style guide

## Rhythm
- There is a new composition every **1.5–3 s**, cut on the speaker's phrases. Each beat has one clear focal idea.
- Every graphic is timed to the exact word in the SRT that it illustrates. Pops land on the word, not near it.
- Each scene change gets a short whoosh unless the scene is marked `quiet`. Small pops/clicks accent the individual elements.

## The Eva window (the presenter is always on screen)
The window morphs continuously between these shapes. The engine eases position, size, corner radius and zoom together.

| Shape | Typical geometry (1920×1080) | Use |
|---|---|---|
| Full-bleed | `0,0,1920,1080` | Openings, emotional moments, a hook chip over her video |
| Large rounded card | right `1240,170,600,700` or left `60,240,460,600`, radius 32–36 | Explaining next to a headline |
| Circle | 270–340 px; top-right `1590,36,290,290`, top-center, top-left, bottom-left | Busy scenes, screens, lists |
| Big centered circle | about 450 px, center or right-center | Call to action, finale |

Rules:
- The **whole head is always visible**. The engine caps the zoom from the face calibration so the head fills at most about 60% of a card and a little less in a circle.
- The window never covers key graphics or the caption zone (the bottom ~150 px, centered).
- The ring color matches the scene: lime on navy, ink on lime or paper, white with a glow on red or purple.
- Each section's first pose equals the previous section's last pose.

## Palette
| Token | Hex | |
|---|---|---|
| Ink | `#0b0b0d` | text and dark backgrounds |
| Acid lime | `#d4ff2e` | the signature color: highlights, numbers, chips |
| Red | `#ff2b3d` | stamps, alarms, CTA sunburst |
| Electric blue | `#2a2cf2` | console scenes, headlines on paper |
| Navy | `#070b2e` | console backgrounds |
| Cyan | `#22e3ff` | glows, reel borders |
| Orange | `#ff7a1a` | 3D-stage floor glow, secondary chips |
| Purple | `#8a5cff` (brand purple `#5b3fd6` for product scenes) | product/brand scenes |
| Paper | `#f4f2ec` | calm explanatory scenes |

## Type
- **English display:** giant condensed uppercase (Anton), 90–260 px, tight line height.
- **Chinese:** Noto Sans CJK SC Black. Big Chinese display text is fine.
- **Chips:** heavy-weight text on a solid fill, small radius, soft shadow. They are often bilingual: `PRACTICE DAILY · 每天练习`.
- **HUD:** small mono uppercase labels for secondary English notes (`ISEE`, `ILLUSTRATIVE`).

## Surfaces
- Cards and chips are **solid**: high-saturation fills or white. Never use outline-only empty boxes. Any translucency must be at least 80% opaque.
- Real screen recordings sit on rounded white "screens" with a deep shadow. On the dark stage they can be tilted in 3D.

## Motion vocabulary
- **Pop** with overshoot (easeOutBack) for chips, numbers and icons.
- **Slide** with outExpo for headlines.
- **Clip-path wipes** for scene entries (left, right, up).
- **Counters and odometers** that roll to the real number.
- **Flip tiles** for scores, e.g. a row of "9" tiles.
- **Bars** that grow (illustrative unless the numbers are real).
- **Stamps** (NOT ENOUGH, NOT WORKING ✕) and check marks that stamp in.
- **Typewriter text** in chat bubbles or a URL bar.
- **Confetti or heart bursts** for wins.
- A **slow 3–6% push-in** on hero shots.
- **3D perspective screens** for real footage.

## Themes → named templates
The themes are now named templates **T01–T21** (T18 and T22 were retired). See `templates.md` for each one's shots, colors, Eva window and sample images.
- **Bright family:** T01 Acid Lime Kinetic · T02 Electric Blue Console · T04 Paper · T05 Red Sunburst · T06 Brand Purple · T07 Cartoon Eva
- **Dark:** T03 Dark 3D Stage
- **Neon:** T08 Neon Explainer (violet/magenta grade, glowing cream type, concept diagrams)
- **Vintage:** T12 Old Newspaper (aged paper, film strips and photos in b/w halftone, red brush stamps, hand-drawn red marks, typewriter, grain; Eva stays in natural colour)
- **Tech:** T13 Tech Blue (royal-blue gradient, chamfered thin-line HUD frame, blue tabs, dash ladders, barcodes, cyan serif titles, numbered contents, outlined cards)
- **Future:** T14 Future Style (indigo gradient, animated 3D wireframe wave floor in every shot, slowly rotating dotted globe with real continents and an orbit ring, glowing chip with circuit pulses, rotating wireframe ring, glowing white headlines, RULE 1/2/3 lists)
- **Learning:** T15 Learning Style (flat storybook illustration on indigo: twinkling stars and drifting clouds in every shot, bubbly rounded white lettering, book staircase, paper planes on dashed paths, sun, Read → Think → Create icons on soft blobs, open book with a pink sunrise, corner decorations, goal stickers)
- **Comic:** T16 Comic Pop (rotating sunburst rays with halftone dots in green/yellow/blue/purple/cyan, puffy white comic clouds with thick black outlines that bob, white zigzag lightning split screens for VS, big speech cloud title, black action marks, outlined yellow stars, sparkles over a cloud ground, outlined sticker cards, comic lettering)
- **Science:** T17 Science Network (near-black navy with drifting orange/blue bokeh, rippling plexus ribbon of connected nodes, slowly rotating plexus globe with real continents, chain of plexus spheres, plexus tunnel flowing toward the camera, white headlines with a cyan keyword)
- **HUD family:** T09 Showcase Wall Opener · T10 HUD Keynote · T11 HUD Dashboard. These share a dark frame with corner brackets, mono labels, a running timecode and a bracketed Eva window. Accents are blue `#4d7cff`, gold `#f5b83d` and green `#34d27b`.

## Signature beats
- A hook chip on a full-bleed opening.
- `01 / 02 / 03` section chips.
- A big word plus a bilingual chip, e.g. `RESULTS` + `MY DAUGHTER · 我女儿`.
- `YEAH!` + confetti + a 掌声 chip for wins.
- A product reveal: letter drop, then mascot pop, then real site screen, then feature chips.
- A CTA on a red sunburst: pill button, giant offer, then a URL typing into an address bar.
- A finale on lime, with the Eva circle big at center, the closing line and a brand/URL chip.

## Captions (exact burn style, ASS)
- **CN:** Noto Sans CJK SC Black 52 px, white, black outline 4, shadow 2, bottom-center, bottom margin 34.
- **EN:** Inter Bold 34 px, light grey, outline 3, directly under the Chinese line.
- **Side margins** are 380 px, so long lines wrap instead of running into a corner Eva circle.
- **One keyword per Chinese line** is highlighted in lime `#d4ff2e`.
- **Fades** are 60 ms in and 40 ms out.
- `scripts/captions.py` pairs each Chinese cue with the English cue it overlaps most, so slightly different timings are fine.
