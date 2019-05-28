""" module to test processing methods """
import unittest
import boto3
import os
from copy import deepcopy
from moto import mock_ses, mock_s3
from botocore.parsers import ResponseParserError

from forward_recieved_email import processing
from forward_recieved_email.config import settings
from . import SAMPLES_PATH


class TestProcessingMainHandler(unittest.TestCase):
    """ test to processing  """
    
    DEFAULT_EVENT = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:us-east-1:726337636269:SNSForwardEmails:298fa6ed-bd6b-40dd-bd86-21c0f8f047fa",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "4f5a8ced-138b-5ba7-b705-d9d437df5bf8",
                    "TopicArn": "arn:aws:sns:us-east-1:726337636269:SNSForwardEmails",
                    "Subject": "Amazon SES Email Receipt Notification",
                    "Message": '{"notificationType":"Received","mail":{"timestamp":"2019-04-23T14:32:52.371Z","source":"cesarabruschetta@gmail.com","messageId":"bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1","destination":["no-reply@helpec.com.br"],"headersTruncated":false,"headers":[{"name":"Return-Path","value":"<cesarabruschetta@gmail.com>"},{"name":"Received","value":"from mail-it1-f181.google.com (mail-it1-f181.google.com [209.85.166.181]) by inbound-smtp.us-east-1.amazonaws.com with SMTP id bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1 for no-reply@helpec.com.br; Tue, 23 Apr 2019 14:32:52 +0000 (UTC)"},{"name":"X-SES-Spam-Verdict","value":"PASS"},{"name":"X-SES-Virus-Verdict","value":"PASS"},{"name":"Received-SPF","value":"pass (spfCheck: domain of _spf.google.com designates 209.85.166.181 as permitted sender) client-ip=209.85.166.181; envelope-from=cesarabruschetta@gmail.com; helo=mail-it1-f181.google.com;"},{"name":"Authentication-Results","value":"amazonses.com; spf=pass (spfCheck: domain of _spf.google.com designates 209.85.166.181 as permitted sender) client-ip=209.85.166.181; envelope-from=cesarabruschetta@gmail.com; helo=mail-it1-f181.google.com; dkim=pass header.i=@gmail.com; dmarc=pass header.from=gmail.com;"},{"name":"X-SES-RECEIPT","value":"AEFBQUFBQUFBQUFITUxhSnFUT2d2dm4yRE5kMlhpY095QjNyWEUzQkkyNDBzKzBWdjNDMGkxSUFDTXpPSTAybG9hNHRWa1l4QUgyYmlDYmJabWZqeFgvMlE5ZGVRVStVS0VNWXo5Q0kxbTJXUEkyYkV4bTlFVnJYOTZpT0d0S0lFWDk1VWcwcWlCYStWNVd2c0dWbURmcUZ0Mis2WmllU3lZOU1kT3gwbzVJUXFqWWFkK2VhcmVFMnBQNXl1Ynd4eGJFeVRJb2hUVk1jWWpSOUkrOSttY0p5VHNWcnlVZUUrQzJuUDF5d1h3SC9PNnBWa0VsWFY3d2pna0FLRUxqcDJNZTdCWDdsRDFkRWZaSkFUaVZMbFRrMEc2U2w5cHRVMDNOaEpxeFlyYUVMMTBlNExlZ0wwbVE9PQ=="},{"name":"X-SES-DKIM-SIGNATURE","value":"a=rsa-sha256; q=dns/txt; b=dr/CYYSt/mYsB8cR9juD0aEB478OZJBx8h2W6anzraUvX6jVPLrWS75sV9j3nrGwlfWU7/XngfcjwsZ5qE5pXETWO3PUBblJ5pDqzAQQOyhZ2ABCTP4KB+a9s2tFwD4WnVFQblSfJnc3NacuzudZqnGHx31EqCCUB95yk9GMIeQ=; c=relaxed/simple; s=6gbrjpgwjskckoa6a5zn6fwqkn67xbtw; d=amazonses.com; t=1556029972; v=1; bh=ywQreeOkadAdZ4/Mb1zduBsKNiG1+BXALry0J1bAdw4=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;"},{"name":"Received","value":"by mail-it1-f181.google.com with SMTP id v8so2790032itf.0 for <no-reply@helpec.com.br>; Tue, 23 Apr 2019 07:32:52 -0700 (PDT)"},{"name":"DKIM-Signature","value":"v=1; a=rsa-sha256; c=relaxed/relaxed; d=gmail.com; s=20161025; h=mime-version:references:in-reply-to:from:date:message-id:subject:to; bh=K8y9wkgTIbOTc5gTsasKDdwFKtbdjtYf/L8YeKUzILo=; b=p/5EzGkfWBKfWUe6UteKF5mCKaLRQZ8sbhfYJE3y0rdGMsB2dawznQYLPoU5xGJuaRnm67ilof/DRMqOst0Pj9f89uK+XjEYFuhi/gJ8TFCYED+NBR0ouXQHZi1FUftsm2j0wxqnXBWharE/aX8VRivSDSkLK/Dd0NoGJeVBPBWAa/3yiKwnhm6uo7tW81KxYswvyHwtjdX9tlUSb952O3rH6IB21kdCebDf/UqJ6N7hTskfXSwugZtcyyaMtnr9L/6wkexSvZd4lVWE8Msd8yvdnDXvFfXAzNAihx1eqpdzy5iTJmw9fbm49xVwlG/KiOp/MohoOZGj9v+1ILi1Qg=="},{"name":"X-Google-DKIM-Signature","value":"v=1; a=rsa-sha256; c=relaxed/relaxed; d=1e100.net; s=20161025; h=x-gm-message-state:mime-version:references:in-reply-to:from:date :message-id:subject:to; bh=K8y9wkgTIbOTc5gTsasKDdwFKtbdjtYf/L8YeKUzILo=; b=eqehPEGfeL0gBwPp/EjuCkddiPVXxmYKOKNJT6w9KMnvrFfbnsaqRoBoyadvWXMGEj qTuHG7DF4OVYvub5N1H0nZwbp/jN6sekdAhRksw11L6ocY4CqJoKMN4TyrAoVQzgbj0A 8G8O0QEcIHkBXp9DWzVEHy7yp/HenGnVwoBzgF3pzuqXr3OeYtIlma2DyGDVja/xMpxD SUmlneIVuhYUF1cYmVqQkpEMg44e1p6Q8misj4ZKfe28lW66uV8YbIhpsYI4ZJReDU/F MiwXTTzxc3tkssN5qpHbPqoCLg0Lc27DOTgZmHQ520kBZvvU0MehTkKg1I8hujW2S/GI UjAA=="},{"name":"X-Gm-Message-State","value":"APjAAAU7FtElN25DXrAG9S7wkytsfpdOR9t2Ogt1WtCy33k0cNaVJsLc 818YM3v/5j4c9NU5LsFanyA32Vfd6Un+FcEISnt8xZSe"},{"name":"X-Google-Smtp-Source","value":"APXvYqyvwHXb7PSGn+TbrIXD26bsNROGd4f//xSjz+sZB6sqKyfnWEguw3lcSZ09G9mEFp3B5jHeVbnF0+KJ/nXY9SE="},{"name":"X-Received","value":"by 2002:a05:660c:202:: with SMTP id y2mr2299056itj.0.1556029971147; Tue, 23 Apr 2019 07:32:51 -0700 (PDT)"},{"name":"MIME-Version","value":"1.0"},{"name":"References","value":"<CAJzr1CqRme-LcD1FEDhTafdkVKA+0+aOR65KBbFYGpNfkxfm9w@mail.gmail.com>"},{"name":"In-Reply-To","value":"<CAJzr1CqRme-LcD1FEDhTafdkVKA+0+aOR65KBbFYGpNfkxfm9w@mail.gmail.com>"},{"name":"From","value":"Cesar Augusto Bruschetta <cesarabruschetta@gmail.com>"},{"name":"Date","value":"Tue, 23 Apr 2019 11:32:42 -0300"},{"name":"Message-ID","value":"<CAJzr1CqtvvXRsUvC_ZuOex6jMEyLJcxR-n0fL4c0cBZrSAeAeA@mail.gmail.com>"},{"name":"Subject","value":"Fwd: dadda"},{"name":"To","value":"no-reply@helpec.com.br"},{"name":"Content-Type","value":"multipart/alternative; boundary=\\"000000000000b0b0c80587337519\\""}],"commonHeaders":{"returnPath":"cesarabruschetta@gmail.com","from":["Cesar Augusto Bruschetta <cesarabruschetta@gmail.com>"],"date":"Tue, 23 Apr 2019 11:32:42 -0300","to":["no-reply@helpec.com.br"],"messageId":"<CAJzr1CqtvvXRsUvC_ZuOex6jMEyLJcxR-n0fL4c0cBZrSAeAeA@mail.gmail.com>","subject":"Fwd: dadda"}},"receipt":{"timestamp":"2019-04-23T14:32:52.371Z","processingTimeMillis":477,"recipients":["no-reply@helpec.com.br"],"spamVerdict":{"status":"PASS"},"virusVerdict":{"status":"PASS"},"spfVerdict":{"status":"PASS"},"dkimVerdict":{"status":"PASS"},"dmarcVerdict":{"status":"PASS"},"action":{"type":"S3","topicArn":"arn:aws:sns:us-east-1:726337636269:SNSForwardEmails","bucketName":"receive-email-forward-sns","objectKeyPrefix":"","objectKey":"bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1"}}}',
                    "Timestamp": "2019-04-23T14:32:52.864Z",
                    "SignatureVersion": "1",
                    "Signature": "QWxVxfpQwrkBEyYpj002cNQc9153OVvCcmSnwPQMD60U9wJXjfCT/siioCnSXIgb44NkEbdAGmvsw4y4KFpLKss4jYjwd7dknsh9lSOsPvEPLd+0BbkeYuMEs6NsxrVetNHVosfmQrK+xlX3NcPJRas5rSDWZJEkuBhb1mmDQIYr+gVQbEIRkSByqLADYm3U4Go9uf2h/Zge2kElnSiffIdOCKvwEarxcTufUenuSrrOwfUDvGwXtFEgjFBCVw0kJCOnwpgCKBTRZFjt1FxAvrEcGcECCPXgtB99sAkbUNcIvPvCPMmvSgAKWEk6TBZQ8DTgm0z4J3Vfq8yscoOC6A==",
                    "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-6aad65c2f9911b05cd53efda11f913f9.pem",
                    "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:726337636269:SNSForwardEmails:298fa6ed-bd6b-40dd-bd86-21c0f8f047fa",
                    "MessageAttributes": {},
                },
            }
        ]
    }

    @mock_ses
    @mock_s3
    def test_main_handler(self):
        """ test to processing.main_handler  """

        conn_ses = boto3.client("ses", region_name=settings.AWS_DEFAULT_REGION)
        conn_ses.verify_email_identity(EmailAddress="no-reply@helpec.com.br")

        conn_s3 = boto3.resource("s3", region_name=settings.AWS_DEFAULT_REGION)
        conn_s3.create_bucket(Bucket="receive-email-forward-sns")
        bucket = conn_s3.Bucket("receive-email-forward-sns")

        bucket.put_object(
            Key="bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1",
            Body=open(os.path.join(SAMPLES_PATH, "email.txt"), "rb").read(),
        )

        result = processing.main_handler(self.DEFAULT_EVENT)
        self.assertFalse(result)

    @mock_ses
    @mock_s3
    def test_main_handler_test_error(self):
        """ test to processing.main_handler with error """

        conn_ses = boto3.client("ses", region_name=settings.AWS_DEFAULT_REGION)
        conn_ses.verify_email_identity(EmailAddress="no-reply@test.com.br")

        conn_s3 = boto3.resource("s3", region_name=settings.AWS_DEFAULT_REGION)
        conn_s3.create_bucket(Bucket="receive-email-forward-sns")
        bucket = conn_s3.Bucket("receive-email-forward-sns")

        bucket.put_object(
            Key="bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1",
            Body=open(os.path.join(SAMPLES_PATH, "email.txt"), "rb").read(),
        )

        self.assertRaises(
            ResponseParserError, processing.main_handler, self.DEFAULT_EVENT
        )

    @mock_ses
    @mock_s3
    def test_main_handler_test_not_s3(self):
        """ test to processing.main_handler not s3 """

        event = deepcopy(self.DEFAULT_EVENT)
        event["Records"][0]["Sns"]["Message"] = '{"notificationType":"Received","mail":{"timestamp":"2019-04-23T14:32:52.371Z","source":"cesarabruschetta@gmail.com","messageId":"bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1","destination":["no-reply@helpec.com.br"],"headersTruncated":false,"headers":[{"name":"Return-Path","value":"<cesarabruschetta@gmail.com>"},{"name":"Received","value":"from mail-it1-f181.google.com (mail-it1-f181.google.com [209.85.166.181]) by inbound-smtp.us-east-1.amazonaws.com with SMTP id bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1 for no-reply@helpec.com.br; Tue, 23 Apr 2019 14:32:52 +0000 (UTC)"},{"name":"X-SES-Spam-Verdict","value":"PASS"},{"name":"X-SES-Virus-Verdict","value":"PASS"},{"name":"Received-SPF","value":"pass (spfCheck: domain of _spf.google.com designates 209.85.166.181 as permitted sender) client-ip=209.85.166.181; envelope-from=cesarabruschetta@gmail.com; helo=mail-it1-f181.google.com;"},{"name":"Authentication-Results","value":"amazonses.com; spf=pass (spfCheck: domain of _spf.google.com designates 209.85.166.181 as permitted sender) client-ip=209.85.166.181; envelope-from=cesarabruschetta@gmail.com; helo=mail-it1-f181.google.com; dkim=pass header.i=@gmail.com; dmarc=pass header.from=gmail.com;"},{"name":"X-SES-RECEIPT","value":"AEFBQUFBQUFBQUFITUxhSnFUT2d2dm4yRE5kMlhpY095QjNyWEUzQkkyNDBzKzBWdjNDMGkxSUFDTXpPSTAybG9hNHRWa1l4QUgyYmlDYmJabWZqeFgvMlE5ZGVRVStVS0VNWXo5Q0kxbTJXUEkyYkV4bTlFVnJYOTZpT0d0S0lFWDk1VWcwcWlCYStWNVd2c0dWbURmcUZ0Mis2WmllU3lZOU1kT3gwbzVJUXFqWWFkK2VhcmVFMnBQNXl1Ynd4eGJFeVRJb2hUVk1jWWpSOUkrOSttY0p5VHNWcnlVZUUrQzJuUDF5d1h3SC9PNnBWa0VsWFY3d2pna0FLRUxqcDJNZTdCWDdsRDFkRWZaSkFUaVZMbFRrMEc2U2w5cHRVMDNOaEpxeFlyYUVMMTBlNExlZ0wwbVE9PQ=="},{"name":"X-SES-DKIM-SIGNATURE","value":"a=rsa-sha256; q=dns/txt; b=dr/CYYSt/mYsB8cR9juD0aEB478OZJBx8h2W6anzraUvX6jVPLrWS75sV9j3nrGwlfWU7/XngfcjwsZ5qE5pXETWO3PUBblJ5pDqzAQQOyhZ2ABCTP4KB+a9s2tFwD4WnVFQblSfJnc3NacuzudZqnGHx31EqCCUB95yk9GMIeQ=; c=relaxed/simple; s=6gbrjpgwjskckoa6a5zn6fwqkn67xbtw; d=amazonses.com; t=1556029972; v=1; bh=ywQreeOkadAdZ4/Mb1zduBsKNiG1+BXALry0J1bAdw4=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;"},{"name":"Received","value":"by mail-it1-f181.google.com with SMTP id v8so2790032itf.0 for <no-reply@helpec.com.br>; Tue, 23 Apr 2019 07:32:52 -0700 (PDT)"},{"name":"DKIM-Signature","value":"v=1; a=rsa-sha256; c=relaxed/relaxed; d=gmail.com; s=20161025; h=mime-version:references:in-reply-to:from:date:message-id:subject:to; bh=K8y9wkgTIbOTc5gTsasKDdwFKtbdjtYf/L8YeKUzILo=; b=p/5EzGkfWBKfWUe6UteKF5mCKaLRQZ8sbhfYJE3y0rdGMsB2dawznQYLPoU5xGJuaRnm67ilof/DRMqOst0Pj9f89uK+XjEYFuhi/gJ8TFCYED+NBR0ouXQHZi1FUftsm2j0wxqnXBWharE/aX8VRivSDSkLK/Dd0NoGJeVBPBWAa/3yiKwnhm6uo7tW81KxYswvyHwtjdX9tlUSb952O3rH6IB21kdCebDf/UqJ6N7hTskfXSwugZtcyyaMtnr9L/6wkexSvZd4lVWE8Msd8yvdnDXvFfXAzNAihx1eqpdzy5iTJmw9fbm49xVwlG/KiOp/MohoOZGj9v+1ILi1Qg=="},{"name":"X-Google-DKIM-Signature","value":"v=1; a=rsa-sha256; c=relaxed/relaxed; d=1e100.net; s=20161025; h=x-gm-message-state:mime-version:references:in-reply-to:from:date :message-id:subject:to; bh=K8y9wkgTIbOTc5gTsasKDdwFKtbdjtYf/L8YeKUzILo=; b=eqehPEGfeL0gBwPp/EjuCkddiPVXxmYKOKNJT6w9KMnvrFfbnsaqRoBoyadvWXMGEj qTuHG7DF4OVYvub5N1H0nZwbp/jN6sekdAhRksw11L6ocY4CqJoKMN4TyrAoVQzgbj0A 8G8O0QEcIHkBXp9DWzVEHy7yp/HenGnVwoBzgF3pzuqXr3OeYtIlma2DyGDVja/xMpxD SUmlneIVuhYUF1cYmVqQkpEMg44e1p6Q8misj4ZKfe28lW66uV8YbIhpsYI4ZJReDU/F MiwXTTzxc3tkssN5qpHbPqoCLg0Lc27DOTgZmHQ520kBZvvU0MehTkKg1I8hujW2S/GI UjAA=="},{"name":"X-Gm-Message-State","value":"APjAAAU7FtElN25DXrAG9S7wkytsfpdOR9t2Ogt1WtCy33k0cNaVJsLc 818YM3v/5j4c9NU5LsFanyA32Vfd6Un+FcEISnt8xZSe"},{"name":"X-Google-Smtp-Source","value":"APXvYqyvwHXb7PSGn+TbrIXD26bsNROGd4f//xSjz+sZB6sqKyfnWEguw3lcSZ09G9mEFp3B5jHeVbnF0+KJ/nXY9SE="},{"name":"X-Received","value":"by 2002:a05:660c:202:: with SMTP id y2mr2299056itj.0.1556029971147; Tue, 23 Apr 2019 07:32:51 -0700 (PDT)"},{"name":"MIME-Version","value":"1.0"},{"name":"References","value":"<CAJzr1CqRme-LcD1FEDhTafdkVKA+0+aOR65KBbFYGpNfkxfm9w@mail.gmail.com>"},{"name":"In-Reply-To","value":"<CAJzr1CqRme-LcD1FEDhTafdkVKA+0+aOR65KBbFYGpNfkxfm9w@mail.gmail.com>"},{"name":"From","value":"Cesar Augusto Bruschetta <cesarabruschetta@gmail.com>"},{"name":"Date","value":"Tue, 23 Apr 2019 11:32:42 -0300"},{"name":"Message-ID","value":"<CAJzr1CqtvvXRsUvC_ZuOex6jMEyLJcxR-n0fL4c0cBZrSAeAeA@mail.gmail.com>"},{"name":"Subject","value":"Fwd: dadda"},{"name":"To","value":"no-reply@helpec.com.br"},{"name":"Content-Type","value":"multipart/alternative; boundary=\\"000000000000b0b0c80587337519\\""}],"commonHeaders":{"returnPath":"cesarabruschetta@gmail.com","from":["Cesar Augusto Bruschetta <cesarabruschetta@gmail.com>"],"date":"Tue, 23 Apr 2019 11:32:42 -0300","to":["no-reply@helpec.com.br"],"messageId":"<CAJzr1CqtvvXRsUvC_ZuOex6jMEyLJcxR-n0fL4c0cBZrSAeAeA@mail.gmail.com>","subject":"Fwd: dadda"}},"receipt":{"timestamp":"2019-04-23T14:32:52.371Z","processingTimeMillis":477,"recipients":["no-reply@helpec.com.br"],"spamVerdict":{"status":"PASS"},"virusVerdict":{"status":"PASS"},"spfVerdict":{"status":"PASS"},"dkimVerdict":{"status":"PASS"},"dmarcVerdict":{"status":"PASS"},"action":{"type":"no-S3","topicArn":"arn:aws:sns:us-east-1:726337636269:SNSForwardEmails","bucketName":"receive-email-forward-sns","objectKeyPrefix":"","objectKey":"bs82kksd5uhl2b598fhhro1scu3d05a39id0gdg1"}}}'

        result = processing.main_handler(event)
        self.assertFalse(result)
