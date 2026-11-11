#!/usr/bin/env python3
"""Web API reliability against a real Postgres (same SQL functions as Supabase), with a fake store and fake Modal spawn.

    EVA_PG_HOST=/var/tmp/evapg EVA_PG_PORT=54329 python3 saas/tests/test_api_reliability.py

1. Render-start failure (Modal error) → HTTP 503 with a clear message, version failed, free preview / credits back at once.
2. Render-start hang (longer than EVA_SPAWN_TIMEOUT) → same, within the timeout; a render that starts late skips the
   released version; releasing twice is a no-op (idempotent); the person can try again.
3. HD export start failure → credits back; a new HD request for the same version is accepted.
4. Blocking work runs off the event loop: while one request waits on a slow Supabase/Modal call, other requests
   (quote, version polling) still answer immediately.
5. Normal path unchanged: preview starts, charge recorded, render handed over once; Server-Timing header present.
"""
import asyncio, os, sys, threading, time, uuid
from pathlib import Path
os.environ["EVA_SPAWN_TIMEOUT"] = "1.0"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
import db as D, api_v2
import json
from starlette.applications import Starlette

PG = D.LocalPG(); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)


class Store:   # the upload exists; nothing else is needed for these paths
    def size(self, key): return 1000
    def url(self, key, **k): return "https://r2.invalid/" + key
    def get_json(self, key): return None


class Spawn:
    def __init__(self): self.mode, self.calls, self.delay = "ok", [], 0
    def __call__(self, kind, vid):
        self.calls.append((kind, vid))
        if self.delay: time.sleep(self.delay)
        if self.mode == "error": raise ConnectionError("modal unavailable")
        if self.mode == "hang": time.sleep(3)


SP = Spawn(); acc = api_v2.Accounts(PG, Store(), {}, SP)
USERS = {}
class Auth:   # the API checks bearer tokens with the database object
    def __getattr__(self, k): return getattr(PG, k)
    def user(self, token): return USERS.get(token)
acc.db = Auth()
app = Starlette(routes=api_v2.routes(acc, lambda req: "https://eva-video-studio.vercel.app"))


class Resp:
    def __init__(self, status, headers, body): self.status_code, self.headers, self._b = status, headers, body
    def json(self): return json.loads(self._b or b"{}")


class Client:   # minimal in-process ASGI client (no network, no extra packages)
    async def req(self, method, path, headers=None, json_body=None):
        path, _, qs = path.partition("?"); body = json.dumps(json_body).encode() if json_body is not None else b""
        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method, "scheme": "http", "path": path,
                 "raw_path": path.encode(), "query_string": qs.encode(), "root_path": "", "server": ("t", 80), "client": ("c", 1),
                 "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()] + [(b"content-type", b"application/json")]}
        sent, out = [False], {"status": 0, "headers": {}, "body": b""}
        async def receive():
            if not sent[0]: sent[0] = True; return {"type": "http.request", "body": body, "more_body": False}
            await asyncio.sleep(3600)
        async def send(m):
            if m["type"] == "http.response.start": out["status"] = m["status"]; out["headers"] = {k.decode(): v.decode() for k, v in m["headers"]}
            elif m["type"] == "http.response.body": out["body"] += m.get("body", b"")
        await app(scope, receive, send); return Resp(out["status"], out["headers"], out["body"])
    async def post(self, path, headers=None, json=None): return await self.req("POST", path, headers, json)
    async def get(self, path, headers=None): return await self.req("GET", path, headers)


def user():
    uid = str(uuid.uuid4()); PG.rpc("eva_account", user_id=uid); tok = uuid.uuid4().hex
    USERS[tok] = {"id": uid, "email": f"{uid[:8]}@example.com"}; return uid, {"Authorization": f"Bearer {tok}"}


def project(uid):
    pid = "p" + uuid.uuid4().hex[:11]
    PG.rpc("eva_create_project", id=pid, user_id=uid, title="Rel", upload_key=f"uploads/{pid}/input.mp4", upload_bytes=1000, source_days=30)
    return pid


OPTS = {"aspect": "9:16", "templates": ["T23"], "template_mode": "single", "music": "mix"}
def me(uid): return PG.rpc("eva_account", user_id=uid)
def status(vid): return (PG.rpc("eva_version", version_id=vid) or {}).get("status")


