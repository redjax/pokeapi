import sys

sys.path.append(".")

import json

from pathlib import Path
import random
from typing import Union

from pokeapi.core.conf import api_settings, app_settings
from pokeapi.dependencies import init_cache, loguru_sinks
from pokeapi.utils.path_utils import ensure_dirs_exist
from loguru import logger as log
from red_utils.ext.diskcache_utils import (
    check_cache_key_exists,
    get_val,
    set_val,
)
from red_utils.ext.loguru_utils import init_logger

if __name__ == "__main__":
    ## Ensure directory paths exist before starting app
    ensure_dirs_exist([app_settings.data_dir, app_settings.cache_dir])
    ## Initialize Loguru logger
    init_logger(sinks=loguru_sinks)

    log.info(f"[env:{app_settings.env}|container:{app_settings.container_env}]")

    log.debug(f"App Settings: {app_settings}")
    log.debug(f"API Settings: {api_settings}")

    ## Create caches
    # req_cache = init_cache("requests")
    # app_cache = init_cache("app")
