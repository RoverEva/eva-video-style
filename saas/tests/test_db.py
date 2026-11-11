#!/usr/bin/env python3
"""Credits / free-preview / library SQL against a real Postgres (the same functions Supabase runs).

    EVA_PG_HOST=/var/tmp/evapg EVA_PG_PORT=54329 python3 saas/tests/test_db.py

Covers: 3 lifetime free previews (no daily reset), failure/cancel/QA-failure release, credits fallback, insufficient
credits, concurrency (20 parallel requests for 3 free slots and for one credit balance), HD export once per version
(repeat = free), top-up idempotency, ownership checks, deletion, retention, My Account history (002), privileges (anon cannot touch anything)."""
import json, os, subprocess, sys, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
import db as D

PG = D.LocalPG()
PSQL = ["psql", *PG.args, "-At", "-v", "ON_ERROR_STOP=1"]


def sql(q, role=None):
    pre = f"set role {role}; " if role else ""
    return subprocess.run(PSQL + ["-c", pre + q], capture_output=True, text=True)


def acct(uid): return PG.rpc("eva_account", user_id=uid)


def new_user():
    uid = str(uuid.uuid4()); acct(uid); return uid


def project(uid, pid=None):
    pid = pid or "p" + uuid.uuid4().hex[:11]
    PG.rpc("eva_create_project", id=pid, user_id=uid, title="Test", upload_key=f"uploads/{pid}/input.mp4", upload_bytes=1000, source_days=30); return pid


def preview(uid, pid, cost=13):
    vid = "v" + uuid.uuid4().hex[:11]
    return vid, PG.rpc("eva_start_preview", user_id=uid, project_id=pid, version_id=vid, cost=cost, options={"aspect": "9:16", "templates": ["T17"]})


def finish(vid, status, days=30): return PG.rpc("eva_finish", version_id=vid, status=status, retain_days=days, video_key=f"outputs/{vid}.mp4")


