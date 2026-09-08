from __future__ import annotations
import argparse, mimetypes, time
import requests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-url", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--poll-seconds", type=int, default=4)
    ap.add_argument("--max-polls", type=int, default=60)
    a = ap.parse_args()
    api = a.api_url.rstrip("/")
    ctype = mimetypes.guess_type(a.image)[0] or "image/jpeg"
    r = requests.post(f"{api}/upload", json={"content_type": ctype}, timeout=30)
    r.raise_for_status()
    job = r.json()
    print("job_id=", job["job_id"])
    with open(a.image, "rb") as f:
        u = requests.put(job["upload_url"], data=f, headers={"content-type": ctype}, timeout=120)
    u.raise_for_status()
    for _ in range(a.max_polls):
        s = requests.get(f"{api}/jobs/{job['job_id']}", timeout=30)
        s.raise_for_status()
        payload = s.json()
        print(payload)
        if payload["status"] in {"COMPLETED", "FAILED"}:
            return
        time.sleep(a.poll_seconds)
    raise TimeoutError("Job did not reach a terminal state.")


if __name__ == "__main__":
    main()
