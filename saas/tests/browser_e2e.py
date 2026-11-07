#!/usr/bin/env python3
"""Customer journey in a real browser, against any deployment (local stack or the live Vercel + Modal + Stripe test mode):
home page → upload a REAL video → options → free preview → Stripe Checkout (test card 4242…) → automatic HD delivery
→ download the MP4 and check it with ffprobe. Writes screenshots and a JSON summary (timings, sizes) to OUT_DIR.

    python3 saas/tests/browser_e2e.py SITE_URL VIDEO.mp4 OUT_DIR [--aspect 9:16] [--templates T17,T20] [--music mix|none|track:id,id]
"""
import argparse, json, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright


# ───────────── Stripe Checkout (hosted page, TEST mode, test card only) ─────────────
TEST_CARD = {"number": "4242 4242 4242 4242", "exp": "12 / 34", "cvc": "123", "name": "EVA E2E Test", "zip": "94107"}
CARD_NUMBER = '#cardNumber, input[name="cardNumber"], input[name="cardnumber"], input[autocomplete="cc-number"]'
CARD_EXP = '#cardExpiry, input[name="cardExpiry"], input[name="exp-date"], input[autocomplete="cc-exp"]'
CARD_CVC = '#cardCvc, input[name="cardCvc"], input[name="cvc"], input[autocomplete="cc-csc"]'


def _usable(loc):
    """visible AND enabled: never act on an element just because it exists in the DOM"""
    try: return loc.is_visible() and loc.is_enabled()
    except Exception: return False


def _first_usable(loc):
    try: n = loc.count()
    except Exception: return None
    for i in range(n):
        if _usable(loc.nth(i)): return loc.nth(i)
    return None


def _card_frame(pg):
    """the page or frame (Stripe may move card inputs into an iframe) whose card-number input is usable"""
    for fr in [pg.main_frame] + [f for f in pg.frames if f is not pg.main_frame]:
        if _first_usable(fr.locator(CARD_NUMBER)): return fr
    return None


def _wait(fn, seconds):
    t0 = time.time()
    while time.time() - t0 < seconds:
        r = fn()
        if r: return r
        time.sleep(.5)
    return None


def stripe_pay(pg, out, email, redact=(), timeout=60):
    """Pay on Stripe Checkout with the test card. Two valid layouts:
    A  payment methods shown as an accordion → click the VISIBLE "Card"/"Pay with card" control, then fill the fields
    B  card already active (fields visible; the accordion button may exist but be hidden) → fill directly, no click
    On any failure saves stripe_fail.png + stripe_fail.html (private token redacted) next to the other outputs."""
    try:
        pg.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        em = _wait(lambda: _first_usable(pg.locator('#email, input[name="email"], input[type="email"]')), 20)
        if em and not em.input_value(): em.fill(email)
        state = "B: card already active"
        fr = _wait(lambda: _card_frame(pg), 8)
        if not fr:
            pickers = [pg.get_by_role("button", name=re.compile(r"^\s*(pay with )?card\s*$", re.I)),
                       pg.get_by_role("radio", name=re.compile(r"\bcard\b", re.I)),
                       pg.get_by_label(re.compile(r"^\s*card\s*$", re.I)),
                       pg.locator('[data-testid="card-accordion-item-button"]'),
                       pg.locator('[data-testid="card-accordion-item"] button, [data-testid="card-accordion-item"] input[type="radio"]')]
            btn = _wait(lambda: next((b for b in (_first_usable(p) for p in pickers) if b), None), 20)
            if not btn: raise RuntimeError("no visible card fields and no visible, enabled Card payment-method control")
            btn.click(); state = "A: clicked visible card accordion"
            fr = _wait(lambda: _card_frame(pg), 30)
            if not fr: raise RuntimeError("clicked the Card control but the card fields did not become visible")
        print("stripe checkout:", state, "(frame)" if fr is not pg.main_frame else "", flush=True)
        _first_usable(fr.locator(CARD_NUMBER)).fill(TEST_CARD["number"])
        (_wait(lambda: _first_usable(fr.locator(CARD_EXP)), 10) or _fail("expiry field not visible")).fill(TEST_CARD["exp"])
        (_wait(lambda: _first_usable(fr.locator(CARD_CVC)), 10) or _fail("CVC field not visible")).fill(TEST_CARD["cvc"])
        for sel, val in (('#billingName, input[name="billingName"]', TEST_CARD["name"]), ('#billingPostalCode, input[name="billingPostalCode"]', TEST_CARD["zip"])):
            el = _first_usable(pg.locator(sel)) or _first_usable(fr.locator(sel))
            if el and not el.input_value(): el.fill(val)
        try: pg.screenshot(path=out / "4_checkout.png")
        except Exception: pass
        # the real submit button first; never the "Pay with card" payment-method button
        sub = _wait(lambda: _first_usable(pg.locator('button[type="submit"]:not([data-testid*="accordion"])'))
                    or _first_usable(pg.get_by_role("button", name=re.compile(r"^\s*(pay|complete|buy)\b(?!.*\bcard\b)", re.I))), 15)
        if not sub: raise RuntimeError("no visible, enabled Pay button")
        sub.click()
        return state
    except Exception as e:
        _diag(pg, out, redact, e); raise


