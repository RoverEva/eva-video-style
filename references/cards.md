# EVA Card System

One shared, theme-aware card layer (`engine/cards.js`, global `K.EC`) that any template can call. It is **opt-in**: a section only gets it by adding `<script src="…/engine/cards.js"></script>` after `templates.js`. Existing templates, ASR, captions and music are untouched.

## Pieces
| Layer | API |
|---|---|
| Themes | `EC.theme(name, overrides)` — `premium` (reference look), `t17`, `t20`, `t01`, `t09`. Cards stay white / warm white; a theme changes accent, numerals, headline type, shadow tint, line colour and default motion. Backgrounds stay the template's own. |
| Components | `HeroCard`, `StepCard` (`dir: 'h' \| 'v'`), `IconCard` (`shape: 'tile' \| 'disc'`), `FlowCard` (linear or curved, animated arrow), `FeatureCard` (icon or `image`). Each returns `{ g, at(t, t0) }`. Icons come from `K.T.cpIcon` (`K.T.cpIconNames`). |
| Layouts (9) | `EC.layout(L, name, data, box, th)` → `o.at(t, times)`: `hero`, `steps-v`, `steps-h`, `orbit`, `statement`, `stack`, `feature`, `journey`, `grid`. All are compositions of the five components. |
| Motion | `EC.move(el, t, t0, th, {preset})`: `fade-slide`, `pop`, `float`, `stack`, `tilt`, `rearrange`; plus `EC.connector(...).at(u)` for arrow drawing / curved path reveal. Sequential steps = one landing time per item (`EC.times(t0, n, step)` or ASR word times). |
| Safe areas | `EC.region('right' \| 'left' \| 'top' \| 'bottom' \| 'around', evaWindowRect)` gives a card box beside the presenter; `EC.overlapsFace(box, rect)` checks it. |

## In a section
```js
const th = K.EC.theme('t17');
C.scene({ t0: 0, t1: 6, z: 60, quiet: true,                       // z 60 = above the Eva window
  build(L) { return { s: K.EC.layout(L, 'stack', { steps }, K.EC.region('right', WIN), th) }; },
  update(lt, st, t) { st.s.at(t, ['Idea', 'Plan', 'Build', 'Grow'].map(w => T(EV.asr.at(w)))); } });
```

## JSON card specs
`EC.fromSchema(L, specs, th, { toLocal: T, win })` then `EC.schemaAt(list, t)`.
```json
{ "id": "card_001", "type": "step", "layout": "steps-v", "style": "t17",
  "content": { "number": 1, "title": "IDEA", "subtitle": "Find the opportunity", "icon": "idea" },
  "position": { "anchor": "right", "x": 0.55, "y": 0.2, "w": 0.4, "h": 0.25 },
  "animation": { "preset": "fade-slide", "start": 2.5, "duration": 0.6 } }
```
- `type`: `hero | step | icon | flow | feature | layout`; a `layout` entry carries `content.items` (`[{title, sub, icon}]`).
- Timing: `animation.times` (absolute) > `animation.words` / `word` (looked up with `EV.asr`) > `start` + `stagger`. Absolute times go through `toLocal`.
- `style` may name another theme for one card; unknown types, layouts, presets or icons are rejected by `EC.validate`.

## Writing cards from a finished script (for the editing agent)
1. Read the final script / storyboard / SRT once; list the key ideas, steps, features and processes.
2. Pick the component + layout per beat (sequence → `steps-v`/`steps-h`/`stack`, cycle → `orbit`, journey → `journey`, one claim → `hero`/`statement`, detail → `feature`, overview → `grid`).
3. Write short on-screen text taken from the spoken words. Never rewrite the voiceover or add claims it does not make.
4. Choose icons from `K.T.cpIconNames`; place cards with `EC.region` so they never cover the face.
5. Time each item from the ASR word timestamps (`animation.words`).

## Preview
`scripts/cards_preview.sh [OUT]` renders one still per template (T17, T20, T01, T09, same sample content) and a 3×3 sheet of the nine layouts — no video. Tests: `node tests/test_cards.mjs`.
