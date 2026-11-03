#!/usr/bin/env python3
"""Customer journey in a real browser, against any deployment (local stack or the live Vercel + Modal + Stripe test mode):
home page → upload a REAL video → options → free preview → Stripe Checkout (test card 4242…) → automatic HD delivery
→ download the MP4 and check it with ffprobe. Writes screenshots and a JSON summary (timings, sizes) to OUT_DIR.

    python3 saas/tests/browser_e2e.py SITE_URL VIDEO.mp4 OUT_DIR [--aspect 9:16] [--templates T17,T20] [--music mix|none|track:id,id]
"""
import argparse, json, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("site"); ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--aspect", default="9:16"); ap.add_argument("--templates", default="T17,T20"); ap.add_argument("--music", default="mix")
    ap.add_argument("--email", default="eva-e2e@example.com"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); T = {"start": time.time()}; res = {"site": a.site, "video": a.video}
    mark = lambda k: T.__setitem__(k, round(time.time() - T["start"], 1))
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.on("console", lambda m: m.type == "error" and print("[console]", m.text))
        pg.goto(a.site.rstrip("/") + "/"); pg.wait_for_load_state("networkidle"); pg.screenshot(path=out / "1_home.png", full_page=True)
        pg.set_input_files("#file", a.video)
        pg.check(f"input[name=aspect][value='{a.aspect}']", force=True)
        tpls = [t for t in a.templates.split(",") if t]
        for box in pg.query_selector_all("input[name=tpl]"):
            want = box.get_attribute("value") in tpls
            if box.is_checked() != want: box.set_checked(want, force=True)
        if not tpls: pg.check("input[name=tplauto]", force=True)
        mode, _, ids = a.music.partition(":")
        pg.check(f"input[name=music][value='{mode}']", force=True)
        for t in filter(None, ids.split(",")): pg.check(f"input[name=track][value='{t}']", force=True)
        pg.screenshot(path=out / "2_options.png", full_page=True)
        pg.click("#go"); mark("submitted")
        pg.wait_for_url("**/video.html?id=*", timeout=10 * 60_000); mark("uploaded"); res["video_page"] = pg.url.split("#")[0]
        pg.wait_for_function("() => /preview is ready|couldn't be processed/.test(document.querySelector('#jobTitle').textContent)", timeout=20 * 60_000, polling=2000)
        mark("preview_ready"); pg.screenshot(path=out / "3_preview.png")
        if "couldn't" in pg.inner_text("#jobTitle"): res["error"] = pg.inner_text("#jobSub"); print(json.dumps(res)); sys.exit(1)
        pg.click("#jobAction button.btn"); pg.wait_for_url(lambda u: "video.html" not in u, timeout=60_000); mark("checkout_open")
        if "stripe.com" in pg.url:
            pg.wait_for_selector("#cardNumber", timeout=60_000); pg.screenshot(path=out / "4_checkout.png")
            if pg.query_selector("#email"): pg.fill("#email", a.email)
            pg.fill("#cardNumber", "4242 4242 4242 4242"); pg.fill("#cardExpiry", "12 / 34"); pg.fill("#cardCvc", "123")
            if pg.query_selector("#billingName"): pg.fill("#billingName", "EVA E2E Test")
            if pg.query_selector("#billingPostalCode") and pg.is_visible("#billingPostalCode"): pg.fill("#billingPostalCode", "94107")
            pg.click("button[type=submit]")
        pg.wait_for_url("**/video.html?id=*paid=1*", timeout=3 * 60_000); mark("paid_redirect")
        pg.wait_for_function("() => /video is ready|refunded/.test(document.querySelector('#jobTitle').textContent)", timeout=30 * 60_000, polling=3000)
        mark("hd_ready"); pg.screenshot(path=out / "5_delivered.png")
        res["final_title"] = pg.inner_text("#jobTitle"); res["final_sub"] = pg.inner_text("#jobSub")
        href = pg.get_attribute("#jobAction a.btn", "href")
        api_base = pg.evaluate("() => window.EVA_API"); job = pg.url.split("id=")[1].split("&")[0].split("#")[0]
        tok = pg.evaluate(f"() => localStorage.getItem('eva:{job}')")
        b.close()
    try:   # measured render time and compute cost recorded by the workers
        v = json.loads(urllib.request.urlopen(f"{api_base}/api/jobs/{job}?t={urllib.parse.quote(tok)}", timeout=30).read())
        res["job"] = job; res["metrics"] = {"preview": v["preview"].get("metrics"), "final": (v.get("final") or {}).get("metrics"), "music": (v.get("final") or {}).get("music")}
    except Exception as e: res["metrics_error"] = str(e)
    if not href: print(json.dumps(res)); sys.exit(1)
    mp4 = out / "delivered.mp4"; urllib.request.urlretrieve(href, mp4); mark("downloaded")
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height", "-of", "json", mp4],
                                   capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    res.update(delivered={"width": v["width"], "height": v["height"], "duration": float(pr["format"]["duration"]), "bytes": int(pr["format"]["size"]),
                          "audio": any(s["codec_type"] == "audio" for s in pr["streams"])}, seconds=T)
    (out / "summary.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