def _fail(msg): raise RuntimeError(msg)


def _diag(pg, out, redact, err):
    """failure evidence for the CI artifact: screenshot + page HTML (+ frame list); private tokens and emails redacted"""
    try:
        pg.screenshot(path=out / "stripe_fail.png", full_page=True)
        html = pg.content()
        for r in redact: html = html.replace(r, "[redacted]").replace(urllib.parse.quote(r), "[redacted]")
        html = re.sub(r"#t=[A-Za-z0-9_%-]+", "#t=[redacted]", html)
        frames = "\n".join(f"<!-- frame: {f.url.split('?')[0]} -->" for f in pg.frames)
        (out / "stripe_fail.html").write_text(f"<!-- error: {err} -->\n<!-- url: {pg.url.split('#')[0].split('?')[0]} -->\n{frames}\n{html}")
        print("stripe step failed; saved stripe_fail.png + stripe_fail.html:", err, flush=True)
    except Exception as e2: print("could not save Stripe diagnostics:", e2, flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("site"); ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--aspect", default="9:16"); ap.add_argument("--templates", default="T17,T20"); ap.add_argument("--music", default="mix")
    ap.add_argument("--email", default="eva-e2e@example.com"); ap.add_argument("--expect", choices=["delivered", "refunded"], default="delivered")
    a = ap.parse_args()
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
        pv_job = pg.url.split("id=")[1].split("&")[0].split("#")[0]; pv_tok = pg.evaluate(f"() => localStorage.getItem('eva:{pv_job}')")
        pg.click("#jobAction button.btn"); pg.wait_for_url(lambda u: "stripe.com" in u or "paid=1" in u, timeout=60_000); mark("checkout_open")
        if "stripe.com" in pg.url:
            res["stripe_state"] = stripe_pay(pg, out, a.email, redact=[pv_tok] if pv_tok else [])
        pg.wait_for_url("**/video.html?id=*paid=1*", timeout=3 * 60_000); mark("paid_redirect")
        pg.wait_for_function("() => /video is ready|refunded/.test(document.querySelector('#jobTitle').textContent)", timeout=30 * 60_000, polling=3000)
        mark("hd_ready" if a.expect == "delivered" else "refunded"); pg.screenshot(path=out / "5_result.png")
        res["final_title"] = pg.inner_text("#jobTitle"); res["final_sub"] = pg.inner_text("#jobSub")
        href = pg.get_attribute("#jobAction a.btn", "href")
        api_base = pg.evaluate("() => window.EVA_API"); job = pg.url.split("id=")[1].split("&")[0].split("#")[0]
        tok = pg.evaluate(f"() => localStorage.getItem('eva:{job}')")
        b.close()
    try:   # measured render time and compute cost recorded by the workers
        v = json.loads(urllib.request.urlopen(f"{api_base}/api/jobs/{job}?t={urllib.parse.quote(tok)}", timeout=30).read())
        res["job"] = job; res["metrics"] = {"preview": v["preview"].get("metrics"), "final": (v.get("final") or {}).get("metrics"), "music": (v.get("final") or {}).get("music")}
    except Exception as e: res["metrics_error"] = str(e)
    # private handle for live_checks.py (token = access to the video): never in the public JSON artifact
    (out / "private.txt").write_text(json.dumps({"api": api_base, "job": job, "token": tok, "href": href}))
    if a.expect == "refunded":
        ok = "refunded" in res["final_title"].lower() and not href
        res["refund_ok"] = ok; (out / "summary.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
        sys.exit(0 if ok else 1)
    if not href or "ready" not in res["final_title"]: print(json.dumps(res)); sys.exit(1)
    mp4 = out / "delivered.mp4"; urllib.request.urlretrieve(href, mp4); mark("downloaded")
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height", "-of", "json", mp4],
                                   capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    res.update(delivered={"width": v["width"], "height": v["height"], "duration": float(pr["format"]["duration"]), "bytes": int(pr["format"]["size"]),
                          "audio": any(s["codec_type"] == "audio" for s in pr["streams"])}, seconds=T)
    (out / "summary.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
