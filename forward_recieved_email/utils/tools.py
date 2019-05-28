""" module to utils method """
import boto3
import logging
import os
import re

from typing import List, Dict
from email.parser import BytesParser
from datetime import datetime

from forward_recieved_email.config import settings, BASE_PATH

logger = logging.getLogger(__name__)


RE_DOMAIN = re.compile("\@(.*)$")


def read_spammer_file(filename: str) -> List[str]:
    """read file spam domain or email"""

    file_path = os.path.join(BASE_PATH, "spammer", "%s.txt" % filename)
    with open(file_path, "r") as fp:
        return [l.strip() for l in fp.readlines()]


def decode_email(msg_str: bytes) -> str:
    """ decode msg string to object """

    p = BytesParser()
    message = p.parsebytes(msg_str)
    decoded_message = ""
    for part in message.walk():
        charset = part.get_content_charset()
        if part.get_content_type() == "text/plain":
            part_str = part.get_payload(decode=1)
            decoded_message += part_str.decode(charset)
    return decoded_message


def get_domain(email):
    """ return domain to email """
    return (RE_DOMAIN.findall(email) or [""])[0]


def sed_email_to(message_id: str, domain: str, subject: str, body: str) -> Dict:
    """ Send email to forward addresse """

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

    except Exception as e1:
        logger.error(
            "An error occurred while sending bounce for message: %s", message_id
        )
        raise e1
