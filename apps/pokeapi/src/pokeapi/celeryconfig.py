from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field

from dynaconf import settings

# broker_url: str = "pyamqp://"
# result_backend: str = "rpc://"
# task_serializer: str = "json"
# result_serialiser: str = "json"
# accept_content: list = ["json"]
# timezone: str = "America/New_York"
# enable_utc: bool = True

class CelerySettings(BaseSettings):
    rabbitmq_host: str = Field(default=settings.RABBITMQ_HOST, env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=settings.RABBITMQ_PORT, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default=settings.RABBITMQ_USER, env="RABBITMQ_USER")
    rabbitmq_password: str = Field(default=settings.RABBITMQ_PASS, env="RABBITMQ_PASS")
    redis_host: str = Field(default=settings.REDIS_HOST, env="REDIS_HOST")
    redis_port: int = Field(default=settings.REDIS_PORT, env="REDIS_PORT")