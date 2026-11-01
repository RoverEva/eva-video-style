"""EVA Video Studio · private Cloudflare R2 storage (S3 API). Keys only come from environment variables
(Modal secret `eva-r2`): R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET.

Layout:  uploads/<job>/input.mp4   (deleted after UPLOAD_DAYS)
         outputs/<job>/{final.mp4, preview.mp4, captions.srt, report_*.json}   (deleted after OUTPUT_DAYS)
The bucket stays private; customers only ever get time-limited presigned URLs."""
import os
import boto3
from botocore.config import Config

UPLOAD_DAYS, OUTPUT_DAYS = 3, 14


def client():
    return boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                        region_name="auto", config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}))


BUCKET = lambda: os.environ["R2_BUCKET"]


def upload(path, key, content_type="video/mp4"): client().upload_file(str(path), BUCKET(), key, ExtraArgs={"ContentType": content_type})
def download(key, path): client().download_file(BUCKET(), key, str(path))
def exists(key):
    try: client().head_object(Bucket=BUCKET(), Key=key); return True
    except Exception: return False


def presign_get(key, seconds=3600, filename=None):
    p = {"Bucket": BUCKET(), "Key": key}
    if filename: p["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
    return client().generate_presigned_url("get_object", Params=p, ExpiresIn=seconds)


def presign_put(key, seconds=900, content_type="video/mp4"):
    return client().generate_presigned_url("put_object", Params={"Bucket": BUCKET(), "Key": key, "ContentType": content_type}, ExpiresIn=seconds)


def apply_retention():
    """Bucket lifecycle rules = automatic deletion of customer media, even if every worker is down."""
    rules = [{"ID": "uploads", "Status": "Enabled", "Filter": {"Prefix": "uploads/"}, "Expiration": {"Days": UPLOAD_DAYS}},
             {"ID": "outputs", "Status": "Enabled", "Filter": {"Prefix": "outputs/"}, "Expiration": {"Days": OUTPUT_DAYS}},
             {"ID": "abort-multipart", "Status": "Enabled", "Filter": {"Prefix": ""}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}}]
    client().put_bucket_lifecycle_configuration(Bucket=BUCKET(), LifecycleConfiguration={"Rules": rules})
    return rules
