from __future__ import annotations

import sys

sys.path.append(".")

from loguru import logger as log
from red_utils.ext.loguru_utils import LoguruSinkStdErr, init_logger

sinks = [LoguruSinkStdErr().as_dict()]

if __name__ == "__main__":
    init_logger(sinks=sinks)

    log.info("Pokeapi called without any parameters.")
