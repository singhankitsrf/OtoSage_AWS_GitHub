# OtoSage AWS — Project Charter

**Owner:** Ankit Kumar Singh  
**Portfolio role:** AI Platform Architect / AWS ML Engineer / AI Lead  
**Project type:** AWS-native healthcare AI platform reference architecture

## Product objective

Demonstrate an event-driven ML platform on AWS that links data ingestion, leakage-aware preprocessing, SageMaker training/evaluation, governed model promotion, asynchronous inference, job tracking, observability, infrastructure-as-code, and CI/CD.

## Current delivered scope

- SageMaker Processing/Training/Pipeline design
- Model Registry quality-gate and manual-approval pattern
- asynchronous inference architecture
- S3, Lambda, API Gateway, DynamoDB and SNS integration code
- CloudWatch observability pattern
- SHA-256 data-integrity controls
- EfficientNetV2-S training/evaluation code
- Terraform infrastructure definitions
- GitHub Actions/OIDC deployment pattern
- Hugging Face portfolio runtime with explicit AWS/non-AWS boundary

## Delivery roadmap

### Phase 1 — Platform architecture — COMPLETE
- [x] end-to-end AWS service design
- [x] ML lifecycle code
- [x] async inference/job-state workflow
- [x] Terraform IaC
- [x] CI and deployment workflow pattern
- [x] responsible-use and evidence boundaries

### Phase 2 — Executed AWS evidence — NEXT
- [ ] Deploy Terraform in an owned AWS account
- [ ] Run SageMaker Processing and Training jobs
- [ ] Execute evaluation and model-quality gate
- [ ] Register an approved model version in SageMaker Model Registry
- [ ] Deploy and invoke an asynchronous endpoint
- [ ] Capture CloudWatch, job-state and cost evidence

### Phase 3 — Platform hardening
- [ ] Add least-privilege IAM review and policy tests
- [ ] Add blue/green or canary model-release strategy
- [ ] Add autoscaling/queue-pressure measurements
- [ ] Add failure injection and recovery tests
- [ ] Publish measured latency/cost/SLO data only after execution

## Success criteria

1. Infrastructure can be reproduced from Terraform without manual drift.
2. Model promotion is blocked when engineering gates fail.
3. Endpoint/job lifecycle is observable end-to-end.
4. No cloud-deployment or clinical-validation claim is made without committed execution evidence.

## Risks and controls

| Risk | Control |
|---|---|
| AWS configuration drift | Terraform + CI validation |
| Unsafe model promotion | evaluation gate + manual registry approval |
| Long-running inference | asynchronous endpoint architecture |
| Unsupported cloud claims | executed-evidence-only documentation |

## Recruiter signal

AWS · SageMaker · Model Registry · Async Inference · Terraform · Serverless · Event-Driven Architecture · MLOps · CI/CD · Healthcare AI
