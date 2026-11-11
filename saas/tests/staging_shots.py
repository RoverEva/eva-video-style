#!/usr/bin/env python3
"""Review screenshots of the staging site, desktop + phone.   staging_shots.py SITE OUT_DIR
Each in English and 简体中文: Home (logo, 9:16 + 16:9 demos, How EVA works, language menu), Templates + detail modal, Pricing, and — signed in through a real Supabase magic link for a
throwaway user (deleted afterwards; needs SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY) — the account menu, My Account and
My Videos. Staging has no API backend, so My Account / My Videos show the signed-in shell, not credits or videos."""
import json, os, sys, urllib.request, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright

site, out = sys.argv[1].rstrip("/"), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
S, K = "".join((os.environ.get("SUPABASE_URL") or "").split()), "".join((os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").split())
def admin(method, path, body=None):
    req = urllib.request.Request(S + "/auth/v1/admin" + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"apikey": K, "Authorization": f"Bearer {K}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read() or b"{}")
uid = None
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        for lang in ("en", "zh"):   # English (default) and 简体中文, chosen with ?lang= and kept by the site
          for name, vp in (("desktop", {"width": 1366, "height": 900}), ("phone", {"width": 390, "height": 844})):
            ctx = b.new_context(viewport=vp); pg = ctx.new_page(); P = f"{lang}_"
            pg.goto(site + f"/?lang={lang}"); pg.wait_for_timeout(3500); pg.screenshot(path=str(out / f"{P}1_home_{name}.png"))
            pg.locator("#how").scroll_into_view_if_needed(); pg.wait_for_timeout(1200)
            pg.locator("#how").screenshot(path=str(out / f"{P}1b_how_{name}.png"))
            if name == "desktop": pg.evaluate("scrollTo(0, 0)"); pg.click(".langbtn"); pg.wait_for_timeout(250); pg.screenshot(path=str(out / f"{P}1c_language_menu.png"), clip={"x": 766, "y": 0, "width": 600, "height": 260})
            pg.goto(site + "/templates.html"); pg.wait_for_selector(".g-card"); pg.wait_for_timeout(2000)
            pg.screenshot(path=str(out / f"{P}2_templates_{name}.png"), full_page=(name == "phone"))
            pg.click(".g-card[data-id=T17]"); pg.wait_for_selector("#gDlg[open]"); pg.wait_for_timeout(600)
            pg.screenshot(path=str(out / f"{P}3_template_modal_{name}.png")); pg.keyboard.press("Escape")
            pg.goto(site + "/pricing.html"); pg.wait_for_selector(".pr-offer"); pg.wait_for_timeout(500)
            pg.screenshot(path=str(out / f"{P}4_pricing_{name}.png"), full_page=True)
            if S and K:
                email = f"staging-shots-{uuid.uuid4().hex[:8]}@example.com"
                uid = uid or admin("POST", "/users", {"email": email, "email_confirm": True}).get("id")
                if uid:
                    u = admin("GET", f"/users/{uid}")
                    link = admin("POST", "/generate_link", {"type": "magiclink", "email": u["email"], "redirect_to": site + "/account.html"})
                    pg.goto(link.get("action_link") or link["properties"]["action_link"]); pg.wait_for_selector(".avatar", timeout=20000); pg.wait_for_timeout(1500)
                    pg.screenshot(path=str(out / f"{P}5_account_{name}.png"), full_page=True)
                    pg.goto(site + "/videos.html"); pg.wait_for_selector(".avatar"); pg.wait_for_timeout(1500); pg.click(".avatar"); pg.wait_for_timeout(300)
                    pg.screenshot(path=str(out / f"{P}6_videos_menu_{name}.png"))
            ctx.close()
        b.close()
finally:
    if uid:
        try: admin("DELETE", f"/users/{uid}"); print("throwaway user deleted")
        except Exception as e: print("user delete failed:", type(e).__name__)
print("screenshots:", sorted(x.name for x in out.glob("*.png")))
