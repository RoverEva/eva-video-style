# Eva Video Style · engine API

The engine is plain HTML, CSS and JS. A section is one page whose picture is a pure function of time `t`. `scripts/render.mjs` steps `t` frame by frame and screenshots each frame, so renders are deterministic and frame-exact.

Files: `engine/engine.js` (core, global `EV`), `engine/kit.js` (design kit, global `K`), `engine/templates.js` (T08–T17 helpers, `K.T`), `engine/land.js` (world land mask for the T14 globe) and `engine/engine.css`. Start from `template/section/`.

## Section setup (`scenes.js`)
```js
(function () {
  const C = EV, { el, tf, pop, slide, wipe, P, ease, clamp, lerp } = C, k = K;
  const S0 = 1122 / 30;            // section start in the source video (exact frame / 30)
  C.src0 = S0;                     // Eva's footage is read from src0 + t
  C.end = 1088 / 30;               // section length
  const T = s => s - S0;           // convert SRT times (absolute) to local times
  C.evaDir = '../media/eva';
  C.face = { x: .54, y: .35, h: .5 };
  C.evaKeys = [ /* window path */ ];
  C.ringFn = t => ({ color: k.LIME, width: 6, glow: 'rgba(212,255,46,.4)' });
  C.scene({ ... }); C.scene({ ... });
})();
```

## Eva window path
`C.evaKeys = [{ t, d, L: { x, y, w, h, r, s, o } }, ...]`
- `t` is the start time and `d` is the move duration in seconds. Each move eases (quintic) from wherever the window is at `t`.
- `L` gives the window rectangle in stage pixels: `r` is the corner radius (use `w/2` for a circle), `s` is the desired zoom (capped automatically to keep the whole head visible), and `o` is the opacity.
- The first key (`d: 0`) is the starting pose, and it must equal the previous section's final pose.

`C.ringFn(t)` returns `{ color, width, shadow?, glow? }` for the window outline.

## Scenes
```js
C.scene({
  t0: 0, t1: T(48.0),          // active while t0 <= t < t1 (overlap ~0.03 s with the next scene)
  bg: k.NAVY, cls: 'linegrid', // background + optional pattern class: dotgrid | dotgrid-w | linegrid
  z: 1,                        // layer order; Eva window is z 50 (use z 60 to draw over full-bleed Eva)
  quiet: false,                // true = no automatic whoosh at t0
  build(L) { const st = {}; /* create elements once */ return st; },
  update(lt, st, t) { /* set transforms for local time lt / section time t */ },
});
```
Everything is created in `build`. In `update`, only transforms, opacity, text and image sources change, so any frame can render in isolation.

## Core helpers (`EV`)
| Helper | Returns / does |
|---|---|
| `el(parent, tag, cls, style, html)` | creates an element |
| `tf(e, {x, y, s, sx, sy, r, rx, ry, persp, o})` | sets transform and opacity |
| `pop(t, t0, d=.38, k=1.9)` | `{s, o}` overshoot pop that starts at `t0` |
| `slide(t, t0, d, dx, dy)` | `{x, y, o}` slide in from an offset |
| `wipe(e, u, 'l'/'r'/'u'/'d')` | clip-path reveal, `u` from 0 to 1 |
| `P(t, a, d)` | progress from 0 to 1 |
| `ease.outBack/outExpo/out3/io3/smooth5/outElastic` | easing curves |
| `rng(seed)` | deterministic random numbers (never use `Math.random`) |
| `seq(dir, seconds, count)` / `setSrc(img, src)` | image-sequence frame path / load it |

