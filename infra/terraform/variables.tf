variable "project_name" {
  type    = string
  default = "otosage-aws"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "sagemaker_endpoint_name" {
  type    = string
  default = "otosage-aws-async"
}

variable "github_org" {
  type        = string
  default     = ""
  description = "GitHub organization or username. Leave blank to skip OIDC role creation."
}

variable "github_repo" {
  type        = string
  default     = ""
  description = "GitHub repository. Leave blank to skip OIDC role creation."
}

variable "log_retention_days" {
  type    = number
  default = 30
}
