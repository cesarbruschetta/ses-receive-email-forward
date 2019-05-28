""" module to test utils methods """
import os
import unittest
import boto3
from botocore.parsers import ResponseParserError
from moto import mock_ses
from unittest.mock import patch

from forward_recieved_email.utils import tools, check_spam
from . import SAMPLES_PATH


class TestUtilsTools(unittest.TestCase):
    """ test to utils.tools  """

    def test_read_spammer_file(self):
        """ method read_spammer_file """

        result = tools.read_spammer_file("domains")
        self.assertIn("0costofivf.com", result)

    def test_decode_email(self):
        """ method decode_email """

        with open(os.path.join(SAMPLES_PATH, "email.txt"), "rb") as fp:
            file_msg = fp.read()
        text = tools.decode_email(file_msg)
        self.assertIn("Cesar Augusto Bruschetta", text)

    @mock_ses
    def test_sed_email_to(self):
        """ method sed_email_to """
        conn = boto3.client("ses", region_name="us-east-1")
        conn.verify_email_identity(EmailAddress="no-reply@helpec.com.br")

        result = tools.sed_email_to(
            "123456789", "helpec.com.br", "ASSUNTO", "MENSAGEM TEXTO"
        )

    @mock_ses
    def test_sed_email_to_error(self):
        """ method sed_email_to with error """
        conn = boto3.client("ses", region_name="us-east-1")
        conn.verify_email_identity(EmailAddress="no-reply@test.com.br")

        arg = (
            "123456789", "helpec.com.br", "ASSUNTO", "MENSAGEM TEXTO"
        )
        self.assertRaises(
            ResponseParserError, tools.sed_email_to, *arg
        )


class TestUtilsCheckSpam(unittest.TestCase):
    """ test to utils untils.check_spam """

    def test_check_email_is_spam(self):
        """ method check_email_is_spam """

        receipt = {
            "timestamp": "2019-04-23T14:32:52.371Z",
            "processingTimeMillis": 477,
            "recipients": ["no-reply@helpec.com.br"],
            "spamVerdict": {"status": "PASS"},
            "virusVerdict": {"status": "PASS"},
            "spfVerdict": {"status": "PASS"},
            "dkimVerdict": {"status": "PASS"},
            "dmarcVerdict": {"status": "PASS"},
            "action": {
                "type": "S3",
                "topicArn": "arn:aws:sns:us-east-1:726337636269:SNSForwardEmails",
                "bucketName": "sth",
                "objectKeyPrefix": "",
                "objectKey": "bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1",
            },
        }
        check_spam.check_email_is_spam(
            "123456789", receipt, "test@example.com", "helpec.com.br"
        )

    @patch("forward_recieved_email.utils.check_spam.boto3")
    def test_check_email_is_spam_error(self, mk_boto3):
        """ method check_email_is_spam error """

        mk_boto3.client().send_bounce.return_value = {
            "MessageId": "726337636269"
        }

        receipt = {
            "timestamp": "2019-04-23T14:32:52.371Z",
            "processingTimeMillis": 477,
            "recipients": ["no-reply@helpec.com.br"],
            "spamVerdict": {"status": "PASS"},
            "virusVerdict": {"status": "FAIL"},
            "spfVerdict": {"status": "PASS"},
            "dkimVerdict": {"status": "PASS"},
            "dmarcVerdict": {"status": "PASS"},
            "action": {
                "type": "S3",
                "topicArn": "arn:aws:sns:us-east-1:726337636269:SNSForwardEmails",
                "bucketName": "sth",
                "objectKeyPrefix": "",
                "objectKey": "bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1",
            },
        }
        
        args = (
            "123456789", receipt, "test@example.com", "helpec.com.br"
        )
        self.assertRaises(
            Exception, check_spam.check_email_is_spam, *args
        )
        
    @mock_ses
    def test_check_email_is_spam_error2(self):
        """ method check_email_is_spam error 2 """
        
        conn = boto3.client("ses", region_name="us-east-1")
        conn.verify_email_identity(EmailAddress="no-reply@helpec.com.br")

        receipt = {
            "timestamp": "2019-04-23T14:32:52.371Z",
            "processingTimeMillis": 477,
            "recipients": ["no-reply@helpec.com.br"],
            "spamVerdict": {"status": "PASS"},
            "virusVerdict": {"status": "FAIL"},
            "spfVerdict": {"status": "PASS"},
            "dkimVerdict": {"status": "PASS"},
            "dmarcVerdict": {"status": "PASS"},
            "action": {
                "type": "S3",
                "topicArn": "arn:aws:sns:us-east-1:726337636269:SNSForwardEmails",
                "bucketName": "sth",
                "objectKeyPrefix": "",
                "objectKey": "bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1",
            },
        }
        
        args = (
            "123456789", receipt, "test@example.com", "helpec.com.br"
        )
        self.assertRaises(
            NotImplementedError, check_spam.check_email_is_spam, *args
        )
        
