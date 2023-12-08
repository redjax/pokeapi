from pydantic import BaseModel, Field, validator, ValidationError
from typing import Union
from datetime import datetime
import uuid
from pathlib import Path

from loguru import logger as log

from core.conf import app_settings

SERIALIZE_DIR: str = app_settings.serialize_dir

from red_utils.ext.msgpack_utils import (
    SerialFunctionResponse,
)

import msgpack


class SerializedData(BaseModel):
    data: dict = Field(default=None)
    output_dir: Union[Path, str] = Field(default=SERIALIZE_DIR)
    name: Union[uuid.UUID, str] | None = Field(default=uuid.uuid4())
    date_serialized: datetime = Field(default_factory=datetime.now)

    @validator("output_dir")
    def validate_output_dir(cls, v) -> Path:
        if isinstance(v, str):
            v = Path(v)
        elif isinstance(v, Path):
            return v
        else:
            raise ValidationError

    @property
    def filename(self) -> str:
        if not self.name.endswith(".msgpack"):
            return f"{self.name}.msgpack"
        else:
            return self.name

    @property
    def output_path(self) -> Path:
        _path: Path = Path(f"{self.output_dir}/{self.name}")

        return _path

    def serialize(self) -> SerialFunctionResponse:
        if self.data is None:
            raise ValueError("Missing data to serialize")
        if self.name is None:
            log.warning("Filename is empty. Generating UUID filename.")
            _filename: str = f"{uuid.uuid4()}.msgpack"
            self.name = _filename

        if not self.output_path.parent.exists():
            try:
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception creating output directory: {self.output_path.parent}. Details: {exc}"
                )
                log.error(
                    f"Error serializing file to {self.output_path}. Details: {exc}"
                )

        serial_data = self.model_dump_json()
        log.debug(f"Serial data [{self.name}] type: ({type(self)})")
        # log.debug(f"Serial data: {serial_data}")
        serial_data["output_dir"] = str(self.output_dir)
        ser: bytes = msgpack.packb(serial_data)
        with open(self.output_path, "wb") as outfile:
            outfile.write(ser)

        return ser

    def deserialze(self) -> dict:
        raise NotImplementedError("Deserializing objects is not implemented yet")

        with open(self.output_path, "rb") as read_file:
            bytes_data = data_file.read()

        data = msgpack.unpackb(bytes_data)
