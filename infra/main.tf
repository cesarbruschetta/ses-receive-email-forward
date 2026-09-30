data "aws_caller_identity" "current" {}

resource "aws_sns_topic" "email" {
  name =  "${var.project_name}-sns-topic"
}

resource "aws_sns_topic_policy" "email" {
  arn    = aws_sns_topic.email.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

resource "aws_sns_topic_subscription" "lambda" {
  topic_arn = aws_sns_topic.email.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.mail_forwarder.arn
}