from __future__ import annotations
import os
from urllib.parse import urlparse
import boto3
from common import log_event, response

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
TABLE = ddb.Table(os.environ["JOBS_TABLE"])
TTL = int(os.getenv("RESULT_URL_TTL_SECONDS", "900"))


def _parse_s3(uri):
    p = urlparse(uri)
    if p.scheme != "s3":
        raise ValueError("Not S3")
    return p.netloc, p.path.lstrip("/")


def handler(event, context):
    job_id = (event.get("pathParameters") or {}).get("job_id")
    if not job_id:
        return response(400, {"error": "Missing job_id."})
    item = TABLE.get_item(Key={"job_id": job_id}).get("Item")
    if not item:
        return response(404, {"error": "Job not found."})
    out = {
        "job_id": job_id,
        "status": item.get("status"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }
    if item.get("failure_reason"):
        out["failure_reason"] = item["failure_reason"]
    if item.get("status") == "COMPLETED" and item.get("output_location"):
        try:
            b, k = _parse_s3(item["output_location"])
            out["result_url"] = s3.generate_presigned_url(
                "get_object", Params={"Bucket": b, "Key": k}, ExpiresIn=TTL
            )
            out["result_url_expires_in_seconds"] = TTL
        except ValueError:
            out["output_location"] = item["output_location"]
    log_event("job_status_requested", job_id=job_id, status=item.get("status"))
    return response(200, out)
