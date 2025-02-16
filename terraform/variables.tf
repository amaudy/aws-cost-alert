variable "project_name" {
  description = "Name of the project, used for resource naming"
  type        = string
  default     = "aws-cost-alert"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "email_endpoint" {
  description = "Email address to receive cost alerts"
  type        = string
}

variable "schedule_expression" {
  description = "CloudWatch Events schedule expression"
  type        = string
  default     = "cron(0 13 * * ? *)"  # 20:00 Bangkok time
}
