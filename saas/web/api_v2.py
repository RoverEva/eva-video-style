"""EVA Video Studio · account API (/api/v2): sign-in, lifetime free previews, credits, My Videos, HD export, top-ups.

Every route needs `Authorization: Bearer <Supabase access token>`; the user id comes from Supabase Auth, never from the
browser. Money and limits are enforced inside Postgres (saas/db/*.sql, account row locked), so concurrent requests,
double clicks, second tabs and replayed webhooks cannot overspend or double-charge.

Pricing (shown before anything is charged; integer credits, $9.99 = 100 credits):
    preview  12-15 credits by duration (first 3 previews per account are free, for life)
    HD       38-52 credits by duration, rendered from the original upload + the saved version's exact configuration
Retention (env): previews EVA_PREVIEW_DAYS=30, HD EVA_HD_DAYS=90, source upload = preview retention.
"""
from pathlib import Path
import json, os, re, secrets, time
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

try: from . import progress, stripe_lite
except ImportError: import progress, stripe_lite

MAX_BYTES, MAX_SECONDS = 200 * 1024 * 1024, 30
TOPUP = {"cents": 999, "credits": 100}
PREVIEW_DAYS = int(os.environ.get("EVA_PREVIEW_DAYS", 30))
HD_DAYS = int(os.environ.get("EVA_HD_DAYS", 90))
URL_TTL = 900
ID_RE = re.compile(r"^[a-z0-9]{12}$")
# launch templates (approved 2026-11-08). T19 Footage Intro is listed but not selectable until its cut-out + B-roll path ships.
TEMPLATES = {"T23": "Creative Pop", "T21": "Clean & Minimal", "T17": "Sci-Fi Network", "T02": "Electric Blue", "T01": "Bold Lime"}
NAMES = dict(TEMPLATES, T19="Footage Intro", T20="Soft Pop", T09="Gallery Wall")   # labels, incl. templates of older saved versions
TRACKS = {"bright-pop": "Bright Pop", "calm-lofi": "Calm Lo-fi", "inspire": "Inspire", "luxury-ambient": "Luxury Ambient"}


GALLERY = json.loads((Path(__file__).resolve().parent / "gallery.json").read_text())
GALLERY_PREFIX = os.environ.get("EVA_GALLERY_PREFIX", "staging/template-demos/gallery/")
GALLERY_TTL = 900


def gallery_payload(store_):
    """public Template Gallery: signed 15-min links to the approved, optimised assets of SELECTABLE templates only
    (T19 and anything pending review never leave the bucket). Signing is local: no R2 call per request."""
    out = []
    for t in GALLERY["templates"]:
        if t["id"] not in TEMPLATES: continue
        assets = {}
        for ar, a in t["assets"].items():
            if a.get("status") != "approved": continue
            assets[ar] = {k: {"url": store_.presign_get(GALLERY_PREFIX + a[k]["key"], GALLERY_TTL), "bytes": a[k]["bytes"]}
                          for k in ("thumb", "clip5", "full15") if k in a}
        out.append({"id": t["id"], "name": TEMPLATES[t["id"]], "assets": assets})
    return {"templates": out, "expires_in": GALLERY_TTL}


def _d(sec): return max(1.0, min(float(sec or MAX_SECONDS), MAX_SECONDS))
def preview_cost(sec): return 12 + round(3 * _d(sec) / MAX_SECONDS)     # 12..15
def hd_cost(sec): return 38 + round(14 * _d(sec) / MAX_SECONDS)         # 38..52
def new_id(prefix): return prefix + secrets.token_hex(6)[:11]   # 12 characters, [a-z0-9]


def err(msg, code=400, **kw): return JSONResponse(dict(error=msg, **kw), status_code=code)


class Unavailable(Exception): pass   # a read-only view the database could not serve → HTTP 503


