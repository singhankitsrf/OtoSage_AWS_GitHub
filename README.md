# OtoSage-AWS

### AWS-Native Event-Driven Healthcare AI Platform for Otoscopic Image Analysis

**Amazon SageMaker Pipelines • Model Registry • Asynchronous Inference • S3 • Lambda • API Gateway • DynamoDB • SNS • CloudWatch • Terraform • GitHub Actions OIDC**

> **Research and engineering portfolio project — not a medical device and not intended for autonomous clinical diagnosis or treatment.**

---

## Why this repository exists

Most medical-image GitHub projects stop at a notebook and an accuracy score.

**OtoSage-AWS is deliberately different.** It demonstrates how an AI engineer or
cloud/ML architect can take a medical-vision workload through the complete AWS
lifecycle:

**data ingestion → data quality → managed training → model evaluation → model
governance → cloud deployment → event-driven inference → observability → CI/CD**

The repository is designed as a flagship portfolio project for roles such as:

- Senior AI / ML Engineer
- Healthcare AI Engineer
- AWS AI / ML Architect
- MLOps Engineer / Architect
- Applied AI Scientist
- AI Platform Engineer
- Cloud AI Technical Lead

---

## Dataset

The project design is based on a supplied archive of **3,000 otoscopic images**
covering five classes:

| Class | Images |
|---|---:|
| Acute Otitis Media | 600 |
| Cerumen Impaction | 600 |
| Chronic Otitis Media | 600 |
| Myringosclerosis | 600 |
| Normal | 600 |
| **Total** | **3,000** |

### Data-integrity finding

An archive-level audit found **78 repeated-content groups**, representing a
duplicate surplus of 78 files. The project therefore does **not** perform a naïve
random split.

The SageMaker preprocessing job:

1. verifies image readability;
2. computes SHA-256;
3. detects exact duplicates;
4. hard-fails if the same exact image appears under different labels;
5. keeps one canonical exact duplicate;
6. creates deterministic stratified train/validation/test splits.

See [`docs/DATASET_AUDIT.md`](docs/DATASET_AUDIT.md).

---

# Architecture

```mermaid
flowchart TB

    subgraph ML["Managed ML Lifecycle"]
        RAW[(Private S3 Dataset)]
        PREP[SageMaker Processing<br/>QA + SHA-256 dedupe + split]
        TRAIN[SageMaker Training<br/>EfficientNetV2-S]
        EVAL[SageMaker Processing<br/>F1 + AUC + ECE + Brier]
        GATE{Quality Gate}
        REG[SageMaker Model Registry<br/>Pending Manual Approval]

        RAW --> PREP --> TRAIN --> EVAL --> GATE --> REG
    end

    subgraph APP["Event-Driven Inference"]
        USER[Client]
        API[API Gateway HTTP API]
        UPL[Lambda<br/>Create Pre-signed Upload]
        S3IN[(S3 incoming/)]
        SUB[Lambda<br/>Submit Async Inference]
        SM[SageMaker Async Endpoint]
        S3OUT[(S3 results/)]
        SNS[SNS Success / Failure]
        DONE[Lambda<br/>Complete Job]
        DDB[(DynamoDB Job State)]
        GET[Lambda<br/>Get Job]

        USER -->|POST /upload| API --> UPL
        UPL --> DDB
        UPL -->|pre-signed URL| USER
        USER -->|direct image PUT| S3IN
        S3IN --> SUB --> SM
        SM --> S3OUT
        SM --> SNS --> DONE --> DDB
        USER -->|GET /jobs/{job_id}| API --> GET --> DDB
        GET -->|pre-signed result URL| USER
    end

    REG -. approved version .-> SM
```

---

# What this project demonstrates

| Capability | Implementation |
|---|---|
| Cloud architecture | AWS event-driven inference platform |
| Medical-image data QA | integrity checks + SHA-256 leakage prevention |
| Managed ML | SageMaker Processing and Training |
| MLOps | SageMaker Pipelines |
| Governance | Model Registry + manual approval |
| Evaluation | accuracy, balanced accuracy, macro F1, AUC, ECE, Brier |
| Uncertainty | confidence + normalized entropy |
| Human oversight | review recommendation for uncertain predictions |
| Serverless API | API Gateway + Lambda |
| Secure upload | expiring S3 pre-signed PUT URL |
| Async serving | SageMaker Asynchronous Inference |
| State management | DynamoDB |
| Event notifications | SNS |
| Cost control | async endpoint autoscaling + scale-to-zero design |
| Infrastructure-as-Code | Terraform |
| CI/CD | GitHub Actions |
| Credential security | AWS/GitHub OIDC pattern |
| Observability | CloudWatch logs + dashboard template |
| Responsible AI | model card, security notes, no fabricated metrics |

