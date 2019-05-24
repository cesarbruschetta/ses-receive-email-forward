""" module to method from check spam email """
import re
import boto3
import logging
import json
from datetime import datetime

from forward_recieved_email import config
from forward_recieved_email.utils import tools


RE_DOMAIN = re.compile("\@(.*)$")
logger = logging.getLogger(__name__)


def check_email_is_spam(message_id: str, receipt: str, sender: str) -> None:
    """ Check if any spam check failed  """

    SPAMMER_DOMAINS = map(re.compile, tools.read_spammer_file("domains"))
    SPAMMER_EMAILS = map(re.compile, tools.read_spammer_file("emails"))
    sender_domain = (RE_DOMAIN.findall(sender) or [""])[0]

    if (
        receipt["spfVerdict"]["status"] == "FAIL"
        or receipt["dkimVerdict"]["status"] == "FAIL"
        or receipt["spamVerdict"]["status"] == "FAIL"
        or receipt["virusVerdict"]["status"] == "FAIL"
        or all(map(lambda x: x.search(sender_domain), SPAMMER_DOMAINS))
        or all(map(lambda x: x.search(sender), SPAMMER_EMAILS))
    ):

        send_bounce_params = {
            "OriginalMessageId": message_id,
            "BounceSender": "mailer-daemon@{}".format(config.EMAIL_DOMAIN),
            "MessageDsn": {
                "ReportingMta": "dns; {}".format(config.EMAIL_DOMAIN),
                "ArrivalDate": datetime.now().isoformat(),
            },
            "BouncedRecipientInfoList": [],
        }

        for recipient in receipt["recipients"]:
            send_bounce_params["BouncedRecipientInfoList"].append(
                {"Recipient": recipient, "BounceType": "ContentRejected"}
            )

        logger.info("Bouncing message with parameters:")
        logger.info(json.dumps(send_bounce_params))

        try:
            ses_client = boto3.client("ses")
            bounceResponse = ses_client.send_bounce(**send_bounce_params)
            logger.info(
                "Bounce for message %s sent, bounce message ID: %s",
                message_id,
                bounceResponse["MessageId"],
            )

            raise Exception("Bounce for message 'disposition': 'stop_rule_set'")
        except Exception as e:
            logger.error(
                "An error occurred while sending bounce for message: %s", message_id
            )
            logger.exception(e)
            raise e
    else:
        logger.info("Accepting message: %s", message_id)
