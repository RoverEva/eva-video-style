#!/usr/bin/env python3
"""Website language (English default / 简体中文) in a real browser.   browser_i18n.py SITE [--local-auth API]
English by default with <html lang=en>; the 🌐 switcher in the header opens ✓ English / 简体中文; choosing 简体中文 keeps it
across navigation and reloads (localStorage) and switching back restores English; every public page has the switcher and
no sideways scroll on phones; in Chinese the main customer text is translated (leftover English sentences are listed),
while template IDs stay as they are. --local-auth also checks the signed-in My Account / My Videos pages (local stack)."""
import re, sys
from playwright.sync_api import sync_playwright

SITE = sys.argv[1].rstrip("/"); LOCAL = sys.argv[sys.argv.index("--local-auth") + 1].rstrip("/") if "--local-auth" in sys.argv else None
fails, errs = [], []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)
PAGES = ["/", "/templates.html", "/pricing.html", "/videos.html", "/account.html"]
# English that may stay in Chinese mode: brand, product names, template names/IDs, formats, platform names
KEEP = re.compile(r"EVA|Video Studio|Reels|TikTok|Shorts|YouTube|Stripe|Creator|Pro\b|MP4|MOV|HD|AI|T\d\d|you@example\.com|"
                  r"Creative Pop|Clean & Minimal|Sci-Fi Network|Electric Blue|Bold Lime|Bright Pop|Calm Lo-fi|Inspire|Luxury Ambient|English")
LEFT_JS = """() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode, p = n.parentElement; if (!p || p.closest('script,style,[hidden],dialog:not([open]),[data-no-i18n]')) continue;
    const r = p.getBoundingClientRect(); if (!r.width || !r.height) continue; const s = n.nodeValue.trim(); if (/[A-Za-z]{3,} [A-Za-z]{3,}/.test(s)) out.push(s); }
  return out; }"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", {"width": 1366, "height": 900}), ("phone", {"width": 390, "height": 844})):
        ctx = b.new_context(viewport=vp); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(SITE + "/"); pg.wait_for_selector(".langbtn")
        check(pg.evaluate("document.documentElement.lang") == "en" and pg.text_content(".langbtn").strip() == "EN" and "How EVA works" in pg.text_content("#how"),
              f"{name}: English by default, switcher shows EN")
        pg.click(".langbtn"); items = pg.eval_on_selector_all(".langmenu [data-l]", "x => x.map(b => b.textContent + (b.getAttribute('aria-checked') === 'true' ? '✓' : ''))")
        check(items == ["English✓", "简体中文"], f"{name}: menu {items}")
        pg.click(".langmenu [data-l=zh]"); pg.wait_for_load_state("load"); pg.wait_for_selector(".langbtn"); pg.wait_for_timeout(1500)
        check(pg.evaluate("document.documentElement.lang") == "zh-CN" and "EVA 如何工作" in pg.text_content("#how") and pg.text_content(".langbtn").strip() == "中文",
              f"{name}: 简体中文 applied on the homepage")
        tiles = pg.eval_on_selector_all(".how-tile .how-nm b", "x => x.map(e => e.textContent)")
        check(len(tiles) == 6 and all(re.fullmatch(r"T\d\d", t) for t in tiles), f"{name}: template IDs unchanged in Chinese {tiles}")
        for path in PAGES:
            pg.goto(SITE + path); pg.wait_for_selector(".langbtn"); pg.wait_for_timeout(1800)
            left = [s for s in pg.evaluate(LEFT_JS) if not KEEP.fullmatch(s) and len(KEEP.sub("", s).strip(" ·:,.→+—-()")) > 6 and re.search(r"[A-Za-z]{3,} [A-Za-z]{3,}", KEEP.sub("", s))]
            check(pg.evaluate("document.documentElement.lang") == "zh-CN" and not left, f"{name} zh {path}: kept Chinese, untranslated: {left[:6]}")
            check(pg.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{name} zh {path}: no horizontal overflow")
            if name == "phone": check(pg.evaluate("document.querySelector('.top').getBoundingClientRect().height") < 90, f"phone zh {path}: header stays one compact row")
        pg.reload(); pg.wait_for_selector(".langbtn"); check(pg.text_content(".langbtn").strip() == "中文", f"{name}: Chinese survives a reload")
        if LOCAL:
            import json, urllib.request
            tok = json.loads(urllib.request.urlopen(LOCAL + "/_local_signin?email=i18n%40example.com").read())
            pg.evaluate("t => localStorage.setItem('eva:auth', t)", json.dumps(tok))
            for path, want in (("/account.html", "点数与账单"), ("/videos.html", "我的视频")):
                pg.goto(SITE + path); pg.wait_for_selector(".avatar"); pg.wait_for_timeout(2000)
                left = [s for s in pg.evaluate(LEFT_JS) if not KEEP.fullmatch(s) and re.search(r"[A-Za-z]{3,} [A-Za-z]{3,}", KEEP.sub("", s))]
                check(want in pg.text_content("main") and not left, f"{name} zh signed-in {path}: untranslated: {left[:6]}")
            pg.click(".avatar"); m = pg.text_content(".acctmenu"); check("我的账户" in m and "退出登录" in m, f"{name}: account menu in Chinese")
            pg.evaluate("localStorage.removeItem('eva:auth')")
        pg.goto(SITE + "/pricing.html"); pg.wait_for_selector(".langbtn"); pg.click(".langbtn"); pg.click(".langmenu [data-l=en]")
        pg.wait_for_load_state("load"); pg.wait_for_selector(".langbtn"); pg.wait_for_timeout(500)
        check(pg.evaluate("document.documentElement.lang") == "en" and "Simple pricing" in pg.text_content("main"), f"{name}: back to English")
        pg.goto(SITE + "/?lang=zh"); pg.wait_for_selector(".langbtn"); check(pg.text_content(".langbtn").strip() == "中文", f"{name}: ?lang=zh link opens Chinese")
        pg.goto(SITE + "/?lang=en"); ctx.close()
    b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser i18n:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
