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


def read_from_file(file: Union[str, Path] = None, mode: str = "r") -> list[str]:
    """Read lines of file into list of strings.

    Params:
    -------

    file (str|Path): Path to a file to read from. If a string is passed, it is
        converted to a Path object.

    mode (str): File mode.
    """
    if not file:
        raise ValueError(f"Missing file to read from.")

    if isinstance(file, str):
        file: Path = Path(file)

    if not file.exists():
        log.error(FileNotFoundError(file))
        return None

    lines: list[str] = []

    try:
        with open(file, mode) as f:
            _lines: list[str] = f.readlines()

        for line in _lines:
            lines.append(line.strip("\n").lower())

        log.debug(f"Read [{len(lines)}] Pokemon name(s) from file [{file}]")

        return lines

    except Exception as exc:
        raise Exception(
            f"Unhandled exception reading Pokemon names from file: [{file}]. Details: {exc}"
        )
