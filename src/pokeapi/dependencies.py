from __future__ import annotations

from pokeapi.core.conf import api_settings, app_settings

import httpx

from red_utils.ext.httpx_utils import default_headers
from red_utils.ext.loguru_utils import (
    LoguruSinkAppFile,
    LoguruSinkErrFile,
    LoguruSinkStdOut,
)

loguru_sinks: list = [
    LoguruSinkStdOut(level=app_settings.log_level).as_dict(),
    LoguruSinkAppFile(level=app_settings.log_level).as_dict(),
    LoguruSinkErrFile(level=app_settings.log_level).as_dict(),
]


def get_request_client(headers: dict = default_headers) -> httpx.Client:
    """Build & return a synchronous HTTPX request client."""
    try:
        _client: httpx.Client = httpx.Client(headers=headers)

        return _client
    except Exception as exc:
        raise Exception(f"Unhandled exception getting request client. Details: {exc}")


async def get_async_request_client(
    headers: dict = default_headers,
) -> httpx.AsyncClient:
    """Build & return an asynchronous HTTPX request client."""
    try:
        _client: httpx.AsyncClient = httpx.AsyncClient(headers=headers)

        yield _client
    except Exception as exc:
        raise Exception(
            f"Unhandled exception getting async request client. Details: {exc}"
        )
    finally:
        _client.close()
