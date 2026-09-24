import json
import logging
from typing import Any

from forward_received_email import processing
from forward_received_email.config import settings
from forward_received_email.utils import logger as c_logger

c_logger.configure_logger()

logger = logging.getLogger(__name__)


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    """AWS Lambda entry point."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOGGER_LEVEL)

    logger.debug(json.dumps(event, indent=4))
    return processing.main_handler(event)
