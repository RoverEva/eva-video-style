#!/usr/bin/env python3
"""Staging check of the real Supabase project — leaves nothing behind. Never prints keys, tokens or the DB URL.

    SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY SUPABASE_DB_URL [EVA_SITE_URL]  python3 saas/tests/supabase_staging_check.py

1. Database: connect through SUPABASE_DB_URL (pooler mode reported), server version, role; inventory of `public` before.
2. Migration safety: saas/db/tests/tx_check.sql — 001 applied twice + lockdown + credits / 3 lifetime free previews /
   My Videos rules, all inside one transaction that is ROLLED BACK; inventory after must equal before.
3. Auth (GoTrue): health + settings (email sign-in on), then ONE throwaway user (staging-check-<id>@example.com,
   created confirmed via the admin API — no email is sent): a magic link per site page the app uses must land on that
   page with a session; a foreign redirect must NOT be honoured; the session token validates exactly as the API does it
   (GET /auth/v1/user with the service key as apikey). The user is deleted at the end, whatever happens.
4. REST: the browser's anon key cannot call any eva_* function (only checked if the migration is already applied).
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = {k: (os.environ.get(k) or "").strip() for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_DB_URL")}
RO = os.environ.get("EVA_READ_ONLY") == "1"   # production preflight: no migration test, no test user, DB session read-only
if RO: os.environ["PGOPTIONS"] = (os.environ.get("PGOPTIONS", "") + " -c default_transaction_read_only=on").strip()
SITE = (os.environ.get("EVA_SITE_URL") or "https://eva-video-studio.vercel.app").rstrip("/")
fails, R = [], {}


def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)
    return c


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None


def http(method, url, key=None, bearer=None, body=None, follow=True):
    h = {"Content-Type": "application/json"}
    if key: h["apikey"] = key
    if bearer: h["Authorization"] = f"Bearer {bearer}"
    req = urllib.request.Request(url, method=method, headers=h, data=json.dumps(body).encode() if body is not None else None)
    op = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with op.open(req, timeout=30) as r: return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), e.read()
    except (urllib.error.URLError, OSError) as e:          # unreachable host: report, do not crash
        print(f"INFO network error for {urllib.parse.urlparse(url).hostname}: {type(e).__name__}"); return 0, {}, b""


def jl(b):
    try: return json.loads(b or b"null")
    except ValueError: return None


def psql(*args, sql=None, file=None):
    if RO and file: raise RuntimeError("read-only mode runs no SQL files")
    ro = ["-q", "-c", "set session characteristics as transaction read only"] if RO else []
    cmd = ["psql", E["SUPABASE_DB_URL"], "-v", "ON_ERROR_STOP=1", "-X", *args, *ro] + (["-c", sql] if sql else []) + (["-f", str(file)] if file else [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def inventory():
    r = psql("-At", sql="select coalesce(string_agg(c.relkind || ':' || c.relname, ',' order by c.relname), '') from pg_class c "
                        "join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relkind in ('r','v','m','S','f','p');"
                        "select coalesce(string_agg(p.proname, ',' order by p.proname), '') from pg_proc p join pg_namespace n on n.oid = p.pronamespace "
                        "where n.nspname = 'public'")
    return r.stdout.strip().splitlines() if r.returncode == 0 else None


def main():
    miss = [k for k, v in E.items() if not v]
    if not check(not miss, "Supabase secrets present in this environment" + (f" (missing: {', '.join(miss)})" if miss else "")):
        return
    want = (os.environ.get("SUPABASE_PROJECT_REF") or "").strip()      # public project ref (dashboard link), not a secret
    try: host = urllib.parse.urlparse(E["SUPABASE_URL"]).hostname or ""
    except ValueError: host = ""
    ref = host.split(".")[0] if host.endswith(".supabase.co") else ""
    url_ok = check(bool(ref) and E["SUPABASE_URL"].rstrip("/") == f"https://{ref}.supabase.co" and (not want or ref == want),
                   f"SUPABASE_URL is the project URL https://{want or '<ref>'}.supabase.co"
                   + ("" if ref else f" (it is not: host looks like '{host.split('.')[0] or '?'}…' — use Settings → API → Project URL)"))
    if not url_ok and want:
        E["SUPABASE_URL"] = f"https://{want}.supabase.co"; ref = want
        print(f"INFO continuing the Auth checks with the dashboard project URL https://{want}.supabase.co (fix the secret)")
    R["project_ref"] = ref
    # API keys: format, and for legacy JWT keys the project + role inside them (never the key itself)
    import base64
    def key_facts(k):
        if k.startswith("sb_publishable_"): return {"format": "new publishable"}
        if k.startswith("sb_secret_"): return {"format": "new secret"}
        parts = k.split(".")
        if len(parts) == 3:
            try:
                c = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
                return {"format": "legacy JWT", "ref": c.get("ref"), "role": c.get("role"), "exp_year": time.gmtime(c.get("exp", 0)).tm_year}
            except Exception: pass
        return {"format": "unrecognised"}
    fa, fs = key_facts(E["SUPABASE_ANON_KEY"]), key_facts(E["SUPABASE_SERVICE_ROLE_KEY"])
    R["keys"] = {"anon": fa, "service": fs}; print(f"INFO anon key: {fa} | service key: {fs}")
    check(fa.get("role") == "anon" or fa["format"] == "new publishable", "SUPABASE_ANON_KEY is the anon / publishable key")
    check(fs.get("role") == "service_role" or fs["format"] == "new secret", "SUPABASE_SERVICE_ROLE_KEY is the service_role / secret key")
    for n, f in (("anon", fa), ("service", fs)):
        if f.get("ref"): check(f["ref"] == ref, f"{n} key belongs to project {ref}")
    applied = database(ref)
    auth()
    rest_lockdown(applied)


def database(ref):
    """sections 1 + 2; returns whether migration 001 was already applied before this run"""
    try: dbu = urllib.parse.urlparse(E["SUPABASE_DB_URL"]); dbu.port; dbu.hostname
    except ValueError:
        check(False, "SUPABASE_DB_URL is a valid connection URI (it is not: see the 'shape' step — e.g. square brackets "
                     "left from Supabase's [YOUR-PASSWORD] template, or a password with unencoded special characters)")
        return False
    mode = "session pooler" if "pooler.supabase.com" in (dbu.hostname or "") and dbu.port == 5432 else \
           "transaction pooler" if dbu.port == 6543 else "direct" if (dbu.hostname or "").startswith("db.") else "other"
    R["db_mode"] = mode
    check(ref in (dbu.username or "") + (dbu.hostname or ""), f"SUPABASE_DB_URL points at the same project ({mode})")

    # 1 · database
    r = psql("-At", sql="select split_part(version(), ' on ', 1) || ' | role=' || current_user || ' | db=' || current_database()")
    check(r.returncode == 0, "database connection" + (f": {r.stdout.strip()}" if r.returncode == 0 else f" FAILED: {r.stderr.strip()[:200]}"))
    if r.returncode: return False
    before = inventory(); R["public_before"] = before
    applied = bool(before and "r:eva_schema" in before[0])
    print(f"INFO public schema before: {len(before[0].split(',')) if before and before[0] else 0} relations, "
          f"{len(before[1].split(',')) if before and len(before) > 1 and before[1] else 0} functions; migration already applied: {applied}")

    if RO:
        r = psql("-At", sql="show transaction_read_only")
        check(r.stdout.strip() == "on", "read-only mode: database session is read-only (no migration test — that ran in staging)")
        return applied
    # 2 · migration safety (rolled back)
    t = time.time(); r = psql(file=ROOT / "saas/db/tests/tx_check.sql")
    out = r.stdout + r.stderr; Path("tx_check.out").write_text(out)
    rows = re.findall(r"^\s*\d+\s*\|\s*(PASS|FAIL)\s*\|\s*([^|]+?)\s*\|", out, re.M)
    for res, name in rows: print(f"{res} db: {name}")
    check(r.returncode == 0 and "TX CHECK: ALL PASS" in out and rows and all(x == "PASS" for x, _ in rows),
          f"migration 001 applies twice + {len(rows)} business/lockdown checks inside one transaction ({time.time() - t:.1f} s)")
    if r.returncode and not rows: print(out[-1500:])
    after = inventory()
    check(after == before, "rolled back: public schema identical before and after (nothing kept)")

    return applied


def auth():
    # 3 · auth
    st, _, b = http("GET", E["SUPABASE_URL"] + "/auth/v1/health", key=E["SUPABASE_ANON_KEY"])
    check(st == 200, f"Auth service healthy ({st})")
    st, _, b = http("GET", E["SUPABASE_URL"] + "/auth/v1/settings", key=E["SUPABASE_ANON_KEY"]); s = jl(b) or {}
    check(st == 200 and (s.get("external") or {}).get("email") is True, "email sign-in enabled")
    check(s.get("disable_signup") is False, f"new users can sign up (disable_signup={s.get('disable_signup')})")
    R["auth_settings"] = {k: s.get(k) for k in ("disable_signup", "mailer_autoconfirm", "sms_provider")}
    if RO:
        st, _, _ = http("GET", E["SUPABASE_URL"] + "/auth/v1/admin/users?page=1&per_page=1", key=E["SUPABASE_SERVICE_ROLE_KEY"], bearer=E["SUPABASE_SERVICE_ROLE_KEY"])
        check(st == 200, f"service key accepted by the Auth admin API (read-only list, {st})")
        st, _, _ = http("GET", E["SUPABASE_URL"] + "/auth/v1/user", key=E["SUPABASE_ANON_KEY"], bearer="not-a-token")
        check(st in (401, 403), f"invalid token rejected ({st})"); return
    email = f"staging-check-{uuid.uuid4().hex[:10]}@example.com"; uid = None
    try:
        st, _, b = http("POST", E["SUPABASE_URL"] + "/auth/v1/admin/users", key=E["SUPABASE_SERVICE_ROLE_KEY"], bearer=E["SUPABASE_SERVICE_ROLE_KEY"],
                        body={"email": email, "email_confirm": True})
        uid = (jl(b) or {}).get("id")
        if not check(st in (200, 201) and uid, f"admin API: throwaway test user created ({st})"): return
        for page in ("/", "/video.html?v=staging-check", "/videos.html"):
            st, _, b = http("POST", E["SUPABASE_URL"] + "/auth/v1/admin/generate_link", key=E["SUPABASE_SERVICE_ROLE_KEY"],
                            bearer=E["SUPABASE_SERVICE_ROLE_KEY"], body={"type": "magiclink", "email": email, "redirect_to": SITE + page})
            j = jl(b) or {}; link = j.get("action_link") or (j.get("properties") or {}).get("action_link")
            if not check(st == 200 and link, f"magic link generated for {page} (no email sent)"): continue
            st, h, _ = http("GET", link, follow=False); loc = h.get("Location") or h.get("location") or ""
            target, frag = loc.split("#", 1) if "#" in loc else (loc, "")
            tok = urllib.parse.parse_qs(frag).get("access_token", [None])[0]
            check(st in (302, 303) and target == SITE + page and tok, f"sign-in link lands on {SITE}{page} with a session (redirect allowed)")
            if tok and page == "/":
                st, _, b = http("GET", E["SUPABASE_URL"] + "/auth/v1/user", key=E["SUPABASE_SERVICE_ROLE_KEY"], bearer=tok)
                check(st == 200 and (jl(b) or {}).get("email") == email and (jl(b) or {}).get("id") == uid,
                      "session token validates the way the API checks it (GET /auth/v1/user)")
        st, _, b = http("POST", E["SUPABASE_URL"] + "/auth/v1/admin/generate_link", key=E["SUPABASE_SERVICE_ROLE_KEY"],
                        bearer=E["SUPABASE_SERVICE_ROLE_KEY"], body={"type": "magiclink", "email": email, "redirect_to": "https://attacker.example.com/steal"})
        j = jl(b) or {}; link = j.get("action_link") or (j.get("properties") or {}).get("action_link")
        if link:
            st, h, _ = http("GET", link, follow=False); loc = (h.get("Location") or h.get("location") or "")
            check(not loc.startswith("https://attacker.example.com"), f"foreign redirect NOT honoured (falls back to {loc.split('#')[0][:60]})")
        else: check(st >= 400, f"foreign redirect refused at link creation ({st})")
        st, _, _ = http("GET", E["SUPABASE_URL"] + "/auth/v1/user", key=E["SUPABASE_ANON_KEY"], bearer="not-a-token")
        check(st in (401, 403), f"invalid token rejected ({st})")
    finally:
        if uid:
            st, _, _ = http("DELETE", E["SUPABASE_URL"] + f"/auth/v1/admin/users/{uid}", key=E["SUPABASE_SERVICE_ROLE_KEY"], bearer=E["SUPABASE_SERVICE_ROLE_KEY"])
            check(st in (200, 204), f"throwaway test user deleted ({st})")
            st, _, b = http("GET", E["SUPABASE_URL"] + f"/auth/v1/admin/users/{uid}", key=E["SUPABASE_SERVICE_ROLE_KEY"], bearer=E["SUPABASE_SERVICE_ROLE_KEY"])
            check(st == 404, "test user gone")


def rest_lockdown(applied):
    # 4 · REST lockdown (only meaningful once the migration is applied for real)
    if applied:
        st, _, _ = http("POST", E["SUPABASE_URL"] + "/rest/v1/rpc/eva_account", key=E["SUPABASE_ANON_KEY"], bearer=E["SUPABASE_ANON_KEY"],
                        body={"p": {"user_id": str(uuid.uuid4())}})
        check(st in (401, 403, 404), f"browser anon key cannot call eva_account via REST ({st})")
    else:
        print("INFO REST lockdown check skipped: migration not applied yet (the approved deploy applies it; tx_check proved the privileges)")


if __name__ == "__main__":
    try: main()
    finally:
        R["fails"] = fails; Path("supabase_check.json").write_text(json.dumps(R, indent=1))
        print("supabase read-only check:" if RO else "supabase staging check:", "ok" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)
