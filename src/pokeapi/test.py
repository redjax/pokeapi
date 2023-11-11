from __future__ import annotations

import sys

sys.path.append(".")

import json

from pathlib import Path
import random
from typing import Union

from pokeapi.core.conf import api_settings, app_settings
from pokeapi.dependencies import get_request_client, loguru_sinks
from pokeapi.domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.path_utils import ensure_dirs_exist, read_from_file

import diskcache
import httpx

from loguru import logger as log
from red_utils.ext import msgpack_utils
from red_utils.ext.diskcache_utils import (
    check_cache_key_exists,
    default_cache_conf,
    default_timeout_dict,
    get_val,
    new_cache,
    set_val,
)
from red_utils.ext.loguru_utils import init_logger

ensure_dirs_exist([app_settings.data_dir, app_settings.cache_dir])
pokemon_names_file: Path = Path(f"{app_settings.data_dir}/list_all_pokemon.txt")


def request_pokemon(
    pokemon_name: str = None,
    use_cache: bool = True,
    cache: diskcache.Cache | None = None,
) -> dict:
    def _request(url, client: httpx.Client) -> httpx.Response:
        try:
            with client as c:
                res = c.get(url)

                log.info(
                    f"Request Pokemon: {pokemon_name}, response: [{res.status_code}: {res.reason_phrase}]"
                )

                return res

        except Exception as exc:
            raise Exception(
                f"Unhandled exception requesting Pokemon: {pokemon_name}. Details: {exc}"
            )

    client = httpx.Client()

    if cache is None:
        if use_cache is True:
            raise ValueError("use_cache is set to True, but no cache object was passed")
        else:
            pass

    log.info(f"Requesting Pokemon: {pokemon_name}")

    req_url: str = f"{api_settings.base_url}/pokemon/{pokemon_name}"

    if not use_cache:
        log.info(f"Cache is disabled, making live request.")
        res = _request(url=req_url)
        log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

        if res.status_code == 200:
            log.info(f"Success requesting Pokemon: {pokemon_name}")
            content = json.loads(res.content.decode("utf-8"))

            return content

        else:
            log.warning(
                f"Non-200 status code in response: [{res.status_code}: {res.reason_phrase}] {res.text}"
            )

            return None

    else:
        log.info(f"Cache is enabled, attempting cached request")

        if not check_cache_key_exists(cache=req_cache, key=pokemon_name):
            log.warning("Did not find response in cache. Making live request.")

            res = _request(url=req_url, client=client)

            if res.status_code == 200:
                content = json.loads(res.content.decode("utf-8"))

                set_val(
                    cache=req_cache,
                    key=pokemon_name,
                    val=content,
                )

                return content

            else:
                log.info(
                    f"Non-200 success response: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                return None

        else:
            log.info("Found response in cache. Loading from cache.")

            response: dict = get_val(cache=req_cache, key=pokemon_name)
            # log.debug(f"Cached response: {response}")

            return response


def request_all_pokemon(
    limit: int = 100000,
    offset: int = 0,
    use_cache: bool = True,
    cache: diskcache.Cache | None = None,
):
    """Request all pokemon by setting a high limit & offset.

    Example URL for all Pokemon:
        https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0

    Params:
    -------

    limit (int): Limit response page size. Set to a high number, like 100,000, to request
        all pokemon at once.

    offset (int): When requesting results in pages, the offset skips first X number of results.
    """
    if cache is None:
        if use_cache is True:
            raise ValueError("use_cache is set to True, but no cache object was passed")
        else:
            pass

    url: str = f"{api_settings.base_url}/pokemon"
    params: dict[str, int] = {"limit": limit, "offset": offset}

    client: httpx.Client = httpx.Client()

    if not use_cache:
        log.info(f"Cache is disabled, making live request.")
        with client as c:
            res = c.get(url, params=params)

        log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

        if res.status_code == 200:
            log.info(f"Success requesting all Pokemon")
            content = json.loads(res.content.decode("utf-8"))

            return content

        else:
            log.warning(
                f"Non-200 status code in response: [{res.status_code}: {res.reason_phrase}] {res.text}"
            )

            return None

    else:
        log.info(f"Cache is enabled, attempting cached request")

        if not check_cache_key_exists(cache=req_cache, key="all_pokemon"):
            log.warning("Did not find response in cache. Making live request.")

            with client as c:
                res = c.get(url, params=params)

            log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

            if res.status_code == 200:
                content = json.loads(res.content.decode("utf-8"))

                set_val(
                    cache=req_cache,
                    key="all_pokemon",
                    val=content,
                )

                return content

            else:
                log.info(
                    f"Non-200 success response: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                return None

        else:
            log.info("Found response in cache. Loading from cache.")

            response: dict = get_val(cache=req_cache, key="all_pokemon")
            # log.debug(f"Cached response: {response}")

            return response


if __name__ == "__main__":
    init_logger(sinks=loguru_sinks)
    req_cache_conf = default_cache_conf
    req_cache_conf["directory"] = f"{app_settings.cache_dir}/requests"
    req_cache = new_cache(cache_conf=default_cache_conf)

    all_pokemon: APIAllPokemon = APIAllPokemon()
    all_pokemon.get_pokemon(use_cache=True, cache=req_cache)
    log.debug(all_pokemon.pokemon_list)

    rand_index = random.randint(0, len(all_pokemon.pokemon_list))
    sample_pokemon: APIPokemonResource = all_pokemon.pokemon_list[rand_index]
    log.debug(f"Sample Pokemon: {sample_pokemon}")
    sample_pokemon.get(use_cache=True, cache=req_cache)
    log.debug(f"Sample Pokemon response ({type(sample_pokemon.response)})")
