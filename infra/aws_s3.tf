resource "aws_s3_bucket" "mail" {
  bucket        = "${var.project_name}-mail-receipts"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "mail" {
  bucket = aws_s3_bucket.mail.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "mail" {
  bucket = aws_s3_bucket.mail.id
  policy = data.aws_iam_policy_document.ses_bucket_policy.json
}