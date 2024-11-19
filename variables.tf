variable "environment" {
  type        = string
  default     = ""
  description = "value"  
}

variable "naming_prefix" {
    type = string
    default = ""
    description = ""
}

variable "region" {
  type        = string
  default     = ""
  description = "value"
}

variable "teams_webhook_url" {
  type        = string
  default     = ""
  description = "value"

}

variable "email_address_to" {
  type        = list(string)
  default     = ["value"]
  description = "value"
}

variable "ec2_instance_ids" {
    type        = list(string)
  default     = []
  description = "value"
}

variable "stop_cron_expression" {
  type        = string
  default     = ""
  description = "value"
}


variable "start_cron_expression" {
  type        = string
  default     = ""
  description = "value"
}

variable "enable_ms_teams_reporting" {
    type = bool
    default = true
    description = "value"
}

variable "ms_teams_incomming_webhook_url" {
  type = string
  default = ""https://cloudandthingsza.webhook.office.com/webhookb2/a98bb423-ddf6-4627-87c8-a0381fc7c6f9@d1516fb8-e664-4e2b-962e-f38e4315ac51/IncomingWebhook/e2f0d3becb0c49ed87c96cf8cc3a714f/249b7042-16ff-404b-995b-d4d28be54c77/V2i58YdipA3gTc0j0-23is7bmVYODHGJ_NALgvbZbYW9U1""
  description = "value"
}