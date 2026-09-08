---
title: OtoSage AWS
emoji: ☁️
colorFrom: orange
colorTo: blue
sdk: static
app_file: index.html
pinned: true
license: mit
short_description: AWS healthcare AI architecture and deployment evidence
tags:
- aws
- sagemaker
- mlops
- healthcare-ai
- terraform
- model-registry
- async-inference
- responsible-ai
- ci-cd
---

# OtoSage AWS — End-to-End Cloud AI Deployment Project

**Author:** Ankit Kumar Singh  
**Positioning:** AWS AI Platform Architecture • SageMaker • MLOps • Terraform • CI/CD • Responsible AI

OtoSage is an event-driven healthcare AI platform design for otoscopic image analysis. The public Hugging Face Space is a free client-side evidence and architecture workbench; the GitHub repository retains the backend implementation and AWS infrastructure design.

> **Evidence boundary:** No AWS account resources are contacted by this public Space. A genuine five-class trained checkpoint is not configured here, and AWS endpoint latency/cost/availability are not claimed as executed evidence.

## End-to-end architecture

```text
Image/request
→ input QA
→ S3 event / API boundary
→ SageMaker Pipeline
→ evaluation + quality gate
→ Model Registry
→ approval boundary
→ Async Inference endpoint
→ Lambda/API Gateway
→ DynamoDB/SNS
→ CloudWatch
→ Terraform + GitHub Actions OIDC
```

## What is demonstrated

- event-driven AWS architecture
- SageMaker Pipelines and Model Registry release design
- asynchronous inference pattern
- model-quality gates and approval controls
- checkpoint/model provenance interfaces
- infrastructure-as-code with Terraform
- GitHub Actions/OIDC deployment design
- image QA workbench in the public Space
- explicit separation of architecture evidence from unexecuted cloud claims

## Current evidence status

| Evidence | Status |
|---|---|
| Browser-side image QA | Live |
| Docker application | CI validated |
| AWS architecture and IaC | In GitHub |
| Model registry/quality-gate code | In GitHub |
| Actual SageMaker training job | Not claimed |
| Live AWS endpoint | Not claimed |
| Cloud latency/cost evidence | Not established |
| Clinical validation | Not established |

- GitHub: https://github.com/singhankitsrf/OtoSage_AWS_GitHub
- Space: https://huggingface.co/spaces/singhankit491/otosage-aws
