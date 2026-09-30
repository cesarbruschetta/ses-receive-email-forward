terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket  = "prod-726337636269-project-tfstate"
    key     = "ses-email-forwarder/terraform.tfstate"
    region  = "us-east-1"
    encrypt = "true"


  }
}

provider "aws" {
  region = var.aws_region
}
