output "dataset_bucket" { value=aws_s3_bucket.dataset.id }
output "inference_bucket" { value=aws_s3_bucket.inference.id }
output "jobs_table" { value=aws_dynamodb_table.jobs.name }
output "api_url" { value=aws_apigatewayv2_api.http.api_endpoint }
output "sagemaker_role_arn" { value=aws_iam_role.sagemaker.arn }
output "success_topic_arn" { value=aws_sns_topic.inference_success.arn }
output "failure_topic_arn" { value=aws_sns_topic.inference_failure.arn }
output "github_actions_role_arn" { value=local.enable_github_oidc ? aws_iam_role.github_actions[0].arn : null }
