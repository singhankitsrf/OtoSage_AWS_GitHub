from __future__ import annotations
import argparse, json, tarfile, hashlib
from pathlib import Path
import numpy as np, torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s


def ece(y, probs, bins=15):
    conf = probs.max(1)
    pred = probs.argmax(1)
    corr = (pred == y).astype(float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            total += m.mean() * abs(corr[m].mean() - conf[m].mean())
    return float(total)


def brier(y, p):
    return float(np.mean(np.sum((p - np.eye(p.shape[1])[y]) ** 2, axis=1)))


@torch.inference_mode()
def predict(model, loader, device):
    ys = []
    ps = []
    model.eval()
    for x, y in loader:
        p = torch.softmax(model(x.to(device)), 1).cpu().numpy()
        ys.extend(y.numpy())
        ps.extend(p)
    return np.asarray(ys), np.asarray(ps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default="/opt/ml/processing/model")
    ap.add_argument("--test-dir", default="/opt/ml/processing/test")
    ap.add_argument("--output-dir", default="/opt/ml/processing/evaluation")
    a = ap.parse_args()
    md = Path(a.model_dir)
    ext = md / "extracted"
    ext.mkdir(parents=True, exist_ok=True)
    with tarfile.open(md / "model.tar.gz", "r:gz") as tar:
        tar.extractall(ext, filter="data")
    ck = torch.load(ext / "model.pt", map_location="cpu")
    names = ck["class_names"]
    size = int(ck["image_size"])
    model = efficientnet_v2_s(weights=None)
    n = model.classifier[-1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(float(ck.get("dropout", 0.25))), nn.Linear(n, len(names))
    )
    model.load_state_dict(ck["model_state"])
    w = EfficientNet_V2_S_Weights.DEFAULT
    tf = transforms.Compose(
        [
            transforms.Resize(int(size * 1.14)),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=w.transforms().mean, std=w.transforms().std),
        ]
    )
    ds = datasets.ImageFolder(a.test_dir, transform=tf)
    if ds.classes != names:
        raise RuntimeError("Test class order mismatch.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    y, p = predict(model, DataLoader(ds, batch_size=64, shuffle=False, num_workers=2), device)
    pred = p.argmax(1)
    metrics = {
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "ece": ece(y, p),
        "brier_score": brier(y, p),
    }
    try:
        metrics["macro_roc_auc_ovr"] = float(
            roc_auc_score(y, p, average="macro", multi_class="ovr")
        )
    except ValueError:
        metrics["macro_roc_auc_ovr"] = None
    payload = {
        "classification_metrics": metrics,
        "class_report": classification_report(
            y, pred, target_names=names, output_dict=True, zero_division=0
        ),
        "class_names": names,
    }
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps(payload, indent=2))
    np.savez_compressed(
        out / "predictions.npz", y_true=y, probabilities=p, class_names=np.asarray(names)
    )
    provenance = {
        "checkpoint_sha256": hashlib.sha256((ext / "model.pt").read_bytes()).hexdigest(),
        "test_samples": len(y),
        "class_names": names,
        "scope": "image-level holdout; patient independence not established",
    }
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
