#!/usr/bin/env python3
"""Account journey in a real browser against the local stack (stand-in sign-in, fake Stripe top-up page):
sign in → upload + free preview (cost shown) → My Videos → new version → top up and return → HD export of the older
version (cost + confirm) → download → phone-width screenshots. Usage: browser_accounts.py SITE VIDEO OUT_DIR"""
import json, re, sys, time, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright

site, video, out = sys.argv[1].rstrip("/"), sys.argv[2], Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True); R = {}
shot = lambda pg, n: pg.screenshot(path=out / f"{n}.png", full_page=True)


def wait_title(pg, pat, s=900):
    pg.wait_for_function(f"() => /{pat}/i.test(document.querySelector('#jobTitle').textContent)", timeout=s * 1000, polling=1500)


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(site + "/"); pg.wait_for_load_state("networkidle")
    pg.set_input_files("#file", video); pg.click("#go")                              # not signed in → sign-in panel
    pg.fill(".email-in", f"eva-{uuid.uuid4().hex[:6]}@example.com"); pg.click("text=Email me a sign-in link"); pg.wait_for_load_state("networkidle")
    time.sleep(2); pg.wait_for_selector("#costLine", state="attached")
    pg.wait_for_function("() => document.querySelector('#costLine') && /free/i.test(document.querySelector('#costLine').textContent)", timeout=20000)
    pg.set_input_files("#file", video); time.sleep(1.5)
    R["cost_line_before_generating"] = pg.inner_text("#costLine"); R["header"] = pg.inner_text(".top nav .acct"); shot(pg, "1_home_signed_in")
    pg.click("#go"); pg.wait_for_url("**/video.html?v=*", timeout=120000); v1 = pg.url.split("v=")[1]
    wait_title(pg, "Preview 1 is ready"); time.sleep(2); shot(pg, "2_preview_ready"); R["preview_page_buttons"] = pg.locator("#jobAction .btn").all_inner_texts()
    pg.goto(site + "/videos.html"); pg.wait_for_selector(".vcard"); time.sleep(1.5); shot(pg, "3_my_videos")
    nv = pg.locator(".proj-head .row button").first; nv.click(); R["regen_confirm_text"] = pg.inner_text("#libNote"); nv.click()   # two-step confirm
    pg.wait_for_url("**/video.html?v=*", timeout=60000); v2 = pg.url.split("v=")[1]; wait_title(pg, "Preview 2 is ready"); R["regen_version"] = v2
    pg.goto(f"{site}/video.html?v={v1}"); wait_title(pg, "Preview 1 is ready")                         # go back to the OLDER version
    pg.get_by_role("button", name=re.compile("Export HD")).click(); time.sleep(1); R["hd_confirm_no_credits"] = pg.inner_text(".confirm"); shot(pg, "4_hd_confirm_no_credits")
    pg.get_by_role("button", name="Top up first").click(); pg.wait_for_selector("text=Top up $9.99 · 100 credits"); shot(pg, "5_topup_offer")
    pg.get_by_role("button", name="Top up $9.99 · 100 credits").click()
    pg.wait_for_url(re.compile(r".*video\.html\?v=" + v1 + r".*topup=done.*"), timeout=60000); time.sleep(2)
    R["after_topup_note"] = pg.locator("#jobAction .note").first.inner_text(); R["header_after_topup"] = pg.inner_text(".top nav .acct")
    pg.get_by_role("button", name=re.compile("Export HD")).click(); R["hd_confirm"] = pg.inner_text(".confirm"); shot(pg, "6_hd_confirm")
    pg.get_by_role("button", name=re.compile(r"Export for \d+ credits")).click()
    pg.wait_for_url("**/video.html?v=h*", timeout=60000); h = pg.url.split("v=")[1]
    wait_title(pg, "HD video is ready", 1800); time.sleep(2); shot(pg, "7_hd_ready"); R["hd_page"] = pg.inner_text("#jobSub")
    with pg.expect_download(timeout=60000) as d: pg.get_by_role("link", name="Download HD").click()
    f = out / "hd.mp4"; d.value.save_as(f); R["hd_bytes"] = f.stat().st_size
    pg.goto(site + "/videos.html"); pg.wait_for_selector(".vcard"); time.sleep(1.5); shot(pg, "8_my_videos_after"); R["header_end"] = pg.inner_text(".top nav .acct")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx.add_init_script(f"localStorage.setItem('eva:auth', {json.dumps(pg.evaluate('() => localStorage.getItem(\"eva:auth\")'))})")
    m = ctx.new_page()
    for url, n in ((site + "/videos.html", "9m_my_videos"), (f"{site}/video.html?v={h}", "9m_hd")):
        m.goto(url); m.wait_for_timeout(3000); R[n + "_overflow"] = m.evaluate("() => document.documentElement.scrollWidth > innerWidth"); m.screenshot(path=out / f"{n}.png", full_page=True)
    R["page_errors"] = errs; b.close()
(out / "summary.json").write_text(json.dumps(R, indent=1)); print(json.dumps(R, indent=1))
