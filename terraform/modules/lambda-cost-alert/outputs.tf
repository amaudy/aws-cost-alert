output "lambda_function_name" {
  description = "Name of the created Lambda function"
  value       = aws_lambda_function.cost_alert.function_name
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.cost_alert.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
}
