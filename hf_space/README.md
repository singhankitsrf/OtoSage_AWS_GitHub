---
title: OtoSage AWS
emoji: ☁️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: true
license: mit
short_description: AWS medical AI platform demo with safe model provenance
tags:
- aws
- sagemaker
- mlops
- computer-vision
- healthcare-ai
- terraform
- model-registry
- ci-cd
- responsible-ai
- gradio
---

# OtoSage AWS — End-to-End AI Platform Deployment Project

**Author:** Ankit Kumar Singh  
**Positioning:** AWS AI Platform • SageMaker • MLOps • Computer Vision • IaC • CI/CD • Responsible AI  
**Live runtime:** Hugging Face Docker Space  
**Source repository:** https://github.com/singhankitsrf/OtoSage_AWS_GitHub

OtoSage is a recruiter-facing **end-to-end AWS medical-AI platform engineering project**. It connects model-development controls with a reference event-driven cloud architecture built around SageMaker Pipelines, Model Registry, asynchronous inference, S3, Lambda, API Gateway, DynamoDB, SNS, CloudWatch, Terraform, and GitHub Actions OIDC.

> **Evidence boundary:** The public Hugging Face Space runs a local research workbench and does **not** claim that the AWS infrastructure has been deployed in a live account. The original five-class dataset and genuine trained checkpoint are not bundled, so disease-performance metrics remain unclaimed until a real run is available.

## What this project demonstrates

- production-style AWS AI/ML platform architecture
- SageMaker training/pipeline and model-registry design
- asynchronous inference pattern for image jobs
- S3-based object/event flow
- Lambda/API Gateway orchestration interfaces
- DynamoDB job-state design
- SNS notification pattern
- CloudWatch observability interfaces
- Terraform infrastructure-as-code
- GitHub Actions OIDC deployment design
- model-quality gates and manual approval boundary
- SHA-256 data deduplication / cross-label protection
- calibration-aware evaluation contract
- checkpoint provenance and safe model-readiness behavior
- Hugging Face Docker deployment for recruiter-accessible demonstration

## End-to-end cloud architecture

```text
Client / image submission
        ↓
API Gateway
        ↓
Lambda orchestration
        ↓
S3 input object
        ↓
SageMaker asynchronous inference
        ↓
Model Registry / approved model boundary
        ↓
S3 inference output
        ↓
DynamoDB job state
        ↓
SNS notification / result retrieval
        ↓
CloudWatch logs + metrics
```

## ML release flow

```text
Dataset ingestion
        ↓
SHA-256 duplicate / cross-label checks
        ↓
Deterministic preprocessing
        ↓
Model training pipeline
        ↓
Evaluation
  ├─ accuracy / balanced accuracy
  ├─ macro-F1
  ├─ ROC-AUC
  ├─ ECE
  └─ Brier score
        ↓
Quality gate
        ↓
Model Registry
        ↓
Manual approval boundary
        ↓
Asynchronous inference deployment
```

## Current live evidence status

| Evidence | Status |
|---|---|
| Hugging Face image-quality workbench | Implemented |
| Docker runtime | Implemented |
| Checkpoint provenance | Implemented |
| AWS architecture/IaC source | Available in GitHub |
| SageMaker training execution in this environment | Not claimed |
| Live AWS endpoint deployment | Not claimed |
| Five-class checkpoint in this Space | Not configured |
| Disease-classification accuracy | Not claimed |
| Clinical validation | Not established |

The live Space uses Gradio's local queue for demonstration. It deliberately does not present the local queue as if it were an AWS asynchronous endpoint.

## Reproducibility and governance design

A promoted model is expected to be traceable through:

- dataset/deduplication evidence
- deterministic split/preprocessing configuration
- evaluation outputs
- quality-gate decision
- model artifact hash
- Model Registry version
- approval state
- source Git revision
- deployment configuration

This separation between **validated model evidence**, **approval**, and **deployment** is the core platform-engineering signal of the project.

## Infrastructure-as-code and security posture

The repository models infrastructure through Terraform and uses the GitHub Actions OIDC pattern to avoid embedding long-lived AWS credentials in source control. Cloud account execution, cost, autoscaling behavior, and service quotas must be verified separately in an authorized AWS environment.

## Hugging Face deployment role

The public Space is intentionally a **portfolio runtime**, not a substitute for the AWS backend. It exposes:

- permitted image upload
- image-quality statistics
- model-readiness status
- optional real checkpoint inference
- checkpoint provenance
- evidence-status disclosure

This makes the cloud project clickable without falsifying cloud-execution claims.

## CI/CD release controls

```text
Pull request / deployment change
        ↓
Stage tracked Space files
        ↓
Build exact Docker image
        ↓
Container startup test
        ↓
HTTP smoke test
        ↓
Publish validated Space to Hugging Face
```

## Engineering decisions

**Why asynchronous inference?**  
Image workloads can be bursty and may exceed synchronous request windows. The architecture separates submission, processing, job state, and result retrieval.

**Why Model Registry + manual approval?**  
A deployable artifact should be distinguishable from an approved production candidate. The approval boundary supports governance and rollback discipline.

**Why not claim AWS deployment here?**  
Architecture and code are not the same as account-level execution evidence. This project keeps those claims separate so the portfolio remains technically credible.

## Responsible-use statement

OtoSage is a **medical-AI platform engineering demonstration**. Clinical use would require approved datasets, external validation, patient-level controls, clinical oversight, security/governance review, monitoring, and applicable regulatory/organizational approval.

## Explore the implementation

- **GitHub source:** https://github.com/singhankitsrf/OtoSage_AWS_GitHub
- **Evaluation status:** https://github.com/singhankitsrf/OtoSage_AWS_GitHub/blob/main/evaluation/status.json
- **Hugging Face Space:** https://huggingface.co/spaces/singhankit491/otosage-aws

### Portfolio signal

This project demonstrates **AI Lead / AI Platform Architect** capability across cloud architecture, ML lifecycle governance, model-registry controls, asynchronous serving, infrastructure-as-code, CI/CD, observability, responsible AI, and evidence-backed deployment communication.