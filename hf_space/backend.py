"""Image QA is available without weights; disease predictions require a real checkpoint."""

from __future__ import annotations
import hashlib
import os
from pathlib import Path
import numpy as np
from PIL import Image

KIND = "aws"
BUNDLE = None
MODEL_HASH = None
MODEL_STATUS = "No trained checkpoint configured. Image quality inspection only."


def load_model():
    global BUNDLE, MODEL_HASH, MODEL_STATUS
    local = os.getenv("MODEL_PATH")
    repo_id, revision = os.getenv("HF_MODEL_REPO"), os.getenv("HF_MODEL_REVISION")
    if repo_id:
        if (
            not revision
            or len(revision) != 40
            or any(c not in "0123456789abcdef" for c in revision.lower())
        ):
            raise ValueError("Set HF_MODEL_REVISION to a full immutable commit SHA")
        if not repo_id.startswith("singhankit491/"):
            raise ValueError("Use a reviewed model repository in singhankit491")
        from huggingface_hub import hf_hub_download

        filename = "best.pt" if KIND == "vision" else "model.pt"
        local = hf_hub_download(
            repo_id, filename=filename, revision=revision, token=os.getenv("HF_TOKEN")
        )
    if not local:
        return
    checkpoint = Path(local)
    if KIND == "vision":
        from otovision.inference import load_checkpoint

        BUNDLE = load_checkpoint(checkpoint, device="cpu")
    else:
        from ml.src.inference import model_fn

        if checkpoint.name != "model.pt":
            raise ValueError("OtoSage expects a checkpoint named model.pt")
        BUNDLE = model_fn(str(checkpoint.parent))
    MODEL_HASH = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    MODEL_STATUS = (
        "Checkpoint loaded; research inference enabled. Clinical validation is not established."
    )


def inspect(image):
    if image is None:
        raise ValueError("Select an image for inspection")
    if image.width * image.height > 20_000_000:
        raise ValueError("Image exceeds 20 megapixels")
    rgb = image.convert("RGB")
    arr = np.asarray(rgb.resize((256, 256)), dtype=float) / 255
    gray = arr.mean(axis=2)
    result = {
        "width": image.width,
        "height": image.height,
        "mean_brightness": float(gray.mean()),
        "dark_pixel_fraction": float((gray < 0.05).mean()),
        "bright_pixel_fraction": float((gray > 0.95).mean()),
        "gradient_energy": float(
            np.mean(np.diff(gray, axis=0) ** 2) + np.mean(np.diff(gray, axis=1) ** 2)
        ),
        "scope": "descriptive image statistics; not a validated clinical image-quality score",
    }
    if BUNDLE is None:
        return result, {}, {"status": "awaiting_checkpoint", "message": MODEL_STATUS}
    if KIND == "vision":
        from otovision.inference import predict_image

        prediction = predict_image(*[BUNDLE[0], rgb, BUNDLE[1], BUNDLE[2], BUNDLE[3]])
    else:
        from ml.src.inference import predict_fn

        prediction = predict_fn(rgb, BUNDLE)
    prediction["checkpoint_sha256"] = MODEL_HASH
    return result, prediction["probabilities"], prediction
