locals {
  lambda_function_name = var.project_name
  lambda_handler      = "lambda_function.lambda_handler"
  lambda_runtime      = "python3.9"
}

# Create Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/deployment.zip"
  excludes    = [
    "terraform",
    ".git",
    ".gitignore",
    "deploy.sh",
    "cleanup.sh",
    "README.md"
  ]
}

# Install dependencies
resource "null_resource" "install_dependencies" {
  triggers = {
    requirements = filemd5("${path.module}/src/requirements.txt")
    source_code  = filemd5("${path.module}/src/lambda_function.py")
  }

  provisioner "local-exec" {
    command = <<EOT
      cd ${path.module}/src && \
      pip install --target . -r requirements.txt && \
      rm -rf *.dist-info __pycache__
    EOT
  }
}

# SNS Topic
resource "aws_sns_topic" "cost_alert" {
  name = var.project_name
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.cost_alert.arn
  protocol  = "email"
  endpoint  = var.email_endpoint
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [aws_sns_topic.cost_alert.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "cost_alert" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = local.lambda_function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = local.lambda_handler
  runtime         = local.lambda_runtime
  timeout         = 30
  memory_size     = 128

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.cost_alert.arn
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    data.archive_file.lambda_zip,
    null_resource.install_dependencies
  ]
}

# CloudWatch Event Rule
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "${var.project_name}-daily-trigger"
  description         = "Triggers AWS Cost Alert Lambda function daily"
  schedule_expression = var.schedule_expression
}

# CloudWatch Event Target
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.cost_alert.arn
}

# Lambda Permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_alert.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}
