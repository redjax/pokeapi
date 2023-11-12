from .celeryapp import app
from loguru import logger as log

from pokeapi.domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.pokemon_utils import cache_all_pokemon
from red_utils.ext.diskcache_utils import check_cache_key_exists, get_val, set_val
from pokeapi.dependencies import init_cache

import diskcache

req_cache = init_cache("requests")
app_cache = init_cache("app")


@app.task
def refresh_all_pokemon(all_pokemon_dict: dict) -> dict:
    if all_pokemon_dict is None:
        raise ValueError("Missing APIAllPokemon dict object")

    cache: diskcache.Cache = req_cache

    # log.debug(f"All Pokemon dict ({type(all_pokemon_dict)}): {all_pokemon_dict}")
    all_pokemon: APIAllPokemon = APIAllPokemon.model_validate(all_pokemon_dict)
    # log.debug(f"All Pokemon object ({type(all_pokemon)}): {all_pokemon}")

    all_pokemon.get_pokemon(use_cache=True, cache=cache)

    return all_pokemon.model_dump()


@app.task
def refresh_single_pokemon(pokemon_dict: dict) -> dict:
    if pokemon_dict is None:
        raise ValueError("Missing APIPokemonResource dict object")

    cache: diskcache.Cache = req_cache

    pokemon: APIPokemonResource = APIPokemonResource.model_validate(pokemon_dict)
    log.info(f"Refreshing Pokemon {pokemon.name}")

    pokemon.get(use_cache=True, cache=cache)

    return pokemon.model_dump()
