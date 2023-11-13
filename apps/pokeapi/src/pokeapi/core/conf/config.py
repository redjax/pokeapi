from __future__ import annotations

from pathlib import Path
from typing import Union

from dynaconf import settings
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str | None = Field(default=settings.ENV or "prod", env="ENV")
    container_env: bool | None = Field(
        default=settings.CONTAINER_ENV or False, env="CONTAINER_ENV"
    )
    log_level: str | None = Field(default=settings.LOG_LEVEL or "INFO", env="LOG_LEVEL")

    data_dir: Union[str, Path] | None = Field(default=".data", env="DATA_DIR")
    cache_dir: Union[str, Path] | None = Field(default=".cache", env="CACHE_DIR")

    @field_validator("data_dir")
    def valid_data_dir(cls, v) -> Path:
        if v is None:
            return v
        elif isinstance(v, str):
            return Path(v)
        elif isinstance(v, Path):
            return v
        else:
            raise ValidationError


class APISettings(BaseSettings):
    base_url: str | None = Field(default=settings.API_BASE_URL or None)


class CelerySettings(BaseSettings):
    rabbitmq_host: str | None = Field(
        default=settings.RABBITMQ_HOST or None, env="RABBITMQ_HOST"
    )
    rabbitmq_port: int | None = Field(
        default=settings.RABBITMQ_PORT or None, env="RABBITMQ_PORT"
    )
    rabbitmq_user: str | None = Field(
        default=settings.RABBITMQ_USER or None, env="RABBITMQ_USER"
    )
    rabbitmq_password: str | None = Field(
        default=settings.RABBITMQ_PASS or None, env="RABBITMQ_PASS"
    )
    redis_host: str | None = Field(
        default=settings.REDIS_HOST or None, env="REDIS_HOST"
    )
    redis_port: Union[str, int] | None = Field(
        default=settings.REDIS_PORT or None, env="REDIS_PORT"
    )
