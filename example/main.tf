module "terraform-aws-automate-ec2-start-stop" {
  source                     = "./../"
  environment                = var.environment
  error_email_footer         = var.error_email_footer
  error_email_header         = var.error_email_header
  error_email_subject        = var.error_email_subject
  ms_teams_reporting_enabled = var.ms_teams_reporting_enabled
  ms_teams_webhook_url       = var.ms_teams_webhook_url
  region                     = var.region
  success_email_footer       = var.success_email_footer
  success_email_header       = var.success_email_header
  success_email_subject      = var.success_email_subject
  naming_prefix              = var.naming_prefix
  notification_emails        = var.notification_emails
  start_expression           = var.start_expression
  stop_expression            = var.stop_expression
  schedule_auto_start_key    = var.schedule_auto_start_key
  schedule_auto_start_value  = var.schedule_auto_start_value
  schedule_auto_stop_key     = var.schedule_auto_stop_key
  schedule_auto_stop_value   = var.schedule_auto_stop_value
  lambda_memory_size         = var.lambda_memory_size
  lambda_timeout             = var.lambda_timeout
}