---

# Repository structure

```text
otosage-aws-platform/
│
├── app/
│   └── lambdas/
│       ├── create_upload.py
│       ├── submit_inference.py
│       ├── complete_job.py
│       ├── get_job.py
│       ├── job_utils.py
│       └── common.py
│
├── ml/
│   ├── pipeline/
│   │   └── build_pipeline.py
│   └── src/
│       ├── preprocess.py
│       ├── train.py
│       ├── evaluate.py
│       └── inference.py
│
├── deployment/
│   ├── deploy_async_endpoint.py
│   └── configure_autoscaling.py
│
├── infra/
│   └── terraform/
│       ├── main.tf
│       ├── iam.tf
│       ├── lambda.tf
│       ├── api.tf
│       ├── events.tf
│       ├── github_oidc.tf
│       └── ...
│
├── scripts/
│   ├── upload_dataset.py
│   ├── create_pipeline.py
│   └── invoke_demo.py
│
├── observability/
├── tests/
├── docs/
├── data/
├── .github/workflows/
├── DEPLOYMENT_CHECKLIST.md
└── pyproject.toml
```

---

# ML workflow

## 1. SageMaker Processing

The preprocessing job operates on the private S3 dataset and produces:

```text
processed/
├── train/
├── val/
└── test/
```

It also writes:

- `manifest.csv`
- `data_quality.json`

The pipeline explicitly prevents exact duplicate leakage.

## 2. SageMaker Training

Default model:

**EfficientNetV2-S transfer learning**

Training includes:

- ImageNet initialization
- augmentation
- AdamW
- cosine annealing
- label smoothing
- automatic mixed precision on CUDA
- early stopping
- macro-F1 checkpoint selection

## 3. Evaluation

The managed evaluation step generates:

- accuracy
- balanced accuracy
- macro F1
- multiclass ROC-AUC
- expected calibration error
- multiclass Brier score
- class-level precision / recall / F1

## 4. Model quality gate

Example engineering thresholds:

```text
Macro F1 >= 0.80
ECE <= 0.15
```

These are **pipeline parameters**, not claimed experimental results.

A model that passes the technical gate is registered as:

```text
PendingManualApproval
```

An engineer must review and approve it before deployment.

---

# AWS serving workflow

## Step 1 — Request an upload URL

```http
POST /upload
```

Request:

```json
{
  "content_type": "image/jpeg"
}
```

Response:

```json
{
  "job_id": "uuid",
  "upload_url": "https://...",
  "object_key": "incoming/uuid.jpg",
  "expires_in_seconds": 900
}
```

## Step 2 — Upload directly to S3

The client uploads the image using the returned pre-signed URL.

The image does not need to pass through the Lambda/API body.

## Step 3 — Automatic inference submission

An S3 `ObjectCreated` event invokes `submit_inference`.

The Lambda invokes:

```text
SageMaker InvokeEndpointAsync
```

and stores the job state in DynamoDB.

## Step 4 — Completion event

SageMaker writes the inference result to S3 and sends a success/failure
notification to SNS.

SNS invokes the completion Lambda, which updates DynamoDB.

## Step 5 — Retrieve job status

```http
GET /jobs/{job_id}
```

A completed job returns an expiring pre-signed result URL.

---

# Quick start

## Prerequisites

Install:

- Python 3.11+
- Git
- AWS CLI v2
- Terraform 1.6+
- AWS account

Verify your AWS identity:

```bash
aws sts get-caller-identity
```

---

## Install Python dependencies

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install --upgrade pip
pip install -e ".[dev,aws]"
```

Tests:

```bash
pytest -q
ruff check .
```

---

# Deploy the AWS infrastructure

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit the file.

Then:

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Important Terraform outputs:

```bash
terraform output
```

You will receive values for:

- dataset S3 bucket
- inference S3 bucket
- API URL
- DynamoDB table
- SageMaker execution role
- SNS topics
- GitHub OIDC role when enabled

---

# Upload the dataset to AWS

Keep the original 3,000 medical images outside Git.

Extract the dataset locally:

```text
Otoscopic_Data/
├── Acute Otitis Media/
├── Cerumen Impaction/
├── Chronic Otitis Media/
├── Myringosclerosis/
└── Normal/
```

Upload:

```bash
python scripts/upload_dataset.py \
  --data-root "/path/to/Otoscopic_Data" \
  --bucket YOUR_DATASET_BUCKET \
  --prefix raw/
```

---

# Create the SageMaker Pipeline

Linux/macOS:

```bash
export AWS_REGION=us-east-1
export DATA_BUCKET=YOUR_DATASET_BUCKET
export SAGEMAKER_ROLE_ARN=YOUR_SAGEMAKER_ROLE_ARN
export MODEL_PACKAGE_GROUP=otosage-aws-models

