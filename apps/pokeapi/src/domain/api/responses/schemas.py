from __future__ import annotations

import json

from pathlib import Path
from typing import Union

from core.conf import api_settings

import diskcache
import httpx

from loguru import logger as log
from pydantic import BaseModel, Field, ValidationError, field_validator
from red_utils.ext.diskcache_utils import check_cache_key_exists, get_val, set_val
from red_utils.ext.msgpack_utils import msgpack_serialize


class APIPokemonResource(BaseModel):
    """Class representation of a Pokemon resource from the Pokemon API.

    PARAMS:
    -------

    * name (str): The Pokemon's name.
    * request_url (str): The Pokemon API endpoint for this Pokemon.
    * response (dict): Response from the Pokemon API endpoint. This value is empty until
        .get() is ran.

    Methods
    -------
    * .get(): Request Pokemon data from the Pokemon API. Optionally enable cachine by passing a diskcache.Cache object.

    PROPERTIES:
    -----------

    * .serialized (bytes): Return a msgpack-serialized bytestring representation of Pokemon.
    """

    name: str | None = Field(default=None)
    request_url: str | None = Field(default=None, alias="url")
    response: dict | None = Field(default=None)

    @property
    def serialized(self) -> bytes:
        try:
            _serialized = msgpack_serialize(self.model_dump_json())

            return _serialized

        except Exception as exc:
            raise Exception(
                f"Unhandled exception serializing APIPokemonResponse. Details: {exc}"
            )

    def get(
        self,
        use_cache: bool = False,
        cache: diskcache.Cache = None,
    ) -> dict[str, str]:
        if cache is None:
            if use_cache:
                log.error(
                    ValueError(
                        "use_cache is True, but no cache was passed. Disabling use_cache"
                    )
                )

                use_cache = False

        cache_key: str = str(self.name)

        client = httpx.Client()

        if not use_cache:
            log.info(f"Cache is disabled, making live request.")
            with client as c:
                res = c.get(self.request_url)

            log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

            if res.status_code == 200:
                log.info(f"Success requesting all Pokemon")
                content = json.loads(res.content.decode("utf-8"))

                self.response = content

                return content

            else:
                log.warning(
                    f"Non-200 status code in response: [{res.status_code}: {res.reason_phrase}] {res.text}"
                )

                return None

        else:
            log.info(f"Cache is enabled, attempting cached request")

            if not check_cache_key_exists(cache=cache, key=cache_key):
                log.warning("Did not find response in cache. Making live request.")

                with client as c:
                    res = c.get(self.request_url)

                log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

                if res.status_code == 200:
                    content = json.loads(res.content.decode("utf-8"))

                    self.response = content

                    set_val(
                        cache=cache,
                        key=cache_key,
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

                res: dict = get_val(cache=cache, key=cache_key)
                self.response = res

                return res


class APIAllPokemon(BaseModel):
    """Class to store all Pokemon available from the Pokemon API.

    DESCRIPTION:
    ------------

    Requests all Pokemon from API by setting a high limit and 0 offset. The response is
    a list of dict values, containing a Pokemon's name and the URL to request the Pokemon's
    data from the Pokemon API. These are converted to APIPokemonResource objects, and the data
    can be retrieved using the APIPokemonResource's .get() method.

    PARAMS:
    -------

    * url (str): URL to request all Pokemon from.
    * params (dict[str, int]): Params to set request limit=100000, offset=0.
        This is what facilitates returning all Pokemon from the /pokemon endpoint.
    * pokemon_list (list[APIPokemonResource]): Variable containing all Pokemon responses.
        This value is empty until .get_pokemon() is run.

    PROPERTIES:
    -----------

    * names_list (list[str]): A list of all Pokemon name strings found in object's pokemon_list variable. List
        will be empty until .get_pokemon() is run.

    Methods
    -------
    * .get_pokemon(): Request all Pokemon resources and their URL from the Pokemon API, optionally caching requests if a
        diskcache.Cache instance is passed to the function.
    """

    url: str | None = Field(default=f"{api_settings.base_url}/pokemon")
    params: dict[str, int] | None = Field(default={"limit": 100000, "offset": 0})
    pokemon_list: list[APIPokemonResource] | None = Field(default=None)

    @property
    def names_list(self) -> list[str]:
        """List of all Pokemon names returned from the Pokemon API."""
        if self.pokemon_list is None:
            log.error(
                "Pokemon list is empty. Run .get_pokemon() function to populate list, then try .names_list again."
            )

        names: list[str] = []

        for pk in self.pokemon_list:
            names.append(pk.name)

        return names

    def get_pokemon(
        self,
        use_cache: bool = False,
        cache: diskcache.Cache = None,
    ) -> dict[str, str]:
        """Request all Pokemon resources from the Pokemon API.

        PARAMS:
        -------

        * use_cache (bool): When True, enables caching if a diskcache.Cache instance is passed to the function.
        * cache (discache.Cache): Provide a cache for storing responses from the Pokemon API.
        """
        client = httpx.Client()

        if not use_cache:
            log.info(f"Cache is disabled, making live request.")
            with client as c:
                res = c.get(self.url, params=self.params)

            log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

            if res.status_code == 200:
                log.info(f"Success requesting all Pokemon")
                content = json.loads(res.content.decode("utf-8"))

                all_pokemon_dict: list[dict] = content["results"]
                all_pokemon: list[APIPokemonResource] = []

                for p in all_pokemon_dict:
                    pk: APIPokemonResource = APIPokemonResource.model_validate(p)
                    all_pokemon.append(pk)

                self.pokemon_list = all_pokemon

                return content

            else:
                log.warning(
                    f"Non-200 status code in response: [{res.status_code}: {res.reason_phrase}] {res.text}"
                )

                return None

        else:
            log.info(f"Cache is enabled, attempting cached request")

            if not check_cache_key_exists(cache=cache, key="all_pokemon"):
                log.warning("Did not find response in cache. Making live request.")

                with client as c:
                    res = c.get(self.url, params=self.params)

                log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

                if res.status_code == 200:
                    content = json.loads(res.content.decode("utf-8"))

                    all_pokemon_dict: list[dict] = content["results"]
                    all_pokemon: list[APIPokemonResource] = []

                    for p in all_pokemon_dict:
                        pk: APIPokemonResource = APIPokemonResource.model_validate(p)
                        all_pokemon.append(pk)

                    self.pokemon_list = all_pokemon

                    set_val(
                        cache=cache,
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

                res: dict = get_val(cache=cache, key="all_pokemon")

                all_pokemon_dict: list[dict] = res["results"]
                all_pokemon: list[APIPokemonResource] = []

                for p in all_pokemon_dict:
                    pk: APIPokemonResource = APIPokemonResource.model_validate(p)
                    all_pokemon.append(pk)

                self.pokemon_list = all_pokemon

                return res
