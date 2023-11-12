from __future__ import annotations

import sys

sys.path.append(".")

import json

from pathlib import Path
import random
from typing import Union

from pokeapi.core.conf import api_settings, app_settings
from pokeapi.dependencies import loguru_sinks, init_cache
from pokeapi.domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.path_utils import ensure_dirs_exist

from loguru import logger as log
from red_utils.ext import msgpack_utils
from red_utils.ext.diskcache_utils import (
    check_cache_key_exists,
    get_val,
    set_val,
)
from red_utils.ext.loguru_utils import init_logger
from red_utils.ext.msgpack_utils import (
    msgpack_serialize,
    msgpack_serialize_file,
    msgpack_deserialize,
    msgpack_deserialize_file,
)


def cache_all_pokemon(
    pokemon_list: list[APIPokemonResource] = None, use_cache: bool = False, cache=None
) -> None:
    if pokemon_list is None:
        raise ValueError("Missing list of APIPokemonResource objects.")

    if cache is not None:
        use_cache = True
    else:
        use_cache = False

    for pokemon in pokemon_list:
        log.debug(f"Requesting Pokemon [{pokemon.name}] from: {pokemon.request_url}")
        try:
            pokemon.get(use_cache=use_cache, cache=cache)
        except Exception as exc:
            log.error(
                Exception(
                    f"Unhandled exception requesting Pokemon [{pokemon.name}]. Details: {exc}"
                )
            )


if __name__ == "__main__":
    ensure_dirs_exist([app_settings.data_dir, app_settings.cache_dir])
    init_logger(sinks=loguru_sinks)
    req_cache = init_cache("requests")
    app_cache = init_cache("app")

    all_pokemon: APIAllPokemon = APIAllPokemon()
    all_pokemon.get_pokemon(use_cache=True, cache=req_cache)

    rand_index = random.randint(0, len(all_pokemon.pokemon_list))
    sample_pokemon: APIPokemonResource = all_pokemon.pokemon_list[rand_index]
    log.debug(f"Sample Pokemon: {sample_pokemon}")
    sample_pokemon.get(use_cache=True, cache=req_cache)
    log.debug(f"Sample Pokemon response ({type(sample_pokemon.response)})")

    if not check_cache_key_exists(cache=app_cache, key="all_pokemon"):
        log.warning(f"Did not find cache_key 'all_pokemon' in cache. Saving.")
        all_pokemon_serialized = msgpack_serialize(
            _json=all_pokemon.model_dump_json()
        ).detail

        set_val(cache=app_cache, key="all_pokemon", val=all_pokemon_serialized)

    else:
        log.debug(f"Found cache_key 'all_pokemon' in cache. Loading from cache.")

        all_pokemon_serialized = get_val(cache=app_cache, key="all_pokemon")

    log.debug(f"All pokemon serialized ({type(all_pokemon_serialized)})")
    log.debug(
        f"All pokemon deserialized ({type(msgpack_deserialize(all_pokemon_serialized))})"
    )

    cache_all_pokemon(all_pokemon.pokemon_list, use_cache=True, cache=req_cache)
