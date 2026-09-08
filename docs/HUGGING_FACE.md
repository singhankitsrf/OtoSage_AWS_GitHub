# OtoSage AWS on Hugging Face

Target Space: `singhankit491/otosage-aws` (a deployment target, not a claim that it is live).

## Run locally

From the repository root:

```bash
pip install -r hf_space/requirements.txt
PYTHONPATH=.:src python hf_space/app.py
```

For image inference also install torch==2.6.0 and torchvision==0.21.0 from the PyTorch CPU wheel index.



## Build the exact deployment

```bash
pip install huggingface_hub==1.30.0
python scripts/publish_space.py --repo-id singhankit491/otosage-aws --stage-only /tmp/otosage-aws-space
docker build -t otosage-aws /tmp/otosage-aws-space
docker run --rm -p 7860:7860 otosage-aws
```

The staging command copies only tracked allowlisted source files. Commit intended changes first.
Patient data, local credentials and trained checkpoints are excluded.

## Publish

Authenticate securely with `hf auth login`, then run:

```bash
python scripts/publish_space.py --repo-id singhankit491/otosage-aws
```

Alternatively, configure a narrowly scoped Hugging Face write token as the GitHub Actions secret
`HF_TOKEN` and run the **Hugging Face Space** workflow. It builds and checks application startup before uploading.
No token belongs in source code, a README, a Docker build argument, or a chat message.
The workflow uses default CPU Space hardware and does not request paid GPU resources.

After publishing, wait for the Hugging Face build to finish, open the application, execute its example,
and verify the displayed output. Record the Space commit and the GitHub source revision.
The upload script reports current runtime state but does not mistake BUILDING for RUNNING.

## Scope

Local asynchronous image jobs with an AWS deployment reference. The AWS/Azure infrastructure remains in GitHub and requires its own account deployment.
This CPU demonstration is not evidence of clinical validation or a measured production cloud deployment.
