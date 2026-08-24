# Terraform Stack

This stack provisions the application-side cloud platform:

- private encrypted S3 dataset and inference buckets
- DynamoDB job-state table
- SNS completion/failure topics
- four Lambda functions
- API Gateway HTTP API
- S3 event-driven inference submission
- SageMaker execution role
- optional GitHub Actions OIDC provider/role
- bounded CloudWatch log retention

The SageMaker endpoint is deployed separately after an approved model version
exists in Model Registry.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

For a development teardown:

```bash
terraform destroy
```
