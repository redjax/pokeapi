from __future__ import annotations

from pokeapi.core.conf import api_settings, app_settings

import httpx
import diskcache

from red_utils.ext.httpx_utils import default_headers
from red_utils.ext.loguru_utils import (
    LoguruSinkAppFile,
    LoguruSinkErrFile,
    LoguruSinkStdOut,
)
from red_utils.ext.diskcache_utils import default_cache_conf, new_cache

loguru_sinks: list = [
    LoguruSinkStdOut(level=app_settings.log_level).as_dict(),
    LoguruSinkAppFile(level=app_settings.log_level).as_dict(),
    LoguruSinkErrFile(level=app_settings.log_level).as_dict(),
]


def init_cache(cache_name: str) -> diskcache.Cache:
    """Quickly initialize a diskcache.Cache.

    Uses the default cache conf from red_utils, overriding the directory
    with the value passed to cache_name.
    """
    cache_conf = default_cache_conf
    cache_conf["directory"] = f"{app_settings.cache_dir}/{cache_name}"
    cache = new_cache(cache_conf=cache_conf)

    return cache