class Accounts:
    def __init__(self, db, store, kv, spawn, stripe_mod=stripe_lite, cancel=None):
        self.db, self.s, self.kv, self.spawn, self.stripe, self.cancel_call = db, store, kv, spawn, stripe_mod, cancel

    # ── helpers ──
    def account(self, u): return self.db.rpc("eva_account", user_id=u["id"], email=u.get("email"))

    def options(self, b):
        aspect = b.get("aspect"); mode = b.get("template_mode", "single"); music = b.get("music", "none")
        tpls = [t for t in b.get("templates") or [] if t in TEMPLATES]; tracks = [t for t in b.get("music_tracks") or [] if t in TRACKS]
        if aspect not in ("9:16", "16:9"): raise ValueError("Choose 9:16 or 16:9.")
        if mode not in ("single", "multi", "auto"): raise ValueError("bad template mode")
        if mode != "auto" and not tpls: raise ValueError("Choose at least one visual template.")
        if music not in ("none", "track", "mix"): raise ValueError("bad music option")
        if music == "track" and not 1 <= len(tracks) <= 3: raise ValueError("Choose one to three music tracks.")
        return {"aspect": aspect, "templates": (tpls[:1] if mode == "single" else tpls) or ["T17"], "template_mode": mode, "music": music,
                "music_tracks": tracks[:3], "preview_seconds": 10}

    def urls(self, v):
        out = {}
        if v.get("thumb_key"): out["thumb_url"] = self.s.presign_get(v["thumb_key"], URL_TTL)
        if v.get("video_key") and v.get("status") == "done":
            out["video_url"] = self.s.presign_get(v["video_key"], URL_TTL)
            if v.get("kind") == "hd": out["download_url"] = self.s.presign_get(v["video_key"], URL_TTL, f"EVA_{v['project_id']}_v{v['n']}_HD.mp4")
        return out

    def present(self, v, duration=None):
        if not v: return None
        x = {k: v.get(k) for k in ("id", "project_id", "kind", "n", "source_version", "options", "status", "charge", "favorite", "error",
                                   "created_at", "finished_at", "expires_at", "qa", "report")}
        x["templates"] = [NAMES.get(t, t) for t in (v.get("options") or {}).get("templates", [])]
        x.update(self.urls(v))
        if v.get("status") in ("queued", "running"):
            w = {"state": "running", "updated_ts": time.time() if v.get("status") == "queued" else 0}
            x["progress"] = progress.summary(self.kv, v["id"], v["kind"] if v["kind"] == "preview" else "final", w)
        elif v.get("status") == "done": x["progress"] = {"progress": 100}
        if duration is not None: x["hd_cost"], x["preview_cost"] = hd_cost(duration), preview_cost(duration)
        return x

    # ── flow ──
    def me(self, u):
        a = self.account(u); a.pop("user_id", None)
        return dict(a, topup=TOPUP, retention={"preview_days": PREVIEW_DAYS, "hd_days": HD_DAYS})

    def history(self, u):
        """credit purchases and charges for the My Account page — read-only view of the existing ledger"""
        self.account(u)
        try: rows = self.db.history(u["id"], 200)
        except Exception as e:   # read-only page: report it as unavailable instead of a bare 500
            print("history unavailable:", type(e).__name__, str(e)[:200], flush=True); raise Unavailable("History is unavailable right now.")
        out, by = [], {}
        for r in rows: by.setdefault((r["kind"], r["ref"]), r)
        for r in rows:
            m = r.get("meta") or {}
            if r["kind"] == "topup":
                cents = m.get("amount_cents") or 0
                out.append({"ts": r["created_at"], "type": "purchase", "label": "Credit purchase" if cents else "Credit grant",
                            "credits": r["credits"], "amount_cents": cents, "status": "paid" if cents else "granted"})
            elif r["kind"] == "reserve":
                free = m.get("type") == "free"; what = "HD export" if m.get("for") == "hd" else "Preview"
                st = "refunded" if ("release", r["ref"]) in by else "charged" if ("capture", r["ref"]) in by else "in progress"
                out.append({"ts": r["created_at"], "type": "hd" if m.get("for") == "hd" else "preview", "label": what + (" (free)" if free else ""),
                            "credits": r["credits"], "free": free, "status": st, "version": r["ref"]})
            elif r["kind"] == "adjust":
                out.append({"ts": r["created_at"], "type": "adjust", "label": "Adjustment", "credits": r["credits"], "status": "applied"})
        return {"items": out[:100]}

    def create_project(self, u, b):
        size, ctype, dur = b.get("size"), b.get("type"), b.get("duration")
        if not isinstance(size, int) or size <= 0: raise ValueError("missing file size")
        if size > MAX_BYTES: raise ValueError("The video is larger than 200 MB.")
        if ctype not in ("video/mp4", "video/quicktime"): raise ValueError("Please upload an MP4 (or MOV) video.")
        if dur is not None and float(dur) > MAX_SECONDS + .5: raise ValueError(f"This video is {round(float(dur))} seconds long. The limit is 30 seconds.")
        k = f"up:{time.strftime('%Y-%m-%d', time.gmtime())}:{u['id']}"
        n = (self.kv.get(k) or 0) + 1
        if n > 30: raise PermissionError("Upload limit reached for today.")
        self.kv[k] = n
        self.account(u); pid = new_id("p"); key = f"projects/{pid}/source.mp4"
        self.db.rpc("eva_create_project", id=pid, user_id=u["id"], title=(b.get("name") or "Untitled video")[:120], upload_key=key,
                    upload_bytes=size, duration_s=float(dur) if dur else None, source_days=PREVIEW_DAYS)
        return {"project": pid, "put_url": self.s.presign_put(key, size, ctype, URL_TTL), "put_type": ctype,
                "costs": {"preview": preview_cost(dur), "hd": hd_cost(dur)}}

    def project_of(self, u, pid):
        lib = self.db.rpc("eva_library", user_id=u["id"], project_id=pid)
        return lib[0] if lib else None

    def duration(self, pr): return float(pr.get("duration_s") or MAX_SECONDS)

    def start_preview(self, u, pid, b):
        pr = self.project_of(u, pid)
        if not pr: raise LookupError("not found")
        if not pr.get("upload_key") or not self.s.size(pr["upload_key"]): raise ValueError("The upload has not finished yet (or has expired).")
        opts = self.options(b) if b.get("aspect") else (pr["versions"][0]["options"] if pr["versions"] else None)
        if not opts: raise ValueError("Choose your settings first.")
        vid = new_id("v"); cost = preview_cost(self.duration(pr))
        r = self.db.rpc("eva_start_preview", user_id=u["id"], project_id=pid, version_id=vid, cost=cost, options=opts)
        if not r.get("ok"): return r
        self.spawn("preview", vid)
        return dict(r, version=vid)

    def start_hd(self, u, src_vid):
        src = self.db.rpc("eva_version", version_id=src_vid, user_id=u["id"])
        if not src or src["kind"] != "preview": raise LookupError("not found")
        pr = self.project_of(u, src["project_id"]); vid = new_id("h")
        r = self.db.rpc("eva_start_hd", user_id=u["id"], version_id=vid, source_version=src_vid, cost=hd_cost(self.duration(pr)))
        if r.get("ok") and not r.get("existing") and not r.get("duplicate"): self.spawn("hd", vid); r["version"] = vid
        elif r.get("existing"): r["version"] = r["existing"]
        return r

    def cancel(self, u, vid):
        v = self.db.rpc("eva_version", version_id=vid, user_id=u["id"])
        if not v: raise LookupError("not found")
        if v["status"] not in ("queued", "running"): return {"ok": False, "reason": "not_running", "status": v["status"]}
        r = self.db.rpc("eva_finish", version_id=vid, status="canceled", retain_days=0, error="canceled by user")
        if self.cancel_call:
            try: self.cancel_call(vid)
            except Exception: pass
        return dict(r, status="canceled")

    def topup(self, u, site, return_to):
        rt = return_to if isinstance(return_to, str) and re.match(r"^/[A-Za-z0-9_./?=&%-]*$", return_to or "") and "//" not in return_to else "/videos.html"
        sep = "&" if "?" in rt else "?"
        s = self.stripe.call("POST", "/checkout/sessions", {
            "mode": "payment", "client_reference_id": u["id"], "customer_email": u.get("email"),
            "metadata": {"type": "topup", "user_id": u["id"], "credits": str(TOPUP["credits"])},
            "payment_intent_data": {"metadata": {"type": "topup", "user_id": u["id"]}, "description": f"EVA Video Studio · {TOPUP['credits']} credits"},
            "line_items": [{"quantity": 1, "price_data": {"currency": "usd", "unit_amount": TOPUP["cents"],
                            "product_data": {"name": f"{TOPUP['credits']} EVA credits", "description": "Use for previews (12-15) and HD exports (38-52)"}}}],
            "success_url": f"{site}{rt}{sep}topup=done", "cancel_url": f"{site}{rt}{sep}topup=canceled",
            "expires_at": int(time.time()) + 3600}, idem=f"topup-{u['id']}-{int(time.time() // 30)}")   # one session per 30 s window
        return {"url": s["url"]}

    def on_topup(self, sess):
        md = sess.get("metadata") or {}
        if sess.get("payment_status") != "paid": return "not paid yet"
        r = self.db.rpc("eva_topup", user_id=md.get("user_id"), session_id=sess["id"], credits=int(md.get("credits", TOPUP["credits"])),
                        amount_cents=sess.get("amount_total"), livemode=sess.get("livemode"))
        return "duplicate top-up ignored" if r.get("duplicate") else f"credited, balance {r.get('credits')}" if r.get("ok") else r.get("reason")

    def library(self, u):
        lib = self.db.rpc("eva_library", user_id=u["id"])
        for pr in lib:
            d = self.duration(pr)
            pr["versions"] = [self.present(v, d) for v in pr["versions"]]
            pr["costs"] = {"preview": preview_cost(d), "hd": hd_cost(d)}
            pr.pop("upload_key", None)
        return lib

    def version(self, u, vid):
        v = self.db.rpc("eva_version", version_id=vid, user_id=u["id"])
        if not v: return None
        pr = self.project_of(u, v["project_id"]); x = self.present(v, self.duration(pr) if pr else None)
        x["project_title"] = v.get("project_title")
        if v["kind"] == "preview" and pr:
            hd = [h for h in pr["versions"] if h["kind"] == "hd" and h.get("source_version") == vid and h["status"] not in ("failed", "qa_failed", "canceled")]
            if hd: x["hd"] = self.present(hd[0])
        return x

    def delete(self, u, vid=None, pid=None):
        r = self.db.rpc("eva_delete", user_id=u["id"], **({"version_id": vid} if vid else {"project_id": pid}))
        for k in r.get("keys") or []:
            try: self.s.delete(k)
            except Exception: pass
        return {"ok": r.get("ok"), "reason": r.get("reason"), "deleted_files": len(r.get("keys") or [])}