python scripts/create_pipeline.py
```

PowerShell:

```powershell
$env:AWS_REGION="us-east-1"
$env:DATA_BUCKET="YOUR_DATASET_BUCKET"
$env:SAGEMAKER_ROLE_ARN="YOUR_SAGEMAKER_ROLE_ARN"
$env:MODEL_PACKAGE_GROUP="otosage-aws-models"

python scripts/create_pipeline.py
```

Start it:

```bash
aws sagemaker start-pipeline-execution \
  --pipeline-name otosage-aws-training-pipeline
```

---

# Approve the model

After a real run:

1. open Amazon SageMaker;
2. inspect the pipeline execution;
3. inspect the evaluation JSON;
4. open Model Registry;
5. review the model version;
6. change the selected version from `PendingManualApproval` to `Approved`.

Do not approve a model solely because it crossed an arbitrary technical metric.

---

# Deploy asynchronous inference

```bash
python deployment/deploy_async_endpoint.py \
  --model-package-group otosage-aws-models \
  --endpoint-name otosage-aws-async \
  --output-s3 s3://YOUR_INFERENCE_BUCKET/results/ \
  --success-topic-arn YOUR_SUCCESS_TOPIC_ARN \
  --failure-topic-arn YOUR_FAILURE_TOPIC_ARN \
  --role-arn YOUR_SAGEMAKER_ROLE_ARN
```

Configure autoscaling:

```bash
python deployment/configure_autoscaling.py \
  --endpoint-name otosage-aws-async \
  --variant-name AllTraffic \
  --min-capacity 0 \
  --max-capacity 4 \
  --target-backlog-per-instance 2
```

---

# Test the complete cloud workflow

Use the included client:

```bash
python scripts/invoke_demo.py \
  --api-url YOUR_API_URL \
  --image example.jpg
```

The script:

1. requests an upload URL;
2. uploads the image directly to S3;
3. polls job status;
4. prints the completed result metadata.

---

# GitHub Actions + AWS OIDC

The repository includes:

```text
.github/workflows/ci.yml
.github/workflows/deploy-infra.yml
```

The deployment workflow expects:

Repository secret:

```text
AWS_GITHUB_ROLE_ARN
```

Repository variable:

```text
AWS_REGION
```

The intent is to use short-lived federated credentials rather than storing a
permanent AWS access key in GitHub.

---

# Security

The baseline stack includes:

- private S3 buckets
- public-access blocking
- server-side encryption
- short-lived pre-signed URLs
- IAM execution roles
- DynamoDB point-in-time recovery
- GitHub OIDC pattern
- no medical images in Git
- no model weights in Git
- no credentials in Git

See [`docs/SECURITY.md`](docs/SECURITY.md).

---

# Cost-aware architecture

The serving layer uses **SageMaker Asynchronous Inference** because it is well
suited to queued, bursty image inference and can be configured to scale down to
zero.

Other controls include:

- S3 inference-object expiration
- DynamoDB on-demand billing
- bounded CloudWatch log retention
- parameterized training instances
- Terraform teardown

See [`docs/COST_CONTROLS.md`](docs/COST_CONTROLS.md).

---

# What to show recruiters after your first AWS run

Add real evidence to the repository:

1. SageMaker Pipeline DAG screenshot
2. Model Registry version screenshot
3. actual data-quality report
4. actual evaluation metrics
5. actual API response
6. CloudWatch dashboard screenshot
7. measured end-to-end inference time
8. small cost breakdown for one training/demo run

Never invent model or infrastructure performance.

---

# Recruiter-ready project summary

> **OtoSage-AWS** is an AWS-native Healthcare AI platform that operationalizes
> otoscopic image classification through SageMaker Pipelines, governed Model
> Registry promotion, and event-driven asynchronous inference. The serving
> architecture uses API Gateway, Lambda, S3, DynamoDB and SNS, while Terraform
> and GitHub Actions OIDC provide reproducible infrastructure and secure CI/CD.

---

# Strong interview statement

> “I wanted the portfolio project to demonstrate more than computer vision.
> I treated the otoscopic model as one component of a governed AWS AI platform.
> The design includes leakage-aware data preparation, managed training,
> calibration-aware evaluation, explicit model approval, secure asynchronous
> inference, event-driven job tracking, infrastructure-as-code and federated
> CI/CD.”

---

## Responsible use

This repository is an engineering/research portfolio implementation.

It is **not** evidence that the trained model is clinically validated, regulated,
safe for autonomous diagnosis, or suitable for treatment decisions.

---

## Author

**Ankit Kumar Singh**

Healthcare AI • AWS • SageMaker • Applied AI • Medical Imaging • MLOps • Cloud Architecture

