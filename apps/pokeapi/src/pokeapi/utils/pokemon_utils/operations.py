from __future__ import annotations

from domain.api.responses import APIPokemonResource

import diskcache

from loguru import logger as log


def cache_all_pokemon(
    pokemon_list: list[APIPokemonResource] = None,
    use_cache: bool = False,
    cache: diskcache.Cache | None = None,
) -> None:
    """Loop over list of APIPokemonResource objects and make request, caching the response.

    DESCRIPTION:
    ------------

    This function can be run periodically (or scheduled, i.e. with Celery), to keep a cached response
    for all Pokemon served by the Pokemon API.

    PARAMS:
    -------

    * pokemon_list (list[APIPokemonResource]): A list of APIPokemonResource instances to be cached.
    * use_cache (bool): When True, will try to use the cache.
    * cache (diskcache.Cache): An instantiated diskcache.Cache object for storing the key/value.
    """
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