def main():
    for m in sorted((Path(__file__).resolve().parents[1] / "db").glob("[0-9]*.sql")):   # 001, 002, … in order, like the deploy
        subprocess.run(PSQL + ["-q", "-1", "-f", str(m)], check=True, capture_output=True)

    # ── lifetime free previews; failures never consume ──
    u = new_user(); p = project(u)
    assert acct(u)["free_left"] == 3 and acct(u)["credits"] == 0
    v1, r = preview(u, p); assert r["ok"] and r["charge"]["type"] == "free", r
    v_dup = PG.rpc("eva_start_preview", user_id=u, project_id=p, version_id=v1, cost=13, options={}); assert v_dup["duplicate"]
    assert preview(u, p)[1]["reason"] == "busy"                                    # one preview at a time per project
    finish(v1, "failed"); assert acct(u)["free_left"] == 3                          # failed → released
    for st in ("canceled", "qa_failed"):
        v, r = preview(u, p); finish(v, st); assert acct(u)["free_left"] == 3, st     # cancel / critical QA → released
    for i in range(3):
        v, r = preview(u, p); assert r["charge"]["type"] == "free"; finish(v, "done")
    a = acct(u); assert a["free_left"] == 0 and a["free_used"] == 3, a
    assert finish(v, "failed").get("duplicate")                                     # late failure after success: no refund
    assert acct(u)["free_used"] == 3
    v, r = preview(u, p); assert not r["ok"] and r["reason"] == "insufficient_credits" and r["need"] == 13, r   # no daily reset, no credits
    print("free previews: 3 lifetime, failures/cancel/QA-failure released, 4th refused without credits")

    # ── top-ups are idempotent per Stripe session ──
    SID = "cs_test_" + uuid.uuid4().hex
    t1 = PG.rpc("eva_topup", user_id=u, session_id=SID, credits=100, amount_cents=999)
    t2 = PG.rpc("eva_topup", user_id=u, session_id=SID, credits=100, amount_cents=999)
    assert t1["credits"] == 100 and t2["duplicate"] and t2["credits"] == 100
    v, r = preview(u, p, 14); assert r["charge"] == {"type": "credits", "amount": 14} and acct(u)["credits"] == 86
    finish(v, "failed"); assert acct(u)["credits"] == 100                            # credits back on failure
    v, r = preview(u, p, 14); finish(v, "done"); assert acct(u)["credits"] == 86
    print("top-up idempotent; credit preview reserved, released on failure, captured on success")

    # ── HD export from a saved version: charged once, repeat = existing (free download) ──
    src = v
    h1 = "h" + uuid.uuid4().hex[:11]; r = PG.rpc("eva_start_hd", user_id=u, version_id=h1, source_version=src, cost=45); assert r["ok"] and acct(u)["credits"] == 41
    r2 = PG.rpc("eva_start_hd", user_id=u, version_id="h" + uuid.uuid4().hex[:11], source_version=src, cost=45)
    assert r2.get("existing") == h1 and acct(u)["credits"] == 41, r2               # double click / second tab: no second charge
    finish(h1, "failed", 90); assert acct(u)["credits"] == 86                        # failed HD → credits back
    h2 = "h" + uuid.uuid4().hex[:11]; PG.rpc("eva_start_hd", user_id=u, version_id=h2, source_version=src, cost=45); finish(h2, "done", 90)
    r3 = PG.rpc("eva_start_hd", user_id=u, version_id="h" + uuid.uuid4().hex[:11], source_version=src, cost=45)
    assert r3.get("existing") == h2 and r3["status"] == "done" and acct(u)["credits"] == 41   # re-download is free
    poor = new_user(); pp = project(poor); pv, _ = preview(poor, pp); finish(pv, "done")
    assert PG.rpc("eva_start_hd", user_id=poor, version_id="hx" + uuid.uuid4().hex[:10], source_version=pv, cost=45)["reason"] == "insufficient_credits"
    assert PG.rpc("eva_start_hd", user_id=poor, version_id="hy" + uuid.uuid4().hex[:10], source_version=src, cost=45)["reason"] == "no_source"   # not theirs
    print("HD export: charged once per saved version, released on failure, repeat download free, other users' versions refused")

    # ── concurrency: 20 parallel requests for 3 free slots / one credit balance ──
    c = new_user(); projs = [project(c) for _ in range(20)]
    with ThreadPoolExecutor(20) as ex: res = list(ex.map(lambda pid: preview(c, pid)[1], projs))
    free = sum(1 for r in res if r.get("ok") and r["charge"]["type"] == "free"); refused = sum(1 for r in res if not r.get("ok"))
    a = acct(c); assert free == 3 and refused == 17 and a["free_held"] == 3 and a["free_left"] == 0, (free, refused, a)
    k = new_user(); PG.rpc("eva_topup", user_id=k, session_id="cs_k" + uuid.uuid4().hex, credits=100, amount_cents=999)
    for _ in range(3): kp = project(k); kv, _ = preview(k, kp); finish(kv, "done")  # use up free previews
    projs = [project(k) for _ in range(20)]
    with ThreadPoolExecutor(20) as ex: res = list(ex.map(lambda pid: preview(k, pid, 15)[1], projs))
    paid = sum(1 for r in res if r.get("ok")); a = acct(k)
    assert paid == 6 and a["credits"] == 10, (paid, a)                               # 6 × 15 = 90 of 100, never negative
    print("concurrency: 20 parallel requests → exactly 3 free slots; 20 parallel credit spends → 6 × 15, balance 10, never negative")

    # ── library, ownership, favorite, delete, retention ──
    lib = PG.rpc("eva_library", user_id=u); assert len(lib) == 1 and len(lib[0]["versions"]) >= 8 and all("user_id" not in v for v in lib[0]["versions"])
    assert PG.rpc("eva_library", user_id=poor)[0]["id"] == pp                       # each user sees only their own
    assert PG.rpc("eva_version", version_id=src, user_id=poor) is None             # cross-user version lookup → nothing
    assert PG.rpc("eva_update_version", version_id=src, user_id=u, favorite=True)["favorite"] is True
    assert PG.rpc("eva_update_version", version_id=src, user_id=poor, favorite=False) is None
    d = PG.rpc("eva_delete", user_id=u, version_id=h2); assert f"outputs/{h2}.mp4" in d["keys"]
    assert all(v["id"] != h2 for v in PG.rpc("eva_library", user_id=u)[0]["versions"])
    sql(f"update versions set expires_at = now() - interval '1 day' where id = '{src}'"); sql(f"update projects set source_expires_at = now() - interval '1 day' where id = '{p}'")
    e = PG.rpc("eva_expire"); assert f"outputs/{src}.mp4" in e["keys"] and f"uploads/{p}/input.mp4" in e["keys"]
    assert PG.rpc("eva_version", version_id=src, user_id=u) is None
    dp = PG.rpc("eva_delete", user_id=poor, project_id=pp); assert f"uploads/{pp}/input.mp4" in dp["keys"] and PG.rpc("eva_library", user_id=poor) == []
    print("library: owner-only, favorites, delete (R2 keys returned), retention expiry of versions and source uploads")

    # ── My Account history (002 eva_history): grants, purchases, charges, refunds, free previews; own rows only ──
    hu = new_user(); hp = project(hu)
    PG.rpc("eva_topup", user_id=hu, session_id="e2e-grant-" + uuid.uuid4().hex[:8], credits=100, amount_cents=0)        # labelled grant
    PG.rpc("eva_topup", user_id=hu, session_id="cs_test_" + uuid.uuid4().hex, credits=100, amount_cents=999)             # paid top-up
    fv, _ = preview(hu, hp); finish(fv, "done")                                                                           # free preview
    for _ in range(2): x, _ = preview(hu, hp); finish(x, "done")
    cv, r = preview(hu, hp, 14); assert r["charge"]["amount"] == 14; finish(cv, "done")                                   # paid preview
    rv, _ = preview(hu, hp, 14); finish(rv, "failed")                                                                     # refunded preview
    hh = "h" + uuid.uuid4().hex[:11]; PG.rpc("eva_start_hd", user_id=hu, version_id=hh, source_version=cv, cost=47); finish(hh, "done", 90)
    other = new_user(); PG.rpc("eva_topup", user_id=other, session_id="cs_test_" + uuid.uuid4().hex, credits=100, amount_cents=999)
    rows = PG.history(hu, 200); kinds = [r["kind"] for r in rows]
    assert rows and [r["created_at"] for r in rows] == sorted((r["created_at"] for r in rows), reverse=True), "newest first"
    assert kinds.count("topup") == 2 and "release" in kinds and "capture" in kinds, kinds
    assert all(set(r) == {"id", "kind", "ref", "credits", "free", "meta", "created_at"} for r in rows)
    assert {r["ref"] for r in rows}.isdisjoint({r["ref"] for r in PG.history(other, 200)})                                   # own rows only
    assert len(PG.history(hu, 3)) == 3 and PG.history(str(uuid.uuid4())) == []
    import api_v2
    acc = api_v2.Accounts.__new__(api_v2.Accounts); acc.db = PG; acc.account = lambda u: acct(u["id"])
    items = acc.history({"id": hu})["items"]; by = {(i["type"], i["status"], i.get("free", False)) for i in items}
    want = {("purchase", "granted", False), ("purchase", "paid", False), ("preview", "charged", True), ("preview", "charged", False),
            ("preview", "refunded", False), ("hd", "charged", False)}
    assert want <= by, by
    assert next(i for i in items if i["status"] == "paid")["amount_cents"] == 999 and next(i for i in items if i["type"] == "hd")["credits"] == -47
    assert all(i.get("version") != "x" for i in acc.history({"id": other})["items"]) and len(acc.history({"id": other})["items"]) == 1
    print("history: grant, paid top-up, free/paid previews, refund, HD export listed newest first; each user sees only their own")

    # ── privileges: browser roles can't read tables or call functions ──
    for role in ("anon", "authenticated"):
        assert sql("select count(*) from public.accounts", role).returncode != 0
        assert sql(f"select public.eva_topup('{{\"user_id\":\"{u}\",\"session_id\":\"x\",\"credits\":999}}'::jsonb)", role).returncode != 0
    assert sql(f"select public.eva_account('{{\"user_id\":\"{u}\"}}'::jsonb)", "service_role").returncode == 0
    for role in ("anon", "authenticated"):
        assert sql(f"select public.eva_history('{{\"user_id\":\"{u}\"}}'::jsonb)", role).returncode != 0
    assert sql(f"select public.eva_history('{{\"user_id\":\"{u}\"}}'::jsonb)", "service_role").returncode == 0
    assert sql("select count(*) from public.ledger", "service_role").returncode != 0   # like production: no table access, functions only
    print("privileges: anon/authenticated denied on tables and functions; service_role allowed")
    print("db tests: ok")


if __name__ == "__main__":
    main()
