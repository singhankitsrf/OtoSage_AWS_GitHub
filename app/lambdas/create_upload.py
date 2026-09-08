from __future__ import annotations
import json, os, uuid
import boto3
from common import log_event, now_iso, response

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
BUCKET = os.environ["INFERENCE_BUCKET"]
TABLE = ddb.Table(os.environ["JOBS_TABLE"])
TTL = int(os.getenv("UPLOAD_TTL_SECONDS", "900"))
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Body must be valid JSON."})
    content_type = body.get("content_type", "image/jpeg")
    if content_type not in ALLOWED:
        return response(415, {"error": "Unsupported image content type."})
    job_id = str(uuid.uuid4())
    key = f"incoming/{job_id}{ALLOWED[content_type]}"
    TABLE.put_item(
        Item={
            "job_id": job_id,
            "status": "AWAITING_UPLOAD",
            "content_type": content_type,
            "input_key": key,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        },
        ConditionExpression="attribute_not_exists(job_id)",
    )
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=TTL,
    )
    log_event("upload_url_created", job_id=job_id, key=key)
    return response(
        201, {"job_id": job_id, "upload_url": url, "object_key": key, "expires_in_seconds": TTL}
    )
