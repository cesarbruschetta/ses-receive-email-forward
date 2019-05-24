""" module to test utils methods """
import os
import unittest
import boto3
from moto import mock_ses

from forward_recieved_email.utils import tools, check_spam
from forward_recieved_email import config
from . import SAMPLES_PATH


class TestUtilsTools(unittest.TestCase):
    """ test to utils.tools  """
    
    def test_read_spammer_file(self):
        """ method read_spammer_file """
        
        result = tools.read_spammer_file("domains")
        self.assertIn("0costofivf.com", result)
    
    def test_decode_email(self):
        """ method decode_email """
        
        with open( os.path.join(SAMPLES_PATH, "email.txt"), "rb") as fp:
            file_msg = fp.read()
        text = tools.decode_email(file_msg)
        self.assertIn("Cesar Augusto Bruschetta", text)
    
    @mock_ses
    def test_sed_email_to(self):
        """ method sed_email_to """
        conn = boto3.client('ses', region_name='us-east-1')
        conn.verify_email_identity(EmailAddress="no-reply@helpec.com.br")
    
        result = tools.sed_email_to("123456789","ASSUNTO","MENSAGEM TEXTO")
        
class TestUtilsCheckSpam(unittest.TestCase):
    """ test to utils untils.check_spam """
    
    def test_check_email_is_spam(self):
        """ method check_email_is_spam """
        
        receipt = {'timestamp': '2019-04-23T14:32:52.371Z', 'processingTimeMillis': 477, 'recipients': ['no-reply@helpec.com.br'], 'spamVerdict': {'status': 'PASS'}, 'virusVerdict': {'status': 'PASS'}, 'spfVerdict': {'status': 'PASS'}, 'dkimVerdict': {'status': 'PASS'}, 'dmarcVerdict': {'status': 'PASS'}, 'action': {'type': 'S3', 'topicArn': 'arn:aws:sns:us-east-1:726337636269:SNSForwardEmails', 'bucketName': 'sth', 'objectKeyPrefix': '', 'objectKey': 'bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1'}}
        check_spam.check_email_is_spam("123456789", receipt,"test@example.com")
        