async def main():
    c = Client()
    if True:
        # 5. normal path
        uid, H = user(); pid = project(uid); SP.mode = "ok"; SP.calls.clear()
        r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS); j = r.json()
        check(r.status_code == 200 and j["charge"]["type"] == "free" and SP.calls == [("preview", j["version"])] and status(j["version"]) == "queued"
              and "app;dur=" in r.headers.get("server-timing", ""), f"normal start: free preview, handed to Modal once, Server-Timing {r.headers.get('server-timing')}")
        PG.rpc("eva_finish", version_id=j["version"], status="done", retain_days=30)

        # 1. Modal error → released at once
        SP.mode = "error"; a0 = me(uid)
        r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS); a1 = me(uid)
        vid = SP.calls[-1][1]
        check(r.status_code == 503 and "Nothing was charged" in r.json()["error"], f"Modal error → 503 '{r.json().get('error')}'")
        check(status(vid) == "failed" and a1["free_held"] == 0 and a1["free_used"] == a0["free_used"] and a1["free_left"] == a0["free_left"],
              f"Modal error: version failed, free preview returned at once (free_left {a0['free_left']} → {a1['free_left']}, held {a1['free_held']})")
        again = PG.rpc("eva_finish", version_id=vid, status="failed", retain_days=0, error="again")
        check(again.get("duplicate") is True and me(uid) == a1 and status(vid) == "failed", "releasing twice is a no-op (idempotent), balance unchanged")

        # 2. Modal hang → released within the timeout; late render skips; retry works
        SP.mode = "hang"; t = time.time()
        r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS); dt = time.time() - t; vid = SP.calls[-1][1]
        check(r.status_code == 503 and dt < 2.5 and status(vid) == "failed" and me(uid)["free_held"] == 0,
              f"Modal hang → 503 after {dt:.1f} s (limit 1 s + overhead), reservation released")
        v = PG.rpc("eva_version", version_id=vid); check(v["status"] not in ("queued", "running"), "a render that starts late finds the version released and skips it")
        SP.mode = "ok"; r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS)
        check(r.status_code == 200, "trying again right after works")
        PG.rpc("eva_finish", version_id=r.json()["version"], status="done", retain_days=30); src = r.json()["version"]

        # paid preview + HD: credits come back on start failure
        PG.rpc("eva_topup", user_id=uid, session_id="cs_test_" + uuid.uuid4().hex, credits=100, amount_cents=999)
        while me(uid)["free_left"] > 0:
            r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS); PG.rpc("eva_finish", version_id=r.json()["version"], status="done", retain_days=30)
        c0 = me(uid)["credits"]; SP.mode = "error"
        r = await c.post(f"/api/v2/projects/{pid}/previews", headers=H, json=OPTS)
        check(r.status_code == 503 and me(uid)["credits"] == c0, f"paid preview start failure: credits back ({c0} → {me(uid)['credits']})")
        r = await c.post(f"/api/v2/versions/{src}/hd", headers=H)
        check(r.status_code == 503 and me(uid)["credits"] == c0, f"HD start failure: credits back ({me(uid)['credits']})")
        SP.mode = "ok"; r = await c.post(f"/api/v2/versions/{src}/hd", headers=H); j = r.json()
        check(r.status_code == 200 and j["charge"]["amount"] > 0 and me(uid)["credits"] == c0 - j["charge"]["amount"], f"HD request accepted again after the failed start (charged {j['charge']['amount']})")

        # 4. slow dependency does not block other requests
        uid2, H2 = user(); pid2 = project(uid2); SP.mode = "ok"; SP.delay = 0.9
        slow = asyncio.create_task(c.post(f"/api/v2/projects/{pid2}/previews", headers=H2, json=OPTS)); await asyncio.sleep(0.1)
        t = time.time(); q = await c.get("/api/v2/quote?duration=20", headers=H); v = await c.get(f"/api/v2/versions/{src}", headers=H); fast = time.time() - t
        r = await slow; SP.delay = 0
        check(q.status_code == 200 and v.status_code == 200 and fast < 0.6 and r.status_code == 200,
              f"while a render start waits 0.9 s, quote + version polling answer in {fast:.2f} s (not blocked)")
        r = await c.get(f"/api/v2/versions/{src}", headers=H2); check(r.status_code == 404, "another user still cannot read the version")

asyncio.run(main())
print("api reliability:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
