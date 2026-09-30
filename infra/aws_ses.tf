resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "${var.project_name}-rule-set"
}

resource "aws_ses_active_receipt_rule_set" "main" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
}

resource "aws_ses_receipt_rule" "main" {
  name          = "${var.project_name}-rule"
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
  enabled       = true
  scan_enabled  = true
  recipients    = var.ses_recipient_addresses

  s3_action {
    bucket_name       = aws_s3_bucket.mail.bucket
    object_key_prefix = "mail/"
    position          = 1
  }

  sns_action {
    topic_arn = aws_sns_topic.email.arn
    position  = 2
  }
}