## Kit (`K`)
| Helper | Use |
|---|---|
| `K.LIME RED BLUE INK NAVY CYAN PAPER OR PU WHITE` | palette |
| `K.disp(p, text, color, size, x, y, extra)` | giant condensed English display text |
| `K.cn(p, text, color, size, x, y)` | heavy Chinese text |
| `K.chip(p, text, bg, fg, size, x, y, extra)` | solid label chip |
| `K.hud(p, text, color, x, y, size)` | small mono label |
| `K.card(p, x, y, w, h, bg, extra)` | solid rounded card |
| `K.O(e, origin)` / `K.center(e)` | transform origin / center text horizontally |
| `K.emoji(p, char, size, x, y)` | color emoji |
| `K.svg(p, w, h, x, y)` / `K.sv(svg, tag, attrs)` | SVG drawing |
| `K.screen(p, x, y, w, aspect)` + `K.play(screen, dir, offset, lt, count)` | real screen recording playback |
| `K.imgLayer(p)` | full-frame image layer (e.g. cartoon clip) |
| `K.stageBg`, `K.floor(L, color)` | dark 3D stage + perspective floor |
| `K.symbols(L, seed)` | colored symbol field |
| `K.sunburst(L)` | rotating rays (rotate it in update) |
| `K.confetti(L, n, seed, x0, w)` + `K.burst(c, t, t0)` | celebration |
| `K.note(L, text, x, y, color)` | `ILLUSTRATIVE` label |
| `K.sfx(kind, t, gain, args)` | sound cue: whoosh, pop `{f}`, click, impact, riser, ding `{f}`, applause `{d}` |

## Patterns
**Odometer that rolls to a real number:** one window per digit, each holding a strip of 0–9 that translates to the digit with `ease.outExpo`.
**Flip tiles:** cards with `transformOrigin: 50% 50%`, animated with `sy: ease.outBack(P(t, start + i*.4, .45))`.
**URL typing:** `text.slice(0, floor((t - t0) / .07) + 1)` plus a `▌` cursor, and a click cue per character.
**Stamp:** a rotated red chip with `pop(t, t0, .3, 2.6)` and an `impact` cue.

## Template helpers (`K.T`, engine/templates.js)
Each builder creates elements in `build()`; the matching `*At()` animates them in `update()`. See `template/demo/t08` … `template/demo/t17` for full working sections.

