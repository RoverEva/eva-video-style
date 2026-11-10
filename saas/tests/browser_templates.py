#!/usr/bin/env python3
"""Template Gallery, public Pricing and internal Plans concept in a real browser.   browser_templates.py SITE
Gallery: all catalog templates with original IDs; 5 launch templates first and the only ones "Available" / with
Use template (which preselects it in the studio); cards show only thumbnail + name + status (+ small ID); paging 24 on
desktop / 12 on phones with Load more; works with 120 templates; one filter menu + search, state in the URL; lazy
thumbnails; no video until the person presses play; detail modal opens/closes; no sideways scroll.
Pricing: the real one-time $9.99 / 100 credits offer, 3 free previews, no subscription prices, FAQs collapsed.
Plans concept (internal): approved prices, all subscription buttons disabled.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = sys.argv[1].rstrip("/"); fails, errs = [], []
CAT = json.loads((Path(__file__).resolve().parents[2] / "site/templates/catalog.json").read_text())
CAT["templates"] = [x for x in CAT["templates"] if x["status"] != "excluded"]   # T08 excluded by Eva
LAUNCH = ["T23", "T21", "T17", "T02", "T01"]
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)
ids_of = lambda pg: pg.eval_on_selector_all(".g-card", "x => x.map(c => c.dataset.id)")

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp, page in (("desktop", {"width": 1366, "height": 900}, 24), ("phone", {"width": 390, "height": 844}, 12)):
        pg = b.new_page(viewport=vp); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(SITE + "/templates.html"); pg.wait_for_selector(".g-card")
        ids = ids_of(pg)
        check(len(ids) == min(page, len(CAT["templates"])) and ids[:5] == LAUNCH, f"{name}: first page = {len(ids)} cards, launch templates first {ids[:5]}")
        if not pg.is_hidden("#gMore"): pg.click("#gMore"); pg.wait_for_timeout(200)
        while not pg.is_hidden("#gMore"): pg.click("#gMore"); pg.wait_for_timeout(200)
        ids = ids_of(pg)
        check(sorted(ids) == sorted(t["id"] for t in CAT["templates"]) and len(set(ids)) == len(ids) and len(ids) == 25 and "T08" not in ids, f"{name}: Load more reaches all {len(ids)} templates, each once, T08 not shown")
        st = pg.eval_on_selector_all(".g-card", "x => x.map(c => c.dataset.id + '=' + c.querySelector('.g-st').textContent)")
        check(all((s.split('=')[1] == "Available") == (s.split('=')[0] in LAUNCH) for s in st), f"{name}: only the launch templates say Available")
        kids = pg.eval_on_selector_all(".g-card", "x => [...new Set(x.map(c => [...c.children].map(k => k.className.split(' ')[0]).join(',')))]")
        check(kids == ["g-media,g-id,g-name,g-st"], f"{name}: cards hold only thumbnail, ID, name, status {kids}")
        check(pg.eval_on_selector_all(".g-media img", "x => x.every(i => i.loading === 'lazy')") and pg.eval_on_selector_all("video", "x => x.length") == 0,
              f"{name}: lazy thumbnails, no video loaded in the grid")
        check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name}: no horizontal overflow")
        cols = pg.evaluate("getComputedStyle(document.querySelector('.g-grid')).gridTemplateColumns.split(' ').length")
        check((cols == 2) if name == "phone" else (4 <= cols <= 5), f"{name}: {cols} columns")
        # modal: available template
        pg.click(".g-card[data-id=T17]"); pg.wait_for_selector("#gDlg[open]")
        m = pg.evaluate("() => ({ h: document.querySelector('.gd-head h2').textContent, desc: document.querySelector('.gd-desc').textContent, use: [...document.querySelectorAll('#gDlg a.btn')].map(a => a.getAttribute('href')) })")
        check(m["h"] == "Science Network" and len(m["desc"]) > 20 and m["use"] == ["/?tpl=T17#studio"], f"{name}: T17 modal: description + Use template {m['use']}")
        if name == "desktop": pg.screenshot(path="/tmp/gal_modal_desktop.png")
        pg.click("#gDlg .gd-close"); check(pg.is_hidden("#gDlg"), f"{name}: modal closes")
        pg.click(".g-card[data-id=T05]"); pg.wait_for_selector("#gDlg[open]")
        m = pg.evaluate("() => ({ use: document.querySelectorAll('#gDlg a.btn').length, txt: document.querySelector('.gd-acts').textContent })")
        check(m["use"] == 0 and "Preview only" in m["txt"], f"{name}: T05 modal: Preview only, no Use template")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(150); check(pg.is_hidden("#gDlg"), f"{name}: Escape closes the modal")
        if name == "phone": pg.click(".g-card[data-id=T28]"); pg.wait_for_selector("#gDlg[open]"); pg.screenshot(path="/tmp/gal_modal_phone.png"); pg.keyboard.press("Escape")
        if name == "desktop":
            for q, want in (("T17", ["T17"]), ("房产", ["T28"]), ("newspaper", ["T12"])):
                pg.fill("#gQ", q); pg.wait_for_timeout(300); got = ids_of(pg); check(got == want, f"search '{q}' → {got}")
            pg.fill("#gQ", ""); pg.wait_for_timeout(300); pg.select_option("#gCat", "edu"); pg.wait_for_timeout(200)
            got = ids_of(pg); check(set(got) == {t["id"] for t in CAT["templates"] if "edu" in t["categories"]} and "cat=edu" in pg.url, f"filter Education → {got}, kept in the URL")
            pg.select_option("#gCat", "available"); pg.wait_for_timeout(200); check(ids_of(pg) == LAUNCH, "filter Available now → the 5 launch templates")
            pg.goto(SITE + "/templates.html"); pg.wait_for_selector(".g-card[data-id=T21]"); pg.click(".g-card[data-id=T21]"); pg.click("#gDlg a.btn"); pg.wait_for_timeout(2500)
            sel = pg.eval_on_selector_all("[name=tpl]:checked", "x => x.map(i => i.value)"); check(sel == ["T21"], f"Use template T21 → studio with T21 selected ({sel})")
            pg.goto(SITE + "/?tpl=T05#studio"); pg.wait_for_timeout(2000)
            sel = pg.eval_on_selector_all("[name=tpl]:checked", "x => x.map(i => i.value)"); check("T05" not in sel, f"non-selectable template cannot be preselected ({sel})")
            # scale: 120 templates
            big = dict(CAT, templates=CAT["templates"] + [dict(CAT["templates"][5], id=f"X{i:03}", status="soon", thumb=None, launch_order=None) for i in range(120 - len(CAT["templates"]))])
            pg.route("**/templates/catalog.json", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(big)))
            pg.goto(SITE + "/templates.html"); pg.wait_for_selector(".g-card"); n1 = len(ids_of(pg)); pg.click("#gMore"); pg.wait_for_timeout(200); n2 = len(ids_of(pg))
            check(n1 == 24 and n2 == 48 and "120 templates" in pg.text_content("#gCount"), f"120 templates: {n1} → {n2} after Load more ({pg.text_content('#gCount')})")
            pg.unroute("**/templates/catalog.json")
        # public pricing
        pg.goto(SITE + "/pricing.html"); pg.wait_for_selector(".pr-offer")
        t = pg.text_content("main")
        check("$9.99" in t and "100 credits" in t and "One-time payment" in t and "3 free previews" in t, f"{name}: pricing shows the one-time $9.99 / 100 credits and 3 free previews")
        check(not any(x in t for x in ("$19.99", "$39.99", "/month", "250 credits", "550 credits")), f"{name}: no subscription prices on the public page")
        opn = pg.eval_on_selector_all(".pr-faq details", "x => x.filter(d => d.open).length")
        pg.click(".pr-faq summary >> nth=0"); now = pg.eval_on_selector_all(".pr-faq details", "x => x.filter(d => d.open).length")
        check(opn == 0 and now == 1, f"{name}: FAQs collapsed, open on tap")
        check(pg.eval_on_selector_all("main a.btn", "x => x.map(a => a.getAttribute('href'))") == ["account.html#billing"], f"{name}: one buy button → the existing checkout")
        check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name}: pricing, no horizontal overflow")
        # internal concept
        pg.goto(SITE + "/plans.html"); pg.wait_for_selector(".p-card")
        m = pg.eval_on_selector_all(".p-card .p-price b", "x => x.map(e => e.textContent)")
        check(m == ["$19.99", "$39.99", "Coming soon"], f"{name}: concept monthly {m}")
        pg.click("[data-period=year]"); pg.wait_for_timeout(200)
        y = pg.eval_on_selector_all(".p-card:not(.soon) .p-bill", "x => x.map(e => e.textContent.split(' ')[0])")
        check(y == ["$191.88", "$383.88"], f"{name}: concept yearly billed upfront {y}")
        check(pg.eval_on_selector_all(".p-card button", "x => x.length == 3 && x.every(b => b.disabled)") and
              pg.evaluate("document.querySelector('meta[name=robots]').content").startswith("noindex"), f"{name}: concept buttons disabled, page noindex")
        pg.close()
    b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser templates:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
