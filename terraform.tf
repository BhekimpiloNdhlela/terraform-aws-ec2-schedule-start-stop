terraform {
  required_version = ">= 1.4.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.72.1"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      "Environment"                 = var.environment
      "workload.owner"              = "n/a"
      "technical.environment"       = var.environment
      "technical.terraform.managed" = "true"
      "workload.project"            = "e-commerce-platform"
      "Name"                        = "MyResourceName"
      "Application"                 = "api-gateway"
      "Department"                  = "automation"
      "Purpose"                     = "analytics-pipeline"
      "Compliance"                  = "n/a"
      "Backup"                      = "false"
      "Lifecycle"                   = "active"
      "Criticality"                 = "high"
      "CreatedBy"                   = "terraform"
    }
  }
}
