#!/usr/bin/env python3
"""Release test of the account features against the DEPLOYED stack (Modal API + workers, R2, Supabase, Stripe TEST mode).
Run by the deploy workflow after an approved deploy; uses throwaway test users (e2e-<run>@example.com) that
it deletes at the end. No real customer data is read or changed.

    python3 saas/tests/live_accounts_e2e.py API_URL SITE_URL VIDEO OUT.json
    env: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, STRIPE_SECRET_KEY (test)

Credits for the test user come from a labelled grant (ledger ref e2e-grant-<run>), because Stripe's hosted card form
can't be automated; the Checkout Session itself is created through the API and verified with Stripe.
"""
import json, os, secrets, subprocess, sys, tempfile, time, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

API, SITE, VIDEO, OUT = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"), Path(sys.argv[3]), Path(sys.argv[4])
SB, ANON, SVC = os.environ["SUPABASE_URL"].strip().rstrip("/"), "".join(os.environ["SUPABASE_ANON_KEY"].split()), "".join(os.environ["SUPABASE_SERVICE_ROLE_KEY"].split())
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "web")); import db as D, stripe_lite
DB = D.Supabase(SB, SVC); RUN = uuid.uuid4().hex[:8]; USERS = []; E = {"run": RUN, "checks": {}, "timings": {}}
O = {"Origin": SITE}; OPTS = {"aspect": "9:16", "templates": ["T23", "T21"], "template_mode": "multi", "music": "mix"}


def check(name, cond, detail=None):
    E["checks"][name] = {"ok": bool(cond), "detail": detail}; print(("PASS " if cond else "FAIL ") + name + (f": {detail}" if detail is not None else ""), flush=True)
    if not cond: raise AssertionError(name)


def signin(tag):
    email, pw = f"e2e-{RUN}-{tag}@example.com", secrets.token_urlsafe(18)
    r = requests.post(f"{SB}/auth/v1/admin/users", headers={"apikey": SVC, "Authorization": f"Bearer {SVC}"}, json={"email": email, "password": pw, "email_confirm": True}, timeout=30)
    r.raise_for_status(); USERS.append(r.json()["id"])
    t = requests.post(f"{SB}/auth/v1/token?grant_type=password", headers={"apikey": ANON}, json={"email": email, "password": pw}, timeout=30).json()["access_token"]
    return {"Authorization": f"Bearer {t}", **O}, r.json()["id"]


REQS = []   # per-request timing: every API call is recorded (method, path, status, seconds); slow ones are printed


def call(h, m, path, **kw):
    t = time.time(); rec = {"t": time.strftime("%H:%M:%S", time.gmtime(t)), "m": m, "path": path}; REQS.append(rec)
    try:
        r = requests.request(m, API + "/api/v2" + path, headers=h, timeout=60, **kw)
        rec.update(status=r.status_code, s=round(time.time() - t, 2), modal_call=r.headers.get("modal-function-call-id"))
        if rec["s"] > 5: print(f"SLOW {m} {path} → {r.status_code} in {rec['s']} s", flush=True)
        return r
    except requests.RequestException as e:
        rec.update(status=type(e).__name__, s=round(time.time() - t, 2))
        print(f"REQUEST FAILED {m} {path} after {rec['s']} s: {type(e).__name__} (started {rec['t']} UTC)", flush=True); raise


def probe_duration(f):   # the real length of the test clip, as the website measures it before uploading
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True, check=True).stdout
    return round(float(out.strip()), 2)


DUR = probe_duration(VIDEO)


def upload(h, name, dur=None):
    dur = DUR if dur is None else dur
    data = VIDEO.read_bytes(); j = call(h, "POST", "/projects", json={"name": name, "size": len(data), "type": "video/mp4", "duration": dur}).json()
    requests.put(j["put_url"], data=data, headers={"Content-Type": "video/mp4", **O}, timeout=300).raise_for_status(); return j


def wait(h, vid, timeout=1500):
    t0, seen = time.time(), []
    while time.time() - t0 < timeout:
        v = call(h, "GET", f"/versions/{vid}").json()
        if v.get("progress"): seen.append(v["progress"].get("progress"))
        if v["status"] not in ("queued", "running"): return v, round(time.time() - t0, 1), seen
        time.sleep(3)
    raise AssertionError(f"timeout {vid}")


