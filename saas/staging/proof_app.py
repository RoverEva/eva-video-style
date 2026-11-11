"""EVA Video Studio · STAGING proof render (separate Modal app; never the production app or its volume).

    modal run saas/staging/proof_app.py --pid pa04f1da3d9d --old-vid v7f5b675a309 --templates T23,T21,T17,T02,T01

Three private Modal containers (dev-branch code), each with only the secret it needs:
  1. reads the original upload + its ASR/face cache + the old production preview from R2 (server-side; nothing leaves R2)
  2. for 16:9 and 9:16: plans with Claude Opus 5.5 (real Anthropic API, Modal secret `eva-anthropic-staging`), renders the
     full clip in HD, renders the full-length 720p watermarked preview, runs visual QA (coverage, motion, relevance, face,
     captions), builds contact sheets and a side-by-side comparison with the old production preview
  3. uploads everything to the PRIVATE prefix  staging/proofs/<run>/  in the same bucket (download in the Cloudflare
     dashboard; the prefix is deleted by `--cleanup <run>`)
  4. returns ONLY aggregate numbers (model id, tokens, cost, coverage, verdicts, file names) — no video, transcript, card
     text or storyboard ever goes to stdout/GitHub logs: all worker output is captured into a log file stored in R2.
Secrets: fetch/publish get eva-r2 only; render gets eva-anthropic-staging only. No Stripe, Supabase or mail secrets anywhere.
"""
import contextlib, io, json, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent.parent
app = modal.App("eva-video-studio-staging")
image = modal.Image.from_dockerfile(str(ROOT / "saas/Dockerfile"), context_dir=str(ROOT))
vol = modal.Volume.from_name("eva-staging-jobs", create_if_missing=True)
# Secrets are looked up per Modal environment. The app runs in the environment Eva chose for staging (modal run --env);
# R2 access may live in another environment (EVA_R2_SECRET_ENV). required_keys makes Modal refuse to start without them.
ANTHROPIC_SECRET = modal.Secret.from_name("eva-anthropic-staging", environment_name=os.environ.get("EVA_ANTHROPIC_SECRET_ENV") or None, required_keys=["ANTHROPIC_API_KEY"])
R2_SECRET = modal.Secret.from_name("eva-r2", environment_name=os.environ.get("EVA_R2_SECRET_ENV") or None)
CACHE = ["srt/talk.asr.json", "srt/talk.bilingual.srt", "srt/talk.transcript.js", "srt/talk.en.srt", "face.json"]


