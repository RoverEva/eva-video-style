"""EVA Video Studio · web API (Starlette, served by Modal as an ASGI app; the website on Vercel calls it).

Customer flow (no human in the loop):
  POST /api/uploads                 → job id + private token + presigned PUT URL (browser uploads straight to R2)
  POST /api/jobs/{id}/preview       → validates options, rate limits, starts the ≤ 10 s watermarked preview render
  GET  /api/jobs/{id}?t=TOKEN       → state, preview URL, HD download URL once paid and rendered
  POST /api/jobs/{id}/checkout      → Stripe Checkout ($9.99, price fixed on the server)
  POST /api/stripe/webhook          → signature-verified; paid → full HD render starts; duplicate payment → refunded
Reconciler (cron, also called by workers): failed or stuck paid renders are retried, then refunded automatically.

State lives in R2: orders/<id>.json (written here), jobs/<id>/<kind>.json (written by the render worker).
"""
import hashlib, hmac, json, os, re, secrets, time
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

try: from . import stripe_lite as stripe
except ImportError: import stripe_lite as stripe

PRICE_CENTS = 999
MAX_BYTES, MAX_SECONDS, PREVIEW_SECONDS = 200 * 1024 * 1024, 30, 10
TEMPLATES = {"T17": "Sci-Fi Network", "T20": "Soft Pop", "T01": "Bold Lime", "T09": "Wall / HUD"}
TRACKS = {"bright-pop": "Bright Pop", "calm-lofi": "Calm Lo-fi", "inspire": "Inspire", "luxury-ambient": "Luxury Ambient"}
LIMITS = {"preview_per_ip_day": int(os.environ.get("EVA_PREVIEWS_PER_IP", 3)), "preview_global_day": int(os.environ.get("EVA_PREVIEWS_PER_DAY", 150)),
          "uploads_per_ip_day": 12, "max_final_attempts": 2, "stuck_minutes": 40}
ORIGIN_OK = re.compile(os.environ.get("EVA_SITE_ORIGINS", r"^https://eva-video-studio[a-z0-9-]*\.vercel\.app$|^http://(localhost|127\.0\.0\.1)(:\d+)?$"))
JOB_RE = re.compile(r"^[a-z0-9]{12}$")


def today(): return time.strftime("%Y-%m-%d", time.gmtime())
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def err(msg, code=400): return JSONResponse({"error": msg}, status_code=code)


def client_ip(req: Request):
    xf = req.headers.get("x-forwarded-for", "")
    return (xf.split(",")[0].strip() if xf else (req.client.host if req.client else "?"))