def main():
    A, a_id = signin("a"); B, _ = signin("b")
    check("sign-in required", call(O, "GET", "/me").status_code == 401)
    me = call(A, "GET", "/me").json(); check("new account: 3 free previews, 0 credits", me["free_left"] == 3 and me["credits"] == 0, me)
    # expected prices come from the server's own quote for the clip's real duration (12-15 preview / 38-52 HD by length)
    Q = call(A, "GET", f"/quote?duration={DUR}").json(); PV, HD = Q["preview"], Q["hd"]; E["clip"] = {"duration_s": DUR, "preview": PV, "hd": HD}
    check("quote matches the duration formula", 12 <= PV <= 15 and 38 <= HD <= 52, {"duration_s": DUR, **Q})
    p = upload(A, "Release test"); check("costs shown before generating", p["costs"] == {"preview": PV, "hd": HD}, p["costs"])
    r = call(A, "POST", f"/projects/{p['project']}/previews", json=OPTS).json(); v1 = r["version"]; check("preview 1 is free", r["charge"]["type"] == "free", r["charge"])
    v, secs, prog = wait(A, v1); E["timings"]["preview_1_s"] = secs
    check("preview 1 done on Modal with thumbnail + signed video", v["status"] == "done" and v.get("thumb_url") and v.get("video_url"), v.get("error"))
    check("progress monotonic", all(b >= a for a, b in zip(prog, prog[1:])), sorted(set(prog))[:10])
    row = DB.rpc("eva_version", version_id=v1); E["cost_preview_1"] = row.get("cost"); E["qa_preview_1"] = row.get("qa")
    r = call(A, "POST", f"/projects/{p['project']}/previews", json={}).json(); v2 = r["version"]; v, secs, _ = wait(A, v2); E["timings"]["preview_2_s"] = secs
    row2 = DB.rpc("eva_version", version_id=v2); E["cost_preview_2"] = row2.get("cost")
    check("version 2 reused the cached transcript (no second ASR)", (row2.get("cost") or {}).get("asr_cached") is True, row2.get("cost"))
    u = v["video_url"]; check("signed R2 link works, bare object refused", requests.get(u, headers={"Range": "bytes=0-99"}).status_code in (200, 206)
                              and requests.get(u.split("?")[0]).status_code in (400, 401, 403))
    check("other user cannot read or export", call(B, "GET", f"/versions/{v1}").status_code == 404 and call(B, "POST", f"/versions/{v1}/hd").status_code in (404, 409))
    pf = upload(A, "e2e-fail release"); r = call(A, "POST", f"/projects/{pf['project']}/previews", json=OPTS).json(); v, _, _ = wait(A, r["version"])
    check("failed render releases the free preview", v["status"] == "failed" and call(A, "GET", "/me").json()["free_left"] == 1, v.get("error"))
    t = call(A, "POST", "/topup", json={"return_to": f"/video.html?v={v1}"}).json(); sid = t["url"].split("/pay/")[1].split("#")[0]
    s = stripe_lite.call("GET", f"/checkout/sessions/{sid}")
    check("top-up Checkout: TEST mode, $9.99, 100 credits, returns to the selected video", s["livemode"] is False and s["amount_total"] == 999 and s["metadata"]["type"] == "topup"
          and s["metadata"]["credits"] == "100" and f"/video.html?v={v1}" in s["success_url"], {"status": s["status"]})
    DB.rpc("eva_topup", user_id=a_id, session_id=f"e2e-grant-{RUN}", credits=100, amount_cents=0, livemode=False)   # labelled test grant
    r = call(A, "POST", f"/versions/{v1}/hd").json(); h = r["version"]; check(f"HD export of the older version charged {HD}", r["charge"]["amount"] == HD and call(A, "GET", "/me").json()["credits"] == 100 - HD, r)
    check("second HD request = same export, no charge", call(A, "POST", f"/versions/{v1}/hd").json().get("existing") == h and call(A, "GET", "/me").json()["credits"] == 100 - HD)
    v, secs, _ = wait(A, h); E["timings"]["hd_s"] = secs; rowh = DB.rpc("eva_version", version_id=h); E["cost_hd"] = rowh.get("cost"); E["qa_hd"] = rowh.get("qa")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "hd.mp4"; f.write_bytes(requests.get(v["download_url"], timeout=300).content)
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", f], capture_output=True, text=True).stdout)
    vs = next(x for x in pr["streams"] if x["codec_type"] == "video")
    check("HD 1080x1920 full length, downloaded", (vs["width"], vs["height"]) == (1080, 1920) and float(pr["format"]["duration"]) > 9.5, [vs["width"], vs["height"], pr["format"]["duration"]])
    # paid preview that fails → its credits are refunded (the last free preview is held by a running preview, then cancelled)
    hold = call(A, "POST", f"/projects/{upload(A, 'e2e-hold')['project']}/previews", json=OPTS).json()["version"]
    c0 = call(A, "GET", "/me").json()["credits"]
    r = call(A, "POST", f"/projects/{upload(A, 'e2e-fail paid')['project']}/previews", json=OPTS).json()
    c1 = call(A, "GET", "/me").json()["credits"]; v, _, _ = wait(A, r["version"]); call(A, "POST", f"/versions/{hold}/cancel")
    check(f"failed paid preview: {PV} credits charged, then refunded", c0 - c1 == PV and v["status"] == "failed" and call(A, "GET", "/me").json()["credits"] == c0,
          {"charged": c0 - c1, "status": v["status"]})
    # My Account: purchase/charge history (read-only view of the ledger; needs the service key to read the table)
    hist = call(A, "GET", "/history"); items = hist.json().get("items", []) if hist.status_code == 200 else []
    check("My Account history: grant, charges and refunds listed", hist.status_code == 200 and any(i["type"] == "purchase" for i in items)
          and any(i["status"] == "refunded" for i in items) and call(O, "GET", "/history").status_code == 401, {"status": hist.status_code, "n": len(items)})
    C, _ = signin("c"); projs =[upload(C, f"c{i}")["project"] for i in range(6)]
    def start(pid):   # a response lost in transit (seen once: server 200 in 0.5 s, client ReadTimeout) is reconciled below
        try: return call(C, "POST", f"/projects/{pid}/previews", json=OPTS)
        except requests.RequestException as e: return e
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(start, projs))
    codes = [x.status_code if hasattr(x, "status_code") else type(x).__name__ for x in res]
    lib = call(C, "GET", "/library").json()["projects"]   # server truth: which of the 6 projects actually started a preview
    started = [v["id"] for pr in lib if pr["id"] in projs for v in pr.get("versions", [])]
    E["parallel_6"] = {"codes": codes, "server_started": len(started), "lost_responses": sum(not isinstance(c, int) for c in codes)}
    for vid in started: call(C, "POST", f"/versions/{vid}/cancel")
    time.sleep(5)
    check("6 parallel previews → exactly 3 free starts (server state); cancels release them",
          len(started) == 3 and codes.count(200) + codes.count(402) + E["parallel_6"]["lost_responses"] == 6 and call(C, "GET", "/me").json()["free_left"] == 3, E["parallel_6"])
    d = call(A, "POST", f"/versions/{v2}/delete").json(); check("delete removes files", d["ok"] and requests.get(u).status_code in (403, 404), d)
    E["ok"] = True


if __name__ == "__main__":
    try: main()
    except Exception as e: E["ok"] = False; E["error"] = f"{type(e).__name__}: {e}"
    finally:
        for uid in USERS:   # remove the test users' data and accounts
            try:
                for pr in DB.rpc("eva_library", user_id=uid): DB.rpc("eva_delete", user_id=uid, project_id=pr["id"])
                requests.delete(f"{SB}/auth/v1/admin/users/{uid}", headers={"apikey": SVC, "Authorization": f"Bearer {SVC}"}, timeout=30)
            except Exception: pass
        ok = [x["s"] for x in REQS if isinstance(x.get("status"), int)]
        E["requests"] = {"n": len(REQS), "p50_s": sorted(ok)[len(ok) // 2] if ok else None, "max_s": max(ok) if ok else None,
                         "slow": [x for x in REQS if not isinstance(x.get("status"), int) or x["s"] > 5], "last": REQS[-3:]}
        OUT.write_text(json.dumps(E, indent=1, default=str)); print(json.dumps({k: E[k] for k in E if k != "checks"}, indent=1, default=str))
        sys.exit(0 if E.get("ok") else 1)