def routes(acc: Accounts, site_of):
    def user(req: Request):
        h = req.headers.get("authorization", "")
        return acc.db.user(h[7:].strip()) if h.lower().startswith("bearer ") else None

    async def body(req):
        try: return await req.json()
        except Exception: return {}

    def guarded(fn):
        async def h(req):
            u = user(req)
            if not u: return err("Please sign in.", 401)
            try: return await fn(req, u)
            except ValueError as e: return err(str(e))
            except LookupError as e: return err("not found" if str(e) == "'not found'" or str(e) == "not found" else str(e), 404)
            except PermissionError as e: return err(str(e), 429)
            except stripe_lite.StripeError as e: return err(f"payment unavailable: {e}", 503)
            except Unavailable as e: return err(str(e), 503)
        return h

    async def me(req, u): return JSONResponse(acc.me(u))
    async def history(req, u): return JSONResponse(acc.history(u))
    async def quote(req, u):
        d = req.query_params.get("duration"); return JSONResponse({"preview": preview_cost(d), "hd": hd_cost(d)})
    async def projects(req, u): return JSONResponse(acc.create_project(u, await body(req)))
    async def previews(req, u):
        r = acc.start_preview(u, req.path_params["pid"], await body(req))
        if r.get("ok"): return JSONResponse(r)
        msgs = {"insufficient_credits": f"This preview costs {r.get('need')} credits and you have {r.get('have')}. Top up to continue.",
                "busy": "A preview for this video is already being made.", "no_project": "not found"}
        return err(msgs.get(r.get("reason"), r.get("reason")), 402 if r.get("reason") == "insufficient_credits" else 409, **r)
    async def hd(req, u):
        r = acc.start_hd(u, req.path_params["vid"])
        if r.get("ok"): return JSONResponse(r)
        msgs = {"insufficient_credits": f"HD export costs {r.get('need')} credits and you have {r.get('have')}. Top up to continue.",
                "source_expired": "The original upload for this video has expired, so HD can no longer be rendered.", "no_source": "This version can't be exported yet."}
        return err(msgs.get(r.get("reason"), r.get("reason")), 402 if r.get("reason") == "insufficient_credits" else 409, **r)
    async def library(req, u): return JSONResponse({"projects": acc.library(u), "account": acc.me(u)})
    async def version(req, u):
        v = acc.version(u, req.path_params["vid"]); return JSONResponse(v) if v else err("not found", 404)
    async def favorite(req, u):
        b = await body(req); r = acc.db.rpc("eva_update_version", version_id=req.path_params["vid"], user_id=u["id"], favorite=bool(b.get("favorite")))
        return JSONResponse(r) if r else err("not found", 404)
    async def cancel(req, u): return JSONResponse(acc.cancel(u, req.path_params["vid"]))
    async def del_version(req, u):
        r = acc.delete(u, vid=req.path_params["vid"]); return JSONResponse(r) if r["ok"] else err("This video is still rendering.", 409)
    async def del_project(req, u):
        r = acc.delete(u, pid=req.path_params["pid"]); return JSONResponse(r) if r["ok"] else err("A version is still rendering.", 409)
    async def topup(req, u): return JSONResponse(acc.topup(u, site_of(req), (await body(req)).get("return_to")))

    async def gallery(req): return JSONResponse(gallery_payload(acc.s), headers={"Cache-Control": "private, max-age=600"})

    P = "/api/v2"
    return [Route(P + "/me", guarded(me)), Route(P + "/history", guarded(history)), Route(P + "/quote", guarded(quote)), Route(P + "/library", guarded(library)),
            Route(P + "/projects", guarded(projects), methods=["POST"]), Route(P + "/projects/{pid}/previews", guarded(previews), methods=["POST"]),
            Route(P + "/projects/{pid}/delete", guarded(del_project), methods=["POST"]),
            Route(P + "/versions/{vid}", guarded(version)), Route(P + "/versions/{vid}/hd", guarded(hd), methods=["POST"]),
            Route(P + "/versions/{vid}/favorite", guarded(favorite), methods=["POST"]), Route(P + "/versions/{vid}/cancel", guarded(cancel), methods=["POST"]),
            Route(P + "/versions/{vid}/delete", guarded(del_version), methods=["POST"]), Route(P + "/topup", guarded(topup), methods=["POST"]),
            Route(P + "/gallery", gallery)]   # public, read-only
