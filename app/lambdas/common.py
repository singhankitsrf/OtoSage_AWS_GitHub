from __future__ import annotations
import json, logging, os
from datetime import datetime, timezone

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def response(status_code, body):
    return {"statusCode": status_code,
            "headers": {"content-type":"application/json","cache-control":"no-store"},
            "body": json.dumps(body)}

def log_event(event_name, **fields):
    LOGGER.info(json.dumps({"event":event_name, **fields}, default=str))
