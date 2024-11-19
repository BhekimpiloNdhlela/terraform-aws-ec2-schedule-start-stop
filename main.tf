provider "aws" {
  region = "us-east-1"  # Adjust to your preferred AWS region
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_policy" "lambda_policy" {
  name = "lambda_execution_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:DescribeInstances"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "sns:Publish"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

# Attach the Policy to the Role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# SNS Topic for Notifications
resource "aws_sns_topic" "sns_topic" {
  name = "ec2_notification_topic"
}

# Lambda Function
resource "aws_lambda_function" "ec2_manager_lambda" {
  function_name = "ec2_manager"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  filename      = "path/to/your/deployment/package.zip"  # Update with the path to your deployment package

  environment {
    variables = {
      SNS_TOPIC_ARN     = aws_sns_topic.sns_topic.arn
      EC2_INSTANCE_ID   = "your-ec2-instance-id"  # Update with your EC2 instance ID
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy_attachment]
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.ec2_manager_lambda.function_name}"
  retention_in_days = 7  # Adjust retention as needed
}

# EventBridge Rule for Starting EC2 Instance
resource "aws_cloudwatch_event_rule" "start_rule" {
  name                = "start_ec2_rule"
  schedule_expression = "cron(0 8 * * ? *)"  # Update with your desired cron schedule
}

# EventBridge Rule for Stopping EC2 Instance
resource "aws_cloudwatch_event_rule" "stop_rule" {
  name                = "stop_ec2_rule"
  schedule_expression = "cron(0 20 * * ? *)"  # Update with your desired cron schedule
}

# EventBridge Targets
resource "aws_cloudwatch_event_target" "start_target" {
  rule = aws_cloudwatch_event_rule.start_rule.name
  arn  = aws_lambda_function.ec2_manager_lambda.arn
}

resource "aws_cloudwatch_event_target" "stop_target" {
  rule = aws_cloudwatch_event_rule.stop_rule.name
  arn  = aws_lambda_function.ec2_manager_lambda.arn
}

# Lambda Permissions for EventBridge
resource "aws_lambda_permission" "allow_eventbridge_start" {
  statement_id  = "AllowExecutionFromEventBridgeStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_manager_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_rule.arn
}

resource "aws_lambda_permission" "allow_eventbridge_stop" {
  statement_id  = "AllowExecutionFromEventBridgeStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_manager_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.stop_rule.arn
}

# SNS Topic Subscription for Email Notifications
resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.sns_topic.arn
  protocol  = "email"
  endpoint  = "your-email@example.com"  # Update with your email address
}
