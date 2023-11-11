from pydantic import BaseModel, Field, field_validator, ValidationError

from typing import Union
from pathlib import Path

from loguru import logger as log

from red_utils.ext.msgpack_utils import msgpack_serialize
from red_utils.ext.diskcache_utils import get_val, set_val, check_cache_key_exists

import json
import httpx
import diskcache

from pokeapi.core.conf import api_settings


class APIPokemonResource(BaseModel):
    name: str | None = Field(default=None)
    request_url: str | None = Field(default=None, alias="url")

    @property
    def serialized(self) -> bytes:
        try:
            _serialized = msgpack_serialize(self.model_dump_json())

            return _serialized

        except Exception as exc:
            raise Exception(
                f"Unhandled exception serializing APIPokemonResponse. Details: {exc}"
            )


class APIAllPokemon(BaseModel):
    """Requests all Pokemon from API by setting a high limit and 0 offset."""

    url: str | None = Field(default=f"{api_settings.base_url}/pokemon")
    params: dict[str, int] | None = Field(default={"limit": 100000, "offset": 0})
    pokemon_list: list[APIPokemonResource] | None = Field(default=None)

    def get_pokemon(
        self,
        use_cache: bool = False,
        cache: diskcache.Cache = None,
    ) -> dict[str, str]:
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
