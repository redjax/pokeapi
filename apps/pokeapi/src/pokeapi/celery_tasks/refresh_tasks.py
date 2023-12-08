from pokeapi.celeryapp import app
from loguru import logger as log

from domain.api.responses import APIAllPokemon, APIPokemonResource
from pokeapi.utils.serialize_utils import SerializedData, SerialFunctionResponse
from pokeapi.utils.pokemon_utils import cache_all_pokemon
from red_utils.ext.diskcache_utils import check_cache_key_exists, get_val, set_val
from pokeapi.dependencies import init_cache
from red_utils.ext.loguru_utils import LoguruSinkAppFile, LoguruSinkErrFile

from core.conf import app_settings

import diskcache

req_cache = init_cache("requests")
app_cache = init_cache("app")

SERIALIZE_DIR: str = app_settings.serialize_dir

log.add(**LoguruSinkAppFile(sink="logs/celery/celery_task_app.log").as_dict())
log.add(**LoguruSinkErrFile(sink="logs/celery/celery_task_err.log").as_dict())


@app.task
def refresh_all_pokemon(all_pokemon_dict: dict) -> dict:
    if all_pokemon_dict is None:
        raise ValueError("Missing APIAllPokemon dict object")

    cache: diskcache.Cache = req_cache

    # log.debug(f"All Pokemon dict ({type(all_pokemon_dict)}): {all_pokemon_dict}")
    all_pokemon: APIAllPokemon = APIAllPokemon.model_validate(all_pokemon_dict)
    # log.debug(f"All Pokemon object ({type(all_pokemon)}): {all_pokemon}")

    all_pokemon.get_pokemon(use_cache=True, cache=cache)

    serialize_obj: SerializedData = SerializedData(
        output_dir=SERIALIZE_DIR,
        data=all_pokemon.model_dump(),
        name="all-pokemon.msgpack",
    )
    try:
        serialize_obj.serialize()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing {serialize_obj.name} to file {serialize_obj.output_path}. Details: {exc}"
        )
        log.error(msg)
        pass

    return all_pokemon.model_dump()


@app.task
def refresh_single_pokemon(pokemon_dict: dict) -> dict:
    if pokemon_dict is None:
        raise ValueError("Missing APIPokemonResource dict object")

    cache: diskcache.Cache = req_cache

    pokemon: APIPokemonResource = APIPokemonResource.model_validate(pokemon_dict)
    log.info(f"Refreshing Pokemon {pokemon.name}")

    pokemon.get(use_cache=True, cache=cache)

    serialize_obj: SerializedData = SerializedData(
        output_dir=f"SERIALIZE_DIR/pokemon",
        data=pokemon.model_dump(),
        name=pokemon.name,
    )
    try:
        serialize_obj.serialize()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing {serialize_obj.name} to file {serialize_obj.output_path}. Details: {exc}"
        )
        log.error(msg)
        pass

    return pokemon.model_dump()
