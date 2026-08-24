resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.submit_inference.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.inference.arn
}

resource "aws_s3_bucket_notification" "inference" {
  bucket = aws_s3_bucket.inference.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.submit_inference.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_sns_topic_subscription" "success" {
  topic_arn = aws_sns_topic.inference_success.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.complete_job.arn
}

resource "aws_sns_topic_subscription" "failure" {
  topic_arn = aws_sns_topic.inference_failure.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.complete_job.arn
}

resource "aws_lambda_permission" "allow_sns_success" {
  statement_id  = "AllowSNSSuccessInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.complete_job.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.inference_success.arn
}

resource "aws_lambda_permission" "allow_sns_failure" {
  statement_id  = "AllowSNSFailureInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.complete_job.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.inference_failure.arn
}
