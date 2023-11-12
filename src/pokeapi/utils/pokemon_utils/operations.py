import diskcache
from loguru import logger as log

from pokeapi.domain.api.responses import APIPokemonResource


def cache_all_pokemon(
    pokemon_list: list[APIPokemonResource] = None,
    use_cache: bool = False,
    cache: diskcache.Cache | None = None,
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
