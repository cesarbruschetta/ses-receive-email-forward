variable "aws_region" {
  description = "AWS region for the SES forwarding stack."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base name used for the AWS resources."
  type        = string
  default     = "ses-email-forwarder"
}

variable "ses_recipient_addresses" {
  description = "Email addresses or domains handled by the SES receipt rule."
  type        = list(string)
}

variable "forward_addresses" {
  description = "Email addresses that receive the forwarded mail."
  type        = list(string)
}

variable "from_address" {
  description = "Sender used when the Lambda resends the message through SES."
  type        = string
  default     = "AWS Forward <no-reply@%s>"
}

variable "logger_level" {
  description = "Logging level used by the Lambda runtime."
  type        = string
  default     = "INFO"
}

variable "lambda_image_tag" {
  description = "Container image tag for the Lambda function."
  type        = string
  default     = "latest"
}
