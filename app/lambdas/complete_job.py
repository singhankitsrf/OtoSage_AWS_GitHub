from __future__ import annotations
import json, os
import boto3
from common import log_event, now_iso

ddb = boto3.resource("dynamodb")
TABLE = ddb.Table(os.environ["JOBS_TABLE"])


def handler(event, context):
    for record in event.get("Records", []):
        raw = record.get("Sns", {}).get("Message", "{}")
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            message = {"raw_message": raw}
        inference_id = (
            message.get("inferenceId") or message.get("InferenceId") or message.get("inference_id")
        )
        if not inference_id:
            log_event("completion_missing_inference_id", message=message)
            continue
        status = (
            message.get("inferenceStatus") or message.get("InferenceStatus") or "COMPLETED"
        ).upper()
        final = "FAILED" if status in {"FAILED", "FAILURE", "ERROR"} else "COMPLETED"
        output = None
        rp = message.get("responseParameters")
        if isinstance(rp, dict):
            output = rp.get("outputLocation")
        output = output or message.get("outputLocation")
        reason = message.get("failureReason") or message.get("FailureReason")
        expr = "SET #s=:s, updated_at=:u"
        names = {"#s": "status"}
        vals = {":s": final, ":u": now_iso()}
        if output:
            expr += ", output_location=:o"
            vals[":o"] = output
        if reason:
            expr += ", failure_reason=:r"
            vals[":r"] = str(reason)[:1500]
        TABLE.update_item(
            Key={"job_id": inference_id},
            UpdateExpression=expr,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=vals,
        )
        log_event("inference_completed", job_id=inference_id, status=final)
    return {"ok": True}
