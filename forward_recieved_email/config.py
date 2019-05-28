""" module to config app """
import os
import logging
from typing import Dict

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


def get_log_level(loglevel):
    """ return loglevel to config """
    return getattr(logging, loglevel.upper())


def split_list_email(str_email):
    """ return list to emails """
    if not isinstance(str_email, list):
        return [e.strip() for e in str_email.split(",")]
    return str_email


class Configuration:
    """ class to config app """

    DEFAULT_SETTINGS = [
        ("FORWARD_ADDRESSES", "FORWARD_ADDRESSES", split_list_email, []),
        ("AWS_DEFAULT_REGION", "AWS_DEFAULT_REGION", str, "us-east-1"),
        ("FROM_ADDRESS", "FROM_ADDRESS", str, "AWS Forward <no-reply@%s>"),
        ("LOGGER_LEVEL", "LOGGER_LEVEL", get_log_level, "WARNING"),
    ]

    def __repr__(self):
        return "<%(cls)s >" % {"cls": self.__class__.__name__}

    def __init__(self):
        self.parse_settings(defaults=self.DEFAULT_SETTINGS)

    def parse_settings(self, defaults: Dict) -> None:
        """Analisa e retorna as configurações da app com base no env.
        O argumento `defaults` deve receber uma lista associativa na forma:
    
          [
            (<diretiva de config>, <variável de ambiente>, <função de conversão>, <valor padrão>),
          ]
        """
        parsed = {}
        cfg = list(defaults)

        for name, envkey, convert, default in cfg:
            value = os.environ.get(envkey, default)
            if convert is not None:
                value = convert(value)

            setattr(self, name, value)


settings = Configuration()
