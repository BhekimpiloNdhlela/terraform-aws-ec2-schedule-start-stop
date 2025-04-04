output "sns_topic_arn" {
  description = "ARN of the SNS topic for notifications."
  value       = aws_sns_topic.automate_ec2_start_stop.name
}

output "lambda_function" {
  description = "Name of the Lambda function."
  value       = aws_lambda_function.automate_ec2_start_stop.arn
}

output "cloudwatch_logs" {
  description = "CloudWatch Log Group used by the Lambda."
  value       = aws_cloudwatch_log_group.automate_ec2_start_stop.arn
}
