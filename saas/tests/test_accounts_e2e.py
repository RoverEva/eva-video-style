#!/usr/bin/env python3
"""Account features end to end over HTTP against saas/tests/local_stack.py (real pipeline renders, local Postgres,
local storage, signed fake Stripe webhooks). Writes a JSON evidence report.

    python3 saas/tests/test_accounts_e2e.py VIDEO.mp4 OUT.json [API=http://127.0.0.1:8000]
"""
import json, subprocess, sys, tempfile, time, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

VIDEO, OUT = Path(sys.argv[1]), Path(sys.argv[2]); API = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:8000"
ORIGIN = {"Origin": "http://127.0.0.1:8080"}
E = {"checks": {}, "timings": {}}
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "web")); import db as DBM
PG = DBM.LocalPG()


def check(name, cond, detail=None):
    E["checks"][name] = {"ok": bool(cond), "detail": detail}; print(("PASS " if cond else "FAIL ") + name + (f": {detail}" if detail is not None else ""), flush=True)
    if not cond: OUT.write_text(json.dumps(E, indent=1, default=str)); sys.exit(f"failed: {name}")


def signin(email): return {"Authorization": "Bearer " + requests.get(f"{API}/_local_signin", params={"email": email}).json()["access_token"], **ORIGIN}


def call(h, method, path, **kw): return requests.request(method, API + "/api/v2" + path, headers=h, timeout=60, **kw)


def upload(h, name, dur=10.0, path=VIDEO):
    data = path.read_bytes(); r = call(h, "POST", "/projects", json={"name": name, "size": len(data), "type": "video/mp4", "duration": dur}); r.raise_for_status(); j = r.json()
    requests.put(j["put_url"], data=data, headers={"Content-Type": "video/mp4"}).raise_for_status(); return j


def wait(h, vid, timeout=900):
    t0, seen = time.time(), []
    while time.time() - t0 < timeout:
        v = call(h, "GET", f"/versions/{vid}").json()
        if v.get("progress"): seen.append(v["progress"].get("progress"))
        if v["status"] not in ("queued", "running"): return v, round(time.time() - t0, 1), seen
        time.sleep(2)
    raise SystemExit(f"timeout {vid}")


OPTS = {"aspect": "9:16", "templates": ["T23", "T21"], "template_mode": "multi", "music": "mix"}


