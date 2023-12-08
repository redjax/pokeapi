from __future__ import annotations

import sys

sys.path.append(".")

from core import api_settings, app_settings
from pokeapi.dependencies import init_cache, loguru_sinks
from domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.path_utils import ensure_dirs_exist
from pokeapi.utils.pokemon_utils import cache_all_pokemon

from loguru import logger as log
from red_utils.ext.loguru_utils import init_logger

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

    log.debug(f"Retrieved [{len(all_pokemon.pokemon_list)}] Pokemon")
