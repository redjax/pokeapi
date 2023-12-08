from pathlib import Path

DATA_DIR: Path = Path(".data")
CACHE_DIR: Path = Path(".cache")
SERIALIZE_DIR: Path = Path(".serialize")

ALL_POKEMON_JSON: Path = Path(f"{DATA_DIR}/all_pokemon.json")

DEFAULT_RABBITMQ_PORT: int = 5672
DEFAULT_REDIS_PORT: int = 6379
