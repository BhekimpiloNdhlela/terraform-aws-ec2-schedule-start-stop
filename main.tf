# IAM role for Lambda function
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.naming_prefix}-lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

# IAM policy for Lambda to allow necessary actions
resource "aws_iam_policy" "lambda_execution_policy" {
  name        = "${var.naming_prefix}-lambda-execution-policy"
  description = "IAM policy for Lambda function to manage EC2, SNS, and CloudWatch Logs"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow managing EC2 instances
      {
        Effect   = "Allow"
        Action   = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:DescribeInstances"
        ]
        Resource = "*"
      },
      # Allow publishing to SNS
      {
        Effect   = "Allow"
        Action   = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.automate_ec2_start_stop.arn
      },
      # Allow writing logs to CloudWatch Logs
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.naming_prefix}-automate-ec2-start-stop:*"
      }
    ]
  })
}

# Attach the policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}

# Data for Lambda assume role policy
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Reference the Lambda role in the Lambda function resource
resource "aws_lambda_function" "automate_ec2_start_stop" {
  function_name = "${var.naming_prefix}-automate-ec2-start-stop"
  filename      = data.archive_file.automate_ec2_start_stop.output_path
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "index.handler"
  runtime       = "python3.10"
  timeout       = 180
  memory_size   = 256

  source_code_hash = data.archive_file.automate_ec2_start_stop.output_base64sha256

  depends_on = [aws_cloudwatch_log_group.automate_ec2_start_stop]

  environment {
    variables = {
      SNS_TOPIC_ARN              = aws_sns_topic.automate_ec2_start_stop.arn
      ERROR_EMAIL_SUBJECT        = var.error_email_subject
      ERROR_EMAIL_HEADER         = var.error_email_header
      ERROR_EMAIL_FOOTER         = var.error_email_footer
      EC2_INSTANCE_IDS           = var.ec2_instance_ids
      STOP_CRON_EXPRESSION       = var.stop_cron_expression
      START_CRON_EXPRESSION      = var.start_cron_expression
      MS_TEAMS_REPORTING_ENABLED = var.ms_teams_reporting_enabled
      MS_TEAMS_WEBHOOK_URL       = var.ms_teams_webhook_url
    }
  }

  lifecycle {
    ignore_changes = [tags, tags_all]
  }
}


# Archive the Lambda function code into a zip file
data "archive_file" "automate_ec2_start_stop" {
  type        = "zip"
  source_dir  = "${path.module}/automate-ec2-start-stop"
  output_path = "${path.module}/builds/automate-ec2-start-stop.zip"
}

# CloudWatch log group for the Lambda function
resource "aws_cloudwatch_log_group" "automate_ec2_start_stop" {
  name              = "/aws/lambda/${var.naming_prefix}-automate-ec2-start-stop"
  retention_in_days = 7

  lifecycle {
    prevent_destroy = false
  }
}

# Create an SNS topic that will be used to send error emails in case
# there is an issue with the process.
resource "aws_sns_topic" "automate_ec2_start_stop" {
  name = "${var.naming_prefix}-automate-ec2-start-stop"
}

# Create SNS subscribers that will subscribe to the SNS topic
resource "aws_sns_topic_subscription" "email_subscription" {
  for_each               = toset(var.notification_emails)
  topic_arn              = aws_sns_topic.automate_ec2_start_stop.arn
  protocol               = "email"
  endpoint_auto_confirms = true
  endpoint               = each.value
}

# EventBridge rule to trigger the Lambda function to START EC2 instances at 6 AM
resource "aws_cloudwatch_event_rule" "start_ec2_instances" {
  name                = "${var.naming_prefix}-start-ec2-instances"
  description         = "EventBridge rule to trigger Lambda function to start EC2 instances at 6 AM (Monday to Friday)"
  schedule_expression = "cron(0 6 ? * 2-6 *)" # 6 AM Monday to Friday
}

# EventBridge rule target for starting EC2 instances
resource "aws_cloudwatch_event_target" "start_ec2_instances" {
  rule      = aws_cloudwatch_event_rule.start_ec2_instances.name
  target_id = "${var.naming_prefix}-start-ec2-instances"
  arn       = aws_lambda_function.automate_ec2_start_stop.arn
}

# EventBridge rule to trigger the Lambda function to STOP EC2 instances at 6 PM
resource "aws_cloudwatch_event_rule" "stop_ec2_instances" {
  name                = "${var.naming_prefix}-stop-ec2-instances"
  description         = "EventBridge rule to trigger Lambda function to stop EC2 instances at 6 PM (Monday to Friday)"
  schedule_expression = "cron(0 18 ? * 2-6 *)" # 6 PM Monday to Friday
}

# EventBridge rule target for stopping EC2 instances
resource "aws_cloudwatch_event_target" "stop_ec2_instances" {
  rule      = aws_cloudwatch_event_rule.stop_ec2_instances.name
  target_id = "${var.naming_prefix}-stop-ec2-instances"
  arn       = aws_lambda_function.automate_ec2_start_stop.arn
}
