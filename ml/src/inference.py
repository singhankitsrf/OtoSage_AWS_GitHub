from __future__ import annotations
import io, json, math
import numpy as np, torch
from PIL import Image
from torch import nn
from torchvision import transforms
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s


def model_fn(model_dir):
    ck = torch.load(f"{model_dir}/model.pt", map_location="cpu")
    model = efficientnet_v2_s(weights=None)
    n = model.classifier[-1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(float(ck.get("dropout", 0.25))), nn.Linear(n, len(ck["class_names"]))
    )
    model.load_state_dict(ck["model_state"])
    model.eval()
    return {"model": model, "class_names": ck["class_names"], "image_size": int(ck["image_size"])}


def input_fn(request_body, content_type):
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError(f"Unsupported content type: {content_type}")
    return Image.open(io.BytesIO(request_body)).convert("RGB")


def _normalized_entropy(probs):
    p = np.clip(np.asarray(probs, dtype=float), 1e-12, 1.0)
    return float(-np.sum(p * np.log(p)) / math.log(len(p)))


def predict_fn(image, bundle):
    model = bundle["model"]
    names = bundle["class_names"]
    size = bundle["image_size"]
    w = EfficientNet_V2_S_Weights.DEFAULT
    tf = transforms.Compose(
        [
            transforms.Resize(int(size * 1.14)),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=w.transforms().mean, std=w.transforms().std),
        ]
    )
    with torch.inference_mode():
        probs = torch.softmax(model(tf(image).unsqueeze(0)), 1)[0].numpy()
    idx = int(probs.argmax())
    conf = float(probs[idx])
    ent = _normalized_entropy(probs)
    return {
        "predicted_class": names[idx],
        "confidence": conf,
        "normalized_entropy": ent,
        "review_recommended": bool(conf < 0.75 or ent > 0.65),
        "probabilities": {n: float(probs[i]) for i, n in enumerate(names)},
        "disclaimer": "Research-only prediction; not a clinical diagnosis.",
    }


def output_fn(prediction, accept):
    return json.dumps(prediction), "application/json"
