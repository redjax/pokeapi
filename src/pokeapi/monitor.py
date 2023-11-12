"""WIP:

Monitor a file (i.e. the error.log file) for events or specific strings
and react.
"""
from __future__ import annotations

from pathlib import Path
from queue import Queue
from threading import Event, Thread
import time

from typing import Callable, Union

from loguru import logger as log
from pydantic import BaseModel, Field, FilePath, ValidationError, field_validator

def detect_string_thread(
    detect: Union[str, list[str]], text_queue: Queue, line_ready: Event
):
    detect = [detect] if isinstance(detect, str) else detect
    try:
        print(f"Monitoring text stream for string(s): {detect}...")

        while True:
            # Wait for a line to be ready
            line_ready.wait()

            line, line_number = text_queue.get()
            for detect_str in detect:
                if detect_str.lower() in line.lower():
                    print(
                        f"String '{detect_str}' detected on line {line_number}: {line.strip()}"
                    )

    except Exception as exc:
        raise Exception(f"Error in detect_string_multi_thread. Details: {exc}")


class TailFile(BaseModel):
    read_file: Union[str, Path] | None = Field(default=None)
    text_queue: Queue | None = Field(default_factory=Queue)
    line_ready: Event | None = Field(default_factory=Event)

    @field_validator("read_file")
    def validate_read_file(cls, v) -> Path:
        if isinstance(v, str):
            return Path(v)
        elif isinstance(v, Path):
            return v
        else:
            raise ValidationError

    class Config:
        arbitrary_types_allowed = True

    def start_thread(self, func: Callable, *args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    def tail(self, line_ready: Event):
        try:
            with open(self.read_file, "r") as file:
                line_number = 0
                while True:
                    line = file.readline()
                    if not line:
                        time.sleep(0.1)
                    else:
                        line_number += 1
                        self.text_queue.put(
                            (line, line_number)
                        )  # Pass line and line number
                        line_ready.set()

        except Exception as e:
            print(f"Error reading file: {e}")


# Example usage
if __name__ == "__main__":
    tail_file = TailFile(read_file="test.txt", text_queue=Queue())

    # Create an Event to signal when a line is ready
    line_ready = Event()

    # Start the file reading thread using the tail method
    tail_file.start_thread(tail_file.tail, line_ready)

    ## Simulate another thread that processes the text stream

    tail_file.start_thread(
        detect_string_thread,
        ["error", "test", "testing"],
        tail_file.text_queue,
        line_ready,
    )
