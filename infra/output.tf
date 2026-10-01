output "s3_bucket_name" {
  value = aws_s3_bucket.mail.bucket
}

output "sns_topic_arn" {
  value = aws_sns_topic.email.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.mail_forwarder.function_name
}
