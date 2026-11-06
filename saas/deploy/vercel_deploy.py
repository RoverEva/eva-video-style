#!/usr/bin/env python3
"""Deploy step: publish site/ to Vercel production through the REST API (no CLI), print the production domain.

    vercel_deploy.py SITE_DIR PROJECT          env: VERCEL_TOKEN, optional VERCEL_SCOPE (team id or slug)

Checks the token first and prints Vercel's own error message (never the token). Creates the project if missing,
uploads files by SHA-1 (unchanged files are skipped by Vercel), creates a production deployment, waits until READY.
Writes `site=https://<domain>` to $GITHUB_OUTPUT when run in Actions.
"""
import hashlib, os, sys, time
from pathlib import Path
import requests

API = "https://api.vercel.com"
T = os.environ.get("VERCEL_TOKEN", "").strip()
H = {"Authorization": f"Bearer {T}"}
SCOPE = os.environ.get("VERCEL_SCOPE", "").strip()


def q():
    if not SCOPE: return {}
    return {"teamId": SCOPE} if SCOPE.startswith("team_") else {"slug": SCOPE}


def call(method, path, **kw):
    r = requests.request(method, API + path, headers={**H, **kw.pop("headers", {})}, params={**q(), **kw.pop("params", {})}, timeout=120, **kw)
    if r.status_code >= 400:
        try: e = r.json().get("error", {})
        except Exception: e = {"message": r.text[:300]}
        raise SystemExit(f"Vercel {method} {path}: HTTP {r.status_code} {e.get('code', '')}: {e.get('message', '')}")
    return r.json() if r.content else {}


def main():
    site, name = Path(sys.argv[1]), sys.argv[2]
    if not T: raise SystemExit("VERCEL_TOKEN is empty")
    # 1. token check: personal tokens can read /v2/user; team tokens may only see their team
    r = requests.get(API + "/v2/user", headers=H, timeout=30)
    if r.ok: print("token ok: user", r.json().get("user", {}).get("username"))
    else:
        msg = (r.json().get("error", {}) if r.headers.get("content-type", "").startswith("application/json") else {}).get("message", r.text[:200])
        print(f"/v2/user: HTTP {r.status_code} {msg}")
        t = requests.get(API + "/v2/teams", headers=H, timeout=30)
        teams = [x.get("slug") for x in (t.json().get("teams", []) if t.ok else [])]
        print(f"/v2/teams: HTTP {t.status_code} {teams}")
        if not (t.ok and (SCOPE or len(teams) == 1)):
            raise SystemExit("Vercel did not accept VERCEL_TOKEN for a personal account. Create a new token (Account Settings → Tokens) "
                             "with scope = your account, or add secret VERCEL_SCOPE = your team slug.")
        if not SCOPE:
            globals()["SCOPE"] = teams[0]; print("using team", SCOPE)
    # 2. project
    try: proj = call("GET", f"/v9/projects/{name}")
    except SystemExit as e:
        if "404" not in str(e): raise
        proj = call("POST", "/v10/projects", json={"name": name, "framework": None}); print("created project", name)
    # 3. files
    files = []
    for p in sorted(x for x in site.rglob("*") if x.is_file() and ".vercel" not in x.parts):
        data = p.read_bytes(); sha = hashlib.sha1(data).hexdigest()
        call("POST", "/v2/files", data=data, headers={"x-vercel-digest": sha, "Content-Type": "application/octet-stream"})
        files.append({"file": str(p.relative_to(site)), "sha": sha, "size": len(data)})
    print("uploaded", len(files), "files")
    # 4. production deployment
    d = call("POST", "/v13/deployments", params={"skipAutoDetectionConfirmation": "1"},
             json={"name": name, "project": proj["id"], "target": "production", "files": files,
                   "projectSettings": {"framework": None, "buildCommand": None, "outputDirectory": None, "installCommand": None}})
    t0 = time.time()
    while d.get("readyState") not in ("READY", "ERROR", "CANCELED") and time.time() - t0 < 600:
        time.sleep(4); d = call("GET", f"/v13/deployments/{d['id']}")
    if d.get("readyState") != "READY": raise SystemExit(f"deployment {d.get('id')} ended {d.get('readyState')}")
    doms = [x["name"] for x in call("GET", f"/v9/projects/{proj['id']}/domains").get("domains", [])]
    dom = next((x for x in doms if x.endswith(".vercel.app")), doms[0] if doms else d.get("alias", [d["url"]])[0])
    print("deployment", d["url"], "READY; production domain:", dom)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f: f.write(f"site=https://{dom}\n")


if __name__ == "__main__":
    main()
