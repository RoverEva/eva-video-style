#!/usr/bin/env python3
"""Read-only Vercel helper for the frontend-only release: print the CURRENT production deployment of a project (the
rollback target) as id / url / created, and write prev_id / prev_url to $GITHUB_OUTPUT.
    vercel_prod.py PROJECT          env: VERCEL_TOKEN, optional VERCEL_SCOPE (team id or slug). Never prints the token."""
import os, sys, time
import requests
API, T, SCOPE = "https://api.vercel.com", os.environ.get("VERCEL_TOKEN", "").strip(), os.environ.get("VERCEL_SCOPE", "").strip()
H = {"Authorization": f"Bearer {T}"}
q = ({"teamId": SCOPE} if SCOPE.startswith("team_") else {"slug": SCOPE}) if SCOPE else {}
def get(path, **p):
    r = requests.get(API + path, headers=H, params={**q, **p}, timeout=60)
    if not r.ok: raise SystemExit(f"Vercel GET {path}: HTTP {r.status_code} {(r.json().get('error') or {}).get('message', '') if r.content else ''}")
    return r.json()
proj = get(f"/v9/projects/{sys.argv[1]}")
deps = get("/v6/deployments", projectId=proj["id"], target="production", state="READY", limit=1).get("deployments", [])
if not deps: raise SystemExit("no READY production deployment found")
d = deps[0]; when = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(d["created"] / 1000))
print(f"current production deployment (rollback target): {d['uid']} https://{d['url']} created {when}")
if os.environ.get("GITHUB_OUTPUT"):
    with open(os.environ["GITHUB_OUTPUT"], "a") as f: f.write(f"prev_id={d['uid']}\nprev_url=https://{d['url']}\n")
