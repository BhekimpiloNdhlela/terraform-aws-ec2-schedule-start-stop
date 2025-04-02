environment                = "prod"
naming_prefix              = "ec2-auto-start-stop"
region                     = "eu-west-1"
notification_emails        = ["bheki@cloudandthings.io"]
stop_expression            = "rate(2 minutes)"
start_expression           = "rate(1 day)"
ms_teams_reporting_enabled = true
ms_teams_webhook_url       = "https://cloudandthingsza.webhook.office.com/webhookb2/a98bb423-ddf6-4627-87c8-a0381fc7c6f9@d1516fb8-e664-4e2b-962e-f38e4315ac51/IncomingWebhook/e2f0d3becb0c49ed87c96cf8cc3a714f/249b7042-16ff-404b-995b-d4d28be54c77/V2i58YdipA3gTc0j0-23is7bmVYODHGJ_NALgvbZbYW9U1"
error_email_subject        = "Lambda Error Notification [EC2 Start/Stop]"
error_email_header         = "Hi 👋🏾,\nThe following error occurred while running the Lambda function:\n"
error_email_footer         = "Please check the AWS CloudWatch logs for more details.\nBest regards,\nFooBar Team"
success_email_subject      = "Lambda Success Notification [EC2 Start/Stop]"
success_email_header       = "Hi 👋🏾,\nThe Lambda function executed successfully, the following EC2 instance(s) were terminated:\n"
success_email_footer       = "Please review the AWS CloudWatch logs for detailed execution information.\nBest regards,\nFooBar Team"
schedule_auto_start_key    = "scheduled-auto-start"
schedule_auto_start_value  = "true"
schedule_auto_stop_key     = "scheduled-auto-stop"
schedule_auto_stop_value   = "true"