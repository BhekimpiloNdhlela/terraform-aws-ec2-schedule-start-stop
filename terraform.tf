provider "aws" {
  region = var.region

  default_tags {
    tags = {
      "Environment"                 = var.environment
      "workload.owner"              = "n/a"
      "technical.environment"       = var.environment
      "technical.terraform.managed" = "true"
      "workload.project"            = "n/a"
      "Name"                        = "EC2StartStopAutomation"
      "Application"                 = "automate-ec2-start-stop"
      "Department"                  = "automation"
      "Purpose"                     = "compute-cost-optimization"
      "Compliance"                  = "n/a"
      "Backup"                      = "false"
      "Lifecycle"                   = "active"
      "Criticality"                 = "high"
      "CreatedBy"                   = "terraform"
    }
  }
}
