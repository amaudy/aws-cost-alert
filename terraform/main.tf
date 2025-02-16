terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

module "lambda_cost_alert" {
  source = "./modules/lambda-cost-alert"

  project_name    = var.project_name
  aws_region      = var.aws_region
  email_endpoint  = var.email_endpoint
  schedule_expression = var.schedule_expression
}
