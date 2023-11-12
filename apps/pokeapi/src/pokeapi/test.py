"""This file is a constantly-changing testbed for pokeapi while it's under development.

It should be removed when no longer needed.
"""

from __future__ import annotations

import sys

sys.path.append(".")

import json

from pathlib import Path
import random
from typing import Union

from pokeapi.core.conf import api_settings, app_settings
from pokeapi.dependencies import init_cache, loguru_sinks
from pokeapi.domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.path_utils import ensure_dirs_exist
from pokeapi.utils.pokemon_utils import cache_all_pokemon

from loguru import logger as log
from red_utils.ext import msgpack_utils
from red_utils.ext.diskcache_utils import (
    check_cache_key_exists,
    get_val,
    set_val,
)
from red_utils.ext.loguru_utils import init_logger
from red_utils.ext.msgpack_utils import (
    msgpack_deserialize,
    msgpack_deserialize_file,
    msgpack_serialize,
    msgpack_serialize_file,
)

if __name__ == "__main__":
    ## Ensure directory paths exist before starting app
    ensure_dirs_exist([app_settings.data_dir, app_settings.cache_dir])
    ## Initialize Loguru logger
    init_logger(sinks=loguru_sinks)

    ## Create caches
    req_cache = init_cache("requests")
    app_cache = init_cache("app")

    ## Initialize APIAllPokemon class. This class stores a list of resources (classes with
    #  name/URL pairs and a .get() function to retrieve)
    all_pokemon: APIAllPokemon = APIAllPokemon()
    ## Retrieve all pokemon, using cached responses if available
    all_pokemon.get_pokemon(use_cache=True, cache=req_cache)

    ## Select a random pokemon from the list of all pokemon
    rand_index = random.randint(0, len(all_pokemon.pokemon_list))
    sample_pokemon: APIPokemonResource = all_pokemon.pokemon_list[rand_index]
    log.debug(f"Sample Pokemon: {sample_pokemon}")

    ## Request Pokemon from the pokemon API. Uses cached response if available
    sample_pokemon.get(use_cache=True, cache=req_cache)
    log.debug(f"Sample Pokemon response ({type(sample_pokemon.response)})")

    if not check_cache_key_exists(cache=app_cache, key="all_pokemon"):
        ## All pokemon response was not cached. Serialize the response and cache it
        log.warning(f"Did not find cache_key 'all_pokemon' in cache. Saving.")

        ## Serialize value
        all_pokemon_serialized = msgpack_serialize(
            _json=all_pokemon.model_dump_json()
        ).detail

        ## Cache value
        set_val(cache=app_cache, key="all_pokemon", val=all_pokemon_serialized)

    else:
        ## All pokemon response was found in cache. Deserialize cached & response
        log.debug(f"Found cache_key 'all_pokemon' in cache. Loading from cache.")

        ## Load value from cache
        all_pokemon_serialized = get_val(cache=app_cache, key="all_pokemon")

    log.debug(f"All pokemon serialized ({type(all_pokemon_serialized)})")
    log.debug(
        f"All pokemon deserialized ({type(msgpack_deserialize(all_pokemon_serialized))})"
    )

    ## Make requests for all Pokemon resources in all_pokemon.pokemon_list. Use cached values, if available
    # cache_all_pokemon(all_pokemon.pokemon_list, use_cache=True, cache=req_cache)
