""" module to config app """

import os

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

FORWARD_ADDRESSES = ["cesarabruschetta@gmail.com"]

AWS_DEFAULT_REGION = 'us-east-1'
FROM_ADDRESS = "AWS Forward <no-reply@%s>"
