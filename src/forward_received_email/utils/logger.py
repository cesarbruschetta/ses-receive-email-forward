"""module to utils of logger app"""

from logging import config as l_config


def configure_logger():
    l_config.dictConfig(
        {
            "version": 1,
            'disable_existing_loggers': False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",  # noqa: E501
                    "datefmt": "%Y-%m-%d %H:%M:%S",  # noqa: E501
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            'root': {
                'handlers': ['console'],
            },
        }
    )
