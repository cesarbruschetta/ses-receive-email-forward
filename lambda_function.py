import sys
import os
import json
import logging
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forward_recieved_email.utils import logger as c_logger
from forward_recieved_email.config import settings
from forward_recieved_email import processing

# SET LOGGER
c_logger.configure_logger()

logger = logging.getLogger(__name__)


def lambda_handler(event: Dict, context: Dict) -> None:
    """ AWS lambda start """

    # CHANGE LOGGER
    logger = logging.getLogger()
    logger.setLevel(settings.LOGGER_LEVEL)

    logger.debug(json.dumps(event, indent=4))

    result = processing.main_handler(event)
    return result
