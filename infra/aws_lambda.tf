locals {
  lambda_image_uri = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_name}:${var.lambda_image_tag}"
}

resource "aws_lambda_function" "mail_forwarder" {
  function_name = "${var.project_name}-lambda"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = local.lambda_image_uri
  timeout       = 60
  memory_size   = 512
  architectures = ["x86_64"]

  environment {
    variables = {
      FORWARD_ADDRESSES = join(",", var.forward_addresses)
      FROM_ADDRESS      = var.from_address
      LOGGER_LEVEL      = var.logger_level
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.mail_forwarder.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_permission" "sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mail_forwarder.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.email.arn
}

