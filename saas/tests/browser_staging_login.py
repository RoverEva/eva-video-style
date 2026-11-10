#!/usr/bin/env python3
"""Staging site, real Supabase Auth, real browser: magic link → lands on the staging site signed in → session survives a
reload → Sign out → stays signed out after a reload. One throwaway user (deleted). Prints facts only, never links/tokens.

    SITE=https://… python3 saas/tests/browser_staging_login.py      env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request, uuid
from playwright.sync_api import sync_playwright

S = "".join(os.environ["SUPABASE_URL"].split()); K = "".join(os.environ["SUPABASE_SERVICE_ROLE_KEY"].split())
SITE = os.environ["SITE"].rstrip("/"); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)
def admin(method, path, body=None):
    req = urllib.request.Request(S + "/auth/v1/admin" + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"apikey": K, "Authorization": f"Bearer {K}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e: return e.code, {}

email = f"staging-login-{uuid.uuid4().hex[:8]}@example.com"
st, u = admin("POST", "/users", {"email": email, "email_confirm": True}); uid = u.get("id")
try:
    check(bool(uid), f"throwaway user created ({st})")
    st, j = admin("POST", "/generate_link", {"type": "magiclink", "email": email, "redirect_to": SITE + "/"})
    link = j.get("action_link") or (j.get("properties") or {}).get("action_link")
    check(bool(link), "magic link generated (same link the email contains; no email sent)")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(link); pg.wait_for_load_state("networkidle")
        host = urllib.parse.urlparse(pg.url).netloc
        check(host == urllib.parse.urlparse(SITE).netloc, f"magic link redirects to the staging site ({host})")
        pg.wait_for_selector(".top nav .avatar", timeout=15000)
        check(pg.text_content(".top nav .avatar") == email[0].upper(), "signed in: header shows the account avatar")
        check("access_token" not in pg.url, "token removed from the address bar")
        pg.reload(); pg.wait_for_load_state("networkidle")
        check(pg.is_visible(".top nav .avatar"), "session persists after reload")
        pg.goto(SITE + "/videos.html"); pg.wait_for_load_state("networkidle")
        check(pg.is_visible(".top nav .avatar"), "session persists on another page (My Videos)")
        pg.click(".top nav .avatar")
        with pg.expect_navigation(timeout=15000): pg.click(".acctmenu .signout")   # sign out reloads the page
        pg.wait_for_load_state("networkidle"); pg.reload(); pg.wait_for_load_state("networkidle")
        left = pg.evaluate("() => Object.keys(localStorage).filter(k => k.startsWith('sb-') && k.endsWith('auth-token')).length")
        check(pg.is_visible(".top nav a.signin") and left == 0, f"signed out: no session after reload (Sign in shown {pg.is_visible('.top nav a.signin')}, stored sessions {left})")
        check(not errs, f"no page errors {errs[:2]}")
        b.close()
finally:
    if uid: st, _ = admin("DELETE", f"/users/{uid}"); check(st in (200, 204), f"throwaway user deleted ({st})")
print("staging login:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
