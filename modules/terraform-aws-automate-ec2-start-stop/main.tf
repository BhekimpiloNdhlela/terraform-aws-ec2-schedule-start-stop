# IAM role for Lambda function
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.naming_prefix}-lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

# Attach the policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}

# Reference the Lambda role in the Lambda function resource
resource "aws_lambda_function" "automate_ec2_start_stop" {
  function_name = "${var.naming_prefix}-lambda-function"
  filename      = data.archive_file.automate_ec2_start_stop.output_path
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "index.handler"
  runtime       = "python3.10"
  timeout       = 180
  memory_size   = 256

  source_code_hash = data.archive_file.automate_ec2_start_stop.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.automate_ec2_start_stop]
  layers           = [aws_lambda_layer_version.automate_ec2_start_stop.arn]

  environment {
    variables = {
      SNS_TOPIC_ARN                 = aws_sns_topic.automate_ec2_start_stop.arn
      ERROR_EMAIL_SUBJECT           = var.error_email_subject
      ERROR_EMAIL_HEADER            = var.error_email_header
      ERROR_EMAIL_FOOTER            = var.error_email_footer
      SUCCESS_EMAIL_SUBJECT         = var.success_email_subject
      SUCCESS_EMAIL_FOOTER          = var.success_email_footer
      SUCCESS_EMAIL_HEADER          = var.success_email_header
      MS_TEAMS_REPORTING_ENABLED    = var.ms_teams_reporting_enabled
      MS_TEAMS_WEBHOOK_URL          = var.ms_teams_webhook_url
      EC2_SCHEDULE_AUTO_START_VALUE = var.schedule_auto_start_value
      EC2_SCHEDULE_AUTO_STOP_VALUE  = var.schedule_auto_stop_value
      EC2_SCHEDULE_AUTO_START_KEY   = var.schedule_auto_start_key
      EC2_SCHEDULE_AUTO_STOP_KEY    = var.schedule_auto_stop_key
    }
  }

  lifecycle {
    ignore_changes = [tags, tags_all]
  }
}

resource "aws_lambda_layer_version" "automate_ec2_start_stop" {
  filename            = "${path.module}/layer/requests.zip"
  layer_name          = "${var.naming_prefix}-requests"
  description         = "The requests library for Lambda function to make HTTP requests to MS Teams webhook."
  compatible_runtimes = ["python3.10"]
}

# Grant EventBridge permission to invoke the Lambda function
resource "aws_lambda_permission" "eventbridge_invoke" {
  for_each = local.eventbridge_rules

  statement_id  = "${var.naming_prefix}-${each.value.name_suffix}-permission"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.automate_ec2_start_stop.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_schedule[each.key].arn
}

# CloudWatch log group for the Lambda function
resource "aws_cloudwatch_log_group" "automate_ec2_start_stop" {
  name              = "/aws/lambda/${var.naming_prefix}-logging"
  retention_in_days = 7

  lifecycle {
    prevent_destroy = false
  }
}

# Create an SNS topic to send error notifications
resource "aws_sns_topic" "automate_ec2_start_stop" {
  name = "${var.naming_prefix}-topic"
}

# Create SNS subscriptions for error notifications
resource "aws_sns_topic_subscription" "email_subscription" {
  for_each = toset(var.notification_emails)

  topic_arn              = aws_sns_topic.automate_ec2_start_stop.arn
  protocol               = "email"
  endpoint_auto_confirms = true
  endpoint               = each.value
}

# Create EventBridge rules
resource "aws_cloudwatch_event_rule" "ec2_schedule" {
  for_each = local.eventbridge_rules

  name                = "${var.naming_prefix}-${each.value.name_suffix}-eventbridge-rule"
  description         = each.value.description
  schedule_expression = each.value.cron_expression
}

# Create EventBridge targets for the Lambda function
resource "aws_cloudwatch_event_target" "ec2_schedule" {
  for_each = local.eventbridge_rules

  rule      = aws_cloudwatch_event_rule.ec2_schedule[each.key].name
  target_id = "${var.naming_prefix}-${each.value.name_suffix}-eventbridge-target"
  arn       = aws_lambda_function.automate_ec2_start_stop.arn

  # Pass a custom input to identify the source of the trigger
  input = jsonencode({
    source      = each.key
    action      = each.value.action
    description = each.value.description
  })
}
