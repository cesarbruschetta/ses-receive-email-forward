""" module to utils method """
import boto3
import logging
import json
from typing import Dict

from email.parser import Parser
from datetime import datetime

from forward_recieved_email.utils import tools, check_spam


logger = logging.getLogger(__name__)


def main_handler(event: Dict) -> None:

    logger.info("Starting - processing forward recieved E-mail")

    ses_notification = event["Records"][0]["Sns"]
    message_id = ses_notification["MessageId"]
    message = json.loads(ses_notification["Message"])
    receipt = message["receipt"]
    sender = message["mail"]["source"]
    destination = message["mail"]["destination"][0]
    subject = message["mail"]["commonHeaders"]["subject"]

    domain = tools.get_domain(destination)

    # Check if any spam check failed
    logger.info("Starting - inbound-sns-spam-filter: %s", message_id)
    check_spam.check_email_is_spam(message_id, receipt, sender, domain)

    # now distribute to list:
    action = receipt["action"]
    if action["type"] != "S3":
        logger.exception("Mail body is not saved to S3. Or I have done sth wrong.")
        return None

    try:
        s3_client = boto3.resource("s3")
        mail_obj = s3_client.Object(action["bucketName"], action["objectKey"])
        body = tools.decode_email(mail_obj.get()["Body"].read())
        tools.sed_email_to(message_id, domain, subject, body)

    except Exception as e2:
        logger.error(
            "An error occurred while sending bounce for message: %s", message_id
        )
        raise e2

    return None
