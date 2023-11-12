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
