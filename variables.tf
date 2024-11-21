variable "environment" {
  type        = string
  description = "The environment in which resources are deployed (e.g., dev, test, prod)."

  validation {
    condition     = length(var.environment) > 0
    error_message = "The 'environment' variable must not be empty."
  }
}

variable "naming_prefix" {
  type        = string
  description = "The prefix used for naming AWS resources."

  validation {
    condition     = length(var.naming_prefix) > 0
    error_message = "The 'naming_prefix' variable must not be empty."
  }
}

variable "region" {
  type        = string
  description = "The AWS region to deploy resources."

  validation {
    condition     = length(var.region) > 0
    error_message = "The 'region' variable must not be empty."
  }
}

variable "notification_emails" {
  type        = list(string)
  description = "A list of email addresses to receive notifications."

  validation {
    condition     = length(var.notification_emails) > 0
    error_message = "The 'notification_emails' variable must contain at least one email address."
  }
}

variable "ec2_instance_ids" {
  type        = list(string)
  description = "A list of EC2 instance IDs to be managed."

  validation {
    condition     = length(var.ec2_instance_ids) > 0
    error_message = "The 'ec2_instance_ids' variable must contain at least one EC2 instance ID."
  }
}

variable "stop_expression" {
  type        = string
  description = "The cron expression for stopping EC2 instances."

  validation {
    condition     = length(var.stop_expression) > 0
    error_message = "The 'stop_cron_expression' variable must not be empty."
  }
}

variable "start_expression" {
  type        = string
  description = "The cron expression for starting EC2 instances."

  validation {
    condition     = length(var.start_expression) > 0
    error_message = "The 'start_cron_expression' variable must not be empty."
  }
}

variable "ms_teams_reporting_enabled" {
  type        = bool
  description = "Flag to enable or disable MS Teams reporting."

  validation {
    condition     = var.ms_teams_reporting_enabled == true || var.ms_teams_reporting_enabled == false
    error_message = "The 'ms_teams_reporting_enabled' variable must be either true or false."
  }
}

variable "ms_teams_webhook_url" {
  type        = string
  description = "The MS Teams webhook URL for reporting."

  validation {
    condition     = length(var.ms_teams_webhook_url) > 0
    error_message = "The 'ms_teams_webhook_url' variable must not be empty."
  }
}

variable "error_email_subject" {
  type        = string
  description = "The subject of error notification emails."

  validation {
    condition     = length(var.error_email_subject) > 0
    error_message = "The 'error_email_subject' variable must not be empty."
  }
}

variable "error_email_header" {
  type        = string
  description = "The header content of error notification emails."

  validation {
    condition     = length(var.error_email_header) > 0
    error_message = "The 'error_email_header' variable must not be empty."
  }
}

variable "error_email_footer" {
  type        = string
  description = "The footer content of error notification emails."

  validation {
    condition     = length(var.error_email_footer) > 0
    error_message = "The 'error_email_footer' variable must not be empty."
  }
}

variable "success_email_subject" {
  type        = string
  description = "The subject of success notification emails."

  validation {
    condition     = length(var.success_email_subject) > 0
    error_message = "The 'success_email_subject' variable must not be empty."
  }
}

variable "success_email_header" {
  type        = string
  description = "The header content of success notification emails."

  validation {
    condition     = length(var.success_email_header) > 0
    error_message = "The 'success_email_header' variable must not be empty."
  }
}

variable "success_email_footer" {
  type        = string
  description = "The footer content of success notification emails."

  validation {
    condition     = length(var.success_email_footer) > 0
    error_message = "The 'success_email_footer' variable must not be empty."
  }
}