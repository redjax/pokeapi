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
    serialize_dir: Union[str, Path] | None = Field(
        default=".serialize", env="SERIALIZE_DIR"
    )

    @field_validator("data_dir", "cache_dir", "serialize_dir")
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
    broker_host: str = Field(
        default=settings.CELERY_BROKER_HOST, env="CELERY_BROKER_HOST"
    )
    broker_port: Union[str, int] = Field(
        default=settings.CELERY_BROKER_PORT, env="CELERY_BROKER_PORT"
    )
    broker_user: str = Field(
        default=settings.CELERY_BROKER_USER, env="CELERY_BROKER_USER"
    )
    broker_password: str = Field(
        default=settings.CELERY_BROKER_PASS, env="CELERY_BROKER_PASS"
    )
    backend_host: str = Field(
        default=settings.CELERY_BACKEND_HOST, env="CELERY_BACKEND_HOST"
    )
    backend_port: Union[str, int] = Field(
        default=settings.CELERY_BACKEND_PORT, env="CELERY_BACKEND_PORT"
    )

    @field_validator("broker_port", "backend_port")
    def validate_port(cls, v) -> int:
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass

        return v

    @property
    def broker_url(self) -> str:
        try:
            _url = f"amqp://{self.broker_user}:{self.broker_password}@{self.broker_host}:{self.broker_port}"
            return _url

        except Exception as exc:
            raise Exception(
                f"Unhandled exception building Celery broker URL. Details: {exc}"
            )

    @property
    def backend_url(self) -> str:
        try:
            _url = f"redis://{self.backend_host}:{self.backend_port}"

            return _url

        except Exception as exc:
            raise Exception(
                f"Unhandled exception building Celery backend URL. Details: {exc}"
            )


## Initialize settings objects
app_settings = Settings()
api_settings = APISettings()
celery_settings: CelerySettings = CelerySettings()
