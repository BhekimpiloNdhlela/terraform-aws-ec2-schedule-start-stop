# Terraform Module: Automated EC2 Start/Stop with Notifications

This Terraform module automates the scheduled start and stop of EC2 instances using AWS EventBridge and Lambda. It also integrates notifications via Amazon SNS and optionally Microsoft Teams.

## Features

- **Automated EC2 Start/Stop**: Schedule EC2 instance start and stop based on cron or rate expressions.
- **Tag-based Instance Selection**: Target instances based on specific tags.
- **Notification System**:
  - Send email notifications via Amazon SNS for success and failure cases.
  - Optional Microsoft Teams notifications via a webhook.
- **Multi-Environment Support**: Works across `dev`, `test`, and `prod` environments.
- **Secure Webhook Storage**: Microsoft Teams webhook URLs are securely stored in AWS SSM Parameter Store.

## Architecture Overview

This solution utilizes the following AWS services:

- **AWS SNS**: Sends email notifications for success and failures.
- **AWS EventBridge Rules**:
  - **Stop Rule**: Triggers Lambda to stop EC2 instances at a scheduled time.
  - **Start Rule**: Triggers Lambda to start EC2 instances at a scheduled time.
- **AWS Lambda**: Executes EC2 start/stop operations when triggered by EventBridge.
- **AWS S3**: Stores external dependencies (e.g., `requests` module for Teams webhook calls).
- **AWS SSM Parameter Store**: Securely manages Microsoft Teams webhook URLs.

### Infrastructure Diagram

![Project Architecture](./infra-documentation/infra-diagram.png "Architecture Overview")

---

## Folder Structure
```
.
├── example
│   ├── main.tf                  # Example usage of the module
│   ├── terraform.tf             # Terraform configuration file
│   └── variables.tf             # Variables for the example
├── infra-documentation
│   └── infra-diagram.png        # Architecture diagram
├── modules
│   └── terraform-aws-automate-ec2-start-stop
│       ├── lambda
│       │   └── automate-ec2-start-stop.py  # Python script for Lambda function
│       ├── README.md         # Documentation for the module
│       ├── data.tf           # Data sources
│       ├── iam.tf            # IAM role and policies
│       ├── locals.tf         # Local variables
│       ├── main.tf           # Main module configuration
│       ├── outputs.tf        # Outputs from the module
│       ├── variables.tf      # Input variables for the module
│       └── versions.tf       # Required Terraform and provider versions
├── LICENSE                # License file
└── README.md              # Project documentation
```

## Usage

```hcl
module "ec2_scheduler" {
  source = "github.com/BhekimpiloNdhlela/terraform-aws-ec2-schedule-start-stop.git"

  environment                = "prod"
  naming_prefix              = "ec2-auto-start-stop"
  region                     = "eu-west-1"
  notification_emails        = ["foo@bar.com"]
  stop_expression            = "rate(2 minutes)"
  start_expression           = "rate(1 day)"
  ms_teams_reporting_enabled = false
  ms_teams_webhook_url       = "https://foobar.webhook.office.com/..."
  error_email_subject        = "EC2 Scheduler Error Notification"
  error_email_header         = "Hi 👋🏾,\nAn error occurred while executing the EC2 scheduler Lambda:\n"
  error_email_footer         = "Please check AWS CloudWatch logs for details.\nBest,\nFooBar Team"
  success_email_subject      = "EC2 Scheduler Success Notification"
  success_email_header       = "Hi 👋🏾,\nThe EC2 scheduler Lambda executed successfully. Instances affected:\n"
  success_email_footer       = "Check AWS CloudWatch logs for execution details.\nBest,\nFooBar Team"
  schedule_auto_start_key    = "scheduled-auto-start"
  schedule_auto_start_value  = "true"
  schedule_auto_stop_key     = "scheduled-auto-stop"
  schedule_auto_stop_value   = "true"
}
```

---

## Inputs

| Name                         | Type           | Default | Description                                             |
| ---------------------------- | -------------- | ------- | ------------------------------------------------------- |
| `environment`                | `string`       | `""`    | Deployment environment (`dev`, `test`, `prod`).        |
| `naming_prefix`              | `string`       | `""`    | Prefix for AWS resource names.                         |
| `region`                     | `string`       | `""`    | AWS region for deployment.                             |
| `notification_emails`        | `list(string)` | `[]`    | Email recipients for notifications.                    |
| `stop_expression`            | `string`       | `""`    | Schedule for stopping EC2 instances.                   |
| `start_expression`           | `string`       | `""`    | Schedule for starting EC2 instances.                   |
| `ms_teams_reporting_enabled` | `bool`         | `false` | Enable/disable Microsoft Teams reporting.              |
| `ms_teams_webhook_url`       | `string`       | `""`    | Microsoft Teams webhook URL.                           |
| `error_email_subject`        | `string`       | `""`    | Subject for error notification emails.                 |
| `error_email_header`         | `string`       | `""`    | Header for error notification emails.                  |
| `error_email_footer`         | `string`       | `""`    | Footer for error notification emails.                  |
| `success_email_subject`      | `string`       | `""`    | Subject for success notification emails.               |
| `success_email_header`       | `string`       | `""`    | Header for success notification emails.                |
| `success_email_footer`       | `string`       | `""`    | Footer for success notification emails.                |
| `schedule_auto_start_key`    | `string`       | `""`    | Tag key for identifying auto-start instances.          |
| `schedule_auto_start_value`  | `string`       | `""`    | Tag value for identifying auto-start instances.        |
| `schedule_auto_stop_key`     | `string`       | `""`    | Tag key for identifying auto-stop instances.           |
| `schedule_auto_stop_value`   | `string`       | `""`    | Tag value for identifying auto-stop instances.         |

---

## Outputs

| Name              | Description                                |
| ----------------- | ------------------------------------------ |
| `sns_topic_arn`   | ARN of the SNS topic for notifications.    |
| `lambda_function` | Name of the Lambda function.               |
| `cloudwatch_logs` | CloudWatch Log Group for Lambda logging.   |

---

## Requirements

- Terraform 1.0+
- AWS Provider 4.0+
- IAM permissions for EC2, Lambda, SNS, and CloudWatch.

---

## Deployment Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/BhekimpiloNdhlela/terraform-aws-ec2-schedule-start-stop.git
   cd terraform-aws-ec2-schedule-start-stop
   ```

2. Create a `terraform.tfvars` file with your configuration:

   ```hcl
    environment                = "prod"
    naming_prefix              = "ec2-auto-start-stop"
    region                     = "eu-west-1"
    notification_emails        = ["foo@bar.com"]
    stop_expression            = "rate(2 minutes)"
    start_expression           = "rate(1 day)"
    ms_teams_reporting_enabled = false
    ms_teams_webhook_url       = "https://foobar.webhook.office.com/webhookb2/..."
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
   ```

3. Initialize Terraform:

   ```bash
   terraform init
   ```

4. Plan and apply:

   ```bash
   terraform plan
   terraform apply
   ```

---

## Author

Maintained by **Bheki Ndhlela**. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

