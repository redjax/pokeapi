from __future__ import annotations

from core.conf import api_settings, app_settings

import diskcache
import httpx

from red_utils.ext.diskcache_utils import default_cache_conf, new_cache
from red_utils.ext.httpx_utils import default_headers
from red_utils.ext.loguru_utils import (
    LoguruSinkAppFile,
    LoguruSinkErrFile,
    LoguruSinkStdOut,
)

## List default sinks. Include stdout, stderr, & app.log file
loguru_sinks: list = [
    LoguruSinkStdOut(level=app_settings.log_level).as_dict(),
    LoguruSinkAppFile(level=app_settings.log_level).as_dict(),
    LoguruSinkErrFile(level=app_settings.log_level).as_dict(),
]


def init_cache(
    cache_name: str, cache_conf: dict | None = default_cache_conf
) -> diskcache.Cache:
    """Quickly initialize a diskcache.Cache.

    DESCRIPTION:
    ------------

    Quickly initializes a cache at the default cache directory. If cache_conf is not overridden,
    uses the default configuration from red_utils.ext.diskcache_utils.defaault_cache_conf, replacing
    the directory name for the cache with the value passed for cache_name.

    PARAMS:
    -------

    *cache_name (str): Overrides the cache_conf["directory"] value, renaming the directory where the cache is stored.
    *cache_conf (dict): Cache configuration dict for the DiskCache Cache. Defaults to red_utils.ext.diskcache_utils.default_cache_conf.
    """
    if cache_conf is None:
        cache_conf = default_cache_conf

    cache_conf["directory"] = f"{app_settings.cache_dir}/{cache_name}"
    cache = new_cache(cache_conf=cache_conf)

    return cache
