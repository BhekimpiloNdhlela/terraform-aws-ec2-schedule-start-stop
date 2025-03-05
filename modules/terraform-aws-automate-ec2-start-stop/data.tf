data "aws_caller_identity" "current" {}

# Data for Lambda assume role policy
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# Archive the Lambda function code into a zip file
data "archive_file" "automate_ec2_start_stop" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/automate-ec2-start-stop"
  output_path = "${path.module}/builds/lambda/automate-ec2-start-stop.zip"
}
