#!/usr/bin/env python3
"""Homepage hero + brand in a real browser: both Before/After comparisons at once (9:16 phone frame, 16:9 landscape frame),
frame aspect == video aspect (no stretch/crop), Raw upload left, Eva's style-showcase montage right (demos.json
hero.showcase), both play muted and loop independently, slider moves, Preview Only note; header logo keeps its proportions; /favicon.ico is the tab icon;
desktop side by side, phone stacked, no horizontal overflow.   python3 saas/tests/browser_hero.py SITE OUT_DIR
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE, OUT = sys.argv[1].rstrip("/"), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
fails, errs = [], []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for name, vp in (("desktop", {"width": 1366, "height": 860}), ("phone", {"width": 390, "height": 844})):
        pg = b.new_page(viewport=vp); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(SITE + "/"); pg.wait_for_timeout(3000)
        for fid, want in (("heroV", 9 / 16), ("heroH", 16 / 9)):
            pg.locator(f"#{fid}").scroll_into_view_if_needed(); pg.wait_for_timeout(2500)
            r = pg.evaluate(f"""() => {{ const p = document.getElementById('{fid}'), r = p.getBoundingClientRect(), v = [...p.querySelectorAll('video')];
                 return {{ box: r.width / r.height, vids: v.map(x => [x.videoWidth, x.videoHeight, x.currentTime, x.getAttribute('src')]) }} }}""")
            ok = len(r["vids"]) == 2 and all(w and abs(w / h - want) < .01 for w, h, _, _ in r["vids"]) and abs(r["box"] - want) < .01
            check(ok, f"{name} {fid}: frame {r['box']:.4f} = video aspect {want:.4f}, Raw + Edit {[(w, h) for w, h, _, _ in r['vids']]}")
            srcs = [s for *_, s in r["vids"]]   # right side = Eva's approved style-showcase montage (demos/showcase/), Raw unchanged
            check(len(srcs) == 2 and srcs[0].endswith("/before.mp4") and srcs[1] == ("demos/showcase/styles-9x16.mp4" if fid == "heroV" else "demos/showcase/styles-16x9.mp4"),
                  f"{name} {fid}: Raw upload left, Style Showcase montage right ({srcs})")
            tags = pg.eval_on_selector_all(f"#{fid} .tag", "x => x.map(t => t.textContent)")
            check(tags == ["Raw", "Style Showcase"], f"{name} {fid}: labels {tags}, no sound button")
            check(pg.evaluate(f"[...document.querySelectorAll('#{fid} video')].every(v => v.muted && v.loop)"), f"{name} {fid}: both muted and looping")
            check(all(t > .1 for _, _, t, _ in r["vids"]), f"{name} {fid}: both play ({[round(t, 2) for _, _, t, _ in r['vids']]})")
        if name == "desktop":
            v, h = pg.locator("#heroV").bounding_box(), pg.locator("#heroH").bounding_box()
            check(v["x"] + v["width"] <= h["x"] and v["y"] < 860 and h["y"] < 860, "desktop: both comparisons visible side by side above the fold")
            box = h; pg.mouse.move(box["x"] + box["width"] * .5, box["y"] + box["height"] * .5); pg.mouse.down()
            pg.mouse.move(box["x"] + box["width"] * .25, box["y"] + box["height"] * .5); pg.mouse.up()
            check(pg.evaluate("getComputedStyle(document.getElementById('heroH')).getPropertyValue('--split').trim()").startswith("2"), "16:9 slider drags")
            t0 = pg.evaluate("[...document.querySelectorAll('#heroH video')].map(v => v.currentTime)"); pg.wait_for_timeout(5600)
            t1 = pg.evaluate("[...document.querySelectorAll('#heroH video')].map(v => v.currentTime)")
            check(t1[0] != t1[1], f"Raw (5.06 s) and Style Showcase (8.3 s) loop independently ({[round(x, 2) for x in t0]} → {[round(x, 2) for x in t1]})")
            check("Preview Only" in pg.text_content(".wipe-hint"), "hint explains the montage and that some styles are Preview Only")
            logo = pg.evaluate("() => { const i = document.querySelector('.logo img'); return [i.naturalWidth / i.naturalHeight, i.clientWidth / i.clientHeight, i.currentSrc.split('/').pop()] }")
            check(abs(logo[0] - logo[1]) < .02, f"header logo keeps its proportions ({logo[1]:.3f} vs {logo[0]:.3f}, {logo[2]})")
            ico = pg.evaluate("() => [...document.querySelectorAll('link[rel~=icon]')].map(l => l.getAttribute('href'))")
            st = pg.request.get(SITE + "/favicon.ico")
            check(ico == ["/favicon.ico"] and st.status == 200 and st.body()[:4] == b"\x00\x00\x01\x00", f"favicon: only /favicon.ico referenced, served as ICO ({ico}, {st.status})")
        else:
            v, h = pg.locator("#heroV").bounding_box(), pg.locator("#heroH").bounding_box()
            check(h["y"] >= v["y"] + v["height"], "phone: comparisons stacked")
        check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name}: no horizontal overflow")
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(600); pg.screenshot(path=str(OUT / f"hero_{name}.png"))
        pg.close()
    for page in ("video.html", "videos.html", "legal.html", "account.html"):
        pg = b.new_page(); pg.goto(f"{SITE}/{page}")
        ico = pg.evaluate("() => [...document.querySelectorAll('link[rel~=icon]')].map(l => l.getAttribute('href'))")
        check(ico == ["/favicon.ico"] and pg.is_visible(".logo img"), f"{page}: new logo + /favicon.ico"); pg.close()
    b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser hero:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
