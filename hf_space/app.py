from __future__ import annotations
import json
import time
from pathlib import Path
import gradio as gr
from hf_space import backend

backend.load_model()


def run(image):
    if image is None:
        raise gr.Error("Select an image first. Use only images you are permitted to process.")
    started = time.perf_counter()
    quality, probabilities, prediction = backend.inspect(image)
    prediction["processing_seconds"] = round(time.perf_counter() - started, 4)
    return quality, probabilities, prediction


with gr.Blocks(title="OtoSage AWS | Ankit Kumar Singh", delete_cache=(300, 300)) as demo:
    gr.Markdown(
        "# OtoSage AWS\n### Inspect queued image jobs locally; retain the AWS deployment architecture in GitHub.\nBuilt by **Ankit Kumar Singh** · [GitHub source](https://github.com/singhankitsrf/OtoSage_AWS_GitHub)"
    )
    gr.Markdown(
        "**Research demonstration.** No autonomous diagnosis or treatment advice. Use de-identified, permitted images only. Gradio temporarily caches uploaded images; the application schedules cache cleanup and does not maintain a patient database."
    )
    gr.Markdown("**Model status:** " + backend.MODEL_STATUS)
    with gr.Tab("Image workbench"):
        image = gr.Image(type="pil", label="Permitted image", sources=["upload"])
        button = gr.Button("Inspect image", variant="primary")
        quality = gr.JSON(label="Image statistics")
        probabilities = gr.Label(label="Class probabilities — available only with trained weights")
        prediction = gr.JSON(label="Inference status and checkpoint provenance")
        button.click(
            run,
            image,
            [quality, probabilities, prediction],
            api_name="inspect",
            concurrency_limit=1,
        )
    with gr.Tab("Evaluation and deployment"):
        gr.Markdown(
            "The five-class dataset and trained weights are not included. This Space reports image statistics until the owner configures a real checkpoint. It never substitutes random predictions or manuscript numbers.\n\nSet MODEL_PATH locally, or configure HF_MODEL_REPO and a full immutable HF_MODEL_REVISION in Space settings. A private model also needs a read-scoped HF_TOKEN secret.\n\nThe repository retains its original training/evaluation pipeline. Publish saved prediction arrays, split provenance and checkpoint hashes from an actual run before making model-performance claims."
        )
        gr.JSON(
            json.loads(
                (Path(__file__).resolve().parents[1] / "evaluation/status.json").read_text()
            ),
            label="Evidence status",
        )
        gr.Markdown(
            "Requests here use Gradio’s local queue. This is not an AWS S3/SageMaker/DynamoDB deployment. AWS jobs, approval, autoscaling and cost require separate account verification."
        )


if __name__ == "__main__":
    demo.queue(max_size=12, default_concurrency_limit=1).launch(
        server_name="0.0.0.0", server_port=7860, share=False, show_error=False, max_file_size="10mb"
    )
