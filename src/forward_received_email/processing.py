"""Processing logic for SES notification events."""

import json
import logging
from typing import Any

import boto3

from forward_received_email.config import settings
from forward_received_email.utils import check_spam, tools

logger = logging.getLogger(__name__)


def main_handler(event: dict[str, Any]) -> None:
    """Process an SES SNS notification and forward the e-mail."""
    logger.info("Starting - processing received e-mail")

    records = event.get("Records", [])
    if not records:
        logger.warning("No SES records found in event payload.")
        return None

    ses_notification = records[0].get("Sns", {})
    message = json.loads(ses_notification["Message"])
    receipt = message["receipt"]
    sender = message["mail"]["source"]
    destination = message["mail"]["destination"][0]
    subject = message["mail"]["commonHeaders"].get("subject", "No subject")

    domain = tools.get_domain(destination)

    logger.info(
        "Starting - inbound-sns-spam-filter: %s",
        ses_notification.get("MessageId"),
    )
    check_spam.check_email_is_spam(
        ses_notification["MessageId"], receipt, sender, domain
    )

    action = receipt.get("action", {})
    if action.get("type") != "S3":
        logger.exception("Mail body is not saved to S3.")
        return None

    try:
        s3_client = boto3.resource(
            "s3", region_name=settings.AWS_DEFAULT_REGION
        )
        mail_obj = s3_client.Object(action["bucketName"], action["objectKey"])
        body = tools.decode_email(mail_obj.get()["Body"].read())
        tools.sed_email_to(
            ses_notification["MessageId"], domain, subject, body
        )
    except Exception as exc:  # pragma: no cover - logged for debugging
        logger.error(
            "An error occurred while processing the e-mail: %s",
            ses_notification.get("MessageId"),
        )
        raise exc

    return None
