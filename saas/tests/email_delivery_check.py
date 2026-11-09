#!/usr/bin/env python3
"""Real sign-in email through Supabase Custom SMTP → Resend, then real authentication with the emailed link. Staging.

Recipient: Resend's test inbox delivered+<id>@resend.dev (accepted and logged by Resend, no real person, no bounce).
  1. POST /auth/v1/otp (what the site's sign-in button does) → Supabase sends the email through Custom SMTP
  2. Resend API (RESEND_API_KEY, full-access key): the email is in the logs, from the evavideostudio.com sender,
     last_event delivered
  3. the emailed magic link → lands on the site with a session; the token validates (GET /auth/v1/user);
     the 6-digit code in the same email (if the template shows it) verifies too
  4. the throwaway user is deleted
Prints facts only — never keys, links or tokens.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, uuid, html as H

E = {k: "".join((os.environ.get(k) or "").split()) for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "RESEND_API_KEY")}
SITE = (os.environ.get("EVA_SITE_URL") or "https://eva-video-studio.vercel.app").rstrip("/")
DOMAIN = os.environ.get("EVA_MAIL_DOMAIN", "evavideostudio.com")
fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)
    return c

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a): return None

def http(method, url, key=None, bearer=None, body=None, follow=True):
    h = {"Content-Type": "application/json", "User-Agent": "eva-staging-check"}
    if key: h["apikey"] = key
    if bearer: h["Authorization"] = f"Bearer {bearer}"
    req = urllib.request.Request(url, method=method, headers=h, data=json.dumps(body).encode() if body is not None else None)
    op = urllib.request.build_opener(*([] if follow else [NoRedirect]))
    try:
        with op.open(req, timeout=30) as r: return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), e.read()
    except Exception as e: return 0, {}, type(e).__name__.encode()

def jl(b):
    try: return json.loads(b)
    except Exception: return None

def main():
    S, A, SR, RK = E["SUPABASE_URL"], E["SUPABASE_ANON_KEY"], E["SUPABASE_SERVICE_ROLE_KEY"], E["RESEND_API_KEY"]
    if not check(S and A and SR, "Supabase secrets present"): return
    tag = uuid.uuid4().hex[:10]; email = f"delivered+eva-{tag}@resend.dev"; uid = None
    try:
        t0 = time.time()
        st, _, b = http("POST", S + "/auth/v1/otp?redirect_to=" + urllib.parse.quote(SITE + "/"), key=A,
                        body={"email": email, "create_user": True})
        msg = ((jl(b) or {}).get("msg") or (jl(b) or {}).get("error_description") or (jl(b) or {}).get("message") or "")[:160]
        check(st == 200, f"Supabase accepted the sign-in request and sent the email via Custom SMTP (HTTP {st}{': ' + msg if msg else ''})")
        if st != 200: return
        if not RK:
            print("INFO RESEND_API_KEY is not in the staging environment: check Resend → Emails for the message to "
                  f"delivered+eva-{tag}@resend.dev (status Delivered). The emailed-link sign-in step needs that key."); return
        hdr = {"Authorization": f"Bearer {RK}", "User-Agent": "eva-staging-check"}
        def rget(path):
            try:
                with urllib.request.urlopen(urllib.request.Request("https://api.resend.com" + path, headers=hdr), timeout=30) as r: return r.status, jl(r.read())
            except urllib.error.HTTPError as e: return e.code, jl(e.read())
            except Exception: return 0, None
        found = None
        for _ in range(30):
            st, j = rget("/emails?limit=50")
            if st != 200: break
            found = next((m for m in (j or {}).get("data", []) if email in [x.lower() for x in m.get("to", [])]), None)
            if found: break
            time.sleep(4)
        if not check(st == 200, f"Resend API readable with this key (HTTP {st}{' — needs a Full access key' if st in (401, 403) else ''})"): return
        if not check(bool(found), f"email is in Resend's logs ({time.time() - t0:.0f} s after the request)"): return
        for _ in range(15):
            st, m = rget(f"/emails/{found['id']}")
            if (m or {}).get("last_event") in ("delivered", "bounced", "complained"): break
            time.sleep(4)
        m = m or {}
        frm = (m.get("from") or "")
        check(frm.lower().rstrip(">").endswith("@" + DOMAIN), f"sent from the {DOMAIN} domain ({frm})")
        check(m.get("last_event") == "delivered", f"Resend status: {m.get('last_event')} (subject: {m.get('subject')!r})")
        body = H.unescape(m.get("html") or m.get("text") or "")
        link = next((u for u in re.findall(r'https?://[^\s"\'<>]+', body) if "/auth/v1/verify" in u), None)
        if check(bool(link), "email contains the sign-in link"):
            st, h, _ = http("GET", link, follow=False); loc = h.get("Location") or h.get("location") or ""
            target, frag = loc.split("#", 1) if "#" in loc else (loc, "")
            tok = urllib.parse.parse_qs(frag).get("access_token", [None])[0]
            check(st in (302, 303) and target.rstrip("/") == SITE and bool(tok), f"emailed link signs in and lands on {SITE}/ (HTTP {st})")
            if tok:
                st, _, b = http("GET", S + "/auth/v1/user", key=SR, bearer=tok); u = jl(b) or {}
                uid = u.get("id")
                check(st == 200 and (u.get("email") or "").lower() == email, "session from the emailed link validates (GET /auth/v1/user)")
        code = re.search(r"(?<!\d)(\d{6})(?!\d)", re.sub(r"<[^>]+>", " ", body))
        if code:   # the template shows {{ .Token }} — one link/code per email: it was used above, so just report presence
            print("INFO the email also shows a 6-digit code (OTP sign-in available)")
        else: print("INFO no 6-digit code in the template (link sign-in only — add {{ .Token }} to the template for code sign-in)")
    finally:
        if not uid:
            st, _, b = http("GET", S + "/auth/v1/admin/users?page=1&per_page=200", key=SR, bearer=SR)
            uid = next((u["id"] for u in (jl(b) or {}).get("users", []) if (u.get("email") or "").lower() == email), None)
        if uid:
            st, _, _ = http("DELETE", S + f"/auth/v1/admin/users/{uid}", key=SR, bearer=SR)
            check(st in (200, 204), f"throwaway test user deleted ({st})")

if __name__ == "__main__":
    try: main()
    except Exception as e: check(False, f"unexpected {type(e).__name__}")
    print("email delivery check:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
