from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pandas as pd
from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import train_test_split

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def scan(root):
    rows = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        try:
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                w, h = im.size
                mode = im.mode
            rows.append(
                {
                    "path": str(path),
                    "filename": path.name,
                    "class_name": path.parent.name,
                    "sha256": sha256(path),
                    "readable": True,
                    "width": w,
                    "height": h,
                    "mode": mode,
                }
            )
        except (UnidentifiedImageError, OSError):
            rows.append(
                {
                    "path": str(path),
                    "filename": path.name,
                    "class_name": path.parent.name,
                    "sha256": "",
                    "readable": False,
                    "width": None,
                    "height": None,
                    "mode": "",
                }
            )
    return pd.DataFrame(rows)


def prepare(frame, seed=42):
    frame = frame.copy()
    readable = frame[frame["readable"]].copy()
    conflict = (
        readable.groupby("sha256")["class_name"]
        .nunique()
        .reset_index(name="n_classes")
        .query("n_classes > 1")
    )
    if not conflict.empty:
        raise RuntimeError("Identical image bytes appear under multiple labels.")
    frame["is_exact_duplicate"] = False
    frame["canonical_path"] = ""
    for digest, group in readable.groupby("sha256"):
        canonical = sorted(group["path"].tolist())[0]
        frame.loc[group.index, "canonical_path"] = canonical
        dup_idx = group[group["path"] != canonical].index
        frame.loc[dup_idx, "is_exact_duplicate"] = True
    canonical = frame[frame["readable"] & (~frame["is_exact_duplicate"])].copy()
    tr, tmp = train_test_split(
        canonical.index, test_size=0.30, random_state=seed, stratify=canonical["class_name"]
    )
    va, te = train_test_split(
        tmp, test_size=0.50, random_state=seed, stratify=canonical.loc[tmp, "class_name"]
    )
    frame["split"] = "excluded"
    frame.loc[tr, "split"] = "train"
    frame.loc[va, "split"] = "val"
    frame.loc[te, "split"] = "test"
    frame.loc[~frame["readable"], "split"] = "invalid"
    return frame


def copy_splits(frame, dst):
    dst = Path(dst)
    for split in ("train", "val", "test"):
        for _, row in frame[frame["split"] == split].iterrows():
            src = Path(row["path"])
            out = dst / split / row["class_name"] / src.name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default="/opt/ml/processing/input")
    ap.add_argument("--output-dir", default="/opt/ml/processing/output")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    frame = scan(a.input_dir)
    if frame.empty:
        raise RuntimeError("No images found.")
    frame = prepare(frame, a.seed)
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out / "manifest.csv", index=False)
    copy_splits(frame, out)
    canonical = frame[frame["readable"] & (~frame["is_exact_duplicate"])]
    report = {
        "total_files": len(frame),
        "readable_files": int(frame["readable"].sum()),
        "exact_duplicate_surplus": int(frame["is_exact_duplicate"].sum()),
        "canonical_files": len(canonical),
        "class_counts": canonical["class_name"].value_counts().sort_index().to_dict(),
        "split_counts": canonical["split"].value_counts().to_dict(),
    }
    (out / "data_quality.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
