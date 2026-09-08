from __future__ import annotations
import os, urllib.parse
import boto3
from common import log_event, now_iso
from job_utils import job_id_from_key, content_type_for_key

runtime = boto3.client("sagemaker-runtime")
ddb = boto3.resource("dynamodb")
TABLE = ddb.Table(os.environ["JOBS_TABLE"])
ENDPOINT = os.environ["SAGEMAKER_ENDPOINT_NAME"]


def handler(event, context):
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        if not key.startswith("incoming/"):
            continue
        job_id = job_id_from_key(key)
        input_location = f"s3://{bucket}/{key}"
        result = runtime.invoke_endpoint_async(
            EndpointName=ENDPOINT,
            InputLocation=input_location,
            InferenceId=job_id,
            ContentType=content_type_for_key(key),
            Accept="application/json",
        )
        TABLE.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET #s=:s, updated_at=:u, inference_id=:i, output_location=:o",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "SUBMITTED",
                ":u": now_iso(),
                ":i": result.get("InferenceId", job_id),
                ":o": result.get("OutputLocation", ""),
            },
        )
        log_event("async_inference_submitted", job_id=job_id, endpoint=ENDPOINT)
    return {"ok": True}
