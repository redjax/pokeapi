import sys

sys.path.append(".")

from core.conf import app_settings, celery_settings
from pokeapi.dependencies import init_cache, loguru_sinks
from domain.api.responses import APIAllPokemon, APIPokemonResource
from domain.enums.celery_enums import CeleryTaskState
from pokeapi.utils.path_utils import ensure_dirs_exist
from pokeapi.utils.pokemon_utils import cache_all_pokemon

from loguru import logger as log
import diskcache

from red_utils.ext.diskcache_utils import check_cache_key_exists, get_val, set_val
from red_utils.ext.loguru_utils import init_logger
from red_utils.ext.context_managers.cli_spinners import SimpleSpinner

from pokeapi.celery_tasks import refresh_all_pokemon, refresh_single_pokemon
from pokeapi.celeryapp import app as celery_app
from celery.result import AsyncResult

import random

from dynaconf import settings

import time

CONTINUUOUS: bool = True
LOOP_SLEEP: int = 3600


def check_task(task_id: str | None = None) -> AsyncResult:
    if task_id is None:
        raise ValueError("Missing task_id to check.")

    task = AsyncResult(task_id)

    # log.debug(f"Task ID [{task_id}] state: {task.state}")

    return task.state, task.result


def run_all_pokemon_refresh(
    all_pokemon: APIAllPokemon = APIAllPokemon(),
    task_sleep: int = 10,
) -> None:
    log.info("Refreshing cache of all Pokemon resources")

    try:
        with SimpleSpinner("Refreshing all Pokemon resource objects in cache... "):
            all_pokemon_res: AsyncResult = refresh_all_pokemon.delay(
                all_pokemon_dict=all_pokemon.model_dump()
            )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running Celery task, refresh_all_pokemon(). Details: {exc}"
        )
        log.error(msg)

    while True:
        all_pokemon_state, result = check_task(all_pokemon_res.id)
        log.debug(f"Refreshed state: {all_pokemon_state}")

        if all_pokemon_state == "SUCCESS":
            # log.debug(f"Result: {result}")
            all_pokemon_res = APIAllPokemon.model_validate(result)
            log.info("Refresh all Pokemon resources task completed successfully!")

            return all_pokemon_res
            break
        elif all_pokemon_state in ("FAILURE", "REVOKED"):
            log.error(
                f"Task [{all_pokemon_res.id}] failed or revoked. State: {all_pokemon_state}."
            )
            break
        else:
            with SimpleSpinner(
                f"Task [{all_pokemon_res.id}] is still in progress. Waiting for {task_sleep} second(s)..."
            ):
                time.sleep(task_sleep)


def loop_refresh_pokemon_resources(all_pokemon: APIAllPokemon = None):
    all_pokemon_list: list[APIPokemonResource] = all_pokemon.pokemon_list
    log.debug(f"Refreshing [{len(all_pokemon_list)}] Pokemon...")

    refresh_pokemon_tasks: list[AsyncResult] = []

    with SimpleSpinner("Refreshing cached Pokemon resources"):
        for p in all_pokemon_list:
            try:
                refresh_pokemon_res: AsyncResult = refresh_single_pokemon.delay(
                    pokemon_dict=p.model_dump()
                )
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception running Celery task, refresh_all_pokemon(). Details: {exc}"
                )
                log.error(msg)

            refresh_pokemon_tasks.append(refresh_pokemon_res)

    return_pokemon: list[APIPokemonResource] = []

    for refresh_task in refresh_pokemon_tasks:
        task_id: int = refresh_task.id
        log.debug(f"Working on task [{task_id}]")

        while True:
            refresh_pokemon_state, result = check_task(refresh_task.id)
            log.debug(
                f"Task [{refresh_task.id}] refreshed state: {refresh_pokemon_state}"
            )

            if refresh_pokemon_state == "SUCCESS":
                # log.debug(f"Result: {result}")
                refresh_pokemon_res = APIPokemonResource.model_validate(result)
                log.info(f"Refresh Pokemon resource task completed successfully!")

                return_pokemon.append(refresh_pokemon_res)
                break

            elif refresh_pokemon_state in ("FAILURE", "REVOKED"):
                log.error(
                    f"Task [{refresh_task.id}] failed or revoked. State: {refresh_pokemon_state}."
                )
                break
            else:
                with SimpleSpinner(
                    f"Task [{refresh_task.id}] is still in progress. Waiting for 5 second(s)..."
                ):
                    time.sleep(5)

    return return_pokemon


if __name__ == "__main__":
    ensure_dirs_exist(
        [app_settings.data_dir, app_settings.cache_dir, app_settings.serialize_dir]
    )
    init_logger(sinks=loguru_sinks)

    req_cache = init_cache("requests")
    app_cache = init_cache("app")

    log.info(
        f"[env:{app_settings.env}|container:{app_settings.container_env}] Starting background cache refresh tasks"
    )

    log.debug(f"Celery settings: {celery_settings}")

    if CONTINUUOUS:
        loop: bool = True
        loop_count: int = 0

        while loop:
            log.info(f"[Loop {loop_count}] Starting background cache refresh tasks")

            try:
                all_pokemon: APIAllPokemon = run_all_pokemon_refresh(task_sleep=5)
            except Exception as exc:
                log.error(
                    Exception(f"Unhandled exception refreshing all pokemon: {exc}")
                )

                loop = False
                break

            try:
                refreshed_pokemon: list[
                    APIPokemonResource
                ] = loop_refresh_pokemon_resources(all_pokemon=all_pokemon)
            except Exception as exc:
                log.error(
                    Exception(
                        f"Unhandled exception refreshing individual Pokemon. Details: {exc}"
                    )
                )
                loop = False
                break

            log.debug(f"Refreshed [{len(refreshed_pokemon)}]")

            if len(refreshed_pokemon) > 0:
                rand_index: int = random.randint(0, len(refreshed_pokemon) - 1)
                refreshed: APIPokemonResource = refreshed_pokemon[rand_index]

                log.debug(f"(Sample) Refreshed Pokemon [{refreshed.name}]")

            log.info("Finished refreshing cache.")
            with SimpleSpinner(
                f"[Loop {loop_count}] Finished refreshing cache. Sleeping for {LOOP_SLEEP} second(s)..."
            ):
                time.sleep(LOOP_SLEEP)
                loop_count += 1

    else:
        all_pokemon: APIAllPokemon = run_all_pokemon_refresh(task_sleep=5)
        refreshed_pokemon: list[APIPokemonResource] = loop_refresh_pokemon_resources(
            all_pokemon=all_pokemon
        )
        log.debug(f"Refreshed [{len(refreshed_pokemon)}]")

        if len(refreshed_pokemon) > 0:
            rand_index: int = random.randint(0, len(refreshed_pokemon) - 1)
            refreshed: APIPokemonResource = refreshed_pokemon[rand_index]

            log.debug(f"(Sample) Refreshed Pokemon [{refreshed.name}]")
