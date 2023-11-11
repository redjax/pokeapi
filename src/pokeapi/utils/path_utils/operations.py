from __future__ import annotations

from pathlib import Path
from typing import Union

from loguru import logger as log


def ensure_dirs_exist(dirs: list[Union[str, Path]] = None) -> None:
    """Loop over list of dir strings/paths. Create directories that do not exist."""
    if dirs is None:
        raise ValueError("Missing dirs to ensure existence.")

    for d in dirs:
        if isinstance(d, str):
            d = Path(d)

        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
