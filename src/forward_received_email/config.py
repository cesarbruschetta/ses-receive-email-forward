"""Application settings for the SES forwarder."""

from __future__ import annotations

import logging
import os
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_log_level(loglevel: str) -> int:
    """Return the logging level for the given name."""
    return getattr(logging, loglevel.upper(), logging.INFO)


def split_list_email(value: Any) -> list[str]:
    """
    Return an email list from a comma-delimited
    string or an existing list.
    """
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    FORWARD_ADDRESSES: Annotated[list[str], Field(default_factory=list)] = (
        Field(
            default_factory=list,
            validation_alias="FORWARD_ADDRESSES",
        )
    )
    AWS_DEFAULT_REGION: str = Field(default="us-east-1")
    FROM_ADDRESS: str = Field(default="AWS Forward <no-reply@%s>")
    LOGGER_LEVEL: Annotated[int, Field(default=logging.INFO)] = Field(
        default=logging.INFO, validation_alias="LOGGER_LEVEL"
    )

    @field_validator("FORWARD_ADDRESSES", mode="before")
    @classmethod
    def validate_forward_addresses(cls, value: Any) -> list[str]:
        return split_list_email(value)

    @field_validator("LOGGER_LEVEL", mode="before")
    @classmethod
    def validate_logger_level(cls, value: Any) -> int:
        if isinstance(value, int):
            return value
        if value is None:
            return logging.INFO
        return get_log_level(str(value))


settings = Settings()
