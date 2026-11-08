#!/usr/bin/env python3
"""Template Gallery in a real browser (local stack or staging site).

    python3 saas/tests/browser_gallery.py SITE OUT_DIR

For 9:16 and 16:9: every selectable template card shows its WebP (loaded, right orientation), ▶ plays the 5 s demo
(muted, time advances, toggles off), "Full preview" opens the 15 s demo in a dialog and plays, playing never changes
the template selection, T19 is absent, signed links answer 200. Phone width: no horizontal overflow. Gallery API down:
plain chips, studio still usable. No page errors. Screenshots + summary.json in OUT_DIR.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

site, out = sys.argv[1].rstrip("/"), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
R, errors, fails = {}, [], []
G = json.loads((Path(__file__).resolve().parents[1] / "web/gallery.json").read_text())
PENDING = {(t["id"], ar) for t in G["templates"] for ar, a in t["assets"].items() if a["status"] != "approved"}
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(site + "/"); pg.wait_for_selector(".tplcard.has-media img", timeout=15000)
    for ar in ("9:16", "16:9"):
        pg.check(f"[name=aspect][value='{ar}']"); pg.wait_for_timeout(800)
        ids = pg.eval_on_selector_all(".tplcard", "cs => cs.map(c => c.dataset.tpl)")
        check("T19" not in ids and len(ids) == 5, f"{ar}: 5 template cards, no T19 ({ids})")
        for tid in ids:
            c = f".tplcard[data-tpl={tid}]"
            pending = (tid, ar) in PENDING
            info = pg.eval_on_selector(c, """c => { const i = c.querySelector('.tplplay img'); return i && { w: i.naturalWidth, h: i.naturalHeight,
                      wide: c.querySelector('.tplmedia').classList.contains('wide'), src: i.src } }""")
            if pending:   # no approved asset for this aspect: no picture/video at all, a "coming soon" card, still selectable
                s_ = pg.eval_on_selector(c, """c => ({ media: !c.querySelector('.tplmedia').hidden, vids: c.querySelectorAll('video, img').length,
                         soon: !c.querySelector('.tplsoon').hidden && c.querySelector('.tplsoon').textContent,
                         wide: c.querySelector('.tplsoon').classList.contains('wide'), full: !c.querySelector('.tplfull').hidden })""")
                check(not s_["media"] and s_["vids"] == 0 and not s_["full"] and s_["soon"] == f"{ar} preview coming soon" and s_["wide"] == (ar == "16:9"),
                      f"{ar} {tid}: pending — no other-aspect demo shown, '{s_['soon']}' card")
                pg.check(f"{c} [name=tpl]"); check(pg.is_checked(f"{c} [name=tpl]"), f"{ar} {tid}: still selectable")
                R[f"{ar} {tid}"] = {"pending": True}; continue
            check(bool(info and info["w"] > 0), f"{ar} {tid}: WebP thumbnail loaded {info and (info['w'], info['h'])}")
            if not info: continue
            check(info["wide"] == (ar == "16:9") == (info["w"] > info["h"]), f"{ar} {tid}: card, thumbnail and chosen aspect agree ({info['w']}x{info['h']})")
            R[f"{ar} {tid}"] = {"thumb": [info["w"], info["h"]], "orientation": "16:9" if info["wide"] else "9:16"}
            before = pg.is_checked(f"{c} [name=tpl]")
            pg.click(f"{c} .tplplay"); pg.wait_for_timeout(1800)
            v = pg.eval_on_selector(c, "c => { const v = c.querySelector('.tplplay video'); return v && { t: v.currentTime, muted: v.muted, d: v.duration } }")
            check(bool(v and v["t"] > .5 and v["muted"] and abs(v["d"] - 5) < .1), f"{ar} {tid}: 5 s demo plays muted ({v})")
            check(pg.is_checked(f"{c} [name=tpl]") == before, f"{ar} {tid}: playing does not change the selection")
            pg.click(f"{c} .tplplay"); pg.wait_for_timeout(200)
            check(pg.eval_on_selector(c, "c => !c.querySelector('.tplplay video')"), f"{ar} {tid}: second tap stops the demo")
            pg.click(f"{c} .tplfull"); pg.wait_for_timeout(2000)
            d = pg.evaluate("() => { const v = document.querySelector('.tpldlg video'); return { open: document.querySelector('.tpldlg').open, t: v.currentTime, d: v.duration } }")
            check(d["open"] and d["t"] > .5 and abs(d["d"] - 15.03) < .15, f"{ar} {tid}: full 15 s preview plays in the dialog ({d})")
            if tid == ids[0]: pg.screenshot(path=str(out / f"dialog_{ar.replace(':', 'x')}.png"))
            pg.click(".tpldlg .btn"); pg.wait_for_timeout(200)
        el = pg.query_selector("#tplChips"); el.scroll_into_view_if_needed(); el.screenshot(path=str(out / f"gallery_{ar.replace(':', 'x')}.png"))
    urls = pg.evaluate("async () => { const j = await (await fetch((window.EVA_API||'') + '/api/v2/gallery')).json(); return j.templates.flatMap(t => Object.values(t.assets).flatMap(a => Object.values(a).map(x => x.url))) }")
    codes = [pg.request.get(u).status for u in urls]
    check(all(c == 200 for c in codes) and len(codes) == 27, f"all {len(codes)} signed gallery links (27 approved) answer 200")
    # phone width
    m = b.new_page(viewport={"width": 390, "height": 844}); m.on("pageerror", lambda e: errors.append(str(e)))
    m.goto(site + "/"); m.wait_for_selector(".tplcard.has-media img", timeout=15000)
    ov = m.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
    check(ov <= 0, f"phone width: no horizontal overflow ({ov}px)")
    m.query_selector("#tplChips").screenshot(path=str(out / "gallery_phone.png"))
    # gallery API down → plain chips
    f = b.new_page(); f.route("**/api/v2/gallery", lambda r: r.abort()); f.goto(site + "/"); f.wait_for_timeout(1500)
    chips = f.eval_on_selector_all(".tplcard [name=tpl]", "x => x.length"); media = f.eval_on_selector_all(".tplcard.has-media", "x => x.length")
    check(chips == 5 and media == 0, f"gallery unavailable: {chips} plain template chips, studio usable")
    b.close()
check(not errors, f"no page errors {errors[:3]}")
R["fails"] = fails; (out / "summary.json").write_text(json.dumps(R, indent=1))
print("browser gallery:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
