#!/usr/bin/env python3
"""Account menu + My Account page in a real browser against the local stack (EVA_LOCAL_AUTH), desktop and phone width.

    python3 saas/tests/browser_account.py SITE API OUT_DIR
Checks: signed out → "Sign in" button; signed in → avatar with the initial, menu (My Account, My Videos, Credits & Billing,
Sign Out), session survives reload; My Account shows email, credits, free previews x/3, purchase history; display name
changes the avatar initial; My Videos with the account service down says "couldn't load" (not "Sign in"); Sign Out works;
no horizontal overflow; no page errors.
"""
import json, sys, uuid
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

SITE, API, OUT = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"), Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
fails, errs = [], []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

email = f"acct-{uuid.uuid4().hex[:6]}@example.com"
tok = requests.get(f"{API}/_local_signin", params={"email": email}).json()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", {"width": 1280, "height": 900}), ("phone", {"width": 390, "height": 844})):
        ctx = b.new_context(viewport=vp); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(SITE + "/"); pg.wait_for_selector(".top nav .acct a.signin", timeout=10000)
        check(pg.is_visible(".top nav .acct a.signin"), f"{name}: signed out → Sign in button")
        pg.evaluate(f"localStorage.setItem('eva:auth', {json.dumps(json.dumps(tok))})")
        pg.goto(SITE + "/account.html"); pg.wait_for_selector(".acard .stats", timeout=15000)
        check((pg.text_content(".avatar") or "") == email[0].upper(), f"{name}: avatar shows the email initial ({pg.text_content('.avatar')})")
        check(email not in (pg.text_content(".top nav") or "").replace(pg.text_content(".acctmenu") or "", ""), f"{name}: full email not in the nav bar")
        txt = pg.text_content("#acctBody")
        check(email in txt and "credits" in txt and "/3" in txt, f"{name}: My Account shows email, credits, free previews x/3")
        pg.wait_for_selector(".hist table, .hist p", timeout=10000)
        check(pg.query_selector(".hist p.note.bad") is None, f"{name}: purchase history loads")
        pg.click(".avatar"); items = pg.eval_on_selector_all(".acctmenu a", "x => x.map(a => a.textContent)")
        check(items == ["My Account", "My Videos", "Credits & Billing", "Sign Out"], f"{name}: menu {items}")
        pg.keyboard.press("Escape"); check(pg.is_hidden(".acctmenu"), f"{name}: Escape closes the menu")
        check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name}: no horizontal overflow")
        pg.reload(); pg.wait_for_selector(".avatar", timeout=10000); check(True, f"{name}: session persists after reload")
        if name == "desktop":
            pg.fill(".kv input", "Zoe"); pg.click(".kv .btn"); pg.wait_for_timeout(800)
            check(pg.text_content(".avatar") == "Z", "display name sets the avatar initial (Z)")
            pg.route("**/api/v2/me", lambda r: r.fulfill(status=503, body='{"error":"unavailable"}', content_type="application/json"))
            pg.goto(SITE + "/videos.html"); pg.wait_for_timeout(1500)
            sub = pg.text_content("#libSub") or ""
            check("couldn't load" in sub and "Sign in" not in sub and pg.is_visible(".avatar"),
                  f"My Videos, signed in but account service down: '{sub}' (not asked to sign in)")
            pg.unroute("**/api/v2/me")
        pg.goto(SITE + "/videos.html"); pg.wait_for_selector(".avatar", timeout=10000)
        check("Sign in to see" not in (pg.text_content("#libSub") or ""), f"{name}: My Videos agrees with the header (signed in)")
        pg.screenshot(path=str(OUT / f"videos_{name}.png"))
        pg.click(".avatar"); pg.click(".acctmenu .signout"); pg.wait_for_timeout(1200)
        check(pg.is_visible(".top nav .acct a.signin"), f"{name}: Sign Out → signed out")
        ctx.close()
    b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser account:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
