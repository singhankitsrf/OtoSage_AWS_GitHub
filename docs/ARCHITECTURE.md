# Architecture Decisions

## ADR-001 — Direct-to-S3 image upload
The API returns a short-lived pre-signed PUT URL. Clients upload directly to S3, which prevents image payloads from being proxied through Lambda.

## ADR-002 — Event-driven inference
S3 ObjectCreated events invoke the submission Lambda. That function submits the S3 object to SageMaker Asynchronous Inference and records state in DynamoDB.

## ADR-003 — Managed asynchronous endpoint
The design favors queued image inference and cost-aware autoscaling rather than keeping an always-on service for bursty development workloads.

## ADR-004 — Explicit model governance
SageMaker Pipelines evaluates a trained model and applies configurable metric gates. Passing models are registered with PendingManualApproval rather than being automatically deployed.

## ADR-005 — Infrastructure lifecycle separated from model lifecycle
Terraform owns durable application infrastructure. Model deployment code runs only after a model version has been approved.
