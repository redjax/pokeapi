from __future__ import annotations

import sys

sys.path.append(".")

import json

from pathlib import Path
import random
from typing import Union

from pokeapi.core.conf import api_settings, app_settings
from pokeapi.dependencies import get_request_client, loguru_sinks
from pokeapi.domain.pokemon import PokemonNamesFile
from pokeapi.utils.path_utils import ensure_dirs_exist

import diskcache
import httpx

from loguru import logger as log
from red_utils.ext.diskcache_utils import (
    check_cache_key_exists,
    default_cache_conf,
    default_timeout_dict,
    get_val,
    new_cache,
    set_val,
)
from red_utils.ext.loguru_utils import init_logger
from red_utils.ext import msgpack_utils

ensure_dirs_exist([app_settings.data_dir, app_settings.cache_dir])
pokemon_names_file: Path = Path(f"{app_settings.data_dir}/list_all_pokemon.txt")


def request_pokemon(
    pokemon_name: str = None,
    client: httpx.Client = None,
    use_cache: bool = True,
    cache: diskcache.Cache | None = None,
) -> dict:
    def _request(url=None, client=client) -> httpx.Response:
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

    if client is None:
        log.warning(
            f"No request client was passed to the request_pokemon function. Initializing a new client."
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


def load_all_pokemon_names(
    read_file: Union[str, Path] = pokemon_names_file
) -> list[str]:
    """Read all Pokemon names from pre-populated text file."""
    if not read_file.exists():
        raise FileNotFoundError(f"Could not find file: {read_file}")

    names: list[str] = []

    try:
        with open(read_file, "r") as names_file:
            lines = names_file.readlines()

            for line in lines:
                names.append(line.strip("\n").lower())

        log.debug(f"Read [{len(names)}] Pokemon name(s) from file [{read_file}]")

        return names

    except Exception as exc:
        raise Exception(
            f"Unhandled exception reading Pokemon names from file: [{read_file}]. Details: {exc}"
        )


if __name__ == "__main__":
    init_logger(sinks=loguru_sinks)
    req_cache_conf = default_cache_conf
    req_cache_conf["directory"] = f"{app_settings.cache_dir}/requests"
    req_cache = new_cache(cache_conf=default_cache_conf)

    # client = httpx.Client()
    client: httpx.Client = get_request_client()

    pokemon_names_file: PokemonNamesFile = PokemonNamesFile()
    pokemon_names_file.read_from_file()
    log.debug(f"Found [{len(pokemon_names_file.names_list)}] Pokemon name(s)")

    pokemon_responses: list[dict] = []

    for name in pokemon_names_file.names_list:
        res = request_pokemon(pokemon_name=name, cache=req_cache)
        pokemon_responses.append(res)

    log.info(f"Got [{len(pokemon_responses)}] Pokemon response(s)")
    if len(pokemon_responses) > 0:
        rand_index = random.randint(0, len(pokemon_responses))

        sample_response = pokemon_responses[rand_index]
        log.debug(
            f"Random response sample ({type(sample_response)}): {sample_response}"
        )
