# ---------------------------------------------------------------------------------------------------------------------
# CREATE THE LAMBDA FUNCTION
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_lambda_function" "event_handler" {
  function_name = var.name
  role          = aws_iam_role.lambda.arn

  filename         = data.archive_file.source_code.output_path
  source_code_hash = data.archive_file.source_code.output_base64sha256

  runtime = var.runtime
  handler = var.handler

  memory_size = var.memory_size
  timeout     = var.timeout

  environment {
    variables = var.environment_variables
  }

  # https://stackoverflow.com/a/59954373/3899136
  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.cw_lambda_group,
  ]
}

# ---------------------------------------------------------------------------------------------------------------------
# LOGGING THROUGH CLOUD WATCH
# ---------------------------------------------------------------------------------------------------------------------

# Know more at: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function#cloudwatch-logging-and-permissions

resource "aws_cloudwatch_log_group" "cw_lambda_group" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = 1
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "custom-lambda-${var.name}"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# CREATE A DEPLOYMENT PACKAGE FOR THE LAMBDA FUNCTION BY ZIPPING UP THE SOURCE CODE
# ---------------------------------------------------------------------------------------------------------------------

data "archive_file" "source_code" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/deployment-package.zip"
}

# ---------------------------------------------------------------------------------------------------------------------
# CREATE AN IAM ROLE FOR THE LAMBDA FUNCTION
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "lambda" {
  name               = var.name
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

data "aws_iam_policy_document" "lambda_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
