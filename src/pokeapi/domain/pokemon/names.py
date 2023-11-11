from __future__ import annotations

from pathlib import Path
from typing import Union

from pokeapi.core.conf import app_settings

from loguru import logger as log
from pydantic import BaseModel, Field, ValidationError, field_validator

pokemon_names_file: Path = Path(f"{app_settings.data_dir}/list_all_pokemon.txt")


class PokemonNamesFile(BaseModel):
    """The .list property of this class is a list of all Pokemon names loaded from a file defined in read_file."""

    read_file: Union[str, Path] | None = Field(default=pokemon_names_file)
    names_list: list[str] | None = Field(default=None)

    @field_validator("read_file")
    def valid_read_file(cls, v) -> Path:
        if isinstance(v, str):
            return Path(v)
        elif isinstance(v, Path):
            return v
        else:
            raise ValidationError

    def read_from_file(self) -> list[str]:
        """Read all Pokemon names from pre-populated text file."""
        if not self.read_file.exists():
            raise FileNotFoundError(f"Could not find file: {self.read_file}")

        names: list[str] = []

        try:
            with open(self.read_file, "r") as names_file:
                lines = names_file.readlines()

                for line in lines:
                    names.append(line.strip("\n").lower())

            log.debug(
                f"Read [{len(names)}] Pokemon name(s) from file [{self.read_file}]"
            )

            self.names_list = names
            return names

        except Exception as exc:
            raise Exception(
                f"Unhandled exception reading Pokemon names from file: [{self.read_file}]. Details: {exc}"
            )
