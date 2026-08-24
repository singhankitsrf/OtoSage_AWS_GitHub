locals {
  lambda_source = "${path.module}/../../app/lambdas"
}

data "archive_file" "create_upload" {
  type        = "zip"
  output_path = "${path.module}/.terraform/create_upload.zip"

  source {
    content  = file("${local.lambda_source}/create_upload.py")
    filename = "create_upload.py"
  }

  source {
    content  = file("${local.lambda_source}/common.py")
    filename = "common.py"
  }
}

data "archive_file" "get_job" {
  type        = "zip"
  output_path = "${path.module}/.terraform/get_job.zip"

  source {
    content  = file("${local.lambda_source}/get_job.py")
    filename = "get_job.py"
  }

  source {
    content  = file("${local.lambda_source}/common.py")
    filename = "common.py"
  }
}

data "archive_file" "submit_inference" {
  type        = "zip"
  output_path = "${path.module}/.terraform/submit_inference.zip"

  source {
    content  = file("${local.lambda_source}/submit_inference.py")
    filename = "submit_inference.py"
  }

  source {
    content  = file("${local.lambda_source}/common.py")
    filename = "common.py"
  }

  source {
    content  = file("${local.lambda_source}/job_utils.py")
    filename = "job_utils.py"
  }
}

data "archive_file" "complete_job" {
  type        = "zip"
  output_path = "${path.module}/.terraform/complete_job.zip"

  source {
    content  = file("${local.lambda_source}/complete_job.py")
    filename = "complete_job.py"
  }

  source {
    content  = file("${local.lambda_source}/common.py")
    filename = "common.py"
  }
}

resource "aws_lambda_function" "create_upload" {
  function_name    = "${var.project_name}-create-upload"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "create_upload.handler"
  filename         = data.archive_file.create_upload.output_path
  source_code_hash = data.archive_file.create_upload.output_base64sha256
  timeout          = 15

  environment {
    variables = {
      INFERENCE_BUCKET   = aws_s3_bucket.inference.id
      JOBS_TABLE         = aws_dynamodb_table.jobs.name
      UPLOAD_TTL_SECONDS = "900"
    }
  }
}

resource "aws_lambda_function" "get_job" {
  function_name    = "${var.project_name}-get-job"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "get_job.handler"
  filename         = data.archive_file.get_job.output_path
  source_code_hash = data.archive_file.get_job.output_base64sha256
  timeout          = 15

  environment {
    variables = {
      JOBS_TABLE             = aws_dynamodb_table.jobs.name
      RESULT_URL_TTL_SECONDS = "900"
    }
  }
}

resource "aws_lambda_function" "submit_inference" {
  function_name    = "${var.project_name}-submit-inference"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "submit_inference.handler"
  filename         = data.archive_file.submit_inference.output_path
  source_code_hash = data.archive_file.submit_inference.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      JOBS_TABLE              = aws_dynamodb_table.jobs.name
      SAGEMAKER_ENDPOINT_NAME = var.sagemaker_endpoint_name
    }
  }
}

resource "aws_lambda_function" "complete_job" {
  function_name    = "${var.project_name}-complete-job"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "complete_job.handler"
  filename         = data.archive_file.complete_job.output_path
  source_code_hash = data.archive_file.complete_job.output_base64sha256
  timeout          = 15

  environment {
    variables = {
      JOBS_TABLE = aws_dynamodb_table.jobs.name
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  for_each = {
    create_upload    = aws_lambda_function.create_upload.function_name
    get_job          = aws_lambda_function.get_job.function_name
    submit_inference = aws_lambda_function.submit_inference.function_name
    complete_job     = aws_lambda_function.complete_job.function_name
  }

  name              = "/aws/lambda/${each.value}"
  retention_in_days = var.log_retention_days
}
