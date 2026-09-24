"""Utility functions for the e-mail forwarder."""

import logging
import os
import re
from email.parser import BytesParser

import boto3

from forward_received_email.config import BASE_PATH, settings

logger = logging.getLogger(__name__)

RE_DOMAIN = re.compile(r"@(.+)$")


def read_spammer_file(filename: str) -> list[str]:
    """Read spam domain or e-mail file data."""
    file_path = os.path.join(BASE_PATH, "spammer", f"{filename}.txt")
    with open(file_path, "r", encoding="utf-8") as file_pointer:
        return [
            line.strip() for line in file_pointer.readlines() if line.strip()
        ]


def decode_email(msg_str: bytes) -> str:
    """Decode a raw SES message into plain text."""
    message = BytesParser().parsebytes(msg_str)
    decoded_message = ""
    for part in message.walk():
        if part.get_content_type() != "text/plain":
            continue
        charset = part.get_content_charset() or "utf-8"
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        decoded_message += payload.decode(  # type: ignore
            charset, errors="replace"
        )
    return decoded_message


def get_domain(email: str) -> str:
    """Return the domain part from an e-mail address."""
    return (RE_DOMAIN.findall(email) or [""])[0]


def sed_email_to(message_id: str, domain: str, subject: str, body: str):
    """Send the e-mail to the configured forwarding addresses."""
    ses_client = boto3.client("ses", region_name=settings.AWS_DEFAULT_REGION)
    try:
        response = ses_client.send_email(
            Source=settings.FROM_ADDRESS % domain,
            Destination={"ToAddresses": settings.FORWARD_ADDRESSES},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": body},
                    "Html": {"Data": body.replace("\n", "<br />")},
                },
            },
        )
        return response
    except Exception as exc:  # pragma: no cover - real AWS call path
        logger.error(
            "An error occurred while sending the forwarded message: %s",
            message_id,
        )
        raise exc
