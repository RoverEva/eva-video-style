#!/usr/bin/env python3
"""Desktop + phone screenshots of the staging site's Gallery and Plans pages (for review).  staging_shots.py SITE OUT_DIR"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
site, out = sys.argv[1].rstrip("/"), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", {"width": 1366, "height": 900}), ("phone", {"width": 390, "height": 844})):
        pg = b.new_page(viewport=vp)
        pg.goto(site + "/templates.html"); pg.wait_for_selector(".g-card"); pg.wait_for_timeout(2500)
        pg.screenshot(path=str(out / f"gallery_{name}.png"), full_page=True)
        pg.goto(site + "/plans.html"); pg.wait_for_selector(".p-card"); pg.wait_for_timeout(800)
        pg.screenshot(path=str(out / f"plans_{name}_monthly.png"), full_page=True)
        pg.click("[data-period=year]"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / f"plans_{name}_yearly.png"), full_page=True)
        pg.close()
    b.close()
print("screenshots:", sorted(x.name for x in out.glob("*.png")))
