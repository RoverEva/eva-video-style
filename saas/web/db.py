"""EVA Video Studio · database access = calls to the atomic SQL functions in saas/db/*.sql (one jsonb in, jsonb out).

Supabase   production: PostgREST RPC with the service-role key (server only; Modal secret eva-supabase)
LocalPG    tests/local stack: the same functions on a local Postgres through psql (no Python driver needed)
Auth: Supabase access tokens are verified by asking Supabase Auth who they belong to (works with any signing key type);
results are cached for 60 s.
"""
import json, os, subprocess, time
import requests


class DBError(Exception): pass


class Supabase:
    def __init__(self, url=None, key=None):
        self.url = (url or os.environ["SUPABASE_URL"]).strip().rstrip("/")
        self.key = "".join((key or os.environ["SUPABASE_SERVICE_ROLE_KEY"]).split())
        self.h = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        self._users = {}

    def rpc(self, fn, **p):
        r = requests.post(f"{self.url}/rest/v1/rpc/{fn}", headers=self.h, data=json.dumps({"p": p}, default=str), timeout=30)
        if r.status_code >= 300: raise DBError(f"{fn}: HTTP {r.status_code} {r.text[:300]}")
        return r.json()

    def history(self, user_id, limit=100):
        """read-only: the user's ledger rows, newest first (service key; the browser has no table access)"""
        r = requests.get(f"{self.url}/rest/v1/ledger", headers=self.h, timeout=30,
                         params={"select": "kind,ref,credits,free,meta,created_at", "user_id": f"eq.{user_id}", "order": "created_at.desc,id.desc", "limit": str(int(limit))})
        if r.status_code >= 300: raise DBError(f"ledger: HTTP {r.status_code} {r.text[:200]}")
        return r.json()

    def user(self, token):
        """{id, email} for a valid Supabase access token, else None"""
        if not token: return None
        hit = self._users.get(token)
        if hit and hit[0] > time.time(): return hit[1]
        r = requests.get(f"{self.url}/auth/v1/user", headers={"apikey": self.key, "Authorization": f"Bearer {token}"}, timeout=15)
        u = {"id": r.json()["id"], "email": r.json().get("email")} if r.ok and r.json().get("id") else None
        if len(self._users) > 5000: self._users.clear()
        self._users[token] = (time.time() + 60, u)
        return u


class LocalPG:
    def __init__(self, dsn_args=None):
        self.args = dsn_args or ["-h", os.environ.get("EVA_PG_HOST", "/var/tmp/evapg"), "-p", os.environ.get("EVA_PG_PORT", "54329"), "-U", "postgres"]
        self.tokens = {}   # test sign-in: token → {id, email}

    def rpc(self, fn, **p):
        body = json.dumps(p, default=str)
        if "$EVA$" in body: raise DBError("bad input")
        r = subprocess.run(["psql", *self.args, "-At", "-v", "ON_ERROR_STOP=1", "-c", f"select public.{fn}($EVA${body}$EVA$::jsonb)"],
                           capture_output=True, text=True)
        if r.returncode: raise DBError(f"{fn}: {r.stderr.strip()[:300]}")
        out = r.stdout.strip()
        return json.loads(out) if out else None

    def history(self, user_id, limit=100):
        import uuid; uid = str(uuid.UUID(str(user_id)))   # validated before it goes into SQL
        q = (f"select coalesce(json_agg(x), '[]') from (select kind, ref, credits, free, meta, created_at from public.ledger "
             f"where user_id = '{uid}' order by created_at desc, id desc limit {int(limit)}) x")
        r = subprocess.run(["psql", *self.args, "-At", "-v", "ON_ERROR_STOP=1", "-c", q], capture_output=True, text=True)
        if r.returncode: raise DBError(f"ledger: {r.stderr.strip()[:300]}")
        return json.loads(r.stdout.strip() or "[]")

    def user(self, token): return self.tokens.get(token)


def from_env():
    if os.environ.get("EVA_LOCAL_PG"): return LocalPG()
    return Supabase()