def _sh(cmd): subprocess.run([str(c) for c in cmd], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _sheet(mp4, out, cols=6):   # contact sheet: 1 frame per second
    _sh(["ffmpeg", "-loglevel", "error", "-y", "-i", mp4, "-vf", f"fps=1,scale=480:-2,tile={cols}x3:padding=6:color=white", "-frames:v", "1", out])


LIMITS = dict(cpu=4.0, memory=8192, timeout=3600)   # resource limits of the render container
_paths = lambda: [sys.path.insert(0, p) for p in ("/app/saas/worker", "/app/saas/web")]


@app.function(image=image, volumes={"/jobs": vol}, secrets=[R2_SECRET], timeout=600)
def fetch(run: str, pid: str, old_vid: str):
    """R2 → private staging volume: ONLY this project's upload, its transcript/face cache and the old preview."""
    _paths(); import store; S = store.from_env(); base = Path(f"/jobs/{run}/in"); (base / "cache/srt").mkdir(parents=True)
    src = next((k for k in (f"projects/{pid}/source.mp4", f"uploads/{pid}/input.mp4") if S.size(k)), None)   # v2 projects keep the source at projects/<pid>/source.mp4
    if not src: return {"error": "source video not found in R2 (expired or wrong project id)"}
    S.download(src, base / "input.mp4"); got = []
    for f in CACHE:
        if S.size(f"projects/{pid}/cache/{f}"): S.download(f"projects/{pid}/cache/{f}", base / "cache" / f); got.append(f)
    try: S.download(f"versions/{old_vid}/video.mp4", base / "old_preview.mp4")
    except Exception: pass
    vol.commit(); return {"source": src.split("/")[-1], "cache": got, "old_preview": (base / "old_preview.mp4").exists()}


@app.function(image=image, volumes={"/jobs": vol}, secrets=[ANTHROPIC_SECRET], **LIMITS)
def render(run: str, templates: str, aspects: str = "16:9,9:16", instructions: str = ""):
    """Plan with Claude Opus 5.5 + render, isolated: no R2, Stripe, Supabase or mail credentials in this container
    (only the staging Anthropic key the planner needs) and only this run's folder on the volume."""
    _paths(); import pipeline
    vol.reload(); base = Path(f"/jobs/{run}"); src = base / "in/input.mp4"; old = base / "in/old_preview.mp4"
    out = base / "out"; out.mkdir(exist_ok=True); log = io.StringIO(); summary = {"run": run, "prefix": f"staging/proofs/{run}/", "results": {}}
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        for ar in aspects.split(","):
            tag = ar.replace(":", "x"); wd = base / tag / "work"; shutil.copytree(base / "in/cache", wd)
            if (wd / "srt/talk.transcript.js").exists(): (wd / "srt/.restored").write_text("cache")   # same source: reuse its transcript
            opts = {"aspect": ar, "templates": templates.split(","), "template_mode": "multi", "music": "mix", "music_tracks": [],
                    "paid": True, "preview_seconds": 30, "instructions": instructions}
            of = base / tag / "opts.json"; of.write_text(json.dumps(opts)); t = time.time(); r = {}
            try: r["rc"] = pipeline.main(["run", str(src), str(wd), "--options", str(of), "--workers", "4"])
            except SystemExit as e: r["rc"] = e.code
            except Exception as e: r["rc"] = -1; r["error"] = type(e).__name__ + ": " + str(e).split("(")[0].split(":")[0][:90]   # no transcript text
            r["render_wall_s"] = round(time.time() - t, 1)
            plog = wd / "logs/prepare.log"   # API errors are Anthropic's own text (safe); validation errors may quote speech → counted only
            for line in (plog.read_text(errors="replace").splitlines() if plog.exists() else []):
                if "AI storyboard failed:" in line:
                    m = line.split("AI storyboard failed:", 1)[1].strip()
                    r["planner_error"] = m[:400] if m.startswith(("Anthropic API", "The AI storyboard is not configured", "only claude", "Claude returned")) else m.split("(")[0][:80] + "(details withheld: may quote speech)"
            plan = json.loads((wd / "plan.json").read_text()) if (wd / "plan.json").exists() else {}
            pl = plan.get("planner") or {}
            r.update(model=pl.get("model") or pl.get("source"), usage=pl.get("usage"), attempts=[{"attempt": a["attempt"], "errors": len(a["errors"]), "seconds": a["seconds"]} for a in pl.get("attempts") or []],
                     beats=len((plan.get("storyboard") or {}).get("beats") or []), components=sorted({c["kind"] for c in plan.get("cards", [])}))
            fin = wd / "out/final.mp4"
            if fin.exists():
                shutil.copy(fin, out / f"new_{tag}_HD.mp4"); _sheet(fin, out / f"new_{tag}_contact_sheet.jpg")
                # full-length 720p watermarked preview, same command as the product (pipeline deliver)
                pw, ph = pipeline.PREVIEW[ar]; font = pipeline.ENGINE_REPO / "engine/fonts/Anton-Regular.ttf"; fs = round(pw / 20)
                mark = f"drawtext=fontfile={font}:text='EVA VIDEO STUDIO · PREVIEW':fontsize={fs}:fontcolor=white@0.45:shadowcolor=black@0.35:shadowx=2:shadowy=2"
                _sh(["ffmpeg", "-loglevel", "error", "-y", "-i", fin, "-vf", f"scale={pw}:{ph},{mark}:x=(w-text_w)/2:y=h*0.30,{mark}:x=(w-text_w)/2:y=h*0.62",
                     "-c:v", "libx264", "-crf", "28", "-preset", "veryfast", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out / f"new_{tag}_preview_720p.mp4"])
                cov = wd / "out/coverage"
                for f in ("coverage.json", "coverage.md", "timeline.png"):
                    if (cov / f).exists(): shutil.copy(cov / f, out / f"new_{tag}_{f}")
                rep = json.loads((wd / "out/report_final.json").read_text()); c = rep.get("coverage") or {}
                r["qa"] = {k: c.get(k) for k in ("verdict", "meaningful_coverage", "template_coverage", "raw_s", "longest_raw_s", "unexplained_raw_s")}
                r["qa"]["motion"] = c.get("motion"); r["qa"]["content"] = c.get("content"); r["qa"]["templates"] = c.get("templates")
                r["qa"]["issues"] = [i["severity"] + " " + i["text"].split(":")[0] for i in c.get("issues") or []]
                r["video"] = {k: rep.get(k) for k in ("duration", "width", "height", "lufs")}
                (out / f"new_{tag}_storyboard.json").write_text(json.dumps(plan.get("storyboard"), indent=1, ensure_ascii=False))
                if old.exists():   # side by side: old production preview (10 s, then frozen) | new edit, both letterboxed
                    fit = "scale=960:540:force_original_aspect_ratio=decrease,pad=960:540:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
                    _sh(["ffmpeg", "-loglevel", "error", "-y", "-i", old, "-i", fin, "-filter_complex",
                         f"[0:v]{fit},tpad=stop_mode=clone:stop_duration=30[a];[1:v]{fit}[b];[a][b]hstack=shortest=1[v]",
                         "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-shortest", out / f"compare_old_vs_new_{tag}.mp4"])
            if (wd / "pipeline.log").exists(): shutil.copy(wd / "pipeline.log", out / f"{tag}_pipeline.log")
            r["files"] = sorted(p.name for p in out.iterdir() if p.name.startswith(("new_" + tag, "compare_old_vs_new_" + tag)))
            summary["results"][ar] = r
    (out / "worker.log").write_text(log.getvalue()); vol.commit()
    return summary


@app.function(image=image, volumes={"/jobs": vol}, secrets=[R2_SECRET], timeout=900)
def publish(run: str):
    """staging volume → the PRIVATE R2 prefix staging/proofs/<run>/; then the run folder is removed from the volume."""
    _paths(); import store; S = store.from_env(); vol.reload(); out = Path(f"/jobs/{run}/out"); n = 0
    CT = {"mp4": "video/mp4", "jpg": "image/jpeg", "png": "image/png", "json": "application/json", "md": "text/markdown", "log": "text/plain"}
    for p in sorted(out.iterdir()): S.upload(p, f"staging/proofs/{run}/{p.name}", CT[p.suffix[1:]]); n += 1
    shutil.rmtree(f"/jobs/{run}"); vol.commit(); return {"uploaded": n}


@app.function(image=image, secrets=[R2_SECRET], timeout=300)
def cleanup(run: str):
    for p in ("/app/saas/worker", "/app/saas/web"): sys.path.insert(0, p)
    import store; S = store.from_env(); n = len(S.list(f"staging/proofs/{run}/")); S.delete_prefix(f"staging/proofs/{run}/")
    return {"deleted": n}


@app.function(image=image, secrets=[ANTHROPIC_SECRET], timeout=120)
def ping():   # smallest real Claude Opus 5.5 call: proves the key, the model id and the cost bookkeeping
    import urllib.request
    body = {"model": "claude-opus-5-5", "max_tokens": 20, "messages": [{"role": "user", "content": "Reply with the single word: ready"}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: j = json.loads(r.read())
    u = j.get("usage", {}); return {"model": j.get("model"), "usage": u, "usd": round((u.get("input_tokens", 0) * 4 + u.get("output_tokens", 0) * 20) / 1e6, 6),
                                    "reply_ok": "ready" in json.dumps(j.get("content")).lower()}


LINK_IMAGE = modal.Image.debian_slim(python_version="3.12").pip_install("boto3==1.35.90", "cryptography==44.0.0")


@app.function(image=LINK_IMAGE, secrets=[R2_SECRET], timeout=120)
def links(run: str, pubkey_pem: str, hours: int = 48):
    """Private, temporary download links: presigned GET URLs (expire after `hours`) for every file of the run, ENCRYPTED with
    a public key (RSA-OAEP + AES-256-GCM). Only the holder of the private key (Claude's session, never the repo or the log)
    can read them; the public log shows ciphertext only."""
    import base64, boto3
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    c = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID'].strip()}.r2.cloudflarestorage.com", region_name="auto",
                     aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"].strip(), aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"].strip())
    b = (os.environ.get("R2_BUCKET") or "eva-video-studio").strip(); pre = f"staging/proofs/{run}/"
    keys = [o["Key"] for o in c.list_objects_v2(Bucket=b, Prefix=pre).get("Contents", [])]
    urls = {k[len(pre):]: c.generate_presigned_url("get_object", Params={"Bucket": b, "Key": k, "ResponseContentDisposition": "inline"}, ExpiresIn=hours * 3600) for k in keys}
    data = json.dumps({"run": run, "expires_h": hours, "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "urls": urls}).encode()
    k, n = AESGCM.generate_key(256), os.urandom(12)
    ek = serialization.load_pem_public_key(pubkey_pem.encode()).encrypt(k, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return {"files": len(urls), "ek": base64.b64encode(ek).decode(), "nonce": base64.b64encode(n).decode(), "ct": base64.b64encode(AESGCM(k).encrypt(n, data, None)).decode()}


@app.function(image=modal.Image.debian_slim(), secrets=[ANTHROPIC_SECRET], timeout=60)
def check_anthropic():   # configuration check only: no API call, the key is never returned or printed
    k = os.environ.get("ANTHROPIC_API_KEY", ""); other = sorted(n for n in os.environ if any(w in n.upper() for w in ("STRIPE", "SUPABASE", "R2_", "RESEND", "SMTP", "DATABASE")))
    return {"key_present": bool(k.strip()), "key_format_ok": k.strip().startswith("sk-ant-"), "whitespace_around_key": k != k.strip(), "other_service_vars_in_render": other}


@app.function(image=modal.Image.debian_slim(), secrets=[R2_SECRET], timeout=60)
def check_r2():
    return {"r2_vars_present": all(os.environ.get(n, "").strip() for n in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")),
            "anthropic_key_in_storage_containers": "ANTHROPIC_API_KEY" in os.environ}


@app.local_entrypoint()
def main(pid: str = "pa04f1da3d9d", old_vid: str = "v7f5b675a309", templates: str = "T23,T21,T17,T02,T01", aspects: str = "16:9,9:16", skip_ping: bool = False, check_only: bool = False, links_only: str = ""):
    if links_only:   # new temporary links for an existing run (old ones expired)
        print("LINKS", json.dumps(links.remote(links_only, os.environ["EVA_LINKS_PUBKEY"]))); return
    if check_only:
        print("CHECK", json.dumps({"render_secrets": ["eva-anthropic-staging"], "fetch_publish_secrets": ["eva-r2"], "anthropic": check_anthropic.remote(), "r2": check_r2.remote()})); return
    if not skip_ping: print("PING", json.dumps(ping.remote()))
    run = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    f = fetch.remote(run, pid, old_vid); print("FETCH", json.dumps(f))
    if f.get("error"): return
    res = render.remote(run, templates, aspects)
    print("PUBLISH", json.dumps(publish.remote(run)))
    print("PROOF", json.dumps(res))
    pk = os.environ.get("EVA_LINKS_PUBKEY", "")
    if pk: print("LINKS", json.dumps(links.remote(run, pk)))