class Service:
    """Business rules, independent of HTTP and of Modal (tests inject a local store, a dict and fake spawn/stripe)."""
    def __init__(self, store, counters, spawn, stripe_mod=stripe, mailer=None):
        self.s, self.cnt, self.spawn, self.stripe, self.mail = store, counters, spawn, stripe_mod, mailer

    # ── records ──
    def order(self, job): return self.s.get_json(f"orders/{job}.json")
    def save(self, o): o["updated"] = time.time(); self.s.put_json(f"orders/{o['id']}.json", o); return o
    def worker(self, job, kind): return self.s.get_json(f"jobs/{job}/{kind}.json") or {}

    def auth(self, job, token):
        if not JOB_RE.match(job or ""): return None
        o = self.order(job)
        if not (o and token): return None
        ok = hmac.compare_digest(o["token_hash"], h(token)) or (o.get("mail_token") and hmac.compare_digest(o["mail_token"], token))
        return o if ok else None

    def bump(self, key, limit):
        """counter with a daily key; returns False when over the limit (Modal Dict in production)"""
        n = (self.cnt.get(key) or 0) + 1
        if n > limit: return False
        self.cnt[key] = n; return True

    # ── flow ──
    def create(self, ip, name, size, ctype):
        if not isinstance(size, int) or size <= 0: raise ValueError("missing file size")
        if size > MAX_BYTES: raise ValueError("The video is larger than 200 MB.")
        if ctype not in ("video/mp4", "video/quicktime"): raise ValueError("Please upload an MP4 (or MOV) video.")
        if not self.bump(f"up:{today()}:{h(ip)[:16]}", LIMITS["uploads_per_ip_day"]): raise PermissionError("Upload limit reached for today.")
        job, token = secrets.token_hex(6), secrets.token_urlsafe(24)
        o = self.save({"id": job, "token_hash": h(token), "created": time.time(), "ip": h(ip)[:16], "stripe_mode": self.stripe.mode(),
                       "upload": {"name": (name or "video.mp4")[:120], "size": size, "type": ctype}, "state": "uploading"})
        return {"job": job, "token": token, "put_url": self.s.presign_put(f"uploads/{job}/input.mp4", size, ctype), "put_type": ctype}

    def options(self, body):
        aspect = body.get("aspect"); tpls = [t for t in body.get("templates") or [] if t in TEMPLATES]
        mode = body.get("template_mode", "single"); music = body.get("music", "none"); tracks = [t for t in body.get("music_tracks") or [] if t in TRACKS]
        if aspect not in ("9:16", "16:9"): raise ValueError("Choose 9:16 or 16:9.")
        if mode not in ("single", "multi", "auto"): raise ValueError("bad template mode")
        if mode != "auto" and not tpls: raise ValueError("Choose at least one visual template.")
        if mode == "single": tpls = tpls[:1]
        if music not in ("none", "track", "mix"): raise ValueError("bad music option")
        if music == "track" and not 1 <= len(tracks) <= 3: raise ValueError("Choose one to three music tracks.")
        return {"aspect": aspect, "templates": tpls or ["T17"], "template_mode": mode, "music": music, "music_tracks": tracks[:3],
                "preview_seconds": PREVIEW_SECONDS}

    def preview(self, o, ip, body):
        if o.get("preview_started"): return o   # idempotent: one free preview per upload
        size = self.s.size(f"uploads/{o['id']}/input.mp4")
        if not size: raise ValueError("The upload has not finished yet.")
        if size > MAX_BYTES: raise ValueError("The video is larger than 200 MB.")
        opts = self.options(body)
        if self.stripe.mode() == "test" and o["upload"]["name"].startswith("e2e-fail-final"):
            opts["_fail_final"] = True   # live failure test: paid render fails → retry → automatic refund (never with live keys)
        if not self.bump(f"pv:{today()}", LIMITS["preview_global_day"]): raise PermissionError("We've hit today's free preview capacity. Please try again tomorrow.")
        if not self.bump(f"pv:{today()}:{h(ip)[:16]}", LIMITS["preview_per_ip_day"]): raise PermissionError("Free preview limit reached (3 per day).")
        o.update(options=opts, state="preview", preview_started=time.time()); self.save(o)
        self.spawn("preview", o["id"], dict(opts, paid=False), attempt=0)
        return o

    def checkout(self, o, site, token):
        pv = self.worker(o["id"], "preview")
        if pv.get("state") != "done": raise ValueError("The preview is not ready yet.")
        if o.get("paid"): raise ValueError("This video is already paid.")
        n = o.get("checkout_n", 0) + 1; base = f"{site}/video.html?id={o['id']}"
        # the private token rides in the URL fragment (never sent to a server) so the buyer lands back on their video page
        s = self.stripe.checkout(o["id"], f"{base}&paid=1#t={token}", f"{base}#t={token}", PRICE_CENTS, "EVA Video Studio · HD video", attempt=n)
        o.update(checkout_n=n, checkout={"session": s["id"], "at": time.time()}); self.save(o)
        return s["url"]

    def on_paid(self, session):
        job = (session.get("metadata") or {}).get("job") or session.get("client_reference_id")
        o = self.order(job) if job and JOB_RE.match(job) else None
        if not o: return "unknown job"
        if session.get("payment_status") != "paid": return "not paid yet"
        pi = session.get("payment_intent")
        if o.get("paid"):
            if o["paid"]["payment_intent"] == pi: return "duplicate event"
            # a second payment for the same video (two tabs): refund it automatically
            r = self.stripe.refund(pi, job, "duplicate"); o.setdefault("extra_refunds", []).append({"pi": pi, "refund": r.get("id"), "at": time.time()})
            self.save(o); return "duplicate payment refunded"
        cd = session.get("customer_details") or {}
        o.update(paid={"at": time.time(), "session": session["id"], "payment_intent": pi, "amount": session.get("amount_total"),
                       "email": cd.get("email") or session.get("customer_email"), "livemode": session.get("livemode")},
                 state="rendering", final_attempts=1, final_started=time.time(), mail_token=secrets.token_urlsafe(24))
        self.save(o)
        self.spawn("final", job, dict(o["options"], paid=True), attempt=1)
        return "render started"

    def on_final_result(self, job):
        """worker finished (done or failed after Modal's own retries): deliver, retry once more, or refund"""
        o = self.order(job); w = self.worker(job, "final")
        if not o or not o.get("paid") or o.get("state") in ("delivered", "refunded"): return o and o.get("state")
        if w.get("state") == "done":
            o.update(state="delivered", delivered_at=time.time()); self.save(o)
            if self.mail and o["paid"].get("email"):
                try: o["mailed"] = bool(self.mail(o["paid"]["email"], job, o["mail_token"])); self.save(o)
                except Exception as e: o["mail_error"] = str(e)[:200]; self.save(o)
            return "delivered"
        if w.get("state") == "rejected" or o.get("final_attempts", 1) >= LIMITS["max_final_attempts"]:
            return self.refund(o, w.get("error") or w.get("reason") or "render failed")
        o["final_attempts"] = o.get("final_attempts", 1) + 1; o["final_started"] = time.time(); self.save(o)
        self.spawn("final", job, dict(o["options"], paid=True), attempt=o["final_attempts"])
        return "retrying"

    def refund(self, o, reason):
        r = self.stripe.refund(o["paid"]["payment_intent"], o["id"])
        o.update(state="refunded", refunded={"at": time.time(), "refund": r.get("id"), "reason": str(reason)[:300]}); self.save(o)
        return "refunded"

    def reconcile(self):
        """cron: paid orders whose render failed or went silent → on_final_result / retry; old previews marked failed"""
        acts = {}
        for key, _ in self.s.list("orders/"):
            o = self.s.get_json(key)
            if not o: continue
            if o.get("paid") and o.get("state") == "rendering":
                w = self.worker(o["id"], "final")
                if w.get("state") in ("done", "failed", "rejected"): acts[o["id"]] = self.on_final_result(o["id"])
                elif time.time() - max(o.get("final_started", 0), w.get("updated_ts", 0)) > LIMITS["stuck_minutes"] * 60:
                    self.s.put_json(f"jobs/{o['id']}/final.json", dict(w, state="failed", error="stuck: no progress"))
                    acts[o["id"]] = self.on_final_result(o["id"])
        return acts

    def view(self, o):
        pv, fn = self.worker(o["id"], "preview"), self.worker(o["id"], "final")
        v = {"id": o["id"], "state": o.get("state"), "options": o.get("options"), "upload": o.get("upload"), "price": PRICE_CENTS / 100,
             "preview": {k: pv.get(k) for k in ("state", "stage", "reason", "progress")}, "paid": bool(o.get("paid")),
             "stripe_mode": o.get("stripe_mode")}
        if o.get("state") == "uploading" and self.s.size(f"uploads/{o['id']}/input.mp4"): v["state"] = "uploaded"
        if pv.get("state") == "done":
            v["preview"]["url"] = self.s.presign_get(f"outputs/{o['id']}/preview.mp4", 3600)
            v["preview"]["metrics"] = {"total_s": (pv.get("timing") or {}).get("total_s"), "compute_usd": pv.get("compute_usd")}
        if pv.get("state") in ("failed", "rejected"): v["preview"]["error"] = pv.get("reason") or "We couldn't render this video. Please try another file."
        if o.get("paid"):
            v["final"] = {k: fn.get(k) for k in ("state", "stage", "progress")}
            if o.get("state") == "delivered" or fn.get("state") == "done":
                v["final"]["url"] = self.s.presign_get(f"outputs/{o['id']}/final.mp4", 3600, f"EVA_{o['id']}.mp4")
                v["final"]["expires"] = (o.get("delivered_at") or time.time()) + 7 * 86400
                if fn.get("report"): v["final"].update({k: fn["report"].get(k) for k in ("width", "height", "duration", "music")})
                v["final"]["metrics"] = {"total_s": (fn.get("timing") or {}).get("total_s"), "compute_usd": fn.get("compute_usd")}
            if o.get("refunded"): v["refunded"] = {"at": o["refunded"]["at"]}
        return v