def main():
    run = uuid.uuid4().hex[:6]
    A, B = signin(f"a-{run}@example.com"), signin(f"b-{run}@example.com")
    check("sign-in required", call({**ORIGIN}, "GET", "/me").status_code == 401)
    me = call(A, "GET", "/me").json(); check("new account: 3 free previews, 0 credits", me["free_left"] == 3 and me["credits"] == 0, me)
    q = call(A, "GET", "/quote", params={"duration": 10}).json(); q30 = call(A, "GET", "/quote", params={"duration": 30}).json()
    check("costs: preview 12-15, HD 38-52 by duration", (q["preview"], q["hd"], q30["preview"], q30["hd"]) == (13, 43, 15, 52), [q, q30])

    p = upload(A, "Blue shirt demo"); check("project created, costs shown before generating", p["costs"] == {"preview": 13, "hd": 43}, p["costs"])
    r = call(A, "POST", f"/projects/{p['project']}/previews", json=OPTS).json(); v1 = r["version"]
    check("preview 1 uses a free preview", r["charge"] == {"type": "free", "amount": 0}, r["charge"])
    dup = call(A, "POST", f"/projects/{p['project']}/previews", json=OPTS); check("second request while rendering refused", dup.status_code == 409, dup.json().get("error"))
    v, secs, prog = wait(A, v1); E["timings"]["preview_1_s"] = secs
    check("preview 1 done with thumbnail, video, plan, expiry", v["status"] == "done" and v.get("thumb_url") and v.get("video_url") and v.get("expires_at"), {k: v.get(k) for k in ("status", "expires_at")})
    check("progress observed and never decreased", len(prog) > 3 and all(b >= a for a, b in zip(prog, prog[1:])), sorted(set(prog))[:12])
    q = v.get("qa") or {}; E["qa_preview_1"] = {k: (q.get(k) or {}).get("status") if k in ("pre", "post") else q.get(k) for k in ("status", "mode", "pre", "post")}
    check("QA ran before and after rendering (report mode) and is saved with the version",
          q.get("mode") == "report" and (q.get("pre") or {}).get("status") in ("pass", "warn", "fail") and (q.get("post") or {}).get("status") in ("pass", "warn", "fail")
          and PG.rpc("eva_version", version_id=v1).get("qa_key") == f"versions/{v1}/qa-report.json", E["qa_preview_1"])
    check("QA warnings do not block delivery in report mode", v["status"] == "done", q.get("status"))

    r = call(A, "POST", f"/projects/{p['project']}/previews", json={}).json(); v2 = r["version"]   # regenerate: same settings
    v, secs, _ = wait(A, v2); E["timings"]["preview_2_cached_s"] = secs
    lib = call(A, "GET", "/library").json(); proj = lib["projects"][0]
    check("regenerate: version 2 under the same project, same settings", len(proj["versions"]) == 2 and proj["versions"][0]["options"] == proj["versions"][1]["options"],
          [x["n"] for x in proj["versions"]])
    vv2 = PG.rpc("eva_version", version_id=v2); check("version 2 reused the cached transcript (no second ASR)", (vv2.get("cost") or {}).get("asr_cached") is True, vv2.get("cost"))
    check("free previews left: 1", call(A, "GET", "/me").json()["free_left"] == 1)

    # privacy between users
    check("user B cannot see A's version", call(B, "GET", f"/versions/{v1}").status_code == 404)
    check("user B's library is empty", call(B, "GET", "/library").json()["projects"] == [])
    check("user B cannot render on A's project", call(B, "POST", f"/projects/{p['project']}/previews", json=OPTS).status_code in (404, 409))
    check("user B cannot export A's version", call(B, "POST", f"/versions/{v1}/hd").status_code in (404, 409))
    check("user B cannot delete A's version", call(B, "POST", f"/versions/{v1}/delete").json().get("deleted_files", 0) == 0 and call(A, "GET", f"/versions/{v1}").status_code == 200)
    u = call(A, "GET", f"/versions/{v1}").json()["video_url"]
    check("files only through signed links (local store stands in for R2)", "/_local/versions/" in u)

    # failure and cancel never consume a free preview
    pf = upload(A, "e2e-fail clip"); r = call(A, "POST", f"/projects/{pf['project']}/previews", json=OPTS).json()
    v, _, _ = wait(A, r["version"]); check("failed render releases the free preview", v["status"] == "failed" and call(A, "GET", "/me").json()["free_left"] == 1, v.get("error"))
    pc = upload(A, "cancel me"); r = call(A, "POST", f"/projects/{pc['project']}/previews", json=OPTS).json()
    c = call(A, "POST", f"/versions/{r['version']}/cancel").json(); time.sleep(3)
    check("canceled render releases the free preview", c.get("status") == "canceled" and call(A, "GET", "/me").json()["free_left"] == 1, c)

    # third free preview, then credits are required
    p3 = upload(A, "third"); r = call(A, "POST", f"/projects/{p3['project']}/previews", json=OPTS).json(); wait(A, r["version"])
    r4 = call(A, "POST", f"/projects/{p3['project']}/previews", json={})
    check("4th preview refused: lifetime limit, no credits, exact cost shown", r4.status_code == 402 and r4.json()["need"] == 13, r4.json().get("error"))

    # top-up through (fake) Stripe Checkout; webhook delivered twice
    t = call(A, "POST", "/topup", json={"return_to": f"/video.html?v={v1}"}).json()
    page = requests.get(t["url"], allow_redirects=False)
    check("top-up returns to the selected video", page.status_code in (302, 307) and f"/video.html?v={v1}" in page.headers.get("location", "") and "topup=done" in page.headers["location"], page.headers.get("location"))
    me = call(A, "GET", "/me").json(); check("100 credits added once (webhook replay ignored)", me["credits"] == 100, me)

    # HD export of the OLDER version (v1), from the source + its saved configuration
    r = call(A, "POST", f"/versions/{v1}/hd").json(); h = r["version"]
    check("HD export charged 43 credits", r["charge"] == {"type": "credits", "amount": 43} and call(A, "GET", "/me").json()["credits"] == 57, r)
    r2 = call(A, "POST", f"/versions/{v1}/hd").json(); check("second HD request = same export, no charge", r2.get("existing") == h and call(A, "GET", "/me").json()["credits"] == 57, r2)
    v, secs, _ = wait(A, h, 1800); E["timings"]["hd_export_s"] = secs
    check("HD done with download link", v["status"] == "done" and v.get("download_url"), v.get("error"))
    hdv = PG.rpc("eva_version", version_id=h)
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "hd.mp4"; f.write_bytes(requests.get(v["download_url"]).content)
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", f], capture_output=True, text=True).stdout)
    vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
    qh = hdv.get("qa") or {}; E["qa_hd"] = {"status": qh.get("status"), "pre_reused": (qh.get("pre") or {}).get("reused"), "post": (qh.get("post") or {}).get("status")}
    check("HD export: post-render QA on the HD master, pre-render report reused (same plan)", (qh.get("post") or {}).get("status") in ("pass", "warn", "fail") and (qh.get("pre") or {}).get("reused") is True, E["qa_hd"])
    check("HD is full 1080x1920, full length, from the saved version's plan", (vs["width"], vs["height"]) == (1080, 1920) and float(pr["format"]["duration"]) > 9.5
          and (hdv.get("report") or {}).get("width") == 1080, {"w": vs["width"], "h": vs["height"], "s": pr["format"]["duration"]})
    r3 = call(A, "POST", f"/versions/{v1}/hd").json(); check("re-download of purchased HD is free", r3.get("existing") == h and call(A, "GET", "/me").json()["credits"] == 57)

    # concurrency through the API: 10 parallel previews, 0 credits, 3 free → exactly 3 start
    C = signin(f"c-{run}@example.com"); projs = [upload(C, f"c{i}")["project"] for i in range(10)]
    with ThreadPoolExecutor(10) as ex: res = list(ex.map(lambda pid: call(C, "POST", f"/projects/{pid}/previews", json=OPTS), projs))
    started = [x.json()["version"] for x in res if x.status_code == 200]
    for vid in started: call(C, "POST", f"/versions/{vid}/cancel")
    check("10 parallel preview requests → exactly 3 free starts, rest 402", len(started) == 3 and sum(x.status_code == 402 for x in res) == 7, [x.status_code for x in res])

    # favorites, persistence across sessions, deletion, retention
    call(A, "POST", f"/versions/{v2}/favorite", json={"favorite": True})
    A2 = signin(f"a-{run}@example.com"); lib2 = call(A2, "GET", "/library").json()
    fav = [x for pr_ in lib2["projects"] for x in pr_["versions"] if x["id"] == v2]
    check("new session sees the same library, favorite kept", fav and fav[0]["favorite"] is True and len(lib2["projects"]) >= 3)
    old_url = call(A, "GET", f"/versions/{v2}").json()["video_url"]
    d = call(A, "POST", f"/versions/{v2}/delete").json()
    check("delete removes the version and its files", d["ok"] and d["deleted_files"] >= 3 and requests.get(old_url).status_code == 404 and call(A, "GET", f"/versions/{v2}").status_code == 404, d)
    subprocess.run(["psql", *PG.args, "-c", f"update versions set expires_at = now() - interval '1 minute' where id = '{h}'"], capture_output=True)
    keys = PG.rpc("eva_expire")["keys"]
    check("retention: expired HD returned for deletion and hidden", f"versions/{h}/video.mp4" in keys and call(A, "GET", f"/versions/{h}").status_code == 404, len(keys))
    E["ok"] = True; OUT.write_text(json.dumps(E, indent=1, default=str)); print("accounts e2e: ok", json.dumps(E["timings"]))


if __name__ == "__main__":
    main()
