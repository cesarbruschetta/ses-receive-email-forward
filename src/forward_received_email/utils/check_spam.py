"""Spam and security checks for incoming SES mail."""

import json
import logging
from datetime import datetime

import boto3

from forward_received_email.config import settings
from forward_received_email.utils import tools

logger = logging.getLogger(__name__)


def check_email_is_spam(
    message_id: str, receipt: dict, sender: str, domain: str
) -> None:
    """Reject messages that fail spam or sender checks."""
    blocked_emails = {
        entry.lower() for entry in tools.read_spammer_file("emails")
    }
    sender_email = sender.lower()

    is_spam = (
        receipt.get("spfVerdict", {}).get("status") == "FAIL"
        or receipt.get("dkimVerdict", {}).get("status") == "FAIL"
        or receipt.get("spamVerdict", {}).get("status") == "FAIL"
        or receipt.get("virusVerdict", {}).get("status") == "FAIL"
        or sender_email in blocked_emails
    )

    if not is_spam:
        logger.info("Accepting message: %s", message_id)
        return

    send_bounce_params = {
        "OriginalMessageId": message_id,
        "BounceSender": "mailer-daemon@" + domain,
        "MessageDsn": {
            "ReportingMta": "dns; " + domain,
            "ArrivalDate": datetime.now().isoformat(),
        },
        "BouncedRecipientInfoList": [
            {"Recipient": recipient, "BounceType": "ContentRejected"}
            for recipient in receipt.get("recipients", [])
        ],
    }

    logger.info("Bouncing message with parameters:")
    logger.info(json.dumps(send_bounce_params))

    try:
        ses_client = boto3.client(
            "ses", region_name=settings.AWS_DEFAULT_REGION
        )
        bounce_response = ses_client.send_bounce(**send_bounce_params)
        logger.info(
            "Bounce for message %s sent, bounce message ID: %s",
            message_id,
            bounce_response["MessageId"],
        )
        raise Exception("Bounce for message 'disposition': 'stop_rule_set'")
    except Exception as exc:
        logger.error(
            "An error occurred while sending bounce for message: %s",
            message_id,
        )
        raise exc
