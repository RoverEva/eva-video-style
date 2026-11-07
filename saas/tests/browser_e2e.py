#!/usr/bin/env python3
"""Customer journey in a real browser, against any deployment (local stack or the live Vercel + Modal + Stripe test mode):
home page → upload a REAL video → options → free preview → Stripe Checkout. With --checkout-only (the deploy test) it stops
once Stripe-hosted Checkout has opened and verifies the TEST-mode Checkout Session via the Stripe API: Stripe protects its
hosted card fields against automation, so payment → webhook → render → download is covered by saas/tests/test_api.py
(server side) and by a manual sandbox purchase. Without the flag (local stack) it pays and checks the delivered MP4. Writes screenshots and a JSON summary (timings, sizes) to OUT_DIR.

    python3 saas/tests/browser_e2e.py SITE_URL VIDEO.mp4 OUT_DIR [--aspect 9:16] [--templates T17,T20] [--music mix|none|track:id,id]
"""
import argparse, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright


# ───────────── Stripe Checkout (hosted page, TEST mode): opened + verified, card entry never automated ─────────────
def _fail(msg): raise RuntimeError(msg)


def checkout_opened(pg, out, job, redact=()):
    """PASS when our checkout button landed on Stripe-hosted Checkout for a TEST-mode session that belongs to this job.
    The session is re-read server-side from the Stripe API (key from env; read-only call, no new permissions)."""
    try:
        u = urllib.parse.urlsplit(pg.url)
        m = re.search(r"/(cs_test_[A-Za-z0-9]+)", u.path)
        pg.wait_for_load_state("domcontentloaded", timeout=60_000)
        checks = {"stripe_hosted_url": u.scheme == "https" and u.hostname == "checkout.stripe.com",
                  "test_mode_session_id": bool(m), "page_loaded": bool(pg.title() is not None)}
        info = {"session": m.group(1)[:14] + "…" if m else None}
        if m and os.environ.get("STRIPE_SECRET_KEY"):
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web")); import stripe_lite
            cs = stripe_lite.call("GET", f"/checkout/sessions/{m.group(1)}")
            checks.update(session_livemode_false=cs.get("livemode") is False, amount_999_usd=cs.get("amount_total") == 999 and cs.get("currency") == "usd",
                          session_belongs_to_job=(cs.get("metadata") or {}).get("job") == job and cs.get("client_reference_id") == job,
                          session_open_unpaid=cs.get("status") == "open" and cs.get("payment_status") == "unpaid",
                          returns_to_video_page="/video.html?id=" + job in (cs.get("success_url") or ""))
            info.update(status=cs.get("status"), payment_status=cs.get("payment_status"), amount_total=cs.get("amount_total"), livemode=cs.get("livemode"))
        else: checks["session_verified_via_api"] = False
        info["checks"] = checks
        print("stripe checkout opened:", json.dumps(info), flush=True)
        if not all(checks.values()): _diag(pg, out, redact, RuntimeError(f"checkout checks failed: {checks}"))
        return info
    except Exception as e:
        _diag(pg, out, redact, e); raise


def _diag(pg, out, redact, err):   # writes stripe_fail.png / stripe_fail.html
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
    ap.add_argument("--checkout-only", action="store_true", help="live deploy test: stop once Stripe Checkout has opened and verify "
                    "the Checkout Session through the Stripe API (Stripe blocks automation of its hosted card fields)")
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
        api_base = pg.evaluate("() => window.EVA_API")
        pg.click("#jobAction button.btn"); pg.wait_for_url(lambda u: "stripe.com" in u or "paid=1" in u, timeout=60_000); mark("checkout_open")
        if a.checkout_only:
            res.update(job=pv_job, checkout=checkout_opened(pg, out, pv_job, redact=[pv_tok]))
            try: pg.screenshot(path=out / "4_checkout.png")
            except Exception: pass
            b.close()
            v = json.loads(urllib.request.urlopen(f"{api_base}/api/jobs/{pv_job}?t={urllib.parse.quote(pv_tok)}", timeout=30).read())
            res["metrics"] = {"preview": v["preview"].get("metrics")}; res["seconds"] = T
            (out / "private.txt").write_text(json.dumps({"api": api_base, "job": pv_job, "token": pv_tok, "href": None}))
            ok = all(res["checkout"]["checks"].values())
            (out / "summary.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
            sys.exit(0 if ok else 1)
        if "stripe.com" in pg.url:   # only the local stack's fake checkout redirects straight back with paid=1
            sys.exit("Stripe-hosted Checkout opened: card entry is not automated (Stripe blocks it); run with --checkout-only")
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
