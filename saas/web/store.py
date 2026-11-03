"""EVA Video Studio · storage for the web API and workers: private Cloudflare R2 (S3 API), or a local folder for tests.

Bucket layout (all private; customers only ever get short-lived presigned URLs):
    uploads/<job>/input.mp4          customer upload                      deleted after UPLOAD_DAYS (lifecycle rule)
    outputs/<job>/{preview,final}.mp4 rendered files, captions, reports   deleted after OUTPUT_DAYS
    jobs/<job>/{preview,final}.json  worker-owned render status           deleted after OUTPUT_DAYS
    orders/<job>.json                order record (API / webhook owned)   deleted after ORDER_DAYS (Stripe keeps payment records)
    config/stripe_webhook.json       webhook signing secret (written by setup)
Keys come from env (Modal secret `eva-r2`): R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET.
"""
import json, os, shutil, time
from pathlib import Path

UPLOAD_DAYS, OUTPUT_DAYS, ORDER_DAYS = 3, 7, 90
RETENTION = (("uploads/", UPLOAD_DAYS), ("outputs/", OUTPUT_DAYS), ("jobs/", OUTPUT_DAYS), ("orders/", ORDER_DAYS))


class R2:
    def __init__(self):
        import boto3
        from botocore.config import Config
        self.b = os.environ["R2_BUCKET"]
        self.c = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                              aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                              region_name="auto", config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}))

    def put_json(self, key, obj): self.c.put_object(Bucket=self.b, Key=key, Body=json.dumps(obj).encode(), ContentType="application/json")

    def get_json(self, key):
        try: return json.loads(self.c.get_object(Bucket=self.b, Key=key)["Body"].read())
        except self.c.exceptions.NoSuchKey: return None
        except Exception as e:
            if "NoSuchKey" in str(e) or "404" in str(e): return None
            raise

    def size(self, key):
        try: return self.c.head_object(Bucket=self.b, Key=key)["ContentLength"]
        except Exception: return None

    def list(self, prefix):
        out, tok = [], None
        while True:
            kw = {"Bucket": self.b, "Prefix": prefix, **({"ContinuationToken": tok} if tok else {})}
            r = self.c.list_objects_v2(**kw); out += [(o["Key"], o["LastModified"].timestamp()) for o in r.get("Contents", [])]
            if not r.get("IsTruncated"): return out
            tok = r["NextContinuationToken"]

    def upload(self, path, key, ctype="video/mp4"): self.c.upload_file(str(path), self.b, key, ExtraArgs={"ContentType": ctype})
    def download(self, key, path): self.c.download_file(self.b, key, str(path))

    def delete_prefix(self, prefix):
        for k, _ in self.list(prefix): self.c.delete_object(Bucket=self.b, Key=k)

    def presign_put(self, key, size, ctype="video/mp4", seconds=1800):
        # ContentLength is signed: the browser can only upload exactly the announced number of bytes (≤ 200 MB, checked by the API)
        return self.c.generate_presigned_url("put_object", Params={"Bucket": self.b, "Key": key, "ContentType": ctype, "ContentLength": size}, ExpiresIn=seconds)

    def presign_get(self, key, seconds=3600, filename=None):
        p = {"Bucket": self.b, "Key": key}
        if filename: p["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
        return self.c.generate_presigned_url("get_object", Params=p, ExpiresIn=seconds)

    def delete(self, key): self.c.delete_object(Bucket=self.b, Key=key)

    def expire(self):
        """retention without bucket-admin rights: delete objects older than their prefix's period (daily cron)"""
        n = 0
        for prefix, days in RETENTION:
            for k, t in self.list(prefix):
                if time.time() - t > days * 86400: self.delete(k); n += 1
        return n

    def setup_bucket(self):
        """Lifecycle rules delete customer media automatically, even if every worker is down; CORS lets the browser PUT
        straight to R2 with a presigned URL (the URL itself is the authorisation)."""
        rules = [{"ID": p.strip("/"), "Status": "Enabled", "Filter": {"Prefix": p}, "Expiration": {"Days": d}}
                 for p, d in (("uploads/", UPLOAD_DAYS), ("outputs/", OUTPUT_DAYS), ("jobs/", OUTPUT_DAYS), ("orders/", ORDER_DAYS))]
        rules.append({"ID": "abort-multipart", "Status": "Enabled", "Filter": {"Prefix": ""}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}})
        out = {}
        for name, fn in (("lifecycle", lambda: self.c.put_bucket_lifecycle_configuration(Bucket=self.b, LifecycleConfiguration={"Rules": rules})),
                         ("cors", lambda: self.c.put_bucket_cors(Bucket=self.b, CORSConfiguration={"CORSRules": [{"AllowedOrigins": ["*"],
                             "AllowedMethods": ["PUT", "GET", "HEAD"], "AllowedHeaders": ["*"], "ExposeHeaders": ["ETag"], "MaxAgeSeconds": 3600}]}))):
            try: fn(); out[name] = "set"
            except Exception as e:   # bucket-scoped object token: set these once in the Cloudflare dashboard instead
                out[name] = "not permitted for this token (set it in the Cloudflare dashboard)" if "AccessDenied" in str(e) or "403" in str(e) else f"error: {e}"[:200]
        return out


class Local:
    """Same interface on a folder (tests and local runs). Presigned URLs point at the API's /_local route."""
    def __init__(self, root, base_url="http://testserver"):
        self.r = Path(root); self.r.mkdir(parents=True, exist_ok=True); self.base = base_url

    def _p(self, key): return self.r / key
    def put_json(self, key, obj): p = self._p(key); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(obj))
    def get_json(self, key): p = self._p(key); return json.loads(p.read_text()) if p.exists() else None
    def size(self, key): p = self._p(key); return p.stat().st_size if p.exists() else None
    def list(self, prefix): return [(str(p.relative_to(self.r)), p.stat().st_mtime) for p in self.r.rglob("*") if p.is_file() and str(p.relative_to(self.r)).startswith(prefix)]
    def upload(self, path, key, ctype=None): p = self._p(key); p.parent.mkdir(parents=True, exist_ok=True); shutil.copy(path, p)
    def download(self, key, path): Path(path).parent.mkdir(parents=True, exist_ok=True); shutil.copy(self._p(key), path)
    def delete_prefix(self, prefix):
        for k, _ in self.list(prefix): self._p(k).unlink()
    def presign_put(self, key, size, ctype="video/mp4", seconds=1800): return f"{self.base}/_local/{key}?size={size}"
    def presign_get(self, key, seconds=3600, filename=None): return f"{self.base}/_local/{key}"
    def delete(self, key): self._p(key).unlink(missing_ok=True)
    def expire(self):
        n = 0
        for prefix, days in RETENTION:
            for k, t in self.list(prefix):
                if time.time() - t > days * 86400: self.delete(k); n += 1
        return n
    def setup_bucket(self): return {}


def from_env():
    if os.environ.get("EVA_LOCAL_STORE"): return Local(os.environ["EVA_LOCAL_STORE"], os.environ.get("EVA_LOCAL_BASE", "http://127.0.0.1:8000"))
    return R2()


def now(): return time.time()
