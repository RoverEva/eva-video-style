#!/usr/bin/env python3
"""31–60 s videos for TEST ACCOUNTS ONLY, end to end against saas/tests/local_stack.py (real API code, real SQL money
functions on local Postgres, real render pipeline). The stack must run with EVA_LONG_VIDEO_EMAILS=long@example.com.

    python3 saas/tests/test_long_video.py VIDEO_45S.mp4 [API]

Checks: a normal account is still refused over 30 s; the test account gets 60 s, quote 18 / 66; a 45 s preview renders
(free), its HD export is charged 66, renders full length and downloads; a failed 31–60 s HD refunds its 66 credits; a
failed paid 31–60 s preview refunds its 18 credits; free-preview count and balance end where they should.
"""
import json, subprocess, sys, time, uuid
from pathlib import Path
import requests

VIDEO = Path(sys.argv[1]); API = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
O = {"Origin": "http://127.0.0.1:8080"}; fails = []
PG = ["psql", "-h", "/var/tmp/evapg", "-p", "54329", "-U", "postgres", "-At", "-c"]
OPTS = {"aspect": "9:16", "templates": ["T17"], "template_mode": "single", "music": "none"}
def check(c, m, d=None):
    print(("PASS " if c else "FAIL ") + m + (f"  {d}" if d is not None else ""), flush=True)
    if not c: fails.append(m)
def signin(email): return {"Authorization": "Bearer " + requests.get(f"{API}/_local_signin", params={"email": email}).json()["access_token"], **O}
def call(h, m, p, **k): return requests.request(m, API + "/api/v2" + p, headers=h, timeout=60, **k)
def sql(q): return subprocess.run(PG + [q], capture_output=True, text=True).stdout.strip()
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VIDEO)], capture_output=True, text=True).stdout)
data = VIDEO.read_bytes()
def upload(h, name):
    r = call(h, "POST", "/projects", json={"name": name, "size": len(data), "type": "video/mp4", "duration": dur})
    if r.status_code != 200: return r
    j = r.json(); requests.put(j["put_url"], data=data, headers={"Content-Type": "video/mp4"}).raise_for_status(); return j
def wait(h, vid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = call(h, "GET", f"/versions/{vid}").json()
        if v["status"] not in ("queued", "running"): return v
        time.sleep(3)
    raise SystemExit("timeout")
me = lambda h: call(h, "GET", "/me").json()

N = signin(f"normal-{uuid.uuid4().hex[:6]}@example.com")
r = call(N, "POST", "/projects", json={"name": "too long", "size": len(data), "type": "video/mp4", "duration": dur})
check(r.status_code == 400 and "30 seconds" in r.text and me(N)["max_seconds"] == 30, f"normal account: {dur:.1f} s refused, limit stays 30 s", r.json().get("error"))

L = signin("long@example.com"); a = me(L)
check(a["max_seconds"] == 60, "test account: limit 60 s")
q = call(L, "GET", f"/quote?duration={dur}").json(); q30 = call(L, "GET", "/quote?duration=30").json()
check(q == {"preview": 18, "hd": 66} and q30 == {"preview": 15, "hd": 52}, f"prices: {dur:.0f} s → {q}, 30 s unchanged → {q30}")
uid = sql("select user_id from accounts where email='long@example.com'")
sql(f"select public.eva_topup('{{\"user_id\":\"{uid}\",\"session_id\":\"long-test-{uuid.uuid4().hex[:6]}\",\"credits\":200,\"amount_cents\":0,\"livemode\":false}}'::jsonb)")
c0, f0 = me(L)["credits"], me(L)["free_left"]

# 1 · 45 s preview (free) → HD export charged 66, full length, downloadable
p1 = upload(L, "long 45 s"); v = call(L, "POST", f"/projects/{p1['project']}/previews", json=OPTS).json()["version"]
pv = wait(L, v); check(pv["status"] == "done" and me(L)["free_left"] == f0 - 1 and me(L)["credits"] == c0, f"45 s preview done, free preview used, no credits ({pv['status']})", pv.get("error"))
r = call(L, "POST", f"/versions/{v}/hd").json(); h = r.get("version")
check(r.get("charge", {}).get("amount") == 66 and me(L)["credits"] == c0 - 66, "HD of a 45 s video charged 66", r.get("charge"))
hv = wait(L, h); dl = (call(L, "GET", f"/versions/{h}").json() or {}).get("download_url")
ok = False
if hv["status"] == "done" and dl:
    Path("/tmp/long_hd.mp4").write_bytes(requests.get(dl, timeout=300).content)
    d2 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "/tmp/long_hd.mp4"], capture_output=True, text=True).stdout or 0)
    ok = abs(d2 - dur) < 0.6
check(ok and me(L)["credits"] == c0 - 66, f"45 s HD rendered full length and downloaded ({hv['status']})", hv.get("error"))

# 2 · failed 31–60 s HD → 66 refunded
p2 = upload(L, "long 45 s b"); v2 = call(L, "POST", f"/projects/{p2['project']}/previews", json=OPTS).json()["version"]; wait(L, v2)
sql(f"update projects set title = 'e2e-fail long hd' where id = '{p2['project']}'")
cb = me(L)["credits"]; h2 = call(L, "POST", f"/versions/{v2}/hd").json()["version"]; held = me(L)["credits"]
x = wait(L, h2)
check(cb - held == 66 and x["status"] == "failed" and me(L)["credits"] == cb, "failed 31–60 s HD: 66 held, then refunded", {"held": cb - held, "status": x["status"]})

# 3 · failed PAID 31–60 s preview → 18 refunded (the last free preview is held by a running preview, then cancelled)
p4 = upload(L, "long hold"); hold = call(L, "POST", f"/projects/{p4['project']}/previews", json=OPTS).json()["version"]
cb = me(L)["credits"]; p3 = upload(L, "e2e-fail long preview")
r = call(L, "POST", f"/projects/{p3['project']}/previews", json=OPTS).json(); held = me(L)["credits"]
x = wait(L, r["version"]); call(L, "POST", f"/versions/{hold}/cancel"); time.sleep(3)
check(cb - held == 18 and x["status"] == "failed" and me(L)["credits"] == cb, "failed paid 31–60 s preview: 18 held, then refunded", {"held": cb - held, "status": x["status"]})
end = me(L)
check(end["credits"] == c0 - 66 and end["free_left"] == f0 - 2, f"end state: credits {end['credits']} (= start − one HD), free previews {end['free_left']} (2 used)")
print("long video:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
