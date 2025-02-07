# Terraform Module: Automate EC2 Start/Stop with Notifications

This Terraform module automates the start and stop of specified EC2 instances on a defined schedule using AWS EventBridge and Lambda. Notifications are sent via Amazon SNS and optionally reported to Microsoft Teams.

## Features

- Automatically start and stop EC2 instances based on cron expressions.
- Send email notifications via SNS in case of errors.
- Optional reporting to Microsoft Teams via a webhook.
- Configurable for different environments (e.g., `dev`, `test`, `prod`).

---

## Architecture/Infrastructure
This solution leverages the following AWS services:

- **AWS SNS**  
  Simple Notification Service (SNS) is used to send emails to the specified email endpoints. SNS is responsible for reporting errors or notifying the success/failure of the start/stop process.

- **AWS EventBridge Rule (STOP)**  
  This rule is configured to trigger the Lambda function to stop the specified EC2 instances.

- **AWS EventBridge Rule (START)**  
  This rule is configured to trigger the Lambda function to start the specified EC2 instances.

- **AWS Lambda**  
  The Lambda function is used to start or stop the specified EC2 instances when triggered by an EventBridge rule, based on the defined cron expression.

- **AWS S3**  
  An S3 bucket is used to store an external module (`requests`), which is required for making POST requests to the Microsoft Teams Incoming Webhook endpoint.

- **AWS SSM Parameter Store**  
  The Microsoft Teams Incoming Webhook URL is securely stored in AWS Systems Manager (SSM) Parameter Store.


The following is the infrastructure diagram of the solution:


![Project Architecture](infra-documentation/infra-diagram.png "Architecture Overview")
---
## Usage

```hcl
module "automate_ec2_start_stop" {
  source = "github.com/BhekimpiloNdhlela/terraform-aws-ec2-schedule-start-stop.git"

  environment                = "prod"
  naming_prefix              = "my-app"
  region                     = "us-east-1"
  notification_emails        = ["foo@bar.com"]
  ec2_instance_ids           = ["i-0abcd1234efgh5678", "i-1234abcd5678efgh"]
  stop_cron_expression       = "0 18 * * 1-5" # 6:00 PM Monday-Friday
  start_cron_expression      = "0 6 * * 1-5"  # 6:00 AM Monday-Friday
  ms_teams_reporting_enabled = true
  ms_teams_webhook_url       = "https://example.webhook.office.com"
  error_email_subject        = "Lambda Error Notification"
  error_email_header         = "The following error occurred while running the Lambda function:"
  error_email_footer         = "Please check the AWS CloudWatch logs for more details."
  success_email_subject      = "Lambda Error Notification"
  success_email_header       = "The following error occurred while running the Lambda function:"
  success_email_footer       = "Please check the AWS CloudWatch logs for more details."
}
```

---

## Inputs

| Name                         | Type           | Default | Description                                                   |
| ---------------------------- | -------------- | ------- | ------------------------------------------------------------- |
| `environment`                | `string`       | `""`    | The environment for deployment (e.g., `dev`, `test`, `prod`). |
| `naming_prefix`              | `string`       | `""`    | Prefix for naming AWS resources.                              |
| `region`                     | `string`       | `""`    | AWS region for resource deployment.                           |
| `notification_emails`        | `list(string)` | `[]`    | List of email addresses to receive notifications.             |
| `ec2_instance_ids`           | `list(string)` | `[]`    | List of EC2 instance IDs to manage.                           |
| `stop_cron_expression`       | `string`       | `""`    | Cron expression for stopping EC2 instances.                   |
| `start_cron_expression`      | `string`       | `""`    | Cron expression for starting EC2 instances.                   |
| `ms_teams_reporting_enabled` | `bool`         | `true`  | Enable or disable MS Teams reporting.                         |
| `ms_teams_webhook_url`       | `string`       | `""`    | Microsoft Teams webhook URL for reporting.                    |
| `error_email_subject`        | `string`       | `""`    | Subject for error notification emails.                        |
| `error_email_header`         | `string`       | `""`    | Header for error notification emails.                         |
| `error_email_footer`         | `string`       | `""`    | Footer for error notification emails.                         |

---

## Outputs

| Name              | Description                              |
| ----------------- | ---------------------------------------- |
| `sns_topic_arn`   | ARN of the SNS topic for notifications.  |
| `lambda_function` | Name of the Lambda function.             |
| `cloudwatch_logs` | CloudWatch Log Group used by the Lambda. |

---

## Requirements

- Terraform 1.0+
- AWS Provider 4.0+
- IAM permissions to create Lambda, EC2, SNS, and CloudWatch resources.

---

## Deployment

1. Clone the repository:

   ```bash
   git clone https://github.com/BhekimpiloNdhlela/terraform-aws-ec2-schedule-start-stop.git
   cd automate-ec2-start-stop
   ```

2. Create a `terraform.tfvars` file with your configuration:

   ```hcl
   environment                = "prod"
   naming_prefix              = "my-app"
   region                     = "us-east-1"
   notification_emails        = ["foo@bar.com"]
   ec2_instance_ids           = ["i-0abcd1234efgh5678"]
   stop_cron_expression       = "0 18 * * 1-5"
   start_cron_expression      = "0 6 * * 1-5"
   ms_teams_reporting_enabled = true
   ms_teams_webhook_url       = "https://example.webhook.office.com"
   error_email_subject        = "Error Notification"
   error_email_header         = "An error occurred:"
   error_email_footer         = "Check CloudWatch Logs for details."
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

## Feature Request/TODO:
- convert to module for reusability
- JP has requested to use tags instead of a list of ec2 instance `auto-on` and `auto-off` inconjuction with the ec2 instance IDs list

## Author

This module is maintained by **Bheki Ndhlela**. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.