| Template | Builders → animators |
|---|---|
| HUD (T09–T11) | `hudBg`, `hudFrame(L,label,code)`→`hudFrameAt(f,t)`, `title(L,a,hi,x,y,size,col)`, `kicker(L,txt,x,y,col)`; Eva bracket frame: `ringFn = () => ({ width: 0, color: 'transparent', hud: 'rgba(255,255,255,.55)' })` |
| T10 Keynote | `curve`→`curveAt(c,u)`, `odometer(L,text,x,y,size)`→`odometerAt(o,t,t0,d)`, `breaking`, `globe(L,cx,cy,r)`→`globeAt(g,lt,orbitU)`, `orb`, `fileIcon`, `rows(L,x,y,[[icon,name,note]])`, `vs`, `metal(L,txt,y,size)`→`metalAt(m,lt,t0)` |
| T11 Dashboard | `flow`→`flowAt`, `gauge`→`gaugeAt(g,u,val)`, `timer`→`timerAt`, `quote`, `checks`→`checksAt`, `timeline`, `xStamp`, `grid`→`gridAt`, `bars`→`barsAt`, `toggle`→`toggleAt`, `slider`→`sliderAt`, `lines`→`linesAt`, `terminal`→`terminalAt`, `goldStamp`, `version`→`versionAt` |
| T08 Neon | `neonGrade(L)` (a layer with z > 50 over full-bleed Eva), `glow`, `pixel(L,txt,cy,size)`, `echo(L,txt,size,n)`, `article`→`articleAt`, `collage(L,srcs,spots)`→`collageAt`, `bubble`→`bubbleAt`, `slots`→`slotsAt`, `tag`→`tagAt` |
| T12 Newspaper | `NEWS` palette, `newsBg(dark)`, `grain(L,op)`→`grainAt(g,t)`, `masthead`, `columns`, `headline`, `photo(L,src,x,y,w,h,rot)`, `tape`, `filmstrip(L,x,y,srcs,fw,rot)`, `brush(L,txt,x,y,size,rot)`, `scribble(L,'arrow'/'bolt'/'circle'/'x'/'underline',x,y,size)`→`scribbleAt(s,u)`, `typed`→`typedAt`, `cover`, `caption`; Eva window keeps natural colour: `ringFn = () => ({ color: '#f3ecdc', width: 12 })` (an optional `filter` key on ringFn can grade the Eva window, but Eva prefers her real colours) |
| T13 Tech Blue | `TECH` palette, `techBg`, `techFrame(L,opts)`→`techFrameAt(f,u)`, `techTitle(L,title,sub,x,y,size,align)`, `toc(L,[[title,sub]],cy)`→`tocAt(o,t,t0,step)`, `panel(L,x,y,w,h,title,sub)`→`panelAt(p,u)`, `icon(L,'window'/'code'/'play'/'chart'/'cloud'/'doc',x,y,size)`, `colCard(L,x,y,w,h,icon,title,bullets,foot)`, `band(L,src,x,y,w,h)`, `infoCard(L,icon,title,desc,x,y,w)`, `corner(L,x,y,flip)`; Eva: `ringFn = () => ({ color: K.T.TECH.CYAN, width: 2, hud: K.T.TECH.CYAN })` |
| T14 Future | `FUT` palette, `futBg`, `wave(L,{horizon,amp,speed})`→`waveAt(w,t)` (call every frame so the floor keeps moving), `globeT(L,cx,cy,r,{lon0,tilt,speed,orbit})`→`globeTAt(g,t,fadeIn)` (needs `land.js`), `chip(L,cx,cy,size)`→`chipAt(c,t)`, `torus(L,cx,cy,R,r)`→`torusAt(o,t)`, `futTitle(L,l1,l2,cn,x,y,size)`→`futTitleAt(d,t,t0)`, `rules(L,[cn...],x,y,'RULE',size)`→`rulesAt(rows,t,t0,step)` |
| T15 Learning | `LRN` palette, `learnBg`, `sky(L,nStars,seed,clouds)`→`skyAt(o,t)` (call every frame), `bubbly(L,txt,x,y,size,{anchor,font,fill})` (rounded lettering for EN or CN), `book(L,x,y,w,h,col)`, `stairs(L,x,y)`→`stairsAt(bs,t,t0,step)`, `sun(L,cx,cy,r)`→`sunAt(s,t,u)`, `plane(L,pts,size)`→`planeAt(p,u)`, `blob(L,cx,cy,r,col)`, `lIcon(L,'openbook'/'bulb'/'pencil'/'notebook',cx,cy,size)`, `rays`, `dashArc`→`dashArcAt`, `bigBook(L,cx,baseY,w)`→`bigBookAt(o,t,u)`, `goal(L,txt,x,y,col,rot)` |
| T16 Comic | `CMC` palettes (`GREEN`, `YELLOW`, `BLUE`, `PURPLE`, `CYAN`, `LIME` = [dark, light]), `burst(L,cx,cy,pal,clip,{rays,dots,glow})`→`burstAt(b,t,speed)` (call every frame), `zigzag(L,pts)` (returns `left`/`right` clip polygons for a split screen), `comicCloud(L,x,y,w,seed)`→`cloudAt(c,t,amp)`, `cStar(L,cx,cy,r,col)`, `action(L,cx,cy,r,angles)`, `comicText(L,txt,x,y,size,fill,{anchor,font,rot})`, `speechCloud(L,cx,cy,w,txt,size)`, `sparkles(L,n)`→`sparklesAt(a,t)`, `cloudGround(L,y,n)`, `sticker(L,txt,x,y,bg,rot)`; Eva: `ringFn = () => ({ color: '#111', width: 9 })` |
| T17 Science | `SCN` palette, `sciNetBg`, `bokeh(L,n,seed)`→`bokehAt(o,t)`, `ribbon(L,{y,amp,width,cols,rows})`→`ribbonAt(r,t)`, `pSphere(L,cx,cy,r,{n,land,speed,lon0,tilt})`→`pSphereAt(s,t,fade)` (`land:true` needs `land.js`), `tunnel(L,cx,cy,{rmax,speed})`→`tunnelAt(o,t)`, `sciHead(L,['LINE','[CYAN] WORD'],sub,x,y,size)`→`sciHeadAt(h,t,t0)`; call every `*At` each frame so the networks keep moving |
| T09 Wall | 3D tile wall (see `template/demo/t09`), `odometer`, iris wipe + `metal` sparks, title + gold tagline |