def make_app(svc: Service, webhook_secret=lambda: os.environ.get("STRIPE_WEBHOOK_SECRET"), local_store=None):
    async def body(req):
        try: return await req.json()
        except Exception: return {}

    def site_of(req):
        o = req.headers.get("origin", "")
        return o if ORIGIN_OK.match(o) else os.environ.get("EVA_SITE_URL", "https://eva-video-studio.vercel.app")

    async def config(req):
        return JSONResponse({"price": PRICE_CENTS / 100, "max_bytes": MAX_BYTES, "max_seconds": MAX_SECONDS, "preview_seconds": PREVIEW_SECONDS,
                             "templates": TEMPLATES, "tracks": TRACKS, "stripe_mode": stripe.mode()})

    async def uploads(req):
        b = await body(req)
        try: return JSONResponse(svc.create(client_ip(req), b.get("name"), b.get("size"), b.get("type")))
        except ValueError as e: return err(str(e))
        except PermissionError as e: return err(str(e), 429)

    async def job(req):
        o = svc.auth(req.path_params["job"], req.query_params.get("t"))
        return JSONResponse(svc.view(o)) if o else err("not found", 404)

    async def preview(req):
        b = await body(req); o = svc.auth(req.path_params["job"], b.get("token"))
        if not o: return err("not found", 404)
        try: return JSONResponse(svc.view(svc.preview(o, client_ip(req), b)))
        except ValueError as e: return err(str(e))
        except PermissionError as e: return err(str(e), 429)

    async def checkout(req):
        b = await body(req); o = svc.auth(req.path_params["job"], b.get("token"))
        if not o: return err("not found", 404)
        try: return JSONResponse({"url": svc.checkout(o, site_of(req), b.get("token"))})
        except ValueError as e: return err(str(e))
        except stripe.StripeError as e: return err(f"payment unavailable: {e}", 503)

    async def webhook(req):
        raw = await req.body(); sec = webhook_secret()
        if not sec: return err("webhook not configured", 503)
        try: stripe.verify(raw, req.headers.get("stripe-signature", ""), sec)
        except stripe.StripeError as e: return err(str(e), 400)
        ev = json.loads(raw); typ = ev.get("type", "")
        if typ in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
            res = svc.on_paid(ev["data"]["object"])
        else: res = "ignored"
        return JSONResponse({"received": True, "result": res})

    async def health(req): return JSONResponse({"ok": True, "stripe": stripe.mode()})

    routes = [Route("/api/config", config), Route("/api/health", health), Route("/api/uploads", uploads, methods=["POST"]),
              Route("/api/jobs/{job}", job), Route("/api/jobs/{job}/preview", preview, methods=["POST"]),
              Route("/api/jobs/{job}/checkout", checkout, methods=["POST"]), Route("/api/stripe/webhook", webhook, methods=["POST"])]
    if local_store is not None:   # tests / local runs: stands in for R2 presigned PUT/GET
        async def local(req):
            p = local_store.r / req.path_params["key"]
            if req.method == "PUT":
                data = await req.body()
                if req.query_params.get("size") and len(data) != int(req.query_params["size"]): return err("size mismatch", 403)
                p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); return Response(status_code=200)
            return Response(p.read_bytes(), media_type="video/mp4") if p.exists() else err("missing", 404)
        routes.append(Route("/_local/{key:path}", local, methods=["GET", "PUT"]))
    mw = [Middleware(CORSMiddleware, allow_origin_regex=ORIGIN_OK.pattern, allow_methods=["GET", "POST", "PUT"], allow_headers=["content-type"])]
    return Starlette(routes=routes, middleware=mw)
