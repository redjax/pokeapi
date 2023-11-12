from __future__ import annotations

from . import config
from .config import Settings, APISettings, CelerySettings

app_settings = Settings()
api_settings = APISettings()
celery_settings = CelerySettings()
