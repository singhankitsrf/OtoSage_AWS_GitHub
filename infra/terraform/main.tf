provider "aws" { region=var.aws_region default_tags { tags={Project=var.project_name,ManagedBy="Terraform",Portfolio="HealthcareAI"} } }
data "aws_caller_identity" "current" {}
resource "aws_s3_bucket" "dataset" { bucket_prefix="${var.project_name}-dataset-" }
resource "aws_s3_bucket_versioning" "dataset" { bucket=aws_s3_bucket.dataset.id versioning_configuration { status="Enabled" } }
resource "aws_s3_bucket_server_side_encryption_configuration" "dataset" { bucket=aws_s3_bucket.dataset.id rule { apply_server_side_encryption_by_default { sse_algorithm="AES256" } } }
resource "aws_s3_bucket_public_access_block" "dataset" { bucket=aws_s3_bucket.dataset.id block_public_acls=true block_public_policy=true ignore_public_acls=true restrict_public_buckets=true }
resource "aws_s3_bucket" "inference" { bucket_prefix="${var.project_name}-inference-" }
resource "aws_s3_bucket_server_side_encryption_configuration" "inference" { bucket=aws_s3_bucket.inference.id rule { apply_server_side_encryption_by_default { sse_algorithm="AES256" } } }
resource "aws_s3_bucket_public_access_block" "inference" { bucket=aws_s3_bucket.inference.id block_public_acls=true block_public_policy=true ignore_public_acls=true restrict_public_buckets=true }
resource "aws_s3_bucket_lifecycle_configuration" "inference" { bucket=aws_s3_bucket.inference.id rule { id="expire-inference-artifacts" status="Enabled" filter {} expiration { days=30 } } }
resource "aws_dynamodb_table" "jobs" { name="${var.project_name}-jobs" billing_mode="PAY_PER_REQUEST" hash_key="job_id" attribute { name="job_id" type="S" } point_in_time_recovery { enabled=true } }
resource "aws_sns_topic" "inference_success" { name="${var.project_name}-inference-success" }
resource "aws_sns_topic" "inference_failure" { name="${var.project_name}-inference-failure" }
