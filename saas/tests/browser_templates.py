#!/usr/bin/env python3
"""Template Gallery + Plans (concept) in a real browser.   python3 saas/tests/browser_templates.py SITE
Gallery: every catalog template shown once with its original ID; exactly the 5 launch templates are "Available" and the
only ones with "Use template" (which preselects it in the studio); all others Preview only / Coming soon; search
(name, ID, Chinese name, use) and categories filter, URL keeps the state; images lazy; no overflow on phone.
Plans: monthly/yearly prices (yearly = 20% off, billed upfront), every subscription/pack button disabled except the live
$9.99 pack (existing checkout), concept banner shown.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = sys.argv[1].rstrip("/"); fails, errs = [], []
CAT = json.loads((Path(__file__).resolve().parents[2] / "site/templates/catalog.json").read_text())
LAUNCH = ["T23", "T21", "T17", "T02", "T01"]
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", {"width": 1366, "height": 900}), ("phone", {"width": 390, "height": 844})):
        pg = b.new_page(viewport=vp); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(SITE + "/templates.html"); pg.wait_for_selector(".g-card")
        ids = pg.eval_on_selector_all(".g-card", "x => x.map(c => c.dataset.id)")
        check(sorted(ids) == sorted(t["id"] for t in CAT["templates"]) and len(ids) == len(set(ids)), f"{name}: all {len(ids)} templates, original IDs, once each")
        av = pg.eval_on_selector_all(".g-card.available", "x => x.map(c => c.dataset.id)")
        check(av == LAUNCH, f"{name}: exactly the launch templates are Available, listed first ({av})")
        use = pg.eval_on_selector_all(".g-card a.btn", "x => x.map(a => a.closest('.g-card').dataset.id)")
        check(sorted(use) == sorted(LAUNCH), f"{name}: 'Use template' only on selectable templates")
        badges = pg.eval_on_selector_all(".g-card:not(.available) .g-badge", "x => [...new Set(x.map(b => b.textContent))]")
        check(set(badges) <= {"Preview only", "Coming soon"}, f"{name}: others marked {badges}")
        check(pg.eval_on_selector_all(".g-media img", "x => x.every(i => i.loading === 'lazy')"), f"{name}: images lazy-loaded")
        check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name}: no horizontal overflow")
        if name == "desktop":
            for q, want in (("T17", ["T17"]), ("房产", ["T28"]), ("newspaper", ["T12"])):
                pg.fill("#gQ", q); pg.wait_for_timeout(300)
                got = pg.eval_on_selector_all(".g-card", "x => x.map(c => c.dataset.id)"); check(got == want, f"search '{q}' → {got}")
            pg.fill("#gQ", ""); pg.wait_for_timeout(300); pg.click("[data-cat=edu]"); pg.wait_for_timeout(200)
            got = pg.eval_on_selector_all(".g-card", "x => x.map(c => c.dataset.id)")
            check(set(got) == {t["id"] for t in CAT["templates"] if "edu" in t["categories"]} and "cat=edu" in pg.url, f"category Education → {got}, URL keeps it")
            pg.goto(SITE + "/templates.html"); pg.wait_for_selector(".g-card[data-id=T21] a.btn"); pg.click(".g-card[data-id=T21] a.btn"); pg.wait_for_timeout(2500)
            sel = pg.eval_on_selector_all("[name=tpl]:checked", "x => x.map(i => i.value)")
            check(sel == ["T21"], f"'Use template' T21 → studio with T21 selected ({sel})")
            pg.goto(SITE + "/?tpl=T05#studio"); pg.wait_for_timeout(2000)
            sel = pg.eval_on_selector_all("[name=tpl]:checked", "x => x.map(i => i.value)")
            check("T05" not in sel, f"non-selectable template cannot be preselected ({sel})")
        pg.goto(SITE + "/plans.html"); pg.wait_for_selector(".p-card")
        m = pg.eval_on_selector_all(".p-card .p-price b", "x => x.map(e => e.textContent)")
        check(m == ["$19.99", "$39.99", "$79.99"], f"{name}: monthly {m}")
        pg.click("[data-period=year]"); pg.wait_for_timeout(200)
        y = pg.eval_on_selector_all(".p-card .p-bill", "x => x.map(e => e.textContent.split(' ')[0])")
        check(y == ["$191.88", "$383.88", "$767.88"], f"{name}: yearly billed upfront {y}")
        dis = pg.eval_on_selector_all(".p-card button, .p-pack button", "x => x.length > 0 && x.every(b => b.disabled)")
        live = pg.eval_on_selector_all("main a.btn", "x => x.map(a => a.getAttribute('href'))")
        check(dis and set(live) == {"account.html#billing"}, f"{name}: subscriptions + new packs disabled; only the existing $9.99 checkout is live")
        check(pg.is_visible(".concept"), f"{name}: concept banner shown")
        pg.close()
    b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser templates:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
