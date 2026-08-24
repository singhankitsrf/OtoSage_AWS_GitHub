from __future__ import annotations
import argparse, mimetypes
from pathlib import Path
import boto3
SUPPORTED={".jpg",".jpeg",".png",".webp"}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-root",required=True); ap.add_argument("--bucket",required=True); ap.add_argument("--prefix",default="raw/"); ap.add_argument("--region",default=None); a=ap.parse_args(); root=Path(a.data_root); files=[p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED]
    if not files: raise RuntimeError("No supported images found.")
    s3=boto3.Session(region_name=a.region).client("s3")
    for i,p in enumerate(sorted(files),1): rel=p.relative_to(root).as_posix(); key=f"{a.prefix.rstrip('/')}/{rel}"; ctype=mimetypes.guess_type(p.name)[0] or "application/octet-stream"; s3.upload_file(str(p),a.bucket,key,ExtraArgs={"ContentType":ctype}); print(f"Uploaded {i}/{len(files)}") if i%100==0 or i==len(files) else None
    print(f"s3://{a.bucket}/{a.prefix.rstrip('/')}/")
if __name__=="__main__": main()
