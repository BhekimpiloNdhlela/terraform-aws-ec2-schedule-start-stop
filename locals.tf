# Define a map for EventBridge rules
locals {
  eventbridge_rules = {
    start = {
      name_suffix     = "start-ec2-instances"
      description     = "EventBridge rule to trigger Lambda function to start EC2 instances at 6 AM (Monday to Friday)"
      cron_expression = var.start_expression
      action          = "start" # Custom flag for action
    }
    stop = {
      name_suffix     = "stop-ec2-instances"
      description     = "EventBridge rule to trigger Lambda function to stop EC2 instances at 6 PM (Monday to Friday)"
      cron_expression = var.stop_expression
      action          = "stop" # Custom flag for action
    }
  }
}
